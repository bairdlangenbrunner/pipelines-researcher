/* Pipelines review app, the single-file / claude.ai artifact side of the front end. Loaded BEFORE
   app.js by review_app/build_static.py, which puts the dataset in the page itself; anywhere else
   (no window.REVIEW_STATIC) it does nothing.

   There is no server here, so this file does what the server does:
     - the dataset and its key index are one gzipped blob in the page (#review-blob)
     - a decision is checked against the index exactly as gas/Code.gs checks it (validateLines_,
       validateItems_, concernCalls_ are ported below; keep them in step with store.py)
     - the reviewer's records are kept in this browser (localStorage) and, on a published artifact,
       in the artifact's shared database: documents logs/<viewer id>~<browser>~<n>, 250 records each.
       The viewer's address would be preferred for the initials (the ledger derives them from it),
       but the publish service refuses the user scope "email" (checked 2026-10-05), so the page gets
       the profile name only and import_log.py takes the address with --reviewer.
       Every open page listens to that collection, so reviewers see each other's calls. A viewer the
       artifact does not let write (not shared with them by email as an editor, or outside the
       publishing account's organization) is told so in the banner and keeps the log in the browser.
     - the browser log is one key for every build of the page, so a rebuilt page published to the
       same link picks up the decisions this browser made on the earlier build
     - "download decisions" hands over everything the page knows, for review_app/import_log.py
   Nothing here reaches the decision store or the backend sheet. import_log.py carries the records
   into the ledger; push.py is still the only way to the sheet. */
(function () {
  "use strict";
  var CFG = window.REVIEW_STATIC;
  if (!CFG) return;

  var DECISIONS = ["accept", "hold", "reject", "suggest"];
  var LINE_KINDS = ["ref", "fill", "status", "oo", "route", "new_row"];
  var CONCERN_CALLS = ["confirmed", "dismissed", "needs_research"];
  var OTHER_CALLS = ["noted", "todo", "dismissed"];
  var MAX_TEXT = 5000, MAX_RECORDS = 5000, CHUNK = 250;
  var MACHINE = {"backend sync": 1, "push": 1};
  var LS_LOG = "review-artifact-log", LS_DEVICE = "review-artifact-device";

  var G = {
    me: CFG.reviewer || "", email: "", uid: "", device: "",
    idx: null, snapshot: "", built: "", dirs: [],
    own: [],            // the records this browser wrote, oldest first
    remote: {},         // doc id -> the latest body of every other log document
    seen: {},           // record id -> 1
    shown: {},          // key -> time (ms) of the record the page shows for it
    calls: {},          // item key -> its call as of the latest record ('' = open)
    pending: [],        // records waiting for the app to index the dataset
    synced: {},         // chunk number -> how many records the shared log holds for it
    db: null, dl: null, shared: "none", storage: true, booted: false, first: true, dirty: false,
    chain: Promise.resolve(), syncing: false, again: false
  };
  function RA() { return window.ReviewApp; }
  function has(o, k) { return Object.prototype.hasOwnProperty.call(o, k); }
  function ms(ts) { var t = Date.parse(ts || ""); return isNaN(t) ? 0 : t; }
  function uuid() {
    if (window.crypto && crypto.randomUUID) return crypto.randomUUID();
    return "xxxxxxxx-xxxx-4xxx-yxxx-xxxxxxxxxxxx".replace(/[xy]/g, function (c) {
      var r = Math.random() * 16 | 0;
      return (c === "x" ? r : (r & 3 | 8)).toString(16);
    });
  }
  // America/New_York wall time with its offset, the shape store.now() writes
  function now() {
    var d = new Date(), p = {};
    new Intl.DateTimeFormat("en-CA", {timeZone: "America/New_York", hourCycle: "h23", year: "numeric", month: "2-digit",
      day: "2-digit", hour: "2-digit", minute: "2-digit", second: "2-digit"}).formatToParts(d)
      .forEach(function (x) { p[x.type] = x.value; });
    var wall = Date.UTC(+p.year, +p.month - 1, +p.day, +p.hour, +p.minute, +p.second);
    var off = Math.round((wall - d.getTime()) / 60000), a = Math.abs(off);
    function two(n) { return (n < 10 ? "0" : "") + n; }
    return p.year + "-" + p.month + "-" + p.day + "T" + p.hour + ":" + p.minute + ":" + p.second +
      (off < 0 ? "-" : "+") + two(Math.floor(a / 60)) + ":" + two(a % 60);
  }
  // store.initials: "Baird Langenbrunner" and baird.langenbrunner@x.org both give "BL"
  function initials(who) {
    var v = String(who || "").trim();
    if (!v || /^[A-Z]{1,3}$/.test(v)) return v;
    var m = /^([^@\s]+)@[^@\s]+\.[^@\s]+$/.exec(v);
    var parts = (m ? m[1].split(/[._+\-]+/) : v.split(/\s+/)).filter(function (t) { return /^[A-Za-z]/.test(t); });
    if (!parts.length) return "";
    return (parts[0][0] + (parts.length > 1 ? parts[parts.length - 1][0] : "")).toUpperCase();
  }
  function segment(s) { return String(s).replace(/[^A-Za-z0-9_.~:@+-]/g, "-").slice(0, 80) || "x"; }

  // ---- the dataset ----
  function gunzip(b64) {
    if (!window.DecompressionStream) return Promise.reject(new Error("this browser cannot unpack the dataset: use a current Chrome, Edge, Firefox or Safari"));
    var bin = atob(b64), bytes = new Uint8Array(bin.length);
    for (var i = 0; i < bin.length; i++) bytes[i] = bin.charCodeAt(i);
    return new Response(new Blob([bytes]).stream().pipeThrough(new DecompressionStream("gzip"))).text().then(JSON.parse);
  }
  var loaded = null;
  function load() {
    if (!loaded) {
      var el = document.getElementById("review-blob");
      if (!el) return Promise.reject(new Error("the page holds no dataset (review_app/build_static.py writes it)"));
      loaded = gunzip(el.textContent.replace(/\s+/g, "")).then(function (b) {
        G.idx = b.index;
        G.snapshot = (b.data.scope && b.data.scope.snapshot) || "";
        G.built = b.data.built || "";
        G.dirs = b.data.dirs || [];
        return b.data;
      });
    }
    // the app keeps and changes the object it is given, so a reload gets its own copy
    return loaded.then(function (d) { return JSON.parse(JSON.stringify(d)); });
  }

  // ---- validation: a port of gas/Code.gs (itself a port of store.py) ----
  function refuse(msg) { return new Error(msg); }
  function get(I, key) {
    if (typeof key !== "string") return null;
    if (!I.m) {
      I.m = {}; I.dn = {};
      I.dirs.forEach(function (d, i) { I.dn[d] = i; });
    }
    if (has(I.m, key)) return I.m[key];
    var at = key.indexOf("::"), out = null;
    if (at > 0) {
      var dir = key.substr(0, at), rest = key.substr(at + 2), grp = has(I.dn, dir) ? I.keys[I.dn[dir]] : null;
      if (grp && has(grp, rest)) {
        var c = grp[rest];
        out = c.i ? {g: "i", kind: c.i, dir: dir, pid: c.p, call0: c.c0 || ""}
          : {g: "l", kind: c.k, dir: dir, pid: c.p, sheet_row: c.r == null ? null : c.r, ref_col: c.c || "",
             def: c.d || "accept", basis: c.b || "",
             covers: (c.v || []).map(function (x) {
               return {key: x[0], dir: x[0].substr(0, x[0].indexOf("::")), sheet_row: x[1] == null ? null : x[1], ref_col: x[2] || "", kind: x[3]};
             }),
             concerns: (c.x || []).map(function (x) { return {c: x[0], res: x[1] || [], cand: x[2] || "", cols: x[3] || []}; })};
      }
    }
    I.m[key] = out;
    return out;
  }
  function text(v, i, what) {
    var s = v ? String(v) : "";
    if (s.length > MAX_TEXT) throw refuse("record " + i + ": the " + what + " is longer than " + MAX_TEXT + " characters");
    return s;
  }
  function list(records, what) {
    if (!Array.isArray(records) || !records.length) throw refuse("expected a non-empty list of " + what + " records");
    if (records.length > MAX_RECORDS) throw refuse("too many records in one request (" + records.length + ")");
  }
  function entry(idx, r, i) {
    if (!r || typeof r !== "object" || Array.isArray(r)) throw refuse("record " + i + ": not an object");
    var e = get(idx, r.key);
    if (!e) throw refuse("record " + i + ": unknown key " + JSON.stringify(r.key));
    return e;
  }
  function validateLines(records, idx) {
    list(records, "decision");
    var out = [];
    records.forEach(function (r, i) {
      var e = entry(idx, r, i), key = r.key;
      if (e.g !== "l" || LINE_KINDS.indexOf(e.kind) < 0) throw refuse("record " + i + ": " + JSON.stringify(key) + " is an item, not a line");
      var undo = !!(r.undo || r.undecided), decision = r.decision;
      if (undo && !decision) decision = e.def || "hold";
      var rival = (!undo && r.rival) ? String(r.rival) : "";
      if (rival && !decision) decision = "suggest";
      if (!undo && !decision) throw refuse("record " + i + ": no decision given (a bare key never defaults to accept)");
      if (DECISIONS.indexOf(decision) < 0) throw refuse("record " + i + ": decision " + JSON.stringify(decision) + " is not one of " + DECISIONS.join(", "));
      var note = text(r.note, i, "note"), sv = text(r.suggested_value, i, "suggested value");
      if (rival) {
        var rv = (e.concerns || []).filter(function (x) { return x.c === rival && x.cand; })[0];
        if (!rv) throw refuse("record " + i + ": " + JSON.stringify(rival) + " is not a concern with a candidate value on " + JSON.stringify(key));
        if (decision !== "suggest") throw refuse("record " + i + ": taking a concern's candidate is recorded as suggest, not " + decision);
        sv = sv.trim() || rv.cand;
      }
      if (decision === "suggest" && !undo && !(sv.trim() || note.trim())) throw refuse("record " + i + ": a suggestion needs a suggested_value or a note");
      var rec = {key: key, dir: e.dir, pid: e.pid, sheet_row: e.sheet_row == null ? null : e.sheet_row, ref_col: e.ref_col || "",
                 kind: e.kind, decision: decision, suggested_value: sv, note: note, reviewer: null, ts: null, undecided: undo};
      if (e.basis) rec.basis = e.basis;
      if (rival) rec.rival = rival;
      out.push(rec);
      (e.covers || []).forEach(function (c) {
        var cr = {};
        Object.keys(rec).forEach(function (k) { cr[k] = rec[k]; });
        cr.key = c.key; cr.dir = c.dir; cr.sheet_row = c.sheet_row == null ? null : c.sheet_row;
        cr.ref_col = c.ref_col || ""; cr.kind = c.kind; cr.via = key;
        out.push(cr);
      });
    });
    return out;
  }
  function validateItems(records, idx) {
    list(records, "item");
    return records.map(function (r, i) {
      var e = entry(idx, r, i);
      if (e.g !== "i") throw refuse("record " + i + ": " + JSON.stringify(r.key) + " is a line, not an item");
      var undo = !!(r.undo || r.undecided), call = undo ? "" : (r.call ? String(r.call) : "");
      var vocab = e.kind === "concern" ? CONCERN_CALLS : OTHER_CALLS;
      if (!undo && vocab.indexOf(call) < 0) throw refuse("record " + i + ": call " + JSON.stringify(call) + " is not one of " + vocab.join(", ") + " for a " + e.kind + " item");
      return {key: r.key, dir: e.dir, pid: e.pid, kind: e.kind, call: call, note: text(r.note, i, "note"),
              reviewer: null, ts: null, undecided: undo};
    });
  }
  function concernCalls(recs, idx, callOf) {
    var calls = {}, order = [];
    function put(k, call, cols) {
      if (!has(calls, k)) order.push(k);
      calls[k] = {call: call, cols: cols};
    }
    recs.forEach(function (r) {
      if (r.undecided || r.via) return;
      var e = get(idx, r.key);
      if (r.decision === "accept") {
        (e.concerns || []).forEach(function (x) {
          if (callOf(x.c) || !(x.res || []).length) return;
          var cur = calls[x.c];
          if (cur && cur.call === "confirmed") return;
          var cols = cur ? cur.cols.slice() : [];
          x.res.forEach(function (col) { if (cols.indexOf(col) < 0) cols.push(col); });
          put(x.c, "dismissed", cols);
        });
      } else if (r.decision === "suggest" && r.rival) {
        if (callOf(r.rival) === "confirmed") return;
        var rv = (e.concerns || []).filter(function (x) { return x.c === r.rival; })[0];
        put(r.rival, "confirmed", rv.cols.slice());
      }
    });
    if (!order.length) return [];
    return validateItems(order.map(function (k) {
      var v = calls[k];
      return {key: k, call: v.call, note: v.call === "dismissed"
        ? "resolved by accepted " + v.cols.join(", ") + " fill" : "candidate accepted on " + v.cols.join(", ")};
    }), idx);
  }
  function callOf(k) {
    if (has(G.calls, k)) return G.calls[k];
    var e = get(G.idx, k);
    return e && e.g === "i" ? e.call0 : "";
  }

  // ---- the log ----
  function note(r) {            // a record the page now shows
    G.seen[r.id] = 1;
    G.shown[r.key] = Math.max(G.shown[r.key] || 0, ms(r.ts));
    if ("call" in r) G.calls[r.key] = r.undecided ? "" : r.call;
  }
  function readLocal() {
    try {
      var id = localStorage.getItem(LS_DEVICE);
      if (!id) { id = uuid().slice(0, 8); localStorage.setItem(LS_DEVICE, id); }
      G.device = id;
      var recs = JSON.parse(localStorage.getItem(LS_LOG) || "[]");
      G.own = Array.isArray(recs) ? recs.filter(function (r) { return r && r.id && r.key; }) : [];
    } catch (e) {
      G.storage = false;
      G.device = G.device || uuid().slice(0, 8);
      G.own = [];
    }
  }
  function writeLocal() {
    if (!G.storage) return;
    try { localStorage.setItem(LS_LOG, JSON.stringify(G.own)); }
    catch (e) { G.storage = false; }
  }
  // records the page does not show yet, oldest first; one older than what a key shows is dropped
  function fresh(recs) {
    return (recs || []).filter(function (r) { return r && r.id && r.key && !G.seen[r.id]; })
      .sort(function (a, b) { return ms(a.ts) - ms(b.ts); })
      .filter(function (r) {
        G.seen[r.id] = 1;
        if (ms(r.ts) < (G.shown[r.key] || 0)) return false;
        note(r);
        return true;
      });
  }
  function announce(recs) {
    var names = {}, n = 0;
    recs.forEach(function (r) {
      if (r.via || MACHINE[r.reviewer]) return;
      n++;
      names[r.reviewer || "someone"] = 1;
    });
    if (n) RA().toast(n + " new decision" + (n === 1 ? "" : "s") + " by " + Object.keys(names).join(", "));
  }
  function deliver(recs, tell) {
    if (!G.booted) { G.pending = G.pending.concat(recs); return; }
    var f = fresh(recs);
    if (!f.length) return;
    if (RA().applyRemote(f)) G.dirty = true;
    if (tell) announce(f);
  }
  setInterval(function () {
    var ra = RA();
    if (G.booted && G.dirty && ra && !ra.busy()) { G.dirty = false; ra.rerender(); }
  }, 1000);

  // ---- the shared log (the artifact's database) ----
  var NO_WRITE = "This page is not allowed to save your decisions to the shared log: it has to be shared with you " +
    "by email, as an editor, by the person who published it. Your decisions are kept in this browser only; " +
    "use download decisions before closing.";
  // the artifact's refusal codes for a viewer it does not let write; anything else is a plain failure
  function saveError(e) {
    var code = (e && e.code) || "";
    if (code === "invalid_argument" || code === "not_granted" || code === "revoked") return NO_WRITE;
    return "Your decisions could not be saved to the shared log (" + (code || (e && e.message) || "unknown") +
      "), so they are in this browser only. Use download decisions and send the file.";
  }
  function prefix() { return segment(G.uid || "anon") + "~" + segment(G.device) + "~"; }
  function body(n) {
    return {reviewer: G.me, email: G.email, uid: G.uid, device: G.device, n: n, built: G.built, dirs: G.dirs,
            updated: now(), records: G.own.slice(n * CHUNK, (n + 1) * CHUNK)};
  }
  // "shared": decisions go to the artifact's log; "saving": a write is in flight; "local": this browser only.
  // Not shown in the header (the banner speaks when a save fails); G.why2 keeps the reason for a test.
  function state(s, why) {
    G.shared = s;
    if (why) G.why2 = why;
  }
  function sync() {
    if (!G.db) return;
    if (G.syncing) { G.again = true; return; }
    G.syncing = true; G.again = false;
    state("saving");
    var todo = [], chunks = Math.ceil(G.own.length / CHUNK);
    for (var n = 0; n < chunks; n++) {
      var want = Math.min(CHUNK, G.own.length - n * CHUNK);
      if (G.synced[n] !== want) todo.push(n);
    }
    var p = Promise.resolve();
    todo.forEach(function (n) {
      p = p.then(function () {
        var b = body(n);
        return G.db.doc("logs/" + prefix() + n).set(b).then(function () { G.synced[n] = b.records.length; });
      });
    });
    p.then(function () {
      G.syncing = false;
      state("shared");
      if (G.again) sync();
    }, function (e) {
      G.syncing = false;
      state("local", "the shared log refused the write (" + ((e && (e.code || e.message)) || "unknown") + ")");
      if (RA()) RA().banner(saveError(e));
    });
  }
  function onDocs(snap) {
    var mine = prefix(), recs = [], lost = [];
    snap.docs.forEach(function (d) {
      var b = d.data();
      if (!b || !Array.isArray(b.records)) return;
      if (d.id.indexOf(mine) === 0) {           // this browser's own chunk: note what the log holds
        var n = Number(d.id.slice(mine.length));
        if (!has(G.synced, n) || G.first) G.synced[n] = b.records.length;
        b.records.forEach(function (r) { if (r && r.id && !G.seen[r.id] && !G.ownIds[r.id]) lost.push(r); });
        return;
      }
      G.remote[d.id] = b;
      recs = recs.concat(b.records);
    });
    if (lost.length) {                           // the shared log holds records this browser's storage lost
      lost.forEach(function (r) { G.ownIds[r.id] = 1; });
      G.own = lost.concat(G.own).sort(function (a, b) { return ms(a.ts) - ms(b.ts); });
      writeLocal();
      recs = recs.concat(lost);
    }
    var first = G.first;
    G.first = false;
    deliver(recs, !first);
    if (first) sync();
  }
  var connected = null;
  function connect() {
    if (connected) return connected;
    readLocal();
    G.ownIds = {};
    G.own.forEach(function (r) { G.ownIds[r.id] = 1; });
    if (!(window.claude && typeof claude.use === "function")) {      // opened from disk
      if (!G.me) { Store.caps.decide = false; G.why = "This copy was built without a reviewer (build_static.py --reviewer), so it cannot record decisions."; }
      connected = Promise.resolve(G.me);
      return connected;
    }
    connected = Promise.all([claude.use("db"), claude.use("downloads"), claude.use("user")]).then(function (c) {
      var db = c[0], user = c[2];
      G.dl = c[1];
      if (!user) return {db: db};
      return Promise.all([user.id(), user.me(), user.can("data.write")]).then(function (r) {
        return {db: db, uid: r[0], me: r[1], can: r[2]};
      });
    }).then(function (v) {
      var me = v.me || {};
      G.uid = v.uid || me.id || "";
      G.email = me.email || "";
      // the address first: the ledger derives initials from it, so the page and the store agree
      var who = initials(me.email) || initials(me.name);
      if (who) G.me = who;
      else { G.me = ""; Store.caps.decide = false; G.why = "The page could not tell who you are, so it cannot record decisions. Open it signed in to claude.ai."; }
      if (!v.db || !G.uid) { G.why2 = "the shared log is not available in this view"; return G.me; }
      if (v.can === false) {                       // the artifact has said this viewer cannot write
        G.why2 = "your access to this page is view-only"; G.noWrite = true; return G.me;
      }
      G.db = v.db;
      try {
        v.db.collection("logs").onSnapshot(onDocs, function (e) {
          G.db = null;
          state("local", "the shared log stopped answering (" + ((e && e.code) || "unknown") + ")");
        });
      } catch (e) { G.db = null; G.why2 = "the shared log could not be opened"; }
      return G.me;
    }).catch(function () { return G.me; });
    return connected;
  }

  // ---- writes ----
  function save(recs) {
    var ts = now(), batch = uuid();
    recs.forEach(function (r) {
      r.reviewer = G.me; r.ts = ts; r.id = uuid(); r.batch = batch; r.snapshot = G.snapshot; r.origin = "artifact";
      G.ownIds[r.id] = 1;
      note(r);
    });
    G.own = G.own.concat(recs);
    writeLocal();
    if (G.db) sync();
    else if (!G.storage && RA()) RA().banner("This browser will not keep these decisions after the page closes. Use download decisions before you leave.");
    return recs;
  }
  function write(make) {
    if (!Store.caps.decide) return Promise.reject(new Error(G.why || "this page cannot record decisions"));
    var run = function () {
      return new Promise(function (resolve) { resolve(save(make())); });
    };
    var p = G.chain.then(run, run);
    G.chain = p.catch(function () { /* the caller has the error */ });
    return p;
  }

  // ---- download ----
  function logs() {
    var out = [];
    if (G.own.length) out.push({reviewer: G.me, email: G.email, uid: G.uid, device: G.device, records: G.own});
    Object.keys(G.remote).sort().forEach(function (k) { out.push(G.remote[k]); });
    return out;
  }
  function count() {
    var n = 0;
    logs().forEach(function (l) { n += (l.records || []).length; });
    return n;
  }
  function download() {
    var ra = RA(), n = count();
    if (!n) return ra.toast("no decisions have been made on this page yet");
    var stamp = now().slice(0, 16).replace(/[-:]/g, "").replace("T", "_");
    var name = "pipelines_review_log_" + stamp + "_" + (G.me || "anon") + ".json";
    var data = JSON.stringify({built: G.built, dirs: G.dirs, downloaded: now(), logs: logs()}, null, 1);
    if (G.dl) {
      return G.dl.save({filename: name, data: data}).then(function () {
        ra.toast(n + " record" + (n === 1 ? "" : "s") + " saved as " + name);
      }, function (e) {
        if (e && e.code === "declined") return;
        ra.toast("the download did not go through (" + ((e && (e.code || e.message)) || "unknown") + ")");
      });
    }
    try {
      var a = document.createElement("a");
      a.href = URL.createObjectURL(new Blob([data], {type: "application/json"}));
      a.download = name;
      document.body.appendChild(a);
      a.click();
      a.remove();
      ra.toast(n + " record" + (n === 1 ? "" : "s") + " saved as " + name);
    } catch (e) { ra.toast("the download did not go through: " + e.message); }
  }
  function chrome() {
    var who = document.querySelector("header .who"), before = document.getElementById("theme-pick");
    if (!who || document.getElementById("export-btn")) return;
    var btn = document.createElement("button");
    btn.id = "export-btn"; btn.type = "button"; btn.className = "ghost";
    btn.textContent = "download decisions";
    btn.dataset.tip = "save every decision this page knows of as one file, to hand to whoever runs review_app/import_log.py";
    btn.onclick = download;
    who.insertBefore(btn, before);
    var label = document.getElementById("scope");
    if (label && RA() && RA().data) label.dataset.tip = "built " + RA().et(G.built) + " from snapshot " + G.snapshot + ". Decisions made elsewhere since then are not shown.";
    if (!G.db) state("local", G.why2 || "this copy was opened outside claude.ai");
    if (G.why) RA().banner(G.why);
    else if (G.noWrite) RA().banner(NO_WRITE);
    else if (!G.db && !G.storage) RA().banner("This browser will not keep decisions after the page closes, and the shared log is off. Use download decisions before you leave.");
  }

  var Store = {
    mode: "static",
    caps: {decide: true, refresh: false, push: false},
    whoami: function () { return connect(); },
    load: load,
    decide: function (records) {
      return write(function () {
        var recs = validateLines(records, G.idx);
        return recs.concat(concernCalls(recs, G.idx, callOf));
      });
    },
    item: function (records) { return write(function () { return validateItems(records, G.idx); }); },
    refresh: function () { return Promise.reject(new Error("this page cannot rebuild the dataset: run review_app/build_static.py")); },
    // called by the app once it has indexed a dataset: lay this browser's and the shared log's records on it
    ready: function () {
      var D = RA().data;
      G.shown = {}; G.seen = {}; G.calls = {};
      D.pipelines.forEach(function (p) {
        (p.lines || []).concat(p.items || []).forEach(function (o) { if (o.decided_at) G.shown[o.key] = ms(o.decided_at); });
      });
      G.booted = true;
      var recs = G.own.concat(G.pending);
      Object.keys(G.remote).forEach(function (k) { recs = recs.concat(G.remote[k].records); });
      G.pending = [];
      RA().applyRemote(fresh(recs));
      setTimeout(chrome, 0);
    },
    showGeo: function () { RA().toast("route geometry is not in this copy of the page"); },
    open: function (u) {         // window.open is not reliable inside an artifact; a real link is
      var a = document.createElement("a");
      a.href = u; a.target = "_blank"; a.rel = "noopener";
      document.body.appendChild(a);
      a.click();
      a.remove();
    },
    download: download,
    logs: logs,
    state: G
  };
  window.StaticStore = Store;
})();
