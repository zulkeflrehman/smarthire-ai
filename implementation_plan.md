# Implementation Plan — UI/UX Redesign & Candidate Detail Scroll Fix

This plan outlines the deep UI/UX redesign and functional improvements for **SmartHire AI**. It focuses on fixing critical layout issues (such as the inability to scroll the candidate results table or read the candidate profile details) and upgrading the application's overall styling to an ultra-premium, cohesive dark glassmorphism design.

---

## The Walkthroughs (User Journeys) in SmartHire AI

Before implementing the redesign, here are the core user walkthroughs of the application:

1. **Recruitment Command (Dashboard) Walkthrough**:
   - **User Flow:** Recruiter opens the app, views system-wide statistics (Job Postings, Resumes Uploaded, Screened by AI, Shortlisted), sees a list of recent jobs, and checks a quick panel of top candidate matches.
   - **Current Design:** Uses dark background and basic panels.
   - **Redesign Upgrades:** Premium neon borders, glow effects for top statistics, slide-in animation for table rows, and interactive hover scales on metrics cards.

2. **Job Posting Creation Walkthrough**:
   - **User Flow:** Recruiter clicks "New Job", inputs job details (Title, Company, Location, Description, and Required Skills), and submits.
   - **Current Design:** Simple form fields.
   - **Redesign Upgrades:** Interactive form inputs with glowing focus states, floating labels where appropriate, and structured info panels describing how the ML weights function.

3. **Resume Batch Upload Walkthrough**:
   - **User Flow:** Recruiter is redirected to upload resumes for a job. They drag-and-drop or browse files (PDF/DOCX), view a list of selected files with validation, and click "Upload & Parse".
   - **Current Design:** Standard file list and dashed box.
   - **Redesign Upgrades:** Dynamic drag-over glass blur, pulsing upload states, parsing status bars, and custom document icons (PDF vs DOCX).

4. **AI Screening Results Walkthrough (Critical Issue Here)**:
   - **User Flow:** Recruiter runs screening and views a ranked candidate list with BERT/TF-IDF similarity percentages, matched skills, status updates, and a Chart.js score histogram.
   - **Critical Issue:** Recruiter **cannot scroll horizontally** or see the rightmost columns (Status dropdown, Matched Skills, and the AI Profile view link) on many screen widths because the table container has `overflow: hidden`.
   - **Redesign Upgrades:** Change to `overflow-x: auto` with a customized scrollbar, sticky candidate columns, polished status badges, and an updated Chart.js dark-mode theme.

5. **AI Candidate Profile Detail Walkthrough (Critical Issue Here)**:
   - **User Flow:** Recruiter clicks "View Profile" or "AI ✓" to open a candidate's details. They can generate an AI Evaluation (Strengths, Weaknesses, recommendation), get targeted Interview Questions, and chat with an AI recruiter bot.
   - **Critical Issue:** The page uses undefined CSS variables (`var(--slate-900)`, `var(--slate-500)`, `var(--slate-100)`, `var(--indigo-light)`) which render text as dark grey or black, making it **completely invisible** on the dark background. The chatbot messages also render transparently and are unreadable.
   - **Redesign Upgrades:** Standardize variables to match the Obsidian Glass system. Implement beautifully styled RAG chat interfaces (electric-purple bubbles for questions, glassmorphic bubbles for answers), structured strength/weakness blocks with vibrant borders, and smooth loading spinners.

---

## User Review Required

> [!IMPORTANT]
> - **Table Overflow Fix:** The results table horizontal scrollbar will be styled using subtle modern scroll tracks (6px height, rounded corners, glowing purple thumb on hover) to blend into the dark theme without cluttering the screen.
> - **Theme Standardisation:** We will completely eliminate the broken light-theme variables in `candidate_detail.html` and unify them with the dark Obsidian glass variables in `custom.css`.

---

## Proposed Changes

### 1. Global CSS Stylesheet

#### [MODIFY] [custom.css](file:///d:/al/project/smarthire_ai/static/css/custom.css)
- Change `.table-responsive` from `overflow: hidden;` to `overflow-x: auto;` to allow horizontal scrolling of candidate lists.
- Add modern, sleek scrollbar rules for the candidate list table and Chatbot window.
- Add utility styling classes for dark-themed strength/weakness cards and RAG chat bubbles.
- Add custom transitions (`transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1)`) for links, select lists, and buttons.
- Create glow utility classes (`.glow-purple`, `.glow-green`, `.glow-pink`) for metrics card hover actions.

---

### 2. Candidate Profiles & Chatbot

#### [MODIFY] [candidate_detail.html](file:///d:/al/project/smarthire_ai/screening/templates/screening/candidate_detail.html)
- Replace all broken variables:
  - `var(--slate-100)` $\rightarrow$ `rgba(255, 255, 255, 0.08)`
  - `var(--slate-900)` $\rightarrow$ `#FFFFFF` (Primary Text)
  - `var(--slate-700)`, `var(--slate-600)` $\rightarrow$ `var(--text-secondary)`
  - `var(--slate-500)` $\rightarrow$ `var(--text-secondary)`
  - `var(--slate-400)` $\rightarrow$ `var(--text-muted)`
  - `var(--indigo)`, `var(--indigo-500)` $\rightarrow$ `var(--primary)`
  - `var(--indigo-light)` $\rightarrow$ `rgba(139, 92, 246, 0.15)`
  - `var(--red-light)` $\rightarrow$ `var(--danger-bg)`
  - `var(--green-light)` $\rightarrow$ `var(--success-bg)`
  - `var(--amber-light)` $\rightarrow$ `var(--warning-bg)`
- Redesign the chatbot container, messages history, and inputs. Questions will appear as premium right-aligned purple glass bubbles, and answers as left-aligned frosted-glass panels.
- Fix text color in the Strengths, Weaknesses, and Recommendation boxes to ensure readability.

---

### 3. Screening Results List

#### [MODIFY] [results.html](file:///d:/al/project/smarthire_ai/screening/templates/screening/results.html)
- Adjust the layout of the candidate table to fit details beautifully on all viewports.
- Enhance the matched skills list column to prevent excessive wrapping.
- Update the page pagination footer style.
- Customize the Chart.js grid and tooltip colors so that the histogram fits seamlessly inside the premium dark layout.

---

### 4. General Templates Polish

#### [MODIFY] [base.html](file:///d:/al/project/smarthire_ai/screening/templates/screening/base.html)
- Add global page fade-in animation using CSS transitions.
- Enhance sidebar navigation spacing and active links with purple glow highlights.

#### [MODIFY] [index.html](file:///d:/al/project/smarthire_ai/screening/templates/screening/index.html)
- Polish metrics card alignments.
- Add subtle hover transformations to the recent jobs list rows.

#### [MODIFY] [job_detail.html](file:///d:/al/project/smarthire_ai/screening/templates/screening/job_detail.html)
- Enhance the job metadata presentation (alignment, font weight, spacing).
- Update the candidate table style to align with the results list.

#### [MODIFY] [upload_resumes.html](file:///d:/al/project/smarthire_ai/screening/templates/screening/upload_resumes.html)
- Enhance drag-and-drop zone hover animations.
- Refactor file list item borders and color code states.

---

## Verification Plan

### Automated Tests
- Run the Django development server locally using:
  ```bash
  python manage.py runserver
  ```
  *(We will set up a local virtual environment first using `C:\Users\zulke\.local\bin\python3.14.exe` to run all commands).*
- Validate that there are no CSS syntax errors and the page structure compiles correctly.

### Manual Verification
1. **Scrolling Test:** Open the **Screening Results** page on both a desktop screen and a narrowed viewport. Verify that the table overflows cleanly with a visible horizontal scrollbar, and the "AI Profile" view link is fully accessible.
2. **Text Readability Test:** Open the **Candidate Detail** page. Verify that:
   - Candidate Name and Email are fully readable (white/silver text).
   - Score percentage text in the ring center is white.
   - AI Evaluation strengths, weaknesses, and chatbot message bubbles have high contrast and look premium.
3. **Transition Test:** Verify that navigation hover states, dropdown changes, and buttons scale or fade smoothly.
