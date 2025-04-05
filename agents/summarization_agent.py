from typing import Dict, Any, List, Optional
import sys
import os

# Add parent directory to path to make imports work
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from utils.llm_interface import LLMInterface
from utils.data_processor import DataProcessor

class SummarizationAgent:
    """Agent that generates concise summaries of customer conversations"""
    
    def __init__(self, llm_interface: Optional[LLMInterface] = None):
        """
        Initialize the summarization agent
        
        Args:
            llm_interface: Interface for LLM API calls
        """
        self.llm = llm_interface or LLMInterface()
        self.data_processor = DataProcessor()
        
    def summarize(self, conversation: Dict[str, Any]) -> str:
        """
        Summarize a customer support conversation
        
        Args:
            conversation: The conversation to summarize
            
        Returns:
            A string summary of the conversation
        """
        # Format the conversation for summarization
        formatted_conversation = self.data_processor.format_conversation_for_summarization(conversation)
        
        # Prepare the prompt for the LLM
        prompt = self._prepare_summarization_prompt(formatted_conversation)
        
        # Generate the summary
        summary = self.llm.generate_response(
            prompt=prompt,
            temperature=0.3,  # Lower temperature for more factual and concise summary
            max_tokens=150,   # Limit the summary length
        )
        
        return summary
    
    def _prepare_summarization_prompt(self, formatted_conversation: str) -> str:
        """Prepare the prompt for the summarization task"""
        
        prompt = f"""
        Please provide a concise summary of the following customer support conversation.
        Focus on the main issue, any attempted solutions, and the final outcome or current status.
        Keep the summary brief and factual.
        
        Conversation:
        {formatted_conversation}
        
        Summary:
        """
        
        return prompt
    
    def batch_summarize(self, conversations: List[Dict[str, Any]]) -> List[str]:
        """
        Generate summaries for multiple conversations
        
        Args:
            conversations: List of conversations to summarize
            
        Returns:
            List of summaries
        """
        return [self.summarize(conv) for conv in conversations]


# Example usage
if __name__ == "__main__":
    # Sample conversation
    sample_conversation = {
        "conversation_id": "conv123",
        "messages": [
            {
                "sender": "Customer",
                "content": "Hi, I'm having trouble logging into my account. It keeps saying invalid password even though I'm sure it's correct.",
                "timestamp": "2023-06-15 10:05:32"
            },
            {
                "sender": "Agent",
                "content": "Hello! I'm sorry to hear you're having trouble. Let me help you with that. Can you tell me when you last successfully logged in?",
                "timestamp": "2023-06-15 10:06:45"
            },
            {
                "sender": "Customer",
                "content": "I think it was yesterday. I haven't changed my password recently.",
                "timestamp": "2023-06-15 10:07:23"
            },
            {
                "sender": "Agent",
                "content": "Thank you for that information. Let's try resetting your password. I'll send a password reset link to your registered email address. Is that okay?",
                "timestamp": "2023-06-15 10:08:10"
            },
            {
                "sender": "Customer",
                "content": "Yes, that would be great. Thank you!",
                "timestamp": "2023-06-15 10:08:45"
            },
            {
                "sender": "Agent",
                "content": "You're welcome! I've sent the password reset link. Please check your email and follow the instructions to reset your password. Let me know if you need any further assistance.",
                "timestamp": "2023-06-15 10:09:30"
            },
            {
                "sender": "Customer",
                "content": "Got it. I'll check now.",
                "timestamp": "2023-06-15 10:10:05"
            }
        ]
    }
    
    # Create and use the summarization agent
    agent = SummarizationAgent()
    summary = agent.summarize(sample_conversation)
    
    print("Conversation Summary:")
    print(summary) 