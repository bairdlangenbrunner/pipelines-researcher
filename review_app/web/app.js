/* Pipelines review app front end (milestone 4: bulk, items, summary, refresh). Vanilla JS, no modules, no build step
   (phase 2 inlines this file into an Apps Script HtmlService page). All I/O goes through Store;
   controls that need a capability read Store.caps and hide / disable themselves. */
(function () {
  "use strict";
  var T0 = performance.now();

  // ---- Store adapter (phase 1: local HTTP; phase 2 swaps in google.script.run) ----
  var NOT_YET = "this server cannot record decisions";
  var Store = {
    caps: {decide: false, refresh: false, push: false},
    _json: function (r) {
      return r.json().then(function (body) {
        if (!r.ok) throw new Error(body && body.error ? body.error : "HTTP " + r.status);
        return body;
      });
    },
    load: function () { return fetch("/api/data", {cache: "no-store"}).then(Store._json); },
    whoami: function () {
      return fetch("/api/whoami").then(Store._json).then(function (b) {
        if (b.caps) Store.caps = {decide: !!b.caps.decide, refresh: !!b.caps.refresh, push: !!b.caps.push};
        return b.reviewer;
      });
    },
    _post: function (url, records) {
      if (!Store.caps.decide) return Promise.reject(new Error(NOT_YET));
      return fetch(url, {method: "POST", headers: {"Content-Type": "application/json"},
                         body: JSON.stringify(records)}).then(Store._json).then(function (b) { return b.saved; });
    },
    decide: function (records) { return Store._post("/api/decide", records); },
    item: function (records) { return Store._post("/api/item", records); },
    refresh: function () {
      if (!Store.caps.refresh) return Promise.reject(new Error("this server cannot refresh the backend (started with --no-build)"));
      return fetch("/api/refresh", {method: "POST", headers: {"Content-Type": "application/json"}, body: "{}"}).then(Store._json);
    }
  };
  window.Store = Store;

  // ---- state ----
  var D = null;              // the dataset
  var ME = "";
  var LINES = [];            // every line, flat; l._i is its index, l._p its pipeline index
  var ITEMS = [];            // every item, flat; it._p its pipeline index
  var FS = defaults();       // filter state (what the chips and controls show)
  var S = {
    visible: [],             // pipeline indexes passing the filter
    pipe: -1,                // index into D.pipelines
    line: -1,                // selected line index (LINES)
    pin: -1,                 // a pipeline opened by link that the filters would hide
    shown: [],               // line indexes drawn on the current card, in order
    stay: {},                // line keys decided this session: kept in view even if the filter would drop them
    saving: {},              // line / item keys with a save in flight
    tab: "lines",            // the card's tab: "lines" | "items"
    igOpen: {},              // item kind -> details open state (survives a re-render)
    session: {}              // key -> the latest non-undone record this reviewer saved in this page session
  };
  var ITEM_BY_KEY = {};
  var ITEM_CALLS = {concern: ["confirmed", "dismissed", "needs_research"]};
  var OTHER_CALLS = ["noted", "todo", "dismissed"];
  var CALL_HELP = {confirmed: "the concern stands", dismissed: "the concern is closed", needs_research: "goes to a research / Update worklist",
                   noted: "seen, nothing to do", todo: "to do later"};
  var MACHINE = {"backend sync": 1, "push": 1};   // not people: their records never count as reviewed
  var LINE_BY_KEY = {};
  var VERB = {accept: "accepted", hold: "held", reject: "rejected", suggest: "suggested"};
  var $ = function (id) { return document.getElementById(id); };
  var LINE_KINDS = ["ref", "fill", "status", "oo", "route", "new_row"];
  var ITEM_KINDS = ["concern", "wikidiff", "routeqc", "route_suggestion", "monitor", "flag", "escalation",
                    "unresolved", "confirmed", "other"];
  var KIND_LABEL = {ref: "ref", fill: "fill", status: "status", oo: "owners tab", route: "route", new_row: "new row",
                    concern: "concern", wikidiff: "wiki diff", routeqc: "route QC", route_suggestion: "route suggestion",
                    monitor: "monitor", flag: "flag", escalation: "escalation", unresolved: "unresolved",
                    confirmed: "confirmed", other: "other"};
  var DEC = ["undecided", "accept", "hold", "reject"];

  function defaults() {
    return {decision: "undecided", kind: "", tier: "", class_out: "", dir: "", column: "", q: "", row: "",
            contested: false, single: false, owners: false, landed: false};
  }
  function esc(s) {
    return String(s == null ? "" : s).replace(/[&<>"']/g, function (c) {
      return {"&": "&amp;", "<": "&lt;", ">": "&gt;", '"': "&quot;", "'": "&#39;"}[c];
    });
  }
  function isItemKind(k) { return ITEM_KINDS.indexOf(k) >= 0; }
  function blankv(v) { return v == null || String(v).trim() === ""; }
  function dirLabel(d) { return String(d || "").split("/").pop(); }
  function tierOf(l) { return l.tier === "high" || l.tier === "medium" || l.tier === "low" ? l.tier : "untiered"; }
  // a line is decided only by a person's latest record; a machine record (backend sync, push)
  // leaves it undecided (the pre-fill is shown, nothing is pushed)
  function cur(l) { return l.reviewed && l.decision ? l.decision : null; }
  function dstate(o) {
    var d = o._item ? o.call : cur(o);
    return d ? d : "undecided";
  }
  function timeOf(iso) { return String(iso || "").replace("T", " ").slice(11, 16); }
  function decisionText(l) {
    if (l.reviewed && l.decision) return (VERB[l.decision] || l.decision) + " by " + (l.decided_by || "?") + " " + timeOf(l.decided_at);
    if (l.decision && l.decided_by === "backend sync") return "in backend (synced by backend sync, not reviewed)";
    if (l.decision && l.decided_by) return "pre-filled by " + l.decided_by + " (not reviewed)";
    return "";
  }
  // contested linking: a line on a column that an OPEN validity concern (no call yet) names is held
  function lockCols(l, p) {
    var open = {};
    p.items.forEach(function (it) {
      if (it.kind !== "concern" || it.call || !it.contested || typeof it.contested !== "object") return;
      Object.keys(it.contested).forEach(function (c) { open[c] = 1; });
    });
    var cols = [l.column].concat(l.value_cols || []);
    if (l.kind === "status") cols.push("Status");
    return cols.filter(function (c, i) { return c && cols.indexOf(c) === i && open[c]; });
  }
  function rowLabel(l) {
    if (l.kind === "new_row") return "new row";
    if (l.kind === "oo") {
      return "owners tab row " + (l.sheet_row == null ? "?" : l.sheet_row) +
        (l.tracker_sheet_row ? " (tracker row " + l.tracker_sheet_row + ")" : "");
    }
    return l.sheet_row == null ? "row not in snapshot" : "row " + l.sheet_row;
  }
  function segRow(l) { return l.tracker_sheet_row || l.sheet_row; }

  // ---- theme ----
  function initTheme() {
    try {
      var t = localStorage.getItem("review-theme");
      if (t) document.documentElement.setAttribute("data-theme", t);
    } catch (e) { /* storage blocked: follow the system theme */ }
    $("theme").onclick = function () {
      var cur = document.documentElement.getAttribute("data-theme") ||
        (matchMedia("(prefers-color-scheme: dark)").matches ? "dark" : "light");
      var next = cur === "dark" ? "light" : "dark";
      document.documentElement.setAttribute("data-theme", next);
      try { localStorage.setItem("review-theme", next); } catch (e) { /* ignore */ }
    };
  }

  // ---- derived data, once per load ----
  function prepare() {
    LINES = []; ITEMS = []; LINE_BY_KEY = {}; ITEM_BY_KEY = {};
    D.pipelines.forEach(function (p, pi) {
      p._cont = {};
      p.items.forEach(function (it) {
        it._item = true; it._p = pi; it._i = ITEMS.length; ITEM_BY_KEY[it.key] = it;
        var c = it.contested || {};
        Object.keys(c).forEach(function (col) { if (!(col in p._cont) || c[col]) p._cont[col] = c[col] || ""; });
        ITEMS.push(it);
      });
      p.lines.forEach(function (l) {
        l._p = pi; l._i = LINES.length; LINE_BY_KEY[l.key] = l;
        var cols = [l.column].concat(l.value_cols || []);
        if (l.kind === "status") cols.push("Status");
        l._contCols = cols.filter(function (c, i) { return c && cols.indexOf(c) === i && (c in p._cont); });
        l._cont = l._contCols.length > 0;
        l._rows = [l.sheet_row, l.tracker_sheet_row].filter(function (x) { return x != null; });
        LINES.push(l);
      });
      p._hay = [p.name, p.pid, p.country, p.status].concat(p.segments.map(function (s) { return s.sheet_row + " " + s.segment; }))
        .join(" ").toLowerCase();
      p._rows = p.segments.map(function (s) { return s.sheet_row; });
    });
  }

  // ---- filters ----
  function parseRows(s) {      // "357-400, 1141" -> [[357,400],[1141,1141]]; null when empty / unreadable
    var out = [];
    s.replace(/\s*[-–]\s*/g, "-").split(/[,;\s]+/).forEach(function (t) {
      var m = /^(\d+)(?:-(\d+))?$/.exec(t);
      if (m) { var a = +m[1], b = m[2] ? +m[2] : a; out.push([Math.min(a, b), Math.max(a, b)]); }
    });
    return out.length ? out : null;
  }
  function inRows(rows, ranges) {
    return rows.some(function (r) { return ranges.some(function (g) { return r >= g[0] && r <= g[1]; }); });
  }
  // One matcher for lines and items. `skip` names a facet to ignore (for faceted chip counts).
  function match(o, p, fs, skip, ranges, q) {
    var item = !!o._item;
    if (!item && !fs.landed && o.in_backend) return false;
    if (skip !== "kind") {
      if (fs.kind) { if (o.kind !== fs.kind) return false; }
      else if (item) return false;
    }
    if (skip !== "decision" && fs.decision && dstate(o) !== fs.decision && !(!item && S.stay[o.key])) return false;
    if (skip !== "tier" && fs.tier && (item || tierOf(o) !== fs.tier)) return false;
    if (fs.class_out && o.class_out !== fs.class_out) return false;
    if (fs.dir && o.dir !== fs.dir) return false;
    if (fs.column && (item || o.column !== fs.column)) return false;
    if (fs.contested && !(item ? Object.keys(o.contested || {}).length : o._cont)) return false;
    if (fs.single && (item || o.kind !== "status" || !(o.publishers < 2))) return false;
    if (fs.owners && (item || o.kind !== "oo")) return false;
    if (fs.row) {
      if (!ranges) return false;
      var rows = item ? (o.sheet_row != null ? [o.sheet_row] : []) : o._rows;
      if (!inRows(rows, ranges)) return false;
    }
    if (q && p._hay.indexOf(q) < 0) return false;
    return true;
  }
  function pipeMatches(p, pi) {
    var ranges = parseRows(FS.row), q = FS.q.trim().toLowerCase(), n = 0, todo = 0, ni = 0;
    p.lines.forEach(function (l) {
      if (!match(l, p, FS, null, ranges, q)) return;
      n++;
      if (!cur(l)) todo++;
    });
    p.items.forEach(function (it) { if (match(it, p, FS, null, ranges, q)) ni++; });
    p._n = n; p._todo = todo; p._ni = ni;
    return n + ni;
  }
  function refilter(keep) {
    var sel = D.pipelines[S.pipe];
    S.visible = [];
    var nl = 0, ni = 0;
    D.pipelines.forEach(function (p, i) {
      var m = pipeMatches(p, i);
      nl += p._n; ni += p._ni;
      if (m || i === S.pin) S.visible.push(i);
    });
    $("count").textContent = nl + " line" + (nl === 1 ? "" : "s") + (ni ? " + " + ni + " item" + (ni === 1 ? "" : "s") : "") +
      " on " + S.visible.length + " pipeline" + (S.visible.length === 1 ? "" : "s");
    if (S.visible.indexOf(S.pipe) < 0) S.pipe = S.visible.length ? S.visible[0] : -1;
    if (D.pipelines[S.pipe] !== sel) { S.line = -1; S.tab = "lines"; }
    renderChips();
    renderActive();
    renderProgress();
    renderQueue();
    renderCard();
    if (keep !== true) writeRoute(false);
  }
  function facetCounts(facet, values) {
    var ranges = parseRows(FS.row), q = FS.q.trim().toLowerCase(), c = {};
    values.forEach(function (v) { c[v] = 0; });
    function tally(o, p, v) { if (match(o, p, FS, facet, ranges, q) && v in c) c[v]++; }
    D.pipelines.forEach(function (p) {
      p.lines.forEach(function (l) {
        tally(l, p, facet === "decision" ? dstate(l) : facet === "kind" ? l.kind : tierOf(l));
      });
      if (facet === "kind" || (facet === "decision" && isItemKind(FS.kind))) {
        p.items.forEach(function (it) { tally(it, p, facet === "kind" ? it.kind : dstate(it)); });
      }
    });
    return c;
  }
  function chipRow(id, facet, values, labels, anyLabel, totals) {
    var counts = facetCounts(facet, values), h = "";
    if (anyLabel) h += '<button type="button" class="fchip" data-f="' + facet + '" data-v="" aria-pressed="' +
      (FS[facet] === "") + '">' + anyLabel + "</button>";
    values.forEach(function (v) {
      if (totals && !totals[v] && FS[facet] !== v) return;      // a kind the scope does not have
      h += '<button type="button" class="fchip' + (counts[v] ? "" : " zero") + '" data-f="' + facet + '" data-v="' + v +
        '" aria-pressed="' + (FS[facet] === v) + '">' + esc(labels[v] || v) + ' <span class="n">' + counts[v] + "</span></button>";
    });
    document.querySelector("#" + id + " .chips").innerHTML = h;
  }
  function renderChips() {
    var lab = {};
    chipRow("cr-decision", "decision", DEC, lab, "any");
    var tot = {};
    LINES.forEach(function (l) { tot[l.kind] = 1; });
    ITEMS.forEach(function (i) { tot[i.kind] = 1; });
    chipRow("cr-kind", "kind", LINE_KINDS.concat(ITEM_KINDS), KIND_LABEL, "", tot);
    chipRow("cr-tier", "tier", ["high", "medium", "low", "untiered"], lab, "any");
  }
  function fillSelect(id, values) {
    var s = $(id);
    values.forEach(function (v) { var o = document.createElement("option"); o.value = v; o.textContent = id === "f-dir" ? dirLabel(v) : v; s.appendChild(o); });
  }
  function uniq(arr) { return arr.filter(function (x, i) { return x && arr.indexOf(x) === i; }).sort(); }
  function initFilters() {
    fillSelect("f-class_out", uniq(LINES.map(function (l) { return l.class_out; }).concat(ITEMS.map(function (i) { return i.class_out; }))));
    var cols = uniq(LINES.map(function (l) { return l.column; }));
    cols.sort(function (a, b) {
      var ia = D.columns.indexOf(a), ib = D.columns.indexOf(b);
      return (ia < 0 ? 9999 : ia) - (ib < 0 ? 9999 : ib);
    });
    fillSelect("f-column", cols);
    fillSelect("f-dir", D.dirs);
    $("filters").addEventListener("click", function (e) {
      var b = e.target.closest("button[data-f]");
      if (b) {
        var f = b.getAttribute("data-f"), v = b.getAttribute("data-v");
        FS[f] = (FS[f] === v && v !== "") ? (f === "decision" ? "" : "") : v;
        return changed();
      }
      var c = e.target.closest("button[data-clear]");
      if (c) { clearOne(c.getAttribute("data-clear")); changed(); }
    });
    ["class_out", "column", "dir"].forEach(function (f) {
      $("f-" + f).onchange = function () { FS[f] = this.value; changed(); };
    });
    ["contested", "single", "owners", "landed"].forEach(function (f) {
      $("f-" + f).onchange = function () { FS[f] = this.checked; changed(); };
    });
    $("f-q").oninput = function () { FS.q = this.value; changed(true); };
    $("f-row").oninput = function () { FS.row = this.value; changed(true); };
    $("f-more").onclick = function () { toggleMore(); };
    $("f-reset").onclick = function () { FS = defaults(); syncControls(); changed(); };
  }
  function changed(replace) { S.pin = -1; S.stay = {}; refilter(true); writeRoute(replace === true); }
  function clearOne(id) {
    var d = defaults();
    FS[id] = d[id];
    syncControls();
  }
  function toggleMore(open) {
    var box = $("more-filters");
    box.hidden = open == null ? !box.hidden : !open;
    $("f-more").setAttribute("aria-expanded", String(!box.hidden));
    renderActive();
  }
  function syncControls() {
    ["class_out", "column", "dir"].forEach(function (f) {
      $("f-" + f).value = FS[f];
      if ($("f-" + f).value !== FS[f]) { FS[f] = ""; $("f-" + f).value = ""; }
    });
    ["contested", "single", "owners", "landed"].forEach(function (f) { $("f-" + f).checked = FS[f]; });
    $("f-q").value = FS.q; $("f-row").value = FS.row;
  }
  // Every filter that is set is a removable chip, so a control tucked behind "More filters"
  // never filters silently.
  function renderActive() {
    var chips = [], n = 0;
    function chip(id, text, hidden) {
      chips.push('<span class="chip on">' + esc(text) + ' <button type="button" data-clear="' + id +
        '" title="clear this filter" aria-label="clear ' + esc(text) + '">&times;</button></span>');
      if (hidden) n++;
    }
    if (FS.class_out) chip("class_out", "class: " + FS.class_out, true);
    if (FS.column) chip("column", "column: " + FS.column, true);
    if (FS.dir) chip("dir", "dir: " + dirLabel(FS.dir), true);
    if (FS.contested) chip("contested", "contested", false);
    if (FS.single) chip("single", "single-source status", false);
    if (FS.owners) chip("owners", "owners tab", false);
    if (FS.landed) chip("landed", "incl. lines already in the backend", false);
    $("active-filters").innerHTML = chips.join(" ");
    $("active-filters").hidden = !chips.length;
    $("f-more").textContent = ($("more-filters").hidden ? "More filters" : "Fewer filters") + (n ? " (" + n + ")" : "");
  }
  function renderProgress() {
    var total = 0, done = 0;
    LINES.forEach(function (l) { if (!l.in_backend || FS.landed) { total++; if (cur(l)) done++; } });
    $("progress-bar").style.width = total ? (100 * done / total) + "%" : "0";
    $("progress-text").textContent = done + " of " + total + " lines decided";
  }

  // ---- queue ----
  function renderQueue() {
    var h = [];
    S.visible.forEach(function (i) {
      var p = D.pipelines[i];
      var dots = {};
      p.lines.forEach(function (l) { dots[tierOf(l)] = 1; });
      var dd = ["high", "medium", "low"].filter(function (t) { return dots[t]; })
        .map(function (t) { return '<span class="dot ' + t + '" title="' + t + '"></span>'; }).join("");
      var rows = p.segments.map(function (s) { return s.sheet_row; }).filter(function (x) { return x != null; });
      var where = p.pid.indexOf("new:") === 0 ? "new row" : (p.pid === "scope" ? "scope" :
        (rows.length ? "row " + rows[0] + (rows.length > 1 ? " +" + (rows.length - 1) : "") : "no row"));
      var badge = p._todo ? '<span class="n todo" title="lines nobody has decided">' + p._todo + " to decide</span>"
        : (p._n ? '<span class="n">' + p._n + " &middot; done</span>" : (p._ni ? '<span class="n">' + p._ni + " item" + (p._ni === 1 ? "" : "s") + "</span>" : '<span class="n"></span>'));
      h.push('<li data-i="' + i + '"' + (i === S.pipe ? ' class="sel"' : "") + '><div class="pname">' + esc(p.name || "(no name)") +
        '</div><div class="pmeta"><span>' + esc(p.pid.indexOf("new:") === 0 ? "candidate" : p.pid) + " &middot; " + esc(where) +
        '</span><span class="grow"></span>' + badge + '</div>' + (dd ? '<div class="dots">' + dd + "</div>" : "") + "</li>");
    });
    $("pipes").innerHTML = h.join("");
  }
  function selectPipe(i, lineIdx) {
    S.pipe = i;
    S.tab = "lines";
    S.line = lineIdx == null ? -1 : lineIdx;
    var prev = $("pipes").querySelector("li.sel");
    if (prev) prev.classList.remove("sel");
    var li = $("pipes").querySelector('li[data-i="' + i + '"]');
    if (li) { li.classList.add("sel"); li.scrollIntoView({block: "nearest"}); }
    renderCard();
    writeRoute(true);
  }

  // ---- card pieces ----
  function urlLink(u, long) {
    var t = u.length > (long || 78) ? u.slice(0, (long || 78) - 1) + "…" : u;
    if (!/^https?:\/\//i.test(u)) return esc(u);
    return '<a href="' + esc(u) + '" target="_blank" rel="noopener" title="' + esc(u) + '">' + esc(t) + " ↗</a>";
  }
  function splitUrls(text) {
    return String(text || "").split(/,\s*(?=https?:\/\/)|\n+/).map(function (s) { return s.trim(); }).filter(Boolean);
  }
  function chip(text, cls, title) {
    return '<span class="chip' + (cls ? " " + cls : "") + '"' + (title ? ' title="' + esc(title) + '"' : "") + ">" + esc(text) + "</span>";
  }
  function tierChip(l) {
    var t = tierOf(l);
    return chip(t === "untiered" ? "untiered" : t, t === "untiered" ? "" : t,
      t === "untiered" ? "no confidence tier on this record: defaults to hold" : "confidence tier (rule 4)");
  }
  function vchips(u, l) {
    var v = null;
    (l.verifications || []).forEach(function (x) { if (x.url === u) v = x; });
    if (!v) return '<span class="vchips">' + chip("not checked", "", "no verification record for this URL") + "</span>";
    function one(label, val) {
      return chip((val ? "✓ " : "✗ ") + label, val ? "ok" : "bad");
    }
    var out = one("ok", !!v.ok) + one("contains value", !!v.contains_value) + one("names pipeline", !!v.name_found);
    return '<span class="vchips"' + (v.note ? ' title="' + esc(v.note) + '"' : "") + ">" + out + "</span>";
  }
  // The tint of the cell a line would write: tier colour, or re-verified blue; never on an empty cell.
  function tintClass(l) {
    if (l.class_out === "REVERIFIED") return "tint-rev";
    var t = tierOf(l);
    return t === "untiered" ? "" : "tint-" + t;
  }
  function refBlock(l) {
    var cur = splitUrls(l.current_ref), prop = l.proposed_refs || [];
    var text = l.ref_cell_text || "";
    if (l.kind === "status" && l.class_out === "STALE") {
      return '<div class="refcell"><span class="k">[ref]</span> <span class="muted">none by design (stale-status flag)</span></div>';
    }
    var h = '<div class="refcell"><span class="k">[ref] now</span> ';
    if (!cur.length) h += '<span class="blank">blank</span>';
    else h += "<ul>" + cur.map(function (u) { return '<li class="was">' + urlLink(u) + "</li>"; }).join("") + "</ul>";
    h += "</div>";
    var cell = text ? splitUrls(text) : prop.slice();
    if (!cell.length) {
      var why = l.class_out === "DEAD_LINK" ? "current ref is a dead link, no replacement found"
        : (l.class_out === "REVERIFIED" ? "current ref re-verified, nothing to change" : "no URL proposed");
      return h + '<div class="refcell"><span class="k">[ref] would be</span> <span class="muted">' + esc(why) + "</span></div>";
    }
    h += '<div class="refcell"><span class="k">[ref] would be</span><div class="cellnew ' + tintClass(l) + '"><ul>' +
      cell.map(function (u) {
        var isNew = prop.indexOf(u) >= 0;
        return '<li class="' + (isNew ? "" : "kept") + '">' + urlLink(u) + (isNew ? vchips(u, l) : ' <span class="faint">(kept)</span>') + "</li>";
      }).join("") + "</ul></div></div>";
    return h;
  }
  function concernNote(p, col) {
    var t = p._cont[col];
    return '<div class="concern-inline">' + chip("contested", "cont") + " " + (t ? esc(t) : "a validity concern contests this value (no detail recorded)") + "</div>";
  }
  function changesHtml(l, p, skipCol) {
    var pv = l.proposed_values || {}, cols = Object.keys(pv), cur = l.current || {};
    if (!cols.length) {          // nothing proposed: show the current values this [ref] covers, for context
      cols = (l.value_cols || []).filter(function (c) { return !blankv(cur[c]); }).slice(0, 8);
    }
    var rows = [], extra = 0;
    cols.forEach(function (c) {
      if (c === skipCol) return;
      var was = cur[c], has = c in pv, now = pv[c];
      var contested = (c in p._cont) && !blankv(was);
      var wasH = blankv(was) ? '<span class="blank">blank</span>'
        : (contested ? '<span class="tint-cont">' + esc(was) + "</span>" : '<span class="was">' + esc(was) + "</span>");
      var v;
      if (!has) v = '<span class="' + (contested ? "" : "") + '">' + (blankv(was) ? wasH : (contested ? wasH : esc(was))) + "</span>";
      else if (blankv(now) && blankv(was)) { extra++; return; }
      else if (blankv(now)) v = wasH + '<span class="arrow">→</span><span class="blank">(clear)</span>';
      else if (!blankv(was) && String(was).trim() === String(now).trim()) {
        v = (contested ? wasH : esc(was)) + ' <span class="same">(unchanged)</span>';
      } else v = wasH + '<span class="arrow">→</span><span class="newv">' + esc(now) + "</span>";
      rows.push('<div class="k">' + esc(c) + '</div><div class="v">' + v + (contested ? concernNote(p, c) : "") + "</div>");
    });
    return rows.length ? '<div class="chg">' + rows.join("") + "</div>" : "";
  }
  function unitBox(label, inner) {
    return '<div class="unit"><div class="ulabel">' + esc(label) + "</div>" + inner + "</div>";
  }
  function lineCols(l) {
    var c = l.column || "";
    var n = (l.value_cols || []).length;
    if (l.kind === "status") return "Status";
    if (l.kind === "route") return "Route";
    if (l.kind === "oo") return c + (Object.keys(l.proposed_values || {}).length > 1 ? " +" + (Object.keys(l.proposed_values).length - 1) : "");
    return c + (n > 1 ? " +" + (n - 1) : "");
  }
  function lineBody(l, p) {
    if (l.kind === "new_row") return newRowBody(l);
    if (l.kind === "route") return routeBody(l, p);
    if (l.kind === "status") return statusBody(l, p);
    if (l.kind === "fill" || l.kind === "oo") return unitBox("value + [ref] together (decided as one)", changesHtml(l, p) + refBlock(l));
    return (changesHtml(l, p) ? '<div class="unit">' + changesHtml(l, p) + "</div>" : "") + refBlock(l);   // ref
  }
  function statusBody(l, p) {
    var cs = l.current_status || "", ps = l.proposed_status || "";
    var cont = ("Status" in p._cont) && !blankv(cs);
    var h = '<div class="bigstatus">Status: ' + (blankv(cs) ? '<span class="blank">blank</span>'
      : (cont ? '<span class="tint-cont">' + esc(cs) + "</span>" : '<span class="was">' + esc(cs) + "</span>"));
    if (!blankv(ps) && ps !== cs) h += '<span class="arrow">→</span><span class="newv">' + esc(ps) + "</span>";
    else if (!blankv(ps)) h += ' <span class="same">(unchanged)</span>';
    h += "</div>";
    if (cont) h += concernNote(p, "Status");
    var facts = [];
    if (l.verdict) facts.push(chip("verdict: " + l.verdict));
    if (l.evidence_date) facts.push(chip("evidence " + l.evidence_date));
    if (l.class_out === "STALE") facts.push(chip("stale flag", "warn"));
    if (l.publishers < 2) facts.push(chip("single source", "single", "fewer than 2 distinct publishers: a status change stays green only on 2+ (rule 4)"));
    else facts.push(chip(l.publishers + " publishers"));
    h += '<div class="row1">' + facts.join(" ") + "</div>";
    if (l.staleness_rule) h += '<div class="faint" style="margin:4px 0">' + esc(l.staleness_rule) + "</div>";
    return unitBox("status + [ref] together (decided as one)", changesHtml(l, p, "Status") + refBlock(l)) .replace('<div class="ulabel">', h + '<div class="ulabel">');
  }
  function routeBody(l, p) {
    var geo = l.geometry_file ? '/geo/' + encodeURI(String(l.dir).replace(/^batches\//, "") + "/" + l.geometry_file) : "";
    var cur = l.current_route_accuracy, sug = l.suggested_route_accuracy;
    var rows = [
      ["Candidate length", l.length_km == null ? "" : l.length_km + " km"],
      ["Sheet length", l.sheet_length_km == null ? "" : l.sheet_length_km + " km"],
      ["Ratio", l.length_ratio == null ? "" : String(l.length_ratio)]
    ].filter(function (r) { return r[1] !== ""; }).map(function (r) { return '<div class="k">' + r[0] + '</div><div class="v">' + esc(r[1]) + "</div>"; });
    rows.push('<div class="k">RouteAccuracy</div><div class="v">' + (blankv(cur) ? '<span class="blank">blank</span>' : '<span class="was">' + esc(cur) + "</span>") +
      (blankv(sug) ? "" : '<span class="arrow">→</span><span class="newv">' + esc(sug) + "</span>") + "</div>");
    rows.push('<div class="k">QC</div><div class="v">' + (l.qc_passed ? chip("✓ passed", "ok") : chip("✗ did not pass", "bad")) + "</div>");
    rows.push('<div class="k">Geometry</div><div class="v">' + (geo ? '<a href="' + esc(geo) + '" target="_blank" rel="noopener"><code>' + esc(l.geometry_file) + "</code> ↗</a>" : '<span class="muted">none</span>') + "</div>");
    return '<div class="chg">' + rows.join("") + '</div><div class="faint" style="margin-top:4px">Accepting records approval for the §8 apply; it writes no cell.</div>';
  }
  function newRowBody(l) {
    var vals = l.proposed_values || {}, refs = l.proposed_refs || {};
    var tr = Object.keys(vals).filter(function (c) { return !blankv(vals[c]); }).map(function (c) {
      return "<tr><td>" + esc(c) + "</td><td>" + esc(vals[c]) + "</td></tr>";
    });
    Object.keys(refs).forEach(function (c) {
      var us = Array.isArray(refs[c]) ? refs[c] : [refs[c]];
      if (!us.length) return;
      tr.push("<tr><td>" + esc(c) + "</td><td>" + us.map(function (u) { return urlLink(u); }).join("<br>") + "</td></tr>");
    });
    var h = l["class"] === "matched_existing"
      ? '<div class="row1">' + chip("matches existing " + (l.matched_project_id || ""), "newrow") + ' <span class="faint">candidate data for a pipeline already tracked</span></div>' : "";
    return h + '<table class="rowdata">' + tr.join("") + "</table>";
  }
  function detailsHtml(l) {
    var d = [];
    if (l.notes) d.push('<div class="dtxt"><span class="k">researcher notes:</span> ' + esc(l.notes) + "</div>");
    (l.verifications || []).forEach(function (v) {
      if (v.note) d.push('<div class="dtxt"><span class="k">' + esc(v.url) + ":</span> " + esc(v.note) + "</div>");
    });
    var misc = ["class " + (l.class_in || "?") + " → " + (l.class_out || "?"),
                "link live: " + (l.link_live == null ? "unknown" : l.link_live)];
    if (l.kind === "oo") misc.push("owners tab row " + l.sheet_row + (l.tracker_sheet_row ? ", tracker row " + l.tracker_sheet_row : ""));
    d.push('<div class="dtxt"><span class="k">record:</span> ' + esc(misc.join(" · ")) + "</div>");
    return '<details data-more><summary>details (d)</summary>' + d.join("") + "</details>";
  }
  function lineHtml(l, p) {
    var chips = [chip(KIND_LABEL[l.kind], l.kind === "new_row" ? "newrow" : (l.kind === "oo" ? "oo" : "")),
                 l.kind === "new_row" ? chip(tierOf(l) === "untiered" ? "untiered" : tierOf(l), tierOf(l) === "untiered" ? "" : tierOf(l)) : tierChip(l)];
    if (l.class_out && l.kind !== "new_row") chips.push(chip(l.class_out, l.class_out === "REVERIFIED" ? "rev" : ""));
    if (l.kind !== "new_row" && l.kind !== "route") {
      chips.push(chip(l.independent ? "independent" : "not independent", l.independent ? "ok" : "", "a second, independent publisher (preferred, never owed)"));
      if (l.source_language) chips.push(chip("lang " + l.source_language));
    }
    var lock = lockCols(l, p);
    if (l._cont) chips.push(chip("contested", "cont", "a validity concern contests a value on this line"));
    if (lock.length) chips.push(chip("held: concern open", "warn", "a validity concern contests " + lock.join(", ") + " and has no call yet; accept is refused until it does (hold / reject are still allowed)"));
    if (l.in_backend) chips.push(chip("in backend", "", "the snapshot already holds this value and these refs"));
    if (l.sheet_row_moved) chips.push(chip("row re-resolved", "", "the record's sheet_row was stale; this is the live row"));
    var title = l.kind === "new_row" ? (l.name || "candidate") : lineCols(l);
    var h = '<div class="row1"><span class="col">' + esc(title) + "</span> " + chips.join(" ") +
      '<span class="where">' + esc(rowLabel(l)) + " &middot; " + esc(dirLabel(l.dir)) + "</span></div>";
    h += lineBody(l, p);
    var foot = ["default: " + (l.default || "hold")];
    if (l.also_in && l.also_in.length) foot.push("also in " + l.also_in.map(dirLabel).join(", "));
    h += '<div class="faint">' + esc(foot.join(" · ")) + "</div>";
    h += detailsHtml(l);
    var dis = !Store.caps.decide;
    h += '<div class="controls">' + [["accept", "a"], ["hold", "h"], ["reject", "r"]].map(function (b) {
      var off = dis || (b[0] === "accept" && lock.length);
      return '<button type="button" class="b-' + b[0] + '" data-decide="' + b[0] + '"' +
        (off ? ' aria-disabled="true" title="' + esc(dis ? NOT_YET : "held: a concern on " + lock.join(", ") + " is open") + '"' : "") +
        ' aria-pressed="' + (cur(l) === b[0]) + '">' + b[0] + " (" + b[1] + ")</button>";
    }).join("") + '<button type="button" class="ghost" data-undo="1"' + (cur(l) ? "" : " disabled") + ' title="back to undecided (u)">undo (u)</button>' +
      '<span class="dstat" id="dstat-' + l._i + '" role="status">' + esc(decisionText(l)) + "</span></div>";
    return h;
  }

  // ---- items ----
  var HIDE = {call_note: 1, decided_by: 1, decided_at: 1, decision_note: 1, key: 1, dir: 1, also_in: 1, sheet_row: 1, sheet_row_moved: 1, contested: 1, "default": 1, call: 1, reviewed: 1,
              kind: 1, project_id: 1, wiki: 1, pipeline_name: 1, segment_name: 1, value_cols: 1, values: 1, primary_value_col: 1,
              primary_value: 1, _item: 1, _p: 1, countries: 1};
  var BODY = ["recommendation", "action", "detail", "summary", "monitor_reason", "researcher_notes", "staged_note", "staleness_rule", "corridor_desc"];
  function itemHead(it) {
    switch (it.kind) {
      case "concern": return (it.concern_type || "concern") + (it.verdict ? " — " + it.verdict : "");
      case "confirmed": return (it.ref_col && it.ref_col.indexOf("__") !== 0 ? it.ref_col : "existence / status") + (it.verdict ? " — " + it.verdict : "");
      case "unresolved": return (it.primary_value_col || it.ref_col || "") + " unresolved";
      case "wikidiff": return (it.field || "wiki") + " — " + (it.class_out || "");
      case "routeqc": return (it.check || "route QC") + (it.severity ? " (" + it.severity + ")" : "");
      case "route_suggestion": return "route " + (it.class_out === "ROUTE_PARTIAL" ? "partial" : "suggested");
      case "monitor": return it.name || "monitor";
      case "flag": return it.check || "flag";
      case "escalation": return it.title || "escalation";
      default: return (it.ref_col || "") + " " + (it.class_in || "") + " → " + (it.class_out || "");
    }
  }
  function itemBody(it) {
    var h = "", used = {};
    if (it.kind === "wikidiff") {
      h += '<div class="body">sheet: <b>' + (blankv(it.sheet_value) ? '<span class="blank">blank</span>' : esc(it.sheet_value)) + "</b> &middot; wiki: <b>" +
        (blankv(it.wiki_value) ? '<span class="blank">blank</span>' : esc(it.wiki_value)) + "</b>" +
        (it.staged_value ? " &middot; staged: <b>" + esc(it.staged_value) + "</b>" : "") + "</div>";
      used.sheet_value = used.wiki_value = used.staged_value = 1;
    }
    if (it.kind === "routeqc" && (it.measured || it.expected)) {
      h += '<div class="body">measured: ' + esc(it.measured || "") + " &middot; expected: " + esc(it.expected || "") + "</div>";
      used.measured = used.expected = 1;
    }
    if (it.kind === "route_suggestion") {
      h += '<div class="body">' + esc(it.start_name || "?") + " → " + esc(it.end_name || "?") + "</div>";
      used.start_name = used.end_name = 1;
    }
    var src = null;
    BODY.forEach(function (k) { if (!src && !blankv(it[k]) && typeof it[k] === "string") src = k; });
    if (src) {
      var t = it[src], cut = t.length > 500;
      h += '<div class="body">' + esc(cut ? t.slice(0, 500) + "…" : t) + "</div>";
      if (!cut) used[src] = 1;
    }
    return {html: h, used: used};
  }
  function fieldRows(it, used) {
    var rows = [];
    Object.keys(it).forEach(function (k) {
      if (HIDE[k] || used[k] || /_norm$/.test(k) || k.charAt(0) === "_") return;
      var v = it[k];
      if (v == null || v === "" || (Array.isArray(v) && !v.length)) return;
      var t;
      if (Array.isArray(v) && v.every(function (x) { return typeof x === "string"; })) t = v.map(function (x) { return /^https?:/.test(x) ? urlLink(x) : esc(x); }).join("<br>");
      else if (typeof v === "object") t = esc(JSON.stringify(v).slice(0, 400));
      else t = /^https?:\/\//.test(String(v)) ? urlLink(String(v)) : esc(v);
      rows.push("<tr><td>" + esc(k) + "</td><td>" + t + "</td></tr>");
    });
    return rows;
  }
  function itemHtml(it) {
    var cont = it.contested || {}, ck = Object.keys(cont);
    var b = itemBody(it), rows = fieldRows(it, b.used);
    var row = it.sheet_row == null ? "" : "row " + it.sheet_row + " &middot; ";
    var h = '<div class="item' + (ck.length ? " conts" : "") + '"><div class="row1">' + chip(KIND_LABEL[it.kind], "") +
      " <b>" + esc(itemHead(it)) + "</b>" + (it.tier ? " " + tierChip(it) : "") +
      '<span class="where">' + row + esc(dirLabel(it.dir)) + (it.also_in && it.also_in.length ? " (also " + it.also_in.map(dirLabel).join(", ") + ")" : "") + "</span></div>";
    h += b.html;
    ck.forEach(function (c) {
      h += '<div class="concern-inline">' + chip("contested", "cont") + " <b>" + esc(c) + "</b>: " + (cont[c] ? esc(cont[c]) : "<i>no detail recorded</i>") + "</div>";
    });
    if (rows.length) h += "<details><summary>all fields</summary><table class=\"rowdata\">" + rows.join("") + "</table></details>";
    return h + itemControls(it) + "</div>";
  }
  function itemVocab(it) { return ITEM_CALLS[it.kind] || OTHER_CALLS; }
  function itemStat(it) {
    return it.call && it.reviewed ? (it.call.replace("_", " ") + " by " + (it.decided_by || "?") + " " + timeOf(it.decided_at)) : "";
  }
  function itemControls(it) {
    var dis = !Store.caps.decide, v = itemVocab(it);
    var opts = '<option value="">no call</option>' + v.map(function (c) {
      return '<option value="' + c + '"' + (it.call === c ? " selected" : "") + ' title="' + esc(CALL_HELP[c] || "") + '">' + c.replace("_", " ") + "</option>";
    }).join("");
    var hint = it.kind === "concern" ? '<span class="faint">any call releases the lines this concern holds (confirmed: it stands; dismissed: closed; needs research: to an Update worklist)</span>' : "";
    return '<div class="icall"><label>Call <select data-icall="' + it._i + '"' + (dis ? ' disabled title="' + esc(NOT_YET) + '"' : "") + ">" + opts + "</select></label>" +
      '<input type="text" data-inote="' + it._i + '" placeholder="note" value="' + esc(it.call_note || "") + '"' + (dis ? " disabled" : "") + ">" +
      '<span class="dstat" id="istat-' + it._i + '" role="status">' + esc(itemStat(it)) + "</span>" + hint + "</div>";
  }
  function itemsHtml(p) {
    if (!p.items.length) return '<div class="hiddennote">No items on this pipeline.</div>';
    var by = {};
    p.items.forEach(function (it) { (by[it.kind] = by[it.kind] || []).push(it); });
    var h = '<section class="items">';
    ITEM_KINDS.forEach(function (k) {
      if (!by[k]) return;
      var open = k in S.igOpen ? S.igOpen[k] : (k !== "unresolved" && k !== "confirmed");
      h += '<details class="igroup" data-kind="' + k + '"' + (open ? " open" : "") + "><summary>" + esc(KIND_LABEL[k]) + ' <span class="n">(' + by[k].length + ")</span></summary>" +
        by[k].map(itemHtml).join("") + "</details>";
    });
    return h + "</section>";
  }

  // ---- card ----
  function tierSummary(p) {
    var c = {high: 0, medium: 0, low: 0, untiered: 0};
    p.lines.forEach(function (l) { c[tierOf(l)]++; });
    return ["high", "medium", "low", "untiered"].filter(function (t) { return c[t]; })
      .map(function (t) { return chip(c[t] + " " + t, t === "untiered" ? "" : t); }).join(" ");
  }
  function renderCard() {
    var card = $("card");
    if (S.pipe < 0) { card.innerHTML = '<div class="empty">Nothing matches the filters.</div>'; S.shown = []; return; }
    var p = D.pipelines[S.pipe], ranges = parseRows(FS.row), q = FS.q.trim().toLowerCase();
    var isNew = p.pid.indexOf("new:") === 0, isScope = p.pid === "scope";
    var segs = p.segments;
    var open = p.lines.filter(function (l) { return !cur(l); }).length;
    var segTxt = segs.length ? segs.map(function (s) { return "row " + s.sheet_row + (s.segment ? " (" + s.segment + ")" : ""); }).join(", ") : "";
    var ctx = ['<b>' + esc(isNew ? "new candidate, not in the sheet" : (isScope ? "scope-level" : segTxt || "no sheet row")) + "</b>",
               p.country && esc(p.country), p.status && "Status: " + esc(p.status),
               p.wiki && '<a href="' + esc(p.wiki) + '" target="_blank" rel="noopener">wiki ↗</a> <span class="faint">context — never a ref</span>',
               tierSummary(p), esc(open + " open · " + (p.lines.length - open) + " decided")]
      .filter(Boolean).map(function (x) { return "<span>" + x + "</span>"; }).join("");
    var h = "<h2>" + (isNew || isScope ? "" : '<span class="pid">' + esc(p.pid) + "</span>") + esc(p.name || "(no name)") + '</h2><div class="ctx">' + ctx + "</div>" +
      '<div class="ctx2">current values from snapshot ' + esc(D.scope.snapshot) + "</div>";
    var nOpenItems = p.items.filter(function (it) { return !it.call; }).length;
    h += '<div class="tabs" role="tablist">' +
      '<button type="button" role="tab" data-tab="lines" aria-selected="' + (S.tab === "lines") + '">Lines (' + p.lines.length + ")</button>" +
      '<button type="button" role="tab" data-tab="items" aria-selected="' + (S.tab === "items") + '" title="i: switch to the Items tab">Items (' + p.items.length +
      (nOpenItems ? ", " + nOpenItems + " without a call" : "") + ")</button></div>";
    if (S.tab === "items") {
      S.shown = []; S.line = -1;
      card.innerHTML = h + itemsHtml(p);
      return;
    }
    // lines the filter lets through, grouped by segment when the PID spans several sheet rows
    var keep = p.lines.filter(function (l) { return match(l, p, FS, null, ranges, q); });
    var hidden = p.lines.length - keep.length;
    if (S.pin === S.pipe && !keep.length) { keep = p.lines.slice(); hidden = 0; }
    var groups = [];
    if (segs.length > 1) {
      segs.forEach(function (s) { groups.push({seg: s, lines: keep.filter(function (l) { return segRow(l) === s.sheet_row; })}); });
      var rest = keep.filter(function (l) { return !segs.some(function (s) { return s.sheet_row === segRow(l); }); });
      if (rest.length) groups.push({seg: null, lines: rest});
    } else groups.push({seg: null, lines: keep, plain: true});
    S.shown = [];
    groups.forEach(function (g) {
      if (!g.lines.length) return;
      if (!g.plain) h += '<div class="segdiv">' + (g.seg ? "row " + esc(g.seg.sheet_row) + (g.seg.segment ? ' <span class="seg">' + esc(g.seg.segment) + "</span>" : "") : "other rows") + "</div>";
      g.lines.forEach(function (l) {
        S.shown.push(l._i);
        h += '<div class="line tier-' + tierOf(l) + (cur(l) ? " d-" + cur(l) : "") + (lockCols(l, p).length ? " locked" : "") + (l.in_backend ? " dim" : "") +
          (l.kind === "new_row" ? " newcard" : "") + (l._i === S.line ? " cur" : "") + '" id="line-' + l._i + '" data-i="' + l._i + '">' + lineHtml(l, p) + "</div>";
      });
    });
    if (hidden) h += '<div class="hiddennote">' + hidden + " more line" + (hidden === 1 ? "" : "s") + " on this pipeline " + (hidden === 1 ? "is" : "are") +
      ' hidden by the filter &mdash; <a href="#" class="only" data-showall="1">show all</a></div>';
    if (!keep.length && !hidden) h += '<div class="hiddennote">No lines on this pipeline.</div>';
    card.innerHTML = h;
    if (S.line < 0 || S.shown.indexOf(S.line) < 0) S.line = S.shown.length ? S.shown[0] : -1;
    var el = S.line >= 0 && $("line-" + S.line);
    if (el) el.classList.add("cur");
  }
  function setLine(i, noScroll) {
    var prev = S.line >= 0 && $("line-" + S.line);
    if (prev) prev.classList.remove("cur");
    S.line = i;
    var cur = $("line-" + i);
    if (cur) { cur.classList.add("cur"); if (!noScroll) cur.scrollIntoView({block: "nearest"}); }
  }

  // ---- keyboard navigation ----
  function stepLine(dir) {
    var at = S.shown.indexOf(S.line), n = at + dir;
    if (n >= 0 && n < S.shown.length) return setLine(S.shown[n]);
    stepPipe(dir, dir < 0);
  }
  function stepPipe(dir, toLast) {
    var at = S.visible.indexOf(S.pipe), n = at + dir;
    if (n < 0 || n >= S.visible.length) return;
    selectPipe(S.visible[n]);
    if (toLast && S.shown.length) setLine(S.shown[S.shown.length - 1]);
  }
  function firstRef(l) {
    if (!l) return "";
    var refs = l.proposed_refs;
    if (l.kind === "new_row") {
      var out = "";
      Object.keys(refs || {}).forEach(function (c) { if (!out && refs[c] && refs[c].length) out = refs[c][0]; });
      return out;
    }
    if (l.kind === "route") return l.geometry_file ? "/geo/" + encodeURI(String(l.dir).replace(/^batches\//, "") + "/" + l.geometry_file) : "";
    return (refs && refs[0]) || splitUrls(l.current_ref)[0] || "";
  }
  function openFirstRef() {
    var u = firstRef(LINES[S.line]);
    if (u) window.open(u, "_blank", "noopener"); else toast("this line has no ref to open");
  }
  function notYet() { toast(NOT_YET); }
  function setStat(i, text, failed) {
    var e = $("dstat-" + i);
    if (e) { e.textContent = text; e.className = "dstat" + (failed ? " err" : (text === "Saving…" ? " saving" : "")); }
  }
  // Save one line's call. The UI changes only after the server confirms; while it is in flight the
  // line says "Saving…", then "accepted by <reviewer> <time>" (or the refusal). No confirm dialog.
  function save(l, rec, advance) {
    if (!Store.caps.decide) return notYet();
    if (S.saving[l.key]) return;
    S.saving[l.key] = true;
    setStat(l._i, "Saving…");
    Store.decide([rec]).then(function (saved) {
      saved.forEach(applyRecord);
      S.stay[l.key] = true;
      banner("");
      var keepLine = S.line;
      refilter(true);
      if (keepLine >= 0 && $("line-" + keepLine)) setLine(keepLine, true);
      if (advance && S.line === l._i) nextUndecided();
    }).catch(function (e) {
      setStat(l._i, "Not saved: " + e.message, true);
      toast("Not saved: " + e.message);
    }).then(function () { delete S.saving[l.key]; });
  }
  function applyRecord(r) {
    var l = LINE_BY_KEY[r.key];
    if (!l) return;
    l.decision = r.undecided ? null : r.decision;
    l.reviewed = !r.undecided && !MACHINE[r.reviewer];
    l.decided_by = r.undecided ? null : r.reviewer;
    l.decided_at = r.undecided ? null : r.ts;
    l.suggested_value = r.suggested_value || "";
    l.decision_note = r.note || "";
    noteSession(r, "decision");
  }
  function noteSession(r, field) {
    if (r.undecided) delete S.session[r.key];
    else if (!MACHINE[r.reviewer]) S.session[r.key] = {key: r.key, dir: r.dir, kind: r.kind, what: r[field]};
  }
  function applyItemRecord(r) {
    var it = ITEM_BY_KEY[r.key];
    if (!it) return;
    it.call = r.undecided ? null : r.call;
    it.call_note = r.undecided ? null : r.note;
    it.reviewed = !r.undecided && !MACHINE[r.reviewer];
    it.decided_by = r.undecided ? null : r.reviewer;
    it.decided_at = r.undecided ? null : r.ts;
    noteSession(r, "call");
  }
  function lockedCount(p) { return p.lines.filter(function (l) { return lockCols(l, p).length; }).length; }
  // Save one item's call. Same in-place feedback as a line; when a concern's call releases the
  // lock, the card's lines unlock in the same re-render (no reload).
  function saveItem(it, rec) {
    if (!Store.caps.decide) return notYet();
    if (S.saving[it.key]) return;
    S.saving[it.key] = true;
    var p = D.pipelines[it._p], before = lockedCount(p), el = $("istat-" + it._i);
    if (el) { el.textContent = "Saving…"; el.className = "dstat saving"; }
    Store.item([rec]).then(function (saved) {
      saved.forEach(applyItemRecord);
      banner("");
      refilter(true);
      var freed = before - lockedCount(p);
      if (freed > 0) toast(freed + " line" + (freed === 1 ? "" : "s") + " on this card unlocked (the concern has a call)");
      else if (freed < 0) toast(-freed + " line" + (freed === -1 ? "" : "s") + " locked again (the concern is open)");
    }).catch(function (e) {
      renderCard();
      var e2 = $("istat-" + it._i);
      if (e2) { e2.textContent = "Not saved: " + e.message; e2.className = "dstat err"; }
      toast("Not saved: " + e.message);
    }).then(function () { delete S.saving[it.key]; });
  }
  function onItemChange(e) {
    var sel = e.target.closest("select[data-icall]"), inp = e.target.closest("input[data-inote]");
    var t = sel || inp;
    if (!t) return;
    var it = ITEMS[+t.getAttribute(sel ? "data-icall" : "data-inote")];
    if (!it) return;
    var box = t.closest(".icall"), call = box.querySelector("select").value, note = box.querySelector("input").value;
    if (!call) { if (sel && it.call) saveItem(it, {key: it.key, undo: true}); return; }
    if (inp && call === it.call && note === (it.call_note || "")) return;
    saveItem(it, {key: it.key, call: call, note: note});
  }
  function decideCurrent(decision, advance) {
    var l = LINES[S.line];
    if (S.tab === "items") return toast("the Items tab takes calls, not line decisions: press i to go back to the lines");
    if (!l) return;
    var p = D.pipelines[l._p];
    if (decision === "accept") {
      var lk = lockCols(l, p);
      if (lk.length) return toast("held: a validity concern on " + lk.join(", ") + " is open; give it a call before accepting (hold / reject are fine)");
    }
    save(l, {key: l.key, decision: decision}, advance);
  }
  function undoCurrent() {
    var l = LINES[S.line];
    if (S.tab === "items" || !l) return;
    if (!cur(l)) return toast("nothing to undo on this line");
    save(l, {key: l.key, undo: true}, false);
  }
  function nextUndecided() {       // after a keypress decision: the next open line, then the next pipeline
    var at = S.shown.indexOf(S.line);
    for (var n = at + 1; n < S.shown.length; n++) {
      if (!cur(LINES[S.shown[n]])) return setLine(S.shown[n]);
    }
    stepPipe(1);
  }
  function suggestKey() { toast(Store.caps.decide ? "suggest arrives in milestone 5" : NOT_YET); }
  var KEYS = {
    j: function () { stepLine(1); }, k: function () { stepLine(-1); },
    J: function () { stepPipe(1); }, K: function () { stepPipe(-1); },
    o: openFirstRef,
    d: function () {
      var l = S.line >= 0 && $("line-" + S.line), m = l && l.querySelector("details[data-more]");
      if (m) m.open = !m.open;
    },
    a: function () { decideCurrent("accept", true); }, h: function () { decideCurrent("hold", true); },
    r: function () { decideCurrent("reject", true); }, s: suggestKey, u: undoCurrent,
    "/": function (e) { e.preventDefault(); $("f-q").focus(); $("f-q").select(); },
    S: function () { showSummary(); },
    A: function () { showBulk("defaults"); },
    i: toggleItemsTab,
    "?": showHelp
  };
  function toggleItemsTab() {
    if (S.pipe < 0) return;
    S.tab = S.tab === "items" ? "lines" : "items";
    renderCard();
    if (S.tab === "items") { var s1 = document.querySelector("#card select[data-icall]"); if (s1) s1.focus(); }
  }
  var HELP = [["j / k", "next / previous line (runs on into the next pipeline)"], ["J / K", "next / previous pipeline"],
              ["a / h / r", "accept / hold / reject the line; saved at once, then on to the next open line"], ["s", "suggest a different value (milestone 5)"],
              ["A", "accept every default-accept line in view (asks first, with the count)"], ["i", "switch the card between Lines and Items; calls save on change"],
              ["S", "session summary (counts, this session, copy as markdown)"],
              ["u", "undo: the line goes back to undecided"], ["o", "open the line's first ref (new tab)"], ["d", "show / hide the line's details"],
              ["/", "search"], ["?", "this help"]];
  function showHelp() {
    var dlg = $("dialog");
    dlg.setAttribute("data-kind", "help");
    dlg.innerHTML = "<h3>Keyboard</h3><table>" + HELP.map(function (r) { return "<tr><td><kbd>" + r[0] + "</kbd></td><td>" + r[1] + "</td></tr>"; }).join("") +
      '</table><div class="actions"><button type="button" id="dlg-close">Close</button></div>';
    $("dlg-close").onclick = function () { dlg.close(); };
    dlg.showModal();
  }
  function onKey(e) {
    if (e.metaKey || e.ctrlKey || e.altKey) return;
    if ($("dialog").open) {
      if (e.key === "S" && $("dialog").getAttribute("data-kind") === "summary") $("dialog").close();
      return;
    }
    var t = e.target;
    if (t && /^(INPUT|TEXTAREA|SELECT)$/.test(t.tagName)) { if (e.key === "Escape") t.blur(); return; }
    var f = KEYS[e.key];
    if (f) f(e);
  }
  var toastTimer = null;
  function toast(msg) {
    var t = $("toast");
    t.textContent = msg;
    t.hidden = false;
    clearTimeout(toastTimer);
    toastTimer = setTimeout(function () { t.hidden = true; }, 4000);
  }
  function banner(msg) { var b = $("banner"); b.textContent = msg; b.hidden = !msg; }

  function onCardClick(e) {
    if (e.target.closest("[data-showall]")) {
      e.preventDefault();
      var keepPipe = S.pipe;
      FS = defaults(); FS.decision = ""; FS.landed = true;
      syncControls(); S.pin = keepPipe; refilter(true); writeRoute(false);
      return;
    }
    var tb = e.target.closest("button[data-tab]");
    if (tb) {
      if (S.tab !== tb.getAttribute("data-tab")) { S.tab = tb.getAttribute("data-tab"); renderCard(); }
      return;
    }
    var b = e.target.closest("button[data-decide]");
    var ub = e.target.closest("button[data-undo]");
    var ln = e.target.closest(".line");
    if (ln) setLine(+ln.getAttribute("data-i"), true);
    if (ub && !ub.disabled) return undoCurrent();
    if (!b) return;
    if (!Store.caps.decide) return notYet();
    // a click on the pressed button takes the call back (the same record an undo writes)
    if (b.getAttribute("aria-pressed") === "true") return undoCurrent();
    decideCurrent(b.getAttribute("data-decide"), false);
  }

  // ---- bulk ----
  // The targets are the CURRENT filtered queue. Locked (contested) lines and lines a person already
  // decided are skipped here; the server refuses a locked accept anyway (409, nothing written).
  function bulkTargets(mode) {
    var ranges = parseRows(FS.row), q = FS.q.trim().toLowerCase();
    var t = {lines: [], byKind: {}, decision: mode === "hold" ? "hold" : "accept", skip: {locked: 0, decided: 0, other: 0}};
    D.pipelines.forEach(function (p, pi) {
      if (mode === "pipe-high" && pi !== S.pipe) return;
      p.lines.forEach(function (l) {
        if (!match(l, p, FS, null, ranges, q)) return;
        if (cur(l)) { t.skip.decided++; return; }
        if (lockCols(l, p).length) { t.skip.locked++; return; }
        if ((mode === "defaults" && (l.default || "hold") !== "accept") || (mode === "pipe-high" && tierOf(l) !== "high")) { t.skip.other++; return; }
        t.lines.push(l);
        t.byKind[l.kind] = (t.byKind[l.kind] || 0) + 1;
      });
    });
    return t;
  }
  var BULK_TITLE = {defaults: "Accept all defaults in view", hold: "Hold all in view", "pipe-high": "Accept all high in this pipeline"};
  function showBulk(mode) {
    if (!Store.caps.decide) return notYet();
    if (S.pipe < 0) return toast("nothing in view");
    var t = bulkTargets(mode), dlg = $("dialog"), sk = t.skip;
    var skipTxt = [sk.locked && sk.locked + " locked by an open concern", sk.decided && sk.decided + " already decided",
                   sk.other && sk.other + (mode === "pipe-high" ? " not high tier" : " whose default is hold")].filter(Boolean).join(", ");
    if (!t.lines.length) return toast("nothing to " + t.decision + " in view" + (skipTxt ? " (skipped: " + skipTxt + ")" : ""));
    var kinds = Object.keys(t.byKind).map(function (k) { return "<tr><td>" + esc(KIND_LABEL[k]) + "</td><td>" + t.byKind[k] + "</td></tr>"; }).join("");
    dlg.setAttribute("data-kind", "bulk");
    dlg.innerHTML = "<h3>" + esc(BULK_TITLE[mode]) + "</h3><p><b>" + t.lines.length + " line" + (t.lines.length === 1 ? "" : "s") + "</b> will be " +
      (t.decision === "accept" ? "accepted" : "held") + " as " + esc(ME) + ", in one save:</p><table>" + kinds + "</table>" +
      (skipTxt ? '<p class="faint">Skipped: ' + esc(skipTxt) + ".</p>" : "") +
      '<p class="faint" id="bulk-err"></p><div class="actions"><button type="button" class="ghost" id="dlg-cancel">Cancel</button>' +
      '<button type="button" id="dlg-ok">' + (t.decision === "accept" ? "Accept " : "Hold ") + t.lines.length + "</button></div>";
    $("dlg-cancel").onclick = function () { dlg.close(); };
    $("dlg-ok").onclick = function () {
      var ok = $("dlg-ok"); ok.disabled = true; ok.textContent = "Saving…";
      Store.decide(t.lines.map(function (l) { return {key: l.key, decision: t.decision}; })).then(function (saved) {
        saved.forEach(applyRecord);
        t.lines.forEach(function (l) { S.stay[l.key] = true; });
        dlg.close();
        refilter(true);
        toast((t.decision === "accept" ? "accepted " : "held ") + saved.length + " line" + (saved.length === 1 ? "" : "s"));
      }).catch(function (e) {
        ok.disabled = false; ok.textContent = "Retry";
        $("bulk-err").textContent = "Not saved: " + e.message;
        $("bulk-err").className = "err";
      });
    };
    dlg.showModal();
  }

  // ---- session summary ----
  function summaryModel() {
    var kinds = {}, tiers = {}, dirs = {}, ik = {};
    function bump(m, k, f) { (m[k] = m[k] || {decided: 0, open: 0, backend: 0})[f]++; }
    LINES.forEach(function (l) {
      var f = cur(l) ? "decided" : (l.in_backend ? "backend" : "open");
      bump(kinds, l.kind, f); bump(tiers, tierOf(l), f); bump(dirs, l.dir, f);
    });
    ITEMS.forEach(function (it) { bump(ik, it.kind, it.call ? "decided" : "open"); });
    var sess = Object.keys(S.session).map(function (k) { return S.session[k]; }), sw = {}, sd = {};
    sess.forEach(function (r) { sw[r.what] = (sw[r.what] || 0) + 1; sd[r.dir] = (sd[r.dir] || 0) + 1; });
    return {kinds: kinds, tiers: tiers, dirs: dirs, itemKinds: ik, sessWhat: sw, sessDirs: sd, sessN: sess.length};
  }
  function sumRows(m, order, labels) {
    return order.filter(function (k) { return m[k]; }).map(function (k) { return [labels && labels[k] || k, m[k].decided, m[k].open, m[k].backend]; });
  }
  function sumTable(head, rows) {
    return "<table class=\"sumtab\"><tr>" + head.map(function (x) { return "<th>" + esc(x) + "</th>"; }).join("") + "</tr>" +
      rows.map(function (r) { return "<tr>" + r.map(function (x, i) { return "<td" + (i ? ' class="num"' : "") + ">" + esc(x) + "</td>"; }).join("") + "</tr>"; }).join("") + "</table>";
  }
  function summaryMarkdown(m) {
    function tab(head, rows) {
      return "| " + head.join(" | ") + " |\n|" + head.map(function () { return "---"; }).join("|") + "|\n" + rows.map(function (r) { return "| " + r.join(" | ") + " |"; }).join("\n") + "\n";
    }
    var H = ["", "decided", "open", "in backend"];
    var kinds = sumRows(m.kinds, LINE_KINDS, KIND_LABEL), tiers = sumRows(m.tiers, ["high", "medium", "low", "untiered"]);
    var dirs = Object.keys(m.dirs).sort().map(function (d) { return [dirLabel(d), m.dirs[d].decided, m.dirs[d].open, m.dirs[d].backend, m.sessDirs[d] || 0]; });
    var items = ITEM_KINDS.filter(function (k) { return m.itemKinds[k]; }).map(function (k) { return [KIND_LABEL[k], m.itemKinds[k].decided, m.itemKinds[k].open]; });
    var out = "## Review summary: " + D.scope.country + " " + D.scope.commodity + " (snapshot " + D.scope.snapshot + ")\n\nReviewer: " + ME +
      "  \nThis session: " + m.sessN + " saved (" + (Object.keys(m.sessWhat).map(function (k) { return m.sessWhat[k] + " " + k; }).join(", ") || "none") + ")\n\n" +
      "### Lines by kind\n\n" + tab(["kind"].concat(H.slice(1)), kinds) + "\n### Lines by tier\n\n" + tab(["tier"].concat(H.slice(1)), tiers) +
      "\n### Items\n\n" + tab(["kind", "with a call", "without"], items) + "\n### By staging dir\n\n" + tab(["dir", "decided", "open", "in backend", "this session"], dirs);
    return out;
  }
  function copyText(text) {
    function fallback() {
      var ta = document.createElement("textarea");
      ta.value = text; document.body.appendChild(ta); ta.select();
      var ok = false;
      try { ok = document.execCommand("copy"); } catch (e) { ok = false; }
      document.body.removeChild(ta);
      toast(ok ? "summary copied" : "could not copy: select the text by hand");
    }
    if (navigator.clipboard && navigator.clipboard.writeText) navigator.clipboard.writeText(text).then(function () { toast("summary copied"); }, fallback);
    else fallback();
  }
  function showSummary() {
    var dlg = $("dialog");
    if (dlg.open && dlg.getAttribute("data-kind") === "summary") return dlg.close();
    if (dlg.open) return;
    var m = summaryModel(), tot = LINES.length, dec = 0, bk = 0;
    LINES.forEach(function (l) { if (cur(l)) dec++; else if (l.in_backend) bk++; });
    var L = ["decided", "open", "in backend"];
    var items = ITEM_KINDS.filter(function (k) { return m.itemKinds[k]; }).map(function (k) { return [KIND_LABEL[k], m.itemKinds[k].decided, m.itemKinds[k].open]; });
    var dirs = Object.keys(m.dirs).sort().map(function (d) { return [dirLabel(d), m.dirs[d].decided, m.dirs[d].open, m.dirs[d].backend, m.sessDirs[d] || 0]; });
    dlg.setAttribute("data-kind", "summary");
    dlg.innerHTML = "<h3>Session summary</h3><p>" + dec + " of " + tot + " lines decided &middot; " + bk + " in the backend &middot; " + (tot - dec - bk) + " open. " +
      "<b>This session (" + esc(ME) + "):</b> " + m.sessN + " saved" + (m.sessN ? " (" + Object.keys(m.sessWhat).map(function (k) { return m.sessWhat[k] + " " + esc(k); }).join(", ") + ")" : "") + ".</p>" +
      "<h4>Lines by kind</h4>" + sumTable(["kind"].concat(L), sumRows(m.kinds, LINE_KINDS, KIND_LABEL)) +
      "<h4>Lines by tier</h4>" + sumTable(["tier"].concat(L), sumRows(m.tiers, ["high", "medium", "low", "untiered"])) +
      "<h4>Items</h4>" + sumTable(["kind", "with a call", "without"], items) +
      "<h4>By staging dir</h4>" + sumTable(["dir", "decided", "open", "in backend", "this session"], dirs) +
      '<div class="actions"><button type="button" class="ghost" id="dlg-copy">Copy summary as markdown</button><button type="button" id="dlg-close">Close</button></div>';
    $("dlg-close").onclick = function () { dlg.close(); };
    $("dlg-copy").onclick = function () { copyText(summaryMarkdown(m)); };
    dlg.showModal();
  }

  // ---- refresh backend ----
  function refreshBackend() {
    if (!Store.caps.refresh) return toast("this server cannot refresh the backend (started with --no-build)");
    var dlg = $("dialog");
    dlg.setAttribute("data-kind", "refresh");
    dlg.innerHTML = "<h3>Refresh backend</h3><p>This pulls the live sheet (read-only, about a minute), rebuilds this dataset from the new snapshot, " +
      "and marks lines the sheet already holds as <i>in backend</i> (a machine record, not a review). Your decisions are kept.</p>" +
      '<p class="faint" id="rf-err"></p><div class="actions"><button type="button" class="ghost" id="dlg-cancel">Cancel</button><button type="button" id="dlg-ok">Pull and rebuild</button></div>';
    $("dlg-cancel").onclick = function () { dlg.close(); };
    $("dlg-ok").onclick = function () {
      var ok = $("dlg-ok"); ok.disabled = true; ok.textContent = "Pulling…"; $("dlg-cancel").disabled = true;
      var btn = $("sync"); btn.disabled = true;
      Store.refresh().then(function (r) {
        return Store.load().then(function (data) {
          dlg.close();
          reload(data);
          toast("refreshed: snapshot " + r.snapshot + ", " + r.lines + " lines, " + r.synced + " newly in backend");
        });
      }).catch(function (e) {
        ok.disabled = false; ok.textContent = "Retry"; $("dlg-cancel").disabled = false;
        $("rf-err").textContent = "Refresh failed: " + e.message; $("rf-err").className = "err";
      }).then(function () { btn.disabled = !Store.caps.refresh; });
    };
    dlg.showModal();
  }
  function reload(data) {
    var pid = D.pipelines[S.pipe] ? D.pipelines[S.pipe].pid : "";
    D = data;
    prepare();
    S.pin = -1; S.stay = {}; S.line = -1;
    S.pipe = -1;
    D.pipelines.forEach(function (p, i) { if (p.pid === pid) S.pipe = i; });
    $("scope").textContent = D.scope.country + " " + D.scope.commodity + " · " + D.scope.snapshot;
    refilter(true);
  }

  // ---- routing: #/P0736 plus an optional ?query with the filters that differ from the defaults ----
  var ROUTING = false;
  var QK = {decision: "d", kind: "k", tier: "t", class_out: "c", dir: "dir", column: "col", q: "q", row: "row",
            contested: "cont", single: "single", owners: "owners", landed: "landed"};
  function routeHash() {
    var p = D.pipelines[S.pipe], d = defaults(), q = [];
    Object.keys(QK).forEach(function (f) {
      if (FS[f] === d[f]) return;
      var v = FS[f];
      if (typeof v === "boolean") v = "1";
      else if (f === "decision" && v === "") v = "any";
      q.push(QK[f] + "=" + encodeURIComponent(v));
    });
    return "#/" + (p ? encodeURIComponent(p.pid) : "") + (q.length ? "?" + q.join("&") : "");
  }
  function writeRoute(replace) {
    if (ROUTING || !D) return;
    var h = routeHash();
    if (h === location.hash) return;
    try { history[replace ? "replaceState" : "pushState"](null, "", h); } catch (e) { /* file:// or blocked */ }
  }
  function applyRoute() {
    ROUTING = true;
    try {
      var m = /^#\/([^?]*)(?:\?(.*))?$/.exec(location.hash || ""), pid = "";
      FS = defaults();
      if (m) {
        pid = decodeURIComponent(m[1]);
        (m[2] || "").split("&").forEach(function (kv) {
          var i = kv.indexOf("="); if (i < 1) return;
          var k = kv.slice(0, i), v = decodeURIComponent(kv.slice(i + 1));
          Object.keys(QK).forEach(function (f) {
            if (QK[f] !== k) return;
            FS[f] = typeof FS[f] === "boolean" ? v === "1" : (f === "decision" && v === "any" ? "" : v);
          });
        });
      }
      syncControls();
      S.pin = -1;
      var pi = -1;
      D.pipelines.forEach(function (p, i) { if (p.pid === pid) pi = i; });
      S.pipe = pi;
      refilter(true);
      if (pi >= 0 && S.visible.indexOf(pi) < 0) {      // a link to a pipeline the filters would hide
        FS = defaults(); FS.decision = ""; FS.landed = true;
        syncControls(); S.pin = pi; refilter(true);
      }
      if (pi >= 0 && S.visible.indexOf(pi) >= 0 && S.pipe !== pi) selectPipe(pi);
      if (pi >= 0 && S.visible.indexOf(pi) >= 0) { S.pipe = pi; renderQueue(); renderCard(); var li = $("pipes").querySelector("li.sel"); if (li) li.scrollIntoView({block: "nearest"}); }
    } finally { ROUTING = false; }
    writeRoute(true);
  }
  window.addEventListener("popstate", applyRoute);
  window.addEventListener("hashchange", function () { if (!ROUTING && location.hash !== routeHash()) applyRoute(); });

  // ---- boot ----
  window.ReviewApp = {
    get data() { return D; }, state: S, filters: function () { return FS; }, refilter: refilter, Store: Store, timing: {}
  };
  function et(iso) { return String(iso || "").replace("T", " ").slice(0, 16) + " ET"; }
  function boot(reviewer, data) {
    D = data; ME = reviewer;
    var tLoaded = performance.now();
    prepare();
    $("whoami").textContent = reviewer;
    $("scope").textContent = D.scope.country + " " + D.scope.commodity + " · " + D.scope.snapshot;
    $("scope").title = "built " + et(D.built) + " · " + D.dirs.length + " staging dir" + (D.dirs.length === 1 ? "" : "s") + ": " + D.dirs.map(dirLabel).join(", ");
    $("sync").disabled = !Store.caps.refresh;
    $("sync").title = Store.caps.refresh ? "Pull the live sheet (~1 min), rebuild, and mark lines it already holds" : "this server was started with --no-build: it cannot refresh";
    $("push").hidden = !Store.caps.push;
    initFilters();
    applyRoute();
    var tDone = performance.now();
    window.ReviewApp.timing = {loadMs: Math.round(tLoaded - T0), renderMs: Math.round(tDone - tLoaded), totalMs: Math.round(tDone - T0),
                               pipelines: D.pipelines.length, lines: LINES.length, items: ITEMS.length};
    if (window.console) console.info("review app: loaded in " + window.ReviewApp.timing.loadMs + " ms, first render " +
      window.ReviewApp.timing.renderMs + " ms", window.ReviewApp.timing);
  }
  initTheme();
  document.addEventListener("keydown", onKey);
  $("card").addEventListener("click", onCardClick);
  $("pipes").addEventListener("click", function (e) {
    var li = e.target.closest("li[data-i]");
    if (li) selectPipe(+li.getAttribute("data-i"));
  });
  $("help-btn").onclick = showHelp;
  $("sync").onclick = refreshBackend;
  $("summary-btn").onclick = showSummary;
  $("bulk-defaults").onclick = function () { showBulk("defaults"); };
  $("bulk-hold").onclick = function () { showBulk("hold"); };
  $("bulk-pipe").onclick = function () { showBulk("pipe-high"); };
  $("card").addEventListener("change", onItemChange);
  $("card").addEventListener("toggle", function (e) {
    var d = e.target;
    if (d && d.classList && d.classList.contains("igroup")) S.igOpen[d.getAttribute("data-kind")] = d.open;
  }, true);
  Promise.all([Store.whoami(), Store.load()]).then(function (r) { boot(r[0], r[1]); })
    .catch(function (e) { banner("Could not load the dataset: " + e.message); });
})();
