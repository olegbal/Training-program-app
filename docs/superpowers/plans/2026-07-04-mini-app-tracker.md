# Mini App Tracker Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Build the MVP Telegram Mini App tracker screens against the existing workout API.

**Architecture:** Keep the app as a small React/Vite application with local state in `App.tsx`, typed API calls in `src/api/client.ts`, and focused screen/components under `src/screens` and `src/components`. The UI is Telegram-first, mobile-dense, and uses plain CSS.

**Tech Stack:** React, TypeScript, Vite, Vitest, Testing Library, plain CSS.

---

### Task 1: Frontend Test Harness

**Files:**
- Modify: `apps/mini-app/package.json`
- Modify: `apps/mini-app/vite.config.ts`
- Create: `apps/mini-app/src/test/setup.ts`

- [x] **Step 1: Add test dependencies and scripts**

Add Vitest, jsdom, and Testing Library to `devDependencies`; add `test` script.

- [x] **Step 2: Configure Vite test environment**

Set `test.environment` to `jsdom` and load `src/test/setup.ts`.

- [x] **Step 3: Verify**

Run: `npm test -- --run`
Expected: exits successfully once tests exist, or no-test status before app tests are added.

### Task 2: API Client

**Files:**
- Modify: `apps/mini-app/src/api/client.ts`
- Create: `apps/mini-app/src/api/client.test.ts`

- [x] **Step 1: Write failing client tests**

Cover Telegram auth, Bearer headers, add set payloads, and history parsing through mocked `fetch`.

- [x] **Step 2: Run client tests and verify red**

Run: `npm test -- --run src/api/client.test.ts`
Expected: FAIL because the new functions do not exist.

- [x] **Step 3: Implement typed API client**

Add `authTelegram`, `getTodayWorkout`, `startTodayWorkout`, `completeWorkout`, `skipWorkout`, `addSet`, `updateSet`, `deleteSet`, `completeExercise`, `skipExercise`, `replaceExercise`, `getHistory`, and `searchExercises`.

- [x] **Step 4: Verify green**

Run: `npm test -- --run src/api/client.test.ts`
Expected: PASS.

### Task 3: App Screens

**Files:**
- Modify: `apps/mini-app/src/App.tsx`
- Modify: `apps/mini-app/src/screens/TodayScreen.tsx`
- Create: `apps/mini-app/src/screens/WorkoutScreen.tsx`
- Create: `apps/mini-app/src/screens/HistoryScreen.tsx`
- Create: `apps/mini-app/src/screens/LibraryScreen.tsx`
- Create: `apps/mini-app/src/components/ExerciseCard.tsx`
- Create: `apps/mini-app/src/components/ExerciseModal.tsx`
- Create: `apps/mini-app/src/components/SetEditor.tsx`
- Create: `apps/mini-app/src/types/workouts.ts`
- Create: `apps/mini-app/src/App.test.tsx`

- [x] **Step 1: Write failing UI tests**

Cover Today render, opening GIF modal, submitting a set, and completing an exercise with mocked API calls.

- [x] **Step 2: Run UI tests and verify red**

Run: `npm test -- --run src/App.test.tsx`
Expected: FAIL because the tracker UI does not exist.

- [x] **Step 3: Implement screens and components**

Use local state, no router. Show Today, Workout, History, and Library with actions wired to the API client.

- [x] **Step 4: Verify green**

Run: `npm test -- --run src/App.test.tsx`
Expected: PASS.

### Task 4: Styling and Build

**Files:**
- Modify: `apps/mini-app/src/styles.css`

- [x] **Step 1: Replace skeleton CSS**

Add responsive Telegram-first layout, stable card dimensions, button states, modal styling, set rows, tabs, and library filters.

- [x] **Step 2: Verify frontend**

Run: `npm test -- --run`
Run: `npm run build`
Expected: both pass.

- [x] **Step 3: Verify repo**

Run: `apps/api/.venv/bin/python -m pytest tests -q` from `apps/api`
Run: `docker compose build mini-app`
Expected: both pass.

- [x] **Step 4: Commit**

Commit message: `feat: build mini app workout tracker`
