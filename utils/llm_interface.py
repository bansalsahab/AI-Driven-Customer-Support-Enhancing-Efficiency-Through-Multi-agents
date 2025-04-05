import os
import requests
import time
import logging
from typing import Dict, Any, Optional, List

class LLMInterface:
    """Interface for API calls to on-premises LLM (e.g., via Ollama)"""
    
    def __init__(self, base_url: str = "http://localhost:11434/api", 
                 model: str = "llama2", 
                 max_retries: int = 3, 
                 retry_delay: float = 1.0,
                 simulate: bool = False):
        """
        Initialize the LLM interface
        
        Args:
            base_url: Base URL for the LLM API
            model: Default model to use
            max_retries: Maximum number of retries for failed API calls
            retry_delay: Delay between retries in seconds
            simulate: Whether to simulate responses (for testing without LLM)
        """
        self.base_url = base_url
        self.default_model = model
        self.max_retries = max_retries
        self.retry_delay = retry_delay
        self.simulate = simulate
        
        # Set up logging
        logging.basicConfig(level=logging.INFO, 
                            format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
        self.logger = logging.getLogger("LLMInterface")
        
    def generate_response(self, prompt: str, model: Optional[str] = None, temperature: float = 0.7, max_tokens: int = 1000, use_openrouter: bool = False) -> str:
        """
        Generate a response using the configured LLM
        
        Args:
            prompt: The input prompt
            model: The model to use (defaults to self.default_model)
            temperature: Temperature for response generation
            max_tokens: Maximum tokens to generate
            use_openrouter: Ignored parameter (kept for backwards compatibility)
            
        Returns:
            The generated response
        """
        if self.simulate:
            self.logger.info("Simulating LLM response")
            return self._simulate_response(prompt)
        
        model = model or self.default_model
        self.logger.info(f"Generating response using model: {model}")
        
        for attempt in range(self.max_retries):
            try:
                # Increase timeout to 60 seconds
                response = requests.post(
                    f"{self.base_url}/generate",
                    json={
                        "model": model,
                        "prompt": prompt,
                        "temperature": temperature,
                        "max_tokens": max_tokens,
                        "stream": False
                    },
                    timeout=60  # Increased timeout
                )
                
                # Check if request was successful
                response.raise_for_status()
                
                # Parse response
                result = response.json()
                self.logger.debug(f"LLM response received: {result}")
                
                return result.get("response", "")
                
            except requests.exceptions.Timeout:
                self.logger.warning(f"Request timed out (attempt {attempt+1}/{self.max_retries})")
                if attempt < self.max_retries - 1:
                    self.logger.info(f"Retrying in {self.retry_delay} seconds...")
                    time.sleep(self.retry_delay)
                else:
                    self.logger.error("All retry attempts timed out")
                    return self._simulate_response(prompt)
                    
            except requests.exceptions.RequestException as e:
                self.logger.warning(f"API call failed (attempt {attempt+1}/{self.max_retries}): {e}")
                
                if attempt < self.max_retries - 1:
                    self.logger.info(f"Retrying in {self.retry_delay} seconds...")
                    time.sleep(self.retry_delay)
                else:
                    self.logger.error(f"All retry attempts failed: {e}")
                    # Fall back to simulated response if all retries fail
                    self.logger.info("Falling back to simulated response")
                    return self._simulate_response(prompt)
        
        # This should never be reached due to the else clause in the last iteration
        return self._simulate_response(prompt)
    
    def get_embeddings(self, text: str, model: Optional[str] = None, use_openrouter: bool = False) -> List[float]:
        """
        Get embeddings for the given text using Ollama
        
        Args:
            text: The text to embed
            model: The embedding model to use (defaults to self.default_model)
            use_openrouter: Ignored parameter (kept for backwards compatibility)
            
        Returns:
            List of embedding values
        """
        if self.simulate:
            self.logger.info("Simulating embeddings")
            # Return a small random embedding vector for simulation
            import random
            return [random.random() for _ in range(10)]
        
        # Try Ollama embeddings
        model = model or self.default_model
        self.logger.info(f"Generating embeddings using model: {model}")
        
        for attempt in range(self.max_retries):
            try:
                # The correct endpoint is /api/embeddings in newer Ollama versions
                url = f"{self.base_url}/embeddings"
                
                self.logger.debug(f"Making embeddings request to: {url}")
                response = requests.post(
                    url,
                    json={
                        "model": model,
                        "prompt": text
                    },
                    timeout=30
                )
                
                # Check if request was successful
                response.raise_for_status()
                
                # Parse response
                result = response.json()
                self.logger.debug("Embedding response received")
                
                embeddings = result.get("embedding", [])
                if embeddings:
                    return embeddings
                else:
                    self.logger.warning("Empty embeddings received from Ollama API")
                    
            except requests.exceptions.RequestException as e:
                self.logger.warning(f"Ollama embeddings API call failed (attempt {attempt+1}/{self.max_retries}): {e}")
                
                if attempt < self.max_retries - 1:
                    self.logger.info(f"Retrying in {self.retry_delay} seconds...")
                    time.sleep(self.retry_delay)
                else:
                    self.logger.error(f"All Ollama embedding retry attempts failed: {e}")
                    # Return simulated embeddings if all else fails
                    self.logger.info("Generating simulated embeddings due to API failure")
                    import random
                    return [random.random() for _ in range(10)]
        
        # Fallback to simulated embeddings
        self.logger.info("Generating simulated embeddings as final fallback")
        import random
        return [random.random() for _ in range(10)]
    
    def _simulate_embeddings(self, text: str) -> List[float]:
        """
        Generate simulated embeddings for demo purposes
        
        Args:
            text: The text to embed
            
        Returns:
            Simulated embedding vector
        """
        import hashlib
        import random
        
        # Create a hash of the text for consistency
        hash_obj = hashlib.md5(text.encode())
        hash_hex = hash_obj.hexdigest()
        
        # Use the hash to seed the random generator
        random.seed(hash_hex)
        
        # Generate 10-dimensional embeddings vector
        embeddings = [random.random() for _ in range(10)]
        
        return embeddings
    
    def _simulate_response(self, prompt: str) -> str:
        """Simulate LLM response for demonstration purposes"""
        
        # Basic response templates based on prompt content
        if "summarize" in prompt.lower():
            return "This is a simulated summary of the conversation. The customer was experiencing login issues with their account. The agent sent a password reset link to the customer's email, and the customer confirmed they would check their email."
        
        elif "action" in prompt.lower() or "extract" in prompt.lower():
            return """
            {
                "action_items": [
                    {
                        "action": "Send password reset link to customer",
                        "priority": "High",
                        "status": "Completed"
                    },
                    {
                        "action": "Follow up with customer to confirm successful login",
                        "priority": "Medium",
                        "status": "Pending"
                    }
                ],
                "total_actions": 2
            }
            """
        
        elif "route" in prompt.lower() or "team" in prompt.lower():
            return """
            {
                "recommended_team": "Account Management",
                "confidence": "High",
                "justification": "This is an account access issue related to password problems.",
                "timestamp": "2023-06-15 10:15:00"
            }
            """
        
        elif "resolution" in prompt.lower() or "recommend" in prompt.lower():
            return """
            {
                "immediate_steps": [
                    {"action": "Verify refund status", "details": "Check if refund has been processed"},
                    {"action": "Send confirmation email", "details": "Ensure customer receives refund confirmation"}
                ],
                "complete_resolution_path": [
                    {"action": "Monitor account", "details": "Watch for any similar issues"},
                    {"action": "Update documentation", "details": "Document the resolution process"}
                ],
                "reasoning": "Password reset is the standard procedure for login issues when the customer cannot access their account.",
                "confidence_score": 0.85
            }
            """
        
        elif "time" in prompt.lower() or "predict" in prompt.lower():
            return """
            {
                "resolution_time_category": "quick",
                "estimated_time": "2 hours",
                "explanation": "Simple issue with standard resolution path."
            }
            """
        
        else:
            return "I'm not sure how to respond to that prompt."
            
    def batch_generate(self, prompts: List[str], **kwargs) -> List[str]:
        """Generate responses for multiple prompts"""
        return [self.generate_response(prompt, **kwargs) for prompt in prompts] 