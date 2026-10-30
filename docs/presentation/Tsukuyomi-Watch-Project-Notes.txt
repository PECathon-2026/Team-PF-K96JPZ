# Tsukuyomi Watch — feature and file notes

PS-002 · Team PF-K96JPZ · Prepared 30 October 2026 (IST)

Live app: https://tsukuyomi-watch.vercel.app
Repository: https://github.com/PECathon-2026/Team-PF-K96JPZ

## 1. Explain the project in 30 seconds

Tsukuyomi Watch helps an observer choose a place, choose a celestial event and inspect a space image. It combines a stargazing map and nighttime weather ranking, a lunar-style event calendar, conservative local AI image restoration, and interactive comparison tools in a Japanese-inspired interface. Bonus tools retrieve NASA archival images, screen measurement CSVs and reward self-reported observations.

## 2. What each feature does

### The Watchtower — where to observe

Watchtower means a lookout used to observe what is around you. Here it is the location finder. Search a city worldwide, use your location, or select a spot on the scroll-style interactive map. Choose a radius and sort by distance or forecast score. Shrine, temple, mountain and observatory icons represent curated destinations.

City suggestions and observing spots are different datasets. City search uses Open-Meteo/GeoNames and returns up to 20 name matches worldwide. It is not limited to the six stored observing destinations. Selecting a city sets the center for finding those nearby destinations; it does not turn every city into a verified dark-sky site. Provider spelling/coverage can affect results.

For a selected destination, the app retrieves the next future nighttime weather hour: cloud cover, humidity, visibility and supporting temperature/wind. This is a forecast, not a live sensor measurement. The score is a weather heuristic:

Score = round(100 × [40(1 − cloud%/100) + 20 min(visibilityKm/20, 1) + 15(1 − humidity%/100)] / 75)

Example: 50% clouds, 10 km visibility and 50% humidity produces 50/100. Visibility caps at 20 km. Moonlight and light pollution are not included today; do not claim that this score proves ideal astronomical seeing or darkness.

### Moon tracker and reminders

Shows moon phase, illumination and location-specific rise/set data. A missing polar rise or set remains missing rather than being invented. Displays observer-timezone-aware messages such as a moonrise tonight. Local reminders show toasts while the app is open. Calendar exports can be imported into a user's calendar.

Persistent browser push is a separate delivery path: opt in, register an anonymous device, create/cancel jobs, then a scheduler delivers due jobs through Web Push. It requires HTTPS, permission, VAPID credentials, a running API and a periodic scheduler. Do not promise closed-app delivery without verifying the scheduler and a physical device receipt; browser power policies can delay it. Safari endpoints are not enabled in the current allowlist.

### The Celestial Scroll — when to observe

Celestial means related to the sky; a scroll is a rolled manuscript. This is the space event tracker: moon phases, launches, calculated eclipses and approximate meteor windows. Filter types/dates and navigate a real Japanese Kyūreki lunar month, including leap months, or switch to Gregorian view. Open details inside the app and export calendar reminders.

Phase times retain source UTC instants. Launch times can change. Eclipse maxima describe global events rather than local contacts. Meteor windows are recurring approximate dates, with ±1 day labels and noon UTC placeholders, not exact yearly peaks. Event filtering uses UTC civil dates; displayed times use the observer's timezone.

### ISS pass panel

Predicts visible ISS segments for the selected site from fresh CelesTrak orbital elements and SGP4 propagation. It samples the next three days, requires station elevation ≥10°, observer Sun below −6°, and fully sunlit station segments. Stale/invalid data is rejected. These are predictions with sampling/orbit/atmospheric limits, not guaranteed sightings.

### The Spirit Lens — clean and inspect an image

Spirit Lens is a poetic name for a lens revealing faint details. Choose a PNG, JPEG or WebP (up to 12 MB / 24 megapixels). The browser makes an RGB preview whose longest edge is at most 768px, detects source candidates on the original preview and runs a real pretrained DnCNN denoising model locally in a Web Worker with ONNX WASM. Model files are verified with SHA-256 hashes.

Gentle and Balanced settings blend the inferred luminance conservatively, limiting channel changes and protecting detected source regions. Optional six-iteration Richardson–Lucy deconvolution reduces an assumed Gaussian blur; the PSF is user-selected and wrong settings can cause ringing. Richardson–Lucy is a conventional method, not a second AI model.

Local processing keeps selected image pixels off the API server. Bounded edits reduce risk but cannot guarantee preservation of every faint feature. FITS/RAW, 16-bit PNG and full-resolution scientific restoration are not supported. The model is pretrained, not trained from scratch by this team.

### Dojo visualization — understand the result

Dojo means a place of practice/training. The problem statement's visualization interface is implemented inside Spirit Lens: drag the before/after divider, zoom/pan, toggle candidate overlays, inspect brightness/size/morphology and download a restored PNG or JSON report.

Star and galaxy labels are candidates, not confirmed catalogue identities. Nebulae and blended sources can look galaxy-like. Brightness is uncalibrated pixel information, not astronomical magnitude. SSIM/PSNR compare output with the noisy input, not with clean ground truth; a high value alone does not prove scientific accuracy.

### NASA SkyView import — archival sky data

Find a target/name or sky coordinate and request a supported survey/field width. The app imports a bounded 512px archival display JPEG with source provenance, then restores it through the same local pipeline. This is on-demand archive retrieval, not a live camera/telescope stream. The provider can be overloaded; local upload remains available.

### Signal Observatory — measurement screening

An observatory is a place for studying the sky. Upload a light-curve CSV (time_utc,flux,error) or spectrum CSV (wavelength_nm,flux,error), up to 1 MB / 12–2000 rows. The optional error column must be consistently populated. Explicit timezones, unique coordinates and complete values are required.

Robust median/MAD screening flags unusual measurements; spectra use a local baseline. Supplied uncertainty contributes to the threshold. Charts, settings and candidate JSON can be inspected/exported. Synthetic examples are labeled. These are follow-up candidates, not confirmed discoveries or formal scientific significance; a spectrum alone cannot establish time variability.

### Honor journal — encourage observation

Record a past event you actually observed and earn 25 Honor Points once per event. Points derive from local journal entries; badges unlock at 25, 100 and 250 points. Export JSON to keep a copy. This is self-reported, editable device-local storage, not a verified leaderboard or account-synced cloud ledger. The /dojo route displays this journal; the image comparison viewer is in Spirit Lens.

### Themes, meanings and navigation notes

Four motif palettes: Ink Wash (Tsukuyomi), Torii Crimson (Akatsuki), Sakura Rose and Katana Black/Gold. Light/dark mode is independent of the palette. Shared motifs, moon cues, animations and reduced-motion controls support the visual identity. Japanese characters reveal English meanings on hover/focus/touch. Navigation notes explain both each section's name and its function on hover/keyboard focus.

## 3. Architecture and request flows

Planning: React UI → React Query/tRPC client → same-origin /trpc proxy → Express/tRPC input validation → feature service → provider and/or Drizzle/Neon → typed response → UI.

City suggestions: search input → /api/cities on Vercel → fixed Open-Meteo geocoding host → validated city results. Catalogue lookup is independent on the API so one failing dependency does not hide the other.

Image: local file/archive import → validated preview → local worker → verified DnCNN → bounded blend / optional deblur → comparison, candidates and downloads. Selected local image pixels do not go to the backend.

Push: opted-in anonymous device → hashed ownership + stored subscription/jobs → periodic scheduler with a private credential → claimed/retried jobs → browser push service → service-worker notification.

Data: current locations/weather/events/feed bookkeeping and push jobs persist in PostgreSQL. Image previews/results remain in the current browser session. Themes/reminders/Honor use browser storage. User/account/Honor database tables are foundations, not evidence of completed authentication or cloud sync.

## 4. Verification and honest scope

Updated automated run: 31/31 test cases passed across nine test files, including three new worldwide city-search cases. See test-results-current.txt. Frontend/API production builds passed. The older detailed judging deck preserves the previous 28-case audit; it is historical evidence, not the current count.

Tests cover missing nighttime forecasts, score bounds, polar moon data, UTC/leap/lunar dates, invalid orbital elements, ICS escaping, unsafe push endpoints, bounded image changes, flat skies, malformed image headers, known deblur fixtures, bad CSVs and duplicate/future observations.

Remaining evidence gaps: measured code coverage, CI, broad cross-browser/permission/offline E2E, physical closed-app push receipt, concurrency/load validation, a full accessibility audit, astronomy-domain benchmarks and measured user impact. Ready for a controlled hackathon demo; not certified for always-on production or scientific discovery.

## 5. File-by-file guide

Every tracked/nonignored deliverable is listed below. Generated dependency/build directories, private .env files, secret stores, .git internals and ignored PNG previews are intentionally excluded. Configuration and generic UI primitives are distinguished from product features. Paths are relative to the repository root.


### Root configuration

| File | Responsibility |
| --- | --- |
| `.env.example` | Environment-variable template. Lists required configuration names; real credentials belong in ignored environment files. |
| `.gitignore` | Prevents dependencies, build artifacts and private environment files from entering Git. |
| `.npmrc` | pnpm/npm installation settings for this workspace. |

### .vscode

| File | Responsibility |
| --- | --- |
| `.vscode/settings.json` | Shared editor configuration; does not implement application behavior. |

### Root configuration

| File | Responsibility |
| --- | --- |
| `README.md` | Repository overview and setup entry point; detailed completion notes document later features. |

### apps/api

| File | Responsibility |
| --- | --- |
| `apps/api/.eslintrc.cjs` | Package lint rules extending shared repository configuration. |
| `apps/api/package.json` | Package identity, workspace exports, dependencies and runnable scripts for apps/api. |
| `apps/api/src/env.ts` | Validates backend runtime configuration such as port, mode and base URL. |
| `apps/api/src/index.ts` | API process entry point; starts the Express server on the configured port. |
| `apps/api/src/server.ts` | Creates Express, health checks, tRPC transport, OpenAPI JSON and Scalar API documentation. |
| `apps/api/tsconfig.json` | TypeScript compiler/project settings for apps/api. |
| `apps/api/tsup.config.ts` | Bundles the TypeScript API and workspace code into executable server output. |

### apps/web

| File | Responsibility |
| --- | --- |
| `apps/web/.gitignore` | Excludes local/generated files in this directory from version control. |
| `apps/web/README.md` | Frontend development notes. |
| `apps/web/app/analysis/page.tsx` | Signal Observatory CSV controls, synthetic examples, plots, candidate results and export. |
| `apps/web/app/api/cities/route.ts` | Same-origin city geocoding route on the web host; validates names, caches results, deduplicates concurrent lookups and reports provider failures. |
| `apps/web/app/api/skyview/route.ts` | Fixed-host NASA archival-image proxy with validated parameters, time/size/concurrency limits, cache and overload handling. |
| `apps/web/app/bonuses.css` | Signal Observatory, Honor journal and shared bonus-page controls/layout. |
| `apps/web/app/dojo/page.tsx` | Displays the device-local observation journal, derived Honor total, badges and JSON export. |
| `apps/web/app/event-details.css` | Internal event detail, breadcrumb and error-state styling. |
| `apps/web/app/events/[id]/page.tsx` | Dynamic route that opens an event inside this application. |
| `apps/web/app/favicon.ico` | Browser tab/site icon. |
| `apps/web/app/fonts/GeistMonoVF.woff` | Locally hosted Geist Mono variable font. |
| `apps/web/app/fonts/GeistVF.woff` | Locally hosted Geist Sans variable font. |
| `apps/web/app/globals.css` | Global imports and main dashboard/layout styles. |
| `apps/web/app/japanese-text.css` | English-meaning tooltips for Japanese text. |
| `apps/web/app/layout.tsx` | Global document wrapper, local fonts, metadata, environment validation, CSS and providers. |
| `apps/web/app/location-search.css` | City/destination input and suggestion dropdown styling. |
| `apps/web/app/moon-tracker.css` | Moon tracker cards and reminder UI styling. |
| `apps/web/app/navigation-hint.css` | Readable, theme-aware navigation notes displayed on hover or keyboard focus. |
| `apps/web/app/page.tsx` | Main Watchtower/Scroll dashboard: city origin, radius, sorting, destination selection, forecasts and feature navigation. |
| `apps/web/app/spirit-lens.css` | Upload, restoration, comparison, measurement and lens-page layouts. |
| `apps/web/app/spirit-lens/page.tsx` | Route entry for the Spirit Lens restoration and comparison interface. |
| `apps/web/app/theme-landscape.css` | Shared Japanese-inspired landscape artwork styling. |
| `apps/web/app/watch-motion.css` | Animations and reduced-motion behavior. |
| `apps/web/app/watch-palettes.css` | Light/dark color definitions for Ink Wash, Torii, Sakura and Katana palettes. |
| `apps/web/app/watch-theme.css` | Semantic colors and shared visual tokens used by components. |
| `apps/web/app/watchtower-map.css` | Scroll map, marker glyphs, controls, labels and map layout. |
| `apps/web/components.json` | shadcn component generator paths, style and utility configuration. |
| `apps/web/components/background-alerts.tsx` | Browser push opt-in, anonymous device ownership, subscription, reminder scheduling, pending jobs, cancellation and disabling. |
| `apps/web/components/bonus-shell.tsx` | Shared header, feature links, palette landscape and content frame for Signals and Honor pages. |
| `apps/web/components/celestial-scroll.tsx` | Lunar/Gregorian calendar navigation, event-type/date filtering, feed status and event list. |
| `apps/web/components/event-details.tsx` | Loads and presents an event with date/source context, calendar export, alerts and observation form. |
| `apps/web/components/iss-passes.tsx` | Loads visible ISS prediction segments for the selected Watchtower destination. |
| `apps/web/components/japanese-text.tsx` | Accessible hover/focus/touch explanations for Japanese characters and phrases. |
| `apps/web/components/location-search.tsx` | Debounced worldwide city and catalogue searches; displays independent results and chooses a search origin or a saved spot. |
| `apps/web/components/moon-alert-scheduler.tsx` | Checks local reminders while the app is open and shows due moonrise toasts. This is separate from closed-app Web Push. |
| `apps/web/components/moon-tracker.tsx` | Moon phase, illumination, rise/set display, in-app reminders and calendar/push options. |
| `apps/web/components/navigation-hint.tsx` | Shared definitions of feature names/meanings and Radix hover/focus tooltips attached to navigation links. |
| `apps/web/components/observation-form.tsx` | Validates a self-reported observation and records one local Honor award per event. |
| `apps/web/components/scroll-map.tsx` | Initializes Leaflet, loads bundled outlines, creates safe marker popups and supports fit/search-this-area controls. |
| `apps/web/components/sky-atmosphere.tsx` | Decorative sky, drifting petals and atmospheric visual elements. |
| `apps/web/components/spirit-lens/comparison-view.tsx` | Interactive before/after divider, zoom/pan, candidate overlays and inspection controls. |
| `apps/web/components/spirit-lens/skyview-import.tsx` | Target/survey/field controls for NASA archival import; keeps source query provenance. |
| `apps/web/components/spirit-lens/spirit-lens.tsx` | Coordinates image input, worker lifecycle, progress/cancel/error state, restoration settings, candidate details and downloads. |
| `apps/web/components/theme-landscape.tsx` | Reusable SVG motif artwork matching the selected Japanese palette. |
| `apps/web/components/theme-toggle.tsx` | Controls light/dark mode and motif selection. |
| `apps/web/components/ui/accordion.tsx` | Expandable stacked sections. Shared UI primitive; its presence alone does not mean a separate product feature exists. |
| `apps/web/components/ui/alert-dialog.tsx` | Modal confirmation dialog. Shared UI primitive; its presence alone does not mean a separate product feature exists. |
| `apps/web/components/ui/alert.tsx` | Inline status/warning message. Shared UI primitive; its presence alone does not mean a separate product feature exists. |
| `apps/web/components/ui/aspect-ratio.tsx` | Fixed image/media proportions. Shared UI primitive; its presence alone does not mean a separate product feature exists. |
| `apps/web/components/ui/avatar.tsx` | Profile image/fallback. Shared UI primitive; its presence alone does not mean a separate product feature exists. |
| `apps/web/components/ui/badge.tsx` | Compact status label. Shared UI primitive; its presence alone does not mean a separate product feature exists. |
| `apps/web/components/ui/breadcrumb.tsx` | Hierarchical navigation trail. Shared UI primitive; its presence alone does not mean a separate product feature exists. |
| `apps/web/components/ui/button-group.tsx` | Grouped button layout. Shared UI primitive; its presence alone does not mean a separate product feature exists. |
| `apps/web/components/ui/button.tsx` | Reusable styled button. Shared UI primitive; its presence alone does not mean a separate product feature exists. |
| `apps/web/components/ui/calendar.tsx` | Generic date-picker component (the celestial lunar calendar has its own feature implementation). Shared UI primitive; its presence alone does not mean a separate product feature exists. |
| `apps/web/components/ui/card.tsx` | Reusable content panel. Shared UI primitive; its presence alone does not mean a separate product feature exists. |
| `apps/web/components/ui/carousel.tsx` | Scrollable item carousel. Shared UI primitive; its presence alone does not mean a separate product feature exists. |
| `apps/web/components/ui/chart.tsx` | Recharts presentation helpers. Shared UI primitive; its presence alone does not mean a separate product feature exists. |
| `apps/web/components/ui/checkbox.tsx` | Checked/unchecked input. Shared UI primitive; its presence alone does not mean a separate product feature exists. |
| `apps/web/components/ui/collapsible.tsx` | Expandable content block. Shared UI primitive; its presence alone does not mean a separate product feature exists. |
| `apps/web/components/ui/command.tsx` | Command/search menu. Shared UI primitive; its presence alone does not mean a separate product feature exists. |
| `apps/web/components/ui/context-menu.tsx` | Right-click menu. Shared UI primitive; its presence alone does not mean a separate product feature exists. |
| `apps/web/components/ui/dialog.tsx` | Modal dialog. Shared UI primitive; its presence alone does not mean a separate product feature exists. |
| `apps/web/components/ui/drawer.tsx` | Slide-in panel. Shared UI primitive; its presence alone does not mean a separate product feature exists. |
| `apps/web/components/ui/dropdown-menu.tsx` | Action dropdown. Shared UI primitive; its presence alone does not mean a separate product feature exists. |
| `apps/web/components/ui/empty.tsx` | Empty-state presentation. Shared UI primitive; its presence alone does not mean a separate product feature exists. |
| `apps/web/components/ui/field.tsx` | Labeled field layout/feedback. Shared UI primitive; its presence alone does not mean a separate product feature exists. |
| `apps/web/components/ui/form.tsx` | Form context and validation presentation. Shared UI primitive; its presence alone does not mean a separate product feature exists. |
| `apps/web/components/ui/hover-card.tsx` | Hover/focus information card. Shared UI primitive; its presence alone does not mean a separate product feature exists. |
| `apps/web/components/ui/input-group.tsx` | Grouped input/accessory layout. Shared UI primitive; its presence alone does not mean a separate product feature exists. |
| `apps/web/components/ui/input-otp.tsx` | One-time-code input. Shared UI primitive; its presence alone does not mean a separate product feature exists. |
| `apps/web/components/ui/input.tsx` | Styled text input. Shared UI primitive; its presence alone does not mean a separate product feature exists. |
| `apps/web/components/ui/item.tsx` | Reusable list item layout. Shared UI primitive; its presence alone does not mean a separate product feature exists. |
| `apps/web/components/ui/kbd.tsx` | Keyboard-shortcut key label. Shared UI primitive; its presence alone does not mean a separate product feature exists. |
| `apps/web/components/ui/label.tsx` | Accessible form label. Shared UI primitive; its presence alone does not mean a separate product feature exists. |
| `apps/web/components/ui/menubar.tsx` | Desktop-style menu bar. Shared UI primitive; its presence alone does not mean a separate product feature exists. |
| `apps/web/components/ui/navigation-menu.tsx` | Expandable navigation menu. Shared UI primitive; its presence alone does not mean a separate product feature exists. |
| `apps/web/components/ui/pagination.tsx` | Page navigation controls. Shared UI primitive; its presence alone does not mean a separate product feature exists. |
| `apps/web/components/ui/popover.tsx` | Anchored floating panel. Shared UI primitive; its presence alone does not mean a separate product feature exists. |
| `apps/web/components/ui/progress.tsx` | Progress indicator. Shared UI primitive; its presence alone does not mean a separate product feature exists. |
| `apps/web/components/ui/radio-group.tsx` | Single-choice radio inputs. Shared UI primitive; its presence alone does not mean a separate product feature exists. |
| `apps/web/components/ui/resizable.tsx` | Resizable split panels. Shared UI primitive; its presence alone does not mean a separate product feature exists. |
| `apps/web/components/ui/scroll-area.tsx` | Styled scrollable viewport. Shared UI primitive; its presence alone does not mean a separate product feature exists. |
| `apps/web/components/ui/select.tsx` | Styled selection menu. Shared UI primitive; its presence alone does not mean a separate product feature exists. |
| `apps/web/components/ui/separator.tsx` | Visual section divider. Shared UI primitive; its presence alone does not mean a separate product feature exists. |
| `apps/web/components/ui/sheet.tsx` | Side-sheet dialog. Shared UI primitive; its presence alone does not mean a separate product feature exists. |
| `apps/web/components/ui/sidebar.tsx` | Generic sidebar building blocks. Shared UI primitive; its presence alone does not mean a separate product feature exists. |
| `apps/web/components/ui/skeleton.tsx` | Loading placeholder. Shared UI primitive; its presence alone does not mean a separate product feature exists. |
| `apps/web/components/ui/slider.tsx` | Range slider. Shared UI primitive; its presence alone does not mean a separate product feature exists. |
| `apps/web/components/ui/sonner.tsx` | Toast notification host. Shared UI primitive; its presence alone does not mean a separate product feature exists. |
| `apps/web/components/ui/spinner.tsx` | Loading spinner. Shared UI primitive; its presence alone does not mean a separate product feature exists. |
| `apps/web/components/ui/switch.tsx` | On/off control. Shared UI primitive; its presence alone does not mean a separate product feature exists. |
| `apps/web/components/ui/table.tsx` | Table presentation primitives. Shared UI primitive; its presence alone does not mean a separate product feature exists. |
| `apps/web/components/ui/tabs.tsx` | Tabbed content. Shared UI primitive; its presence alone does not mean a separate product feature exists. |
| `apps/web/components/ui/textarea.tsx` | Multiline text field. Shared UI primitive; its presence alone does not mean a separate product feature exists. |
| `apps/web/components/ui/toggle-group.tsx` | Related toggle controls. Shared UI primitive; its presence alone does not mean a separate product feature exists. |
| `apps/web/components/ui/toggle.tsx` | Pressed/unpressed control. Shared UI primitive; its presence alone does not mean a separate product feature exists. |
| `apps/web/components/ui/tooltip.tsx` | Radix accessible tooltip primitives. Shared UI primitive; its presence alone does not mean a separate product feature exists. |
| `apps/web/env.js` | Validates frontend/server environment configuration; production API_URL must use HTTPS. |
| `apps/web/eslint.config.js` | Frontend lint configuration using shared Next.js/React rules. |
| `apps/web/hooks/use-mobile.ts` | Reusable hook that reports a mobile-sized viewport. |
| `apps/web/lib/bonuses.test.ts` | Signal fixture, CSV edge-case and Honor validation/badge tests. |
| `apps/web/lib/event-calendar.ts` | Creates downloadable UTC iCalendar events with escaped text, folded Unicode lines and reminder metadata. |
| `apps/web/lib/geocoding.test.ts` | Tests worldwide query parameters, response mapping, empty/error/malformed data and invalid input without upstream calls. |
| `apps/web/lib/geocoding.ts` | Validates worldwide city-provider responses and maps them into a small UI-safe place shape; requests up to 20 name matches. |
| `apps/web/lib/honor-journal.ts` | Local observation validation, one-award-per-event logic, derived points/badges and cross-tab coordination. |
| `apps/web/lib/moon-reminders.ts` | Local reminder validation, storage/event notifications and observer-timezone-aware moonrise messages. |
| `apps/web/lib/spirit-lens/analysis.test.ts` | Tests input safety, reflection, edit/source preservation, object candidates and flat-sky behavior. |
| `apps/web/lib/spirit-lens/analysis.ts` | Luminance, robust source/morphology detection, conservative color-preserving blends and comparison metrics. |
| `apps/web/lib/spirit-lens/deblur.test.ts` | Tests deconvolution against a known synthetic blurred-source fixture. |
| `apps/web/lib/spirit-lens/deblur.ts` | Gaussian PSF blur operator and optional six-iteration Richardson–Lucy deconvolution. |
| `apps/web/lib/spirit-lens/image.ts` | Checks image headers and size, decodes supported formats, makes bounded previews/synthetic input and exports blobs. |
| `apps/web/lib/spirit-lens/model.ts` | Model identity and integrity hashes, image limits, strength settings and worker message/result types. |
| `apps/web/lib/spirit-lens/spirit-lens.worker.ts` | Verifies model assets, runs tiled DnCNN ONNX WASM inference, applies bounded cleanup/deblur and returns measurements/candidates. |
| `apps/web/lib/transient-analysis.ts` | CSV parsing and time-domain/spectral median-MAD screening, uncertainty handling and candidate output. |
| `apps/web/lib/utils.ts` | Shared class-name utility combining conditional classes and Tailwind conflict resolution. |
| `apps/web/next.config.js` | Next.js configuration, including same-origin /trpc proxy rewrites to the backend. |
| `apps/web/package.json` | Package identity, workspace exports, dependencies and runnable scripts for apps/web. |
| `apps/web/postcss.config.mjs` | Tailwind/PostCSS stylesheet processing configuration. |
| `apps/web/providers/global.tsx` | Installs React Query, tRPC, light/dark mode, motif palette, in-app moon reminders and toast notifications. |
| `apps/web/providers/palette.tsx` | Stores and applies the four motif palettes independently of light/dark mode. |
| `apps/web/public/.gitignore` | Excludes local/generated files in this directory from version control. |
| `apps/web/public/WORLD_OUTLINE_LICENSE.txt` | Attribution/license information for bundled geographic outlines. |
| `apps/web/public/file-text.svg` | Starter/template vector graphic; not an astronomy data source or a core feature implementation. |
| `apps/web/public/globe.svg` | Starter/template vector graphic; not an astronomy data source or a core feature implementation. |
| `apps/web/public/models/dncnn/.gitattributes` | Treats model binary files appropriately in Git. |
| `apps/web/public/models/dncnn/LICENSE.txt` | Upstream model license; retain it when redistributing assets. |
| `apps/web/public/models/dncnn/README.md` | DnCNN origin, export/version and usage/provenance notes. |
| `apps/web/public/models/dncnn/dncnn.data` | External pretrained tensor/weight data loaded by the ONNX graph. |
| `apps/web/public/models/dncnn/dncnn.onnx` | ONNX graph defining the pretrained DnCNN computation. |
| `apps/web/public/next.svg` | Starter/template vector graphic; not an astronomy data source or a core feature implementation. |
| `apps/web/public/push-worker.js` | Service worker that displays received push messages and opens a safe internal application URL when clicked. |
| `apps/web/public/turborepo-dark.svg` | Starter/template vector graphic; not an astronomy data source or a core feature implementation. |
| `apps/web/public/turborepo-light.svg` | Starter/template vector graphic; not an astronomy data source or a core feature implementation. |
| `apps/web/public/vercel.svg` | Starter/template vector graphic; not an astronomy data source or a core feature implementation. |
| `apps/web/public/window.svg` | Starter/template vector graphic; not an astronomy data source or a core feature implementation. |
| `apps/web/public/world-outline.geojson` | Bundled approximate geographic boundaries, letting the scroll map render without a commercial tile API. |
| `apps/web/scripts/prepare-spirit-lens.mjs` | Copies ONNX browser runtime assets into public output before dev/build. |
| `apps/web/trpc/client.ts` | Typed React hooks bound to the shared tRPC router. |
| `apps/web/trpc/create-client.ts` | Builds the HTTP or streaming tRPC transport; browser requests use the web origin. |
| `apps/web/trpc/server.ts` | Typed programmatic API clients for non-hook/server-side use. |
| `apps/web/tsconfig.json` | TypeScript compiler/project settings for apps/web. |
| `apps/web/vercel.json` | Vercel framework, region, install and build commands for the monorepo frontend. |

### Root configuration

| File | Responsibility |
| --- | --- |
| `docker-compose.yml` | Local development infrastructure, including PostgreSQL; not the hosted Neon database. |

### docs

| File | Responsibility |
| --- | --- |
| `docs/API_SETUP.md` | Data-provider setup, URLs and configuration instructions. |
| `docs/BONUS_FEATURES.md` | Archive, signal-analysis and Honor behavior and limits. |
| `docs/COMPLETION_NOTES.md` | Implemented remaining requirements, push prerequisites and practical constraints. |
| `docs/PRODUCTION.md` | Deployment setup, environment wiring and operational notes. |
| `docs/SPIRIT_LENS.md` | Local AI processing, model provenance and image-restoration safeguards. |
| `docs/demo/.gitignore` | Excludes generated recordings, narration audio and frame outputs from Git. |
| `docs/demo/README.md` | Three-minute recording timeline, truthful demo scope and reproduction instructions. |
| `docs/demo/demo-plan.json` | Seven timed scenes and the generated English narration text, totaling 180 seconds. |
| `docs/demo/prepare-narration.ps1` | Uses local Windows speech synthesis, measures each WAV and fits narration to scene allocations. |
| `docs/demo/record-demo.mjs` | Records only an isolated public-app browser, performs the demo, and exports captioned H.264/AAC video plus transcript/provenance. |
| `docs/presentation/.gitignore` | Excludes generated slide PNG previews from Git. |
| `docs/presentation/DEMO_GUIDE.md` | Five-minute demonstration, fallbacks and panel questions. |
| `docs/presentation/READINESS.md` | Detailed historical rubric audit with 28-test baseline, requirement mapping and limitations. |
| `docs/presentation/README.md` | Presentation contents and generation/export instructions. |
| `docs/presentation/Tsukuyomi-Watch-8-Slide-Pitch.pdf` | Portable PDF of the eight-slide pitch. |
| `docs/presentation/Tsukuyomi-Watch-8-Slide-Pitch.pptx` | New concise eight-slide project explanation and pitch with speaker notes. |
| `docs/presentation/Tsukuyomi-Watch-Judging-Deck.pdf` | PDF export of the original 17-slide deck. |
| `docs/presentation/Tsukuyomi-Watch-Judging-Deck.pptx` | Original detailed 17-slide editable judging deck with speaker notes and 28-test audit baseline. |
| `docs/presentation/Tsukuyomi-Watch-Project-Notes.md` | This feature explanation and per-file codebase guide in Markdown. |
| `docs/presentation/Tsukuyomi-Watch-Project-Notes.txt` | Plain-text copy of this guide for opening without a Markdown editor. |
| `docs/presentation/assets/calendar.png` | Actual production calendar screenshot, used as presentation evidence; not a design mockup. |
| `docs/presentation/assets/hero.png` | Actual production hero screenshot, used as presentation evidence; not a design mockup. |
| `docs/presentation/assets/lens.png` | Actual production lens screenshot, used as presentation evidence; not a design mockup. |
| `docs/presentation/assets/live-evidence.json` | Timestamp and displayed measurements from the actual synthetic browser restoration run. |
| `docs/presentation/assets/signals.png` | Actual production signals screenshot, used as presentation evidence; not a design mockup. |
| `docs/presentation/assets/watchtower.png` | Actual production watchtower screenshot, used as presentation evidence; not a design mockup. |
| `docs/presentation/build-deck.cjs` | Reproducibly generates the original detailed PowerPoint using PptxGenJS. |
| `docs/presentation/build-notes.py` | Generates this feature overview and verifies that every tracked/nonignored deliverable has a file description. |
| `docs/presentation/build-pitch.cjs` | Generates the separate eight-slide project pitch using native editable shapes/text and real UI screenshots. |
| `docs/presentation/capture-demo.mjs` | Isolated headless Edge script capturing actual production UI and a labelled synthetic image-restoration result. |
| `docs/presentation/export-deck.ps1` | Uses installed PowerPoint in the background to export the detailed deck to PDF and slide PNGs. |
| `docs/presentation/export-pitch.ps1` | Exports the eight-slide pitch to PDF and slide PNG previews using PowerPoint. |
| `docs/presentation/fixtures/light-curve.csv` | Labelled synthetic light-curve demo data with an injected bright measurement. |
| `docs/presentation/fixtures/spectrum.csv` | Labelled synthetic spectrum with positive and negative injected features. |
| `docs/presentation/test-results-current.txt` | Updated 31-case transcript including three city-geocoding regression cases. |
| `docs/presentation/test-results.txt` | Original recorded 28-case automated test transcript; historical evidence. |
| `docs/presentation/verify-deck.py` | Checks the detailed deck ZIP, slide/notes counts, PDF signature and shape bounds. |

### ops

| File | Responsibility |
| --- | --- |
| `ops/push-cron.mjs` | Calls the protected push delivery procedure; supports periodic invocation or local watch mode. |
| `ops/render-start.mjs` | Loads allowed deployment secrets, runs migrations and the idempotent seed, then starts the compiled API. |

### Root configuration

| File | Responsibility |
| --- | --- |
| `package.json` | Root workspace commands for build, development, database operations, lint and formatting. |

### packages/database

| File | Responsibility |
| --- | --- |
| `packages/database/.eslintrc.cjs` | Package lint rules extending shared repository configuration. |
| `packages/database/IMPLEMENTATION.md` | Database design explanation and schema implementation notes. |
| `packages/database/drizzle.config.ts` | Drizzle schema, migrations directory and database configuration. |
| `packages/database/drizzle/0000_dusty_morg.sql` | Initial user-table migration. |
| `packages/database/drizzle/0001_celestial_foundation.sql` | Creates core location, weather, event and Honor/preference foundation tables and constraints. |
| `packages/database/drizzle/0002_celestial_feeds.sql` | Adds provider feed membership and synchronization bookkeeping. |
| `packages/database/drizzle/0003_moon_conditions.sql` | Adds cached phase/illumination/fetch timestamps to location rise/set data. |
| `packages/database/drizzle/0004_amused_kingpin.sql` | Adds persistent push devices and scheduled delivery jobs. |
| `packages/database/drizzle/meta/0000_snapshot.json` | Drizzle-generated schema snapshot after migration 0000; used for future schema diffs, not runtime feature code. |
| `packages/database/drizzle/meta/0001_snapshot.json` | Drizzle-generated schema snapshot after migration 0001; used for future schema diffs, not runtime feature code. |
| `packages/database/drizzle/meta/0002_snapshot.json` | Drizzle-generated schema snapshot after migration 0002; used for future schema diffs, not runtime feature code. |
| `packages/database/drizzle/meta/0003_snapshot.json` | Drizzle-generated schema snapshot after migration 0003; used for future schema diffs, not runtime feature code. |
| `packages/database/drizzle/meta/0004_snapshot.json` | Drizzle-generated schema snapshot after migration 0004; used for future schema diffs, not runtime feature code. |
| `packages/database/drizzle/meta/_journal.json` | Drizzle migration order/version bookkeeping; not a user observation journal. |
| `packages/database/env.ts` | Validates DATABASE_URL without placing it in client code. |
| `packages/database/index.ts` | Creates the PostgreSQL/Drizzle client and exports query helpers. |
| `packages/database/models/event-feed.ts` | Tracks provider feed membership and refresh attempts/successes. |
| `packages/database/models/events.ts` | Moon, rise/set, ISS, event type, celestial event and related event schema. |
| `packages/database/models/honor.ts` | Schema foundation for preferences, server Honor ledger and badges. Current user-facing journal uses local storage instead. |
| `packages/database/models/push.ts` | Persistent anonymous devices and alert jobs with ownership hashes, claim/attempt/sent timestamps and indexes. |
| `packages/database/models/user.ts` | User profile/account schema foundation, including optional home coordinates and timezone. |
| `packages/database/models/watchtower.ts` | Location, weather snapshot, Night Honor Score and related location schema/constraints. |
| `packages/database/package.json` | Package identity, workspace exports, dependencies and runnable scripts for packages/database. |
| `packages/database/schema.ts` | Re-exports table definitions as the complete schema. |
| `packages/database/seed.ts` | Idempotently populates initial locations and supporting catalogue/reference data. |
| `packages/database/tsconfig.json` | TypeScript compiler/project settings for packages/database. |

### packages/eslint-config

| File | Responsibility |
| --- | --- |
| `packages/eslint-config/README.md` | Shared lint configuration usage notes. |
| `packages/eslint-config/base.js` | Base JavaScript/TypeScript lint rules. |
| `packages/eslint-config/next.js` | Next.js-specific lint rules. |
| `packages/eslint-config/package.json` | Package identity, workspace exports, dependencies and runnable scripts for packages/eslint-config. |
| `packages/eslint-config/react-internal.js` | Shared React component/hook lint rules. |

### packages/logger

| File | Responsibility |
| --- | --- |
| `packages/logger/.eslintrc.cjs` | Package lint rules extending shared repository configuration. |
| `packages/logger/env.ts` | Validates logger level and environment settings. |
| `packages/logger/index.ts` | Shared Winston console logger, readable in development and structured in deployment. |
| `packages/logger/package.json` | Package identity, workspace exports, dependencies and runnable scripts for packages/logger. |
| `packages/logger/tsconfig.json` | TypeScript compiler/project settings for packages/logger. |

### packages/services

| File | Responsibility |
| --- | --- |
| `packages/services/.eslintrc.cjs` | Package lint rules extending shared repository configuration. |
| `packages/services/alerts/alerts.test.ts` | Tests unsafe push endpoints and scheduler credential rejection. |
| `packages/services/alerts/generate-keys.cjs` | Generates VAPID/scheduler credentials into ignored local configuration; refuses to overwrite existing credentials. |
| `packages/services/alerts/index.ts` | Device ownership hashes, safe push endpoints, reminder jobs, claim leases, retries, Web Push and expired-subscription cleanup. |
| `packages/services/alerts/ownership.integration.ts` | Database integration checks for anonymous device/job isolation and deletion using dummy subscriptions; not a physical push receipt test. |
| `packages/services/celestial/calculated.test.ts` | Known eclipse and lunar-date fixtures, meteor estimates and ISS invalid/bounded-prediction tests. |
| `packages/services/celestial/calculated.ts` | Astronomy Engine eclipses, explicitly approximate meteor windows and Japanese lunisolar calendar calculations. |
| `packages/services/celestial/himekuri.d.ts` | TypeScript declarations for the Japanese calendar library import. |
| `packages/services/celestial/index.ts` | Coordinates normalized provider feeds, event upserts/feed membership, refresh policy, lunar intervals and event details. |
| `packages/services/celestial/iss.ts` | Fetches fresh CelesTrak TLEs, runs SGP4 propagation and filters visible fully sunlit ISS segments for an observing site. |
| `packages/services/celestial/providers.test.ts` | Provider/date/ID/pagination validation and calendar-export edge-case tests. |
| `packages/services/celestial/providers.ts` | Normalizes external phase/launch data, UTC month intervals, source IDs and provider status. |
| `packages/services/clients/google-oauth.ts` | Google OAuth URL/client helper used by provider-discovery scaffolding. |
| `packages/services/env.ts` | Service-layer runtime environment validation, including optional Google OAuth configuration. |
| `packages/services/package.json` | Package identity, workspace exports, dependencies and runnable scripts for packages/services. |
| `packages/services/tsconfig.json` | TypeScript compiler/project settings for packages/services. |
| `packages/services/user/index.ts` | Lists Google sign-in as available only when its configuration is present; does not implement full authentication. |
| `packages/services/user/model.ts` | Zod response definitions/types for available authentication methods. |
| `packages/services/watchtower/index.ts` | Reads the destination catalogue, computes nearby distances, ranks forecasts and transactionally caches weather/score pairs. |
| `packages/services/watchtower/moon-model.ts` | Parses USNO moon payloads, validates requested dates/illumination and preserves missing polar rise/set as null. |
| `packages/services/watchtower/moon.test.ts` | Moon UTC/parsing, polar/malformed data and timezone-aware reminder tests. |
| `packages/services/watchtower/moon.ts` | Fetches/caches location-specific moon conditions and integrates stored rise/set data. |
| `packages/services/watchtower/search.ts` | Searches stored destination names; catalogOnly avoids backend geocoding. Legacy combined city lookup remains for compatible callers. |
| `packages/services/watchtower/weather.test.ts` | Weather score bounds, bad/null/no-night payloads, future selection, unit conversion and distance/date-line tests. |
| `packages/services/watchtower/weather.ts` | Open-Meteo forecast adapter, next-night selection, weather-only Night Honor Score and Haversine distance. |

### packages/trpc

| File | Responsibility |
| --- | --- |
| `packages/trpc/.eslintrc.cjs` | Package lint rules extending shared repository configuration. |
| `packages/trpc/client/index.ts` | Exports inferred router input/output types and tRPC client helpers. |
| `packages/trpc/package.json` | Package identity, workspace exports, dependencies and runnable scripts for packages/trpc. |
| `packages/trpc/server/context.ts` | Current request-context placeholder. It does not establish authenticated user sessions. |
| `packages/trpc/server/index.ts` | Combines feature routers into the shared server router and exports context/types. |
| `packages/trpc/server/routes/auth/route.ts` | Lists configured OAuth providers. This is scaffolding, not a completed sign-in/callback/session system. |
| `packages/trpc/server/routes/celestial/route.ts` | Validates month/lunar/event/ISS requests and exposes celestial services. |
| `packages/trpc/server/routes/health/route.ts` | Simple typed health procedure with an OpenAPI mapping. |
| `packages/trpc/server/routes/push/route.ts` | Validates push device, reminder and delivery procedure inputs; forwards ownership and scheduler credentials to service checks. |
| `packages/trpc/server/routes/watchtower/route.ts` | Validates place/radius queries and exposes catalog search, locations, ranking, weather and moon conditions. |
| `packages/trpc/server/schema.ts` | Shared Zod and request-schema helpers for API procedures. |
| `packages/trpc/server/services/index.ts` | Creates the shared UserService instance used by authentication-provider discovery. |
| `packages/trpc/server/trpc.ts` | Creates the typed tRPC instance, OpenAPI metadata support, router and public procedure helpers. |
| `packages/trpc/server/utils/path-generator.ts` | Builds consistent prefixed OpenAPI endpoint paths. |
| `packages/trpc/tsconfig.json` | TypeScript compiler/project settings for packages/trpc. |

### packages/typescript-config

| File | Responsibility |
| --- | --- |
| `packages/typescript-config/base.json` | Shared strict TypeScript compiler defaults. |
| `packages/typescript-config/nextjs.json` | TypeScript defaults specialized for Next.js apps. |
| `packages/typescript-config/node.json` | TypeScript defaults specialized for Node packages. |
| `packages/typescript-config/package.json` | Package identity, workspace exports, dependencies and runnable scripts for packages/typescript-config. |

### Root configuration

| File | Responsibility |
| --- | --- |
| `pnpm-lock.yaml` | Locks resolved dependency versions so installs can be reproduced. |
| `pnpm-workspace.yaml` | Declares apps and shared packages as one pnpm workspace. |
| `prettier.config.js` | Shared source-formatting rules. |
| `render.push.yaml` | Optional separate scheduled push-delivery service blueprint. Requires explicit provisioning; the file alone does not run a scheduler. |
| `render.yaml` | Render API deployment blueprint: free Node service, build/start commands and configuration names. |
| `setup.sh` | Original shell environment-file bootstrap helper. Inspect it for your OS; Windows setup does not depend on running it. |
| `turbo.json` | Turborepo task dependencies, caching and environment forwarding. |

## 6. Quick panel answers

- Why is a city not a destination? A city is a search origin; a destination is a curated observing location with its own data and access context.
- What is innovative? The connected observing workflow, local inspectable AI and culturally coherent interface; underlying models/astronomy algorithms are established.
- Why tRPC plus Zod? Shared compile-time contracts reduce client/server drift; runtime validation still checks untrusted input.
- Is there live telescope video? No. SkyView supplies archival survey images.
- Does the AI prove missing detail? No. It denoises conservatively and offers inspection; fidelity needs domain validation.
- Is Honor secure against its owner editing storage? No. It is a private self-reported practice journal.
- Does the existence of an auth route mean login works? No. Provider discovery is scaffolding; complete callback/session/account sync is future work.
- What should we demo? City search/map, selected-site forecast, lunar events/internal details, labelled image restoration/slider/overlays, then one bonus and the test evidence.

See DEMO_GUIDE.md for the full five-minute script and failure fallbacks. Do not put private environment values or credentials into submission files.
