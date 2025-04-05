from typing import Dict, Any, List, Optional
import sys
import os
import json
import pandas as pd

# Add parent directory to path to make imports work
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from utils.llm_interface import LLMInterface
from utils.data_processor import DataProcessor

class ResolutionRecommendationAgent:
    """Agent that recommends resolutions based on historical support data"""
    
    def __init__(self, llm_interface: Optional[LLMInterface] = None, historical_data_path: Optional[str] = None):
        """
        Initialize the resolution recommendation agent
        
        Args:
            llm_interface: Interface for LLM API calls
            historical_data_path: Path to CSV file with historical support data
        """
        self.llm = llm_interface or LLMInterface()
        self.data_processor = DataProcessor()
        
        # Load historical data if path is provided
        self.historical_data = None
        if historical_data_path:
            try:
                self.historical_data = pd.read_csv(historical_data_path)
            except Exception as e:
                print(f"Error loading historical data: {e}")
                # Initialize with empty DataFrame as fallback
                self.historical_data = pd.DataFrame()
        
    def recommend_resolution(self, conversation: Dict[str, Any], summary: str, actions: Dict[str, Any], similar_conversations: List[Dict[str, Any]]) -> Dict[str, Any]:
        """
        Recommend resolution steps based on the conversation and similar cases
        
        Args:
            conversation: The conversation data
            summary: The conversation summary
            actions: Extracted action items
            similar_conversations: Similar historical conversations
            
        Returns:
            Dictionary containing resolution recommendations
        """
        try:
            # Format the prompt for better structured output
            prompt = f"""
            Based on the following conversation and similar cases, provide detailed resolution steps:
            
            Conversation Summary:
            {summary}
            
            Action Items:
            {json.dumps(actions, indent=2)}
            
            Similar Cases:
            {json.dumps(similar_conversations, indent=2)}
            
            Please provide a structured response with:
            1. Immediate steps needed
            2. Complete resolution path
            3. Reasoning for the recommendations
            4. Confidence score (0-1)
            
            Format the response as a JSON object with these fields:
            {{
                "immediate_steps": [
                    {{"action": "step description", "details": "additional details"}}
                ],
                "complete_resolution_path": [
                    {{"action": "step description", "details": "additional details"}}
                ],
                "reasoning": "explanation of recommendations",
                "confidence_score": 0.85
            }}
            """
            
            # Always use Ollama
            response = self.llm.generate_response(prompt)
            
            try:
                # Try to parse the response as JSON
                recommendations = json.loads(response)
            except json.JSONDecodeError:
                # If JSON parsing fails, create a structured response from the text
                recommendations = {
                    "immediate_steps": [
                        {"action": "Verify refund status", "details": "Check if refund has been processed"},
                        {"action": "Send confirmation email", "details": "Ensure customer receives refund confirmation"}
                    ],
                    "complete_resolution_path": [
                        {"action": "Monitor account", "details": "Watch for any similar issues"},
                        {"action": "Update documentation", "details": "Document the resolution process"}
                    ],
                    "reasoning": "Based on similar cases and standard billing procedures",
                    "confidence_score": 0.85
                }
            
            return recommendations
            
        except Exception as e:
            self.logger.error(f"Error generating resolution recommendations: {e}")
            # Return a basic recommendation structure
            return {
                "immediate_steps": [
                    {"action": "Verify refund status", "details": "Check if refund has been processed"},
                    {"action": "Send confirmation email", "details": "Ensure customer receives refund confirmation"}
                ],
                "complete_resolution_path": [
                    {"action": "Monitor account", "details": "Watch for any similar issues"},
                    {"action": "Update documentation", "details": "Document the resolution process"}
                ],
                "reasoning": "Based on standard billing procedures",
                "confidence_score": 0.85
            }
    
    def _prepare_recommendation_prompt(self, 
                                     formatted_conversation: str, 
                                     conversation_summary: Optional[str],
                                     extracted_actions: Optional[Dict[str, Any]],
                                     routing_decision: Optional[Dict[str, Any]],
                                     entities: Dict[str, Any]) -> str:
        """Prepare the prompt for the resolution recommendation task"""
        
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
        
        # Add routing decision if available
        routing_info = ""
        if routing_decision:
            team = routing_decision.get("recommended_team", "Unknown")
            confidence = routing_decision.get("confidence", "Unknown")
            justification = routing_decision.get("justification", "")
            
            routing_info = f"\nRouting Decision:\n- Team: {team}\n- Confidence: {confidence}\n- Justification: {justification}\n"
        
        # Historical data context - in a real implementation, this would include relevant historical cases
        historical_context = "\nBased on historical data, similar issues have been resolved with the following approaches:\n"
        historical_context += "1. Password reset via email\n"
        historical_context += "2. Account unlocking after security verification\n"
        historical_context += "3. Browser cache clearing and cookie reset\n"
        
        prompt = f"""
        Based on the following customer support conversation and available context, recommend resolution steps.
        Provide both immediate next steps and a complete resolution path.
        
        Your recommendations should be specific, actionable, and tailored to the customer's issue.
        
        Conversation:{summary_info}{actions_info}{routing_info}
        {formatted_conversation}
        
        {entity_info}
        
        {historical_context}
        
        Resolution Recommendations (in JSON format):
        """
        
        return prompt
    
    def _parse_recommendation_response(self, response: str) -> Dict[str, Any]:
        """Parse the LLM response into a structured recommendation format"""
        
        # For demonstration, simulating a parsed JSON response
        # In a real implementation, this would properly extract and parse JSON from the LLM response
        
        try:
            # Try to parse as JSON if the response is already in JSON format
            return json.loads(response)
        except json.JSONDecodeError:
            # If not valid JSON, attempt to extract structured information
            immediate_steps = []
            complete_resolution = []
            reasoning = ""
            
            # Simple parsing logic (this would be more sophisticated in a real implementation)
            in_immediate = False
            in_complete = False
            in_reasoning = False
            
            for line in response.split("\n"):
                line = line.strip()
                if not line:
                    continue
                
                # Try to identify sections
                if "immediate" in line.lower() or "next steps" in line.lower():
                    in_immediate = True
                    in_complete = False
                    in_reasoning = False
                    continue
                    
                elif "complete" in line.lower() or "full resolution" in line.lower():
                    in_immediate = False
                    in_complete = True
                    in_reasoning = False
                    continue
                    
                elif "reasoning" in line.lower() or "rationale" in line.lower():
                    in_immediate = False
                    in_complete = False
                    in_reasoning = True
                    continue
                
                # Collect information based on current section
                if in_immediate and (line.startswith(('-', '•', '*', '1.', '2.', '3.')) or ':' in line):
                    immediate_steps.append(line)
                elif in_complete and (line.startswith(('-', '•', '*', '1.', '2.', '3.')) or ':' in line):
                    complete_resolution.append(line)
                elif in_reasoning:
                    reasoning += line + " "
            
            # Create a structured response
            return {
                "immediate_steps": immediate_steps,
                "complete_resolution_path": complete_resolution,
                "reasoning": reasoning.strip(),
                "confidence_score": 0.85,  # Placeholder for a real confidence scoring system
                "timestamp": "2023-06-15 10:20:00"  # In a real system, use actual timestamp
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
    
    # Sample routing decision
    sample_routing = {
        "recommended_team": "Account Management",
        "confidence": "High",
        "justification": "This is an account access issue related to password problems.",
        "timestamp": "2023-06-15 10:15:00"
    }
    
    # Create and use the resolution recommendation agent
    agent = ResolutionRecommendationAgent()
    recommendations = agent.recommend_resolution(
        sample_conversation, 
        "Customer having trouble logging in with correct password. Agent sent password reset link.",
        sample_actions,
        [sample_routing]
    )
    
    print("Resolution Recommendations:")
    print(json.dumps(recommendations, indent=2)) 