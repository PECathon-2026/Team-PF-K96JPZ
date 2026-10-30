"""Build a readable feature explanation and an inventory of every versioned project file."""
from pathlib import Path
import subprocess

ROOT = Path(__file__).resolve().parents[2]
P = Path(__file__).resolve().parent
descriptions = {}
def group(prefix, rows):
    for name, meaning in rows.items():
        descriptions[prefix + name] = meaning

group('', {
    '.env.example': 'Environment-variable template. Lists required configuration names; real credentials belong in ignored environment files.',
    '.gitignore': 'Prevents dependencies, build artifacts and private environment files from entering Git.',
    '.npmrc': 'pnpm/npm installation settings for this workspace.',
    '.vscode/settings.json': 'Shared editor configuration; does not implement application behavior.',
    'README.md': 'Repository overview and setup entry point; detailed completion notes document later features.',
    'package.json': 'Root workspace commands for build, development, database operations, lint and formatting.',
    'pnpm-lock.yaml': 'Locks resolved dependency versions so installs can be reproduced.',
    'pnpm-workspace.yaml': 'Declares apps and shared packages as one pnpm workspace.',
    'prettier.config.js': 'Shared source-formatting rules.',
    'turbo.json': 'Turborepo task dependencies, caching and environment forwarding.',
    'docker-compose.yml': 'Local development infrastructure, including PostgreSQL; not the hosted Neon database.',
    'render.yaml': 'Render API deployment blueprint: free Node service, build/start commands and configuration names.',
    'render.push.yaml': 'Optional separate scheduled push-delivery service blueprint. Requires explicit provisioning; the file alone does not run a scheduler.',
    'setup.sh': 'Original shell environment-file bootstrap helper. Inspect it for your OS; Windows setup does not depend on running it.',
    'ops/render-start.mjs': 'Loads allowed deployment secrets, runs migrations and the idempotent seed, then starts the compiled API.',
    'ops/push-cron.mjs': 'Calls the protected push delivery procedure; supports periodic invocation or local watch mode.',
})
group('apps/api/', {
    'src/index.ts': 'API process entry point; starts the Express server on the configured port.',
    'src/server.ts': 'Creates Express, health checks, tRPC transport, OpenAPI JSON and Scalar API documentation.',
    'src/env.ts': 'Validates backend runtime configuration such as port, mode and base URL.',
    'tsup.config.ts': 'Bundles the TypeScript API and workspace code into executable server output.',
})
group('apps/web/', {
    'README.md': 'Frontend development notes.',
    'components.json': 'shadcn component generator paths, style and utility configuration.',
    'env.js': 'Validates frontend/server environment configuration; production API_URL must use HTTPS.',
    'eslint.config.js': 'Frontend lint configuration using shared Next.js/React rules.',
    'next.config.js': 'Next.js configuration, including same-origin /trpc proxy rewrites to the backend.',
    'postcss.config.mjs': 'Tailwind/PostCSS stylesheet processing configuration.',
    'vercel.json': 'Vercel framework, region, install and build commands for the monorepo frontend.',
    'hooks/use-mobile.ts': 'Reusable hook that reports a mobile-sized viewport.',
    'providers/global.tsx': 'Installs React Query, tRPC, light/dark mode, motif palette, in-app moon reminders and toast notifications.',
    'providers/palette.tsx': 'Stores and applies the four motif palettes independently of light/dark mode.',
    'trpc/client.ts': 'Typed React hooks bound to the shared tRPC router.',
    'trpc/create-client.ts': 'Builds the HTTP or streaming tRPC transport; browser requests use the web origin.',
    'trpc/server.ts': 'Typed programmatic API clients for non-hook/server-side use.',
    'scripts/prepare-spirit-lens.mjs': 'Copies ONNX browser runtime assets into public output before dev/build.',
    'app/layout.tsx': 'Global document wrapper, local fonts, metadata, environment validation, CSS and providers.',
    'app/page.tsx': 'Main Watchtower/Scroll dashboard: city origin, radius, sorting, destination selection, forecasts and feature navigation.',
    'app/events/[id]/page.tsx': 'Dynamic route that opens an event inside this application.',
    'app/spirit-lens/page.tsx': 'Route entry for the Spirit Lens restoration and comparison interface.',
    'app/analysis/page.tsx': 'Signal Observatory CSV controls, synthetic examples, plots, candidate results and export.',
    'app/dojo/page.tsx': 'Displays the device-local observation journal, derived Honor total, badges and JSON export.',
    'app/api/cities/route.ts': 'Same-origin city geocoding route on the web host; validates names, caches results, deduplicates concurrent lookups and reports provider failures.',
    'app/api/skyview/route.ts': 'Fixed-host NASA archival-image proxy with validated parameters, time/size/concurrency limits, cache and overload handling.',
    'app/globals.css': 'Global imports and main dashboard/layout styles.',
    'app/watch-theme.css': 'Semantic colors and shared visual tokens used by components.',
    'app/watch-palettes.css': 'Light/dark color definitions for Ink Wash, Torii, Sakura and Katana palettes.',
    'app/watch-motion.css': 'Animations and reduced-motion behavior.',
    'app/theme-landscape.css': 'Shared Japanese-inspired landscape artwork styling.',
    'app/watchtower-map.css': 'Scroll map, marker glyphs, controls, labels and map layout.',
    'app/moon-tracker.css': 'Moon tracker cards and reminder UI styling.',
    'app/location-search.css': 'City/destination input and suggestion dropdown styling.',
    'app/navigation-hint.css': 'Readable, theme-aware navigation notes displayed on hover or keyboard focus.',
    'app/japanese-text.css': 'English-meaning tooltips for Japanese text.',
    'app/event-details.css': 'Internal event detail, breadcrumb and error-state styling.',
    'app/spirit-lens.css': 'Upload, restoration, comparison, measurement and lens-page layouts.',
    'app/bonuses.css': 'Signal Observatory, Honor journal and shared bonus-page controls/layout.',
    'app/favicon.ico': 'Browser tab/site icon.',
    'app/fonts/GeistVF.woff': 'Locally hosted Geist Sans variable font.',
    'app/fonts/GeistMonoVF.woff': 'Locally hosted Geist Mono variable font.',
})
group('apps/web/components/', {
    'background-alerts.tsx': 'Browser push opt-in, anonymous device ownership, subscription, reminder scheduling, pending jobs, cancellation and disabling.',
    'bonus-shell.tsx': 'Shared header, feature links, palette landscape and content frame for Signals and Honor pages.',
    'celestial-scroll.tsx': 'Lunar/Gregorian calendar navigation, event-type/date filtering, feed status and event list.',
    'event-details.tsx': 'Loads and presents an event with date/source context, calendar export, alerts and observation form.',
    'iss-passes.tsx': 'Loads visible ISS prediction segments for the selected Watchtower destination.',
    'japanese-text.tsx': 'Accessible hover/focus/touch explanations for Japanese characters and phrases.',
    'location-search.tsx': 'Debounced worldwide city and catalogue searches; displays independent results and chooses a search origin or a saved spot.',
    'moon-alert-scheduler.tsx': 'Checks local reminders while the app is open and shows due moonrise toasts. This is separate from closed-app Web Push.',
    'moon-tracker.tsx': 'Moon phase, illumination, rise/set display, in-app reminders and calendar/push options.',
    'navigation-hint.tsx': 'Shared definitions of feature names/meanings and Radix hover/focus tooltips attached to navigation links.',
    'observation-form.tsx': 'Validates a self-reported observation and records one local Honor award per event.',
    'scroll-map.tsx': 'Initializes Leaflet, loads bundled outlines, creates safe marker popups and supports fit/search-this-area controls.',
    'sky-atmosphere.tsx': 'Decorative sky, drifting petals and atmospheric visual elements.',
    'theme-landscape.tsx': 'Reusable SVG motif artwork matching the selected Japanese palette.',
    'theme-toggle.tsx': 'Controls light/dark mode and motif selection.',
    'spirit-lens/spirit-lens.tsx': 'Coordinates image input, worker lifecycle, progress/cancel/error state, restoration settings, candidate details and downloads.',
    'spirit-lens/comparison-view.tsx': 'Interactive before/after divider, zoom/pan, candidate overlays and inspection controls.',
    'spirit-lens/skyview-import.tsx': 'Target/survey/field controls for NASA archival import; keeps source query provenance.',
})
group('apps/web/lib/', {
    'utils.ts': 'Shared class-name utility combining conditional classes and Tailwind conflict resolution.',
    'geocoding.ts': 'Validates worldwide city-provider responses and maps them into a small UI-safe place shape; requests up to 20 name matches.',
    'geocoding.test.ts': 'Tests worldwide query parameters, response mapping, empty/error/malformed data and invalid input without upstream calls.',
    'event-calendar.ts': 'Creates downloadable UTC iCalendar events with escaped text, folded Unicode lines and reminder metadata.',
    'moon-reminders.ts': 'Local reminder validation, storage/event notifications and observer-timezone-aware moonrise messages.',
    'honor-journal.ts': 'Local observation validation, one-award-per-event logic, derived points/badges and cross-tab coordination.',
    'transient-analysis.ts': 'CSV parsing and time-domain/spectral median-MAD screening, uncertainty handling and candidate output.',
    'bonuses.test.ts': 'Signal fixture, CSV edge-case and Honor validation/badge tests.',
    'spirit-lens/model.ts': 'Model identity and integrity hashes, image limits, strength settings and worker message/result types.',
    'spirit-lens/image.ts': 'Checks image headers and size, decodes supported formats, makes bounded previews/synthetic input and exports blobs.',
    'spirit-lens/analysis.ts': 'Luminance, robust source/morphology detection, conservative color-preserving blends and comparison metrics.',
    'spirit-lens/spirit-lens.worker.ts': 'Verifies model assets, runs tiled DnCNN ONNX WASM inference, applies bounded cleanup/deblur and returns measurements/candidates.',
    'spirit-lens/deblur.ts': 'Gaussian PSF blur operator and optional six-iteration Richardson–Lucy deconvolution.',
    'spirit-lens/analysis.test.ts': 'Tests input safety, reflection, edit/source preservation, object candidates and flat-sky behavior.',
    'spirit-lens/deblur.test.ts': 'Tests deconvolution against a known synthetic blurred-source fixture.',
})
group('apps/web/public/', {
    'push-worker.js': 'Service worker that displays received push messages and opens a safe internal application URL when clicked.',
    'world-outline.geojson': 'Bundled approximate geographic boundaries, letting the scroll map render without a commercial tile API.',
    'WORLD_OUTLINE_LICENSE.txt': 'Attribution/license information for bundled geographic outlines.',
    'models/dncnn/.gitattributes': 'Treats model binary files appropriately in Git.',
    'models/dncnn/README.md': 'DnCNN origin, export/version and usage/provenance notes.',
    'models/dncnn/LICENSE.txt': 'Upstream model license; retain it when redistributing assets.',
    'models/dncnn/dncnn.onnx': 'ONNX graph defining the pretrained DnCNN computation.',
    'models/dncnn/dncnn.data': 'External pretrained tensor/weight data loaded by the ONNX graph.',
})
for asset in ['file-text.svg','globe.svg','next.svg','turborepo-dark.svg','turborepo-light.svg','vercel.svg','window.svg']:
    descriptions['apps/web/public/' + asset] = 'Starter/template vector graphic; not an astronomy data source or a core feature implementation.'
group('packages/trpc/', {
    'client/index.ts': 'Exports inferred router input/output types and tRPC client helpers.',
    'server/index.ts': 'Combines feature routers into the shared server router and exports context/types.',
    'server/context.ts': 'Current request-context placeholder. It does not establish authenticated user sessions.',
    'server/trpc.ts': 'Creates the typed tRPC instance, OpenAPI metadata support, router and public procedure helpers.',
    'server/schema.ts': 'Shared Zod and request-schema helpers for API procedures.',
    'server/services/index.ts': 'Creates the shared UserService instance used by authentication-provider discovery.',
    'server/utils/path-generator.ts': 'Builds consistent prefixed OpenAPI endpoint paths.',
    'server/routes/watchtower/route.ts': 'Validates place/radius queries and exposes catalog search, locations, ranking, weather and moon conditions.',
    'server/routes/celestial/route.ts': 'Validates month/lunar/event/ISS requests and exposes celestial services.',
    'server/routes/push/route.ts': 'Validates push device, reminder and delivery procedure inputs; forwards ownership and scheduler credentials to service checks.',
    'server/routes/auth/route.ts': 'Lists configured OAuth providers. This is scaffolding, not a completed sign-in/callback/session system.',
    'server/routes/health/route.ts': 'Simple typed health procedure with an OpenAPI mapping.',
})
group('packages/services/', {
    'env.ts': 'Service-layer runtime environment validation, including optional Google OAuth configuration.',
    'clients/google-oauth.ts': 'Google OAuth URL/client helper used by provider-discovery scaffolding.',
    'user/index.ts': 'Lists Google sign-in as available only when its configuration is present; does not implement full authentication.',
    'user/model.ts': 'Zod response definitions/types for available authentication methods.',
    'watchtower/index.ts': 'Reads the destination catalogue, computes nearby distances, ranks forecasts and transactionally caches weather/score pairs.',
    'watchtower/weather.ts': 'Open-Meteo forecast adapter, next-night selection, weather-only Night Honor Score and Haversine distance.',
    'watchtower/weather.test.ts': 'Weather score bounds, bad/null/no-night payloads, future selection, unit conversion and distance/date-line tests.',
    'watchtower/search.ts': 'Searches stored destination names; catalogOnly avoids backend geocoding. Legacy combined city lookup remains for compatible callers.',
    'watchtower/moon.ts': 'Fetches/caches location-specific moon conditions and integrates stored rise/set data.',
    'watchtower/moon-model.ts': 'Parses USNO moon payloads, validates requested dates/illumination and preserves missing polar rise/set as null.',
    'watchtower/moon.test.ts': 'Moon UTC/parsing, polar/malformed data and timezone-aware reminder tests.',
    'celestial/index.ts': 'Coordinates normalized provider feeds, event upserts/feed membership, refresh policy, lunar intervals and event details.',
    'celestial/providers.ts': 'Normalizes external phase/launch data, UTC month intervals, source IDs and provider status.',
    'celestial/providers.test.ts': 'Provider/date/ID/pagination validation and calendar-export edge-case tests.',
    'celestial/calculated.ts': 'Astronomy Engine eclipses, explicitly approximate meteor windows and Japanese lunisolar calendar calculations.',
    'celestial/calculated.test.ts': 'Known eclipse and lunar-date fixtures, meteor estimates and ISS invalid/bounded-prediction tests.',
    'celestial/iss.ts': 'Fetches fresh CelesTrak TLEs, runs SGP4 propagation and filters visible fully sunlit ISS segments for an observing site.',
    'celestial/himekuri.d.ts': 'TypeScript declarations for the Japanese calendar library import.',
    'alerts/index.ts': 'Device ownership hashes, safe push endpoints, reminder jobs, claim leases, retries, Web Push and expired-subscription cleanup.',
    'alerts/alerts.test.ts': 'Tests unsafe push endpoints and scheduler credential rejection.',
    'alerts/ownership.integration.ts': 'Database integration checks for anonymous device/job isolation and deletion using dummy subscriptions; not a physical push receipt test.',
    'alerts/generate-keys.cjs': 'Generates VAPID/scheduler credentials into ignored local configuration; refuses to overwrite existing credentials.',
})
group('packages/database/', {
    'IMPLEMENTATION.md': 'Database design explanation and schema implementation notes.',
    'env.ts': 'Validates DATABASE_URL without placing it in client code.',
    'index.ts': 'Creates the PostgreSQL/Drizzle client and exports query helpers.',
    'schema.ts': 'Re-exports table definitions as the complete schema.',
    'seed.ts': 'Idempotently populates initial locations and supporting catalogue/reference data.',
    'drizzle.config.ts': 'Drizzle schema, migrations directory and database configuration.',
    'models/user.ts': 'User profile/account schema foundation, including optional home coordinates and timezone.',
    'models/watchtower.ts': 'Location, weather snapshot, Night Honor Score and related location schema/constraints.',
    'models/events.ts': 'Moon, rise/set, ISS, event type, celestial event and related event schema.',
    'models/event-feed.ts': 'Tracks provider feed membership and refresh attempts/successes.',
    'models/push.ts': 'Persistent anonymous devices and alert jobs with ownership hashes, claim/attempt/sent timestamps and indexes.',
    'models/honor.ts': 'Schema foundation for preferences, server Honor ledger and badges. Current user-facing journal uses local storage instead.',
    'drizzle/0000_dusty_morg.sql': 'Initial user-table migration.',
    'drizzle/0001_celestial_foundation.sql': 'Creates core location, weather, event and Honor/preference foundation tables and constraints.',
    'drizzle/0002_celestial_feeds.sql': 'Adds provider feed membership and synchronization bookkeeping.',
    'drizzle/0003_moon_conditions.sql': 'Adds cached phase/illumination/fetch timestamps to location rise/set data.',
    'drizzle/0004_amused_kingpin.sql': 'Adds persistent push devices and scheduled delivery jobs.',
    'drizzle/meta/_journal.json': 'Drizzle migration order/version bookkeeping; not a user observation journal.',
})
for i in range(5):
    descriptions[f'packages/database/drizzle/meta/{i:04d}_snapshot.json'] = f'Drizzle-generated schema snapshot after migration {i:04d}; used for future schema diffs, not runtime feature code.'
group('packages/logger/', {'index.ts': 'Shared Winston console logger, readable in development and structured in deployment.', 'env.ts': 'Validates logger level and environment settings.'})
group('packages/typescript-config/', {'base.json':'Shared strict TypeScript compiler defaults.', 'nextjs.json':'TypeScript defaults specialized for Next.js apps.', 'node.json':'TypeScript defaults specialized for Node packages.'})
group('packages/eslint-config/', {'README.md':'Shared lint configuration usage notes.', 'base.js':'Base JavaScript/TypeScript lint rules.', 'next.js':'Next.js-specific lint rules.', 'react-internal.js':'Shared React component/hook lint rules.'})
group('docs/', {'API_SETUP.md':'Data-provider setup, URLs and configuration instructions.', 'BONUS_FEATURES.md':'Archive, signal-analysis and Honor behavior and limits.', 'COMPLETION_NOTES.md':'Implemented remaining requirements, push prerequisites and practical constraints.', 'PRODUCTION.md':'Deployment setup, environment wiring and operational notes.', 'SPIRIT_LENS.md':'Local AI processing, model provenance and image-restoration safeguards.'})
group('docs/demo/', {
    '.gitignore': 'Excludes generated recordings, narration audio and frame outputs from Git.',
    'README.md': 'Three-minute recording timeline, truthful demo scope and reproduction instructions.',
    'demo-plan.json': 'Seven timed scenes and the generated English narration text, totaling 180 seconds.',
    'prepare-narration.ps1': 'Uses local Windows speech synthesis, measures each WAV and fits narration to scene allocations.',
    'record-demo.mjs': 'Records only an isolated public-app browser, performs the demo, and exports captioned H.264/AAC video plus transcript/provenance.',
})
group('docs/presentation/', {
    '.gitignore':'Excludes generated slide PNG previews from Git.',
    'README.md':'Presentation contents and generation/export instructions.',
    'READINESS.md':'Detailed historical rubric audit with 28-test baseline, requirement mapping and limitations.',
    'DEMO_GUIDE.md':'Five-minute demonstration, fallbacks and panel questions.',
    'Tsukuyomi-Watch-Judging-Deck.pptx':'Original detailed 17-slide editable judging deck with speaker notes and 28-test audit baseline.',
    'Tsukuyomi-Watch-Judging-Deck.pdf':'PDF export of the original 17-slide deck.',
    'Tsukuyomi-Watch-8-Slide-Pitch.pptx':'New concise eight-slide project explanation and pitch with speaker notes.',
    'Tsukuyomi-Watch-8-Slide-Pitch.pdf':'Portable PDF of the eight-slide pitch.',
    'Tsukuyomi-Watch-Project-Notes.md':'This feature explanation and per-file codebase guide in Markdown.',
    'Tsukuyomi-Watch-Project-Notes.txt':'Plain-text copy of this guide for opening without a Markdown editor.',
    'build-deck.cjs':'Reproducibly generates the original detailed PowerPoint using PptxGenJS.',
    'build-pitch.cjs':'Generates the separate eight-slide project pitch using native editable shapes/text and real UI screenshots.',
    'build-notes.py':'Generates this feature overview and verifies that every tracked/nonignored deliverable has a file description.',
    'export-deck.ps1':'Uses installed PowerPoint in the background to export the detailed deck to PDF and slide PNGs.',
    'export-pitch.ps1':'Exports the eight-slide pitch to PDF and slide PNG previews using PowerPoint.',
    'capture-demo.mjs':'Isolated headless Edge script capturing actual production UI and a labelled synthetic image-restoration result.',
    'verify-deck.py':'Checks the detailed deck ZIP, slide/notes counts, PDF signature and shape bounds.',
    'test-results.txt':'Original recorded 28-case automated test transcript; historical evidence.',
    'test-results-current.txt':'Updated 31-case transcript including three city-geocoding regression cases.',
    'fixtures/light-curve.csv':'Labelled synthetic light-curve demo data with an injected bright measurement.',
    'fixtures/spectrum.csv':'Labelled synthetic spectrum with positive and negative injected features.',
    'assets/live-evidence.json':'Timestamp and displayed measurements from the actual synthetic browser restoration run.',
})
for name in ['calendar','hero','lens','signals','watchtower']:
    descriptions[f'docs/presentation/assets/{name}.png'] = f'Actual production {name} screenshot, used as presentation evidence; not a design mockup.'

# Shared configuration and reusable component library still get individual entries.
ui = {
 'accordion':'Expandable stacked sections', 'alert-dialog':'Modal confirmation dialog', 'alert':'Inline status/warning message',
 'aspect-ratio':'Fixed image/media proportions', 'avatar':'Profile image/fallback', 'badge':'Compact status label',
 'breadcrumb':'Hierarchical navigation trail', 'button-group':'Grouped button layout', 'button':'Reusable styled button',
 'calendar':'Generic date-picker component (the celestial lunar calendar has its own feature implementation)',
 'card':'Reusable content panel', 'carousel':'Scrollable item carousel', 'chart':'Recharts presentation helpers',
 'checkbox':'Checked/unchecked input', 'collapsible':'Expandable content block', 'command':'Command/search menu',
 'context-menu':'Right-click menu', 'dialog':'Modal dialog', 'drawer':'Slide-in panel', 'dropdown-menu':'Action dropdown',
 'empty':'Empty-state presentation', 'field':'Labeled field layout/feedback', 'form':'Form context and validation presentation',
 'hover-card':'Hover/focus information card', 'input-group':'Grouped input/accessory layout', 'input-otp':'One-time-code input',
 'input':'Styled text input', 'item':'Reusable list item layout', 'kbd':'Keyboard-shortcut key label', 'label':'Accessible form label',
 'menubar':'Desktop-style menu bar', 'navigation-menu':'Expandable navigation menu', 'pagination':'Page navigation controls',
 'popover':'Anchored floating panel', 'progress':'Progress indicator', 'radio-group':'Single-choice radio inputs',
 'resizable':'Resizable split panels', 'scroll-area':'Styled scrollable viewport', 'select':'Styled selection menu',
 'separator':'Visual section divider', 'sheet':'Side-sheet dialog', 'sidebar':'Generic sidebar building blocks',
 'skeleton':'Loading placeholder', 'slider':'Range slider', 'sonner':'Toast notification host', 'spinner':'Loading spinner',
 'switch':'On/off control', 'table':'Table presentation primitives', 'tabs':'Tabbed content', 'textarea':'Multiline text field',
 'toggle-group':'Related toggle controls', 'toggle':'Pressed/unpressed control', 'tooltip':'Radix accessible tooltip primitives',
}
for name, text in ui.items():
    descriptions[f'apps/web/components/ui/{name}.tsx'] = text + '. Shared UI primitive; its presence alone does not mean a separate product feature exists.'

header = '''# Tsukuyomi Watch — feature and file notes

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

'''

files = subprocess.check_output(['git','ls-files','--cached','--others','--exclude-standard'], cwd=ROOT, text=True).splitlines()
files = sorted(set(files) | {
    'docs/presentation/Tsukuyomi-Watch-Project-Notes.md',
    'docs/presentation/Tsukuyomi-Watch-Project-Notes.txt',
})
def explain(file):
    if file in descriptions:
        return descriptions[file]
    leaf = Path(file).name
    if leaf == 'package.json':
        return 'Package identity, workspace exports, dependencies and runnable scripts for ' + str(Path(file).parent) + '.'
    if leaf == 'tsconfig.json':
        return 'TypeScript compiler/project settings for ' + str(Path(file).parent) + '.'
    if leaf == '.eslintrc.cjs':
        return 'Package lint rules extending shared repository configuration.'
    if leaf == '.gitignore':
        return 'Excludes local/generated files in this directory from version control.'
    raise ValueError('Missing file description: ' + file)

parts=[header]
previous=None
for file in files:
    section = '/'.join(file.split('/')[:2]) if file.startswith(('apps/','packages/')) else file.split('/')[0] if '/' in file else 'Root configuration'
    if section != previous:
        parts.append('\n### ' + section + '\n\n| File | Responsibility |\n| --- | --- |\n')
        previous=section
    parts.append(f'| `{file}` | {explain(file)} |\n')
parts.append('''
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
''')
content=''.join(parts)
for extension in ['md','txt']:
    (P / ('Tsukuyomi-Watch-Project-Notes.' + extension)).write_text(content, encoding='utf-8')
print(f'Wrote feature notes and descriptions for {len(files)} files.')
