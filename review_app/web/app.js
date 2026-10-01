/* Pipelines review app front end (milestone 4: bulk, items, summary, refresh). Vanilla JS, no modules, no build step
   (phase 2 inlines this file into an Apps Script HtmlService page). All I/O goes through Store;
   controls that need a capability read Store.caps and hide / disable themselves. */
(function () {
  "use strict";
  var T0 = performance.now();

  // ---- Store adapter: local HTTP here; on the Google page gas.js (loaded first) supplies window.GasStore ----
  var NOT_YET = "this server cannot record decisions";
  var Store = window.GasStore || {
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
  var CALL_HELP = {confirmed: "the concern stands", dismissed: "the concern is closed", needs_research: "goes to a research / update worklist",
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
  // audit-trail records (the sweep's own "checked, still operating"): never listed, never asked for a call
  var INFO_KINDS = {confirmed: 1};
  var DEC = ["undecided", "accept", "hold", "reject", "suggest"];

  function defaults() {
    return {decision: "undecided", kind: "", tier: "", class_out: "", dir: "", column: "", q: "", row: "",
            contested: false, owners: false, landed: false, country: [], fuel: ["gas"], by: "", drift: false};
  }
  // distinct non-empty segment names of a pipeline, in sheet order
  function segNames(p) {
    var seen = {};
    return p.segments.map(function (s) { return String(s.segment || "").trim(); })
      .filter(function (n) { if (!n || seen[n]) return false; seen[n] = 1; return true; });
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
  // drawn grayed once a person has decided it (hold stays bright — still open) or it is already in the backend
  function settled(l) { var d = cur(l); return d === "accept" || d === "reject" || d === "suggest"; }
  // a status line covers the Status [ref] record folded into it; the call is incomplete while one
  // of those records still says something else (decided before the fold: deciding again fixes it)
  function gap(l) { return !!(cur(l) && l.uncovered && l.uncovered.length); }
  function dimmed(l) { return (settled(l) && !gap(l)) || !!l.in_backend; }
  function dstate(o) {
    if (o._item && INFO_KINDS[o.kind]) return "info";
    var d = o._item ? o.call : cur(o);
    return d ? d : "undecided";
  }
  var TODAY = (function () {
    try { return new Intl.DateTimeFormat("en-CA", {timeZone: "America/New_York"}).format(new Date()); } catch (e) { return ""; }
  })();
  // today's decisions show HH:MM, older ones their date too (the store keeps every decision ever made)
  function timeOf(iso) {
    var s = String(iso || "").replace("T", " ");
    return !TODAY || s.slice(0, 10) === TODAY ? s.slice(11, 16) : s.slice(0, 16);
  }
  function decisionText(l) {
    if (l.reviewed && l.decision === "suggest") {
      return "suggested: " + (blankv(l.suggested_value) ? "(note only)" : l.suggested_value) + " by " + (l.decided_by || "?") + " " + timeOf(l.decided_at) +
        (blankv(l.decision_note) ? "" : " \u2014 " + l.decision_note);
    }
    if (l.reviewed && l.decision) return (VERB[l.decision] || l.decision) + " by " + (l.decided_by || "?") + " " + timeOf(l.decided_at) +
      (gap(l) ? " \u2014 made before the Status [ref] record joined this card: press " + l.decision + " again to cover it" : "");
    if (l.decision && l.decided_by === "backend sync") return "in backend (synced by backend sync, not reviewed)";
    if (l.decision && l.decided_by) return "pre-filled by " + l.decided_by + " (not reviewed)";
    return "";
  }
  // contested linking: a line on a column that an OPEN validity concern (no call yet) names is held,
  // unless the line IS the resolution: the concern's contested value (non-empty) equals the line's
  // proposed value on that column (trimmed strings), as store.resolves does server-side.
  function selfResolved(it, l, c) {
    var cv = String((it.contested || {})[c] == null ? "" : it.contested[c]).trim();
    var pv = (l.proposed_values || {})[c];
    return cv !== "" && cv === String(pv == null ? "" : pv).trim();
  }
  function touchedCols(l) {
    var cols = [l.column].concat(l.value_cols || []);
    if (l.kind === "status") cols.push("Status");
    return cols.filter(function (c, i) { return c && cols.indexOf(c) === i; });
  }
  function lockCols(l, p) {
    var open = {}, cols = touchedCols(l);
    p.items.forEach(function (it) {
      if (it.kind !== "concern" || it.call || !it.contested || typeof it.contested !== "object") return;
      cols.forEach(function (c) { if ((c in it.contested) && !selfResolved(it, l, c)) open[c] = 1; });
    });
    return cols.filter(function (c) { return open[c]; });
  }
  // columns of this line on which an open concern agrees with the proposed value
  function agreeCols(l, p) {
    var out = [];
    p.items.forEach(function (it) {
      if (it.kind !== "concern" || it.call || !it.contested || typeof it.contested !== "object") return;
      touchedCols(l).forEach(function (c) { if ((c in it.contested) && selfResolved(it, l, c) && out.indexOf(c) < 0) out.push(c); });
    });
    return out;
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
  // theme = a palette (dropdown; "" = the default look) x a mode (light / dark button; unset = follow the system).
  // The page's data-theme is "light" / "dark" for the default palette, "<palette>-<mode>" for the others.
  function initTheme() {
    var root = document.documentElement, pick = $("theme-pick"), mq = matchMedia("(prefers-color-scheme: dark)");
    var pal = "", mode = "";
    function store(k, v) { try { if (v) localStorage.setItem(k, v); else localStorage.removeItem(k); } catch (e) { /* ignore */ } }
    function eff() { return mode || (mq.matches ? "dark" : "light"); }
    function apply() {
      if (!pal && !mode) root.removeAttribute("data-theme");
      else root.setAttribute("data-theme", pal ? pal + "-" + eff() : mode);
      pick.value = pal;
    }
    try {
      pal = localStorage.getItem("review-palette") || "";
      mode = localStorage.getItem("review-mode") || "";
      var old = localStorage.getItem("review-theme");          // the pre-palette key: "light" / "dark"
      if (old && !mode && (old === "light" || old === "dark")) mode = old;
    } catch (e) { /* storage blocked: follow the system theme */ }
    apply();
    pick.onchange = function () { pal = this.value; store("review-palette", pal); apply(); };
    $("theme").onclick = function () { mode = eff() === "dark" ? "light" : "dark"; store("review-mode", mode); apply(); };
    if (mq.addEventListener) mq.addEventListener("change", function () { if (!mode) apply(); });
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
      p._countries = p.scope_countries || [];
      p._commodity = p.commodity || D.scope.commodity;
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
    if (item && INFO_KINDS[o.kind]) return false;
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
    if (fs.owners && (item || o.kind !== "oo")) return false;
    if (fs.by && (o.reviewed ? o.decided_by : "") !== fs.by) return false;
    if (fs.drift && (item || !(o.drift || o.live))) return false;
    if (fs.row) {
      if (!ranges) return false;
      var rows = item ? (o.sheet_row != null ? [o.sheet_row] : []) : o._rows;
      if (!inRows(rows, ranges)) return false;
    }
    if (skip !== "country" && fs.country.length && !p._countries.some(function (c) { return fs.country.indexOf(c) >= 0; })) return false;
    if (fs.fuel.length && fs.fuel.indexOf(p._commodity) < 0) return false;
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
  // a facet dropdown: "any" plus one option per value with its live count ("accept (3)")
  function facetSelect(id, facet, values, labels, totals) {
    var counts = facetCounts(facet, values), h = '<option value="">any</option>';
    values.forEach(function (v) {
      if (totals && !totals[v] && FS[facet] !== v) return;      // a kind the scope does not have
      h += '<option value="' + v + '"' + (FS[facet] === v ? " selected" : "") + ">" + esc(labels[v] || v) + " (" + counts[v] + ")</option>";
    });
    var s = $(id);
    s.innerHTML = h;
    s.value = FS[facet];
  }
  // the batch countries still shown; an all-decided country the build hid is listed apart (hiddenCountries)
  function countryStatus() { return (D.scope && D.scope.country_status) || []; }
  function hiddenCountries() { return countryStatus().filter(function (c) { return c.hidden; }).map(function (c) { return c.country; }); }
  function countries() {
    var hid = hiddenCountries();
    return ((D.scope && D.scope.countries) || []).filter(function (c) { return hid.indexOf(c) < 0; });
  }
  // the batch countries as checkboxes (any ticked country matches; none ticked = every country),
  // each with its live line + item count under the other filters
  function renderCountries() {
    var box = $("f-country"), all = countries(), hid = hiddenCountries();
    renderFuel();
    renderScope();
    box.hidden = all.length < 2 && !hid.length;
    if (box.hidden) return;
    var ranges = parseRows(FS.row), q = FS.q.trim().toLowerCase(), c = {};
    all.forEach(function (k) { c[k] = 0; });
    D.pipelines.forEach(function (p) {
      var n = 0;
      p.lines.forEach(function (l) { if (match(l, p, FS, "country", ranges, q)) n++; });
      p.items.forEach(function (it) { if (match(it, p, FS, "country", ranges, q)) n++; });
      p._countries.forEach(function (k) { if (k in c) c[k] += n; });
    });
    var was = box.querySelector("details"), open = was && was.open, n = FS.country.length;
    box.innerHTML = '<details class="cdrop"' + (open ? " open" : "") + '><summary>country</summary><div class="cmenu"><input type="search" class="csearch" placeholder="find a country" value="' + esc(CQ) + '"><button type="button" class="ctoggle"></button>' + all.map(function (k) {
      return '<label class="check"><input type="checkbox" value="' + esc(k) + '"' + (!n || FS.country.indexOf(k) >= 0 ? " checked" : "") +
        "> " + esc(k) + " (" + c[k] + ")</label>";
    }).join("") + "</div></details>" + (hid.length ? '<span class="cdone" title="every line and asked item in these countries has a decision, so the build left them out (review_data.py --include-done shows them)">all decided, hidden: ' +
      esc(hid.join(", ")) + "</span>" : "");
    filterCountryMenu();
  }
  // fuel: the same checkbox dropdown (none ticked = no filter in the data model, all ticked = same thing)
  var FUELS = ["gas", "oil"];
  function renderFuel() {
    var box = $("f-fuel"), was = box.querySelector("details"), open = was && was.open, n = FS.fuel.length;
    box.innerHTML = '<details class="cdrop fdrop"' + (open ? " open" : "") + '><summary>fuel</summary><div class="cmenu">' +
      FUELS.map(function (k) {
        return '<label class="check"><input type="checkbox" value="' + k + '"' + (!n || FS.fuel.indexOf(k) >= 0 ? " checked" : "") + "> " + k + "</label>";
      }).join("") + "</div></details>";
  }
  // header: each batch country as a box (commodity is a filter; the snapshot name is in the tooltip)
  function renderScope() {
    var list = countries(); if (!list.length && D.scope.country) list = [D.scope.country];
    if (FS.country.length) list = list.filter(function (k) { return FS.country.indexOf(k) >= 0; });   // only the selected ones
    $("scope").innerHTML = FUELS.filter(function (k) { return !FS.fuel.length || FS.fuel.indexOf(k) >= 0; }).map(function (k) { return '<span class="cbox fbox" data-tip="fuel filter: ' + k + ' pipelines">' + k + "</span>"; }).join("") +
      list.map(function (k) { return '<span class="cbox" data-tip="country filter: ' + esc(k) + ' pipelines (' + D.pipelines.filter(function (p) { return p._countries.indexOf(k) >= 0; }).length + ' in this batch)">' + esc(k) + "</span>"; }).join("");
  }
  var CQ = "";   // country-menu search text
  var NO_COUNTRY = "(none)";   // FS.country sentinel: every box unticked, so nothing matches (empty = no filter)
  // the (un)select-all button acts on the countries the search leaves visible
  function toggleLabel() {
    var b = document.querySelector("#f-country .ctoggle"); if (!b) return;
    var boxes = Array.prototype.filter.call(document.querySelectorAll("#f-country .cmenu label:not([hidden]) input"), function () { return true; });
    b.textContent = boxes.length && boxes.every(function (i) { return i.checked; }) ? "deselect all" : "select all";
  }
  function toggleCountries() {
    var cur = countries(), sel = FS.country.length ? cur.filter(function (k) { return FS.country.indexOf(k) >= 0; }) : cur.slice();
    var vis = Array.prototype.map.call(document.querySelectorAll("#f-country .cmenu label:not([hidden]) input"), function (i) { return i.value; });
    var allOn = vis.length && vis.every(function (k) { return sel.indexOf(k) >= 0; });
    sel = allOn ? sel.filter(function (k) { return vis.indexOf(k) < 0; }) : sel.concat(vis.filter(function (k) { return sel.indexOf(k) < 0; }));
    FS.country = sel.length === cur.length ? [] : sel.length ? sel : [NO_COUNTRY];
    changed();
  }
  function filterCountryMenu() {
    var q = CQ.trim().toLowerCase();
    Array.prototype.forEach.call(document.querySelectorAll("#f-country .cmenu label"), function (l) {
      l.hidden = !!q && l.textContent.toLowerCase().indexOf(q) < 0;
    });
    toggleLabel();
  }
  document.addEventListener("click", function (e) {
    Array.prototype.forEach.call(document.querySelectorAll("#f-country details, #f-fuel details"), function (d) {
      if (d.open && !d.contains(e.target)) d.open = false;
    });
  });
  // everyone with a live decision in this dataset (the list grows as other reviewers' calls arrive)
  function fillBy() {
    var seen = {}, s = $("f-by");
    if (!s) return;
    LINES.concat(ITEMS).forEach(function (o) { if (o.reviewed && o.decided_by) seen[o.decided_by] = (seen[o.decided_by] || 0) + 1; });
    if (FS.by && !seen[FS.by]) seen[FS.by] = 0;
    s.innerHTML = '<option value="">anyone</option>' + Object.keys(seen).sort().map(function (k) {
      return '<option value="' + esc(k) + '">' + esc(k) + " (" + seen[k] + ")</option>";
    }).join("");
    s.value = FS.by;
  }
  function renderChips() {
    renderCountries();
    fillBy();
    var lab = {};
    facetSelect("f-decision", "decision", DEC, lab);
    var tot = {};
    LINES.forEach(function (l) { tot[l.kind] = 1; });
    ITEMS.forEach(function (i) { tot[i.kind] = 1; });
    facetSelect("f-kind", "kind", LINE_KINDS.concat(ITEM_KINDS.filter(function (k) { return !INFO_KINDS[k]; })), KIND_LABEL, tot);
    var tt = {};
    LINES.forEach(function (l) { tt[tierOf(l)] = 1; });
    facetSelect("f-tier", "tier", ["high", "medium", "low", "untiered"], lab, tt);
  }
  function fillSelect(id, values) {
    var s = $(id);
    values.forEach(function (v) { var o = document.createElement("option"); o.value = v; o.textContent = id === "f-dir" ? dirLabel(v) : id === "f-class_out" ? classLabel(v) : v; s.appendChild(o); });
  }
  function classLabel(v) { return String(v).toLowerCase().replace(/_/g, " "); }
  function uniq(arr) { return arr.filter(function (x, i) { return x && arr.indexOf(x) === i; }).sort(); }
  function fillFilters() {
    ["f-class_out", "f-column", "f-dir"].forEach(function (id) { $(id).innerHTML = '<option value="">any</option>'; });
    // only values some listed record carries: info items (confirmed) are never listed, so their classes / batches stay out
    var ASK = ITEMS.filter(function (i) { return !INFO_KINDS[i.kind]; }), LISTED = LINES.concat(ASK);
    fillSelect("f-class_out", uniq(LISTED.map(function (l) { return l.class_out; })));
    var cols = uniq(LINES.map(function (l) { return l.column; }));
    cols.sort(function (a, b) {
      var ia = D.columns.indexOf(a), ib = D.columns.indexOf(b);
      return (ia < 0 ? 9999 : ia) - (ib < 0 ? 9999 : ib);
    });
    fillSelect("f-column", cols);
    fillSelect("f-dir", D.dirs.filter(function (d) { return LISTED.some(function (o) { return o.dir === d; }); }));
  }
  function initFilters() {
    fillFilters();
    $("filters").addEventListener("click", function (e) {
      var c = e.target.closest("button[data-clear]");
      if (c) { clearOne(c.getAttribute("data-clear")); changed(); }
    });
    ["decision", "kind", "tier", "class_out", "column", "dir"].forEach(function (f) {
      $("f-" + f).onchange = function () { FS[f] = this.value; changed(); };
    });
    ["contested", "owners", "landed"].forEach(function (f) {
      $("f-" + f).onchange = function () { FS[f] = this.checked; changed(); };
    });
    $("f-fuel").onchange = function () {
      FS.fuel = Array.prototype.map.call(this.querySelectorAll("input:checked"), function (i) { return i.value; });
      if (FS.fuel.length === FUELS.length) FS.fuel = [];
      else if (!FS.fuel.length) FS.fuel = [NO_COUNTRY];   // nothing ticked: nothing matches
      changed();
    };
    $("f-country").onclick = function (e) { if (e.target.classList.contains("ctoggle")) { e.stopPropagation(); toggleCountries(); } };
    $("f-country").oninput = function (e) {
      if (e.target.classList.contains("csearch")) { CQ = e.target.value; filterCountryMenu(); }
    };
    $("f-country").onchange = function (e) {
      if (e.target.classList.contains("csearch")) return;
      FS.country = Array.prototype.map.call(this.querySelectorAll("input[type=checkbox]:checked"), function (i) { return i.value; });
      if (FS.country.length === this.querySelectorAll("input[type=checkbox]").length) FS.country = [];
      else if (!FS.country.length) FS.country = [NO_COUNTRY];   // all ticked = no filter
      changed();
    };
    // "decided by" and "sheet changed" only ever match decided lines: leave the undecided-only default
    $("f-by").onchange = function () { FS.by = this.value; if (FS.by && FS.decision === "undecided") FS.decision = ""; changed(); };
    $("f-drift").onchange = function () { FS.drift = this.checked; if (FS.drift && FS.decision === "undecided") FS.decision = ""; changed(); };
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
    ["contested", "owners", "landed", "drift"].forEach(function (f) { $("f-" + f).checked = FS[f]; });
    fillBy();
    $("f-q").value = FS.q; $("f-row").value = FS.row;
  }
  // Every filter that is set is a removable chip, so a control tucked behind "More filters"
  // never filters silently.
  function renderActive() {
    var chips = [], n = 0;
    function chip(id, text, hidden) {
      chips.push('<span class="chip on">' + esc(text) + ' <button type="button" data-clear="' + id +
        '" aria-label="clear ' + esc(text) + '">&times;</button></span>');
      if (hidden) n++;
    }
    if (FS.class_out) chip("class_out", "class: " + classLabel(FS.class_out), true);
    if (FS.column) chip("column", "column: " + FS.column, true);
    if (FS.dir) chip("dir", "batch: " + dirLabel(FS.dir), true);
    if (FS.by) chip("by", "decided by: " + FS.by, true);
    if (FS.drift) chip("drift", "sheet changed since decided", true);
    if (FS.contested) chip("contested", "contested", false);
    if (FS.owners) chip("owners", "owners tab", false);
    if (FS.landed) chip("landed", "incl. lines already in the backend", false);
    $("active-filters").innerHTML = chips.join(" ");
    $("active-filters").hidden = !chips.length;
    $("f-more").textContent = ($("more-filters").hidden ? "more filters" : "fewer filters") + (n ? " (" + n + ")" : "");
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
        .map(function (t) { return '<span class="dot ' + t + '" data-tip="' + t + ' tier" role="img" aria-label="' + t + ' tier"></span>'; }).join("");
      var rows = p.segments.map(function (s) { return s.sheet_row; }).filter(function (x) { return x != null; });
      var where = p.pid.indexOf("new:") === 0 ? "new row" : (p.pid === "scope" ? "scope" :
        (rows.length ? "row " + rows[0] + (rows.length > 1 ? " +" + (rows.length - 1) : "") : "no row"));
      var badge = p._todo ? '<span class="n todo">' + p._todo + " to decide</span>"
        : (p._n ? '<span class="n">' + p._n + " &middot; done</span>" : (p._ni ? '<span class="n">' + p._ni + " item" + (p._ni === 1 ? "" : "s") + "</span>" : '<span class="n"></span>'));
      var sn = segNames(p);
      h.push('<li data-i="' + i + '"' + (i === S.pipe ? ' class="sel"' : "") + '><div class="pname">' + esc(p.name || "(no name)") +
        (sn.length ? ' <span class="pseg">' + esc(sn[0]) + (sn.length > 1 ? " +" + (sn.length - 1) : "") + "</span>" : "") +
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
    return '<a href="' + esc(u) + '" target="_blank" rel="noopener">' + esc(t) + " ↗</a>";
  }
  function splitUrls(text) {
    return String(text || "").split(/,\s*(?=https?:\/\/)|\n+/).map(function (s) { return s.trim(); }).filter(Boolean);
  }
  // `tip` shows in the #tip popover on hover / keyboard focus; `note` (optional) scrolls under it when long
  function chip(text, cls, tip, note) {
    return '<span class="chip' + (cls ? " " + cls : "") + '"' + (tip ? ' tabindex="0"' + tipAttrs(tip, note) : "") + ">" + esc(text) + "</span>";
  }
  function tipAttrs(tip, note) {
    return ' data-tip="' + esc(tip) + '"' + (note ? ' data-tip-note="' + esc(note) + '"' : "") +
      ' aria-description="' + esc(tip + (note ? ". note: " + note : "")) + '"';
  }
  function tierChip(l) {
    var t = tierOf(l);
    return chip(t === "untiered" ? "untiered" : t, t === "untiered" ? "" : t,
      t === "untiered" ? "no confidence tier on this record: defaults to hold" : "confidence tier (rule 4)");
  }
  // One mark per proposed URL: ✓ when it loads, states the value and names the pipeline; else the failed checks.
  function vmark(u, l) {
    var v = null;
    (l.verifications || []).forEach(function (x) { if (x.url === u) v = x; });
    if (!v) return chip("unchecked", "", "no verification record for this URL: url_verifier did not check it at staging, so whether it loads, states the value or names the pipeline is unknown");
    var bad = [];
    if (!v.ok) bad.push("load");
    if (!v.contains_value) bad.push("value");
    if (!v.name_found) bad.push("name");
    var tip = "URL verifier checks:\n" +
      (v.ok ? "✓" : "✗") + " loads: the page fetched and its text is readable\n" +
      (v.contains_value ? "✓" : "✗") + " states value: the proposed value (or a unit equivalent) is on the page\n" +
      (v.name_found ? "✓" : "✗") + " names pipeline: the pipeline's name is on the page";
    return bad.length ? chip("✗ " + bad.join(", "), "bad", tip, v.note) : chip("✓", "ok", tip, v.note);
  }
  // a URL shortened for the table: host + path, decoded, Wayback shown as "archive › <origin>"
  function shortUrl(u) {
    var s = String(u);
    try { s = decodeURI(s); } catch (e) { /* keep as is */ }
    s = s.replace(/^https?:\/\/(www\.)?/i, "");
    var wb = s.match(/^web\.archive\.org\/web\/\d+[a-z_]*\/(?:https?:\/\/)?(?:www\.)?(.*)$/i);
    if (wb) s = "archive › " + wb[1];
    s = s.replace(/\/$/, "");
    return s.length > 64 ? s.slice(0, 63) + "…" : s;
  }
  function shortLink(u) {
    if (!/^https?:\/\//i.test(u)) return esc(u);
    return '<a href="' + esc(u) + '" target="_blank" rel="noopener">' + esc(shortUrl(u)) + "</a>";
  }
  function tag(t) { return t ? '<span class="tag tag-' + t + '">' + t + "</span>" : ""; }
  function concernNote(p, col, l) {
    var t = p._cont[col];
    if (l && agreeCols(l, p).indexOf(col) >= 0) {
      return '<div class="concern-inline">concern agrees with this value: accepting resolves it' + (t ? " (" + esc(t) + ")" : "") + "</div>";
    }
    return '<div class="concern-inline">concern: ' + (t ? esc(t) : "a validity concern contests this value (no detail recorded)") + "</div>";
  }
  // one value row: field | now | proposed | tag. has=false means context only (not proposed).
  function valueRow(l, p, c, was, now, has) {
    var contested = (c in p._cont) && !blankv(was);
    var wasH = blankv(was) ? "" : '<span class="' + (contested ? "tint-cont" : "") + '">' + esc(was) + "</span>";
    var nowH, t = "", same = false;
    if (!has || (!blankv(was) && String(was).trim() === String(now).trim())) { nowH = wasH; same = true; }
    else if (blankv(now)) { nowH = '<span class="blank">(clear)</span>'; t = "clear"; }
    else { t = blankv(was) ? "fill" : "change"; nowH = '<span class="newv c-' + t + '">' + esc(now) + "</span>"; }
    var r = '<tr class="' + (same ? "same" : "") + '"><td class="f">' + esc(c) + "</td><td>" + wasH + "</td><td>" + nowH + '</td><td class="t">' + tag(t) + "</td></tr>";
    if (contested) r += '<tr class="note"><td></td><td colspan="3">' + concernNote(p, c, l) + "</td></tr>";
    return r;
  }
  function valueRows(l, p, skipCol) {
    var pv = l.proposed_values || {}, cols = Object.keys(pv), cur = l.current || {}, ctx = false;
    if (!cols.length) {          // nothing proposed: the current values this [ref] covers, for context
      cols = (l.value_cols || []).filter(function (c) { return !blankv(cur[c]); }).slice(0, 8);
      ctx = true;
    }
    return cols.map(function (c) {
      if (c === skipCol) return "";
      if (!ctx && blankv(pv[c]) && blankv(cur[c])) return "";
      return valueRow(l, p, c, cur[c], pv[c], !ctx);
    }).join("");
  }
  // the [ref] row: the cell now, and the cell it would be (new URLs tinted with a check mark, kept ones muted)
  function refRow(l) {
    var col = l.ref_col || "[ref]";
    var cur = splitUrls(l.current_ref), prop = l.proposed_refs || [];
    var cell = l.ref_cell_text ? splitUrls(l.ref_cell_text) : prop.slice();
    var nowH = cur.length ? "<ul>" + cur.map(function (u) {
      return '<li class="' + (cell.length && cell.indexOf(u) < 0 ? "dropped" : "") + '">' + shortLink(u) + "</li>";
    }).join("") + "</ul>" : "";
    var propH, t;
    if (l.kind === "status" && l.class_out === "STALE") { propH = '<span class="muted">none (stale-status flag)</span>'; t = ""; }
    else if (!cell.length) {
      propH = '<span class="muted">' + esc({DEAD_LINK: "link gone (404/410), no replacement found", REF_BLOCKED: "could not be fetched from here, no replacement found", REF_UNSUPPORTED: "page loads but does not support the value"}[l.class_out] || "no URL proposed") + "</span>";
      t = "";
    } else {
      var added = cell.filter(function (u) { return cur.indexOf(u) < 0; });
      var dropped = cur.filter(function (u) { return cell.indexOf(u) < 0; });
      t = !cur.length ? "fill" : (dropped.length ? (added.length ? "replace" : "drop") : (added.length ? "add" : ""));
      if (l.class_out === "REVERIFIED" && !added.length && !dropped.length) t = "re-verified";
      propH = !added.length && !dropped.length ? "<ul>" + cell.map(function (u) { return '<li class="kept">' + shortLink(u) + "</li>"; }).join("") + "</ul>"
        : "<ul>" + cell.map(function (u) {
          var isNew = cur.indexOf(u) < 0;
          return isNew ? '<li><span class="newref c-fill">' + shortLink(u) + "</span> " + vmark(u, l) + "</li>"
                       : '<li class="kept">' + shortLink(u) + "</li>";
        }).join("") + "</ul>";
    }
    return '<tr class="ref"><td class="f">' + esc(col) + "</td><td>" + nowH + "</td><td>" + propH + '</td><td class="t">' + tag(t) + "</td></tr>";
  }
  function pairTable(rows) {
    return '<table class="pair"><thead><tr><th></th><th>now</th><th>proposed</th><th></th></tr></thead><tbody>' + rows + "</tbody></table>";
  }
  function lineCols(l) {
    var c = l.column || "";
    if (l.kind === "status") return "Status";
    if (l.kind === "route") return "Route";
    return String(l.ref_col || c).replace(/\s*\[ref\]$/, "") || c;
  }
  function lineBody(l, p) {
    if (l.kind === "new_row") return newRowBody(l);
    if (l.kind === "route") return routeBody(l, p);
    if (l.kind === "status") return statusBody(l, p);
    return pairTable(valueRows(l, p) + refRow(l));   // ref, fill, oo
  }
  function statusBody(l, p) {
    var cs = l.current_status || "", ps = l.proposed_status || "";
    var rows = valueRow(l, p, "Status", cs, ps, !blankv(ps)) + valueRows(l, p, "Status") + refRow(l);
    var facts = [];
    if (l.evidence_date) facts.push(chip("evidence " + l.evidence_date));
    if (l.class_out === "STALE") facts.push(chip("stale flag", "warn"));
    if (l.publishers < 2) facts.push(chip("single source", "single", "fewer than 2 distinct publishers: a status change stays green only on 2+ (rule 4)"));
    else facts.push(chip(l.publishers + " publishers"));
    return pairTable(rows) + '<div class="facts">' + facts.join(" ") + "</div>";
  }
  function routeBody(l, p) {
    var geo = l.geometry_file ? '/geo/' + encodeURI(String(l.dir).replace(/^batches\//, "") + "/" + l.geometry_file) : "";
    var geoA = !geo ? "" : (Store.showGeo ? '<a href="#" class="only" data-geo="' + esc(l.dir + "/" + l.geometry_file) + '">'
      : '<a href="' + esc(geo) + '" target="_blank" rel="noopener">');
    var cur = l.current_route_accuracy, sug = l.suggested_route_accuracy;
    var rows = [
      ["candidate length", l.length_km == null ? "" : l.length_km + " km"],
      ["sheet length", l.sheet_length_km == null ? "" : l.sheet_length_km + " km"],
      ["ratio", l.length_ratio == null ? "" : String(l.length_ratio)]
    ].filter(function (r) { return r[1] !== ""; }).map(function (r) { return '<div class="k">' + r[0] + '</div><div class="v">' + esc(r[1]) + "</div>"; });
    rows.push('<div class="k">RouteAccuracy</div><div class="v">' + (blankv(cur) ? "" : '<span class="was">' + esc(cur) + "</span>") +
      (blankv(sug) ? "" : '<span class="arrow">→</span><span class="newv">' + esc(sug) + "</span>") + "</div>");
    rows.push('<div class="k">QC</div><div class="v">' + (l.qc_passed ? chip("✓ passed", "ok") : chip("✗ did not pass", "bad")) + "</div>");
    rows.push('<div class="k">geometry</div><div class="v">' + (geo ? geoA + "<code>" + esc(l.geometry_file) + "</code> ↗</a>" : '<span class="muted">none</span>') + "</div>");
    return '<div class="chg">' + rows.join("") + '</div><div class="faint" style="margin-top:4px">accepting records approval for the §8 apply; it writes no cell.</div>';
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
    (l.covers || []).forEach(function (c) {
      if (c.notes) d.push('<div class="dtxt"><span class="k">researcher notes (' + esc(c.ref_col || "refs") + " record):</span> " + esc(c.notes) + "</div>");
      (c.verifications || []).forEach(function (v) {
        d.push('<div class="dtxt"><span class="k">' + esc(v.url) + " (" + esc(c.ref_col || "refs") + " record):</span> " + esc(v.note) + "</div>");
      });
    });
    if (l.staleness_rule) d.push('<div class="dtxt"><span class="k">staleness rule:</span> ' + esc(l.staleness_rule) + "</div>");
    (l.covers || []).forEach(function (c) {
      d.push('<div class="dtxt"><span class="k">also decides:</span> the refs-leg record for ' + esc(c.ref_col || "Status [ref]") + " (" +
        esc(KIND_LABEL[c.kind] || c.kind) + " \u00b7 " + esc(c.class_out || "?") + (c.dir !== l.dir ? " \u00b7 " + esc(dirLabel(c.dir)) : "") +
        (c.tier && c.tier !== l.tier ? " \u00b7 its tier " + esc(c.tier) : "") + "); its refs are in the table</div>");
    });
    var misc = ["batch " + dirLabel(l.dir), "class " + (l.class_in || "?") + " → " + (l.class_out || "?"),
                "default " + (l.default || "hold"),
                "link live: " + (l.link_live == null ? "unknown" : l.link_live)];
    if (l.source_language) misc.push("lang " + l.source_language);
    if (l.also_in && l.also_in.length) misc.push("also in " + l.also_in.map(dirLabel).join(", "));
    if (l.kind === "oo") misc.push("owners tab row " + l.sheet_row + (l.tracker_sheet_row ? ", tracker row " + l.tracker_sheet_row : ""));
    d.push('<div class="dtxt"><span class="k">record:</span> ' + esc(misc.join(" · ")) + "</div>");
    return '<details data-more><summary>notes &amp; record</summary>' + d.join("") + "</details>";
  }
  function lineHtml(l, p) {
    var chips = [];
    if (l.kind === "oo" || l.kind === "new_row") chips.push(chip(KIND_LABEL[l.kind], l.kind === "new_row" ? "newrow" : "oo"));
    chips.push(l.kind === "new_row" ? chip(tierOf(l) === "untiered" ? "untiered" : tierOf(l), tierOf(l) === "untiered" ? "" : tierOf(l)) : tierChip(l));
    var lock = lockCols(l, p);
    var agree = agreeCols(l, p);
    if (l._cont) chips.push(chip("contested", "cont", "a validity concern contests a value on this line"));
    if (agree.length) chips.push(chip("resolves concern", "ok", "an open concern's contested value on " + agree.join(", ") + " equals this proposed value; accepting it records a dismissed call on the concern"));
    if (lock.length) chips.push(chip("held: concern open", "warn", "a validity concern contests " + lock.join(", ") + " and has no call yet; accept is refused until it does (hold / reject are still allowed)"));
    if (l.in_backend) chips.push(chip("in backend", "", "the snapshot already holds this value and these refs"));
    if (l.drift && cur(l)) chips.push(chip("sheet changed since decided", "warn", "the backend cells this call was judged against have changed since (it was decided on " + (l.drift.decided_snapshot || "an earlier snapshot") + "): look again, then press the call again to confirm it against the current sheet"));
    if (l.live) chips.push(chip("sheet changed live", "warn", "the backend sheet, read just now, differs from what this line was judged against: " + l.live.map(function (c) { return c[0] + " was " + (c[1] || "blank") + ", is now " + (c[2] || "blank"); }).join("; ") + ". publish again to rebuild the proposal against the new values"));
    if (l.sheet_row_moved) chips.push(chip("row re-resolved", "", "the record's sheet_row was stale; this is the live row"));
    var title = l.kind === "new_row" ? (l.name || "candidate") : lineCols(l);
    var h = '<div class="row1"><span class="col">' + esc(title) + "</span> " + chips.join(" ") +
      '<span class="where">' + esc(rowLabel(l)) + "</span></div>";
    h += lineBody(l, p);
    var dis = !Store.caps.decide;
    h += '<div class="controls">' + [["accept", "a"], ["hold", "h"], ["reject", "r"]].map(function (b) {
      var off = dis || (b[0] === "accept" && lock.length);
      return '<button type="button" class="b-' + b[0] + '" data-decide="' + b[0] + '"' +
        (off ? tipAttrs(dis ? NOT_YET : "held: a concern on " + lock.join(", ") + " is open") + ' aria-disabled="true"' : "") +
        ' aria-pressed="' + (cur(l) === b[0]) + '">' + b[0] + "</button>";
    }).join("") + '<button type="button" class="b-suggest" data-suggest="1"' + (dis ? ' aria-disabled="true"' + tipAttrs(NOT_YET) : "") +
      ' aria-pressed="' + (cur(l) === "suggest") + '">suggest</button>' + (cur(l) ? '<button type="button" class="ghost" data-undo="1">undo</button>' : "") +
      '<span class="dstat" id="dstat-' + l._i + '" role="status">' + esc(decisionText(l)) + "</span></div>";
    h += detailsHtml(l);
    return h;
  }

  // ---- items ----
  var HIDE = {call_note: 1, decided_by: 1, decided_at: 1, decision_note: 1, key: 1, dir: 1, also_in: 1, sheet_row: 1, sheet_row_moved: 1, contested: 1, "default": 1, call: 1, reviewed: 1,
              kind: 1, project_id: 1, wiki: 1, pipeline_name: 1, segment_name: 1, value_cols: 1, values: 1, primary_value_col: 1,
              primary_value: 1, _item: 1, _p: 1, countries: 1};
  var BODY = ["recommendation", "action", "detail", "summary", "monitor_reason", "researcher_notes", "staged_note", "staleness_rule", "corridor_desc"];
  var CONCERN_ISSUE = {existence: "its existence is in doubt", duplicate: "it may duplicate another row",
                       classification: "its classification may be wrong", attribution: "its owner / operator attribution may be wrong",
                       spec: "a spec value (capacity, length, diameter, dates) may be off"};
  function concernHead(it) {
    var issue = CONCERN_ISSUE[it.concern_type], v = it.verdict || "";
    if (!issue) return (it.concern_type || "concern") + (v ? " — " + v : "");
    if (/^confirmed/.test(v)) return "pipeline is real, but " + issue;
    return "open doubt: " + issue;
  }
  function itemHead(it) {
    switch (it.kind) {
      case "concern": return concernHead(it);
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
    var h = '<div class="item' + (ck.length ? " conts" : "") + (it.call && it.reviewed ? " done" : "") + '"><div class="row1">' + chip(KIND_LABEL[it.kind], "") +
      " <b>" + esc(itemHead(it)) + "</b>" + (it.tier ? " " + tierChip(it) : "") +
      '<span class="where">' + row.replace(/ &middot; $/, "") + "</span></div>";
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
    var hint = it.kind === "concern" ? "any call releases the lines this concern holds (confirmed: it stands; dismissed: closed; needs research: to an Update worklist)" : "";
    return '<div class="icall"><label' + (dis ? tipAttrs(NOT_YET) : (hint ? tipAttrs(hint) : "")) + '>call <select data-icall="' + it._i + '"' + (dis ? " disabled" : "") + ">" + opts + "</select></label>" +
      '<input type="text" data-inote="' + it._i + '" placeholder="note" value="' + esc(it.call_note || "") + '"' + (dis ? " disabled" : "") + ">" +
      '<span class="dstat" id="istat-' + it._i + '" role="status">' + esc(itemStat(it)) + "</span></div>";
  }
  function itemsHtml(p) {
    var ask = p.items.filter(function (it) { return !INFO_KINDS[it.kind]; });
    if (!ask.length) return '<div class="hiddennote">nothing to decide on this pipeline.</div>';
    var by = {};
    ask.forEach(function (it) { (by[it.kind] = by[it.kind] || []).push(it); });
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
    if (S.pipe < 0) { card.innerHTML = '<div class="empty">nothing matches the filters.</div>'; S.shown = []; return; }
    var p = D.pipelines[S.pipe], ranges = parseRows(FS.row), q = FS.q.trim().toLowerCase();
    var isNew = p.pid.indexOf("new:") === 0, isScope = p.pid === "scope";
    var segs = p.segments;
    var open = p.lines.filter(function (l) { return !cur(l); }).length;
    var segTxt = segs.length ? "row" + (segs.length > 1 ? "s " : " ") + segs.map(function (s) { return s.sheet_row; }).join(", ") : "";
    var ctx = ['<b>' + esc(isNew ? "new candidate, not in the sheet" : (isScope ? "scope-level" : segTxt || "no sheet row")) + "</b>",
               p.country && esc(p.country), p.status && "status: " + esc(p.status),
               p.wiki && '<a href="' + esc(p.wiki) + '" target="_blank" rel="noopener">wiki ↗</a>',
               tierSummary(p)]
      .filter(Boolean).map(function (x) { return "<span>" + x + "</span>"; }).join("");
    var h = '<div class="cardhead">' + "<h2>" + (isNew || isScope ? "" : '<span class="pid"' + tipAttrs("click to copy the ProjectID") + '>' + esc(p.pid) + "</span>") +
      '<a href="#" class="only" data-tab="all"' + tipAttrs("review everything on this pipeline: every line (filters ignored) and every item") + '>' + esc(p.name || "(no name)") + "</a>" +
      (segNames(p).length ? '<span class="hseg">' + esc(segNames(p).join(" / ")) + "</span>" : "") + '</h2><div class="ctx">' + ctx + "</div>";
    var askItems = p.items.filter(function (it) { return !INFO_KINDS[it.kind]; });
    var nOpenItems = askItems.filter(function (it) { return !it.call; }).length;
    // "(3 to decide)", "(1 of 3 to decide)", "(3, all decided)"
    function todo(n, total) {
      if (!total) return "(0)";
      if (!n) return "(" + total + ", all decided)";
      return "(" + (n === total ? n : n + " of " + total) + " to decide)";
    }
    h += '<div class="tabs" role="tablist">' +
      '<button type="button" role="tab" data-tab="lines" aria-selected="' + (S.tab === "lines") + '">lines ' + todo(open, p.lines.length) + "</button>" +
      '<button type="button" role="tab" data-tab="items" aria-selected="' + (S.tab === "items") + '">items ' + todo(nOpenItems, askItems.length) + "</button>" +
      '<button type="button" role="tab" data-tab="all" aria-selected="' + (S.tab === "all") + '"' + tipAttrs("every line (filters ignored) and every item on this pipeline; also: click the name") + '>everything</button></div></div>';
    if (S.tab === "items") {
      S.shown = []; S.line = -1;
      card.innerHTML = h + itemsHtml(p);
      return;
    }
    // lines the filter lets through, grouped by segment when the PID spans several sheet rows
    var all = S.tab === "all";
    var keep = all ? p.lines.slice() : p.lines.filter(function (l) { return match(l, p, FS, null, ranges, q); });
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
        h += '<div class="line tier-' + tierOf(l) + (cur(l) ? " d-" + cur(l) : "") + (lockCols(l, p).length ? " locked" : "") + (dimmed(l) ? " dim" : "") +
          (l.kind === "new_row" ? " newcard" : "") + (l._i === S.line ? " cur" : "") + '" id="line-' + l._i + '" data-i="' + l._i + '">' + lineHtml(l, p) + "</div>";
      });
    });
    if (hidden) h += '<div class="hiddennote">' + hidden + " more line" + (hidden === 1 ? "" : "s") + " on this pipeline " + (hidden === 1 ? "is" : "are") +
      ' hidden by the filter &mdash; <a href="#" class="only" data-showall="1">show all</a></div>';
    if (!keep.length && !hidden) h += '<div class="hiddennote">no lines on this pipeline.</div>';
    if (all) h += '<h3 class="allitems">items</h3>' + itemsHtml(p);
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
    var l = LINES[S.line], u = firstRef(l);
    if (u && l.kind === "route" && Store.showGeo) return Store.showGeo(l.dir + "/" + l.geometry_file);
    if (u) window.open(u, "_blank", "noopener"); else toast("this line has no ref to open");
  }
  function notYet() { toast(NOT_YET); }
  function setStat(i, text, failed) {
    var e = $("dstat-" + i);
    if (e) { e.textContent = text; e.className = "dstat" + (failed ? " err" : (text === "saving…" ? " saving" : "")); }
  }
  // Save one line's call. The UI changes only after the server confirms; while it is in flight the
  // line says "saving…", then "accepted by <reviewer> <time>" (or the refusal). No confirm dialog.
  function save(l, rec, advance) {
    if (!Store.caps.decide) return notYet();
    if (S.saving[l.key]) return;
    S.saving[l.key] = true;
    setStat(l._i, "saving…");
    var pp = D.pipelines[l._p], before = lockedCount(pp);
    Store.decide([rec]).then(function (saved) {
      applySaved(saved);
      S.stay[l.key] = true;
      banner("");
      var keepLine = S.line;
      refilter(true);
      resolvedToast(saved, before, pp);
      if (keepLine >= 0 && $("line-" + keepLine)) setLine(keepLine, true);
      if (advance && S.line === l._i) nextUndecided();
    }).catch(function (e) {
      setStat(l._i, "not saved: " + e.message, true);
      toast("not saved: " + e.message);
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
    // a call made against other backend cells than this dataset shows (publish.py `basis`) is marked, never dropped
    l.drift = (!r.undecided && r.basis && l.basis && r.basis !== l.basis) ? {decided_snapshot: r.snapshot || "", decided_basis: r.basis} : null;
    if (l.covers) {          // the server wrote the same call to every covered record
      l.covers.forEach(function (c) { c.decision = l.decision; c.decided_by = l.decided_by; c.decided_at = l.decided_at; });
      l.uncovered = [];
    }
    noteSession(r, "decision");
  }
  var REMOTE = false;
  // Records from the store that this page did not save (another reviewer, or another tab): applied
  // to the data, not counted as this session's. Lines on the open card stay in view. -> how many applied.
  function applyRemote(recs) {
    var n = 0, open = D.pipelines[S.pipe];
    REMOTE = true;
    try {
      (recs || []).forEach(function (r) {
        var item = "call" in r, o = item ? ITEM_BY_KEY[r.key] : LINE_BY_KEY[r.key];
        if (!o) return;                       // a cover record (its line carries it) or another dataset version
        if (item) applyItemRecord(r); else applyRecord(r);
        if (!item && open && D.pipelines[o._p] === open) S.stay[r.key] = true;
        n++;
      });
    } finally { REMOTE = false; }
    return n;
  }
  // true while a re-render would take something from under the reviewer's hands
  function busy() {
    var a = document.activeElement;
    return $("dialog").open || !!document.querySelector("#card .sform") || Object.keys(S.saving).length > 0 ||
      !!(a && /^(INPUT|TEXTAREA|SELECT)$/.test(a.tagName) && $("card").contains(a));
  }
  function rerender() {
    var keepLine = S.line;
    refilter(true);
    if (keepLine >= 0 && $("line-" + keepLine)) setLine(keepLine, true);
  }
  function noteSession(r, field) {
    if (REMOTE) return;
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
  // /api/decide returns line records, then item records (`call`) for concerns the accept resolved
  function applySaved(saved) {
    saved.forEach(function (r) { if ("call" in r) applyItemRecord(r); else applyRecord(r); });
  }
  function resolvedToast(saved, before, p) {
    var n = saved.filter(function (r) { return "call" in r; }).length;
    if (!n) return;
    var freed = Math.max(0, before - lockedCount(p));
    toast("concern resolved by this accept: " + freed + " line" + (freed === 1 ? "" : "s") + " unlocked");
  }
  function lockedCount(p) { return p.lines.filter(function (l) { return lockCols(l, p).length; }).length; }
  // Save one item's call. Same in-place feedback as a line; when a concern's call releases the
  // lock, the card's lines unlock in the same re-render (no reload).
  function saveItem(it, rec) {
    if (!Store.caps.decide) return notYet();
    if (S.saving[it.key]) return;
    S.saving[it.key] = true;
    var p = D.pipelines[it._p], before = lockedCount(p), el = $("istat-" + it._i);
    if (el) { el.textContent = "saving…"; el.className = "dstat saving"; }
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
      if (e2) { e2.textContent = "not saved: " + e.message; e2.className = "dstat err"; }
      toast("not saved: " + e.message);
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
  // Suggest: an inline form on the current line. Prefill = the proposed value (fill / oo / status) or the
  // proposed [ref] cell text (ref lines). Enter saves decision "suggest" with suggested_value + note; Esc cancels.
  function suggestPrefill(l) {
    if (l.kind === "ref") return l.ref_cell_text || (l.proposed_refs || []).join(", ");
    if (l.kind === "status") return l.proposed_status || "";
    if (l.kind === "fill" || l.kind === "oo") {
      var pv = l.proposed_values || {}, v = pv[l.column];
      if (blankv(v)) { var ks = Object.keys(pv).filter(function (k) { return !blankv(pv[k]); }); v = ks.length ? pv[ks[0]] : ""; }
      return blankv(v) ? "" : String(v);
    }
    if (l.kind === "new_row") return l.name || "";
    return "";
  }
  function closeSuggest() {
    var f = document.querySelector("#card .sform");
    if (f) f.parentNode.removeChild(f);
  }
  function openSuggest(l) {
    if (!Store.caps.decide) return notYet();
    if (!l) return;
    var el = $("line-" + l._i);
    if (!el) return;
    closeSuggest();
    setLine(l._i, true);
    var prior = l.reviewed && l.decision === "suggest";
    var f = document.createElement("form");
    f.className = "sform";
    f.innerHTML = '<label>suggested value <input type="text" class="sv" autocomplete="off"></label>' +
      '<label>note <input type="text" class="sn" autocomplete="off" placeholder="why"></label>' +
      '<button type="submit" class="sv-save">save suggestion</button><button type="button" class="ghost sv-cancel">cancel (esc)</button>' +
      '<span class="faint sv-err" role="alert"></span>';
    var sv = f.querySelector(".sv"), sn = f.querySelector(".sn"), err = f.querySelector(".sv-err");
    sv.value = prior ? (l.suggested_value || "") : suggestPrefill(l);
    sn.value = prior ? (l.decision_note || "") : "";
    f.addEventListener("keydown", function (e) {
      if (e.key === "Escape") { e.preventDefault(); e.stopPropagation(); closeSuggest(); }
    });
    f.querySelector(".sv-cancel").onclick = closeSuggest;
    f.onsubmit = function (e) {
      e.preventDefault();
      if (blankv(sv.value) && blankv(sn.value)) { err.textContent = "give a suggested value or a note"; return; }
      var b = f.querySelector(".sv-save"); b.disabled = true;
      if (S.saving[l.key]) return;
      S.saving[l.key] = true;
      Store.decide([{key: l.key, decision: "suggest", suggested_value: sv.value, note: sn.value}]).then(function (saved) {
        applySaved(saved);
        S.stay[l.key] = true;
        banner("");
        var keepLine = S.line;
        refilter(true);
        if (keepLine >= 0 && $("line-" + keepLine)) setLine(keepLine, true);
        toast("suggestion saved");
      }).catch(function (e2) {
        b.disabled = false; err.textContent = "not saved: " + e2.message;
      }).then(function () { delete S.saving[l.key]; });
    };
    var ctl = el.querySelector(".controls");
    ctl.parentNode.insertBefore(f, ctl.nextSibling);
    sv.focus(); sv.select();
  }
  function suggestKey() {
    if (S.tab === "items") return toast("the Items tab takes calls, not suggestions: press i to go back to the lines");
    openSuggest(LINES[S.line]);
  }
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
    S: function () { if (SHOW_SUMMARY) showSummary(); },
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
              ["a / h / r", "accept / hold / reject the line; saved at once, then on to the next open line"], ["s", "suggest a different value: inline form on the line (value + note; enter saves, esc cancels); routed to an update worklist by update_seed.py"],
              ["A", "accept every default-accept line in view (asks first, with the count)"], ["i", "switch the card between lines and items; calls save on change"],
              ["S", "session summary (counts, this session, copy as markdown)"],
              ["u", "undo: the line goes back to undecided"], ["o", "open the line's first ref (new tab)"], ["d", "show / hide the line's details"],
              ["/", "search"], ["?", "this help"]];
  function showHelp() {
    var dlg = $("dialog");
    dlg.setAttribute("data-kind", "help");
    dlg.innerHTML = "<h3>keyboard</h3><table>" + HELP.map(function (r) { return "<tr><td><kbd>" + r[0] + "</kbd></td><td>" + r[1] + "</td></tr>"; }).join("") +
      '</table><div class="actions"><button type="button" id="dlg-close">close</button></div>';
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
    var pidEl = e.target.closest(".pid");
    if (pidEl) { copyText(pidEl.textContent, pidEl.textContent + " copied"); return; }
    var ga = e.target.closest("[data-geo]");
    if (ga) { e.preventDefault(); Store.showGeo(ga.getAttribute("data-geo")); return; }
    if (e.target.closest("[data-showall]")) {
      e.preventDefault();
      var keepPipe = S.pipe;
      FS = defaults(); FS.decision = ""; FS.landed = true;
      syncControls(); S.pin = keepPipe; refilter(true); writeRoute(false);
      return;
    }
    var tb = e.target.closest("[data-tab]");
    if (tb && tb.tagName === "A") e.preventDefault();
    if (tb) {
      if (tb.getAttribute("data-tab") === "all") S.pin = S.pipe;   // deciding lines here must not drop the pipeline from the queue
      if (S.tab !== tb.getAttribute("data-tab")) { S.tab = tb.getAttribute("data-tab"); renderCard(); }
      return;
    }
    var sb = e.target.closest("button[data-suggest]");
    var b = e.target.closest("button[data-decide]");
    var ub = e.target.closest("button[data-undo]");
    var ln = e.target.closest(".line");
    if (ln) setLine(+ln.getAttribute("data-i"), true);
    if (ub && !ub.disabled) return undoCurrent();
    if (sb) {
      if (!Store.caps.decide) return notYet();
      return openSuggest(LINES[S.line]);
    }
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
  var BULK_TITLE = {defaults: "accept all defaults in view", hold: "hold all in view", "pipe-high": "accept all high for this pipeline"};
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
      (skipTxt ? '<p class="faint">skipped: ' + esc(skipTxt) + ".</p>" : "") +
      '<p class="faint" id="bulk-err"></p><div class="actions"><button type="button" class="ghost" id="dlg-cancel">cancel</button>' +
      '<button type="button" id="dlg-ok">' + (t.decision === "accept" ? "accept " : "hold ") + t.lines.length + "</button></div>";
    $("dlg-cancel").onclick = function () { dlg.close(); };
    $("dlg-ok").onclick = function () {
      var ok = $("dlg-ok"); ok.disabled = true; ok.textContent = "saving…";
      var pbefore = {};
      t.lines.forEach(function (l) { pbefore[l._p] = lockedCount(D.pipelines[l._p]); });
      Store.decide(t.lines.map(function (l) { return {key: l.key, decision: t.decision}; })).then(function (saved) {
        applySaved(saved);
        t.lines.forEach(function (l) { S.stay[l.key] = true; });
        dlg.close();
        refilter(true);
        var nl = saved.filter(function (r) { return !("call" in r); }).length;
        toast((t.decision === "accept" ? "accepted " : "held ") + nl + " line" + (nl === 1 ? "" : "s"));
        Object.keys(pbefore).forEach(function (pi) { resolvedToast(saved, pbefore[pi], D.pipelines[pi]); });
      }).catch(function (e) {
        ok.disabled = false; ok.textContent = "retry";
        $("bulk-err").textContent = "not saved: " + e.message;
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
    ITEMS.forEach(function (it) { if (!INFO_KINDS[it.kind]) bump(ik, it.kind, it.call ? "decided" : "open"); });
    var sess = Object.keys(S.session).map(function (k) { return S.session[k]; }), sw = {}, sd = {};
    sess.forEach(function (r) { sw[r.what] = (sw[r.what] || 0) + 1; sd[r.dir] = (sd[r.dir] || 0) + 1; });
    var calls = {accept: 0, hold: 0, reject: 0, suggest: 0};
    LINES.forEach(function (l) { if (cur(l) && cur(l) in calls) calls[cur(l)]++; });
    return {calls: calls, kinds: kinds, tiers: tiers, dirs: dirs, itemKinds: ik, sessWhat: sw, sessDirs: sd, sessN: sess.length};
  }
  function callsText(c) { return c.accept + " accepted, " + c.hold + " held, " + c.reject + " rejected, " + c.suggest + " suggested"; }
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
      "  \nThis session: " + m.sessN + " saved (" + (Object.keys(m.sessWhat).map(function (k) { return m.sessWhat[k] + " " + k; }).join(", ") || "none") + ")  \nDecided lines by call: " + callsText(m.calls) + "\n\n" +
      "### Lines by kind\n\n" + tab(["kind"].concat(H.slice(1)), kinds) + "\n### Lines by tier\n\n" + tab(["tier"].concat(H.slice(1)), tiers) +
      "\n### Items\n\n" + tab(["kind", "with a call", "without"], items) + "\n### By batch\n\n" + tab(["batch", "decided", "open", "in backend", "this session"], dirs);
    return out;
  }
  function copyText(text, msg) {
    msg = msg || "summary copied";
    function fallback() {
      var ta = document.createElement("textarea");
      ta.value = text; document.body.appendChild(ta); ta.select();
      var ok = false;
      try { ok = document.execCommand("copy"); } catch (e) { ok = false; }
      document.body.removeChild(ta);
      toast(ok ? msg : "could not copy: select the text by hand");
    }
    if (navigator.clipboard && navigator.clipboard.writeText) navigator.clipboard.writeText(text).then(function () { toast(msg); }, fallback);
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
    dlg.innerHTML = "<h3>session summary</h3><p>" + dec + " of " + tot + " lines decided &middot; " + bk + " in the backend &middot; " + (tot - dec - bk) + " open. " +
      "<b>this session (" + esc(ME) + "):</b> " + m.sessN + " saved" + (m.sessN ? " (" + Object.keys(m.sessWhat).map(function (k) { return m.sessWhat[k] + " " + esc(k); }).join(", ") + ")" : "") + ".<br>decided lines by call: " + callsText(m.calls) + ".</p>" +
      "<h4>lines by kind</h4>" + sumTable(["kind"].concat(L), sumRows(m.kinds, LINE_KINDS, KIND_LABEL)) +
      "<h4>lines by tier</h4>" + sumTable(["tier"].concat(L), sumRows(m.tiers, ["high", "medium", "low", "untiered"])) +
      "<h4>items</h4>" + sumTable(["kind", "with a call", "without"], items) +
      "<h4>by batch</h4>" + sumTable(["batch", "decided", "open", "in backend", "this session"], dirs) +
      '<div class="actions"><button type="button" class="ghost" id="dlg-copy">copy summary as markdown</button><button type="button" id="dlg-close">close</button></div>';
    $("dlg-close").onclick = function () { dlg.close(); };
    $("dlg-copy").onclick = function () { copyText(summaryMarkdown(m)); };
    dlg.showModal();
  }

  // ---- refresh backend ----
  function refreshBackend() {
    if (!Store.caps.refresh) return toast("this server cannot refresh the backend (started with --no-build)");
    var dlg = $("dialog");
    dlg.setAttribute("data-kind", "refresh");
    dlg.innerHTML = "<h3>refresh backend</h3><p>this pulls the live sheet (read-only, about a minute), rebuilds this dataset from the new snapshot, " +
      "and marks lines the sheet already holds as <i>in backend</i> (a machine record, not a review). your decisions are kept.</p>" +
      '<p class="faint" id="rf-err"></p><div class="actions"><button type="button" class="ghost" id="dlg-cancel">cancel</button><button type="button" id="dlg-ok">pull and rebuild</button></div>';
    $("dlg-cancel").onclick = function () { dlg.close(); };
    $("dlg-ok").onclick = function () {
      var ok = $("dlg-ok"); ok.disabled = true; ok.textContent = "pulling…"; $("dlg-cancel").disabled = true;
      var btn = $("sync"); btn.disabled = true;
      Store.refresh().then(function (r) {
        return Store.load().then(function (data) {
          dlg.close();
          reload(data);
          toast("refreshed: snapshot " + r.snapshot + ", " + r.lines + " lines, " + r.synced + " newly in backend");
        });
      }).catch(function (e) {
        ok.disabled = false; ok.textContent = "retry"; $("dlg-cancel").disabled = false;
        $("rf-err").textContent = "refresh failed: " + e.message; $("rf-err").className = "err";
      }).then(function () { btn.disabled = !Store.caps.refresh; });
    };
    dlg.showModal();
  }
  // live drift check (gas.js liveCheck): lines whose watched backend cells differ from the published ones
  function setLive(res) {
    var hit = {};
    ((res && res.changed) || []).forEach(function (c) { if (c.cols.length) hit[c.t + "|" + c.pid + "|" + c.row] = c.cols; });
    var n = 0;
    D.pipelines.forEach(function (p) {
      p.lines.forEach(function (l) {
        l.live = null;
        if (l.kind === "new_row" || l.sheet_row == null) return;
        var cols = hit[(l.tab === "operators_owners" ? "oo" : "tracker") + "|" + p.pid + "|" + l.sheet_row];
        if (!cols) return;
        var mine = (l.value_cols || []).concat(l.ref_col ? [l.ref_col] : [], l.current_status !== undefined ? ["Status"] : [],
                                               l.current_route_accuracy !== undefined ? ["RouteAccuracy"] : []);
        var diff = cols.filter(function (c) { return mine.indexOf(c[0]) >= 0; });
        if (diff.length) { l.live = diff; n++; }
      });
    });
    return n;
  }
  function reload(data) {
    var pid = D.pipelines[S.pipe] ? D.pipelines[S.pipe].pid : "";
    D = data;
    prepare();
    if (Store.ready) Store.ready();
    fillFilters(); syncControls();
    S.pin = -1; S.stay = {}; S.line = -1;
    S.pipe = -1;
    D.pipelines.forEach(function (p, i) { if (p.pid === pid) S.pipe = i; });
    renderScope();
    refilter(true);
  }

  // ---- routing: #/P0736 plus an optional ?query with the filters that differ from the defaults ----
  var ROUTING = false;
  var QK = {decision: "d", kind: "k", tier: "t", class_out: "c", dir: "dir", column: "col", q: "q", row: "row",
            contested: "cont", owners: "owners", landed: "landed", country: "cty", fuel: "fuel", by: "by", drift: "drift"};
  function routeHash() {
    var p = D.pipelines[S.pipe], d = defaults(), q = [];
    Object.keys(QK).forEach(function (f) {
      var v = FS[f];
      if (Array.isArray(v)) {
        if (v.join("|") === d[f].join("|")) return;      // the default (gas only for fuel)
        v = v.length ? v.join("|") : "all";               // "all" = every box ticked
      }
      else if (v === d[f]) return;
      if (typeof v === "boolean") v = "1";
      else if (f === "decision" && v === "") v = "any";
      q.push(QK[f] + "=" + encodeURIComponent(v));
    });
    return "#/" + (p ? encodeURIComponent(p.pid) : "") + (q.length ? "?" + q.join("&") : "");
  }
  var NAV = window.GasNav || null;
  function curHash() { return NAV ? NAV.hash : (location.hash || ""); }
  function writeRoute(replace) {
    if (ROUTING || !D) return;
    var h = routeHash();
    if (h === curHash()) return;
    if (NAV) return NAV.write(h, replace);
    try { history[replace ? "replaceState" : "pushState"](null, "", h); } catch (e) { /* file:// or blocked */ }
  }
  function applyRoute() {
    ROUTING = true;
    try {
      var m = /^#\/([^?]*)(?:\?(.*))?$/.exec(curHash()), pid = "";
      FS = defaults();
      if (m) {
        pid = decodeURIComponent(m[1]);
        (m[2] || "").split("&").forEach(function (kv) {
          var i = kv.indexOf("="); if (i < 1) return;
          var k = kv.slice(0, i), v = decodeURIComponent(kv.slice(i + 1));
          Object.keys(QK).forEach(function (f) {
            if (QK[f] !== k) return;
            FS[f] = Array.isArray(FS[f]) ? (v === "all" ? [] : v.split("|")).filter(function (c) { return c === NO_COUNTRY || (f === "fuel" ? FUELS : countries()).indexOf(c) >= 0; }) :
              typeof FS[f] === "boolean" ? v === "1" : (f === "decision" && v === "any" ? "" : v);
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
    get data() { return D; }, state: S, filters: function () { return FS; }, refilter: refilter, Store: Store, timing: {},
    applyRemote: applyRemote, setLive: setLive, busy: busy, rerender: rerender, reload: reload, applyRoute: applyRoute, writeRoute: writeRoute,
    banner: banner, toast: toast, esc: esc, copyText: copyText, et: et
  };
  function et(iso) { return String(iso || "").replace("T", " ").slice(0, 16) + " ET"; }
  function boot(reviewer, data) {
    D = data; ME = reviewer;
    var tLoaded = performance.now();
    prepare();
    if (Store.ready) Store.ready();
    $("whoami").textContent = reviewer;
    renderScope();
    document.querySelector(".top h1").dataset.tip = "built " + et(D.built) + " · " + D.dirs.length + " staging dir" + (D.dirs.length === 1 ? "" : "s") + ": " + D.dirs.map(dirLabel).join(", ") + " · " + D.scope.commodity + " · " + D.scope.snapshot;
    $("sync").hidden = !Store.caps.refresh;          // shipped hidden: the Google page and a --no-build server cannot refresh
    $("sync").dataset.tip = "pull the live sheet (~1 min), rebuild, and mark lines it already holds";
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

  // ---- tip popover (WCAG 1.4.13: shows on hover and focus, stays while hovered, Esc dismisses) ----
  // for [data-tip] elements only; plain title tooltips are not used (tiny, unthemed, no keyboard access)
  (function () {
    var tip = document.createElement("div"), owner = null, hideT = 0, showT = 0;
    tip.id = "tip"; tip.className = "tip"; tip.setAttribute("role", "tooltip"); tip.hidden = true;
    document.body.appendChild(tip);
    function show(el) {
      clearTimeout(hideT);
      owner = el; tip.innerHTML = '<div class="tip-head"></div>'; tip.firstChild.textContent = el.getAttribute("data-tip");
      var note = el.getAttribute("data-tip-note");
      if (note) { var n = document.createElement("div"); n.className = "tip-note"; n.textContent = "note: " + note; tip.appendChild(n); }
      tip.hidden = false;
      var r = el.getBoundingClientRect(), w = tip.offsetWidth, h = tip.offsetHeight, m = 8;
      var x = Math.min(Math.max(m, r.left), window.innerWidth - w - m);
      var y = r.bottom + 6 + h > window.innerHeight - m ? r.top - 6 - h : r.bottom + 6;
      tip.style.left = x + "px"; tip.style.top = Math.max(m, y) + "px";
    }
    function hide() { clearTimeout(showT); tip.hidden = true; owner = null; }
    function later() { clearTimeout(hideT); hideT = setTimeout(hide, 150); }
    document.addEventListener("mouseover", function (e) {
      var el = e.target.closest && e.target.closest("[data-tip]");
      if (owner && !owner.isConnected) hide();      // its element was re-rendered under the pointer
      if (el) {
        if (el === owner) { clearTimeout(hideT); return; }
        clearTimeout(showT);
        // instant when another tip is already open, else a short native-like delay
        if (owner) show(el); else showT = setTimeout(function () { if (el.isConnected) show(el); }, 300);
      } else {
        clearTimeout(showT);
        if (owner && !tip.contains(e.target)) later(); else if (tip.contains(e.target)) clearTimeout(hideT);
      }
    });
    document.addEventListener("focusin", function (e) {
      var t = e.target.closest && e.target.closest("[data-tip]");
      if (t && e.target.matches(":focus-visible")) show(t);
    });
    document.addEventListener("focusout", function (e) { if (owner && owner.contains(e.target)) hide(); });
    document.addEventListener("keydown", function (e) { if (e.key === "Escape" && !tip.hidden) { hide(); e.stopPropagation(); } }, true);
    document.documentElement.addEventListener("mouseleave", hide);
    document.addEventListener("mousedown", function (e) { if (owner && !tip.contains(e.target) && !owner.contains(e.target)) hide(); });
    window.addEventListener("blur", hide);
    document.addEventListener("scroll", function (e) { if (owner && !tip.contains(e.target)) hide(); }, true);
  })();
  $("card").addEventListener("click", onCardClick);
  $("pipes").addEventListener("click", function (e) {
    var li = e.target.closest("li[data-i]");
    if (li) selectPipe(+li.getAttribute("data-i"));
  });
  $("help-btn").onclick = showHelp;
  $("sync").onclick = refreshBackend;
  // session summary is switched off for now (might come back): set SHOW_SUMMARY = true
  var SHOW_SUMMARY = false;
  $("summary-btn").hidden = !SHOW_SUMMARY;
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
    .catch(function (e) { banner("could not load the dataset: " + e.message); });
})();
