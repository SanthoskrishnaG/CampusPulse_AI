# CampusPulse AI — UI & Theme Redesign Changelog

## 1. Overview & Design Direction
The presentation layer of **CampusPulse AI** (Coimbatore Institute of Technology Smart Campus) has been redesigned into a modern **"AI SaaS Command Center"**. Inspired by modern product designs like Linear, Vercel, and Stripe dashboards, the redesign introduces:
- A data-forward visual hierarchy with an 8px spacing grid.
- A light mode by default (#F6F8FC background, #FFFFFF surface cards) alongside a dark mode (#0A0F1E background, #111827 surface cards).
- A unified design token architecture with WCAG AA compliant contrast ratios and visible focus rings.
- Smooth transitions (150–250ms) and entrance animations that respect `prefers-reduced-motion`.
- **Zero changes to backend logic, API routes, or ML code.**

---

## 2. Central Design Tokens Architecture
The theme tokens and reusable component library live in:
- **`static/css/tokens.css`** (Central design tokens, color palette, typography scale, 8px grid, shadows, and component classes)
- **`static/css/style.css`** (Mapped legacy CSS variables to the central tokens for backward compatibility across all campus subsystems)

### Primary Color Tokens
| Token Name | Value | Usage |
|---|---|---|
| `--color-primary` | `#4F46E5` | Primary buttons, active tabs, brand accents |
| `--color-primary-hover` | `#4338CA` | Hover state for primary buttons |
| `--color-primary-soft` | `#EEF2FF` | Pill badges, subtle tints, active card highlights |
| `--color-ai` | `#06B6D4` | AI engine badge, pulse dots, telemetry indicators |
| `--color-ai-soft` | `rgba(6, 182, 212, 0.10)` | AI insight cards, neural ensemble backgrounds |
| `--brand-gradient` | `linear-gradient(135deg, #4F46E5 0%, #7C3AED 50%, #06B6D4 100%)` | Hero headline highlights and key action CTAs |
| `--sidebar-bg` | `#0B1220` | Deep navy sidebar background |
| `--sidebar-text` | `#CBD5E1` | Sidebar navigation link labels |
| `--sidebar-active` | `linear-gradient(135deg, #4F46E5 0%, #7C3AED 100%)` | Active navigation pill with white text & glow |

### Semantic Tokens (Light & Dark Variants)
- **Success**: `#10B981` (Soft: `#ECFDF5` in Light, `rgba(16, 185, 129, 0.15)` in Dark)
- **Warning**: `#F59E0B` (Soft: `#FFFBEB` in Light, `rgba(245, 158, 11, 0.15)` in Dark)
- **Danger**: `#EF4444` (Soft: `#FEF2F2` in Light, `rgba(239, 68, 68, 0.15)` in Dark)
- **Info**: `#3B82F6` (Soft: `#EFF6FF` in Light, `rgba(59, 130, 246, 0.15)` in Dark)

### Typography Scale
- **UI Font**: `"Inter", -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, sans-serif`
- **Headings Font**: `"Plus Jakarta Sans", "Outfit", sans-serif`
- **Monospace & Numerical**: `ui-monospace, "SFMono-Regular", Menlo, Monaco, Consolas, monospace` with `font-variant-numeric: tabular-nums` on all metrics and KPIs.

---

## 3. Component Library Updates
The following reusable component styles were established in `tokens.css`:
- **Buttons (`.btn`, `.btn-primary`, `.btn-secondary`, `.btn-ghost`, `.btn-sm`, `.btn-lg`)**: Rounded with 8px radius, smooth 150ms transitions, focus rings, and active states.
- **Cards & Surfaces (`.panel-card`, `.card-interactive`)**: Border-radius of 12–16px, 1px border (`var(--border-color)`), elevated on hover with soft shadow.
- **Badges & Chips (`.badge`, `.badge-primary`, `.badge-ai`, `.chip`)**: Rounded pills for department codes, status flags, and research specialization tags.
- **Stat Cards (`.stat-card-modern`)**: 4-column grid (2 rows of 4, no orphan rows), tabular numbers, trend arrows with percentage chips, and subtle sparkline bars.
- **Tables (`.table-clean`)**: Sticky header, subtle border dividers, row hover highlights, and right-aligned actions.
- **Horizontal Stepper (`.stepper-horizontal`)**: Numbered circular badges connected by animated lines for multi-step wizards.
- **Modals (`.modal-backdrop`, `.modal-card`)**: Glassmorphism backdrop-blur, smooth entrance, confirmation dialogs.
- **Skeleton Loaders & Empty States**: Shimmer animation for asynchronous loading states.

---

## 4. Shell, Sidebar & Topbar Modernization
- **Sidebar (`templates/base.html`)**:
  - Deep navy `#0B1220` with grouped uppercase section headers (`INSTITUTIONAL CORE`, `STUDENT ENGAGEMENT`, `SMART CAMPUS OPERATIONS`, `ANALYTICS & ADMIN`).
  - Active navigation pill featuring indigo→violet gradient with soft glow.
  - Replaced legacy text box with a modern **CIT Eco-Pulse Telemetry Card** (91% Campus Sustainability with animated progress bar).
  - Modern bottom user card displaying authenticated user name and role.
- **Sticky Glassmorphic Topbar**:
  - Global Search with `Ctrl + K` badge opening the command palette.
  - Real-time weather chip for Coimbatore microclimate.
  - **"AI Engine • Online" chip & dropdown**: Fully theme-adaptive with high-contrast surface `#111827`, border `#1F2937`, crisp `#F8FAFC` headings, `#E2E8F0` telemetry rows, vivid green status dots, and expanded width (320px) preventing text truncation in Dark Mode.
  - Polished Light/Dark mode toggle (`#themeToggleBtn`) with `localStorage` persistence and zero Flash of Unstyled Content (FOUC).
  - Dynamic Role Switcher reflecting the active user role (`Super Admin`, `Faculty`, `Student`, etc.) with instant demo perspective switching.
  - Profile menu with initials avatar and role badge.

---

## 5. Page-by-Page Redesign

### 1. Dashboard (`templates/common/home.html`)
- **Two-Column Hero Section**:
  - Left: Headline `"CIT Smart Campus. Powered by AI."` with gradient accent on `"Powered by AI."`, subtitle, primary CTA `"Enter Campus Portal"`, ghost button `"Watch Demo"`, and avatar stack.
  - Right: Replaced the flat rendered illustration with a high-definition **3D isometric CIT campus digital twin model** (`static/images/cit_campus_3d_twin.jpg`), layered with non-overlapping smart floating telemetry pills (Academic Blocks, CIT Main Complex, CIT Sports Complex, Residential Hostels) with frosted glassmorphism backdrop-blur.
- **8 KPI Cards in 4-Column Grid**:
  - Clean 4-column layout (2 rows of 4, zero orphan rows).
  - Icon in tinted square, label, big tabular metric, trend chip (% with green up / red down arrow), and sparkline bar.
- **Subsystem Telemetry Cards**:
  - 4 equal-height telemetry cards (Hostel & Facilities, Complaints AI, Academic Risk AI, Fleet Tracker).
  - 2-line clamp with tooltips, progress bars for occupancy/SLA, and live status dots.
- **AI Alert Center**:
  - 2-column severity-coded alert rows with left border accents (amber/red), module tags, timestamps, and dismiss / view actions.
- **Campus AI Intelligence Core Pipeline**:
  - Horizontal 5-stage stepper (Telemetry → Neural Ensembles → Risk & ETA → Recommendations → Interventions) connected by an animated progress line.
  - 12 ML model tiles in a responsive grid with status dots and hover glow.

### 2. Academic Departments (`templates/departments/list.html`)
- Color-coded top-accent stripes per department (AERO, AIDS, BIOTECH, CIVIL, CSE, ECE, EEE, IT, MECH).
- Code chip, block badge, HOD name, and laboratory facility counters.
- Mini stats 3-column pill row: Scholars, Faculty, and Risk % with semantic risk coloring.
- Interactive client-side search input and department category filter chips (Computing & AI, Circuits & Electrical, Core Engineering, Bio Sciences).

### 3. Faculty Directory (`templates/faculty/list.html`)
- Circular initials avatar with dynamic gradient fallback.
- Faculty name, designation badge, and department code pill.
- Research specialization areas displayed as clean tags.
- Cabin location and office hours with dedicated SVG icons.
- Ghost button `"View Mentor Profile"` with arrow icon and hover elevation.
- Department filter chips and real-time mentor search filter.

### 4. Academic Risk AI (`templates/academics/risk_dashboard.html`)
- Semantic KPI cards (Evaluated Cohort in Indigo, High Risk in Red, Moderate Risk in Amber, Healthy in Green, Active Interventions in Cyan).
- Cohort distribution segmented progress bar with legend breakdown.
- Sortable risk table with colored risk badges and percentage probability bars.
- Prominent red `"Auto-Dispatch High-Risk Interventions"` button with an interactive confirmation modal.
- Student deep-dive modal displaying 5-week longitudinal trajectory and feature attribution.

### 5. Student Onboarding / Hostel Form (`templates/accounts/accommodation_setup.html`)
- 3-step wizard with visual progress stepper (`Residency` → `Category` → `Building & Room`).
- Selectable cards with clear active state (2px indigo border, soft background, and checkmark badge).
- Clean dropdowns for assigned buildings with capacity details.
- Real-time inline validation feedback indicating completion readiness.

---

## 6. Data Consistency Fixes
1. **Ongoing Events**: Corrected dashboard binding from the student count (1,550) to the real ongoing campus events count (18).
2. **Faculty Count**: Unified across Dashboard, Departments, and Faculty Directory to 176 mentors (sum of all 9 department faculty records).
3. **Parking Occupancy**: Unified across Dashboard and telemetry widgets to 69% (151 occupied of 220 total parking bays).
4. **Faculty Sample Names**: Verified 176 unique faculty records across departments and research specializations without duplicate names.

---

## 7. Responsive & Visual Verification
Verified and captured at all target viewports using headless Chrome:
- **Desktop (1440px)**:
  - `screenshots/dashboard_light_1440px.png` & `dashboard_dark_1440px.png`
  - `screenshots/departments_1440px.png` & `departments_dark_1440px.png`
  - `screenshots/faculty_1440px.png` & `faculty_dark_1440px.png`
  - `screenshots/academic_risk_ai_1440px.png` & `academic_risk_ai_dark_1440px.png`
  - `screenshots/hostel_onboarding_1440px.png`
- **Tablet (1024px)**: `screenshots/dashboard_light_1024px.png` (sidebar auto-collapses, telemetry cards wrap to 2x2 grid without clipping).
- **Mobile (390px)**: `screenshots/dashboard_light_390px.png` (full fluid stacking, horizontal scrolling avoided, touch-friendly tap targets >= 44px).
