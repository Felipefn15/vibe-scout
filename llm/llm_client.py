#!/usr/bin/env python3
"""
Modular LLM Client with Automatic Fallback
Supports multiple free LLM providers with automatic failover
"""

import json
import logging
import time
import os
from typing import Dict, List, Optional, Any, Union
from abc import ABC, abstractmethod
from dataclasses import dataclass
from dotenv import load_dotenv
import requests
import asyncio
import aiohttp

load_dotenv()

logger = logging.getLogger(__name__)

@dataclass
class LLMResponse:
    """Standardized LLM response format"""
    content: str
    model: str
    provider: str
    tokens_used: Optional[int] = None
    cost: Optional[float] = None
    latency: Optional[float] = None
    success: bool = True
    error_message: Optional[str] = None

@dataclass
class LLMConfig:
    """Configuration for LLM providers"""
    name: str
    api_key_env: str
    base_url: str
    models: List[str]
    max_tokens: int = 2048
    temperature: float = 0.7
    timeout: int = 30
    rate_limit_per_minute: int = 60
    cost_per_1k_tokens: float = 0.0  # Free tier

class BaseLLMProvider(ABC):
    """Abstract base class for LLM providers"""
    
    def __init__(self, config: LLMConfig):
        self.config = config
        self.api_key = os.getenv(config.api_key_env)
        self.last_request_time = 0
        self.request_count = 0
        self.reset_time = time.time()
    
    @abstractmethod
    async def generate(self, prompt: str, model: str = None, **kwargs) -> LLMResponse:
        """Generate response from LLM"""
        pass
    
    def _rate_limit_check(self):
        """Check and enforce rate limits"""
        current_time = time.time()
        
        # Reset counter if minute has passed
        if current_time - self.reset_time >= 60:
            self.request_count = 0
            self.reset_time = current_time
        
        # Check if we're at the limit
        if self.request_count >= self.config.rate_limit_per_minute:
            sleep_time = 60 - (current_time - self.reset_time)
            if sleep_time > 0:
                logger.warning(f"Rate limit reached for {self.config.name}. Waiting {sleep_time:.1f}s")
                time.sleep(sleep_time)
                self.request_count = 0
                self.reset_time = time.time()
        
        self.request_count += 1
        self.last_request_time = current_time

class GroqProvider(BaseLLMProvider):
    """Groq LLM provider implementation"""
    
    def __init__(self):
        config = LLMConfig(
            name="Groq",
            api_key_env="GROQ_API_KEY",
            base_url="https://api.groq.com/openai/v1",
            models=["llama3-8b-8192", "mixtral-8x7b-32768", "gemma2-9b-it"],
            max_tokens=2048,
            rate_limit_per_minute=45,  # Free tier limit
            cost_per_1k_tokens=0.0
        )
        super().__init__(config)
    
    async def generate(self, prompt: str, model: str = None, **kwargs) -> LLMResponse:
        """Generate response using Groq API"""
        if not self.api_key:
            return LLMResponse(
                content="",
                model=model or self.config.models[0],
                provider=self.config.name,
                success=False,
                error_message="API key not found"
            )
        
        self._rate_limit_check()
        
        try:
            start_time = time.time()
            
            # Use aiohttp for async requests
            async with aiohttp.ClientSession() as session:
                headers = {
                    "Authorization": f"Bearer {self.api_key}",
                    "Content-Type": "application/json"
                }
                
                payload = {
                    "model": model or self.config.models[0],
                    "messages": [
                        {"role": "user", "content": prompt}
                    ],
                    "max_tokens": kwargs.get('max_tokens', self.config.max_tokens),
                    "temperature": kwargs.get('temperature', self.config.temperature)
                }
                
                async with session.post(
                    f"{self.config.base_url}/chat/completions",
                    headers=headers,
                    json=payload,
                    timeout=aiohttp.ClientTimeout(total=self.config.timeout)
                ) as response:
                    if response.status == 200:
                        data = await response.json()
                        content = data['choices'][0]['message']['content']
                        usage = data.get('usage', {})
                        
                        latency = time.time() - start_time
                        
                        return LLMResponse(
                            content=content,
                            model=model or self.config.models[0],
                            provider=self.config.name,
                            tokens_used=usage.get('total_tokens'),
                            latency=latency,
                            success=True
                        )
                    else:
                        error_text = await response.text()
                        return LLMResponse(
                            content="",
                            model=model or self.config.models[0],
                            provider=self.config.name,
                            success=False,
                            error_message=f"HTTP {response.status}: {error_text}"
                        )
                        
        except Exception as e:
            logger.error(f"Groq API error: {e}")
            return LLMResponse(
                content="",
                model=model or self.config.models[0],
                provider=self.config.name,
                success=False,
                error_message=str(e)
            )

class OpenRouterProvider(BaseLLMProvider):
    """OpenRouter LLM provider implementation (free tier)"""
    
    def __init__(self):
        config = LLMConfig(
            name="OpenRouter",
            api_key_env="OPENROUTER_API_KEY",
            base_url="https://openrouter.ai/api/v1",
            models=["openai/gpt-3.5-turbo", "anthropic/claude-3-haiku", "meta-llama/llama-3.1-8b-instruct"],
            max_tokens=2048,
            rate_limit_per_minute=50,  # Free tier limit
            cost_per_1k_tokens=0.0
        )
        super().__init__(config)
    
    async def generate(self, prompt: str, model: str = None, **kwargs) -> LLMResponse:
        """Generate response using OpenRouter API"""
        if not self.api_key:
            return LLMResponse(
                content="",
                model=model or self.config.models[0],
                provider=self.config.name,
                success=False,
                error_message="API key not found"
            )
        
        self._rate_limit_check()
        
        try:
            start_time = time.time()
            
            async with aiohttp.ClientSession() as session:
                headers = {
                    "Authorization": f"Bearer {self.api_key}",
                    "Content-Type": "application/json",
                    "HTTP-Referer": "https://vibe-scout.com",  # Required by OpenRouter
                    "X-Title": "Vibe Scout Lead Generation"
                }
                
                payload = {
                    "model": model or self.config.models[0],
                    "messages": [
                        {"role": "user", "content": prompt}
                    ],
                    "max_tokens": kwargs.get('max_tokens', self.config.max_tokens),
                    "temperature": kwargs.get('temperature', self.config.temperature)
                }
                
                async with session.post(
                    f"{self.config.base_url}/chat/completions",
                    headers=headers,
                    json=payload,
                    timeout=aiohttp.ClientTimeout(total=self.config.timeout)
                ) as response:
                    if response.status == 200:
                        data = await response.json()
                        content = data['choices'][0]['message']['content']
                        usage = data.get('usage', {})
                        
                        latency = time.time() - start_time
                        
                        return LLMResponse(
                            content=content,
                            model=model or self.config.models[0],
                            provider=self.config.name,
                            tokens_used=usage.get('total_tokens'),
                            latency=latency,
                            success=True
                        )
                    else:
                        error_text = await response.text()
                        return LLMResponse(
                            content="",
                            model=model or self.config.models[0],
                            provider=self.config.name,
                            success=False,
                            error_message=f"HTTP {response.status}: {error_text}"
                        )
                        
        except Exception as e:
            logger.error(f"OpenRouter API error: {e}")
            return LLMResponse(
                content="",
                model=model or self.config.models[0],
                provider=self.config.name,
                success=False,
                error_message=str(e)
            )

class HuggingFaceProvider(BaseLLMProvider):
    """HuggingFace Inference API provider implementation"""
    
    def __init__(self):
        config = LLMConfig(
            name="HuggingFace",
            api_key_env="HUGGINGFACE_API_KEY",
            base_url="https://api-inference.huggingface.co/models",
            models=["microsoft/DialoGPT-medium", "gpt2", "distilgpt2"],  # Free models
            max_tokens=512,  # Shorter for free tier
            rate_limit_per_minute=30,
            cost_per_1k_tokens=0.0
        )
        super().__init__(config)
    
    async def generate(self, prompt: str, model: str = None, **kwargs) -> LLMResponse:
        """Generate response using HuggingFace Inference API"""
        if not self.api_key:
            return LLMResponse(
                content="",
                model=model or self.config.models[0],
                provider=self.config.name,
                success=False,
                error_message="API key not found"
            )
        
        self._rate_limit_check()
        
        try:
            start_time = time.time()
            
            async with aiohttp.ClientSession() as session:
                headers = {
                    "Authorization": f"Bearer {self.api_key}",
                    "Content-Type": "application/json"
                }
                
                payload = {
                    "inputs": prompt,
                    "parameters": {
                        "max_new_tokens": kwargs.get('max_tokens', self.config.max_tokens),
                        "temperature": kwargs.get('temperature', self.config.temperature),
                        "do_sample": True
                    }
                }
                
                model_name = model or self.config.models[0]
                async with session.post(
                    f"{self.config.base_url}/{model_name}",
                    headers=headers,
                    json=payload,
                    timeout=aiohttp.ClientTimeout(total=self.config.timeout)
                ) as response:
                    if response.status == 200:
                        data = await response.json()
                        # HuggingFace returns different formats depending on the model
                        if isinstance(data, list) and len(data) > 0:
                            content = data[0].get('generated_text', '')
                        else:
                            content = str(data)
                        
                        latency = time.time() - start_time
                        
                        return LLMResponse(
                            content=content,
                            model=model_name,
                            provider=self.config.name,
                            latency=latency,
                            success=True
                        )
                    else:
                        error_text = await response.text()
                        return LLMResponse(
                            content="",
                            model=model_name,
                            provider=self.config.name,
                            success=False,
                            error_message=f"HTTP {response.status}: {error_text}"
                        )
                        
        except Exception as e:
            logger.error(f"HuggingFace API error: {e}")
            return LLMResponse(
                content="",
                model=model or self.config.models[0],
                provider=self.config.name,
                success=False,
                error_message=str(e)
            )

class MockProvider(BaseLLMProvider):
    """Mock LLM provider for testing and fallback"""
    
    def __init__(self):
        config = LLMConfig(
            name="Mock",
            api_key_env="",
            base_url="",
            models=["mock-model"],
            max_tokens=100,
            rate_limit_per_minute=1000,
            cost_per_1k_tokens=0.0
        )
        super().__init__(config)
    
    async def generate(self, prompt: str, model: str = None, **kwargs) -> LLMResponse:
        """Generate mock response"""
        # Simple template-based response
        if "email" in prompt.lower():
            content = """Olá!

Identificamos oportunidades de melhoria digital para seu negócio.

Como especialistas em desenvolvimento de software, podemos ajudar você a:
• Melhorar a performance do seu site
• Desenvolver novas funcionalidades
• Criar aplicações mobile
• Modernizar seus sistemas

Gostaria de agendar uma conversa gratuita?

Atenciosamente,
Felipe França
TECHNOLOGIE FELIPE FRANCA"""
        else:
            content = "Esta é uma resposta simulada do LLM. Configure uma chave de API válida para respostas reais."
        
        return LLMResponse(
            content=content,
            model=model or "mock-model",
            provider=self.config.name,
            success=True
        )

class ModularLLMClient:
    """Main LLM client with automatic fallback"""
    
    def __init__(self, providers: List[str] = None):
        """
        Initialize LLM client with specified providers
        
        Args:
            providers: List of provider names to use (in order of preference)
        """
        self.providers = []
        self.response_cache = {}
        self.stats = {
            'total_requests': 0,
            'successful_requests': 0,
            'failed_requests': 0,
            'provider_stats': {}
        }
        
        # Default provider order (most reliable first)
        default_providers = ['Groq', 'OpenRouter', 'HuggingFace', 'Mock']
        providers = providers or default_providers
        
        # Initialize providers
        for provider_name in providers:
            provider = self._create_provider(provider_name)
            if provider:
                self.providers.append(provider)
                self.stats['provider_stats'][provider_name] = {
                    'requests': 0,
                    'successes': 0,
                    'failures': 0,
                    'total_latency': 0
                }
        
        if not self.providers:
            logger.warning("No LLM providers available. Using mock provider.")
            self.providers.append(MockProvider())
    
    def _create_provider(self, provider_name: str) -> Optional[BaseLLMProvider]:
        """Create provider instance by name"""
        providers_map = {
            'Groq': GroqProvider,
            'OpenRouter': OpenRouterProvider,
            'HuggingFace': HuggingFaceProvider,
            'Mock': MockProvider
        }
        
        provider_class = providers_map.get(provider_name)
        if provider_class:
            try:
                return provider_class()
            except Exception as e:
                logger.error(f"Failed to create {provider_name} provider: {e}")
                return None
        
        logger.warning(f"Unknown provider: {provider_name}")
        return None
    
    async def generate(self, prompt: str, model: str = None, use_cache: bool = True, **kwargs) -> LLMResponse:
        """
        Generate response with automatic fallback
        
        Args:
            prompt: Input prompt
            model: Specific model to use (optional)
            use_cache: Whether to use response caching
            **kwargs: Additional parameters for generation
        
        Returns:
            LLMResponse with content and metadata
        """
        self.stats['total_requests'] += 1
        
        # Check cache first
        if use_cache:
            cache_key = f"{prompt[:100]}_{model}_{hash(str(kwargs))}"
            if cache_key in self.response_cache:
                cached_response = self.response_cache[cache_key]
                logger.info(f"Using cached response from {cached_response.provider}")
                return cached_response
        
        # Try each provider in order
        for provider in self.providers:
            try:
                logger.info(f"Trying {provider.config.name} provider...")
                
                response = await provider.generate(prompt, model, **kwargs)
                
                # Update stats
                provider_name = provider.config.name
                self.stats['provider_stats'][provider_name]['requests'] += 1
                
                if response.success:
                    self.stats['successful_requests'] += 1
                    self.stats['provider_stats'][provider_name]['successes'] += 1
                    if response.latency:
                        self.stats['provider_stats'][provider_name]['total_latency'] += response.latency
                    
                    # Cache successful response
                    if use_cache:
                        cache_key = f"{prompt[:100]}_{model}_{hash(str(kwargs))}"
                        self.response_cache[cache_key] = response
                    
                    logger.info(f"Successfully generated response using {provider_name}")
                    return response
                else:
                    self.stats['failed_requests'] += 1
                    self.stats['provider_stats'][provider_name]['failures'] += 1
                    logger.warning(f"{provider_name} failed: {response.error_message}")
                    
            except Exception as e:
                logger.error(f"Error with {provider.config.name}: {e}")
                self.stats['failed_requests'] += 1
                self.stats['provider_stats'][provider.config.name]['failures'] += 1
        
        # All providers failed
        self.stats['failed_requests'] += 1
        logger.error("All LLM providers failed")
        
        return LLMResponse(
            content="Erro: Todos os provedores de LLM falharam. Verifique suas configurações de API.",
            model=model or "unknown",
            provider="none",
            success=False,
            error_message="All providers failed"
        )
    
    def get_stats(self) -> Dict:
        """Get usage statistics"""
        stats = self.stats.copy()
        
        # Calculate averages
        for provider_name, provider_stats in stats['provider_stats'].items():
            if provider_stats['requests'] > 0:
                provider_stats['success_rate'] = provider_stats['successes'] / provider_stats['requests']
                provider_stats['avg_latency'] = provider_stats['total_latency'] / provider_stats['successes']
            else:
                provider_stats['success_rate'] = 0
                provider_stats['avg_latency'] = 0
        
        return stats
    
    def clear_cache(self):
        """Clear response cache"""
        self.response_cache.clear()
        logger.info("Response cache cleared")
    
    def get_available_providers(self) -> List[str]:
        """Get list of available providers"""
        return [provider.config.name for provider in self.providers]

# Convenience function for easy usage
async def generate_with_fallback(prompt: str, model: str = None, **kwargs) -> LLMResponse:
    """Generate response using the modular LLM client with fallback"""
    client = ModularLLMClient()
    return await client.generate(prompt, model, **kwargs)

# Example usage
if __name__ == "__main__":
    async def test_llm_client():
        client = ModularLLMClient()
        
        prompt = "Gere um email personalizado para um restaurante que precisa melhorar seu site."
        
        print("Testing LLM client with fallback...")
        response = await client.generate(prompt)
        
        print(f"Provider: {response.provider}")
        print(f"Model: {response.model}")
        print(f"Success: {response.success}")
        print(f"Content: {response.content[:200]}...")
        
        if response.latency:
            print(f"Latency: {response.latency:.2f}s")
        
        print("\nStats:")
        print(json.dumps(client.get_stats(), indent=2))
    
    asyncio.run(test_llm_client()) 