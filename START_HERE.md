# Run LegalEase on your laptop

This ZIP contains the complete source code, dependencies list, fonts, configuration templates, and documentation. Your laptop creates its own Python environment during installation. No private API key is included.

## Windows: first-time setup

1. Right-click the ZIP and choose **Extract All**. Open the extracted `LegalEase` folder. Do not run files from inside the ZIP viewer.
2. Install **Python 3.12 or 3.13** from [python.org](https://www.python.org/downloads/). Enable **Add python.exe to PATH** in the installer. If you already have either version, skip this step.
3. Double-click **Install-LegalEase.cmd**. Keep the window open until it says **Installation complete**. Internet access is required; installation may take several minutes. This installs dependencies and creates `.env` without overwriting existing settings.
4. Open the extracted folder in **VS Code → File → Open Folder**. Open `.env` (the installer created it next to `main.py`). Add your own [Google AI Studio API key](https://aistudio.google.com/apikey) and change these lines:

   ```dotenv
   AI_PROVIDER=gemini
   GEMINI_API_KEY=paste_your_own_key_here
   GEMINI_MODEL=gemini-3.5-flash
   ```

   Replace `paste_your_own_key_here` with the actual key and save the file. Keep the other settings unchanged. You can leave `AI_PROVIDER=demo` to explore the interface without a key; demo mode produces templates rather than Gemini drafts.

5. Double-click **Start-LegalEase.cmd**.
6. Open **http://127.0.0.1:8501** in your browser. Keep the command window open while using the app. **Ctrl+C** stops it. Start only one copy at a time.

After first-time setup, repeat steps 5–6 whenever you want to use LegalEase. Stop and restart the app after changing `.env`. Real AI generation requires internet access and Gemini access/quota for your key.

## Windows: running from VS Code

Install the Microsoft Python extension. Press **Ctrl+Shift+P → Python: Select Interpreter** and choose `.venv\Scripts\python.exe`. In **Terminal → New Terminal**, run:

```powershell
.\.venv\Scripts\python.exe run.py
```

If you prefer manual installation, open PowerShell in the extracted folder and run:

```powershell
py -3.13 -m venv .venv
.\.venv\Scripts\python.exe -m pip install -r requirements.txt
if (-not (Test-Path .env)) { Copy-Item .env.example .env }
```

Use `py -3.12` instead if you installed Python 3.12. Then configure `.env` as above and run the application.

## macOS or Linux

Install Python 3.12 or 3.13, extract the ZIP, and open a terminal in the extracted `LegalEase` folder:

```sh
python3.12 -m venv .venv
.venv/bin/python -m pip install -r requirements.txt
if [ ! -f .env ]; then cp .env.example .env; fi
```

Replace `python3.12` with `python3.13` if applicable. Configure `.env` as above, then run:

```sh
.venv/bin/python run.py
```

Open **http://127.0.0.1:8501**. In VS Code select `.venv/bin/python` as the interpreter. Windows `.cmd` files are not used on these platforms. The application was verified on Windows; macOS/Linux commands are provided but have not been executed in those environments.

## If something goes wrong

- **Missing module:** run `Install-LegalEase.cmd` again and launch with `Start-LegalEase.cmd`.
- **Website does not open:** wait for the launcher to report that both services are ready; inspect the command window for errors.
- **Port already in use:** close the earlier LegalEase instance with Ctrl+C before starting another.
- **Gemini error:** confirm `.env` was saved, restart the app, and check your key, model access and quota in Google AI Studio. Temporary provider overload may require retrying later.

Optional developer checks, API documentation, and project details are in [README.md](README.md). If you share your copy later, exclude `.env` and `.venv` again.
