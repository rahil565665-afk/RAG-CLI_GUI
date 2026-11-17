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

Run these commands in PowerShell, one at a time:

```powershell
$projectRoot = Join-Path $HOME 'Projects'
$repoPath = Join-Path $projectRoot 'RAG-CLI_GUI'
New-Item -ItemType Directory -Force -Path $projectRoot | Out-Null
Set-Location $projectRoot
git clone https://github.com/rahil565665-afk/RAG-CLI_GUI.git
Set-Location $repoPath
Get-Location
Get-ChildItem -Force
```

The location should end in `Projects\\RAG-CLI_GUI`. In the file listing, you should see folders such as `app`, `data`, `static`, and `tests`, plus `requirements.txt` and `.env.example`.

**Already cloned this repository?** Do not run `git clone` again. Instead, run these commands to enter the existing clone:

```powershell
$repoPath = Join-Path $HOME 'Projects\\RAG-CLI_GUI'
Set-Location $repoPath
Get-Location
```

If the `RAG-CLI_GUI` folder already exists but is not a Git repository, do not clone over it. Rename that folder or choose a different project directory first.

To update an existing clone, first check for local changes with `git status`. Do not pull over work you have not committed or backed up. When the working tree is clean, run:

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

## Project structure

The repository combines the original CLI application with the browser GUI. The CLI and GUI share the same RAG service, configuration, retrieval implementation, Gemini integration, and local knowledge base.

```text
RAG-CLI_GUI/
├── app/
│   ├── cli.py              # Command-line interface
│   ├── config.py           # Reads local .env and environment settings
│   ├── gemini_client.py    # Gemini API client, retries and structured JSON
│   ├── main.py             # FastAPI application and browser/API endpoints
│   ├── rag_service.py      # Retrieval, generation, safety handling and citations
│   ├── retrieval.py        # Local BM25 retrieval and knowledge-base loading
│   ├── schemas.py          # Pydantic request and response schemas
│   └── service.py          # Shared RAG service factory for CLI and GUI
├── data/
│   ├── northside_dental_knowledge_base.json
│   └── northside_dental_knowledge_base_section_index.md
├── static/
│   ├── app.js              # Browser chat behavior and API requests
│   ├── index.html          # Minimal chat page
│   └── styles.css          # Browser interface styling
├── tests/                  # Offline automated tests
├── .github/workflows/
│   └── tests.yml           # Python test matrix and Docker build check
├── .dockerignore
├── .env.example            # Safe configuration template (no real key)
├── .gitignore              # Excludes .env and local environments
├── Dockerfile
├── requirements.txt
└── README.md
```

## Architecture and design decisions

The project uses a deliberately small, local-first RAG architecture that can be accessed through either the CLI or the browser GUI:

1. **Local knowledge source:** the fictional clinic handbook is represented as a JSON file containing 31 topic-based chunks. Each chunk carries a stable ID, section information, source-page information, keywords, and content. The accompanying section index provides a human-readable guide to the handbook's structure.
2. **Local retrieval before generation:** a BM25 keyword retriever ranks the chunks on the machine running the application. The project does not require a hosted vector database, embedding service, or separate retrieval server.
3. **Relevance gate and top-k selection:** the retriever ranks matching chunks, then the RAG service sends only passages that meet the configured minimum relevance threshold and cover at least 60% of the meaningful query terms. The number of passages is limited to five. The default `TOP_K` is four. This reduces the risk of treating one shared word (for example, “tooth”) as proof of a particular clinic service such as tooth replacement.
4. **Grounded answer generation:** the application sends the question and selected evidence to Google Gemini. For clinic-specific questions, the model is instructed to rely only on the supplied evidence and to treat missing information as unknown rather than guessing. For general dental-education questions, it may provide concise general information, but it must clearly label that information as not confirmed Northside Dental Clinic policy or service information.
5. **Structured response validation:** Pydantic validates the model's small response schema. The application then maps model-cited chunk IDs back to the retrieved local records and builds source citations itself. It does not trust the model to invent section names, document names, or page metadata.
6. **Safety-first deterministic handling:** a narrow emergency-phrase rule runs before a Gemini request for certain obvious emergency symptoms. It directs the user to local emergency services. This is only a limited backstop, not a diagnostic system or a replacement for professional care or local emergency services.
7. **Two interfaces over one service:** the CLI provides terminal-based interaction and structured JSON output. FastAPI serves the minimal browser GUI and the HTTP endpoints. Both call the same service factory and RAG implementation rather than maintaining separate retrieval or answer-generation logic.

These decisions keep the demo understandable, inexpensive to run, and straightforward for a developer to inspect. The lexical BM25 approach is intentionally transparent and runs locally, although it can miss synonyms, paraphrases, and questions that use words different from those in the knowledge base.

### Response structure and source handling

The application response contains four fields:

| **Field** | **Meaning** |
| --- | --- |
| `answer` | The generated answer text. |
| `sources` | Source citations constructed from verified local knowledge-base records. |
| `confidence_score` | A 0–100 retrieval-support indicator based on the cited retrieved passages. It is not a calibrated probability of correctness. |
| `answerable` | Indicates whether the answer has supporting citations from the local knowledge base. |

When no retrieved passage supports a response, the model may still return a clearly labelled general educational answer or explain that a clinic-specific detail is not specified. In that case, `sources` is empty, `confidence_score` is zero, and `answerable` is false. A deterministic emergency response is handled separately before the normal Gemini generation path.

## Libraries and frameworks used

| **Library / tool** | **How it is used** |
| --- | --- |
| Python standard library | CLI argument handling, JSON processing, file paths, tokenization, BM25 scoring, environment access, and regular-expression safety checks. |
| `google-genai` | Calls the Gemini Developer API and requests structured JSON output. |
| Pydantic | Defines and validates the model draft, API request, health response, and application response schemas. |
| `python-dotenv` | Loads the developer's local `.env` configuration without hard-coding API keys. |
| FastAPI | Provides the browser GUI backend, health endpoint, and chat API on top of the same RAG service. |
| Uvicorn | Runs the FastAPI application locally and inside the Docker container. |
| HTTPX2 | Provides the supported HTTP transport used by Starlette's test client in the current dependency setup. |
| pytest | Runs automated tests for CLI behavior, retrieval, service behavior, API behavior, and Gemini schema compatibility. |
| HTML, CSS and JavaScript | Provide the minimal browser interface without a frontend framework or separate JavaScript build step. |
| Docker | Packages the application and its runtime dependencies into a container image. |

No separate vector database, embeddings framework, LangChain, or frontend framework is required by the current implementation.

## Configuration reference

The application reads `.env` from the repository root. Environment variables already defined in the shell take precedence over values in `.env`.

| **Setting** | **Default** | **Purpose** |
| --- | --- | --- |
| `GEMINI_API_KEY` | Required | Private Google Gemini API key used for normal answer generation. |
| `GEMINI_MODEL` | `gemini-3.5-flash-lite` | Gemini model used to generate answers. |
| `TOP_K` | `4` | Maximum number of retrieved passages considered for the answer (1–5). |
| `MIN_RELEVANCE` | `0.22` | Minimum retrieval relevance required for a passage to be sent as supporting evidence (0–1). |
| `RATE_LIMIT_PER_MINUTE` | `30` | Per-process request limit used by the HTTP chat endpoint. |
| `NORTHSIDE_KB_PATH` | `data/northside_dental_knowledge_base.json` | Optional path override for the local knowledge-base JSON file. |

The defaults shown here describe the application configuration. The earlier setup section explains how to create the local `.env` file and enter the Gemini API key. Keep the real key private and do not commit it.

## AI-assisted development

AI coding assistants were used to write most of the code, including much of the CLI, retrieval and RAG service implementation, Gemini integration, schemas, browser GUI, tests, and documentation.

My main contribution was deciding what the application should look like architecturally and specifying that design in detailed implementation prompts. I defined the intended CLI and browser workflow, local knowledge-base retrieval, Gemini-powered grounded response generation, structured JSON output, source citations, and the supporting technology choices before the implementation was generated.

After that, my hands-on coding involvement was mainly in running the project, identifying errors during installation and testing, and correcting those issues. I tested the working application with real Gemini requests and iterated on problems such as Windows dependency installation, CLI behavior, and Gemini's structured-output schema compatibility.

In other words, AI coding assistants produced most of the actual code; I directed the architecture and requirements, then focused on troubleshooting and validating the result.

## Additional troubleshooting: Gemini and retrieval

The basic Windows setup and startup issues are covered in the troubleshooting section above. The notes here cover more specific model-provider and retrieval behavior.

### Gemini returns 400 with an `additionalProperties` or schema error

The `GeminiDraft` schema in `app/schemas.py` must keep `ConfigDict(extra="ignore")`. Gemini's response-schema endpoint does not accept the extra `additionalProperties` field generated by a strict Pydantic schema for this model draft. Do not change that setting back to `extra="forbid"`. The application response and source-citation schemas have their own validation rules.

### Gemini returns 401 or 403

The application classifies these responses as an authentication or permissions failure. Check that the API key is valid and that the corresponding Google AI Studio project can use the Gemini API. If the key was exposed, revoke it and create a replacement key, then update the local `.env` file.

### Gemini returns 404 or says the model is unavailable

Check the current [Gemini model list](https://ai.google.dev/gemini-api/docs/models) and confirm the model ID is available to your project. You can change `GEMINI_MODEL` in `.env`. Model availability can change over time and may vary by account or region.

### Gemini reports a temporary provider or network error

The Gemini client configures SDK retries for common transient HTTP responses, including 408, 429, 500, 502, 503, and 504, with bounded exponential backoff. If the retries are exhausted, the CLI returns a sanitized error code and the GUI returns an actionable HTTP error. For `GEMINI_TEMPORARILY_UNAVAILABLE` or `GEMINI_NETWORK_ERROR`, check connectivity and try again. Persistent quota exhaustion requires the relevant quota window to reset or the project limit to be increased.

### Gemini returns 429 or quota exceeded

This indicates that a rate or usage limit was reached. Check the project's current [Gemini API rate limits](https://ai.google.dev/gemini-api/docs/rate-limits) and usage in Google AI Studio. Wait for the relevant quota window to reset or use a project/model with available quota. A free tier does not mean unlimited requests.

### The answer says the knowledge base does not contain enough information

The local retriever uses BM25 keyword matching, not semantic embeddings. Try a more specific question using terms likely to appear in the clinic document. You can also try `--top-k 5` with the CLI to consider the maximum number of passages. Increasing `TOP_K` does not bypass the relevance and query-coverage checks. A very low `MIN_RELEVANCE` threshold can introduce unrelated passages, so change it carefully.

### The CLI reports a provider error

The CLI intentionally hides low-level provider details, stack traces, local paths, and credentials from normal output. Read the returned error code and message, then check the model ID, network connection, API key, project access, and quota as appropriate. To check the local installation separately, run the automated tests using the command in the setup section above.

## Fictional address in the sample knowledge base

The Northside Dental sample profile uses this invented demonstration address: **18 Cedar Lane, Northside District, Riverton, Example State 00018, USA**. It is stored in the existing clinic-profile knowledge-base chunk so questions such as “What is the clinic address?” or the common typo “What is your adress?” can retrieve the profile. The district, state, and postal code are fictional additions for this demo, not a real location.

## Safety and limitations

- All Northside Dental content is fictional demonstration data.
- Do not use this project to answer real patient questions or make treatment decisions.
- Do not enter or upload real patient information, personal details, or other sensitive information.
- The app does not diagnose, prescribe, recommend medication changes, interpret X-rays, or provide individualized clinical advice. Personal symptoms, treatment decisions, and clinical concerns should be discussed with a licensed dentist or the relevant clinical team.
- Its emergency-phrase check is a narrow deterministic backstop. It is not a diagnostic tool and is not a substitute for local emergency services. The number 911 is only part of the fictional US example and must not be treated as a universal emergency number.
- BM25 is lexical retrieval; it can miss synonyms and paraphrases or fail to retrieve relevant passages when the wording differs from the source material.
- The confidence score describes local retrieval support. It is not a calibrated probability of correctness, clinical certainty, or a measure of treatment safety.
- No appointment booking, live insurance verification, or patient-record integration is included. The assistant must not invent appointment slots, bookings, provider details, fees, or insurance coverage.
- The request rate limiter is in-memory and per process. A multi-instance deployment would need a shared rate limiter.
- Automated tests mock Gemini. Live answers still depend on a valid API key, model access, network connectivity, and available quota.
- Google Gemini API usage is subject to Google's terms, privacy practices, model availability, and rate limits.
- No hosting service, public URL, or deployment is configured by this repository.

