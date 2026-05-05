# Bibliophile Assistant

A CLI tool that uses Ollama and ChromaDB to create a document-based AI assistant. Users can point to folders with documents (Word, PDF, Markdown, Excel, PowerPoint) and the tool will index them for AI-powered question answering.

## Features

- **Document Processing**: Supports PDF, Word (DOCX, DOC), Markdown, Text, Excel (XLSX, XLS), and PowerPoint (PPTX, PPT) files
- **Ollama Integration**: Uses local Ollama models for embeddings and chat
- **ChromaDB**: Vector database for efficient document retrieval
- **Auto-Setup**: Detects hardware (RAM, GPU) and suggests appropriate models
- **User-Friendly CLI**: Easy-to-use command-line interface with progress indicators

## Installation

### Prerequisites

- Python 3.8 or higher
- Git (for cloning)

### Setup

1. Clone the repository:
   ```bash
   git clone https://github.com/JyslaFancy/Bibliophile-Assistant.git
   cd Bibliophile-Assistant
   ```

2. Install Python dependencies:
   ```bash
   pip install -e .
   ```
   Or install manually:
   ```bash
   pip install -r requirements.txt
   ```

3. Install Ollama (if not already installed):
   - The tool can automatically install Ollama on Linux/macOS
   - Or install manually from [https://ollama.ai](https://ollama.ai)

4. Pull the models (the tool will suggest appropriate ones based on your hardware):
   ```bash
   bibliophile setup
   ```

## Usage

### Setup and Configuration

```bash
# Auto-detect hardware and suggest models
bibliophile setup

# Or manually configure
bibliophile setup --manual
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
