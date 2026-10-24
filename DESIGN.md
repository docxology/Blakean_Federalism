# Blakean Federalism research workbench — design contract 0.3.0

23 October 2026. Design-research production for root to integrate into `DESIGN.md` before UI code. This is a proposed implementation contract, not an implementation, usability study, scientific audit or acceptance verdict. The only authored deliverables from this task are this file and `design-030-inspection.json` beside it. Existing project edits belong to their current owners.

Reference branch: **concrete manuscript reference**. All four full `corrected-page-01.png` through `corrected-page-04.png` graphical abstracts were viewed; the cover is page 1 and the warrant sequence on page 2 is the principal interior reference. `tools/render_manuscript.py` and the private article and rights appendix were read in full. No new brand, generated Blake imagery, React, framework setup, decorative animation or runtime network dependency is part of this contract. Print geometry is evidence of the existing language; responsive geometry below is an intentional adaptation.

The frontend router and all ten requested routed references were read in full. Its designpowers README additionally routed to `routing.md` and `orchestration.md`; both were read in full. StyleGallery's catalog, exact `page-grid` and `tab-strip` contracts, and beui's actual `input` and `bouncy-accordion` sources were fetched and read. These inform structure and mechanics only. No third-party component or unlicensed StyleGallery prose is copied. Research links and inspected file identities are recorded in section 8 and the companion inspection record.

## 1. Atmosphere & Identity

A working research folio: white paper on a warm desk, dark teal type, pale green reading surfaces and restrained rust caveats. The recognizable idea is the manuscript's separation of an assertion, its warrant and its limit, expressed through typography and adjacent evidence. The researcher should be able to move from a number or check to the record that qualifies it without encountering a congratulatory score, marketing hero or ornamental image. The same quiet hierarchy carries into dark mode as muted paper-like layers, without luminous accents.

### Users, jobs and information order

| Research situation | Task | Success condition for later QA |
| --- | --- | --- |
| Corpus researcher checking an apparent pattern | Find a saved query, restrict source plane and role, inspect occurrences and coverage | Can name exactly what was searched and the denominator; cannot mistake source units for unique works |
| Political-theory researcher comparing stipulated alternatives | Read a case's inputs, all 15 predicates and missing or insufficient warrants | Can distinguish an evaluated predicate from a legal or empirical conclusion |
| Close reader tracking a quotation | Read the quotation, locator, source link, context and reading/rights ceiling | Can identify the edition/source object and omitted lines without relying on a verification badge |
| Keyboard/screen-reader user, or low-vision reader at high zoom | Perform those same three tasks | No hover-only evidence, hidden focus, lost selection or sideways primary-content scrolling |

Document order: skip link; compact masthead; local/private and dataset notice; Corpus/Cases/Sources navigation; active view; interpretation/method disclosure; provenance and font-license disclosure. The active view places its heading and scope sentence before controls, then results, then detailed method. Important caveats and actual denominators are visible beside results, not only in a footer.

Masthead text: **Blakean Federalism**; secondary line **Research workbench · 0.3.0**. Visible notice: **Local / private research. This document contains aggregate results, synthetic cases and selected quotations. Source links open online only when followed.** This describes intended behavior; root must verify it. A small identity block shows generator version, data version, query method, generation time and input fingerprint. Do not replace the document identity with a large KPI strip.

### Content and truth boundaries

- **Corpus** operates on 20 saved query groups, including `negative_control`, over 180 query/plane/role aggregate cells. The search label is **Find a saved query**; helper text is **Filter saved query names and variants. This does not run a new search of the corpus.** Display each group's exact variants. Do not call the control full-text search.
- **Cases** contains ten synthetic alternative records, paired within five scenario families A–E. Preserve all ten decision IDs. Say **10 synthetic alternatives in 5 scenario families**, avoiding a new claim that ten independent empirical scenarios were studied. Each alternative exposes all 15 explicit check results.
- **Sources** contains exactly Q01–Q13 from the bound quotation specification. Include their source URLs, locators, segment order, context and ceilings. These are selected quotations, not the complete corpus or a claim to have read every cited work.
- Preserve separation among input identity, quotation-selection verification, stipulated rule checks, scholarly reading and rights advice. None becomes a green legitimacy or freedom badge.
- Embed no restricted full texts, full concordance contexts, modern PDF bodies, raw XML, complete ASU source HTML, provider images or manuscript page screenshots. The approved images are design references; they are not workbench assets. Links and bounded rights metadata are sufficient here.

### Dataset identity contract

The generator supplies a small immutable manifest: workbench version; schema versions; corpus capture/projection/index SHA-256 values; query-file hash and matching-method ID; aggregate-data hash; case-input and explicit-assessment hashes; assessor-source hash; quotation-spec and consumed-source hashes; generation timestamp; record cardinalities; plane/role census and its binding. Manifest fields use relative input names, not private absolute workstation paths. Show a short fingerprint inline and the complete hash plus algorithm in a wrapping **Dataset and input identity** disclosure. Never substitute a screenshot timestamp for input identity or label old data current merely because it loaded.

Observed corpus identity: index SHA-256 `8f6cfd5ab62403a50ffdb2c31925fb13daf2e2b226e405334e1a42e03d62b699`; projection SHA-256 `dbab64e36cf44dbf15965e1fed27a33d062a7da0067b1ec3b15699b342c42e0d`. These describe the inspected corpus, not a requirement to freeze all future exports to this snapshot. Root must bind the actual export inputs and display any changed data/version explicitly.

## 2. Color

### Extracted anchors versus intentional adaptations

`render_manuscript.py` defines `INK #173737`, `TEAL #2a7069`, `RUST #995336`, `PALE #edf3f0`. White paper is visible in the four inspected renders and is the unpainted page background. Those are the light-theme anchors. The warm canvas, gray rules, control/state ramp, all dark values and focus treatment below are screen adaptations. Preserve the anchors rather than introducing a separate product palette.

| CSS token | Light | Dark | Role / provenance |
| --- | --- | --- | --- |
| `--surface-canvas` | `#f8f7f2` | `#121c1b` | Adapted outer desk / full-page background |
| `--surface-paper` | `#ffffff` | `#192624` | Observed white paper; adapted dark reading layer |
| `--surface-tonal` | `#edf3f0` | `#20312e` | Exact PALE in light; methods and evidence backgrounds |
| `--surface-hover` | `#e7eeeb` | `#283d38` | Adapted control hover |
| `--surface-selected` | `#dce9e4` | `#304a43` | Adapted current view / selected control wash |
| `--surface-pressed` | `#d8e6e0` | `#355248` | Adapted transient press; primary-ink labels only |
| `--surface-caution` | `#f4e8df` | `#3b2c26` | Adapted rust wash for located missing-warrant text |
| `--text-primary` | `#173737` | `#edf3f0` | Exact INK / PALE anchors repurposed in dark |
| `--text-secondary` | `#4d6260` | `#b5c7c0` | Adapted readable metadata, never faint gray |
| `--accent-teal` | `#2a7069` | `#90c9ba` | Exact TEAL; link and small section-label ink |
| `--accent-rust` | `#995336` | `#e2b093` | Exact RUST; qualified caution, never rejection-by-color alone |
| `--rule-neutral` | `#d6d6d0` | `#4b4d48` | Adapted neutral decorative hairline |
| `--control-boundary` | `#68756f` | `#9aada4` | Adapted control outlines with nontext contrast |
| `--focus-ring` | `#2a7069` | `#90c9ba` | Adapted use of accent; keyboard-only ring |
| `--button-fill` | `#2a7069` | `#90c9ba` | Optional single primary action, if one is needed |
| `--button-ink` | `#ffffff` | `#121c1b` | Contrast pair for that fill |

All component colors reference these semantic variables. `transparent`, `currentColor` and system colors in forced-colors mode are browser mechanics, not extra palette choices. No gradients, colored edge bars, accent tab underlines, card accent outlines, inset accent stripes, blur, sheen, texture assets or decorative shadows. Inline source links keep an ordinary text underline; the ban on accent underlines concerns ornamental selected-state rules, not link affordance. Use a neutral underline for links if its color is set separately.

### State and contrast constraints

- Default controls: paper fill, primary ink, one neutral control-boundary hairline. Hover: hover wash. Selected: selected wash, bold label and a visible **Selected** label where context alone would be ambiguous. Pressed: pressed wash and primary ink. Focus-visible ring remains present during all states.
- Text-only links use teal at rest; during press on a pressed wash, switch to primary ink. Rust is reserved for text on paper/tonal/caution backgrounds; do not put rust text on pressed washes. Disabled controls retain primary/secondary readable text, a native disabled state and a nearby reason; no blanket low-opacity wrapper.
- Calculated sRGB contrast for the declared combinations: primary ink across ordinary and pressed layers is at least **9.96:1 light / 7.62:1 dark**; secondary ink at least **5.05:1 / 4.85:1**. Teal on paper is **5.80:1 / 8.37:1**. Rust on caution is **4.79:1 / 6.90:1**. Primary button pair is **5.80:1 / 9.32:1**. Control-boundary on the darkest pressed layer is **3.74:1 / 3.62:1**. These are token calculations, not a rendered accessibility result. Root must verify actual combinations, native controls, links and focus against computed styles.
- The neutral decorative rule is not sufficiently contrasting to identify a control by itself; use `--control-boundary` on inputs/buttons. Required results never rely on a faint divider or color alone.
- Theme control: native select labeled **Appearance**, options **System**, **Light**, **Dark**. Default System follows `prefers-color-scheme`; explicit choice overrides it for the current document session. No storage permission or persistent browser storage is required. Set the matching `color-scheme` for native inputs. A reload returns to System.

## 3. Typography

The renderer actually uses **Bitstream Vera sans**, including bold and italic, not an editorial serif. Preserve that fact. Editorial character comes from the measured headings, quoted lines, restrained upper-case labels and breathing room; do not invent a serif brand.

| CSS token | Value | Use |
| --- | --- | --- |
| `--font-reading` | `"Blakean Vera", "Bitstream Vera Sans", "DejaVu Sans", sans-serif` | Local embedded Vera, all reading and controls |
| `--font-code` | `ui-monospace, "SFMono-Regular", Consolas, monospace` | Full hashes and machine IDs only; intentional second-family adaptation |
| `--text-title` | `clamp(1.5rem, 1.125rem + 1.5vw, 2rem)` | Compact workbench title; 24–32 CSS px at default root |
| `--text-section` | `1.375rem` | View heading, 22 px |
| `--text-subheading` | `1.125rem` | Case / source title, 18 px |
| `--text-body` | `1rem` | Main prose and input text, 16 px |
| `--text-meta` | `0.875rem` | Table labels, locators, metadata, 14 px minimum |
| `--weight-regular` | `400` | Body |
| `--weight-strong` | `700` | Titles, table headers, selected labels; use actual bold face |
| `--leading-title` | `1.2` | Titles |
| `--leading-ui` | `1.45` | Controls and compact data |
| `--leading-reading` | `1.6` | Quotations, descriptions, caveats |
| `--tracking-title` | `-0.015em` | Workbench / section heading only |
| `--tracking-label` | `0.04em` | Short overlines only |
| `--tracking-body` | `0` | Body, data, IDs and locators |
| `--measure-reading` | `68ch` | Long explanations and quotation measure |
| `--measure-caution` | `60ch` | Short interpretation notices |

Embed the three unmodified local TTF faces, regular/bold/italic, as data URLs in the generated file, with internal family name `Blakean Vera` and their correct weight/style descriptors. Include the inspected font copyright/permission text in a **Font license** disclosure; no CDN or external font file. Do not subset or modify the fonts under the Vera names. The three available font files total 188,332 bytes before base64, so faithful self-contained typography fits this document's budget without a new font toolchain. A fallback remains for font-load failure or user font overrides; it is a fallback to test, not the intended appearance. Do not disable user styles or text scaling to force fidelity.

Use italic Vera sparingly for selected quotation presentation; longer verse may remain regular for legibility. Preserve line and segment boundaries, with natural wrapping on narrow screens. A wrapped verse line uses a small hanging indent derived from `--space-4`; it never forces a horizontal scroller. Record noncontiguous omissions as editorial text outside the quoted wording. Use tabular numeric figures for counts and right alignment at wide widths. Do not shrink hash text below 14 px; wrap it instead. All IDs/URLs use `overflow-wrap:anywhere` and can be selected/copied in full. No ellipsis that destroys the only visible locator.

## 4. Spacing & Layout

### Complete spacing, sizing and responsive tokens

All numeric design intent below is tokenized. Raw `auto`, percentages, intrinsic grid keywords, logical properties, `min()`, `max()` and viewport units remain mechanics. Root default font size is left at the browser preference; pixel equivalents are explanatory only.

```css
:root {
  --space-0: 0;
  --space-1: .25rem;
  --space-2: .5rem;
  --space-3: .75rem;
  --space-4: 1rem;
  --space-5: 1.25rem;
  --space-6: 1.5rem;
  --space-8: 2rem;
  --space-10: 2.5rem;
  --space-12: 3rem;
  --content-max: 76rem;
  --gutter-compact: 1rem;
  --gutter-medium: 1.5rem;
  --gutter-wide: 2rem;
  --control-min-block: 2.75rem;
  --control-padding-inline: .75rem;
  --field-min-inline: 12rem;
  --query-min-inline: 16rem;
  --column-wide-metadata: 16rem;
  --number-min-inline: 7rem;
  --border-width: 1px;
  --focus-width: 3px;
  --focus-offset: 3px;
  --radius-control: .25rem;
  --radius-surface: .5rem;
  --radius-none: 0;
  --icon-size: 1rem;
  --stroke-icon: 2;
  --shadow-none: none;
  --motion-duration: 0ms;
  --motion-easing: linear;
  --z-base: 0;
  --z-focus: 1;
}
```

Media-query thresholds are documented constants (custom properties cannot directly substitute into native media-query conditions): **compact below 40rem**, **medium 40rem to below 64rem**, **wide at least 64rem**. Name them by layout purpose, not device. `--gutter-compact/medium/wide` changes at these thresholds. No fixed page height or constrained vertical panes.

### Responsive composition and scroll ownership

Adopt StyleGallery **page-grid** for aligned margins and central content, and **tab-strip** for peer navigation. Adaptation: the browser document owns **all vertical scrolling**; no sidebar, floating toolbar, independently scrolling case list, sticky masthead or panel-height scroll trap. The page's width ceiling is `--content-max`, the content track can shrink to zero, and every grid/flex child that contains text has `min-inline-size:0`. Use ordinary block flow if grid is unsupported. Do not set `overflow-x:hidden` on the body to conceal defects.

| Layout state | Composition |
| --- | --- |
| Wide | Compact masthead: title left, Appearance control right. Identity follows as a wrapping definition list. Three same-size view controls. Corpus form is a wrapping cluster: expanding query field, plane select, role select, Clear search, Reset filters. Results use a semantic table. Cases stack as ten open-layout articles; each article can place its input definition list in a 16rem column beside checks, but only while the check area remains readable. Source entries can place short locator metadata beside a flexible quotation column. |
| Medium | Masthead and controls wrap naturally. Identity uses two definition columns if they fit. Cases and Sources return to one primary reading column. Corpus still uses a table when its real content fits; the explicit compact transformation below begins below 40rem. |
| Compact | One vertical stack, 16 px-equivalent gutters, title above Appearance. View controls remain visible, equal stature, wrapping if needed. Search is full width; plane and role may share a row only if each is at least `--field-min-inline`, otherwise stack. Reset/clear wrap without compressing tap targets. Corpus cells become labeled records, not a shrunken wide table. All case and quotation detail flows inline. |

The underlying Corpus representation is one semantic table of query/plane/role rows. Below 40rem, present its rows as stacked labeled records with explicit **Query**, **Plane**, **Role**, **Occurrences**, **Matched source units** and **Coverage** labels. Retain actual header associations and table roles if CSS changes the table display; redundant visual labels are hidden from the accessibility tree. Do not rely on CSS-generated labels as the sole accessible labels. Root must exercise the resulting accessibility tree; if the browser loses table semantics, use a genuine definition-list renderer with only one representation active/exposed and matching data. Never expose duplicate desktop/mobile controls or duplicate focus targets.

At every width the page remains text-first and content-height driven. Alignment comes from shared grid tracks, not fixed absolute positioning. Prose stays within `--measure-reading`; dense numeric data may occupy the full track. Put `overflow-wrap:anywhere` on URLs/hashes, use `white-space:normal` on prose, and preserve full link targets. No scrollable `<pre>` element for record data. Opening a disclosure increases the document normally.

### Corpus denominator and aggregation contract

Read-only SQL against the inspected hash-matching index produced this joint source-unit census. Marginal plane/role totals alone cannot supply these intersections.

| Plane | Primary | Editorial / mixed | Unverified | Plane total |
| --- | ---: | ---: | ---: | ---: |
| Reading | 199 | 0 | 341 | 540 |
| Erdman | 0 | 796 | 0 | 796 |
| XML | 0 | 4 | 727 | 731 |
| Role total | 199 | 800 | 1,068 | 2,067 |

For one query group and eligible plane/role cell, show integer occurrences, integer matched source units `m`, denominator `n`, and coverage `m / n` with an optional one-decimal percentage. The complete fraction stays visible, including in compact mode and empty results. The denominator means **all indexed source units in this cell**, not units that matched the query. Example for `states`, Reading / Primary: **264 occurrences; 60 / 199 source units (30.2%)**. This is a local data example, not a literary result.

- `n > 0, m = 0`: display **0 occurrences; 0 / n source units (0.0%)**.
- `n = 0`: display **N/A — no source units in this plane/role**, including occurrence and coverage fields. Never show 0%, `0 / 0`, NaN, a blank cell or a colored zero that implies a search was possible.
- Positive matches with `n = 0`, `m > n`, negative/noninteger values, duplicate query/plane/role keys, missing census, unknown enums or a missing expected cell are invalid inputs. Do not silently coerce them into zero or N/A.
- Filters constrain rows by a single plane and a single role, with **All planes / All roles** options. Query search filters group ID and literal variant labels case-insensitively after trimming. Its match is a display filter, not the corpus matching algorithm. No regular expression execution, semantic expansion or ranking.
- Blank or whitespace-only search restores all 20 saved groups for the current plane/role filters. **Clear search** empties only that field. **Reset filters** clears search and resets plane/role to All while remaining in Corpus; it does not change theme or other views' disclosures. Both are idempotent.
- Each query's counts retain the recorded explicit whole-word variant search. Never recompute corpus occurrences from text visible in the HTML. Do not sum matched-source counts across different queries or average cell percentages into an overall coverage figure. The initial version has no grand multi-query coverage KPI. If one query's disjoint cells are combined in a future version, disclose the exact combined population and sum eligible numerators/denominators, not percentages.
- Status text reports **N of 20 query groups; R aggregate cells shown**; distinguish zero visible query groups from a query present with zero occurrences, and from structural N/A.

## 5. Components

Build **three reusable primitives** in a separate state harness first. These are anatomy/behavior contracts, not React components. Native HTML, small CSS and plain JavaScript are sufficient. Layout helpers (stack, cluster, content-limiter) stay separate from their visual styling. Required states below include explicitly nonapplicable states; do not create fake spinners, clickable data tiles or disabled evidence just to fill a gallery.

### Primitive 1 — Research control

**Structure:** persistent label; native input/select/button or semantic view-tab button; optional helper/error text with stable ID; native or textual selected state. Variants: query input, filter select, Appearance select, Clear/Reset button, view tab. Font body/meta tokens; minimum block size `--control-min-block`; inline padding `--control-padding-inline`; radius control; one control-boundary hairline. The view choices have equal height and visual weight. No extra icon library is required; native disclosure/select markers and explicit text suffice.

| State | Required presentation and behavior |
| --- | --- |
| Default | Paper / primary ink; actual label and helper association. Empty search is valid. |
| Hover | Hover wash only for interactive enabled controls. Data labels do not acquire a hover effect. |
| Active / pressed | Pressed wash, primary ink; no scaling, layout movement or delayed action. |
| Selected | Selected wash plus bold label and semantic state; visible Selected text where needed. No accent outline or underbar. |
| Focus-visible | `--focus-width` solid focus-ring at focus-offset; never clipped by overflow, never replaced by selected wash. |
| Disabled | Native disabled for unavailable-data controls; nearby readable reason. Reset remains enabled in an ordinary empty-result state. Clear may remain enabled when blank, as an idempotent action. |
| Busy | Harness only unless a real nontrivial operation exists. Keep text stable, mark affected region busy and explain **Preparing local results**; do not fake a network loading cycle. |
| Empty | Blank value renders helper, not invalid styling. No-result message belongs to primitive 2. |
| Error | Located text with associated description; retain user's value. Corrupt dataset is a dataset error, not an invalid search. No shaking or color-only error. |

Layout: wrapping cluster; no scroll owner of its own. Keyboard: standard native input/select behavior; Space/Enter for buttons, no global slash shortcut or Escape handler that erases input unexpectedly. Navigation tabs use the section 6 contract. A transient busy state must settle to result or error; it must not trap focus.

### Primitive 2 — Evidence record

**Structure:** stable record identity/title; scope label; named metric/field pairs; short visible interpretation ceiling; optional links to provenance or disclosure. Variants: Corpus result row, case check row, source quotation entry, dataset identity block, empty/error notice. Case article and source list compose repeated records with a stack. Use paper by default, optional tonal method inset, neutral row separators, surface radius only for genuine inset surfaces. Normal spacing is space-4, between records space-6, between semantic groups space-8. Avoid cards within cards.

| State | Required presentation and behavior |
| --- | --- |
| Default | All required labels and values readable; genuine zero remains zero. |
| Hover / pressed / focus | Static record container has none. Only its actual link, control or summary gets primitive 1/3 states. No whole-card click target with nested actions. |
| Selected | Only if it represents an actual selected item; tonal wash plus text and semantic association. Initial cases are a list of independent records, not a selectable ranking. |
| Disabled | Not applicable to an evidence record. An unavailable value is explained as **Unavailable**, never disabled or faded into invisibility. |
| Busy | A real update marks only its result region `aria-busy`; retain stable heading and controls. No stale value is relabeled as newly calculated. |
| Empty query result | **No saved query matches “…”** plus **Clear search** and **Reset filters**; controls remain usable. Insert entered text as text, with wrapping, not HTML. |
| Measured zero | **0 occurrences**, explicit `0 / n`; ordinary ink, not failure red. |
| Structural empty | **N/A** plus **No source units in this plane/role**. Accessible expansion states what N/A means. |
| Missing warrant | Rust text on caution/tonal/paper and literal **Not supplied** or **Insufficient for coercion**, naming the missing field or warrant type. Do not infer absence from a missing findings entry. |
| Invalid / unavailable | Named input/problem and repair direction; no invented zeros, no cached green success, no half-valid summary. Other validated independent sections may remain readable with their own identity. |

**Cases composition:** preserve A-bounded through E-capture and their original alternative descriptions. Each article begins with **Synthetic alternative**, its ID, description, scope ceiling and its rule-result summary in ordinary prose. Permitted summary: **No violations reported by these 15 stipulated checks** or **3 stipulated checks report violations**. Never use a percent passed, star rank, shield, traffic light, freedom meter, legitimacy label or congratulatory success state. The check list stays in stable rule order; failures are not the only rendered rows.

Each check row shows rule ID, plain-language criterion, explicit result (**No violation reported** / **Violation reported**), and relevant input values or a clearly linked inputs disclosure. Conditional checks also explain their trigger; when not triggered say so in supporting text, so a passed noncoercive authority check cannot be read as evidence of a real warrant. Preserve all 15 explicit boolean results even when a conditional predicate did not trigger.

| Required rule ID | Criterion and relevant input to expose |
| --- | --- |
| `ISSUER_TYPE` | Asserting body's entity kind |
| `JURISDICTION_TYPE` | Issuing jurisdiction kind, separate from reach |
| `SUBJECT_COLLAPSE` | Subject kind must not conflate person/collective with poetic state or jurisdiction |
| `CAPTURE` | Whether the assigned role claims to exhaust the person |
| `VISION_HIERARCHY` | Whether vision rank determines rights |
| `RIGHTS_FLOOR` | Equal-personhood assumption |
| `FORCED_REGISTER` | Forced exclusive national registration |
| `TRANSLATION_OBLIGATION` | Public reason and representation limits, including whitespace-only gaps |
| `POETRY_TO_POWER` | Coercive consequence and actual competence-warrant type |
| `AUTHORITY_GAP` | If coercive: competence, competence source, reach, enforcement actor and limits |
| `CONTESTATION` | Forum, voice and revision, each named separately |
| `FORMAL_EXIT_ONLY` | Exit statement and practical/material support |
| `EXCLUDED_AFFECTED` | Affected nonmembers and their standing |
| `RESOURCE_GAP` | Resource-decision trigger and burden allocation |
| `FORCED_INCORPORATION` | Treaty/refusal implication and distinct treatment |

The historical `research/case-assessments.json` inspected here is findings-only. During this task, another owner added `RuleCheck` and schema-2 explicit checks in source. This contract requires root to generate/bind the fresh explicit assessment, not make the browser manufacture 15 passes from the old findings-only file. Missing, duplicate or unknown check IDs invalidate that case's evaluation. An unrun check is **Unavailable**, not No violation. Do not duplicate the assessor's policy logic in client JS.

Case inputs are grouped in the manuscript's order: entity and assigned role; classification warrant and source; asserting authority and competence; consequence and affected people; contestation, exit and revision; temporal scope and provenance. Render actual field contents, with empty/whitespace-only values visibly **Not supplied**. For C-capture, identify the interpretive warrant as insufficient for coercion; it is present, not blank. E-capture must disclose absent burden allocation and denied affected-nonmember standing and treaty/refusal treatment, not only color its summary.

**Sources composition:** exactly Q01–Q13, in stable ID order. Visible even when provenance is collapsed: work, complete locator, quotation, source URL, short context/interpretation limit, bounded verification wording and reading ceiling. Disclosure contains exact segments/anchors/occurrence indices, source digest, normalization method, edition/copy distinctions and rights information. Preserve Q05's right-epigraph reading order and Q11's two noncontiguous excerpts with **Lines 6–11 omitted** outside the quotation. Never silently join Q11 into continuous verse. Quotation verification means selected text matched a bound source under its normalization, not that its interpretation or every edition was verified. Root reruns the actual quotation validator before using **Selection verified against bound ASU source**; otherwise show **Verification unavailable** with reason.

### Primitive 3 — Evidence disclosure

**Structure:** native details/summary; short action/object label; body in source order; no nested interactive element in summary. Variants: **Inputs for A-bounded**, **Query method and limits**, **Dataset and input identity**, **Quotation provenance**, **Reading and rights limits**, **Font license**. Use ordinary document flow; summary minimum target is control-min-block; body top gap space-3; inset space-4; neutral top/bottom row hairline; no accent left border. Keep method/caveat text that governs interpretation visible outside the closed disclosure.

| State | Required presentation and behavior |
| --- | --- |
| Closed | Summary names what will be revealed; native marker indicates state. Hidden body cannot receive focus. |
| Open | Body revealed immediately, full content retained, no arbitrary height cutoff; native marker changes. |
| Hover / pressed | Summary only receives hover/pressed washes and primary ink. |
| Focus-visible | Summary receives visible focus ring; body links retain their own focus affordance. |
| Disabled | Not applicable: evidence remains accessible. If evidence is unavailable, openable explanation names the missing input. |
| Busy | Not applicable for embedded content; do not defer retrieval to a network or fabricate a loader. |
| Empty | Explain **No additional evidence recorded**; do not show an empty frame or an apparently broken toggle. |
| Error | A located textual explanation remains readable inside the disclosure, with an outer visible warning if the missing material affects a displayed claim. |

Multiple disclosures may remain open for comparison. No exclusive accordion and no all-panels collapse on a tab switch. Keep state in memory during the session; no persistent history or query-text storage. A separate **Expand all case details / Collapse all case details** control is optional only if root can retain focus sensibly; it is not needed to satisfy this contract.

## 6. Motion & Interaction

### Mechanisms and deliberate adaptations

The beui `input` source associates label and error text, maintains controlled/uncontrolled input state and reserves message space. Its pill frame, shake and success check are not adopted. The `bouncy-accordion` source uses stable trigger/content identities, explicit open state and hidden/inert closed content, with reduced-motion branches. Adopt its state/evidence continuity, implemented using native details semantics. Its single-open constraint, measured height, spring bounce, rotation animation and framework dependencies are not adopted. These are deliberate adaptations for a small offline instrument and this workbench's adopted zero-motion direction.

All motion durations are `--motion-duration:0ms`, easing linear. No transitions, animated scrolling, initial reveals, count-up, skeleton shimmer, blur, parallax, spring, scale-on-press or delayed tab changes. Reduced-motion and ordinary modes have identical state availability; zero motion is the starting design, not an optimization that removed a promised interaction. State feedback is same-frame tone, text and native control state. No pointer capture, custom drag gesture or hover-revealed evidence.

### Switching views

Enhanced view control follows the [WAI-ARIA tabs pattern](https://www.w3.org/WAI/ARIA/apg/patterns/tabs/) with **manual activation**. Corpus is initially active. One tab participates in the tab sequence; Left/Right arrows move among tabs, wrapping; Home/End move to first/last; Enter/Space activates the focused tab. Focus remains on the activating tab; Tab enters the active panel's first meaningful control, or a focusable panel if needed. Each tab and panel have unique linked IDs, selected/hidden states and programmatic labels. Inactive panels and their descendants are absent from focus/accessibility navigation. The tab bar is a spatially wrapping strip, not a horizontally scrollable reel.

Preserve Corpus filter values and independent disclosure states while changing views. Filter changes do not activate a different view. Theme changes never reset content state. No URL query string or storage entry contains the research search text. Reload starts at Corpus with empty search, All planes/roles and System appearance.

Progressive enhancement: before JS successfully initializes, all three sections are readable in normal flow with ordinary in-document navigation links. Only install tab semantics and hide inactive panels after their handlers are ready. JS-dependent filtering controls are unavailable with an explanation; native disclosures and source links still work. A visible noscript explanation says **Filtering requires JavaScript; the saved results below remain readable.** Script failure must not strand the document with two permanently hidden sections.

### Filtering, reset and status

Search is a literal filter over the preloaded query names/variants; update on input after composition ends, with no submit/network request. Plane/role selects update on native change. During IME composition, preserve the typed value and defer filtering until compositionend. Perform one render/status update per completed input event; no focus replacement and no re-creation of the active text input. Result changes occur below the controls.

Use one polite, atomic status region for visible result counts. Do not mark the whole result list live or announce every row. Coalesce rapid typing announcements after about 200 ms without delaying visible results; this is a functional announcement timer, not an animation. Reset applies all three changes together and emits one status update. After Clear search, return focus to the query field. After Reset filters, keep focus on Reset so repeated keyboard use is predictable. An empty result never disables either recovery action.

External source links are ordinary `https` links, visibly marked **Online source**. They can open in a new tab with `rel="noopener noreferrer"`; no prefetch, prerender, preconnect, DNS hint, fetch, beacon or tracking. Opening a link requires the user's action and may require network access. The workbench itself performs zero runtime network requests and does not check source freshness. No service worker, local server, import map, CDN or directory permission is needed for ordinary `file://` use.

### Interpretation caveats: scoped copy

| Location | Visible plain-language copy |
| --- | --- |
| Corpus under heading | **Counts locate material to read. They do not measure literary meaning or show that Blake endorsed a political relation.** |
| Corpus coverage label/helper | **Coverage counts matching indexed source units in the selected plane and role. Copies and pages may repeat a work; this is not a count of unique works.** |
| Corpus method | **The XML plane includes markup and apparatus. Editorial/mixed pages remain distinct from primary text. A zero is absence in this pinned projection, not the whole oeuvre. Twenty-eight discovered image identifiers remain unresolved in this snapshot.** |
| Cases under heading and summary | **These are synthetic alternatives checked against stated project rules. A result does not establish legality, political legitimacy, consent or observed freedom.** |
| Case warrants | **A stated source of authority is a claim to inspect. Filling a field does not establish that the authority exists or works as described.** |
| Sources under heading | **Verification concerns the selected wording in the bound transcription. Interpretation, illuminated-copy collation and institutional authority require separate argument.** |
| Sources reading ceiling | **Selected passage and immediate context checked; this is not a claim of complete reading of every work, edition or cited scholar.** Keep more specific record-level qualifications alongside this sentence. |
| Sources rights ceiling | **Selected quotations do not clear redistribution of the recovered corpus or modern editions. Source links and item-specific rights notes retain their limits.** No blanket fair-use or CC0 label. |

The 28-image figure must be supplied by the bound manifest; update the copy if the snapshot changes. Expand Arizona State University (ASU) and Library of Congress (LOC) at first use in user-facing evidence text. Explain **E** in a locator as the Erdman edition page reference; expand XML as Extensible Markup Language on first use. Keep quotation wording itself untouched.

## 7. Depth & Surface

Use **mixed: tonal layers plus neutral 1px rules**, with no shadows. The desk/paper/tonal hierarchy carries the manuscript's material language at screen density. Default record rows are open reading surfaces, separated by spacing and occasional neutral rules. A method inset may use tonal fill with surface radius. Controls use the smaller control radius. Do not nest two rounded inset frames; use a stack within the first one. For a rare nested surface, inner corners are square when its padding consumes the outer radius.

Extracted print details: 612 × 792 pt page, 39.6 pt margins (13.97 mm), 7 pt box radius, 11 pt bold diagram labels, 9 pt descriptions, 10 pt body with 12.8 pt leading; cover title 29 pt and interior abstract titles 23 pt. The four references have large section gaps, pale boxes, teal/rust strokes, arrows, small plate images, italic quotation and a fine footer. They also have a full-width teal top band. **These are observations, not screen tokens.**

Preserve: clear common left edge; title/body size contrast; pale evidence grouping; separation of claim, warrant and ceiling; deliberate paired alternatives; visible attribution. Adapt: print sizes to the screen type scale; page margins to responsive gutters; accent box strokes and top band to neutral rules and tonal grouping; large cover whitespace to compact working space. Omit: full-page cover composition, decorative arrows, image thumbnails and teal top stripe. There is no diagram in this version that requires an arrow to explain a relationship. The instrument should resemble the manuscript's working notes, not a miniature PDF or a newly branded SaaS dashboard.

No hover elevation on static case/source records. There is no floating layer to shadow or blur. Focus rings are the sole accent edge treatment, used only for keyboard focus; their role is functional visibility, not card decoration.

## 8. Accessibility Constraints & Accepted Debt

### Accessibility constraints

Target Web Content Accessibility Guidelines (WCAG) 2.2 AA. This is an implementation target, not a conformance claim. Text contrast at least 4.5:1 for normal text, 3:1 only for qualifying large text; essential control boundaries and focus cues at least 3:1 against adjacent layers. See [W3C contrast guidance](https://www.w3.org/WAI/WCAG22/Understanding/contrast-minimum.html). The declared tokens already avoid needing the large-text exception. Root must test actual states and user agents.

- Native controls, visible persistent labels, correctly associated helper/error text, one main landmark, a skip link, one workbench h1 and logical h2/h3 hierarchy. Stable IDs must not be generated from unsafe raw quotation anchors without escaping.
- Every control has a minimum 44 × 44 CSS px-equivalent target at default text size, including summary toggles. Inline prose links may follow the WCAG inline exception but must remain distinctly underlined. Native browser zoom and selection stay enabled.
- Full task completion with keyboard alone, visible unoccluded focus, no focus traps, no automatic focus jump on filtering. Do not require hover, precise pointer movement, a custom shortcut or reading color to understand a result.
- At 200% text size and 400% browser zoom / 320 CSS px reflow, primary content stays one readable column with no horizontal scrolling. Test both long locators and long URLs; increasing font size must not clip fields or collapse source metadata.
- `overflow-wrap:anywhere`, logical margin/padding properties, intrinsic sizing and no fixed block height for quotations or explanation. User font overrides are allowed. No truncation-only access to IDs/hashes/URLs.
- Forced-colors mode retains native controls, outlines and disclosure markers. Use system colors where author colors are overridden; do not set `forced-color-adjust:none` for thematic fidelity.
- Semantic table headers/captions or a tested alternate record representation; count labels and denominator meaning remain accessible at every width. N/A is defined in visible text, and zero is distinguishable from unavailable data.
- Native details behavior follows [MDN's details reference](https://developer.mozilla.org/en-US/docs/Web/HTML/Reference/Elements/details). Do not add a conflicting button role to summary, create nested summary buttons or manually desynchronize expanded state.
- Screen-reader check: selected tab, view heading, labeled filters, one concise status update, a check's criterion/result/input, and a quotation's attribution/omission can each be understood in sequence. Static screenshots cannot establish any of these behaviors.
- Preserve raw quotation/locator wording and identify editorial additions separately. Keep the instruction vocabulary concrete: query group, source unit, selected wording, stated rule, missing field. Avoid an unexplained icon legend or specialist shorthand in controls.
- Do not imply broader reading or rights clearance through an accessible label even when visible copy is cautious. A screen-reader-only label is subject to the same claim ceilings.

### Accepted debt and unresolved implementation prerequisites

Adopted implementation boundaries below are accepted boundaries for this version. No accessibility defect, scientific shortcut or broken offline path is accepted by this design handoff. New debt needs an explicit owner, affected users, reason, exit and root/user acknowledgement; an optimistic empty table is not acceptance.

| Item | Location / affected users | Why bounded here | Owner / exit |
| --- | --- | --- | --- |
| Saved-query filtering only | Corpus; users expecting a new lexical query | This implementation uses a small offline document without restricted corpus bodies. Label the control explicitly; arbitrary corpus searching is outside this artifact. | Root; reconsider only with a separately authorized private search/data architecture |
| Source links do not resolve while offline | Sources; reader wanting the complete source context | Document includes locators, bounded quotation and provenance; external resources open only on deliberate navigation. | Root; keep offline notice and exact URLs; expanding embedded source material requires rights/scope review |
| English interface, user-selected fonts may fall back | Whole document; non-English interface users | English manuscript/brief; preserve all displayed Unicode content and wrapping. No multilingual interface is promised. | Root; future translation work must revisit labels, source order and font coverage |
| Font payload adds about 251 KB base64 before descriptors/license | Single-file artifact; slow storage/mobile parsing | Preserves the real manuscript face without network or new setup. Fits the budget below. | Root; optimize only after measurement, and preserve license/naming rules |
| Cross-browser, screen-reader and real-participant evidence not yet produced | Entire proposed UI | This task authors a contract only and is prohibited from implementing UI. These are pending verification prerequisites, not waived defects or claimed passes. | Root executes matrix; human research limitations remain explicit |
| Fresh assessment and export identity required | Cases / provenance | Existing assessment JSON is legacy findings-only; another owner is updating explicit checks concurrently. | Implementation owner generates all 15 checks per alternative; root binds the final artifact |

### Evidence-shaped performance budgets

Budgets are proposed targets for the ten alternatives, 150 explicit check results, 13 quotations, 20 query groups and 180 aggregate cells actually observed. They are not timing measurements. The historical full concordance is about 24.7 MB and is expressly excluded. Do not solve a budget failure by deleting required evidence, hiding failure rows, shrinking type or omitting an interpretation caveat.

| Measure | Budget and verification root must record |
| --- | --- |
| Delivery | One standalone HTML file, **at most 768 KiB uncompressed on disk**; no sidecars needed to view it |
| Embedded fonts and license | At most 270 KiB including base64/descriptors/license; three unmodified Vera faces, no font fetch |
| CSS | At most 18 KiB uncompressed, no external stylesheet |
| JavaScript | At most 24 KiB uncompressed; no framework, hydration, worker, package runtime or third-party script |
| Markup and research data | At most 420 KiB including all required content and embedded manifest; avoid duplicate hidden mobile copies |
| Network | **Zero runtime requests**, zero connection hints, telemetry and background link checks; user-initiated external navigation tested separately |
| DOM | At most 5,000 element nodes in the complete enhanced document; 180 aggregate rows and 150 check rows do not require virtualization |
| Initial usability | Cold local-file meaningful content and working filters within 1.0 s on recorded desktop reference hardware and within 2.0 s at 4× CPU throttle; five runs, median and worst reported |
| Input feedback | Native press feedback same frame; completed filter/change to visible settled result within 100 ms at 4× CPU throttle, 20 scripted actions; report samples, p95 and max |
| Blocking work | No main-thread task over 50 ms attributable to a filter, view change or disclosure after initialization |
| Stability | No load-induced layout shift after fonts settle; target CLS ≤ 0.01 on startup; disclosure expansion is user-driven normal flow, not a delayed layout surprise |

Arithmetic: 270 + 18 + 24 + 420 = 732 KiB, leaving 36 KiB overhead under the total cap. Test raw final bytes, not just gzip. Measure the actual generated file on `file://` in an offline browser context with a fresh profile/cache state; record browser version, machine, viewport, throttle and run counts. Test a local HTTP mirror only as supplementary evidence if approved by root's workflow; it does not replace actual local-file execution.

The perfection reference asks for real-browser Lighthouse 100 in all categories and mobile/desktop repeats. This task has run no Lighthouse or render audit. Root should retain available raw audit evidence and report category scores and failures honestly. A private `file://` document has no deploy/CDN or public canonical/indexing objective; don't publish it, add a fabricated canonical URL, remove noindex/privacy metadata or install tooling merely to manufacture a public-site score. If the real-browser audit path cannot support the local artifact, label that check **Unavailable** with its exact prerequisite/error and use the direct offline byte/network/interaction evidence above without claiming Lighthouse compliance. Private-file `noindex,nofollow` metadata is appropriate, but is not access control.

### State harness and QA matrix — execute before product integration

Root first integrates sections 1–8 into project `DESIGN.md`, then builds an **isolated primitive state harness** under its own authorized output scope. It must exercise the three primitives using real generator/data paths and intentionally invalid fixtures. No harness produced or run by this design task. Harness state controls/fixtures must not leak into the delivered research document. Only after the primitive showcase is verified should root compose the product views.

Capture harness primitives and product views at **390 × 844**, **768 × 1024** and **1440 × 900**, each in **light and dark**. Also execute **320 CSS px reflow**, 200% text and 400% browser zoom, and capture scrolled-end views containing final source/check rows and complete URL ends. Reduced-motion and forced-colors are separate behavioral passes. Browser actions in T3 Code begin with `preview_status`, then `preview_open` if needed; do not switch tools solely because the preview initially has no tab. The discovered preview tools were available in this design task but were not invoked because no UI was implemented.

| ID | Fixture / action | Required observable evidence |
| --- | --- | --- |
| H01 | Every primitive default, hover, pressed and focus-visible | Same anatomy in both themes at all three showcase widths; token-derived computed styles, visible focus, no accent stripe/outline |
| H02 | Control selected, disabled with reason, real/harness busy, empty and error | Each state visibly distinct and semantically correct; no fake production loader, no hidden reason or invalid empty query |
| H03 | Evidence record genuine zero, structural N/A, unavailable, invalid and missing warrant | Text and denominator semantics differ; static rows never acquire button-like hover/focus |
| H04 | Disclosure closed/open, long content, no additional evidence, missing evidence | Toggle with pointer/Enter/Space; closed links not focusable; open content complete, no clipped height, errors stay readable |
| Q01 | Blank query and All/All filters | 20 saved query groups and 180 cells; four structural gaps per query show N/A; current fingerprint visible |
| Q02 | Literal `states`, Reading / Primary | 264 occurrences and 60 / 199 units (30.2%); variants shown; label explains saved-query filtering |
| Q03 | `negative_control`, each populated cell | Zero occurrences with each real denominator; structural-empty cells remain N/A; zero is not a search failure |
| Q04 | Nonsense display query absent from names/variants | No-match message, zero groups, usable controls; not a fabricated zero-occurrence corpus result |
| Q05 | Type whitespace; Clear; Reset; repeat Reset; change views and return | Blank restores query groups; Clear affects only query; Reset restores All/All and search; theme and unrelated disclosures preserved; focus contract holds |
| Q06 | Long 512-character display query, mixed case, metacharacters, IME composition | No regex/HTML execution, no overflow or lost input; composition not interrupted; one coalesced status announcement |
| Q07 | Source census adversaries: missing denominator, `m > n`, positive match at `n = 0`, duplicate/missing cells | Real generator/validator rejects each fixture with specific error; no silently published normal-looking file; rejected evidence retained |
| C01 | Enumerate ten alternatives and their check IDs | Ten stable decision IDs, exactly 15 unique checks each, total 150; each boolean is explicit and bound to current assessor; all failure and nonfailure rows inspectable |
| C02 | C-capture and E-capture | Present interpretive warrant labeled insufficient for coercion; E's empty burden value and nonmember/treaty problems visible; actual values remain inspectable |
| C03 | Legacy findings-only, remove a check, duplicate a check, swap a case identity | Invalid/unavailable assessment or generation rejection; absence of finding cannot become an invented pass |
| C04 | Conditional rule with antecedent false; lens count changed in an authorized fixture | Predicate result remains explicit with trigger explanation; no implied evidentiary warrant, freedom score or vision-based entitlement |
| S01 | Q01–Q13 in source view | Exactly 13 records, complete locators/source URLs, text segments and context retained, reading/rights ceilings visible |
| S02 | Q05 and Q11 | Right-epigraph order preserved; Q11's omission named outside quote and segment break retained; no invented verse numbers |
| S03 | Change one quotation character or source hash; remove consumed input | Actual quotation validation fails; no Selection verified label or normal artifact from invalid evidence; preserve error output |
| A01 | Keyboard-only: skip link, view tabs, filters, Clear/Reset, details, source links | Real key trace or recording plus focus screenshots; correct arrow/Home/End/manual activation, Tab/Shift-Tab order, no trap or lost focus |
| A02 | Screen reader over tab switch, filtered count, check row and source | Record reader/browser, spoken labels/state/result; one concise status update, full denominator/omission intelligible; don't infer from DOM inspection alone |
| A03 | 320 px, 200% text, 400% zoom, long unbroken ID and URL, multi-paragraph input | No document horizontal overflow, concealed URL end, overlap or clipped control; both themes and scrolled-end captures |
| A04 | System/Light/Dark; OS preference change; reduced motion; forced colors | Correct override/session behavior and native controls; state changes still immediate; focus/selection survive forced colors |
| O01 | Copy generated HTML alone to an empty directory; open with network disabled | All three views, filters, explicit cases, quotes, fonts and disclosures work without sibling files; zero automatic requests; no service worker or origin permission |
| O02 | Disable JS; induce initialization failure | All three static sections and native disclosures readable; navigation links usable; filtering limitation stated; no permanently hidden data |
| O03 | Insert `<`, `&`, quotes and script-closing text into a synthetic label | Data is text, not executable markup; safe JSON embedding; no arbitrary script/event handler or unsafe-link activation |
| P01 | Final artifact bytes / node count / cold-load and 20-action timing | Raw measurements with final HTML hash, input hashes, browser/hardware/throttle; compare each budget, report failures without deleting evidence |
| V01 | Generated styles and all sibling surfaces before integration | Accent-stripe checker exits 0 on authored CSS/HTML; real computed-token and reference-fidelity captures show Vera/paper/teal/rust and documented adaptations |
| V02 | Post-composition objective visual QA, then Lane C walkthrough | Tie screenshots, keyboard/reader records, persona tasks, heuristic findings and outstanding debt to the same generated file hash; root obtains independent review separately from this builder's design work |

Negative controls are required evidence: a validator that has not rejected Q07, C03 and S03 fixtures is not demonstrated merely by a green ordinary run. Use real temporary files and actual generator/validator subprocesses under root's authorized GitVault output boundary, preserving their stderr/exit codes. Root must bind its Python environment/cache/TMP settings per project instructions before execution. This design task performed no package tests, native render jobs or environment setup.

Before integration, root retains a concise handoff packet: final `DESIGN.md` identity; primitive-state captures; final generated HTML hash and manifest; light/dark/width/scrolled-end captures; key/reader/offline/timing records; failing negative-control receipts; actual static check outputs; persona task outcomes; located accessibility/heuristic findings and owner/exit for any accepted debt. Lane C critique follows objective rendered evidence. No numerical visual score or focused suite substitutes for these observations. This contract supplies the work to verify; it does not issue their acceptance decision.

### Exactly what was inspected and what was unavailable

**Local observations:** all four supplied full PNGs viewed with the image tool; renderer (607 lines), article (316 lines), and references/rights appendix (49 lines) read in full; complete `corpus.py` and `institutions.py` read; targeted relevant model definitions read, including the concurrent new `RuleCheck` shape; queries and pin/analysis receipts read; aggregate CSV header/sample and all negative-control rows read; all ten legacy assessment records read; selected case fields for all ten plus full A-bounded/C-capture/E-capture records read; all 13 quotation records and asset metadata extracted from the manuscript specification; import receipt read; pinned SQLite index SHA-256 recalculated, and joint plane/role census queried read-only. The larger primary-passage ledger was inspected as a partial supporting read, not asserted read in full or used as the source of the 13-quotation membership. The raw full concordance, complete corpus bodies, source images beyond the four supplied manuscript renders, and modern scholarship PDF bodies were not read for this design task. No external Blake or scholarly source was newly verified here.

**Guidance read in full:** frontend `SKILL.md`; design `README.md`, `design-system-architecture.md`, `image-to-code-skill.md`, `minimalist-skill.md`, `layout-skill.md`, `stylegallery.md`, `interaction-skill.md`; perfection `README.md`; designpowers `README.md`, `routing.md`, `orchestration.md`, `lane-c-review.md`. Repository/ancestor storage guidance was read. No existing `DESIGN.md` was present in the project's root, docs or src slots when checked. Root owns its creation.

**Public mechanism references consulted:** [StyleGallery catalog](https://raw.githubusercontent.com/changeroa/StyleGallery/main/CATALOG.md), [page-grid contract](https://raw.githubusercontent.com/changeroa/StyleGallery/main/patterns/grid-repetition/page-grid.md), [tab-strip contract](https://raw.githubusercontent.com/changeroa/StyleGallery/main/patterns/in-line-grouping/tab-strip.md), [beui input source](https://beui.dev/r/input/raw), [beui accordion source](https://beui.dev/r/bouncy-accordion/raw). The first-party MDN and W3C pages linked above were consulted for focused semantic/keyboard/contrast guidance, not asserted exhaustively read. These are dated research inputs, not runtime dependencies or copied product brands.

**Availability and scope:** local references, font files/license, SQLite CLI, SHA-256 utility, Bun and public curl fetches were available and invoked. T3 preview tools were discovered; no browser rendering or browser audit was attempted in this design-only task. No required reference fetch failed. Imagen/Lazyweb/new Layer B brand research was not run because root selected the existing approved manuscript as the concrete reference and scoped this pass to the existing project language; it is not labeled an unavailable tool. React developer tools do not apply to this non-React product. Real UI, state harness, browser metrics, screen-reader session, Lighthouse scores and independent acceptance are **not yet produced**; that is a work-stage boundary, not fabricated evidence of unavailable tooling. Source files were observed changing under another owner, so listed hashes bind individual inspected inputs rather than a claimed atomic repository snapshot. No Git operation, project-file write, publication, credential access, lease or framework setup occurred in this task.
