# Demo

A minimal RAG demo with two ways to use the same assistant: **CLI** or **web GUI**.

> Demo only. The included knowledge base is fictional. Do not enter real patient details or other personal or sensitive information.

## Choose how to use it

- **CLI:** ask questions in Command Prompt or PowerShell and receive structured JSON.
- **GUI:** open a small chat page in your browser and inspect supporting sources.

Both interfaces use the same local knowledge base, BM25 retrieval, Gemini answer generation, and configuration. You only need to install the project once.

## 1. Requirements

- Windows 10/11, macOS, or Linux.
- Git.
- Python 3.11 or newer.
- A Google Gemini API key for live answers.
- Internet access when asking Gemini a question.

Check which Python versions are available:

```cmd
py --version
py -0p
```

This project does not require Python 3.12 specifically. Use an installed Python 3 version with `py -3`. If you do not have Python 3.11 or newer, install Python 3.12 with the Windows Python install manager:

```cmd
py install 3.12
py -3.12 --version
```

Then use `py -3.12` instead of `py -3` in the virtual-environment command below. Alternatively, install a current Python 3 release from python.org and reopen your terminal.

## 2. Download the repository

**Important:** run all project commands from inside the folder named `RAG-CLI_GUI`, not from `C:\Users\Dell` or another parent folder. The examples below use Windows Command Prompt (CMD), not PowerShell.

### Windows Command Prompt (CMD)

Open Command Prompt and run:

```cmd
if not exist "%USERPROFILE%\Projects" mkdir "%USERPROFILE%\Projects"
cd /d "%USERPROFILE%\Projects"
git clone https://github.com/rahil565665-afk/RAG-CLI_GUI.git
cd RAG-CLI_GUI
```

If the folder already exists, do not clone it again. Enter it directly:

```cmd
cd /d "%USERPROFILE%\Projects\RAG-CLI_GUI"
```

Confirm that you are in the right place:

```cmd
cd
dir
```

You should see `requirements.txt`, `.env.example`, and the `app`, `data`, and `static` folders.

### Windows PowerShell alternative

Use these commands instead of the CMD commands above:

```powershell
New-Item -ItemType Directory -Force -Path "$HOME\Projects" | Out-Null
Set-Location "$HOME\Projects"
git clone https://github.com/rahil565665-afk/RAG-CLI_GUI.git
Set-Location .\RAG-CLI_GUI
Get-Location
Get-ChildItem
```

Do not mix CMD and PowerShell syntax. For example, CMD uses `copy`; PowerShell uses `Copy-Item`.

## 3. Create the virtual environment and install dependencies

Run these commands from the repository folder.

### CMD

```cmd
py -3 -m venv .venv
.venv\Scripts\python.exe -m pip install --upgrade pip
.venv\Scripts\python.exe -m pip install -r requirements.txt
```

### PowerShell

```powershell
py -3 -m venv .venv
.\.venv\Scripts\python.exe -m pip install --upgrade pip
.\.venv\Scripts\python.exe -m pip install -r requirements.txt
```

If `py -3 -m venv .venv` reports that no Python 3 runtime is installed, install Python first (see step 1), close and reopen the terminal, and retry. If you installed Python 3.12 specifically, use `py -3.12 -m venv .venv`.

## 4. Configure Gemini once

### CMD

```cmd
copy .env.example .env
notepad .env
```

### PowerShell

```powershell
Copy-Item .env.example .env
notepad .env
```

In the file, replace `YOUR_GEMINI_API_KEY` with your own key:

```dotenv
GEMINI_API_KEY=your_actual_key
GEMINI_MODEL=gemini-3.5-flash-lite
TOP_K=4
MIN_RELEVANCE=0.22
RATE_LIMIT_PER_MINUTE=30
```

Save and close Notepad. Keep `.env` private. It is excluded by Git and Docker ignore rules. Never paste your key into source code or commit it.

## 5. Choose one interface

You can use either interface whenever you want. Both use the same settings and backend.

### Option A — CLI

Ask a single question. Multi-word questions can be entered without quotation marks:

```cmd
.venv\Scripts\python.exe -m app.cli What is the clinic address?
```

Start interactive mode to ask several questions in one session:

```cmd
.venv\Scripts\python.exe -m app.cli
```

At `Question>`, type a question and press Enter. Type `exit` or `quit` to leave.

Useful options:

```cmd
.venv\Scripts\python.exe -m app.cli --compact What are the clinic hours?
.venv\Scripts\python.exe -m app.cli --top-k 5 What services are listed?
.venv\Scripts\python.exe -m app.cli --help
```

The same commands work in PowerShell; prefix the executable with `.`:

```powershell
.\.venv\Scripts\python.exe -m app.cli What is the clinic address?
```

### Option B — Browser GUI

Start the local web server:

```cmd
.venv\Scripts\python.exe -m uvicorn app.main:app --host 127.0.0.1 --port 8000
```

Open this address in your browser:

http://127.0.0.1:8000

Type a question and press Enter or select **Send**. Supporting passages are available under the **Sources** disclosure when the model cites local knowledge-base material.

Keep the terminal window open while using the GUI. Press `Ctrl+C` in that window to stop the server.

For PowerShell, use:

```powershell
.\.venv\Scripts\python.exe -m uvicorn app.main:app --host 127.0.0.1 --port 8000
```

The GUI is served by FastAPI; the browser never receives the Gemini API key.

## 6. Run the tests

From the repository root:

```cmd
.venv\Scripts\python.exe -m pytest -q
```

The tests cover the CLI, GUI/static assets, API validation, retrieval, citations, Gemini error handling, and response schema. They use mocked Gemini responses and do not make live Gemini API calls.

GitHub Actions runs the tests on Python 3.11–3.15 and builds the Docker image. The image build job does not publish or deploy the image.

## Deployment-ready container (optional)

The repository includes a Dockerfile. You can build and run the container locally without deploying it:

```bash
docker build -t rag-demo .
docker run --rm -p 8000:8000 --env-file .env rag-demo
```

Then open http://localhost:8000.

For a future deployment, use a host that supports Docker builds, configure `GEMINI_API_KEY` as a secret environment variable, and let the host supply `PORT`. The app listens on `PORT` (default 8000) and exposes `/health` for health checks.

No hosting service, public URL, or deployment is configured by this repository.

## How it works

1. The CLI or browser accepts a user question.
2. FastAPI or the CLI passes it to the shared RAG service.
3. A local BM25 retriever searches 31 knowledge-base chunks and selects relevant evidence.
4. Google Gemini receives the question and the selected passages and generates a structured response.
5. Pydantic validates the response. The application attaches source metadata from trusted local chunks.

The response contains `answer`, `sources`, `confidence_score`, and `answerable`. The confidence score is a retrieval-support indicator, not a calibrated probability of correctness. When no local passage supports an answer, Gemini can still provide an appropriate fallback, but sources are empty and the support score is zero. Obvious emergency phrases are handled by a narrow deterministic safety backstop before model generation.

## Libraries and frameworks

- Python and BM25 retrieval for local keyword search.
- FastAPI and Uvicorn for the GUI/API server.
- Google Gen AI SDK for Gemini answer generation.
- Pydantic for request and structured-response validation.
- python-dotenv for local environment configuration.
- Plain HTML, CSS, and JavaScript for the minimal browser interface.
- pytest for automated tests.
- Docker for containerized deployment.

## AI-assisted development

AI coding assistants were used to implement much of the CLI, retrieval, Gemini integration, GUI, tests, and documentation. The project requirements and architecture were directed through implementation instructions, followed by iterative local testing, debugging, and review of generated changes.

## Limitations

- The knowledge base is fictional demo content; this is not a real clinic service or a clinical decision tool.
- Do not enter patient data, personal details, or sensitive information.
- BM25 is keyword-based and may miss synonyms or paraphrases.
- The confidence score describes retrieval support; it is not a medical or factual certainty score.
- The request rate limiter is in-memory and per process. A multi-instance deployment should use a shared rate limiter.
- Automated tests mock Gemini. A live answer still depends on a valid API key, model access, network connectivity, and available quota.
