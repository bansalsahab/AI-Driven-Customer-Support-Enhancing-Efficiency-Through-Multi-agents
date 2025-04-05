from typing import Dict, Any, List, Optional
import sys
import os
import json

# Add parent directory to path to make imports work
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from utils.llm_interface import LLMInterface
from utils.data_processor import DataProcessor

class RoutingAgent:
    """Agent that decides which team or queue a ticket should be assigned to"""
    
    # Define the available teams/departments for routing
    AVAILABLE_TEAMS = [
        "Technical Support",
        "Billing Support",
        "Account Management",
        "Product Support",
        "Security Team",
        "Escalations Team",
        "General Support"
    ]
    
    def __init__(self, llm_interface: Optional[LLMInterface] = None):
        """
        Initialize the routing agent
        
        Args:
            llm_interface: Interface for LLM API calls
        """
        self.llm = llm_interface or LLMInterface()
        self.data_processor = DataProcessor()
        
    def route_ticket(self, 
                   conversation: Dict[str, Any], 
                   conversation_summary: Optional[str] = None,
                   extracted_actions: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """
        Determine the appropriate team for routing a ticket
        
        Args:
            conversation: The conversation to analyze
            conversation_summary: Optional pre-generated summary of the conversation
            extracted_actions: Optional pre-extracted action items
            
        Returns:
            Dictionary with routing decision and confidence score
        """
        # Format the conversation for routing
        formatted_conversation = self.data_processor.format_conversation_for_summarization(conversation)
        
        # Extract entities to provide context
        entities = self.data_processor.extract_entities(formatted_conversation)
        
        # Prepare the prompt for the LLM
        prompt = self._prepare_routing_prompt(
            formatted_conversation, 
            conversation_summary,
            extracted_actions,
            entities
        )
        
        # Generate the routing response
        response = self.llm.generate_response(
            prompt=prompt,
            temperature=0.2,  # Lower temperature for more consistent routing
            max_tokens=200,   # Provide enough space for detailed routing decision
        )
        
        # Parse the response into a structured format
        return self._parse_routing_response(response)
    
    def _prepare_routing_prompt(self, 
                              formatted_conversation: str, 
                              conversation_summary: Optional[str],
                              extracted_actions: Optional[Dict[str, Any]],
                              entities: Dict[str, Any]) -> str:
        """Prepare the prompt for the routing task"""
        
        # Create context from entities
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
        
        # Add conversation summary if available
        summary_info = f"\nConversation Summary: {conversation_summary}\n" if conversation_summary else ""
        
        # Add extracted actions if available
        actions_info = ""
        if extracted_actions and "action_items" in extracted_actions:
            actions_list = "\n".join([f"- {item.get('action', '')}" 
                                     for item in extracted_actions.get("action_items", [])])
            actions_info = f"\nExtracted Actions:\n{actions_list}\n"
        
        # List available teams
        teams_list = "\n".join([f"- {team}" for team in self.AVAILABLE_TEAMS])
        
        prompt = f"""
        Based on the following customer support conversation, determine which team or department 
        this ticket should be routed to. Choose from the following teams:
        
        {teams_list}
        
        In your response, include:
        1. The recommended team
        2. A confidence level (High, Medium, or Low)
        3. A brief justification for your decision
        
        Conversation:{summary_info}{actions_info}
        {formatted_conversation}
        
        {entity_info}
        
        Routing Decision (in JSON format):
        """
        
        return prompt
    
    def _parse_routing_response(self, response: str) -> Dict[str, Any]:
        """Parse the LLM response into a structured routing decision format"""
        
        # For demonstration, simulating a parsed JSON response
        # In a real implementation, this would properly extract and parse JSON from the LLM response
        
        try:
            # Try to parse as JSON if the response is already in JSON format
            return json.loads(response)
        except json.JSONDecodeError:
            # If not valid JSON, attempt to extract structured information
            team = None
            confidence = "Medium"
            justification = ""
            
            for line in response.split("\n"):
                line = line.strip()
                if not line:
                    continue
                    
                # Extract team recommendation
                if any(team_name.lower() in line.lower() for team_name in self.AVAILABLE_TEAMS):
                    for team_name in self.AVAILABLE_TEAMS:
                        if team_name.lower() in line.lower():
                            team = team_name
                            break
                
                # Extract confidence level
                if "high" in line.lower() and "confidence" in line.lower():
                    confidence = "High"
                elif "medium" in line.lower() and "confidence" in line.lower():
                    confidence = "Medium"
                elif "low" in line.lower() and "confidence" in line.lower():
                    confidence = "Low"
                
                # Collect justification
                if "because" in line.lower() or "reason" in line.lower() or ":" in line:
                    justification += line + " "
            
            # Default to General Support if no team is detected
            if not team:
                team = "General Support"
                
            # Create structured response
            return {
                "recommended_team": team,
                "confidence": confidence,
                "justification": justification.strip(),
                "timestamp": "2023-06-15 10:15:00"  # In a real system, use actual timestamp
            }


# Example usage
if __name__ == "__main__":
    # Sample conversation (reused from previous agents)
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
    
    # Sample extracted actions
    sample_actions = {
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
    
    # Create and use the routing agent
    agent = RoutingAgent()
    routing_decision = agent.route_ticket(
        sample_conversation, 
        "Customer having trouble logging in with correct password. Agent sent password reset link.",
        sample_actions
    )
    
    print("Routing Decision:")
    print(json.dumps(routing_decision, indent=2)) 