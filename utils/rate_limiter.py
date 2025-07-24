import time
import logging
import random
from typing import Optional, Callable, Any
from functools import wraps
import os
from dotenv import load_dotenv

load_dotenv()

logger = logging.getLogger(__name__)

class RateLimiter:
    def __init__(self, max_requests: int = 50, time_window: int = 60, jitter: float = 0.1):
        """
        Initialize rate limiter
        
        Args:
            max_requests: Maximum requests per time window
            time_window: Time window in seconds
            jitter: Random jitter factor (0.0 to 1.0) to avoid thundering herd
        """
        self.max_requests = max_requests
        self.time_window = time_window
        self.jitter = jitter
        self.requests = []
        self.last_request_time = 0
        
        # Load environment-specific settings
        self.groq_rate_limit = int(os.getenv('GROQ_RATE_LIMIT', max_requests))
        self.groq_time_window = int(os.getenv('GROQ_TIME_WINDOW', time_window))
        
    def wait_if_needed(self):
        """Wait if rate limit would be exceeded"""
        current_time = time.time()
        
        # Clean old requests outside the time window
        self.requests = [req_time for req_time in self.requests 
                        if current_time - req_time < self.time_window]
        
        # Check if we're at the limit
        if len(self.requests) >= self.max_requests:
            # Calculate wait time
            oldest_request = min(self.requests)
            wait_time = self.time_window - (current_time - oldest_request)
            
            # Add jitter to avoid thundering herd
            jitter_amount = wait_time * self.jitter * random.random()
            total_wait = wait_time + jitter_amount
            
            logger.info(f"Rate limit reached. Waiting {total_wait:.2f} seconds...")
            time.sleep(total_wait)
            
            # Update current time after waiting
            current_time = time.time()
        
        # Record this request
        self.requests.append(current_time)
        self.last_request_time = current_time
    
    def wait(self):
        """Alias for wait_if_needed for backward compatibility"""
        return self.wait_if_needed()
    
    def exponential_backoff(self, attempt: int, base_delay: float = 1.0, max_delay: float = 60.0) -> float:
        """Calculate exponential backoff delay"""
        delay = min(base_delay * (2 ** attempt), max_delay)
        # Add jitter
        jitter = delay * self.jitter * random.random()
        return delay + jitter

def rate_limited(max_requests: int = 50, time_window: int = 60, retries: int = 3):
    """
    Decorator for rate limiting API calls with retry logic
    
    Args:
        max_requests: Maximum requests per time window
        time_window: Time window in seconds
        retries: Number of retries on failure
    """
    def decorator(func: Callable) -> Callable:
        limiter = RateLimiter(max_requests, time_window)
        
        @wraps(func)
        def wrapper(*args, **kwargs) -> Any:
            for attempt in range(retries + 1):
                try:
                    # Wait if rate limit would be exceeded
                    limiter.wait_if_needed()
                    
                    # Make the API call
                    result = func(*args, **kwargs)
                    
                    # If successful, return immediately
                    return result
                    
                except Exception as e:
                    error_msg = str(e).lower()
                    
                    # Check if it's a rate limit error
                    if '429' in error_msg or 'rate limit' in error_msg or 'too many requests' in error_msg:
                        if attempt < retries:
                            # Calculate backoff delay
                            delay = limiter.exponential_backoff(attempt)
                            logger.warning(f"Rate limit hit (attempt {attempt + 1}/{retries + 1}). "
                                         f"Waiting {delay:.2f} seconds before retry...")
                            time.sleep(delay)
                            continue
                        else:
                            logger.error(f"Rate limit exceeded after {retries} retries")
                            raise
                    
                    # For other errors, log and retry with backoff
                    elif attempt < retries:
                        delay = limiter.exponential_backoff(attempt)
                        logger.warning(f"API call failed (attempt {attempt + 1}/{retries + 1}): {e}. "
                                     f"Retrying in {delay:.2f} seconds...")
                        time.sleep(delay)
                        continue
                    else:
                        logger.error(f"API call failed after {retries} retries: {e}")
                        raise
            
            # This should never be reached
            raise Exception("Unexpected error in rate limiting wrapper")
        
        return wrapper
    return decorator

class GroqRateLimiter:
    """Specialized rate limiter for Groq API"""
    
    def __init__(self):
        # Groq free tier limits: 50 requests per minute
        self.rate_limiter = RateLimiter(
            max_requests=int(os.getenv('GROQ_RATE_LIMIT', 45)),  # Conservative limit
            time_window=int(os.getenv('GROQ_TIME_WINDOW', 60)),
            jitter=0.2
        )
    
    def call_with_retry(self, api_call: Callable, *args, **kwargs) -> Any:
        """Make API call with rate limiting and retry logic"""
        
        @rate_limited(max_requests=45, time_window=60, retries=3)
        def _make_call():
            return api_call(*args, **kwargs)
        
        return _make_call()
    
    def wait_between_batches(self, batch_size: int = 10):
        """Wait between batches of API calls"""
        if batch_size >= 10:
            wait_time = 5 + random.uniform(0, 2)  # 5-7 seconds
            logger.info(f"Waiting {wait_time:.2f} seconds between batches...")
            time.sleep(wait_time)

# Global instance for easy access
groq_limiter = GroqRateLimiter() 