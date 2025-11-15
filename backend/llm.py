"""
LLM wrapper module for Gemini API integration.
"""

import os
from typing import Optional, Iterator
from backend.config import (
    GEMINI_API_KEY,
    GEMINI_MODEL,
    MAX_TOKENS,
    TEMPERATURE
)


class LLMWrapper:
    """Wrapper for Gemini LLM API."""
    
    def __init__(self, provider: str = "gemini"):
        """
        Initialize LLM wrapper with Gemini.
        
        Args:
            provider: Must be "gemini" (only Gemini is supported)
        """
        self.provider = provider.lower()
        if self.provider != "gemini":
            raise ValueError(f"Only Gemini provider is supported. Got: {self.provider}")
        
        self.gemini_api_key = GEMINI_API_KEY
        self.gemini_model = GEMINI_MODEL
        
        if not self.gemini_api_key:
            raise ValueError("Gemini API key not found. Set GEMINI_API_KEY in environment or .env file.")
    
    def generate_response(self, prompt: str, context: Optional[str] = None, stream: bool = False) -> str:
        """
        Generate response from LLM using Gemini.
        
        Args:
            prompt: User query
            context: Retrieved context from RAG
            stream: Whether to stream the response
            
        Returns:
            Generated response text
        """
        if self.provider != "gemini":
            raise ValueError(f"Only Gemini provider is supported. Got: {self.provider}")
        return self._generate_gemini(prompt, context, stream)
    
    def _generate_gemini(self, prompt: str, context: Optional[str] = None, stream: bool = False) -> str:
        """Generate response using Google Gemini API."""
        try:
            import google.generativeai as genai
            
            # Configure Gemini API
            genai.configure(api_key=self.gemini_api_key)
            
            # Try to initialize the model, with fallback to alternative models
            model = None
            model_names_to_try = [
                self.gemini_model,  # Try configured model first
                "gemini-1.5-flash",  # Fast and efficient (recommended)
                "gemini-1.5-pro",    # More capable
            ]
            
            last_error = None
            successful_model = None
            for model_name in model_names_to_try:
                try:
                    model = genai.GenerativeModel(model_name)
                    successful_model = model_name
                    # Model initialized successfully
                    break
                except Exception as e:
                    last_error = e
                    # If it's a 404 error, try next model
                    if "404" in str(e) or "not found" in str(e).lower():
                        continue
                    # For other errors (like API key), raise immediately
                    raise
            
            if model is None:
                # Try to get available models for better error message
                try:
                    available_models = []
                    for m in genai.list_models():
                        if 'generateContent' in m.supported_generation_methods:
                            # Extract just the model name (remove full path)
                            model_name = m.name.split('/')[-1] if '/' in m.name else m.name
                            available_models.append(model_name)
                    raise Exception(
                        f"Model '{self.gemini_model}' not found. "
                        f"Tried: {model_names_to_try}. "
                        f"Available models: {available_models[:5]}. "
                        f"Error: {str(last_error)}"
                    )
                except Exception as list_error:
                    # If we can't list models, just report the original error
                    raise Exception(
                        f"Model '{self.gemini_model}' not found. "
                        f"Tried: {model_names_to_try}. "
                        f"Error: {str(last_error)}. "
                        f"Note: Common model names are 'gemini-1.5-flash' or 'gemini-1.5-pro'"
                    )
            
            # Construct prompt with context
            full_prompt = ""
            if context:
                full_prompt = f"""You are a helpful assistant that answers questions based on the provided context.

Context:
{context}

Use the context above to answer the user's question. If the context doesn't contain enough information, say so.

Question: {prompt}

Answer:"""
            else:
                full_prompt = prompt
            
            # Generate response
            if stream:
                full_response = ""
                response = model.generate_content(
                    full_prompt,
                    generation_config=genai.types.GenerationConfig(
                        max_output_tokens=MAX_TOKENS,
                        temperature=TEMPERATURE
                    ),
                    stream=True
                )
                for chunk in response:
                    if chunk.text:
                        full_response += chunk.text
                return full_response.strip()
            else:
                response = model.generate_content(
                    full_prompt,
                    generation_config=genai.types.GenerationConfig(
                        max_output_tokens=MAX_TOKENS,
                        temperature=TEMPERATURE
                    )
                )
                return response.text.strip()
        
        except ImportError:
            raise ImportError("Google Generative AI library not installed. Install with: pip install google-generativeai")
        except Exception as e:
            raise Exception(f"Error generating Gemini response: {str(e)}")
    
    def _generate_openai(self, prompt: str, context: Optional[str] = None, stream: bool = False) -> str:
        """Generate response using OpenAI API."""
        try:
            from openai import OpenAI
            
            client = OpenAI(api_key=self.openai_api_key)
            
            # Construct messages
            messages = []
            if context:
                system_message = f"""You are a helpful assistant that answers questions based on the provided context.
                
Context:
{context}

Use the context above to answer the user's question. If the context doesn't contain enough information, say so."""
                messages.append({"role": "system", "content": system_message})
            
            messages.append({"role": "user", "content": prompt})
            
            # Generate response
            response = client.chat.completions.create(
                model=self.openai_model,
                messages=messages,
                max_tokens=MAX_TOKENS,
                temperature=TEMPERATURE,
                stream=stream
            )
            
            if stream:
                full_response = ""
                for chunk in response:
                    if chunk.choices[0].delta.content:
                        full_response += chunk.choices[0].delta.content
                return full_response
            else:
                return response.choices[0].message.content.strip()
        
        except ImportError:
            raise ImportError("OpenAI library not installed. Install with: pip install openai")
        except Exception as e:
            raise Exception(f"Error generating OpenAI response: {str(e)}")
    
    def _generate_huggingface(self, prompt: str, context: Optional[str] = None, stream: bool = False) -> str:
        """Generate response using HuggingFace API."""
        try:
            from huggingface_hub import InferenceClient
            
            client = InferenceClient(token=self.huggingface_api_key)
            
            # Construct prompt with context
            full_prompt = ""
            if context:
                full_prompt = f"""Context:
{context}

Question: {prompt}

Answer:"""
            else:
                full_prompt = prompt
            
            # Generate response
            response = client.text_generation(
                full_prompt,
                model=self.huggingface_model,
                max_new_tokens=MAX_TOKENS,
                temperature=TEMPERATURE,
                return_full_text=False
            )
            
            return response.strip()
        
        except ImportError:
            raise ImportError("HuggingFace Hub library not installed. Install with: pip install huggingface_hub")
        except Exception as e:
            raise Exception(f"Error generating HuggingFace response: {str(e)}")
    
    def generate_summary(self, texts: list, summary_type: str = "comprehensive") -> str:
        """
        Generate a summary across multiple documents.
        
        Args:
            texts: List of text chunks to summarize
            summary_type: Type of summary ("comprehensive", "brief", "detailed")
            
        Returns:
            Generated summary
        """
        combined_text = "\n\n---\n\n".join(texts)
        
        summary_prompt = f"""Generate a {summary_type} summary of the following documents. 
Provide key insights, main topics, and important information.

Documents:
{combined_text}

Summary:"""
        
        return self.generate_response(summary_prompt, context=None)

