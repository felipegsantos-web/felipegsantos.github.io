// axe over every page of a built site (both languages), in both themes and at two viewport widths.
// Also opens the mobile menu and the list view of the publications page. Fails on any WCAG 2.2 AA
// violation, and on two things axe leaves to best practice: exactly one h1 per page with no skipped
// heading level, and a visible focus indicator on every focusable element.
// Usage: node axe.mjs ../../_site
import http from "node:http";
import fs from "node:fs";
import path from "node:path";
import { chromium } from "playwright";
import AxeBuilder from "@axe-core/playwright";

const root = path.resolve(process.argv[2] || "../../_site");
const TAGS = ["wcag2a", "wcag2aa", "wcag21a", "wcag21aa", "wcag22aa"];
const MIME = { ".html": "text/html; charset=utf-8", ".css": "text/css", ".js": "text/javascript",
  ".woff2": "font/woff2", ".svg": "image/svg+xml", ".png": "image/png", ".jpg": "image/jpeg",
  ".jpeg": "image/jpeg", ".webp": "image/webp", ".pdf": "application/pdf", ".xml": "application/xml",
  ".txt": "text/plain; charset=utf-8" };

function walk(dir) {
  return fs.readdirSync(dir, { withFileTypes: true }).flatMap((e) =>
    e.isDirectory() ? walk(path.join(dir, e.name)) : [path.join(dir, e.name)]);
}
const pages = walk(root).filter((f) => f.endsWith(".html")).map((f) => {
  const rel = "/" + path.relative(root, f).split(path.sep).join("/");
  return rel.replace(/index\.html$/, "");
}).sort();

const server = http.createServer((req, res) => {
  let p = decodeURIComponent(new URL(req.url, "http://x").pathname);
  let file = path.join(root, p);
  if (!file.startsWith(root)) { res.writeHead(403).end(); return; }
  if (fs.existsSync(file) && fs.statSync(file).isDirectory()) file = path.join(file, "index.html");
  if (!fs.existsSync(file)) {
    res.writeHead(404, { "Content-Type": MIME[".html"] });
    res.end(fs.existsSync(path.join(root, "404.html")) ? fs.readFileSync(path.join(root, "404.html")) : "not found");
    return;
  }
  res.writeHead(200, { "Content-Type": MIME[path.extname(file)] || "application/octet-stream" });
  fs.createReadStream(file).pipe(res);
});
await new Promise((r) => server.listen(0, "127.0.0.1", r));
const base = `http://127.0.0.1:${server.address().port}`;

// Visible headings, in order: one h1, and a heading may be at most one level deeper than the previous.
async function headingProblems(page) {
  return page.evaluate(() => {
    const visible = (el) => !!(el.offsetWidth || el.offsetHeight || el.getClientRects().length) || el.matches(".sr-only");
    const hs = [...document.querySelectorAll("h1,h2,h3,h4,h5,h6")].filter((h) => !h.closest("[hidden]") && visible(h));
    const out = [];
    const h1 = hs.filter((h) => h.tagName === "H1").length;
    if (h1 !== 1) out.push(`${h1} h1 elements`);
    let prev = 0;
    for (const h of hs) {
      const lvl = Number(h.tagName[1]);
      if (prev && lvl > prev + 1) out.push(`h${prev} followed by h${lvl}: "${h.textContent.trim().slice(0, 40)}"`);
      prev = lvl;
    }
    return out;
  });
}

// Tab through the page: every element that takes focus needs a drawn outline (or box-shadow) that no ancestor clips.
async function focusProblems(page) {
  const out = [];
  const seen = new Set();
  await page.evaluate(() => { document.activeElement && document.activeElement.blur(); window.scrollTo(0, 0); });
  for (let i = 0; i < 300; i++) {
    await page.keyboard.press("Tab");
    const r = await page.evaluate(async () => {
      await new Promise((done) => requestAnimationFrame(() => requestAnimationFrame(done))); // let a transition on the outline finish
      const el = document.activeElement;
      if (!el || el === document.body) return { end: true };
      const id = el.tagName + "|" + (el.getAttribute("href") || el.className || el.textContent.trim().slice(0, 30));
      const cs = getComputedStyle(el);
      const drawn = (cs.outlineStyle !== "none" && parseFloat(cs.outlineWidth) > 0) || cs.boxShadow !== "none";
      if (!drawn) return { id, problem: `no focus indicator on ${id}` };
      const box = el.getBoundingClientRect();
      const ring = (parseFloat(cs.outlineWidth) || 0) + (parseFloat(cs.outlineOffset) || 0);
      for (let p = el.parentElement; p && p !== document.documentElement; p = p.parentElement) {
        const ps = getComputedStyle(p);
        if (ps.overflowX === "visible" && ps.overflowY === "visible") continue;
        const pb = p.getBoundingClientRect();
        if (box.left - ring < pb.left - 0.5 || box.right + ring > pb.right + 0.5 || box.top - ring < pb.top - 0.5 || box.bottom + ring > pb.bottom + 0.5)
          return { id, problem: `focus ring of ${id} is clipped by ${p.tagName.toLowerCase()}.${p.className}` };
      }
      return { id };
    });
    if (r.end || seen.has(r.id)) break;
    seen.add(r.id);
    if (r.problem) out.push(r.problem);
  }
  return out;
}

const browser = await chromium.launch(process.env.CHROME_PATH ? { executablePath: process.env.CHROME_PATH, args: ["--no-sandbox"] } : {});
let violations = 0, runs = 0;

for (const theme of ["light", "dark"]) {
  for (const width of [1280, 375]) {
    const ctx = await browser.newContext({ viewport: { width, height: 900 }, reducedMotion: "reduce" });
    await ctx.addInitScript((t) => { try { localStorage.setItem("site-theme", t); } catch (e) {} }, theme);
    const page = await ctx.newPage();
    // the root page only redirects to /en/ or /es/ with JavaScript: keep it on the page
    await page.route("**/router.js", (route) => route.abort());
    for (const url of pages) {
      const target = url;
      const states = [["", null]];
      if (url.match(/^\/(en\/publications|es\/publicaciones)\/$/)) states.push([" (list view)", async () => { await page.click('[data-view="list"]'); }]);
      if (width === 375 && url.match(/^\/(en|es)\/$/)) states.push([" (mobile menu open)", async () => { await page.click(".mobile-menu-btn"); }]);
      for (const [label, setup] of states) {
        await page.goto(base + target, { waitUntil: "networkidle" });
        if (setup) await setup();
        const results = await new AxeBuilder({ page }).withTags(TAGS).analyze();
        runs++;
        for (const msg of await headingProblems(page)) { violations++; console.log(`\n[${theme} ${width}px] ${url}${label}: heading structure: ${msg}`); }
        if (!setup) for (const msg of await focusProblems(page)) { violations++; console.log(`\n[${theme} ${width}px] ${url}${label}: focus: ${msg}`); }
        for (const v of results.violations) {
          violations += v.nodes.length;
          console.log(`\n[${theme} ${width}px] ${url}${label}: ${v.id} (${v.impact}) ${v.help}`);
          for (const n of v.nodes.slice(0, 5)) console.log(`    ${n.target.join(" ")}\n    ${(n.failureSummary || "").split("\n").slice(0, 3).join(" | ")}`);
        }
      }
    }
    await ctx.close();
  }
}
await browser.close();
server.close();
console.log(`\naxe: ${runs} runs over ${pages.length} pages, ${violations} violation(s)`);
process.exit(violations ? 1 : 0);
