"""LLM client implementation using LiteLLM."""

from typing import Optional
import litellm
from ..config import config


class LLMClient:
    """Unified LLM client supporting multiple providers."""
    
    def __init__(self, model: Optional[str] = None):
        """
        Initialize LLM client.
        
        Args:
            model: Model name (e.g., 'gpt-4o', 'claude-3-opus-20240229')
        """
        self.model = model or config.default_model
        
        # Configure API keys
        if config.openai_api_key:
            litellm.api_key = config.openai_api_key
        if config.anthropic_api_key:
            litellm.anthropic_key = config.anthropic_api_key
    
    def chat(
        self,
        message: str,
        system_prompt: Optional[str] = None,
        temperature: Optional[float] = None,
        max_tokens: int = 4096,
    ) -> str:
        """
        Send a chat message and get a response.
        
        Args:
            message: User message
            system_prompt: Optional system prompt
            temperature: Sampling temperature (0-1)
            max_tokens: Maximum response tokens
            
        Returns:
            Assistant response text
        """
        messages = []
        
        if system_prompt:
            messages.append({"role": "system", "content": system_prompt})
        
        messages.append({"role": "user", "content": message})
        
        response = litellm.completion(
            model=self.model,
            messages=messages,
            temperature=temperature or config.temperature,
            max_tokens=max_tokens,
        )
        
        return response.choices[0].message.content
    
    def chat_stream(
        self,
        message: str,
        system_prompt: Optional[str] = None,
        temperature: Optional[float] = None,
    ):
        """
        Send a chat message and stream the response.
        
        Args:
            message: User message
            system_prompt: Optional system prompt
            temperature: Sampling temperature (0-1)
            
        Yields:
            Response text chunks
        """
        messages = []
        
        if system_prompt:
            messages.append({"role": "system", "content": system_prompt})
        
        messages.append({"role": "user", "content": message})
        
        response = litellm.completion(
            model=self.model,
            messages=messages,
            temperature=temperature or config.temperature,
            stream=True,
        )
        
        for chunk in response:
            if chunk.choices[0].delta.content:
                yield chunk.choices[0].delta.content


# Global client instance (lazy initialization)
_client: Optional[LLMClient] = None


def get_llm_client(model: Optional[str] = None) -> LLMClient:
    """
    Get or create the global LLM client.
    
    Args:
        model: Optional model override
        
    Returns:
        LLMClient instance
    """
    global _client
    
    if model:
        return LLMClient(model)
    
    if _client is None:
        _client = LLMClient()
    
    return _client
