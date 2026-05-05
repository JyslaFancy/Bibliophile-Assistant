"""
CLI entry point for Bibliophile Assistant.
"""

import os
import time
import click
from rich.console import Console
from rich.panel import Panel
from rich.progress import Progress, SpinnerColumn, TextColumn
from rich.table import Table

# Lazy imports to avoid dependency issues at import time
console = Console()


def get_setup_module():
    """Lazy import of setup module."""
    from . import setup
    return setup


def get_documents_module():
    """Lazy import of documents module."""
    from . import documents
    return documents


def get_vectorstore_module():
    """Lazy import of vectorstore module."""
    from . import vectorstore
    return vectorstore


def get_qa_module():
    """Lazy import of qa module."""
    from . import qa
    return qa


def get_config_module():
    """Lazy import of config module."""
    from . import config
    return config


@click.group(name="bibliophile", help="Document-based AI assistant using Ollama and ChromaDB")
@click.option("--config", "-c", type=click.Path(), default="~/.bibliophile/config.yaml", help="Config file path")
@click.pass_context
def cli(ctx, config):
    """Main CLI group."""
    ctx.ensure_object(dict)
    ctx.obj["config_path"] = config
    
    # Lazy import config
    config_module = get_config_module()
    ctx.obj["config"] = config_module.ConfigManager(config)


@cli.command(name="setup", help="Setup Ollama and detect hardware")
@click.option("--auto/--manual", default=True, help="Auto-detect and setup")
@click.pass_context
def setup_cli(ctx, auto):
    """Setup Ollama and detect system hardware."""
    setup_module = get_setup_module()
    config_module = get_config_module()
    config = ctx.obj["config"]
    
    with Progress(
        SpinnerColumn(),
        TextColumn("[progress.description]{task.description}"),
        console=console,
    ) as progress:
        
        if auto:
            task = progress.add_task("Detecting hardware...", total=None)
            hardware = setup_module.detect_hardware()
            progress.update(task, completed=True)
            
            console.print(f"\n[bold green]Hardware Detected:[/bold green]")
            table = Table()
            table.add_column("Component", style="cyan")
            table.add_column("Value", style="magenta")
            table.add_row("Total RAM", f"{hardware['ram_gb']} GB")
            table.add_row("Available RAM", f"{hardware['available_ram_gb']} GB")
            table.add_row("GPU", hardware['gpu'] if hardware['gpu'] else "None")
            table.add_row("GPU Memory", f"{hardware['gpu_memory_gb']} GB" if hardware['gpu_memory_gb'] else "None")
            console.print(table)
            
            task = progress.add_task("Suggesting models...", total=None)
            models = setup_module.suggest_models(hardware)
            progress.update(task, completed=True)
            
            console.print(f"\n[bold green]Suggested Models:[/bold green]")
            table = Table()
            table.add_column("Type", style="cyan")
            table.add_column("Model", style="magenta")
            table.add_column("Reason", style="white")
            table.add_row("Chat", models['chat'], models['chat_reason'])
            table.add_row("Embedding", models['embedding'], models['embedding_reason'])
            console.print(table)
            
            if click.confirm("\nUse these suggestions?", default=True):
                config.set_config({
                    "ollama": {
                        "chat_model": models['chat'],
                        "embedding_model": models['embedding']
                    }
                })
                console.print("[green]Configuration saved![/green]")
        
        task = progress.add_task("Checking Ollama...", total=None)
        if not setup_module.check_ollama():
            console.print("\n[bold yellow]Ollama not found![/bold yellow]")
            if click.confirm("Install Ollama now?"):
                setup_module.setup_ollama()
        progress.update(task, completed=True)
    
    # Check if models are pulled
    config.load()
    chat_model = config.get("ollama.chat_model", "llama3")
    embedding_model = config.get("ollama.embedding_model", "llama3")
    
    with Progress() as progress:
        for model_name, model_type in [
            (chat_model, "chat"),
            (embedding_model, "embedding")
        ]:
            task = progress.add_task(f"Checking {model_type} model: {model_name}...", total=None)
            # Check if model exists locally
            local_models = setup_module.list_local_models()
            if model_name not in local_models:
                if click.confirm(f"Pull {model_name} now?"):
                    setup_module.pull_model(model_name)
            progress.update(task, completed=True)


@cli.command(help="Index documents from a folder")
@click.argument("folder", type=click.Path(exists=True, file_okay=False))
@click.option("--name", "-n", help="Name for this document collection")
@click.option("--chunk-size", "-s", type=int, default=1000, help="Chunk size for processing")
@click.option("--overwrite", is_flag=True, help="Overwrite existing collection")
@click.pass_context
def index(ctx, folder, name, chunk_size, overwrite):
    """Index documents from a folder into ChromaDB."""
    config = ctx.obj["config"]
    config.load()
    
    documents_module = get_documents_module()
    vectorstore_module = get_vectorstore_module()
    
    collection_name = name or f"docs_{int(time.time())}"
    
    # Initialize components
    with console.status("[bold green]Initializing document processor..."):
        doc_processor = documents_module.DocumentProcessor(chunk_size=chunk_size)
    
    with console.status("[bold green]Initializing vector store..."):
        vector_store = vectorstore_module.VectorStoreManager(
            config.get("chroma.path", ".bibliophile/chroma"),
            config.get("ollama.embedding_model", "llama3"),
            config.get("ollama.base_url", "http://localhost:11434")
        )
    
    console.print(f"\n[bold green]Processing documents from: {folder}[/bold green]")
    
    # Process documents
    with Progress(
        SpinnerColumn(),
        TextColumn("[progress.description]{task.description}"),
        console=console,
    ) as progress:
        
        task = progress.add_task("Scanning folder...", total=None)
        files = doc_processor.scan_folder(folder)
        progress.update(task, description=f"Found {len(files)} documents", completed=True)
        
        console.print(f"\n[bold]Documents to process:[/bold]")
        for f in files:
            console.print(f"  - {f}")
        
        if not files:
            console.print("[yellow]No supported documents found![/yellow]")
            return
        
        task = progress.add_task("Processing documents...", total=len(files))
        documents = []
        for file_path in files:
            progress.update(task, description=f"Processing {file_path}")
            try:
                chunks = doc_processor.process_file(file_path)
                documents.extend(chunks)
                console.print(f"[green]  Processed {len(chunks)} chunks from {file_path}[/green]")
            except Exception as e:
                console.print(f"[red]Error processing {file_path}: {e}[/red]")
            progress.advance(task)
        
        if not documents:
            console.print("[red]No documents were successfully processed![/red]")
            return
        
        console.print(f"\n[green]Extracted {len(documents)} document chunks[/green]")
        
        task = progress.add_task("Creating embeddings...", total=None)
        progress.update(task, completed=True)
        
        task = progress.add_task(f"Storing in ChromaDB collection: {collection_name}...", total=None)
        vector_store.create_collection(collection_name, documents, overwrite=overwrite)
        progress.update(task, completed=True)
    
    console.print(f"\n[bold green]Successfully indexed {len(documents)} chunks to collection '{collection_name}'[/bold green]")
    
    # Save to config
    current_collections = config.get("collections", [])
    if collection_name not in current_collections:
        current_collections.append(collection_name)
        config.set_config({"collections": current_collections})


@cli.command(help="Ask questions about indexed documents")
@click.argument("question", type=str)
@click.option("--collection", "-c", help="Specific collection to query")
@click.option("--limit", "-l", type=int, default=5, help="Number of results to return")
@click.pass_context
def ask(ctx, question, collection, limit):
    """Ask a question about indexed documents."""
    config = ctx.obj["config"]
    config.load()
    
    qa_module = get_qa_module()
    
    collections = config.get("collections", [])
    if not collections:
        console.print("[red]No collections found. Please index documents first.[/red]")
        console.print("\nTo index documents, run: bibliophile index /path/to/documents")
        return
    
    query_collection = collection or collections[0]
    
    console.print(f"\n[bold]Using collection: {query_collection}[/bold]")
    console.print(f"[bold]Question: {question}[/bold]\n")
    
    with console.status("[bold green]Searching for relevant information..."):
        qa_engine = qa_module.QAEngine(
            config.get("ollama.chat_model", "llama3"),
            config.get("chroma.path", ".bibliophile/chroma"),
            config.get("ollama.base_url", "http://localhost:11434")
        )
        results = qa_engine.query(query_collection, question, limit=limit)
    
    console.print("\n[bold green]Answer:[/bold green]")
    console.print(Panel(results["answer"], border_style="green"))
    
    if results.get("sources"):
        console.print("\n[bold]Sources:[/bold]")
        for i, source in enumerate(results["sources"], 1):
            console.print(f"  {i}. {source}")
    
    console.print(f"\n[dim]Confidence: {results.get('confidence', 0.0):.2%}[/dim]")


@cli.command(help="Start an interactive chat session")
@click.option("--collection", "-c", help="Specific collection to use")
@click.option("--limit", "-l", type=int, default=5, help="Number of results to return")
@click.pass_context
def chat(ctx, collection, limit):
    """Start an interactive chat session with your documents."""
    config = ctx.obj["config"]
    config.load()
    
    qa_module = get_qa_module()
    
    collections = config.get("collections", [])
    if not collections:
        console.print("[red]No collections found. Please index documents first.[/red]")
        console.print("\nTo index documents, run: bibliophile index /path/to/documents")
        return
    
    query_collection = collection or collections[0]
    
    # Initialize QA engine
    qa_engine = qa_module.QAEngine(
        config.get("ollama.chat_model", "llama3"),
        config.get("chroma.path", ".bibliophile/chroma"),
        config.get("ollama.base_url", "http://localhost:11434")
    )
    
    console.print(f"\n[bold green]Starting chat session[/bold green]")
    console.print(f"[dim]Using collection: {query_collection}[/dim]")
    console.print(f"[dim]Type /quit, /exit, or /q to end the session[/dim]")
    console.print(f"[dim]Type /help for available commands[/dim]\n")
    
    # Chat history for context
    conversation_history = []
    
    while True:
        try:
            user_input = click.prompt("\n[bold cyan]You:[/bold cyan] ", type=str, strip=True)
        except (KeyboardInterrupt, EOFError):
            console.print("\n[bold yellow]Session ended.[/bold yellow]")
            break
        
        if not user_input:
            continue
        
        # Handle special commands
        if user_input.lower() in ['/quit', '/exit', '/q']:
            console.print("[bold yellow]Goodbye![/bold yellow]")
            break
        
        if user_input.lower() in ['/help', '/h']:
            console.print("\n[bold]Available commands:[/bold]")
            console.print("  /quit, /exit, /q - End the chat session")
            console.print("  /help, /h - Show this help message")
            console.print("  /clear - Clear conversation history")
            console.print("  /collection - Show current collection")
            continue
        
        if user_input.lower() in ['/clear', '/reset']:
            conversation_history = []
            console.print("[green]Conversation history cleared.[/green]")
            continue
        
        if user_input.lower() in ['/collection', '/col']:
            console.print(f"[bold]Current collection:[/bold] {query_collection}")
            continue
        
        # Add to conversation history
        conversation_history.append({
            "role": "user",
            "content": user_input
        })
        
        # Show typing indicator
        with console.status("[bold green]Thinking..."):
            results = qa_engine.query(query_collection, user_input, limit=limit)
        
        # Add AI response to history
        conversation_history.append({
            "role": "assistant",
            "content": results["answer"]
        })
        
        # Display answer
        console.print(f"\n[bold green]Assistant:[/bold green]")
        console.print(Panel(results["answer"], border_style="green"))
        
        if results.get("sources"):
            console.print("\n[bold]Sources:[/bold]")
            for i, source in enumerate(results["sources"], 1):
                console.print(f"  {i}. {source}")
        
        console.print(f"\n[dim]Confidence: {results.get('confidence', 0.0):.2%}[/dim]")


@cli.command(help="List available collections")
@click.pass_context
def list_collections(ctx):
    """List all indexed document collections."""
    config = ctx.obj["config"]
    config.load()
    
    collections = config.get("collections", [])
    if not collections:
        console.print("[yellow]No collections found. Please index documents first.[/yellow]")
        console.print("\nTo index documents, run: bibliophile index /path/to/documents")
        return
    
    console.print("\n[bold green]Available Collections:[/bold green]")
    for i, collection in enumerate(collections, 1):
        console.print(f"  {i}. {collection}")
    
    console.print(f"\n[dim]Total: {len(collections)} collections[/dim]")


@cli.command(help="Delete a collection")
@click.argument("name", type=str)
@click.confirmation_option(prompt="Are you sure you want to delete this collection?")
@click.pass_context
def delete_collection(ctx, name):
    """Delete a document collection."""
    config = ctx.obj["config"]
    config.load()
    
    vectorstore_module = get_vectorstore_module()
    
    collections = config.get("collections", [])
    if name not in collections:
        console.print(f"[red]Collection '{name}' not found![/red]")
        return
    
    with console.status("[bold green]Deleting collection..."):
        vector_store = vectorstore_module.VectorStoreManager(
            config.get("chroma.path", ".bibliophile/chroma"),
            config.get("ollama.embedding_model", "llama3"),
            config.get("ollama.base_url", "http://localhost:11434")
        )
        vector_store.delete_collection(name)
    
    collections.remove(name)
    config.set_config({"collections": collections})
    console.print(f"[green]Collection '{name}' deleted![/green]")


@cli.command(help="Show current configuration")
@click.pass_context
def config_show(ctx):
    """Show current configuration."""
    config = ctx.obj["config"]
    config.load()
    
    console.print("\n[bold green]Current Configuration:[/bold green]")
    table = Table()
    table.add_column("Setting", style="cyan")
    table.add_column("Value", style="magenta")
    
    all_config = config.get_all()
    if all_config:
        for key, value in all_config.items():
            table.add_row(key, str(value))
    else:
        table.add_row("No configuration", "Run 'bibliophile setup' to configure")
    
    console.print(table)
    console.print(f"\n[dim]Config file: {config.config_path}[/dim]")


@cli.command(help="Reset configuration")
@click.confirmation_option(prompt="Are you sure you want to reset the configuration?")
@click.pass_context
def config_reset(ctx):
    """Reset configuration to defaults."""
    config = ctx.obj["config"]
    config.reset()
    console.print("[green]Configuration reset to defaults![/green]")


@cli.command(help="Show information about the tool")
def version():
    """Show version and basic information."""
    from . import __version__
    
    console.print(f"\n[bold green]Bibliophile Assistant[/bold green]")
    console.print(f"[dim]Version: {__version__}[/dim]")
    console.print("\nA document-based AI assistant using Ollama and ChromaDB")
    console.print("\nAuthor: Harald Daltveit")
    console.print("License: MIT")
    console.print("\nFor more information, see: https://github.com/JyslaFancy/Bibliophile-Assistant")


def main():
    """Entry point for the CLI."""
    # Ensure the bibliophile data directory exists
    data_dir = os.path.expanduser("~/.bibliophile")
    if not os.path.exists(data_dir):
        try:
            os.makedirs(data_dir, exist_ok=True)
        except Exception:
            pass
    
    cli(obj={})


if __name__ == "__main__":
    main()
