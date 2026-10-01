/* Local stand-in for the deployed Apps Script web app: serves the SAME bundled page
   (review_app/gas/index.html) and runs the SAME server code (review_app/gas/Code.gs) under the
   fakes in stubs.js. For developing and testing the Google version without touching Google.

     python review_app/publish.py --no-pull            # writes work/review_publish (the fake Drive folder)
     node review_app/gas_dev/dev_server.js              # http://127.0.0.1:8767/?user=you@globalenergymonitor.org

     [--data work/review_publish] [--store work/review_gas_dev_store.json] [--fresh] [--port 8767]
     [--delay 150] [--no-bundle] [--page FILE]

   ?user=<email> stands in for the Google login (open two tabs with two users to see the
   concurrency behaviour). The fake decision store persists in --store (gitignored work/);
   --fresh starts it empty. GET /store shows its rows as JSON; POST /expire-cache empties the fake
   script cache (a republish then shows up at once, not after a minute). Decisions made here go NOWHERE
   else: not to Google, not to the staging dirs. Loopback only. */
"use strict";
const http = require("http");
const fs = require("fs");
const path = require("path");
const cp = require("child_process");
const stubs = require("./stubs.js");

const ROOT = path.join(__dirname, "..", "..");
function arg(name, dflt) { const i = process.argv.indexOf("--" + name); return i < 0 ? dflt : process.argv[i + 1]; }
function flag(name) { return process.argv.indexOf("--" + name) >= 0; }
const DATA = path.resolve(arg("data", path.join(ROOT, "work", "review_publish")));
const STORE = path.resolve(arg("store", path.join(ROOT, "work", "review_gas_dev_store.json")));
const PORT = Number(arg("port", "8767"));
const DELAY = Number(arg("delay", "0"));
const PAGE = arg("page", path.join(__dirname, "..", "gas", "index.html"));
const HOST = "127.0.0.1";

if (!flag("no-bundle")) {
  const r = cp.spawnSync("python3", [path.join(ROOT, "review_app", "bundle.py")], {stdio: "inherit"});
  if (r.status !== 0) process.exit(r.status || 1);
}
if (!fs.existsSync(path.join(DATA, "scopes.json"))) {
  console.error("no scopes.json in " + DATA + ": run python review_app/publish.py --no-pull first");
  process.exit(1);
}
let sheets = {};
if (!flag("fresh") && fs.existsSync(STORE)) sheets = JSON.parse(fs.readFileSync(STORE, "utf8"));
const world = stubs.makeWorld(DATA, {sheets: sheets});
function persist() { fs.mkdirSync(path.dirname(STORE), {recursive: true}); fs.writeFileSync(STORE, JSON.stringify(world.sheets)); }

// what the page sees as google.script.*: run (calls POST /call), history and url (the real page
// is an iframe whose route lives in the top frame's URL; here the page IS the top frame)
const SHIM = "<script>\n(" + function () {
  var qs = new URLSearchParams(location.search), user = qs.get("user") || "dev@globalenergymonitor.org";
  function runner(ok, fail) {
    return new Proxy({}, {get: function (_, name) {
      if (name === "withSuccessHandler") return function (f) { return runner(f, fail); };
      if (name === "withFailureHandler") return function (f) { return runner(ok, f); };
      return function () {
        var args = Array.prototype.slice.call(arguments);
        fetch("/call", {method: "POST", headers: {"Content-Type": "application/json", "X-Dev-User": user},
                        body: JSON.stringify({fn: name, args: args})})
          .then(function (r) { return r.json(); })
          .then(function (b) { if (b.threw) { if (fail) fail(new Error(b.threw)); } else if (ok) ok(b.value); },
                function (e) { if (fail) fail(e); });
      };
    }});
  }
  function loc() {
    var p = {}, ps = {};
    new URLSearchParams(location.search).forEach(function (v, k) { if (k === "user") return; p[k] = v; (ps[k] = ps[k] || []).push(v); });
    return {hash: location.hash.replace(/^#/, ""), parameter: p, parameters: ps};
  }
  function url(params, hash) {
    var q = new URLSearchParams();
    if (qs.get("user")) q.set("user", qs.get("user"));
    Object.keys(params || {}).forEach(function (k) { q.set(k, params[k]); });
    var s = q.toString();
    return location.pathname + (s ? "?" + s : "") + (hash ? "#" + hash : "");
  }
  var onChange = null;
  window.addEventListener("popstate", function (e) { if (onChange) onChange({state: e.state, location: loc()}); });
  window.google = {script: {
    run: runner(null, null),
    history: {
      push: function (state, params, hash) { history.pushState(state, "", url(params, hash)); },
      replace: function (state, params, hash) { history.replaceState(state, "", url(params, hash)); },
      setChangeHandler: function (f) { onChange = f; }
    },
    url: {getLocation: function (cb) { cb(loc()); }}
  }};
}.toString() + ")();\n</script>\n";

function send(res, code, type, body) {
  res.writeHead(code, {"Content-Type": type, "Cache-Control": "no-store", "X-Content-Type-Options": "nosniff"});
  res.end(body);
}
const server = http.createServer(function (req, res) {
  const host = String(req.headers.host || "").split(":")[0];
  if (host !== "127.0.0.1" && host !== "localhost") return send(res, 403, "text/plain", "loopback only");
  const u = new URL(req.url, "http://" + HOST);
  if (req.method === "GET" && u.pathname === "/") {
    const html = fs.readFileSync(PAGE, "utf8");
    return send(res, 200, "text/html; charset=utf-8", html.replace("<script>", function () { return SHIM + "<script>"; }));
  }
  if (req.method === "GET" && u.pathname === "/store") return send(res, 200, "application/json", JSON.stringify((world.sheets.log || {rows: []}).rows));
  if (req.method === "POST" && u.pathname === "/expire-cache") {      // stands in for the script cache's minute passing
    world.cache.clear();
    return send(res, 200, "application/json", "{}");
  }
  if (req.method === "POST" && u.pathname === "/call") {
    let body = "";
    req.on("data", function (c) { body += c; if (body.length > 20e6) req.destroy(); });
    req.on("end", function () {
      let out;
      try {
        const b = JSON.parse(body);
        out = {value: stubs.callGas(world, String(req.headers["x-dev-user"] || ""), b.fn, b.args)};
        if (b.fn === "decide" || b.fn === "recordItems") persist();
      } catch (e) { out = {threw: String(e && e.message || e)}; }
      setTimeout(function () { send(res, 200, "application/json", JSON.stringify(out)); }, DELAY);
    });
    return;
  }
  send(res, 404, "text/plain", "not found");
});
server.listen(PORT, HOST, function () {
  console.error("review app (Google version, local stand-in): http://" + HOST + ":" + server.address().port + "/?user=you@globalenergymonitor.org");
  console.error("  data folder: " + DATA + "\n  fake store:  " + STORE + (flag("fresh") ? " (started empty)" : ""));
});
