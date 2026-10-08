---
name: "TicketCenter"
description: "A readable Thai service desk shaped by contemporary office wayfinding."
colors:
  ground: "#f3f5f8"
  surface: "#fff"
  surface-soft: "#f5f7fa"
  ink: "#23324a"
  muted: "#59697f"
  line: "#dce2eb"
  accent: "#315ac5"
  accent-hover: "#25479e"
  selected: "#eaf0ff"
  rail: "#202d48"
  rail-ink: "#f3f6ff"
  rail-muted: "#bdc9e1"
  open: "#895406"
  open-bg: "#fff2d8"
  progress: "#6946a3"
  progress-bg: "#f0eafa"
  done: "#1c6647"
  done-bg: "#e4f4e9"
  danger: "#a92f35"
  danger-bg: "#fff0f0"
  hr: "#894961"
  hr-bg: "#f9eaf0"
  it: "#2c6080"
  it-bg: "#e8f1f7"
  chat-ground: "#edf0f5"
  chat-mine: "#315ac5"
  ground-dark: "#161e2e"
  surface-dark: "#202b3f"
  surface-soft-dark: "#28354a"
  ink-dark: "#edf2fa"
  muted-dark: "#b5c2d6"
  line-dark: "#3b4b64"
  accent-dark: "#a7c4ff"
  accent-hover-dark: "#c3d6ff"
  selected-dark: "#2c4066"
  rail-dark: "#151f34"
  open-dark: "#f5cf86"
  open-bg-dark: "#493920"
  progress-dark: "#d4bcfa"
  progress-bg-dark: "#3d3152"
  done-dark: "#a2e3b7"
  done-bg-dark: "#294536"
  danger-dark: "#ffb7b7"
  danger-bg-dark: "#4b2e32"
  hr-dark: "#e6b6c9"
  hr-bg-dark: "#48313b"
  it-dark: "#b0d4ed"
  it-bg-dark: "#294252"
  chat-ground-dark: "#192437"
  chat-mine-dark: "#3c5eab"
  white: "#fff"
  button-ink-dark: "#132440"
  rail-selected: "#dae5ff"
  rail-selected-ink: "#233d75"
  rail-selected-detail: "#284c95"
  rail-hover: "#304365"
  rail-focus: "#b7cbff"
  unread: "#b13940"
  chat-time-mine: "#dfe9ff"
typography:
  display:
    fontFamily: "'Noto Sans Thai', sans-serif"
    fontSize: "clamp(32px, 3.6vw, 50px)"
    fontWeight: 600
    lineHeight: 1.4
    letterSpacing: "-.025em"
  headline:
    fontFamily: "'Noto Sans Thai', sans-serif"
    fontSize: "26px"
    fontWeight: 700
    lineHeight: 1.45
    letterSpacing: "-.02em"
  title:
    fontFamily: "'Noto Sans Thai', sans-serif"
    fontSize: "21px"
    fontWeight: 700
    lineHeight: 1.5
  subheading:
    fontFamily: "'Noto Sans Thai', sans-serif"
    fontSize: "17px"
    fontWeight: 700
    lineHeight: 1.5
  body:
    fontFamily: "'Noto Sans Thai', sans-serif"
    fontSize: "16px"
    fontWeight: 400
    lineHeight: 1.75
  row-title:
    fontFamily: "'Noto Sans Thai', sans-serif"
    fontSize: "16px"
    fontWeight: 600
    lineHeight: 1.7
  button:
    fontFamily: "'Noto Sans Thai', sans-serif"
    fontSize: "15px"
    fontWeight: 600
    lineHeight: 1.5
  label:
    fontFamily: "'Noto Sans Thai', sans-serif"
    fontSize: "14px"
    fontWeight: 600
  metadata:
    fontFamily: "'Noto Sans Thai', sans-serif"
    fontSize: "13px"
    fontWeight: 400
  status:
    fontFamily: "'Noto Sans Thai', sans-serif"
    fontSize: "12px"
    fontWeight: 600
    lineHeight: 1.6
  metric:
    fontFamily: "'Noto Sans Thai', sans-serif"
    fontSize: "30px"
    fontWeight: 600
    lineHeight: 1.4
rounded:
  tight: "4px"
  badge: "5px"
  compact: "6px"
  control: "8px"
  department: "10px"
  panel: "12px"
  dialog: "16px"
  round: "50%"
spacing:
  4: "4px"
  6: "6px"
  8: "8px"
  10: "10px"
  12: "12px"
  14: "14px"
  16: "16px"
  18: "18px"
  20: "20px"
  22: "22px"
  24: "24px"
  28: "28px"
components:
  button-primary:
    backgroundColor: "{colors.accent}"
    textColor: "{colors.white}"
    typography: "{typography.button}"
    rounded: "{rounded.control}"
    padding: "10px 17px"
  button-primary-hover:
    backgroundColor: "{colors.accent-hover}"
  button-primary-dark:
    backgroundColor: "{colors.accent-dark}"
    textColor: "{colors.button-ink-dark}"
  button-primary-dark-hover:
    backgroundColor: "{colors.accent-hover-dark}"
  button-secondary:
    backgroundColor: "{colors.surface}"
    textColor: "{colors.ink}"
    typography: "{typography.button}"
    rounded: "{rounded.control}"
    padding: "10px 17px"
  button-secondary-hover:
    backgroundColor: "{colors.selected}"
  button-text:
    textColor: "{colors.accent}"
    padding: "8px 10px"
  input:
    backgroundColor: "{colors.surface}"
    textColor: "{colors.ink}"
    rounded: "{rounded.control}"
    padding: "11px 12px"
  navigation:
    backgroundColor: "{colors.rail}"
    textColor: "{colors.rail-ink}"
    rounded: "{rounded.control}"
    padding: "10px 12px"
  navigation-active:
    backgroundColor: "{colors.rail-selected}"
    textColor: "{colors.rail-selected-ink}"
  status-open:
    backgroundColor: "{colors.open-bg}"
    textColor: "{colors.open}"
    typography: "{typography.status}"
    rounded: "{rounded.badge}"
    padding: "3px 7px"
  status-progress:
    backgroundColor: "{colors.progress-bg}"
    textColor: "{colors.progress}"
  status-done:
    backgroundColor: "{colors.done-bg}"
    textColor: "{colors.done}"
  status-urgent:
    backgroundColor: "{colors.danger-bg}"
    textColor: "{colors.danger}"
  panel:
    backgroundColor: "{colors.surface}"
    textColor: "{colors.ink}"
    rounded: "{rounded.panel}"
    padding: "24px"
  ticket-row:
    backgroundColor: "{colors.surface}"
    textColor: "{colors.ink}"
    padding: "18px 15px"
  ticket-row-selected:
    backgroundColor: "{colors.selected}"
  journey:
    backgroundColor: "{colors.surface-soft}"
    textColor: "{colors.muted}"
    rounded: "{rounded.badge}"
    padding: "8px 3px"
  journey-reached:
    backgroundColor: "{colors.done-bg}"
    textColor: "{colors.done}"
  chat-feed:
    backgroundColor: "{colors.chat-ground}"
    rounded: "{rounded.department}"
    padding: "18px 14px"
  chat-mine:
    backgroundColor: "{colors.chat-mine}"
    textColor: "{colors.white}"
    rounded: "{rounded.panel}"
    padding: "12px 14px"
---

# Design System: TicketCenter

## Overview

**Creative North Star: "Contemporary Thai Office Wayfinding"**

TicketCenter gives internal service work the clarity of contemporary Thai office wayfinding: a slate navigation rail, cool working surfaces and readable department names. The confirmed familiar inbox structure supports quick scanning and a clear next action.

The interface is practical and moderately dense. Flat rows, restrained borders and blue selection carry hierarchy; generous Thai line spacing keeps requests and conversations readable. Login, employee, agent and administration views share this visual language, and dark mode preserves the same structure.

**Key Characteristics:**

- Slate navigation with a pale blue active item.
- Cool neutral work and conversation surfaces.
- Thai typography with clear titles, compact metadata and tabular counts.
- Text-labeled status, visible unread counts and a compact three-stage request strip.
- Flat panels with depth reserved for dialogs.

## Colors

Blue anchors service actions and selection; slate anchors navigation, while cool neutrals keep request and chat text central. The user-authorized blue/slate palette supersedes the earlier forest-green palette. Frontmatter values are normative. Unsuffixed custom-property tokens describe light mode; `-dark` entries record the corresponding overrides in `:root[data-theme='dark']`. The application resolves them through the original unsuffixed CSS variables. Tokens without a dark override retain their light value. Hard-coded shared colors are recorded by descriptive role.

### Primary

- **Service Blue** (`accent`, `accent-hover`): primary actions, links, focus and selected summaries. Dark mode uses pale blue with the dedicated dark button ink.
- **Slate Rail** (`rail`, `rail-ink`, `rail-muted`): navigation ground, labels and secondary wayfinding. The active rail uses `rail-selected`, `rail-selected-ink` and `rail-selected-detail`; hover uses `rail-hover` and keyboard focus uses `rail-focus`. These rail state colors remain identical in both modes.
- **Blue Selection** (`selected`): current queue row, avatar ground and quiet selected controls. This changes by theme independently from the active rail color.

### Secondary

- **Pending Amber** (`open`, `open-bg`): pending status, aging and availability notices.
- **Progress Violet** (`progress`, `progress-bg`): work in progress and priority history markers.
- **Completion Green** (`done`, `done-bg`): completed work, active accounts and success feedback.
- **Urgency Red** (`danger`, `danger-bg`): urgent work and errors. `unread` is the fixed red badge for unread message counts.
- **Department Blue / Rose** (`it`, `it-bg`, `hr`, `hr-bg`): compact department marks paired with full department names in readable context. Facilities (FAC) reuses progress violet, finance (FIN) reuses pending amber, and procurement (PROC) reuses department blue. These mark departments rather than ticket state; the adjacent text supplies the meaning.

### Neutral

- **Office Ground / Working White / Quiet Surface** (`ground`, `surface`, `surface-soft`): page ground, working panels and restrained secondary containers.
- **Slate Ink / Secondary Ink / Divider** (`ink`, `muted`, `line`): primary text, metadata and borders. Secondary ink is an intentional readable text role, including on cool chat ground.
- **Cool Conversation / Own Message** (`chat-ground`, `chat-mine`): conversation feed and outgoing bubble. Outgoing message text stays white in both modes; its timestamp uses `chat-time-mine`.

**The State Has a Label Rule.** Pair status color with a readable status label; dots, tint and unread counts supplement text.


## Typography

**Display Font:** Noto Sans Thai, with sans-serif fallback.

**Body Font:** Noto Sans Thai, with the same fallback. The font is self-hosted at `/fonts/noto-sans-thai-{0,1,2,3}.ttf`, in weights (400, 500, 600, 700), with `font-display: swap` and `font-synthesis: none`. The accompanying SIL Open Font License is in `frontend/public/fonts/OFL.txt`.

**Character:** One Thai-capable family supplies a calm, direct voice. Titles and names carry weight; metadata stays compact. There is no separate monospaced family: numerical counts use tabular numerals.

### Hierarchy

- **Display:** login introduction only; fluid desktop size, medium weight and generous leading from `typography.display`. At the mobile breakpoint it becomes (30px).
- **Headline:** workspace title, from `typography.headline`; becomes (23px) at the 1000px and 900px rules. Administration titles become (24px) on mobile.
- **Title / Subheading:** section and request headings, from `typography.title` and `typography.subheading`. Detail title becomes (20px) on mobile; modal titles use (22px), then (21px) on mobile. Login form title uses (30px), then (26px) on mobile.
- **Body:** request/chat reading size and line height from `typography.body`. Request description uses (15px), with a maximum width of (70ch); message text and composer remain (16px), including on mobile.
- **Row title:** semibold, spacious Thai lines from `typography.row-title`; long titles wrap anywhere.
- **Button / Label:** action labels and form labels from their corresponding frontmatter roles; explanatory labels use regular weight with line height (1.65).
- **Metadata / Status:** reference numbers, ages, previews and state chips. Dense contextual metadata ranges from (10–13px); list status chips reduce to (11px). These compact roles are not substitutes for request body text.
- **Metric:** administration counts use `typography.metric`, reducing to (26px) on mobile. Counts and reference numbers use tabular numerals.

**The Thai Reading Space Rule.** Use the shipped Noto Sans Thai weights and preserve the generous line height of request and chat text.

## Layout

The desktop shell has a fixed-height rail and main area (100dvh). Its slate rail is (232px) wide; the top account bar is (60px) high. Workspace gutters are (18px), while administration and topbar padding use (28px). The bordered inbox grid uses `minmax(300px, .65fr) minmax(450px, 1.35fr)`. Queue scrolling stays inside the list pane. The detail body scrolls vertically around the conversation and optional request/activity sections, with a stable header and service-action footer.

The desktop conversation reserves (500px) with `flex: 1 0 500px` and a (500px) minimum height. The feed reserves at least (320px); the composer never shrinks. Request details and activity are ordinary flow content with no maximum height or separate clipped reading region. Opening either section grows the outer detail scroll rather than compressing the feed. A short desktop viewport can require scrolling to reach the composer or history.

Spacing is a compact working rhythm drawn from the frontmatter scale. Controls commonly use (8?12px) gaps and reading sections (16?24px). Workspace headers and margins are deliberately smaller than administration gutters. Avoid interpreting the observed set as a strict arithmetic spacing scale.

Responsive rules are inclusive `max-width` queries, with later desktop overrides applied after them:

| Breakpoint | Shipped change |
| --- | --- |
| 1250px | Rail becomes 220px; administration gutters become 22px; inbox columns become `minmax(275px, .8fr) minmax(330px, 1.2fr)`; API pill hides. Workspace header stays compact at `14px 18px 10px` on desktop. |
| 1000px | Rail becomes 200px; inbox gutters become 16px and columns become `minmax(230px, .8fr) minmax(300px, 1.2fr)`; profile copy hides; overview and catalog panels stack; metric contents stack. |
| 900px | Shell switches to document flow; mobile topbar is 64px. Employee/agent sidebar hides, while administration retains a horizontally scrolling navigation strip. Inbox becomes a single pane: list or detail, with a labeled back action. Inbox gutters are 12px; reading gutters are 16px. Administration panels and settings stack; tables scroll horizontally with a 630px minimum table width. Login stacks, modal gutters become 14px. |
| Desktop height ?800px | Header padding contracts and requester context hides. The conversation feed is fixed at 320px with `flex: none` and a 320px maximum; the outer detail body scrolls to the composer and optional content. |

The expansion action applies from (901px): it hides the sidebar, summary tabs and app footer, reduces header padding to (10px 18px), and uses `minmax(320px, .55fr) minmax(480px, 1.45fr)` inbox columns. The labeled action toggles back to the standard workspace.

On mobile, the conversation returns to document flow with no minimum section height. The feed is (320px) tall with a (420px) maximum, and message maximum width increases from (88%) to (93%). The principal input/button baseline is (44px) minimum height, with compact toolbar/composer exceptions; the coarse-pointer rule restores a (44px) refresh target and send-button height. Do not describe every compact desktop control as meeting the same minimum.

## Elevation & Depth

Working views are flat. Surface tone, a one-pixel divider and selection tint establish separation. Dialogs use the single ambient shadow (`0 18px 60px rgba(14,28,51,.22)`) over a dark translucent scrim (`rgba(9,29,23,.55)`). Notification menus are bordered rather than shadowed.

**The Dialog Depth Rule.** Use the dialog shadow for modal separation; ordinary working panels and ticket rows remain flat.

Button background/text transitions last (160ms) with `ease-out`. No decorative animation is part of this system. The shipped reduced-motion query disables animations, transitions and smooth scrolling. Keyboard focus uses an accent outline (3px), offset (3px); search and chat containers use a focus-within outline (2px), offset (2px). Focus inside the rail and login brand uses the pale rail-focus color.

## Shapes

Controls are gently rounded using the control radius; tags and journey stages use the smaller badge radius. Panels, message bubbles and notification menus use the panel radius; dialogs use the larger dialog radius. Department marks use the department radius, reducing to the control radius in smaller instances. Avatars, counts and small state dots are circular.

Messages keep a directional corner: outgoing bottom-right and incoming bottom-left reduce to the tight radius. Borders are restrained one-pixel semantic dividers. SVG icons use `currentColor`, rounded caps/joins and stroke width (1.7), with a default (20px) size and local (15–28px) exceptions. IT/HR/FAC/FIN/PROC monograms identify departments and do not replace action icons.

## Components

### Buttons

Primary and secondary actions are direct, compact and readable. Their frontmatter recipes own padding, type, color and radius; both have a baseline minimum height (44px), centered contents and a (9px) icon gap. Primary hover uses the corresponding accent-hover token. Secondary buttons have a one-pixel divider border and blue hover. Text actions use accent ink and underline on hover. Disabled controls keep the forbidden cursor and opacity (.6). Dark primary actions explicitly use the dark button ink. A class name suggesting danger does not create a separate red confirmation style in the current build.

### Chips

State tags have a small radius, paired semantic text/background colors, semibold labels and a (6px) dot gap. The state dot is (7px), filled with current color. Pending, progress, complete and urgent remain distinct in both themes. Normal-priority tags use the quiet surface and secondary ink. These are informative tags rather than pretend interactive controls.

### Cards / Containers

Working panels use the panel recipe, a semantic one-pixel border and no shadow. Desktop administration padding is (24px), then (20px) at 1250px and (18px 16px) at 900px. Queue rows remain a continuous divided list: default surface, quiet hover and blue selected state. Department marks, ticket references, labeled status and unread badges retain row identity.

### Inputs / Fields

Native inputs, selects and textareas use the input recipe, one-pixel divider border and accent caret. Placeholder text uses secondary ink at full opacity. Disabled inputs use the quiet surface. Search is a bordered compound field with an inline SVG and a contained input; keyboard hints remain a small adjunct. Textarea reading line height is (1.75). Search and chat focus stays on the container, preserving visible focus when the inner control has no outline. Checkbox size is (20px), with semantic accent.

### Navigation

The slate rail uses readable pale text, subdued icons and tabular counts. Rows use the navigation recipe; active rows are pale blue with dark slate ink. Hover is a quieter slate tone. Full Thai department names provide wayfinding. Mobile administration navigation becomes a horizontal strip; employee and agent queues rely on the mobile workspace and list/detail interaction.

### Request Journey and Conversation

The request-details disclosure groups the ordered three-stage request strip, assignment, original description and impact. The signature request strip is an ordered three-stage sequence. Each stage is a compact rounded cell with its numbered circular marker; reached stages use completion tokens and future stages use quiet surface/secondary ink. The strip supplements the labeled status and ownership context.

The cool conversation feed contains incoming working-surface bubbles and outgoing blue bubbles. Authors, timestamps and wrapping message text maintain an explicit reading order. The composer uses a bordered working surface, a quiet action footer and visible container focus; sending stays a primary action. History uses a thin vertical divider with semantic dots, not elevated cards. A labeled connection indicator distinguishes live delivery from reconnecting, alongside a manual message-refresh action. The message log and composer remain visibly separate; optional details and history share the outer detail scroll.

## Do's and Don'ts

### Do:

- **Do** use full Thai department names in navigation, filters and request context; short IT/HR/FAC/FIN/PROC marks may identify compact avatars.
- **Do** reuse semantic custom properties so light and dark modes keep the same hierarchy.
- **Do** keep status words, ownership and the next service action legible.
- **Do** preserve visible keyboard focus and honor reduced motion.
- **Do** preserve the familiar rail, queue and detail organization, with a labeled return from mobile detail.

### Don't:

- **Don't** replace Thai text labels with color or icons alone.
- **Don't** add decorative dashboard cards that compete with service actions.
- **Don't** add shadows to ordinary rows and working panels.
- **Don't** add a second display face or fetch fonts from an external service at runtime.
