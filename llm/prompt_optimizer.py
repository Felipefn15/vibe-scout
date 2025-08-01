#!/usr/bin/env python3
"""
Prompt Optimizer for LLM Integration
Optimizes prompts for better scraping results and efficiency
"""

import json
import logging
import time
from typing import Dict, List, Optional, Any
from dataclasses import dataclass
from llm.llm_client import ModularLLMClient, LLMResponse

logger = logging.getLogger(__name__)

@dataclass
class OptimizedPrompt:
    """Optimized prompt with metadata"""
    prompt: str
    context: Dict
    expected_tokens: int
    success_rate: float
    avg_response_time: float
    optimization_level: str
    last_used: float
    usage_count: int

class PromptOptimizer:
    """Optimizes prompts for LLM-based scraping"""
    
    def __init__(self, llm_providers: List[str] = None):
        """
        Initialize prompt optimizer
        
        Args:
            llm_providers: List of LLM providers to use
        """
        self.llm_client = ModularLLMClient(llm_providers or ['Groq'])
        self.prompt_cache = {}
        self.optimization_history = []
        
        # Performance tracking
        self.stats = {
            'prompts_optimized': 0,
            'tokens_saved': 0,
            'time_saved': 0,
            'success_rate_improvement': 0
        }
    
    async def optimize_scraping_prompt(self, base_prompt: str, context: Dict, 
                                     target_tokens: int = 300) -> OptimizedPrompt:
        """
        Optimize a scraping prompt for better results
        
        Args:
            base_prompt: Original prompt
            context: Context information
            target_tokens: Target token count
            
        Returns:
            Optimized prompt
        """
        try:
            logger.info(f"Optimizing prompt for {context.get('task_type', 'unknown')}")
            
            # Check cache first
            cache_key = self._generate_cache_key(base_prompt, context)
            if cache_key in self.prompt_cache:
                cached_prompt = self.prompt_cache[cache_key]
                if time.time() - cached_prompt.last_used < 3600:  # 1 hour cache
                    logger.info("Using cached optimized prompt")
                    return cached_prompt
            
            # Generate optimization suggestions
            optimization_suggestions = await self._generate_optimization_suggestions(
                base_prompt, context, target_tokens
            )
            
            # Apply optimizations
            optimized_prompt = await self._apply_optimizations(
                base_prompt, optimization_suggestions, context
            )
            
            # Test the optimized prompt
            test_results = await self._test_prompt_effectiveness(optimized_prompt, context)
            
            # Create optimized prompt object
            optimized = OptimizedPrompt(
                prompt=optimized_prompt,
                context=context,
                expected_tokens=test_results.get('expected_tokens', target_tokens),
                success_rate=test_results.get('success_rate', 0.8),
                avg_response_time=test_results.get('avg_response_time', 1.0),
                optimization_level=test_results.get('optimization_level', 'medium'),
                last_used=time.time(),
                usage_count=1
            )
            
            # Cache the result
            self.prompt_cache[cache_key] = optimized
            
            # Update statistics
            self.stats['prompts_optimized'] += 1
            self.stats['tokens_saved'] += max(0, len(base_prompt.split()) - len(optimized_prompt.split()))
            
            logger.info(f"Prompt optimized: {test_results.get('optimization_level', 'medium')} level")
            return optimized
            
        except Exception as e:
            logger.error(f"Error optimizing prompt: {e}")
            return OptimizedPrompt(
                prompt=base_prompt,
                context=context,
                expected_tokens=target_tokens,
                success_rate=0.5,
                avg_response_time=2.0,
                optimization_level='fallback',
                last_used=time.time(),
                usage_count=1
            )
    
    async def _generate_optimization_suggestions(self, prompt: str, context: Dict, 
                                               target_tokens: int) -> List[str]:
        """Generate optimization suggestions using LLM"""
        try:
            optimization_prompt = f"""
            Analyze and suggest optimizations for this scraping prompt:
            
            Original Prompt:
            {prompt}
            
            Context:
            {json.dumps(context, indent=2)}
            
            Target Tokens: {target_tokens}
            
            Suggest specific optimizations to:
            1. Reduce token count while maintaining effectiveness
            2. Improve clarity and precision
            3. Increase success rate
            4. Speed up response time
            
            Return suggestions as a JSON array:
            ["suggestion1", "suggestion2", "suggestion3"]
            """
            
            response = await self.llm_client.generate(
                optimization_prompt,
                max_tokens=400,
                temperature=0.3
            )
            
            if response.success:
                try:
                    suggestions = json.loads(response.content)
                    return suggestions
                except json.JSONDecodeError:
                    logger.warning("Failed to parse optimization suggestions")
            
            # Fallback suggestions
            return self._generate_fallback_suggestions(prompt, target_tokens)
            
        except Exception as e:
            logger.error(f"Error generating optimization suggestions: {e}")
            return self._generate_fallback_suggestions(prompt, target_tokens)
    
    async def _apply_optimizations(self, prompt: str, suggestions: List[str], 
                                 context: Dict) -> str:
        """Apply optimization suggestions to the prompt"""
        try:
            apply_prompt = f"""
            Apply these optimizations to the original prompt:
            
            Original Prompt:
            {prompt}
            
            Optimizations to Apply:
            {json.dumps(suggestions, indent=2)}
            
            Context:
            {json.dumps(context, indent=2)}
            
            Return the optimized prompt that:
            1. Is more concise and clear
            2. Maintains all essential information
            3. Uses precise language
            4. Follows best practices for LLM prompts
            """
            
            response = await self.llm_client.generate(
                apply_prompt,
                max_tokens=600,
                temperature=0.2
            )
            
            if response.success:
                return response.content.strip()
            
            # Fallback optimization
            return self._apply_fallback_optimizations(prompt, suggestions)
            
        except Exception as e:
            logger.error(f"Error applying optimizations: {e}")
            return self._apply_fallback_optimizations(prompt, suggestions)
    
    async def _test_prompt_effectiveness(self, prompt: str, context: Dict) -> Dict:
        """Test the effectiveness of an optimized prompt"""
        try:
            # Create test scenarios
            test_scenarios = self._create_test_scenarios(context)
            
            success_count = 0
            total_response_time = 0
            total_tokens = 0
            
            for scenario in test_scenarios[:3]:  # Test with 3 scenarios
                start_time = time.time()
                
                test_prompt = f"{prompt}\n\nTest Scenario: {scenario}"
                
                response = await self.llm_client.generate(
                    test_prompt,
                    max_tokens=200,
                    temperature=0.3
                )
                
                response_time = time.time() - start_time
                total_response_time += response_time
                
                if response.success:
                    success_count += 1
                    total_tokens += response.tokens_used or 0
            
            avg_response_time = total_response_time / len(test_scenarios[:3])
            success_rate = success_count / len(test_scenarios[:3])
            avg_tokens = total_tokens / len(test_scenarios[:3])
            
            # Determine optimization level
            if success_rate >= 0.9 and avg_response_time < 1.0:
                optimization_level = 'high'
            elif success_rate >= 0.7 and avg_response_time < 2.0:
                optimization_level = 'medium'
            else:
                optimization_level = 'low'
            
            return {
                'success_rate': success_rate,
                'avg_response_time': avg_response_time,
                'expected_tokens': int(avg_tokens),
                'optimization_level': optimization_level
            }
            
        except Exception as e:
            logger.error(f"Error testing prompt effectiveness: {e}")
            return {
                'success_rate': 0.5,
                'avg_response_time': 2.0,
                'expected_tokens': 200,
                'optimization_level': 'fallback'
            }
    
    def _create_test_scenarios(self, context: Dict) -> List[str]:
        """Create test scenarios for prompt validation"""
        task_type = context.get('task_type', 'general')
        
        scenarios = {
            'lead_analysis': [
                "Restaurante italiano com site básico",
                "Consultório médico sem presença digital",
                "Loja de roupas com site desatualizado"
            ],
            'search_strategy': [
                "Encontrar restaurantes em Copacabana",
                "Buscar clínicas médicas em Botafogo",
                "Localizar lojas de roupas no Centro"
            ],
            'content_filtering': [
                "Filtrar leads de alta qualidade",
                "Identificar empresas com problemas web",
                "Priorizar leads com potencial de conversão"
            ]
        }
        
        return scenarios.get(task_type, ["Teste geral de funcionalidade"])
    
    def _generate_cache_key(self, prompt: str, context: Dict) -> str:
        """Generate cache key for prompt"""
        import hashlib
        content = f"{prompt[:100]}_{json.dumps(context, sort_keys=True)}"
        return hashlib.md5(content.encode()).hexdigest()
    
    def _generate_fallback_suggestions(self, prompt: str, target_tokens: int) -> List[str]:
        """Generate fallback optimization suggestions"""
        suggestions = []
        
        # Basic optimizations
        if len(prompt.split()) > target_tokens:
            suggestions.append("Remove redundant words and phrases")
            suggestions.append("Use more concise language")
        
        if "please" in prompt.lower() or "kindly" in prompt.lower():
            suggestions.append("Remove polite words to save tokens")
        
        if prompt.count('"') > 4:
            suggestions.append("Reduce quotation marks usage")
        
        suggestions.append("Use bullet points instead of paragraphs")
        suggestions.append("Specify exact output format")
        
        return suggestions
    
    def _apply_fallback_optimizations(self, prompt: str, suggestions: List[str]) -> str:
        """Apply fallback optimizations"""
        optimized = prompt
        
        # Apply basic optimizations
        if "Remove redundant words" in str(suggestions):
            optimized = optimized.replace("please", "").replace("kindly", "")
            optimized = optimized.replace("  ", " ")
        
        if "Use bullet points" in str(suggestions):
            # Convert paragraphs to bullet points where appropriate
            lines = optimized.split('\n')
            optimized_lines = []
            for line in lines:
                if len(line) > 100 and line.strip():
                    optimized_lines.append(f"• {line.strip()}")
                else:
                    optimized_lines.append(line)
            optimized = '\n'.join(optimized_lines)
        
        return optimized.strip()
    
    def get_optimized_prompt(self, task_type: str, context: Dict) -> str:
        """Get optimized prompt for specific task type"""
        # Pre-optimized prompts for common tasks
        optimized_prompts = {
            'lead_analysis': """
            Analyze this business lead for {sector} sector:
            
            Lead: {lead_data}
            
            Provide JSON analysis:
            {{
                "intelligence_score": 0-100,
                "business_potential": "high/medium/low",
                "digital_maturity": "advanced/intermediate/basic",
                "pain_points": ["point1", "point2"],
                "opportunities": ["opp1", "opp2"],
                "recommended_services": ["service1", "service2"],
                "conversion_probability": 0-100,
                "priority_level": "high/medium/low"
            }}
            """,
            
            'search_strategy': """
            Generate search strategies for {sector} in {region}:
            
            Return JSON array:
            [
                {{
                    "source": "search_engine",
                    "keywords": ["keyword1", "keyword2"],
                    "filters": {{"location": "region"}},
                    "priority": 1-10,
                    "expected_quality": "high/medium/low"
                }}
            ]
            """,
            
            'content_filtering': """
            Filter these leads based on strategy:
            Strategy: {strategy}
            Leads: {leads_data}
            
            Return JSON array with high-quality leads only.
            Include leads that are:
            1. Relevant to target sector
            2. Have good business potential
            3. Match expected quality level
            """
        }
        
        base_prompt = optimized_prompts.get(task_type, "{prompt}")
        
        # Apply context
        try:
            return base_prompt.format(**context)
        except KeyError:
            return base_prompt
    
    def get_stats(self) -> Dict:
        """Get optimization statistics"""
        return self.stats.copy()
    
    def clear_cache(self):
        """Clear prompt cache"""
        self.prompt_cache.clear()
        logger.info("Prompt cache cleared")

# Convenience functions
async def optimize_prompt_for_scraping(base_prompt: str, task_type: str, 
                                     context: Dict) -> str:
    """Convenience function for prompt optimization"""
    optimizer = PromptOptimizer()
    optimized = await optimizer.optimize_scraping_prompt(base_prompt, context)
    return optimized.prompt

def get_optimized_prompt_template(task_type: str) -> str:
    """Get optimized prompt template for common tasks"""
    optimizer = PromptOptimizer()
    return optimizer.get_optimized_prompt(task_type, {})

if __name__ == "__main__":
    async def test_prompt_optimizer():
        """Test the prompt optimizer"""
        optimizer = PromptOptimizer()
        
        base_prompt = """
        Please analyze this business lead for the restaurant sector and provide a comprehensive analysis including intelligence score, business potential, digital maturity assessment, pain points identification, opportunities analysis, recommended services, conversion probability calculation, and priority level determination.
        """
        
        context = {
            'task_type': 'lead_analysis',
            'sector': 'restaurantes',
            'region': 'Rio de Janeiro'
        }
        
        optimized = await optimizer.optimize_scraping_prompt(base_prompt, context)
        print(f"Original: {len(base_prompt)} chars")
        print(f"Optimized: {len(optimized.prompt)} chars")
        print(f"Optimization level: {optimized.optimization_level}")
        print(f"Success rate: {optimized.success_rate:.2%}")
        
        print(f"\nOptimized prompt:\n{optimized.prompt}")
    
    import asyncio
    asyncio.run(test_prompt_optimizer()) 