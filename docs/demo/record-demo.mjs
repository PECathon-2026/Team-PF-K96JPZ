// Records ONLY a fresh headless browser visiting the public app, never the desktop.
import { spawn } from "node:child_process";
import { readFile, writeFile, mkdir, mkdtemp } from "node:fs/promises";
import { tmpdir } from "node:os";
import path from "node:path";
import { performance } from "node:perf_hooks";

const plan = JSON.parse(await readFile(new URL("./demo-plan.json", import.meta.url), "utf8"));
const work = process.env.DEMO_WORK || path.join(tmpdir(), "tsukuyomi-demo-recording");
const output = process.env.DEMO_OUTPUT;
if (!output) throw new Error("Set DEMO_OUTPUT to the authorized output folder.");
const ffmpeg = process.env.FFMPEG_PATH || path.join(tmpdir(), "tsukuyomi-demo-tools/node_modules/ffmpeg-static/ffmpeg.exe");
const framesDir = path.join(work, "frames-" + Date.now());
await mkdir(framesDir, { recursive: true });
await mkdir(output, { recursive: true });
const pause = ms => new Promise(resolve => setTimeout(resolve, ms));
const profile = await mkdtemp(path.join(tmpdir(), "tsukuyomi-demo-browser-"));
const browser = spawn(process.env.EDGE_PATH || "C:/Program Files (x86)/Microsoft/Edge/Application/msedge.exe", [
  "--headless=new", "--disable-gpu", "--no-first-run", "--no-default-browser-check",
  "--autoplay-policy=no-user-gesture-required", "--remote-debugging-port=9334", `--user-data-dir=${profile}`, "about:blank",
], { windowsHide: true, stdio: "ignore" });
let socket, recording = false, started = 0;
let snapshotTimer, snapshotBusy = false, snapshotFailure;
const frames = [], writes = [], pending = new Map();
let id = 0;
function send(method, params = {}) {
  return new Promise((resolve, reject) => {
    const key = ++id;
    pending.set(key, { resolve, reject });
    socket.send(JSON.stringify({ id: key, method, params }));
  });
}
async function evaluate(expression) {
  const data = await send("Runtime.evaluate", { expression, returnByValue: true, awaitPromise: true });
  if (data.exceptionDetails) throw new Error(JSON.stringify(data.exceptionDetails));
  return data.result.value;
}
function saveFrame(data, time) {
  if (!recording || time >= 180 || (frames.length && time - frames.at(-1).time < 1 / 12)) return;
  const file = path.join(framesDir, `frame-${String(frames.length).padStart(5, "0")}.jpg`);
  frames.push({ file, time });
  writes.push(writeFile(file, Buffer.from(data, "base64")));
}
async function snapshot() {
  if (!recording || snapshotBusy) return;
  snapshotBusy = true;
  try {
    const data = await send("Page.captureScreenshot", { format: "jpeg", quality: 80, captureBeyondViewport: false });
    saveFrame(data.data, (performance.now() - started) / 1000);
  } catch (error) {
    // During a full-page navigation Chrome can briefly detach the old document.
    // The next periodic capture records the loaded page instead.
    if (!/Not attached to an active page|Inspected target navigated/i.test(String(error))) throw error;
  } finally { snapshotBusy = false; }
}
async function waitFor(expression, label, timeout = 30000) {
  const until = performance.now() + timeout;
  while (performance.now() < until) {
    if (await evaluate(`Boolean(${expression})`)) return;
    await pause(200);
  }
  throw new Error(`${label}: ${await evaluate("document.body.innerText.slice(-1200)")}`);
}
async function go(route) {
  await send("Page.navigate", { url: plan.url + route });
  await waitFor(`document.readyState === 'complete' && !!document.querySelector('.watch-theme-toggle:not(:disabled)')`, "Page hydration");
  await evaluate("document.fonts.ready.then(()=>true)");
}
async function scroll(selector, block = "start") {
  await evaluate(`document.querySelector(${JSON.stringify(selector)})?.scrollIntoView({block:${JSON.stringify(block)},behavior:'instant'})`);
  await pause(180);
  // Headless screencasting may omit compositor-only scroll frames. Explicit
  // screenshots preserve the actual current view even when the page is idle.
  await snapshot();
}
let cursor = { x: 1100, y: 600 };
async function move(x, y, steps = 10) {
  const from = cursor;
  for (let i = 1; i <= steps; i++) {
    await send("Input.dispatchMouseEvent", { type: "mouseMoved", x: from.x + (x - from.x) * i / steps, y: from.y + (y - from.y) * i / steps, pointerType: "mouse", buttons: 0 });
    await pause(16);
  }
  cursor = { x, y };
}
async function click(selector) {
  await evaluate(`document.querySelector(${JSON.stringify(selector)})?.scrollIntoView({block:'nearest',behavior:'instant'})`);
  const point = await evaluate(`(()=>{const e=document.querySelector(${JSON.stringify(selector)});if(!e)throw new Error('Missing control: '+${JSON.stringify(selector)});const r=e.getBoundingClientRect();return{x:r.x+r.width/2,y:r.y+r.height/2};})()`);
  await move(point.x, point.y);
  await send("Input.dispatchMouseEvent", { type: "mousePressed", button: "left", clickCount: 1, ...point });
  await send("Input.dispatchMouseEvent", { type: "mouseReleased", button: "left", clickCount: 1, ...point });
  await pause(180);
}
async function at(second, task) {
  const remaining = second * 1000 - (performance.now() - started);
  if (remaining > 0) await pause(remaining);
  const late = (performance.now() - started) / 1000 - second;
  if (late > 5) throw new Error(`Demo action ${second}s missed by ${late.toFixed(1)}s; retry instead of publishing a mistimed recording.`);
  if (task) await task();
}
async function range(value) {
  const rect = await evaluate(`(()=>{const r=document.querySelector('.lens-compare-control input').getBoundingClientRect();return{x:r.x,y:r.y,w:r.width,h:r.height};})()`);
  const point = { x: rect.x + 8 + (rect.w - 16) * value / 100, y: rect.y + rect.h / 2 };
  await move(point.x, point.y, 16);
  await send("Input.dispatchMouseEvent", { type: "mousePressed", button: "left", clickCount: 1, ...point });
  await send("Input.dispatchMouseEvent", { type: "mouseReleased", button: "left", clickCount: 1, ...point });
}
async function runEncoder(args, label) {
  console.log(label);
  await new Promise((resolve, reject) => {
    const child = spawn(ffmpeg, ["-hide_banner", "-loglevel", "error", "-y", ...args], { cwd: work, windowsHide: true, stdio: ["ignore", "ignore", "pipe"] });
    let errors = "";
    child.stderr.on("data", data => errors += data.toString());
    child.on("error", reject);
    child.on("exit", code => code === 0 ? resolve() : reject(new Error(`${label}: ${errors}`)));
  });
}

try {
  let targets;
  for (let i = 0; i < 60; i++) {
    try { targets = await (await fetch("http://localhost:9334/json")).json(); if (targets.length) break; } catch {}
    await pause(200);
  }
  socket = new WebSocket(targets.find(target => target.type === "page").webSocketDebuggerUrl);
  await new Promise((resolve, reject) => { socket.onopen = resolve; socket.onerror = reject; });
  socket.onmessage = event => {
    const message = JSON.parse(event.data);
    if (message.id) {
      const handler = pending.get(message.id);
      pending.delete(message.id);
      if (handler) message.error ? handler.reject(new Error(JSON.stringify(message.error))) : handler.resolve(message.result);
    } else if (message.method === "Page.screencastFrame") {
      const time = (performance.now() - started) / 1000;
      saveFrame(message.params.data, time);
      void send("Page.screencastFrameAck", { sessionId: message.params.sessionId }).catch(() => {});
    }
  };
  await send("Page.enable");
  await send("Page.bringToFront");
  await send("Emulation.setFocusEmulationEnabled", { enabled: true });
  await send("Emulation.setDeviceMetricsOverride", { width: 1440, height: 720, deviceScaleFactor: 1, mobile: false });
  await send("Page.addScriptToEvaluateOnNewDocument", { source: `addEventListener('DOMContentLoaded',()=>{const dot=document.createElement('div');dot.style.cssText='position:fixed;width:18px;height:18px;border:2px solid #efbd73;border-radius:50%;pointer-events:none;z-index:2147483647;transform:translate(-50%,-50%);box-shadow:0 0 0 3px #0007;display:none';document.documentElement.append(dot);addEventListener('mousemove',e=>{dot.style.display='block';dot.style.left=e.clientX+'px';dot.style.top=e.clientY+'px'});});` });

  console.log("Preflight: warming the API, calendar, city search and local AI model.");
  await go("/");
  await waitFor(`document.querySelectorAll('.leaflet-marker-icon').length === 6 && !!document.querySelector('.scroll-event h3 a')`, "Map/calendar data", 90000);
  const city = await evaluate(`fetch('/api/cities?query=Delhi').then(r=>r.json())`);
  if (!city.places?.some(place => place.region.includes("India"))) throw new Error("Delhi provider preflight failed");
  await go("/spirit-lens");
  await click(".lens-demo");
  await waitFor(`!!document.querySelector('.lens-restore:not(:disabled)')`, "Demo image");
  await click(".lens-restore");
  await waitFor(`!!document.querySelector('.lens-measurements') || !!document.querySelector('.lens-error')`, "AI model warmup", 150000);
  if (await evaluate(`!!document.querySelector('.lens-error')`)) throw new Error(await evaluate(`document.querySelector('.lens-error').innerText`));
  console.log("Preflight AI:", await evaluate(`document.querySelector('.lens-status').innerText`));
  await go("/analysis");
  await evaluate(`Array.from(document.querySelectorAll('button')).find(b=>b.textContent.includes('Load synthetic')).click()`);
  await evaluate(`document.querySelector('form').requestSubmit()`);
  await waitFor(`!!document.querySelector('.signal-chart')`, "Signal example");
  await go("/");
  await waitFor(`document.querySelectorAll('.leaflet-marker-icon').length === 6`, "Opening map");
  await evaluate("scrollTo({top:0,behavior:'instant'})");
  await move(1000, 600);

  console.log("Recording: 0:00 / 3:00 — introduction.");
  started = performance.now();
  recording = true;
  await send("Page.startScreencast", { format: "jpeg", quality: 80, maxWidth: 1440, maxHeight: 720, everyNthFrame: 3 });
  await snapshot();
  snapshotTimer = setInterval(() => { void snapshot().catch(error => { snapshotFailure = error; }); }, 750);
  await at(12, async () => {
    const r = await evaluate(`(()=>{const r=document.querySelector('.watch-sidebar nav a[href="#celestial-scroll"]').getBoundingClientRect();return{x:r.x+r.width/2,y:r.y+r.height/2};})()`);
    await move(r.x, r.y); await pause(1200); await move(1100, 600);
  });
  await at(18, async () => { console.log("Recording: 0:18 — Watchtower."); await scroll(".watch-search"); });
  await at(19, async () => {
    await click(".watch-search input");
    for (const character of "Delhi") { await send("Input.insertText", { text: character }); await pause(130); }
    await waitFor(`document.querySelector('.watch-search-results')?.innerText.includes('India')`, "Worldwide city suggestions", 10000);
  });
  await at(24, async () => {
    await evaluate(`Array.from(document.querySelectorAll('.watch-search-results button')).find(b=>b.textContent.includes('India')).click()`);
    await waitFor(`!!document.querySelector('.watch-explorer') && document.querySelector('.watch-toolbar')?.innerText.includes('Delhi')`, "Nearby curated spots", 12000);
    await scroll(".watch-explorer");
  });
  await at(29, () => click(".watch-place-list button"));
  await at(32, async () => { await scroll(".watch-conditions"); await waitFor(`!!document.querySelector('.watch-weather-grid')`, "Night forecast", 10000); });
  await at(43, () => scroll(".watch-conditions"));

  await at(50, async () => { console.log("Recording: 0:50 — Celestial Scroll."); await scroll("#celestial-scroll"); });
  await at(55, async () => { await evaluate(`Array.from(document.querySelectorAll('.scroll-filters button')).find(b=>b.textContent.includes('Moon phase')).click()`); });
  await at(61, async () => {
    await waitFor(`!!document.querySelector('.scroll-event h3 a')`, "Moon phase events");
    await click(".scroll-event h3 a");
    await waitFor(`!!document.querySelector('.event-hero h1')`, "Internal event detail");
  });
  await at(69, () => scroll(".event-hero"));
  await at(75, async () => { await click('.event-breadcrumb a'); await waitFor(`!!document.querySelector('.scroll-calendar')`, "Return to Scroll"); await scroll("#celestial-scroll"); });

  await at(80, async () => { console.log("Recording: 1:20 — Spirit Lens."); await go("/spirit-lens"); await scroll(".lens-workspace"); });
  await at(85, async () => { await click(".lens-demo"); await waitFor(`!!document.querySelector('.lens-restore:not(:disabled)')`, "Synthetic input"); });
  await at(89, async () => { await click(".lens-restore"); await scroll(".lens-workspace"); });
  await at(107, async () => {
    await waitFor(`!!document.querySelector('.lens-measurements') || !!document.querySelector('.lens-error')`, "Recorded restoration", 10000);
    if (await evaluate(`!!document.querySelector('.lens-error')`)) throw new Error(await evaluate(`document.querySelector('.lens-error').innerText`));
    console.log("Recorded AI:", await evaluate(`document.querySelector('.lens-status').innerText`));
    await scroll(".lens-comparison");
  });
  await at(110, () => range(18));
  await at(112, () => range(82));
  await at(114, () => range(50));
  await at(117, () => click('.lens-view-toolbar button[aria-label="Zoom in"]'));
  await at(120, () => click('.lens-view-toolbar button[aria-pressed]'));
  await at(122, () => click('.lens-view-toolbar button[aria-pressed]'));
  await at(124, () => scroll(".lens-measurements"));
  await at(129, async () => {
    // The archive controls are a separate form; showing their actual heading avoids a network-dependent fetch.
    await evaluate(`Array.from(document.querySelectorAll('h2')).find(e=>e.textContent.includes('Borrow a view'))?.scrollIntoView({block:'start',behavior:'instant'})`);
  });

  await at(135, async () => {
    console.log("Recording: 2:15 — Signal Observatory."); await go("/analysis");
    await evaluate(`Array.from(document.querySelectorAll('button')).find(b=>b.textContent.includes('Load synthetic')).click()`);
    await evaluate(`document.querySelector('form').requestSubmit()`);
    await waitFor(`!!document.querySelector('.signal-chart')`, "Signal results");
    await scroll(".signal-chart", "center");
  });
  await at(149, () => scroll(".signal-chart", "center"));
  await at(155, async () => { console.log("Recording: 2:35 — Honor and themes."); await go("/dojo"); await scroll(".bonus-cards", "center"); });
  await at(161, async () => {
    await evaluate("scrollTo({top:0,behavior:'instant'})");
    await evaluate(`(()=>{const s=document.querySelector('select[aria-label="Color palette"]');s.value='akatsuki';s.dispatchEvent(new Event('change',{bubbles:true}));})()`);
  });
  await at(164, () => click(".watch-theme-toggle"));
  await at(168, () => click(".watch-theme-toggle"));
  await at(170, async () => { console.log("Recording: 2:50 — closing."); await go("/"); await evaluate("scrollTo({top:0,behavior:'instant'})"); await move(1150, 580); });
  await at(180);
  recording = false;
  clearInterval(snapshotTimer);
  await send("Page.stopScreencast");
  await Promise.all(writes);
  await writeFile(path.join(framesDir, "timeline.json"), JSON.stringify(frames));
  if (snapshotFailure) throw snapshotFailure;
  console.log(`Captured ${frames.length} actual browser frames.`);
  if (frames.length < 150) throw new Error("Insufficient screencast frames");
  frames[0].time = 0;
  const quote = file => file.replaceAll("\\", "/").replaceAll("'", "'\\''");
  let concat = "ffconcat version 1.0\n";
  for (let i = 0; i < frames.length; i++) {
    const end = frames[i + 1]?.time ?? 180;
    concat += `file '${quote(frames[i].file)}'\nduration ${Math.max(.001, end - frames[i].time).toFixed(6)}\n`;
  }
  concat += `file '${quote(frames.at(-1).file)}'\n`;
  await writeFile(path.join(work, "frames.ffconcat"), concat);

  const speech = JSON.parse((await readFile(path.join(work, "speech.json"), "utf8")).replace(/^\uFEFF/, ""));
  const srtTime = seconds => { const ms = Math.round(seconds * 1000); return `${String(Math.floor(ms / 3600000)).padStart(2,"0")}:${String(Math.floor(ms / 60000) % 60).padStart(2,"0")}:${String(Math.floor(ms / 1000) % 60).padStart(2,"0")},${String(ms % 1000).padStart(3,"0")}`; };
  const assTime = seconds => `${Math.floor(seconds/3600)}:${String(Math.floor(seconds/60)%60).padStart(2,"0")}:${(seconds%60).toFixed(2).padStart(5,"0")}`;
  let srt = "", ass = `[Script Info]\nScriptType: v4.00+\nPlayResX: 1440\nPlayResY: 810\nWrapStyle: 0\n[V4+ Styles]\nFormat: Name, Fontname, Fontsize, PrimaryColour, SecondaryColour, OutlineColour, BackColour, Bold, Italic, Underline, StrikeOut, ScaleX, ScaleY, Spacing, Angle, BorderStyle, Outline, Shadow, Alignment, MarginL, MarginR, MarginV, Encoding\nStyle: Default,Arial,25,&H00F5EEE5,&H00F5EEE5,&H0024100C,&H0024100C,0,0,0,0,100,100,0,0,1,1,0,2,70,70,18,1\n[Events]\nFormat: Layer, Start, End, Style, Name, MarginL, MarginR, MarginV, Effect, Text\n`;
  let offset = 0, count = 0;
  plan.scenes.forEach((scene, index) => {
    const words = scene.text.split(/\s+/);
    for (let start = 0; start < words.length; start += 12) {
      const caption = words.slice(start, start + 12).join(" ");
      const from = offset + start / words.length * speech[index].duration;
      const until = offset + Math.min(start + 12, words.length) / words.length * speech[index].duration;
      srt += `${++count}\n${srtTime(from)} --> ${srtTime(until)}\n${caption}\n\n`;
      ass += `Dialogue: 0,${assTime(from)},${assTime(until)},Default,,0,0,0,,${caption}\n`;
    }
    offset += scene.seconds;
  });
  await writeFile(path.join(work,"captions.ass"), ass);
  const stem = "Tsukuyomi-Watch-3-Minute-Demo";
  await writeFile(path.join(output, stem + ".srt"), srt);
  await writeFile(path.join(output, stem + "-Transcript.txt"), "GENERATED ENGLISH NARRATION · 3-MINUTE LIVE APPLICATION WALKTHROUGH\nSynthetic image and signal examples are explicitly labelled in the application.\n\n" + plan.scenes.map(scene => scene.title + "\n" + scene.text).join("\n\n"));
  const audioInputs = plan.scenes.flatMap((_, index) => ["-i", path.join(work, `voice-${index}.wav`)]);
  const audioFilters = plan.scenes.map((scene,index) => `[${index}:a]aformat=sample_fmts=s16:sample_rates=44100:channel_layouts=mono,apad,atrim=duration=${scene.seconds},asetpts=PTS-STARTPTS[a${index}]`).join(";") + ";" + plan.scenes.map((_,i)=>`[a${i}]`).join("") + "concat=n=7:v=0:a=1[out]";
  await runEncoder([...audioInputs,"-filter_complex",audioFilters,"-map","[out]","narration.wav"],"Assembling 180-second narration.");
  const mp4 = path.join(output, stem + ".mp4");
  await runEncoder(["-f","concat","-safe","0","-i","frames.ffconcat","-i","narration.wav","-vf","pad=1440:810:0:0:color=0x0c1024,ass=captions.ass","-fps_mode","cfr","-r","24","-c:v","libx264","-preset","fast","-crf","21","-pix_fmt","yuv420p","-threads","4","-c:a","aac","-b:a","128k","-t","180","-movflags","+faststart","-metadata","title=Tsukuyomi Watch — Three Minute Demo","-metadata","comment=Live public application, generated English narration, labelled synthetic image and signal examples.",mp4],"Encoding the narrated, captioned MP4.");
  await writeFile(path.join(output, stem + "-Evidence.json"), JSON.stringify({recordedAt:new Date().toISOString(),url:plan.url,seconds:180,frames:frames.length,narration:"Generated locally with Microsoft Zira Desktop",scope:"Isolated browser only; no desktop, microphone, webcam or signed-in user profile",syntheticFixtures:["Spirit Lens demo star field","Signal Observatory light curve"]},null,2));
  console.log("Saved", mp4);
} finally {
  recording = false;
  clearInterval(snapshotTimer);
  socket?.close();
  browser.kill();
}
