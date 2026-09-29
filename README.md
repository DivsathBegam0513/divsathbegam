# LegalEase

A complete local legal-document drafting application built from the supplied **LegalEase.pdf**: Streamlit frontend, FastAPI backend, Google Gemini integration, an editable preview, branding, automatic term tables, and TXT / DOCX / PDF export.

**Start in offline demo mode without an API key.** To generate real AI drafts, add your own Gemini key and change `AI_PROVIDER` as described below. Demo output is clearly marked as a template and is not AI-generated. Every draft requires professional review before use.

**Received this project as a ZIP?** Extract it first, then follow [START_HERE.md](START_HERE.md). On Windows, `Install-LegalEase.cmd` installs the runtime dependencies and creates a local `.env`. Use `Start-LegalEase.cmd` after installation.

## Quick start in VS Code on Windows

1. Open **VS Code → File → Open Folder** and select your extracted **LegalEase** folder. Open the whole folder, not an individual Python file.
2. Install the Microsoft **Python** extension if prompted. Install Python **3.12 or 3.13** if neither is available.
3. Select **Terminal → New Terminal**. If you already ran `Install-LegalEase.cmd`, go directly to step 5. Otherwise run:

   ```powershell
   py -3.13 -m venv .venv
   .\.venv\Scripts\python.exe -m pip install -r requirements-dev.txt
   ```

4. If `.env` is missing, run:

   ```powershell
   Copy-Item .env.example .env
   ```

   Do not overwrite an existing `.env` containing your settings. In VS Code press **Ctrl+Shift+P → Python: Select Interpreter → .venv\Scripts\python.exe**.

5. Start both services:

   ```powershell
   .\.venv\Scripts\python.exe run.py
   ```

6. Open **http://127.0.0.1:8501**. API documentation is at **http://127.0.0.1:8000/docs**. Keep the terminal running; **Ctrl+C** stops both services.

You can also double-click **Start-LegalEase.cmd** after setup. The launcher prints the browser address. No activation command or PowerShell execution-policy change is required for the Python commands above.

If you have Python 3.12 instead, replace `py -3.13` with `py -3.12`. The optional `setup.ps1` script automates installation when your PowerShell policy allows local scripts.

## Starting from Command Prompt

After completing installation, open Command Prompt in the project folder and run:

```bat
python main.py
```

`python app.py` and `python run.py` also start both services. These entry points automatically use the project's virtual environment for FastAPI and Streamlit, even if your default `python` points to another installation. You can also double-click `Start-LegalEase.cmd`.

Open http://127.0.0.1:8501 and keep the launcher running. Use Ctrl+C to stop it. Only start one launcher at a time. For intentionally separate services, use the commands later in this guide.

## Use the application

1. Choose NDA, employment contract, residential lease, freelance contract, service agreement, or a custom title.
2. Enter the parties and their roles. Enter terms separated by semicolons or new lines, the effective date, and the jurisdiction. **See an example** provides fictional inputs you can copy.
3. Click **Generate draft**. The sidebar identifies the provider; expand it using the top-left toggle if collapsed.
4. Read **Document preview**. In **Edit wording**, change the text and click **Apply edits**. The `## Key Terms` section becomes a table; edit its `-` lines to update the table.
5. Optionally use **Review notes → Review saved draft**. Gemini summarizes and identifies review points; demo mode only extracts text/headings and identifies visible placeholders.
6. Set a company name, serif/sans font, and optional PNG/JPEG logo. Click **Prepare downloads**, then download TXT, Word or PDF.

Downloads use the last **applied and prepared** version. Apply edits and prepare again after changes. Editing or generating a new draft invalidates earlier exports and review notes. TXT preserves text; fonts and logos apply to Word/PDF. The preview uses a standard reading style rather than reproducing page layout.

**Import a document** accepts UTF-8 TXT, DOCX and text-based PDF, up to 5 MB. PDFs are limited to 50 pages; extracted text is limited to 60,000 characters. Import extracts text rather than preserving original layout. Scanned PDFs require OCR outside this application.

## Enable real Gemini generation

Create an API key in [Google AI Studio](https://aistudio.google.com/apikey), then edit the root `.env` locally:

```dotenv
AI_PROVIDER=gemini
GEMINI_API_KEY=your_actual_key_here
GEMINI_MODEL=gemini-3.5-flash
BACKEND_URL=http://127.0.0.1:8000
BACKEND_API_KEY=
REQUEST_TIMEOUT_SECONDS=90
RATE_LIMIT_PER_MINUTE=30
```

Stop and restart both services after any configuration change. Confirm the Gemini submission checkbox before generating or reviewing. The configured model is replaceable with one available to your Google project; model access, billing and quota are controlled by Google. Your key stays in the server-side environment and must not be committed to Git.

The implementation uses the current `google-genai` SDK. The supplied PDF's legacy `google-generativeai` snippets were updated using Google's [migration guide](https://ai.google.dev/gemini-api/docs/migrate). The default model is based on the [current model catalog](https://ai.google.dev/gemini-api/docs/models), checked on September 23, 2026. After the user configured a key, live generation and structured document review succeeded using `gemini-3.5-flash`, and all three export formats were verified. This model was selected after `gemini-3.8-flash` returned HTTP 503 due to high demand. Availability can change; the app retries transient server failures once and displays the specific error if they persist.

Gemini drafting and review support **English, French, Spanish and German**. Demo mode is English only. Bundled Unicode fonts cover these scripts. PDF export rejects unsupported characters rather than silently dropping them; DOCX/TXT can preserve other scripts, whose rendering depends on fonts installed on your computer.

## Run tests

From the project folder, install the optional developer dependencies and run:

```powershell
.\.venv\Scripts\python.exe -m pip install -r requirements-dev.txt
.\.venv\Scripts\python.exe -m pytest -q
.\.venv\Scripts\python.exe -m ruff check .
.\.venv\Scripts\python.exe -m pip check
```

The automated suite uses offline data, mocked Gemini responses, API integration tests and Streamlit's AppTest. It never requires or spends an API key. It checks invalid requests, authentication, throttling, timeout/quota errors, edited exports, Unicode, logos, pagination, HTML escaping, import validation and the generate/edit/review/download UI flow.

With the application running, open a second terminal for a real HTTP check:

```powershell
.\.venv\Scripts\python.exe scripts\smoke_test.py
```

To test your configured Gemini key, set Gemini mode, restart, then explicitly permit sending the included fictional sample:

```powershell
.\.venv\Scripts\python.exe scripts\smoke_test.py --allow-gemini
```

This live check makes generation and review requests and may consume your provider quota. See [TEST_REPORT.md](TEST_REPORT.md) for the delivered verification results and remaining limitations.

## Run frontend and backend separately

Terminal 1:

```powershell
.\.venv\Scripts\python.exe -m uvicorn main:app --host 127.0.0.1 --port 8000 --reload
```

Terminal 2:

```powershell
.\.venv\Scripts\python.exe -m streamlit run app.py
```

The VS Code **Run and Debug** panel also includes API, UI and combined configurations.

## API examples

Interactive docs: `http://127.0.0.1:8000/docs`.

```powershell
$draft = Invoke-RestMethod -Method Post -Uri http://127.0.0.1:8000/generate `
  -ContentType 'application/json' -InFile examples\nda-request.json
$draft.document
```

| Method | Path | Purpose |
|---|---|---|
| GET | `/` | API identity and links |
| GET | `/health` | Provider and configuration status; does not call Gemini |
| POST | `/generate` | Input document_type, parties, terms, dates, jurisdiction, language; returns document, provider, model and notice |
| POST | `/analyze` | Input document and language; returns summary, key_clauses, review_points, provider and notice |
| POST | `/export` | Input current document, document_type, format and branding; returns binary download |
| POST | `/extract` | Input filename and content_base64; returns extracted document text |

`branding` has `company_name`, `font` (`serif` or `sans`), and optional `logo_base64`. If `BACKEND_API_KEY` is set, include `X-API-Key` on all POST requests. The frontend handles this automatically. Validation failures return 422; missing/invalid API token 401; request size overflow 413; limits 429; unconfigured or overloaded Gemini 503; provider failures 502; provider timeout 504.

## Folders and configuration

```text
LegalEase/
  app.py, run.py                 UI entry point and two-service launcher
  main.py, routes.py            FastAPI application and API endpoints
  models.py, config.py          Data contracts and environment settings
  security.py                   Optional API token and local rate limiting
  ai_core/                      Gemini SDK, prompts and offline templates
  frontend/                     Streamlit workspace, API client and styles
  services/                     Preview parsing, export and import
  assets/fonts/                 Redistributable Unicode fonts and license
  examples/                     Fictional API input
  scripts/                      Running-API smoke test
  tests/                        Automated API, provider and UI tests
  docs/                         Architecture and PDF requirements analysis
  .vscode/                      Interpreter, debugger and extension settings
  .streamlit/                   Theme, upload limits and local server defaults
  .env.example                  Safe example configuration
  requirements*.txt             Pinned dependencies and tested snapshot
  Dockerfile, compose.yaml       Optional two-service local containers
```

`requirements.txt` pins direct runtime dependencies; `requirements-dev.txt` adds tests/lint. `requirements-lock-windows-py312.txt` records the full tested Windows/Python 3.12 environment. Use the direct requirement files for other supported platforms. Do not copy `.venv` between computers; recreate it.

## Optional Docker

With Docker Desktop installed and a root `.env` present:

```powershell
docker compose up --build
```

Open port 8501. `docker compose down` stops both containers. Local published ports bind only to `127.0.0.1`. Container configuration is supplied but was not executed in the build environment.

On macOS/Linux, use `python3.12 -m venv .venv`, `.venv/bin/python -m pip install -r requirements-dev.txt`, copy `.env.example` to `.env` if needed, and `.venv/bin/python run.py`.

## Troubleshooting

| Symptom | Fix |
|---|---|
| `py` is not recognized | Install Python 3.12/3.13 from python.org, reopen VS Code, or use `python` if it is the supported interpreter. |
| Import/module not found | Use `.venv\Scripts\python.exe`, install requirements in that environment, and open the project root. |
| Backend offline | Start `run.py`; inspect the terminal. For separate services, check BACKEND_URL. |
| Port occupied | Stop your earlier app instance, or run `run.py --api-port 8001 --ui-port 8502`. The launcher sets the matching backend URL for its UI process. |
| 401 | Ensure frontend and backend use the same BACKEND_API_KEY and restart both. |
| Gemini configuration rejected | Check key, model access, billing and quota in Google AI Studio. The app intentionally hides raw provider error details. |
| Quota / rate limit | Wait and review the provider quota. Local API calls also share the configured per-minute limit per client IP. |
| PDF rejects a character | Choose DOCX/TXT or replace that character. Do not silently alter important legal wording. |
| Empty imported PDF | It may be scanned or encrypted. OCR or unlock it using your own document tools first. |
| Download lacks latest wording | Click Apply edits, then Prepare downloads again. |
| Font appearance differs | Word uses installed Times New Roman/Arial; PDF embeds DejaVu serif/sans. Exact typography differs by design. |

## Data handling and scope

This is a **local, single-user application**, with no account system, database, document history or public deployment. Draft text lives in server process memory and Streamlit session state; exports are generated in memory. The app does not intentionally persist uploaded documents or log their bodies. Streamlit may retain session/media data in memory until session cleanup; closing a tab is not a secure memory-erasure guarantee.

In Gemini mode, document details or draft text are sent to Google only on generation/review. Branding/export/import run locally. Provider retention and service terms are governed by your Google account. Treat sensitive inputs accordingly. `.env` and virtual environments are excluded from Git and Docker image contents.

For shared/public deployment, add user authentication, TLS, shared rate limiting, deployment secrets, resource-isolated file parsing and an appropriate storage/retention policy. The included local API token is not a multi-user login system. The app drafts documents; it does not determine legal validity, sign agreements, research current laws or replace legal advice.

Source analysis and deliberate changes from the PDF: [docs/PROJECT_REVIEW.md](docs/PROJECT_REVIEW.md). Technical flow: [docs/ARCHITECTURE.md](docs/ARCHITECTURE.md).
