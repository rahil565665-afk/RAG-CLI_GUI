# RAG CLI + GUI Demo

A minimal retrieval-augmented generation (RAG) demo with two ways to use the same assistant:

- **CLI:** ask questions from a terminal and receive structured JSON.
- **Web GUI:** ask questions in a browser and inspect supporting knowledge-base sources.

Both interfaces use the same local knowledge base, BM25 retrieval, Gemini answer generation, and configuration.

> **Demo and privacy notice:** The included Northside Dental knowledge base is fictional. This is not a real clinic service or a clinical decision tool. Do not enter real patient details, personal information, or other sensitive data.

## Requirements

- Windows 10/11, macOS, or Linux.
- Git.
- Python 3.11 or newer. **Python 3.12 is recommended** for the local setup; the Docker image is also based on Python 3.12.
- A Gemini API key created in [Google AI Studio](https://aistudio.google.com/app/apikey) for normal question answering.
- Internet access when the app sends a question to Gemini.

The GitHub Actions workflow tests Python 3.11–3.15. This does not mean every Python version or operating system has been separately tested on your computer.

### Check Python and Git on Windows

Open **Windows PowerShell** and run:

```powershell
py --version
py list
git --version
```

If Python 3.12 is not installed and you use the Python install manager, install it with:

```powershell
py install 3.12
py -3.12 --version
```

The version command should report Python 3.12.x. You can also install the Python install manager from the [official Python downloads page](https://www.python.org/downloads/). After installing Python or Git, close and reopen PowerShell so the updated commands are available.

## Windows setup (PowerShell — recommended)

**Use the PowerShell commands in this section as written. Do not paste Command Prompt commands such as `if not exist`, `%USERPROFILE%`, or `cd /d` into PowerShell.** The commands below work even when PowerShell initially opens in a protected directory such as `C:\Windows\System32`.

### 1. Clone the repository

Run this block in PowerShell:

```powershell
$projectRoot = Join-Path $HOME 'Projects'
$repoPath = Join-Path $projectRoot 'RAG-CLI_GUI'

New-Item -ItemType Directory -Force -Path $projectRoot | Out-Null

if (Test-Path $repoPath) {
    if (-not (Test-Path (Join-Path $repoPath '.git'))) {
        throw "The folder $repoPath already exists but is not a Git repository. Rename that folder or choose another project directory; do not clone over it."
    }
    Write-Host "Existing Git clone found. Its files will not be overwritten."
}
else {
    Set-Location $projectRoot
    git clone https://github.com/rahil565665-afk/RAG-CLI_GUI.git
    if ($LASTEXITCODE -ne 0) {
        throw "Git clone failed. Check the Git installation, internet connection, and repository URL."
    }
}

Set-Location $repoPath
Get-Location
Get-ChildItem -Force
```

The location should end in `Projects\RAG-CLI_GUI`. In the file listing, you should see folders such as `app`, `data`, `static`, and `tests`, plus `requirements.txt` and `.env.example`.

If you already cloned the repository earlier, the block above enters that existing clone and does **not** replace or overwrite its files. To update a clean existing clone later, first check that you have no uncommitted changes with `git status`, then run:

```powershell
git pull --ff-only
```

### 2. Create a Python virtual environment

Make sure the current directory is the repository root (`RAG-CLI_GUI`), then run:

```powershell
py -3.12 -m venv .venv
& .\.venv\Scripts\python.exe --version
& .\.venv\Scripts\python.exe -m pip install --upgrade pip
& .\.venv\Scripts\python.exe -m pip install -r requirements.txt
```

The version check should report Python 3.12.x. Installing the requirements may take a few minutes and requires internet access.

These commands call the virtual environment's Python directly. You do **not** need to activate the environment or change PowerShell's script-execution policy.

If the first command says Python 3.12 is unavailable, verify it with `py -3.12 --version`. Install Python 3.12 if necessary, reopen PowerShell, and retry from the repository root.

### 3. Configure your Gemini API key

1. Open [Google AI Studio API Keys](https://aistudio.google.com/app/apikey) and create or copy a Gemini API key for a project that can use the Gemini API.
2. In PowerShell, create the local environment file from the example if it does not already exist:

```powershell
if (-not (Test-Path .env)) {
    Copy-Item .env.example .env
}
notepad .env
```

3. In Notepad, replace the placeholder value for `GEMINI_API_KEY` with your key. The file should look like this, with your real key in place of the example text:

```dotenv
GEMINI_API_KEY=PASTE_YOUR_GEMINI_API_KEY_HERE
GEMINI_MODEL=gemini-3.5-flash-lite
TOP_K=4
MIN_RELEVANCE=0.22
RATE_LIMIT_PER_MINUTE=30
```

4. Save the file and close Notepad.

The configured model, `gemini-3.5-flash-lite`, is a stable Gemini API model. See Google's [model documentation](https://ai.google.dev/gemini-api/docs/models/gemini-3.5-flash-lite) for current availability and details.

**Keep the key private.** Do not paste it into source code, screenshots, chat messages, or GitHub. The local `.env` file is excluded by both `.gitignore` and `.dockerignore`; `.env.example` contains only a placeholder. The browser frontend does not receive the API key. Review your Google AI Studio usage and quota if requests are rejected or rate-limited.

A normal question needs a working Gemini API key. Without one, the app can start and its health endpoint can respond, but ordinary CLI and GUI questions return a configuration error rather than a pre-written answer. The deterministic emergency-message backstop is a separate, narrow behavior; it is not a substitute for professional care or local emergency services.

## Choose an interface

Run these commands from the repository root in PowerShell.

### Option A — CLI

Ask one question. Multi-word questions can be typed without quotation marks:

```powershell
& .\.venv\Scripts\python.exe -m app.cli What is the clinic address?
```

Start interactive mode to ask multiple questions in one session:

```powershell
& .\.venv\Scripts\python.exe -m app.cli
```

At the `Question>` prompt, type a question and press Enter. Type `exit` or `quit` to leave.

Useful options:

```powershell
& .\.venv\Scripts\python.exe -m app.cli --compact What are the clinic hours?
& .\.venv\Scripts\python.exe -m app.cli --top-k 5 What services are listed?
& .\.venv\Scripts\python.exe -m app.cli --help
```

### Option B — Browser GUI

Start the local FastAPI web server:

```powershell
& .\.venv\Scripts\python.exe -m uvicorn app.main:app --host 127.0.0.1 --port 8000
```

Open [http://127.0.0.1:8000](http://127.0.0.1:8000) in your browser. To check whether the server has loaded its knowledge base, open [http://127.0.0.1:8000/health](http://127.0.0.1:8000/health).

Type a question and press Enter or select **Send**. When the answer cites local knowledge-base material, open **Sources** to inspect the supporting passages.

Keep the PowerShell window open while using the GUI. Press `Ctrl+C` in that window to stop the server. If port 8000 is already in use, start the server on another port, for example `--port 8001`, and open `http://127.0.0.1:8001`.

## Run the automated tests

From the repository root:

```powershell
& .\.venv\Scripts\python.exe -m pytest -q
```

The tests cover the CLI, GUI/static assets, API validation, retrieval, citations, Gemini error handling, and response schema. Gemini calls are mocked in the automated tests, so running the test suite does not make live Gemini requests or use your API quota.

GitHub Actions runs the test suite on Python 3.11, 3.12, 3.13, 3.14, and 3.15. After the tests pass, a separate job builds the Docker image. The workflow does **not** push an image, publish a site, or deploy the app.

## Optional: build and run the Docker image locally

Docker Desktop (Windows/macOS) or Docker Engine (Linux) must be installed and running. From the repository root, build the image:

```powershell
docker build -t rag-demo .
```

Run it with the local `.env` file supplied at container start:

```powershell
docker run --rm -p 8000:8000 --env-file .env rag-demo
```

Then open [http://localhost:8000](http://localhost:8000). Keep the terminal running while you use the app. Press `Ctrl+C` to stop it.

The Docker build does not include your `.env` file or bake your API key into the image. The key is passed to the running container as an environment variable. **These commands only build and run the app on your computer; they do not deploy it to a hosting provider.**

## macOS and Linux setup

The following commands are for Bash or a compatible shell. Use Python 3.11 or newer; Python 3.12 is recommended.

Check the installed versions:

```bash
python3 --version
git --version
```

Clone and enter the repository:

```bash
mkdir -p "$HOME/Projects"
cd "$HOME/Projects"
git clone https://github.com/rahil565665-afk/RAG-CLI_GUI.git
cd RAG-CLI_GUI
```

Create the virtual environment and install dependencies:

```bash
python3 -m venv .venv
.venv/bin/python --version
.venv/bin/python -m pip install --upgrade pip
.venv/bin/python -m pip install -r requirements.txt
```

Create and edit the local environment file:

```bash
if [ ! -f .env ]; then cp .env.example .env; fi
```

Open `.env` in your preferred text editor and set `GEMINI_API_KEY`. Keep the key private and do not commit the file.

Run the CLI, GUI, or tests with the same virtual-environment Python:

```bash
.venv/bin/python -m app.cli What is the clinic address?
.venv/bin/python -m uvicorn app.main:app --host 127.0.0.1 --port 8000
.venv/bin/python -m pytest -q
```

Run one command at a time. The GUI server command stays active until you stop it with `Ctrl+C`.

## Troubleshooting

- **`py` is not recognized:** Install the Python install manager from [python.org](https://www.python.org/downloads/) or the Microsoft Store, then reopen PowerShell.
- **`git` is not recognized:** Install [Git for Windows](https://git-scm.com/download/win), then reopen PowerShell.
- **Git says it cannot create a folder or reports permission denied:** Check `Get-Location`. Do not clone the project inside `C:\Windows\System32` or another protected system directory. Use the `$HOME\Projects` location in the PowerShell setup above.
- **The virtual-environment Python file is not found:** Make sure PowerShell is in the `RAG-CLI_GUI` repository root, then rerun the virtual-environment creation and dependency-install commands.
- **The app reports that `GEMINI_API_KEY` is missing:** Confirm that `.env` is in the repository root and that the key line is saved as `GEMINI_API_KEY=...` without quotes or extra spaces around the equals sign. Restart the CLI or web server after editing `.env`.
- **Gemini rejects the request or model:** Check the key, project permissions, model ID, internet connection, quota, and current model availability in Google AI Studio.
- **Port 8000 is busy:** Use another port, such as 8001, in the Uvicorn command and open the matching local URL.

## How it works

1. The CLI or browser accepts a question.
2. Both interfaces pass it to the same RAG service.
3. A local BM25 retriever searches the included 31 knowledge-base chunks and selects relevant evidence.
4. Gemini generates a structured response using the question and the selected evidence.
5. Pydantic validates the model response. The application attaches source metadata from trusted local knowledge-base records rather than trusting model-generated source details.

The response contains:

- `answer`: the generated text.
- `sources`: verified citations to local knowledge-base chunks.
- `confidence_score`: a 0–100 retrieval-support indicator, **not** a calibrated probability that the answer is correct.
- `answerable`: whether the response has supporting citations from the local knowledge base.

When no local passage supports the answer, Gemini may still provide a clearly labelled general educational response or explain that a clinic-specific detail is not in the knowledge base. In that case, `sources` is empty, `confidence_score` is 0, and `answerable` is false. A narrow deterministic check for certain obvious emergency phrases runs before Gemini; it directs the user to local emergency services and does not diagnose symptoms.

## Main libraries

- Python for the application.
- BM25 retrieval for local keyword search.
- FastAPI and Uvicorn for the web GUI/API server.
- Google Gen AI SDK for Gemini answer generation.
- Pydantic for request and structured-response validation.
- python-dotenv for local environment configuration.
- HTML, CSS, and JavaScript for the browser interface.
- pytest for automated tests.
- Docker for optional local container builds.

## Limitations

- The knowledge base is fictional demo content; this is not a real clinic service or a clinical decision tool.
- Do not enter patient data, personal details, or sensitive information.
- BM25 is keyword-based and may miss synonyms or paraphrases.
- The confidence score describes retrieval support; it is not a medical or factual certainty score.
- The request rate limiter is in-memory and per process. A multi-instance deployment would need a shared rate limiter.
- Automated tests mock Gemini. Live answers depend on a valid API key, model access, network connectivity, and available quota.
- No hosting service, public URL, or deployment is configured by this repository.

## AI-assisted development

AI coding assistants were used to implement parts of the CLI, retrieval, Gemini integration, GUI, tests, and documentation. The project requirements and architecture were directed through implementation instructions, followed by iterative local testing, debugging, and review of generated changes.
