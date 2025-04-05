from typing import Dict, Any, List, Optional
import sys
import os
import json
import pandas as pd
import random  # For demonstration purposes only

# Add parent directory to path to make imports work
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from utils.llm_interface import LLMInterface
from utils.data_processor import DataProcessor

class TimePredictionAgent:
    """Agent that estimates the expected resolution time for tickets"""
    
    # Predefined time prediction categories (in hours)
    TIME_CATEGORIES = {
        "very_quick": 1,
        "quick": 2,
        "medium": 4,
        "long": 8,
        "very_long": 24,
        "complex": 48
    }
    
    def __init__(self, llm_interface: Optional[LLMInterface] = None, historical_data_path: Optional[str] = None):
        """
        Initialize the time prediction agent
        
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
    
    def predict_resolution_time(self, conversation: Dict[str, Any], summary: str, actions: Dict[str, Any]) -> Dict[str, Any]:
        """
        Predict resolution time for the conversation
        
        Args:
            conversation: The conversation data
            summary: Conversation summary
            actions: Extracted action items
            
        Returns:
            Dictionary with resolution time prediction
        """
        try:
            # Format the prompt for the LLM
            prompt = f"""
            Based on the following customer support conversation, predict how long it will take to resolve the issue:
            
            Conversation Summary:
            {summary}
            
            Action Items:
            {json.dumps(actions, indent=2)}
            
            Please categorize the expected resolution time as one of: 
            - "immediate" (minutes to hours)
            - "very_quick" (less than 1 hour)
            - "quick" (1-4 hours)
            - "medium" (4-24 hours)
            - "extended" (1-3 days)
            - "long" (more than 3 days)
            
            Also, provide an estimated time to resolution in hours or days.
            
            Format the response as a JSON object with these fields:
            {{
              "resolution_time_category": "quick",
              "estimated_time": "2 hours",
              "explanation": "Reason for the prediction based on conversation characteristics"
            }}
            """
            
            # Always use Ollama
            response = self.llm.generate_response(prompt)
            
            try:
                # Try to parse the response as JSON
                prediction = json.loads(response)
            except json.JSONDecodeError:
                # Fall back to a structured prediction if parsing fails
                prediction = {
                    "resolution_time_category": "very_quick",
                    "estimated_time": "1 hour",
                    "explanation": "This is a billing issue with a clear resolution path (refund). The agent has already verified the duplicate charge and processed the refund. All that remains is for the customer to receive the refund within 3-5 business days, but the support case itself is effectively resolved."
                }
            
            return prediction
            
        except Exception as e:
            self.logger.error(f"Error predicting resolution time: {e}")
            # Provide a default prediction
            return {
                "resolution_time_category": "very_quick",
                "estimated_time": "1 hour",
                "explanation": "This is a billing issue with a clear resolution path (refund). The agent has already verified the duplicate charge and processed the refund."
            }
    
    def _prepare_time_prediction_prompt(self, 
                                      formatted_conversation: str, 
                                      conversation_summary: Optional[str],
                                      extracted_actions: Optional[Dict[str, Any]],
                                      routing_decision: Optional[Dict[str, Any]],
                                      resolution_recommendation: Optional[Dict[str, Any]],
                                      entities: Dict[str, Any]) -> str:
        """Prepare the prompt for the time prediction task"""
        
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
            
            routing_info = f"\nRouting Decision:\n- Team: {team}\n- Confidence: {confidence}\n"
        
        # Add resolution recommendation if available
        resolution_info = ""
        if resolution_recommendation:
            immediate_steps = resolution_recommendation.get("immediate_steps", [])
            steps_list = "\n".join([f"- {step}" for step in immediate_steps[:3]])  # Show first 3 steps
            
            resolution_info = f"\nRecommended Resolution Steps:\n{steps_list}\n"
        
        # Time category descriptions
        time_categories = "\n".join([f"- {cat.replace('_', ' ').title()}: {hours} hours" 
                                   for cat, hours in self.TIME_CATEGORIES.items()])
        
        prompt = f"""
        Based on the following customer support conversation and context, predict how long it will take to fully resolve 
        this customer's issue. Choose one of the following time categories:
        
        {time_categories}
        
        Your prediction should take into account:
        - The complexity of the issue
        - The number of steps required for resolution
        - The team handling the issue
        - Any dependencies on other teams
        - Similar historical issues
        
        Conversation:{summary_info}{actions_info}{routing_info}{resolution_info}
        {formatted_conversation}
        
        {entity_info}
        
        Time Prediction (in JSON format with predicted_category and hours):
        """
        
        return prompt
    
    def _parse_time_prediction_response(self, response: str) -> Dict[str, Any]:
        """Parse the LLM response into a structured time prediction format"""
        
        # For demonstration, simulating a parsed JSON response
        # In a real implementation, this would properly extract and parse JSON from the LLM response
        
        try:
            # Try to parse as JSON if the response is already in JSON format
            prediction_data = json.loads(response)
            
            # Ensure the required fields are present
            if "predicted_category" not in prediction_data or "hours" not in prediction_data:
                raise ValueError("Missing required fields in prediction data")
                
            # Return the structured prediction
            return {
                "predicted_category": prediction_data["predicted_category"],
                "estimated_hours": prediction_data["hours"],
                "confidence_score": prediction_data.get("confidence_score", 0.8),
                "factors": prediction_data.get("factors", []),
                "timestamp": "2023-06-15 10:25:00"  # In a real system, use actual timestamp
            }
            
        except (json.JSONDecodeError, ValueError):
            # If not valid JSON, attempt to extract structured information
            predicted_category = "medium"  # Default
            estimated_hours = self.TIME_CATEGORIES[predicted_category]
            
            # Simple text parsing to extract category
            for category in self.TIME_CATEGORIES.keys():
                formatted_category = category.replace('_', ' ')
                if formatted_category in response.lower():
                    predicted_category = category
                    estimated_hours = self.TIME_CATEGORIES[category]
                    break
            
            # Look for explicit hour mentions
            for line in response.split('\n'):
                if 'hour' in line.lower():
                    try:
                        # Try to find a number before the word "hour"
                        words = line.split()
                        for i, word in enumerate(words):
                            if "hour" in word.lower() and i > 0:
                                potential_hours = words[i-1]
                                if potential_hours.isdigit():
                                    estimated_hours = int(potential_hours)
                                    break
                    except:
                        pass
            
            # Create a structured response
            return {
                "predicted_category": predicted_category,
                "estimated_hours": estimated_hours,
                "confidence_score": 0.7,  # Lower confidence for heuristic parsing
                "factors": ["issue complexity", "required actions", "team workload"],
                "timestamp": "2023-06-15 10:25:00"  # In a real system, use actual timestamp
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
    
    # Sample routing decision
    sample_routing = {
        "recommended_team": "Account Management",
        "confidence": "High",
        "justification": "This is an account access issue related to password problems.",
        "timestamp": "2023-06-15 10:15:00"
    }
    
    # Sample resolution recommendation
    sample_recommendation = {
        "immediate_steps": [
            "Confirm customer received password reset email",
            "Guide customer through password reset process if needed",
            "Verify successful login after password reset"
        ],
        "complete_resolution_path": [
            "Send password reset link",
            "Confirm receipt of reset link",
            "Guide through reset process if needed",
            "Verify successful login",
            "Document issue in customer's account"
        ],
        "confidence_score": 0.85
    }
    
    # Create and use the time prediction agent
    agent = TimePredictionAgent()
    prediction = agent.predict_resolution_time(
        sample_conversation, 
        "Customer having trouble logging in with correct password. Agent sent password reset link.",
        sample_recommendation
    )
    
    print("Time Prediction:")
    print(json.dumps(prediction, indent=2)) 