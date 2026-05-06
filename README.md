# Bibliophile Assistant

A CLI tool that uses Ollama and ChromaDB to create a document-based AI assistant. Point it at folders with documents (Word, PDF, Markdown, Excel, PowerPoint) and ask questions in plain English.

## Features

- **Document Processing**: Supports PDF, Word (DOCX, DOC), Markdown, Text, Excel (XLSX, XLS), and PowerPoint (PPTX, PPT) files
- **Ollama Integration**: Uses local Ollama models for embeddings and chat
- **ChromaDB**: Vector database for efficient document retrieval
- **Auto-Setup**: Detects hardware (RAM, GPU) and suggests appropriate models
- **User-Friendly CLI**: Easy-to-use command-line interface with progress indicators

---

## Quick Start (No Python Required)

### 1. Install

**Windows (PowerShell)** — one-liner, works immediately:

```powershell
irm https://raw.githubusercontent.com/JyslaFancy/Bibliophile-Assistant/main/install.ps1 | iex
```

This downloads the latest `bibliophile.exe`, puts it in `%LOCALAPPDATA%\Programs\Bibliophile`, and adds it to your PATH.

After it finishes, restart your terminal and run:

```powershell
bibliophile setup --install-ollama --pull-models --start-server
```

**Windows (winget)** — once approved by winget-pkgs:

```
winget install JyslaFancy.BibliophileAssistant
```

> Currently pending submission. Use the PowerShell install above until then.

**Linux** — one-liner:

```bash
curl -fsSL https://raw.githubusercontent.com/JyslaFancy/Bibliophile-Assistant/main/install.sh | bash
```

Or download the binary directly from the [Releases page](https://github.com/JyslaFancy/Bibliophile-Assistant/releases).

### 2. Run

```bash
# Windows (PowerShell / Command Prompt)
.\bibliophile.exe setup --install-ollama --pull-models --start-server

# Linux
./bibliophile setup --install-ollama --pull-models --start-server
```

That's it. No Python, no pip, no PATH — just download and run.

### 3. Index and Ask

```bash
# Index your documents
./bibliophile index /path/to/your/documents

# Ask a question
./bibliophile ask "What is this about?"

# Start interactive chat
./bibliophile chat
```

**Prerequisites**: You'll need Ollama installed (the `setup` command above handles this automatically). The standalone binary bundles everything else — Python, all libraries, ChromaDB — so you don't install anything else.

---

## Usage

### Setup

```bash
# Auto-detect hardware and suggest models
bibliophile setup

# Full auto-setup (install Ollama + pull models + start server)
bibliophile setup --install-ollama --pull-models --start-server
```

### Index Documents

```bash
# Index all documents in a folder
bibliophile index /path/to/documents

# With a custom collection name
bibliophile index /path/to/documents --name my_project

# With custom chunk size
bibliophile index /path/to/documents --chunk-size 500

# Overwrite existing collection
bibliophile index /path/to/documents --overwrite
```

### Ask Questions

```bash
bibliophile ask "What is the main topic of these documents?"
bibliophile ask "What are the key findings?" --collection my_project
bibliophile ask "Summarize the documents" --limit 10
```

### Interactive Chat

```bash
bibliophile chat
bibliophile chat --collection my_project
```

**Chat Commands:**
- `/quit`, `/exit`, `/q` - End the chat session
- `/help`, `/h` - Show available commands
- `/clear`, `/reset` - Clear conversation history
- `/collection`, `/col` - Show current collection

### Manage Collections

```bash
bibliophile list-collections
bibliophile delete-collection my_project
```

### Configuration

```bash
bibliophile config-show         # Show current configuration
bibliophile config-reset        # Reset to defaults
```

---

## Supported File Types

- `.pdf` — PDF documents
- `.docx` — Word documents (Office Open XML)
- `.doc` — Word documents (legacy, requires `antiword` or `catdoc`)
- `.md` — Markdown files
- `.txt` — Plain text files
- `.xlsx` / `.xls` — Excel spreadsheets
- `.pptx` / `.ppt` — PowerPoint presentations

---

## Hardware Requirements

Bibliophile automatically detects your hardware and suggests appropriate models:

- **Minimum**: 8GB RAM — uses lightweight models
- **Recommended**: 16GB+ RAM — comfortable performance
- **With GPU**: 12GB+ VRAM — GPU-accelerated inference

---

## For Developers

### Install from PyPI

```bash
pip install bibliophile-assistant
```

### Install from Source

```bash
git clone https://github.com/JyslaFancy/Bibliophile-Assistant.git
cd Bibliophile-Assistant
pip install -e ".[dev]"
```

### Build the Standalone Executable

```bash
pip install -e ".[dev]"
python scripts/build.py
```

Output goes to `dist/bibliophile` (or `dist/bibliophile.exe` on Windows).

### Submitting to winget-pkgs

After creating a release, generate the winget manifest:

```bash
python scripts/generate_winget.py v0.1.1
```

Then submit the generated `winget/` files to the [winget-pkgs](https://github.com/microsoft/winget-pkgs) community repository as a pull request. Once merged, users can run:

```
winget install JyslaFancy.BibliophileAssistant
```

### Configuration

Configuration is stored in `~/.bibliophile/config.yaml`:

```yaml
ollama:
  chat_model: "llama3"
  embedding_model: "nomic-embed-text"
  base_url: "http://localhost:11434"

chroma:
  path: ".bibliophile/chroma"

document_processing:
  chunk_size: 1000
  chunk_overlap: 200
  supported_extensions:
    - ".pdf"
    - ".docx"
    - ".doc"
    - ".md"
    - ".txt"
    - ".xlsx"
    - ".xls"
    - ".pptx"
    - ".ppt"
```

## License

MIT License — See [LICENSE](LICENSE) for details.
