"""
Streamlit frontend application for the Intelligent Document Knowledge Assistant.
Clean, minimal, modern UI with document upload, chat interface, and summarization.
"""

import streamlit as st
import sys
from pathlib import Path
import os

# Add backend to path
sys.path.append(str(Path(__file__).parent.parent))

from backend.rag_pipeline import RAGPipeline
from backend.config import DOCUMENTS_DIR, SUPPORTED_EXTENSIONS, DEFAULT_LLM_PROVIDER

# Page configuration
st.set_page_config(
    page_title="Document Knowledge Assistant",
    page_icon="📚",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS for minimal, clean design
st.markdown("""
    <style>
        /* Main container styling */
        .main {
            background-color: #f8f9fa;
        }
        
        /* Header styling */
        h1 {
            color: #2c3e50;
            font-weight: 300;
            letter-spacing: -0.5px;
        }
        
        h2, h3 {
            color: #34495e;
            font-weight: 400;
        }
        
        /* Chat message styling */
        .user-message {
            background-color: #e8ecef;
            padding: 12px 16px;
            border-radius: 12px;
            margin: 8px 0;
            border-left: 3px solid #6c757d;
        }
        
        .bot-message {
            background-color: #ffffff;
            padding: 12px 16px;
            border-radius: 12px;
            margin: 8px 0;
            border-left: 3px solid #495057;
            box-shadow: 0 1px 3px rgba(0,0,0,0.1);
        }
        
        .source-badge {
            background-color: #f1f3f5;
            padding: 4px 8px;
            border-radius: 4px;
            font-size: 0.75rem;
            color: #495057;
            margin: 4px 4px 0 0;
            display: inline-block;
        }
        
        /* Button styling */
        .stButton>button {
            background-color: #495057;
            color: white;
            border: none;
            border-radius: 6px;
            padding: 0.5rem 1.5rem;
            font-weight: 400;
            transition: background-color 0.3s;
        }
        
        .stButton>button:hover {
            background-color: #343a40;
        }
        
        /* Sidebar styling */
        .sidebar .sidebar-content {
            background-color: #ffffff;
        }
        
        /* File uploader styling */
        .uploadedFile {
            background-color: #f8f9fa;
            border: 1px solid #dee2e6;
            border-radius: 6px;
            padding: 8px;
            margin: 4px 0;
        }
        
        /* Status indicators */
        .status-success {
            color: #28a745;
        }
        
        .status-info {
            color: #17a2b8;
        }
        
        /* Hide Streamlit branding */
        #MainMenu {visibility: hidden;}
        footer {visibility: hidden;}
        header {visibility: hidden;}
    </style>
""", unsafe_allow_html=True)


def initialize_session_state():
    """Initialize session state variables."""
    if "rag_pipeline" not in st.session_state:
        try:
            st.session_state.rag_pipeline = RAGPipeline(llm_provider=DEFAULT_LLM_PROVIDER)
        except Exception as e:
            st.session_state.rag_pipeline = None
            st.error(f"Failed to initialize RAG pipeline: {str(e)}")
    
    if "chat_history" not in st.session_state:
        st.session_state.chat_history = []
    
    if "processed_files" not in st.session_state:
        st.session_state.processed_files = []


def get_statistics():
    """Get current system statistics."""
    if st.session_state.rag_pipeline is None:
        return {
            "total_documents": 0,
            "total_chunks": 0,
            "status": "Not initialized"
        }
    
    try:
        stats = st.session_state.rag_pipeline.get_statistics()
        return {
            "total_documents": stats["documents"],
            "total_chunks": stats["total_vectors"],
            "status": "Ready"
        }
    except:
        return {
            "total_documents": 0,
            "total_chunks": 0,
            "status": "Error"
        }


def display_chat_message(role: str, content: str, sources: list = None):
    """Display a chat message with proper styling."""
    if role == "user":
        st.markdown(f'<div class="user-message"><strong>You:</strong> {content}</div>', unsafe_allow_html=True)
    else:
        st.markdown(f'<div class="bot-message"><strong>Assistant:</strong> {content}</div>', unsafe_allow_html=True)
        
        if sources:
            st.markdown("<br><strong>Sources:</strong>", unsafe_allow_html=True)
            source_text = ""
            for source in sources:
                source_text += f'<span class="source-badge">{source["filename"]} (chunk {source["chunk_index"]}, similarity: {source["similarity"]})</span>'
            st.markdown(source_text, unsafe_allow_html=True)


def main():
    """Main application function."""
    initialize_session_state()
    
    # Header
    st.title("📚 Intelligent Document Knowledge Assistant")
    st.markdown("---")
    
    # Sidebar
    with st.sidebar:
        st.header("System Status")
        
        stats = get_statistics()
        st.metric("Documents", stats["total_documents"])
        st.metric("Total Chunks", stats["total_chunks"])
        st.markdown(f"**Status:** <span class='status-info'>{stats['status']}</span>", unsafe_allow_html=True)
        
        st.markdown("---")
        
        st.header("Configuration")
        
        # LLM Provider (Gemini only)
        st.info("**LLM Provider:** Gemini (configured via GEMINI_API_KEY)")
        
        if not st.session_state.rag_pipeline:
            st.warning("⚠️ RAG pipeline not initialized. Check your GEMINI_API_KEY in .env file.")
        
        st.markdown("---")
        
        st.markdown("### About")
        st.markdown("""
        Upload documents (PDF, DOCX, TXT) and ask questions.
        The system uses RAG (Retrieval-Augmented Generation) to provide accurate answers based on your documents.
        """)
    
    # Main content area
    tab1, tab2, tab3 = st.tabs(["📄 Upload Documents", "💬 Chat", "📊 Summarize"])
    
    # Tab 1: Document Upload
    with tab1:
        st.header("Upload Documents")
        st.markdown("Upload PDF, DOCX, or TXT files to build your knowledge base.")
        
        uploaded_files = st.file_uploader(
            "Choose files",
            type=["pdf", "docx", "txt"],
            accept_multiple_files=True
        )
        
        if uploaded_files:
            st.markdown("### Uploaded Files")
            
            for uploaded_file in uploaded_files:
                col1, col2 = st.columns([3, 1])
                
                with col1:
                    st.write(f"**{uploaded_file.name}** ({uploaded_file.size:,} bytes)")
                
                with col2:
                    if st.button("Process", key=f"process_{uploaded_file.name}"):
                        with st.spinner(f"Processing {uploaded_file.name}..."):
                            try:
                                # Save file
                                file_path = st.session_state.rag_pipeline.file_parser.save_uploaded_file(
                                    uploaded_file, uploaded_file.name
                                )
                                
                                # Process document
                                result = st.session_state.rag_pipeline.process_document(file_path)
                                
                                if result["success"]:
                                    st.success(f"✅ Processed {result['filename']} ({result['chunks_count']} chunks)")
                                    if uploaded_file.name not in st.session_state.processed_files:
                                        st.session_state.processed_files.append(uploaded_file.name)
                                else:
                                    st.error(f"❌ Error: {result.get('error', 'Unknown error')}")
                            
                            except Exception as e:
                                st.error(f"❌ Error processing file: {str(e)}")
            
            st.markdown("---")
            
            # Show processed files
            if st.session_state.processed_files:
                st.markdown("### Processed Files")
                for filename in st.session_state.processed_files:
                    st.markdown(f"- ✅ {filename}")
    
    # Tab 2: Chat Interface
    with tab2:
        st.header("Chat with Your Documents")
        
        # Display chat history
        chat_container = st.container()
        with chat_container:
            for message in st.session_state.chat_history:
                display_chat_message(
                    message["role"],
                    message["content"],
                    message.get("sources")
                )
        
        # Chat input
        st.markdown("---")
        query = st.text_input(
            "Ask a question about your documents:",
            key="chat_input",
            placeholder="Type your question here..."
        )
        
        col1, col2 = st.columns([1, 5])
        with col1:
            send_button = st.button("Send", type="primary", use_container_width=True)
        
        if send_button and query:
            # Add user message to history
            st.session_state.chat_history.append({
                "role": "user",
                "content": query
            })
            
            # Generate response
            with st.spinner("Thinking..."):
                try:
                    result = st.session_state.rag_pipeline.answer_question(query)
                    
                    # Add bot response to history
                    st.session_state.chat_history.append({
                        "role": "assistant",
                        "content": result["answer"],
                        "sources": result.get("sources", [])
                    })
                    
                    st.rerun()
                
                except Exception as e:
                    st.error(f"Error generating response: {str(e)}")
                    st.session_state.chat_history.append({
                        "role": "assistant",
                        "content": f"Sorry, I encountered an error: {str(e)}"
                    })
                    st.rerun()
        
        # Clear chat button
        if st.session_state.chat_history:
            if st.button("Clear Chat History"):
                st.session_state.chat_history = []
                st.rerun()
    
    # Tab 3: Multi-Document Summarization
    with tab3:
        st.header("Multi-Document Summary")
        st.markdown("Generate a comprehensive summary across all uploaded documents.")
        
        col1, col2 = st.columns([2, 1])
        
        with col1:
            summary_type = st.selectbox(
                "Summary Type",
                ["comprehensive", "brief", "detailed"],
                index=0
            )
        
        with col2:
            generate_button = st.button("Generate Summary", type="primary", use_container_width=True)
        
        if generate_button:
            with st.spinner("Generating summary..."):
                try:
                    result = st.session_state.rag_pipeline.generate_multi_document_summary(summary_type)
                    
                    if result["success"]:
                        st.success(f"✅ Summary generated from {result['document_count']} document(s) with {result['total_chunks']} total chunks")
                        st.markdown("---")
                        st.markdown("### Summary")
                        st.markdown(result["summary"])
                    else:
                        st.error(f"❌ Error: {result.get('error', 'Unknown error')}")
                
                except Exception as e:
                    st.error(f"Error generating summary: {str(e)}")


if __name__ == "__main__":
    main()

