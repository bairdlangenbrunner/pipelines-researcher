/* Fakes for the Apps Script services review_app/gas/Code.gs uses, so the SAME file runs under
   node: in tests (run.js, driven by tests/test_review_gas.py) and in the local dev server
   (dev_server.js). Nothing here talks to Google.

   A real Apps Script execution starts with fresh globals, so every call gets a NEW vm context
   (callGas); what outlives a call is `world`: the fake spreadsheet, the fake script cache, the
   Drive folder (a local directory) and the script properties.

   Kept deliberately strict where the real service is strict (a cache value over 100 KB throws,
   a range outside the sheet throws, setValues wants the exact shape), so the code is not only
   tested against a pushover. */
"use strict";
const fs = require("fs");
const path = require("path");
const vm = require("vm");
const crypto = require("crypto");

const CODE = path.join(__dirname, "..", "gas", "Code.gs");
const PUBLIC = ["whoami", "getPart", "getDecisions", "decide", "recordItems", "spike"];

function makeWorld(dataDir, opts) {
  opts = opts || {};
  return {
    dataDir: dataDir,
    sheets: opts.sheets || {},          // tab name -> {rows: [[text]], maxRows, maxCols, frozen}
    cache: new Map(),                   // key -> {v, until}
    props: Object.assign({DATA_FOLDER_ID: "dev-folder", STORE_SHEET_ID: "dev-store"}, opts.props || {}),
    now: opts.now || null,              // fixed clock (ms) for tests
    effective: opts.effective || "deployer@example.org",
    stats: {driveReads: 0, appends: 0}
  };
}

function etIso(d) {                      // yyyy-MM-dd'T'HH:mm:ssXXX in America/New_York
  const parts = {};
  new Intl.DateTimeFormat("en-CA", {timeZone: "America/New_York", hourCycle: "h23", year: "numeric", month: "2-digit",
    day: "2-digit", hour: "2-digit", minute: "2-digit", second: "2-digit"}).formatToParts(d)
    .forEach(function (p) { parts[p.type] = p.value; });
  const asUtc = Date.UTC(+parts.year, +parts.month - 1, +parts.day, +parts.hour, +parts.minute, +parts.second);
  const off = Math.round((asUtc - Math.floor(d.getTime() / 1000) * 1000) / 60000), a = Math.abs(off);
  return parts.year + "-" + parts.month + "-" + parts.day + "T" + parts.hour + ":" + parts.minute + ":" + parts.second +
    (off < 0 ? "-" : "+") + String(Math.floor(a / 60)).padStart(2, "0") + ":" + String(a % 60).padStart(2, "0");
}

function fakeSheet(world, name) {
  const sh = world.sheets[name];
  function lastRow() {
    for (let i = sh.rows.length - 1; i >= 0; i--) if (sh.rows[i].some(function (c) { return c !== ""; })) return i + 1;
    return 0;
  }
  function range(r, c, nr, nc) {
    nr = nr == null ? 1 : nr; nc = nc == null ? 1 : nc;
    if (r < 1 || c < 1 || nr < 1 || nc < 1 || r + nr - 1 > sh.maxRows || c + nc - 1 > sh.maxCols)
      throw new Error("The coordinates of the range are outside the dimensions of the sheet.");
    const api = {
      setNumberFormat: function () { return api; }, setFontFamily: function () { return api; },
      setFontSize: function () { return api; }, setFontWeight: function () { return api; },
      setValues: function (vals) {
        if (!Array.isArray(vals) || vals.length !== nr || vals.some(function (row) { return !Array.isArray(row) || row.length !== nc; }))
          throw new Error("The number of rows or columns in the data does not match the range.");
        for (let i = 0; i < nr; i++) {
          while (sh.rows.length < r + i) sh.rows.push([]);
          const row = sh.rows[r + i - 1];
          while (row.length < sh.maxCols) row.push("");
          for (let j = 0; j < nc; j++) {
            const v = vals[i][j] == null ? "" : String(vals[i][j]);       // the range is formatted as text
            if (v.length > 50000) throw new Error("Your input contains more than the maximum of 50000 characters in a single cell.");
            row[c + j - 1] = v;
          }
        }
        return api;
      },
      getValues: function () {
        const out = [];
        for (let i = 0; i < nr; i++) {
          const row = sh.rows[r + i - 1] || [], o = [];
          for (let j = 0; j < nc; j++) o.push(row[c + j - 1] == null ? "" : row[c + j - 1]);
          out.push(o);
        }
        return out;
      }
    };
    return api;
  }
  return {
    getLastRow: lastRow,
    getMaxRows: function () { return sh.maxRows; },
    getMaxColumns: function () { return sh.maxCols; },
    deleteColumns: function (start, n) { sh.maxCols -= n; sh.rows.forEach(function (row) { row.splice(start - 1, n); }); },
    insertRowsAfter: function (after, n) { if (after !== sh.maxRows) throw new Error("stub: insertRowsAfter only at the end"); sh.maxRows += n; },
    getRange: range,
    setFrozenRows: function (n) { sh.frozen = n; }
  };
}

function services(world, user) {
  const clock = function () { return world.now != null ? new Date(world.now) : new Date(); };
  return {
    SpreadsheetApp: {
      openById: function (id) {
        if (id !== world.props.STORE_SHEET_ID) throw new Error("stub: Code.gs opened a spreadsheet other than the store: " + id);
        return {
          getSheetByName: function (n) { return world.sheets[n] ? fakeSheet(world, n) : null; },
          insertSheet: function (n) {
            if (world.sheets[n]) throw new Error("A sheet with the name \"" + n + "\" already exists.");
            world.sheets[n] = {rows: [], maxRows: 1000, maxCols: 26, frozen: 0};
            return fakeSheet(world, n);
          }
        };
      },
      flush: function () { world.stats.appends++; }
    },
    DriveApp: {
      getFolderById: function (id) {
        if (id !== world.props.DATA_FOLDER_ID) throw new Error("stub: Code.gs opened a folder other than the data folder: " + id);
        return {
          getFilesByName: function (name) {
            const p = path.join(world.dataDir, path.basename(name));
            let left = path.basename(name) === name && fs.existsSync(p) ? 1 : 0;
            return {
              hasNext: function () { return left > 0; },
              next: function () {
                left--;
                return {
                  isTrashed: function () { return false; },
                  getLastUpdated: function () { return fs.statSync(p).mtime; },
                  getBlob: function () {
                    world.stats.driveReads++;
                    const buf = fs.readFileSync(p);
                    return {
                      getDataAsString: function () { return buf.toString("utf8"); },
                      getBytes: function () { return Array.from(new Int8Array(buf.buffer, buf.byteOffset, buf.length)); }
                    };
                  }
                };
              }
            };
          }
        };
      }
    },
    CacheService: {
      getScriptCache: function () {
        function get(k) {
          const e = world.cache.get(k);
          if (!e) return null;
          if (e.until < clock().getTime()) { world.cache.delete(k); return null; }
          return e.v;
        }
        return {
          get: get,
          getAll: function (keys) { const o = {}; keys.forEach(function (k) { const v = get(k); if (v != null) o[k] = v; }); return o; },
          putAll: function (m, seconds) {
            Object.keys(m).forEach(function (k) {
              if (Buffer.byteLength(String(m[k]), "utf8") > 100 * 1024) throw new Error("Argument too large: value");
            });
            Object.keys(m).forEach(function (k) { world.cache.set(k, {v: String(m[k]), until: clock().getTime() + seconds * 1000}); });
          }
        };
      }
    },
    LockService: {getScriptLock: function () { return {waitLock: function () {}, releaseLock: function () {}}; }},
    Session: {
      getActiveUser: function () { return {getEmail: function () { return user || ""; }}; },
      getEffectiveUser: function () { return {getEmail: function () { return world.effective; }}; }
    },
    PropertiesService: {getScriptProperties: function () { return {getProperty: function (n) { return world.props[n] || null; }}; }},
    Utilities: {
      formatDate: function (d, tz, fmt) {
        if (tz !== "America/New_York" || fmt !== "yyyy-MM-dd'T'HH:mm:ssXXX") throw new Error("stub: formatDate only knows the ET ISO format");
        return etIso(world.now != null ? new Date(world.now) : d);
      },
      getUuid: function () { return crypto.randomUUID(); },
      base64Encode: function (bytes) { return Buffer.from(Int8Array.from(bytes).buffer).toString("base64"); }
    },
    HtmlService: {
      createHtmlOutputFromFile: function (n) { const o = {file: n, setTitle: function () { return o; }, addMetaTag: function () { return o; }}; return o; },
      createHtmlOutput: function (h) { const o = {html: h, setTitle: function () { return o; }, addMetaTag: function () { return o; }}; return o; }
    }
  };
}

let SCRIPT = null, SCRIPT_MTIME = 0;
/** One Apps Script execution: fresh globals, the world's persistent services, JSON in and out
 *  (google.script.run serialises both ways). A thrown error propagates (the page's failure handler). */
function callGas(world, user, fn, args) {
  if (PUBLIC.indexOf(fn) < 0) throw new Error("not a function the page may call: " + fn);
  const mtime = fs.statSync(CODE).mtimeMs;
  if (!SCRIPT || mtime !== SCRIPT_MTIME) { SCRIPT = new vm.Script(fs.readFileSync(CODE, "utf8"), {filename: "Code.gs"}); SCRIPT_MTIME = mtime; }
  const ctx = vm.createContext(Object.assign({__args: JSON.stringify(args || [])}, services(world, user)));
  SCRIPT.runInContext(ctx);
  const out = vm.runInContext("JSON.stringify(" + fn + ".apply(null, JSON.parse(__args)))", ctx);
  return out === undefined ? null : JSON.parse(out);
}

module.exports = {makeWorld: makeWorld, callGas: callGas, PUBLIC: PUBLIC, etIso: etIso};
