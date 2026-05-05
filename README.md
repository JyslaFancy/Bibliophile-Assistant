# Bibliophile Assistant

A CLI tool that uses Ollama and ChromaDB to create a document-based AI assistant. Users can point to folders with documents (Word, PDF, Markdown, Excel, PowerPoint) and the tool will index them for AI-powered question answering.

## Features

- **Document Processing**: Supports PDF, Word (DOCX, DOC), Markdown, Text, Excel (XLSX, XLS), and PowerPoint (PPTX, PPT) files
- **Ollama Integration**: Uses local Ollama models for embeddings and chat
- **ChromaDB**: Vector database for efficient document retrieval
- **Auto-Setup**: Detects hardware (RAM, GPU) and suggests appropriate models
- **User-Friendly CLI**: Easy-to-use command-line interface with progress indicators

## Installation

### 📦 Option 1: Install from PyPI (Recommended)

```bash
pip install bibliophile-assistant
```

This installs the `bibliophile` command globally.

---

### 📁 Option 2: Install from GitHub

1. Clone the repository:
   ```bash
   git clone https://github.com/JyslaFancy/Bibliophile-Assistant.git
   cd Bibliophile-Assistant
   ```

2. Install in development mode:
   ```bash
   pip install -e .
   ```

---

### ⚠️ Windows Users

After installing, if you get `'bibliophile' is not recognized...`:

**Solution 1: Add Python Scripts to PATH (Recommended)**
```powershell
# Run this once to add to your user PATH
[Environment]::SetEnvironmentVariable("Path", "$env:Path;$env:APPDATA\Python\Scripts", "User")
# Then open a NEW PowerShell window
```

**Solution 2: Use Python module directly**
```powershell
python -m bibliophile.main setup
python -m bibliophile.main index C:\path\to\docs
python -m bibliophile.main chat
```

**Solution 3: Install system-wide (requires admin)**
```powershell
pip install bibliophile-assistant
```

---

### Prerequisites

- **Python 3.8+**
- **pip** (usually comes with Python)

---

### Setup Ollama

After installing the package, set up Ollama:

```bash
# Auto-install Ollama, pull models, and start server
bibliophile setup --install-ollama --pull-models --start-server
```

What this does:
- Detects your hardware (RAM, GPU)
- Installs Ollama automatically (Linux: curl, macOS: curl, Windows: winget)
- Suggests optimal models for your system
- Pulls the recommended models
- Starts the Ollama server

**Note:** Windows users may need to open PowerShell as Administrator for the first install.

## Usage

### 💡 Quick Start

```bash
# Setup everything (Ollama + models + server)
bibliophile setup --install-ollama --pull-models --start-server

# Index your documents
bibliophile index /path/to/your/documents

# Ask a question
bibliophile ask "What is this about?"

# Start interactive chat
bibliophile chat
```

---

### Setup and Configuration

```bash
# Auto-detect hardware and suggest models
bibliophile setup

# Auto-install Ollama if not found
bibliophile setup --install-ollama

# Auto-pull suggested models
bibliophile setup --pull-models

# Start Ollama server
bibliophile setup --start-server

# Full auto-setup (install + models + server)
bibliophile setup --install-ollama --pull-models --start-server

# Or manually configure
bibliophile setup --manual
```

**Windows users:** If `bibliophile` command doesn't work, use:
```powershell
python -m bibliophile.main setup
python -m bibliophile.main index C:\path\to\docs
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
# Ask a question about your documents
bibliophile ask "What is the main topic of these documents?"

# Ask from a specific collection
bibliophile ask "What are the key findings?" --collection my_project

# Get more results
bibliophile ask "Summarize the documents" --limit 10
```

### Interactive Chat

```bash
# Start an interactive chat session
bibliophile chat

# With a specific collection
bibliophile chat --collection my_project

# With more results per query
bibliophile chat --limit 10
```

**Chat Commands:**
- `/quit`, `/exit`, `/q` - End the chat session
- `/help`, `/h` - Show available commands
- `/clear`, `/reset` - Clear conversation history
- `/collection`, `/col` - Show current collection

### Manage Collections

```bash
# List all collections
bibliophile list-collections

# Delete a collection
bibliophile delete-collection my_project
```

### Configuration

```bash
# Show current configuration
bibliophile config-show

# Reset configuration
bibliophile config-reset

# Use custom config file
bibliophile --config /path/to/config.yaml index /path/to/documents
```

## Supported File Types

- `.pdf` - PDF documents
- `.docx` - Word documents (Office Open XML)
- `.doc` - Word documents (legacy)
- `.md` - Markdown files
- `.txt` - Plain text files
- `.xlsx` - Excel spreadsheets
- `.xls` - Excel spreadsheets (legacy)
- `.pptx` - PowerPoint presentations
- `.ppt` - PowerPoint presentations (legacy)

## Configuration

Configuration is stored in `~/.bibliophile/config.yaml` by default.

### Configuration Options

```yaml
ollama:
  chat_model: "llama3"        # Model for chat/answering
  embedding_model: "llama3"   # Model for embeddings
  base_url: "http://localhost:11434"  # Ollama API URL

chroma:
  path: ".bibliophile/chroma"  # ChromaDB data directory
  persist_directory: null

document_processing:
  chunk_size: 1000           # Characters per chunk
  chunk_overlap: 200         # Overlap between chunks
  supported_extensions:     # File extensions to process
    - ".pdf"
    - ".docx"
    - ".md"
    - ".txt"
    - ".xlsx"
    - ".pptx"

collections: []             # List of indexed collections
```

## Hardware Requirements

The tool will automatically detect your system hardware and suggest appropriate models:

- **Minimum**: 8GB RAM - Uses small models like `llama3`
- **Recommended**: 16GB+ RAM - Can use larger models like `llama3.2`
- **With GPU**: 12GB+ VRAM - Can use GPU-accelerated models

## Troubleshooting

### Ollama not found

Make sure Ollama is installed and running:
```bash
ollama --version
ollama serve
```

### Missing dependencies

Install required packages:
```bash
pip install -r requirements.txt
```

For PDF support:
```bash
pip install pypdf
```

For Word/Excel/PowerPoint support:
```bash
pip install python-docx openpyxl python-pptx
```

### ChromaDB issues

Make sure ChromaDB is installed:
```bash
pip install chromadb
```

## Development

Run the CLI directly:
```bash
python -m bibliophile.main
```

Or install in development mode:
```bash
pip install -e .
```

## License

MIT License - See [LICENSE](LICENSE) for details.
