# Multi-Site Sign-In Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Add support for signing into multiple SKPORT game pages in one scheduled run, while keeping Endfield as the default and allowing each site to either share or separate browser profiles.

**Architecture:** Extend configuration to support a list of enabled site entries with per-site URL, state path, and browser profile path. Keep the existing single-site config format working by normalizing legacy settings into a one-site list. Run the existing browser flow once per enabled site, with per-site gating and logging so one game's status never blocks the other.

**Tech Stack:** Python 3.11+, Playwright, Windows Task Scheduler, unittest

---

### Task 1: Add multi-site configuration model

**Files:**
- Modify: `C:\Users\jerry\OneDrive\桌面\AGs\EFCheck\efcheck\config.py`
- Modify: `C:\Users\jerry\OneDrive\桌面\AGs\EFCheck\config\settings.example.json`
- Test: `C:\Users\jerry\OneDrive\桌面\AGs\EFCheck\tests\test_config.py`

- [ ] **Step 1: Write failing tests for multi-site config normalization**
- [ ] **Step 2: Run the config tests to verify they fail**
- [ ] **Step 3: Add `SiteSettings` and normalize legacy config into a default Endfield site**
- [ ] **Step 4: Add explicit multi-site parsing and validation**
- [ ] **Step 5: Re-run the config tests and verify they pass**

### Task 2: Capture sessions by site

**Files:**
- Modify: `C:\Users\jerry\OneDrive\桌面\AGs\EFCheck\capture_session.py`
- Test: `C:\Users\jerry\OneDrive\桌面\AGs\EFCheck\tests\test_capture_session.py`

- [ ] **Step 1: Write failing tests for selecting a site and handling unknown site names**
- [ ] **Step 2: Run the capture-session tests to verify they fail**
- [ ] **Step 3: Add `--site` support and resolve the chosen site's URL/profile**
- [ ] **Step 4: Keep legacy behavior equivalent to selecting the default Endfield site**
- [ ] **Step 5: Re-run the capture-session tests and verify they pass**

### Task 3: Execute sign-in per enabled site

**Files:**
- Modify: `C:\Users\jerry\OneDrive\桌面\AGs\EFCheck\sign_in.py`
- Modify: `C:\Users\jerry\OneDrive\桌面\AGs\EFCheck\efcheck\daily_gate.py`
- Modify: `C:\Users\jerry\OneDrive\桌面\AGs\EFCheck\efcheck\statuses.py` (only if needed)
- Test: `C:\Users\jerry\OneDrive\桌面\AGs\EFCheck\tests\test_sign_in.py`
- Test: `C:\Users\jerry\OneDrive\桌面\AGs\EFCheck\tests\test_daily_gate.py`

- [ ] **Step 1: Write failing tests for multi-site runs, per-site state separation, and aggregated exit behavior**
- [ ] **Step 2: Run the sign-in and gate tests to verify they fail**
- [ ] **Step 3: Update the sign-in runner to iterate over enabled sites**
- [ ] **Step 4: Use per-site state file paths so Endfield and Arknights do not share retry gates**
- [ ] **Step 5: Include site names in console output and log entries**
- [ ] **Step 6: Re-run the sign-in and gate tests and verify they pass**

### Task 4: Update docs and packaging for multi-site usage

**Files:**
- Modify: `C:\Users\jerry\OneDrive\桌面\AGs\EFCheck\README.md`
- Modify: `C:\Users\jerry\OneDrive\桌面\AGs\EFCheck\README.zh-TW.md`
- Modify: `C:\Users\jerry\OneDrive\桌面\AGs\EFCheck\tools\package_windows_release.ps1` (only if release contents need changes)

- [ ] **Step 1: Document the new `sites` configuration structure and default behavior**
- [ ] **Step 2: Document how to add Arknights with shared or separate browser profiles**
- [ ] **Step 3: Document `capture_session.py --site` usage**
- [ ] **Step 4: Verify docs are consistent with the implemented behavior**

### Task 5: Final verification

**Files:**
- Modify: none unless verification finds issues

- [ ] **Step 1: Run `C:\Users\jerry\OneDrive\桌面\AGs\EFCheck\.venv\Scripts\python.exe -m unittest discover -s tests -v`**
- [ ] **Step 2: Run `C:\Users\jerry\OneDrive\桌面\AGs\EFCheck\.venv\Scripts\python.exe .\sign_in.py --dry-run --force` against legacy config**
- [ ] **Step 3: Run `C:\Users\jerry\OneDrive\桌面\AGs\EFCheck\.venv\Scripts\python.exe .\capture_session.py --help`**
- [ ] **Step 4: Report any remaining Arknights-specific runtime risk that still requires live page verification**
