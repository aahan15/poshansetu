# PoshanSetu Prototype v0.2

A more complete local demo for the Seva First Innovation Challenge 2026.

## What's new in v0.2
- Refreshed, responsive visual styling
- English / Marathi interface labels
- SQLite persistence for local demo cases and activity history
- Visual referral journey
- Supervisor review queue and operational actions
- Offline-mode simulation with queued activity events and a sync control
- Expanded pilot guidance, safety notes, and proposed impact scorecard
- CSV export

## Requirements
- Python 3.10+
- Internet is needed only to install Python packages; the app itself runs locally.
- Streamlit and pandas

## Run on Windows (PowerShell)
1. Extract this ZIP.
2. Open the extracted folder in VS Code or PowerShell.
3. Run:

```powershell
python -m venv .venv
.venv\Scripts\Activate.ps1
pip install -r requirements.txt
streamlit run app.py
```

## Run on macOS / Linux
```bash
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
streamlit run app.py
```

Open the local URL Streamlit prints (normally http://localhost:8501).

## Suggested demo sequence
1. Dashboard: show total, open, due-today, and overdue cases.
2. Follow-up register: select PS-1001, change its status/outcome or record a barrier.
3. Referral journey: show the stages and inspect the case's current stage.
4. Supervisor desk: review the overdue/unresolved queue and take a demo action.
5. New follow-up: create a fictional case with a unique code such as DEMO-M-006.
6. Reports: download the demo case CSV.
7. Switch to Marathi and show key navigation labels.
8. Toggle offline simulation, make a change, then use Sync queued changes to demonstrate queued activity events.

## Important behavior and limitations
- Preloaded cases are fictional. Do not enter real beneficiary identifiers, personal details, or health information.
- SQLite database file `poshansetu_demo.db` is created beside `app.py` and persists demo records locally.
- The offline toggle is a demonstration of queued activity events, not a complete offline-first implementation. Case edits still write to local SQLite while offline simulation is active.
- There is no production-grade authentication, multi-user permission system, cloud sync, SMS/WhatsApp, POSHAN Tracker integration, clinical decision support, or medical diagnosis/treatment.
- For a real pilot, secure hosting, appropriate approvals, qualified clinical review, privacy/security controls, and workflow validation are required.
- Metrics shown in the app are calculated from synthetic records; never describe them as real pilot outcomes.

## Resetting sample data
For a clean reset, stop Streamlit, then delete `poshansetu_demo.db`. Restart the app; the synthetic sample cases will be recreated. Do not delete the database if you want to retain local demo edits.
