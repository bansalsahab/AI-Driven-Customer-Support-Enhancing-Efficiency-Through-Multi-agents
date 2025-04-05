from typing import Dict, Any, List, Optional
import sys
import os
import json

# Add parent directory to path to make imports work
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from utils.llm_interface import LLMInterface
from utils.data_processor import DataProcessor

class ActionExtractionAgent:
    """Agent that identifies and extracts key action items from conversations"""
    
    def __init__(self, llm_interface: Optional[LLMInterface] = None):
        """
        Initialize the action extraction agent
        
        Args:
            llm_interface: Interface for LLM API calls
        """
        self.llm = llm_interface or LLMInterface()
        self.data_processor = DataProcessor()
        
    def extract_actions(self, conversation: Dict[str, Any], conversation_summary: Optional[str] = None) -> Dict[str, Any]:
        """
        Extract action items from a customer support conversation
        
        Args:
            conversation: The conversation to analyze
            conversation_summary: Optional pre-generated summary of the conversation
            
        Returns:
            Dictionary with extracted action items
        """
        # Format the conversation for action extraction
        formatted_conversation = self.data_processor.format_conversation_for_summarization(conversation)
        
        # Extract entities to provide context
        entities = self.data_processor.extract_entities(formatted_conversation)
        
        # Prepare the prompt for the LLM
        prompt = self._prepare_action_extraction_prompt(
            formatted_conversation, 
            conversation_summary,
            entities
        )
        
        # Generate the action extraction response
        response = self.llm.generate_response(
            prompt=prompt,
            temperature=0.2,  # Lower temperature for more consistent extraction
            max_tokens=300,   # Provide enough space for detailed actions
        )
        
        # Parse the response into a structured format
        return self._parse_action_response(response)
    
    def _prepare_action_extraction_prompt(self, 
                                        formatted_conversation: str, 
                                        conversation_summary: Optional[str],
                                        entities: Dict[str, Any]) -> str:
        """Prepare the prompt for the action extraction task"""
        
        entity_info = ""
        if entities:
            products = ", ".join(entities.get("products", []))
            issues = ", ".join(entities.get("issues", []))
            sentiment = entities.get("customer_sentiment", "neutral")
            
            entity_info = f"""
            Products mentioned: {products if products else "None"}
            Issues mentioned: {issues if issues else "None"}
            Customer sentiment: {sentiment}
            """
        
        summary_info = f"\nConversation Summary: {conversation_summary}\n" if conversation_summary else ""
        
        prompt = f"""
        Analyze the following customer support conversation and extract all action items that need to be taken.
        These can include:
        - Escalations needed (and to which team/department)
        - Follow-ups required (with timelines if specified)
        - Information that needs to be provided to the customer
        - Technical actions needed to resolve the issue
        - Documentation or records that need to be updated
        
        Format your response as a structured list of action items with priorities (High/Medium/Low).
        
        Conversation:{summary_info}
        {formatted_conversation}
        
        {entity_info}
        
        Action Items (in JSON format):
        """
        
        return prompt
    
    def _parse_action_response(self, response: str) -> Dict[str, Any]:
        """Parse the LLM response into a structured action items format"""
        
        # For demonstration, simulating a parsed JSON response
        # In a real implementation, this would properly extract and parse JSON from the LLM response
        
        try:
            # Try to parse as JSON if the response is already in JSON format
            return json.loads(response)
        except json.JSONDecodeError:
            # If not valid JSON, attempt to extract structured information
            actions = []
            priorities = []
            
            for line in response.split('\n'):
                line = line.strip()
                if not line:
                    continue
                    
                # Check if line contains an action item (simplified parsing)
                if line.startswith(('-', '•', '*', '1.', '2.', '3.')) or 'action' in line.lower():
                    actions.append(line)
                    
                    # Try to determine priority
                    if 'high' in line.lower():
                        priorities.append('High')
                    elif 'medium' in line.lower():
                        priorities.append('Medium')
                    else:
                        priorities.append('Low')
            
            # Create structured response
            structured_actions = []
            for i, action in enumerate(actions):
                structured_actions.append({
                    "action": action,
                    "priority": priorities[i] if i < len(priorities) else "Medium",
                    "status": "Pending"
                })
            
            return {
                "action_items": structured_actions,
                "total_actions": len(structured_actions)
            }


# Example usage
if __name__ == "__main__":
    # Sample conversation (reused from SummarizationAgent)
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
    
    # Create and use the action extraction agent
    agent = ActionExtractionAgent()
    actions = agent.extract_actions(sample_conversation)
    
    print("Extracted Actions:")
    print(json.dumps(actions, indent=2)) 