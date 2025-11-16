"""
LLM wrapper module for Gemini API integration.
"""

import os
from typing import Optional, Iterator
from backend.config import (
    GEMINI_API_KEY,
    GEMINI_MODEL,
    CLAUDE_API_KEY,
    CLAUDE_MODEL,
    MAX_TOKENS,
    TEMPERATURE
)


class LLMWrapper:
    """Wrapper for Gemini LLM API."""
    
    def __init__(self, provider: str = "gemini"):
        """
        Initialize LLM wrapper.

        Args:
            provider: provider name, e.g. "gemini", "openai", "huggingface", or "claude".
        """
        self.provider = provider.lower()
        supported = {"gemini", "openai", "huggingface", "claude"}
        if self.provider not in supported:
            raise ValueError(f"Unsupported LLM provider: {self.provider}. Supported: {supported}")

        # Gemini config
        self.gemini_api_key = GEMINI_API_KEY
        self.gemini_model = GEMINI_MODEL

        # Claude config
        self.claude_api_key = CLAUDE_API_KEY
        self.claude_model = CLAUDE_MODEL

        if self.provider == "gemini" and not self.gemini_api_key:
            raise ValueError("Gemini API key not found. Set GEMINI_API_KEY in environment or .env file.")
        if self.provider == "claude" and not self.claude_api_key:
            raise ValueError("Claude API key not found. Set CLAUDE_API_KEY in environment or .env file.")
    
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
        # Dispatch to provider-specific implementations
        if self.provider == "gemini":
            return self._generate_gemini(prompt, context, stream)
        elif self.provider == "claude":
            return self._generate_claude(prompt, context, stream)
        elif self.provider == "openai":
            return self._generate_openai(prompt, context, stream)
        elif self.provider == "huggingface":
            return self._generate_huggingface(prompt, context, stream)
        else:
            raise ValueError(f"Unsupported provider: {self.provider}")
    
    def _generate_gemini(self, prompt: str, context: Optional[str] = None, stream: bool = False) -> str:
        """Generate response using Google Gemini API."""
        try:
            import google.generativeai as genai
            
            # Configure Gemini API
            genai.configure(api_key=self.gemini_api_key)
            
            # Get list of available models that support generateContent
            available_models = []
            try:
                for m in genai.list_models():
                    if 'generateContent' in m.supported_generation_methods:
                        # Extract model name (remove 'models/' prefix if present)
                        model_name = m.name.replace('models/', '') if m.name.startswith('models/') else m.name
                        available_models.append(model_name)
            except:
                pass  # If we can't list models, continue with defaults
            
            # Try models in order of preference
            model_names_to_try = [
                self.gemini_model,  # Try configured model first
                "gemini-flash-latest",   # Stable latest (recommended)
                "gemini-2.5-flash",      # Latest fast model
                "gemini-2.5-pro",        # Latest capable model
                "gemini-pro-latest",     # Stable latest pro
                "gemini-2.0-flash",      # Version 2.0
            ]
            
            # If we got available models, prioritize those
            if available_models:
                # Reorder to try available models first
                prioritized = [m for m in model_names_to_try if m in available_models]
                model_names_to_try = prioritized + [m for m in model_names_to_try if m not in prioritized]
            
            model = None
            last_error = None
            for model_name in model_names_to_try:
                try:
                    # Just initialize the model - don't test it (saves API calls)
                    model = genai.GenerativeModel(model_name)
                    # Model initialized successfully
                    break
                except Exception as e:
                    last_error = e
                    error_str = str(e).lower()
                    # If it's a 404 or not found/supported error, try next model
                    if "404" in error_str or "not found" in error_str or "not supported" in error_str:
                        continue
                    # For other errors (like API key), raise immediately
                    raise
            
            if model is None:
                error_msg = f"Failed to initialize Gemini model. Tried: {model_names_to_try[:3]}"
                if available_models:
                    error_msg += f"\nAvailable models: {available_models[:5]}"
                error_msg += f"\nLast error: {str(last_error)}"
                raise Exception(error_msg)
            
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
            
            # Generate response with error handling for model compatibility
            try:
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
            except Exception as gen_error:
                # If generation fails with 404/not found, try alternative models
                error_str = str(gen_error).lower()
                if ("404" in error_str or "not found" in error_str or "not supported" in error_str) and available_models:
                    # Try alternative models from available list
                    for alt_model_name in available_models[:3]:
                        if alt_model_name == self.gemini_model:
                            continue
                        try:
                            alt_model = genai.GenerativeModel(alt_model_name)
                            response = alt_model.generate_content(
                                full_prompt,
                                generation_config=genai.types.GenerationConfig(
                                    max_output_tokens=MAX_TOKENS,
                                    temperature=TEMPERATURE
                                )
                            )
                            return response.text.strip()
                        except:
                            continue
                # Re-raise if we can't find a working model
                raise gen_error
        
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

    def _generate_claude(self, prompt: str, context: Optional[str] = None, stream: bool = False) -> str:
        """Generate response using Anthropic/Claude API (Claude Haiku 4.5).

        This function tries to use the `anthropic` Python client if installed. If
        the client is not available, it raises an ImportError explaining how to
        install it.
        """
        try:
            # Prefer the official Anthropic client if installed
            try:
                from anthropic import Client
                client = Client(api_key=self.claude_api_key)

                # Build prompt with context
                if context:
                    full_prompt = f"""You are a helpful assistant that answers questions based on the provided context.\n\nContext:\n{context}\n\nQuestion: {prompt}\n\nAnswer:"""
                else:
                    full_prompt = prompt

                # Anthropic completion parameters vary by client version; use a conservative call
                resp = client.completions.create(
                    model=self.claude_model,
                    prompt=full_prompt,
                    max_tokens=MAX_TOKENS,
                    temperature=TEMPERATURE
                )

                # Response text location may vary; handle common shapes
                if hasattr(resp, 'completion'):
                    return resp.completion.strip()
                if isinstance(resp, dict):
                    # try a few keys
                    for key in ("completion", "text", "output"):
                        if key in resp:
                            return str(resp[key]).strip()
                # Fallback: stringify
                return str(resp).strip()

            except ImportError:
                # Try the new `anthropic` package name or fallback guidance
                raise ImportError("Anthropic client not installed. Install with: pip install anthropic")

        except ImportError as ie:
            raise ImportError(str(ie))
        except Exception as e:
            raise Exception(f"Error generating Claude response: {str(e)}")
    
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

