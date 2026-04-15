# Debug & Cleanup Action Log

**Date:** 2026-04-15
**Purpose:** Record every change made during the debug/cleanup pass, and list
cleanup candidates for the documentation-writing agent to finish.

---

## Root Cause: macOS "opens another version of the application"

**Diagnosis:** `START_HERE.sh` was the only launcher shipped for macOS. On
macOS, double-clicking a `.sh` file in Finder does **not** execute it — Finder
opens it in the default editor (Xcode, Script Editor, or TextEdit depending on
system config). This is exactly what the user reported as "opening another
version of the application."

Finder only executes shell scripts on double-click when they use the `.command`
extension. That file type is routed through Terminal.app by LaunchServices.

**Secondary macOS noise source (fixed):** `launcher.py` called
`check_tkinter_available()`, which imports tkinter and briefly creates a Tk
root. On macOS this flashes a "Python Rocket" app icon in the Dock every
launch — reinforcing the "another app" perception. The subsequent
`launch_gui_mode()` was dead code: it always returned False and fell back to
CLI mode. Both were removed.

---

## Fixes Applied

### 1. New macOS launchers (primary fix)

- **Created `START_HERE.command`** — macOS double-click launcher (runs in
  Terminal). Wraps the same Python launcher path as `START_HERE.sh`. Includes
  a header comment explaining why `.sh` is wrong on macOS and how to handle
  Gatekeeper / quarantine on first launch.
- **Created `install.command`** — macOS double-click installer. Delegates to
  `install.sh` so there is a single source of truth for install steps.
- Both are `chmod +x`.

### 2. `launcher.py` cleanup

- Removed dead `launch_gui_mode()` function (always returned False).
- Removed `check_tkinter_available()` call (caused Python Rocket icon flash on
  macOS).
- Removed `--no-gui` CLI flag (no longer meaningful).
- Removed unused `check_tkinter_available` import.

### 3. `utils/platform_utils.py`

- Removed now-unused `check_tkinter_available()` function.

### 4. `app.py` port bug (affected all OSes, surfaced during Linux test)

- Previously `app.run(... port=5000)` was hardcoded and ignored the
  `FLASK_RUN_PORT` env var that `launcher.py` sets. If port 5000 was busy the
  launcher would select an alternate port, set `FLASK_RUN_PORT`, but app.py
  would still try 5000 and fail with "Address already in use."
- Now reads `FLASK_RUN_PORT` (default 5000).
- Also added `use_reloader=False` to the debug-mode `app.run` so Flask's
  auto-reloader doesn't spawn a child process that confuses the launcher's
  subprocess management.

### 5. `install.sh`

- Chmod +x for the new `.command` files.
- Prints a macOS-specific hint pointing users at `START_HERE.command`, not
  `.sh`.
- Final "Next steps" section adapts to macOS vs Linux.

### 6. `GET_STARTED.md` and `README.md`

- Updated "Start the Application" / Quick Start to list all three launchers
  explicitly (`.bat`, `.command`, `.sh`) and warn macOS users away from the
  `.sh` file. Added Gatekeeper note.
- Updated the Mac desktop-shortcut instructions to reference
  `START_HERE.command`.

---

## Validated Installation Workflows

| OS       | Method                                    | Result |
|----------|-------------------------------------------|--------|
| Linux    | `bash install.sh` in a clean copy         | ✅ venv built, deps installed, no errors |
| Linux    | `./venv/bin/python launcher.py --port N`  | ✅ Flask serves 200 OK on selected port |
| Linux    | Direct `python app.py` with `FLASK_RUN_PORT` | ✅ respects env-provided port |
| macOS    | Logic verified statically (no macOS host available) | See "Not yet tested on a real macOS host" below |
| Windows  | `INSTALL_WINDOWS.bat` + `START_HERE.bat` — reviewed statically | ✅ port fix also benefits Windows |

### Not yet tested on a real macOS host

All macOS changes are shipped but this debug session ran on Linux. A macOS
verification pass should:

1. Double-click `install.command` in Finder and confirm it runs in Terminal.
2. Double-click `START_HERE.command`, confirm the browser opens to
   `http://localhost:<port>`.
3. Confirm no stray Python/Tk icon appears in the Dock during launch.
4. Test Gatekeeper: on first launch Finder may block the files with "cannot
   be opened because it is from an unidentified developer." The right-click →
   Open workflow is documented in the file header and should be covered in
   `INSTALLATION_GUIDE.md`.

---

## Cleanup Candidates (Not Yet Removed — Needs User Sign-Off)

These are recommended for the docs/cleanup agent. None are removed yet because
each deserves a confirmation step.

### High confidence — unrelated to the project

- **`agent-orchestration/`** (836 KB, 10 subdirectories) — Research notes on
  agent frameworks (Temporal, agent-communication, etc.). Completely
  unrelated to the license uploader. Grep shows zero references from app
  code. Already listed in `.gitignore` so it's not tracked — but it still
  lives in the working tree and clutters `ls`. **Recommend: physically
  remove from the working directory (it's not committed anywhere here).**

### Medium confidence — redundant documentation

Root-level `.md` files total ~3,300 lines across 6 files, with significant
overlap:

- `GET_STARTED.md` (139 lines) — quick-start
- `WINDOWS_QUICKSTART.md` (411 lines) — Windows quick-start (overlaps both
  `GET_STARTED.md` and `INSTALLATION_GUIDE.md`)
- `INSTALLATION_GUIDE.md` (1,150 lines) — full install reference
- `README.md` (429 lines) — has its own install section that duplicates
  `INSTALLATION_GUIDE.md` and `GET_STARTED.md`
- `USER_GUIDE.md` (848 lines)
- `CONTRIBUTING.md` (327 lines)

**Recommend:** Pick one quick-start file (`GET_STARTED.md`) and one deep-dive
install file (`INSTALLATION_GUIDE.md`). Fold `WINDOWS_QUICKSTART.md` into
`INSTALLATION_GUIDE.md`. Trim the install section in `README.md` to a pointer.

### `docs/` folder

12 files, much duplication:

- `BUILD_CHECKLIST.md`, `BUILD_INSTRUCTIONS.md`, `QUICK_BUILD_REFERENCE.md`,
  `EXECUTABLE_BUILD_SUMMARY.md`, `RUN_EXECUTABLE.md` — five files about
  building/running the PyInstaller executable. Could merge into one.
- `PRODUCTION_READINESS_REPORT.md`, `PRODUCTION_SECURITY_AUDIT.md` —
  point-in-time snapshots, likely stale; consider archiving.
- `SECURITY_GUIDE.md`, `DEPLOYMENT_GUIDE.md`, `DEVELOPER_GUIDE.md`,
  `API_DOCUMENTATION.md`, `TROUBLESHOOTING_GUIDE.md` — keep.

### Low confidence — keep but tidy

- `diagnose_windows.py` (29 KB) + `DIAGNOSE_WINDOWS.bat` — useful for Windows
  support. Keep.
- `test_security.py` at repo root — consider moving to `tests/`.
- `license_uploader.service`, `nginx.conf.example`, `gunicorn.conf.py` — keep;
  they're used by deployment docs.

### Repo-internal

- `.env` contains real-looking API keys. It's already in `.gitignore`. No
  action; just flagging for the user's awareness.

---

## File Touch List

### Added
- `START_HERE.command`
- `install.command`
- `ACTION_LOG.md` (this file)

### Modified
- `launcher.py` — removed GUI dead code, dropped `--no-gui` flag
- `utils/platform_utils.py` — removed unused `check_tkinter_available`
- `app.py` — honor `FLASK_RUN_PORT`, disable debug reloader
- `install.sh` — chmod new `.command` files, macOS-specific messaging
- `README.md` — clarified Quick Start per-OS
- `GET_STARTED.md` — clarified Quick Start per-OS, Mac desktop shortcut

### Unchanged (but reviewed)
- `START_HERE.sh`, `START_HERE.bat`, `INSTALL_WINDOWS.bat`, `build_unix.sh`,
  `build_windows.bat`, `license_uploader.spec`
