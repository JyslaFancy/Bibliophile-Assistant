"""
Question Answering engine using Ollama and ChromaDB.
"""

import os
import json
from typing import Dict, Any, List, Optional
from rich.console import Console

console = Console()


class QAEngine:
    """Handles question answering using document retrieval and Ollama."""
    
    def __init__(self, model_name: str = "llama3", chroma_path: str = None, base_url: str = "http://localhost:11434"):
        """
        Initialize the QA engine.
        
        Args:
            model_name: Name of the Ollama model to use for answering
            chroma_path: Path to the ChromaDB data directory
            base_url: Base URL for the Ollama API
        """
        self.model_name = model_name
        self.chroma_path = chroma_path
        self.base_url = base_url
        self._vector_store = None
        self._init_vector_store()
    
    def _init_vector_store(self) -> None:
        """Initialize the vector store manager."""
        from .vectorstore import VectorStoreManager
        
        if self.chroma_path:
            self._vector_store = VectorStoreManager(
                persist_directory=self.chroma_path,
                base_url=self.base_url
            )
        else:
            self._vector_store = VectorStoreManager(base_url=self.base_url)
    
    def _generate_prompt(self, query: str, context: str = "") -> str:
        """
        Generate a prompt for the LLM based on the query and context.
        
        Args:
            query: The user's question
            context: Relevant context from documents
            
        Returns:
            Formatted prompt for the LLM
        """
        if context:
            return f"""You are an AI assistant helping users find information in their documents.
Based on the following context from the user's documents, answer the question.

Context:
{context}

Question: {query}

Answer the question using only the information from the context. If the answer is not in the context, say "I don't know" or "I couldn't find that information in your documents."

Answer:"""
        else:
            return f"""You are an AI assistant. Answer the following question: {query}

Answer:"""
    
    def _call_ollama(self, prompt: str, temperature: float = 0.7) -> str:
        """
        Call the Ollama API to get a response.
        
        Args:
            prompt: The prompt to send to the model
            temperature: Temperature for the model response
            
        Returns:
            The model's response
        """
        import requests
        
        try:
            response = requests.post(
                f"{self.base_url}/api/generate",
                json={
                    "model": self.model_name,
                    "prompt": prompt,
                    "stream": False,
                    "options": {
                        "temperature": temperature,
                        "top_p": 0.9,
                        "top_k": 50
                    }
                },
                timeout=120
            )
            
            if response.status_code == 200:
                data = response.json()
                if "response" in data:
                    return data["response"]
                elif "error" in data:
                    raise ValueError(f"Ollama error: {data['error']}")
                else:
                    raise ValueError(f"Unexpected response format: {data}")
            else:
                raise ValueError(f"HTTP error: {response.status_code} - {response.text}")
                
        except requests.exceptions.Timeout:
            raise ValueError("Ollama request timed out")
        except requests.exceptions.ConnectionError:
            raise ValueError(f"Cannot connect to Ollama at {self.base_url}. Make sure Ollama is running.")
        except Exception as e:
            raise ValueError(f"Error calling Ollama: {e}")
    
    def query(self, collection_name: str, question: str, limit: int = 5) -> Dict[str, Any]:
        """
        Query a collection and get an answer.
        
        Args:
            collection_name: Name of the ChromaDB collection to query
            question: The user's question
            limit: Number of documents to retrieve
            
        Returns:
            Dictionary with 'answer', 'sources', and other metadata
        """
        # Step 1: Retrieve relevant documents from ChromaDB
        with console.status("[bold blue]Searching for relevant information..."):
            results = self._vector_store.query(
                collection_name=collection_name,
                query_text=question,
                limit=limit
            )
        
        if not results["results"]:
            return {
                "answer": "I couldn't find any relevant information in your documents.",
                "sources": [],
                "confidence": 0.0
            }
        
        # Step 2: Format the context from retrieved documents
        context_parts = []
        sources = []
        
        for i, (doc, metadata) in enumerate(zip(results["results"], results["metadatas"])):
            if doc and doc.strip():
                source = metadata.get("source", "unknown") if metadata else "unknown"
                file_type = metadata.get("file_type", "unknown") if metadata else "unknown"
                chunk_index = metadata.get("chunk_index", 0) if metadata else 0
                
                context_parts.append(f"--- Document {i+1} (from {source}) ---\n{doc}")
                sources.append(f"{source} (chunk {chunk_index})")
        
        context = "\n\n".join(context_parts) if context_parts else ""
        
        # Step 3: Generate prompt and call Ollama
        prompt = self._generate_prompt(question, context)
        
        with console.status("[bold blue]Generating answer..."):
            try:
                answer = self._call_ollama(prompt)
            except Exception as e:
                console.print(f"[red]Error generating answer: {e}[/red]")
                answer = "I'm sorry, I couldn't generate an answer at this time."
        
        # Calculate confidence (simple heuristic based on retrieval scores)
        if results["distances"]:
            # Convert distances to confidence (lower distance = higher confidence)
            distances = [1.0 - float(d) if d < 1.0 else 0.0 for d in results["distances"]]
            confidence = sum(distances) / len(distances) if distances else 0.0
        else:
            confidence = 0.0
        
        return {
            "answer": answer,
            "sources": sources,
            "confidence": confidence,
            "retrieved_documents": results["results"],
            "distances": results["distances"]
        }
    
    def chat(self, collection_name: str, messages: List[Dict[str, str]], limit: int = 5) -> Dict[str, Any]:
        """
        Have a chat conversation with context from documents.
        
        Args:
            collection_name: Name of the ChromaDB collection
            messages: List of message dictionaries with 'role' and 'content'
            limit: Number of documents to retrieve
            
        Returns:
            Dictionary with 'answer', 'sources', etc.
        """
        # For now, we'll just use the last user message
        # In a full implementation, we'd maintain conversation context
        user_messages = [m for m in messages if m.get("role") == "user"]
        
        if not user_messages:
            return {
                "answer": "Please ask a question.",
                "sources": [],
                "confidence": 0.0
            }
        
        question = user_messages[-1].get("content", "")
        return self.query(collection_name, question, limit)
    
    def get_context(self, collection_name: str, question: str, limit: int = 5) -> str:
        """
        Get the retrieved context for a question without generating an answer.
        Useful for debugging or manual review.
        
        Args:
            collection_name: Name of the ChromaDB collection
            question: The question to find context for
            limit: Number of documents to retrieve
            
        Returns:
            The retrieved context as a string
        """
        results = self._vector_store.query(
            collection_name=collection_name,
            query_text=question,
            limit=limit
        )
        
        context_parts = []
        for i, (doc, metadata) in enumerate(zip(results["results"], results["metadatas"])):
            if doc and doc.strip():
                source = metadata.get("source", "unknown") if metadata else "unknown"
                context_parts.append(f"--- From {source} ---\n{doc}")
        
        return "\n\n".join(context_parts) if context_parts else "No relevant context found."
