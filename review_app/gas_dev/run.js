/* Run a scripted sequence of web-app calls against Code.gs under the fakes (stubs.js).
   stdin:  {"dataDir": "<published mirror>", "now": <ms, optional>, "sheets": {...optional},
            "ops": [{"user": "a@x.org", "fn": "decide", "args": [...]}, {"tick": <ms to advance the clock>}, ...]}
   stdout: {"results": [<return value> | {"threw": "<message>"}], "sheets": {...}, "stats": {...}}
   Used by tests/test_review_gas.py. */
"use strict";
const stubs = require("./stubs.js");
let input = "";
process.stdin.setEncoding("utf8");
process.stdin.on("data", function (c) { input += c; });
process.stdin.on("end", function () {
  const job = JSON.parse(input);
  const world = stubs.makeWorld(job.dataDir, {now: job.now == null ? null : job.now, sheets: job.sheets, props: job.props});
  const results = job.ops.map(function (op) {
    if (op.tick != null) { world.now = (world.now || 0) + op.tick; return null; }
    if (op.clearCache) { world.cache.clear(); return null; }
    try { return stubs.callGas(world, op.user, op.fn, op.args); }
    catch (e) { return {threw: String(e && e.message || e)}; }
  });
  process.stdout.write(JSON.stringify({results: results, sheets: world.sheets, stats: world.stats}));
});
