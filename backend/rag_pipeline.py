"""
RAG Pipeline module that orchestrates the complete retrieval-augmented generation workflow.
"""

import re
from typing import List, Dict, Tuple
from backend.file_parser import FileParser
from backend.embeddings import EmbeddingGenerator
from backend.vector_store import VectorStore
from backend.llm import LLMWrapper
from backend.config import CHUNK_SIZE, CHUNK_OVERLAP, TOP_K, SIMILARITY_THRESHOLD


class RAGPipeline:
    """Complete RAG pipeline for document processing and question answering."""
    
    def __init__(self, llm_provider: str = "gemini"):
        """Initialize RAG pipeline components."""
        self.file_parser = FileParser()
        self.embedding_generator = EmbeddingGenerator()
        self.vector_store = VectorStore(dimension=self.embedding_generator.get_embedding_dimension())
        self.llm = LLMWrapper(provider=llm_provider)
    
    def chunk_text(self, text: str, chunk_size: int = CHUNK_SIZE, overlap: int = CHUNK_OVERLAP) -> List[str]:
        """
        Split text into overlapping chunks.
        
        Args:
            text: Input text to chunk
            chunk_size: Size of each chunk in characters
            overlap: Number of characters to overlap between chunks
            
        Returns:
            List of text chunks
        """
        if not text or len(text) <= chunk_size:
            return [text] if text else []
        
        chunks = []
        start = 0
        
        while start < len(text):
            end = start + chunk_size
            
            # Try to break at sentence boundary
            if end < len(text):
                # Look for sentence endings near the chunk boundary
                sentence_endings = ['. ', '.\n', '! ', '!\n', '? ', '?\n']
                best_break = end
                
                for ending in sentence_endings:
                    # Check within last 100 characters of chunk
                    search_start = max(start, end - 100)
                    pos = text.rfind(ending, search_start, end)
                    if pos != -1:
                        best_break = pos + len(ending)
                        break
                
                end = best_break
            
            chunk = text[start:end].strip()
            if chunk:
                chunks.append(chunk)
            
            # Move start position with overlap
            start = end - overlap if end < len(text) else end
        
        return chunks
    
    def process_document(self, file_path: str) -> Dict:
        """
        Process a document: extract text, chunk, embed, and store.
        
        Args:
            file_path: Path to the document file
            
        Returns:
            Dictionary with processing results
        """
        try:
            # Extract text
            text = self.file_parser.extract_text(file_path)
            if not text:
                return {"success": False, "error": "No text extracted from document"}
            
            # Get file metadata
            metadata_info = self.file_parser.get_file_metadata(file_path)
            
            # Chunk text
            chunks = self.chunk_text(text)
            if not chunks:
                return {"success": False, "error": "No chunks created from document"}
            
            # Generate embeddings
            embeddings = self.embedding_generator.generate_embeddings_batch(chunks)
            
            # Create metadata for each chunk
            chunk_metadata = []
            for i, chunk in enumerate(chunks):
                chunk_metadata.append({
                    "filename": metadata_info["filename"],
                    "chunk_index": i,
                    "chunk_text": chunk,
                    "file_path": file_path,
                    "total_chunks": len(chunks)
                })
            
            # Add to vector store
            self.vector_store.add_vectors(embeddings, chunk_metadata)
            self.vector_store.save()
            
            return {
                "success": True,
                "filename": metadata_info["filename"],
                "chunks_count": len(chunks),
                "total_chunks": self.vector_store.get_size()
            }
        
        except Exception as e:
            return {"success": False, "error": str(e)}
    
    def retrieve_context(self, query: str, top_k: int = TOP_K) -> List[Tuple[Dict, float]]:
        """
        Retrieve relevant context chunks for a query.
        
        Args:
            query: User query
            top_k: Number of top results to retrieve
            
        Returns:
            List of tuples (metadata, similarity_score)
        """
        # Generate query embedding
        query_embedding = self.embedding_generator.generate_embedding(query)
        
        # Search vector store
        results = self.vector_store.search(query_embedding, top_k=top_k)
        
        # Filter by similarity threshold
        filtered_results = [
            (metadata, score) for metadata, score in results 
            if score >= SIMILARITY_THRESHOLD
        ]
        
        return filtered_results if filtered_results else results
    
    def answer_question(self, query: str, top_k: int = TOP_K) -> Dict:
        """
        Answer a question using RAG.
        
        Args:
            query: User question
            top_k: Number of context chunks to retrieve
            
        Returns:
            Dictionary with answer and sources
        """
        try:
            # Retrieve relevant context
            context_results = self.retrieve_context(query, top_k)
            
            if not context_results:
                return {
                    "answer": "I couldn't find relevant information in the documents to answer your question.",
                    "sources": [],
                    "context_used": False
                }
            
            # Build context string
            context_chunks = []
            sources = []
            
            for metadata, score in context_results:
                context_chunks.append(metadata["chunk_text"])
                sources.append({
                    "filename": metadata["filename"],
                    "chunk_index": metadata["chunk_index"],
                    "similarity": round(score, 3)
                })
            
            context = "\n\n---\n\n".join(context_chunks)
            
            # Generate answer using LLM
            answer = self.llm.generate_response(query, context=context)
            
            return {
                "answer": answer,
                "sources": sources,
                "context_used": True
            }
        
        except Exception as e:
            return {
                "answer": f"Error generating answer: {str(e)}",
                "sources": [],
                "context_used": False
            }
    
    def generate_multi_document_summary(self, summary_type: str = "comprehensive") -> Dict:
        """
        Generate a comprehensive summary across all documents.
        
        Args:
            summary_type: Type of summary ("comprehensive", "brief", "detailed")
            
        Returns:
            Dictionary with summary and document count
        """
        try:
            all_metadata = self.vector_store.get_all_metadata()
            
            if not all_metadata:
                return {
                    "success": False,
                    "error": "No documents found in the vector store."
                }
            
            # Get unique documents
            unique_docs = {}
            for metadata in all_metadata:
                filename = metadata["filename"]
                if filename not in unique_docs:
                    unique_docs[filename] = []
                unique_docs[filename].append(metadata["chunk_text"])
            
            # Combine chunks per document
            document_texts = []
            for filename, chunks in unique_docs.items():
                doc_text = "\n".join(chunks)
                document_texts.append(f"Document: {filename}\n\n{doc_text}")
            
            # Generate summary
            summary = self.llm.generate_summary(document_texts, summary_type=summary_type)
            
            return {
                "success": True,
                "summary": summary,
                "document_count": len(unique_docs),
                "total_chunks": len(all_metadata)
            }
        
        except Exception as e:
            return {
                "success": False,
                "error": str(e)
            }
    
    def get_statistics(self) -> Dict:
        """Get statistics about the vector store."""
        return {
            "total_vectors": self.vector_store.get_size(),
            "embedding_dimension": self.vector_store.dimension,
            "documents": len(set(m["filename"] for m in self.vector_store.get_all_metadata()))
        }

