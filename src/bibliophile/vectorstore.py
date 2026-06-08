"""
ChromaDB vector store integration for document embeddings.
"""

import os
import time
from typing import List, Dict, Any, Optional
from pathlib import Path
import chromadb
from chromadb.utils import embedding_functions
from rich.console import Console

console = Console()


class OllamaEmbeddingFunction(embedding_functions.EmbeddingFunction):
    """
    Custom embedding function that uses Ollama for embeddings.
    """

    def __init__(self, model_name: str = "nomic-embed-text", base_url: str = "http://localhost:11434"):
        """
        Initialize the Ollama embedding function.

        Args:
            model_name: Name of the Ollama model to use for embeddings
            base_url: Base URL for the Ollama API
        """
        self.model_name = model_name
        self.base_url = base_url
        self._client = None

    def __call__(self, input: List[str]) -> List[List[float]]:
        """
        Generate embeddings for a list of texts.

        Args:
            input: List of texts to embed

        Returns:
            List of embedding vectors
        """
        try:
            import requests

            if self._client is None:
                # Check if Ollama is running
                try:
                    response = requests.get(f"{self.base_url}/api/tags")
                    if response.status_code != 200:
                        raise ValueError(f"Ollama API not available at {self.base_url}")
                except Exception as e:
                    raise ValueError(f"Cannot connect to Ollama: {e}. Make sure Ollama is running.")

            embeddings = []
            for text in input:
                try:
                    response = requests.post(
                        f"{self.base_url}/api/embeddings",
                        json={
                            "model": self.model_name,
                            "prompt": text
                        },
                        timeout=30
                    )

                    if response.status_code == 200:
                        data = response.json()
                        if "embedding" in data:
                            embeddings.append(data["embedding"])
                        else:
                            raise ValueError(
                                f"Ollama embedding API returned no 'embedding' field. "
                                f"Response: {data}. Is '{self.model_name}' an embedding model?"
                            )
                    else:
                        raise ValueError(
                            f"Ollama embedding API error: HTTP {response.status_code} - {response.text}"
                        )
                except Exception as e:
                    # Re-raise with context — never silently fall back to garbage embeddings
                    raise ValueError(
                        f"Failed to generate embedding for text "
                        f"'{text[:100]}...': {e}"
                    ) from e

            return embeddings

        except Exception as e:
            console.print(f"[red]Embedding generation failed: {e}[/red]")
            # Let the caller handle this — do not return garbage vectors
            raise


class VectorStoreManager:
    """Manages ChromaDB vector store for document collections."""

    def __init__(self, persist_directory: str = None, embedding_model: str = "nomic-embed-text",
                 base_url: str = "http://localhost:11434", use_ollama_embeddings: bool = True):
        """
        Initialize the VectorStoreManager.

        Args:
            persist_directory: Directory to persist the ChromaDB data
            embedding_model: Name of the Ollama model to use for embeddings
            base_url: Base URL for the Ollama API
            use_ollama_embeddings: Whether to use Ollama for embeddings (default: True)
        """
        self.persist_directory = persist_directory
        self.embedding_model = embedding_model
        self.base_url = base_url
        self.use_ollama_embeddings = use_ollama_embeddings
        self._client = None
        self._embedding_function = None

    def _get_client(self) -> chromadb.Client:
        """Get or create the ChromaDB client."""
        if self._client is None:
            if self.persist_directory:
                # Use persistent client
                self._client = chromadb.PersistentClient(path=self.persist_directory)
            else:
                # Use in-memory client
                self._client = chromadb.HttpClient(host="localhost", port=8000)
        return self._client

    def _get_embedding_function(self):
        """Get or create the embedding function."""
        if self._embedding_function is None:
            if self.use_ollama_embeddings:
                self._embedding_function = OllamaEmbeddingFunction(
                    model_name=self.embedding_model,
                    base_url=self.base_url
                )
            else:
                self._embedding_function = None
        return self._embedding_function

    def create_collection(self, name: str, documents: List[Dict[str, Any]], overwrite: bool = False) -> None:
        """
        Create a new collection and add documents.

        Args:
            name: Name of the collection
            documents: List of document chunks (each with 'content' and 'metadata')
            overwrite: Whether to overwrite existing collection
        """
        client = self._get_client()
        embedding_func = self._get_embedding_function()

        # Check if collection exists
        collection = None
        try:
            collection = client.get_collection(name)
            if overwrite:
                # Delete the entire collection and recreate
                client.delete_collection(name)
                console.print(f"[blue]Deleted existing collection '{name}'[/blue]")
                collection = None  # Force recreation below
            else:
                console.print(f"[yellow]Collection '{name}' already exists. Use --overwrite to replace.[/yellow]")
                return
        except (ValueError, Exception):
            # Collection doesn't exist
            collection = None

        # Create collection if it doesn't exist or was deleted
        if collection is None:
            if embedding_func is not None:
                collection = client.create_collection(
                    name=name,
                    embedding_function=embedding_func
                )
            else:
                collection = client.create_collection(name=name)

        # Prepare documents and metadata for ChromaDB
        contents = [doc["content"] for doc in documents]
        metadatas = [doc["metadata"] for doc in documents]
        ids = [f"{name}_{i}" for i in range(len(documents))]

        # Add documents to collection
        collection.add(
            documents=contents,
            metadatas=metadatas,
            ids=ids
        )

        console.print(f"[green]Created collection '{name}' with {len(documents)} documents[/green]")

    def get_collection(self, name: str):
        """
        Get a collection by name.

        Args:
            name: Name of the collection

        Returns:
            ChromaDB collection object
        """
        client = self._get_client()

        try:
            return client.get_collection(name)
        except Exception:
            raise ValueError(f"Collection '{name}' not found")

    def list_collections(self) -> List[str]:
        """
        List all available collections.

        Returns:
            List of collection names
        """
        client = self._get_client()
        return [col.name for col in client.list_collections()]

    def delete_collection(self, name: str) -> None:
        """
        Delete a collection.

        Args:
            name: Name of the collection to delete
        """
        client = self._get_client()
        try:
            client.delete_collection(name)
            console.print(f"[green]Deleted collection '{name}'[/green]")
        except Exception as e:
            console.print(f"[red]Error deleting collection: {e}[/red]")

    def query(self, collection_name: str, query_text: str, limit: int = 5) -> Dict[str, Any]:
        """
        Query a collection for similar documents.

        Args:
            collection_name: Name of the collection to query
            query_text: The query text
            limit: Maximum number of results to return

        Returns:
            Dictionary with 'results', 'distances', and 'ids'
        """
        client = self._get_client()

        try:
            collection = client.get_collection(collection_name)

            results = collection.query(
                query_texts=[query_text],
                n_results=limit
            )

            return {
                "results": results["documents"][0],
                "distances": results["distances"][0],
                "ids": results["ids"][0],
                "metadatas": results["metadatas"][0]
            }

        except Exception as e:
            console.print(f"[red]Error querying collection: {e}[/red]")
            return {
                "results": [],
                "distances": [],
                "ids": [],
                "metadatas": []
            }

    def get_document_by_id(self, collection_name: str, doc_id: str) -> Optional[Dict[str, Any]]:
        """
        Get a document by its ID.

        Args:
            collection_name: Name of the collection
            doc_id: ID of the document

        Returns:
            Document data or None if not found
        """
        try:
            collection = self.get_collection(collection_name)
            result = collection.get(ids=[doc_id])

            if result["ids"] and result["ids"][0] == doc_id:
                return {
                    "content": result["documents"][0],
                    "metadata": result["metadatas"][0]
                }
            return None
        except Exception as e:
            console.print(f"[red]Error getting document: {e}[/red]")
            return None

    def clear(self) -> None:
        """Clear all collections."""
        client = self._get_client()
        collections = client.list_collections()
        for collection in collections:
            client.delete_collection(collection.name)
        console.print("[green]All collections cleared[/green]")

    def reset_client(self) -> None:
        """Reset the ChromaDB client (useful for changing settings)."""
        if self._client is not None:
            try:
                self._client.__exit__(None, None, None)
            except:
                pass
            self._client = None
        self._embedding_function = None
