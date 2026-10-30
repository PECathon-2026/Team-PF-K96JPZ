# Three-minute application demo

The deliverable is `Tsukuyomi-Watch-3-Minute-Demo.mp4` in the user's Desktop `Tsukuyomi-Watch-Submission` folder. It contains an actual walkthrough of the public application, generated English narration and burned-in captions. Matching SRT subtitles, a transcript and recording provenance are saved beside it. Large generated media and temporary frames are not committed to Git.

The recorder captures only a fresh isolated browser visiting https://tsukuyomi-watch.vercel.app. It does not capture the user's desktop, signed-in browser profile, microphone or webcam. This workflow uses browser screencasting and a temporary encoder; it does not require controlling Recordly.

## Timeline

| Time | Feature |
| --- | --- |
| 0:00–0:18 | Project introduction and navigation meaning |
| 0:18–0:50 | Worldwide city suggestions, nearby catalogue and weather |
| 0:50–1:20 | Lunar calendar, event filter and internal detail page |
| 1:20–2:15 | Synthetic image input, actual DnCNN restoration, slider, zoom, overlays, measurements and archival-import explanation |
| 2:15–2:35 | Synthetic light-curve screening |
| 2:35–2:50 | Empty local Honor journal and palette/light-dark changes |
| 2:50–3:00 | Live-app closing and test evidence |

The image and light curve are explicitly synthetic fixtures. Candidate objects are not confirmed identities. Honor observations are not fabricated for the demonstration. Calendar/push controls are described without claiming physical notification receipt. NASA SkyView is archival retrieval, not a live telescope feed; the recording does not rely on an external archive request succeeding.

## Reproduce

Requirements: Windows, installed Edge, Windows PowerShell with System.Speech and Microsoft Zira Desktop, Node, network access and a temporary `ffmpeg-static` installation.

```powershell
npm install --prefix "$env:TEMP/tsukuyomi-demo-tools" --no-audit --no-fund ffmpeg-static
$demoWork = Join-Path $env:TEMP 'tsukuyomi-demo-recording'
powershell -NoProfile -ExecutionPolicy Bypass -File docs/demo/prepare-narration.ps1 -OutputDirectory $demoWork
$env:DEMO_OUTPUT = Join-Path ([Environment]::GetFolderPath('Desktop')) 'Tsukuyomi-Watch-Submission'
node docs/demo/record-demo.mjs
```

The narration script adjusts each scene's speech speed to fit its allocation without truncating words. The capture script warms the API/model before recording, performs actual interactions, timestamps browser frames and assembles exactly 180 seconds of H.264/AAC video. Subtitle timing within a narration scene is estimated from word positions. It fails on unavailable controls or badly delayed actions rather than publishing a misleading successful demo.

The website can change, so selectors and timings may need updating for later versions. A failed attempt leaves temporary frames for debugging but does not publish an MP4. Do not run two recording instances on the same debugging port.
