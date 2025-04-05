import json
from typing import Dict, List, Any, Optional
import pandas as pd
import nltk
from nltk.tokenize import sent_tokenize

# Download NLTK resources if not already present
try:
    nltk.data.find('tokenizers/punkt')
except LookupError:
    nltk.download('punkt')

class DataProcessor:
    """Utility for processing and formatting customer support conversations"""
    
    @staticmethod
    def load_conversation(file_path: str) -> Dict[str, Any]:
        """Load conversation from JSON file"""
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                return json.load(f)
        except Exception as e:
            print(f"Error loading conversation from {file_path}: {e}")
            return {}
    
    @staticmethod
    def load_historical_data(file_path: str) -> pd.DataFrame:
        """Load historical support data from CSV file"""
        try:
            return pd.read_csv(file_path)
        except Exception as e:
            print(f"Error loading historical data from {file_path}: {e}")
            return pd.DataFrame()
    
    @staticmethod
    def format_conversation_for_summarization(conversation: Dict[str, Any]) -> str:
        """Format conversation for summarization"""
        formatted_text = ""
        
        if 'messages' in conversation:
            for msg in conversation['messages']:
                sender = msg.get('sender', 'Unknown')
                content = msg.get('content', '')
                time = msg.get('timestamp', '')
                
                formatted_text += f"{sender} ({time}): {content}\n\n"
        
        return formatted_text
    
    @staticmethod
    def extract_entities(text: str) -> Dict[str, Any]:
        """Extract key entities from text (products, issues, etc.)"""
        # Simplified entity extraction for demo purposes
        # In a real implementation, this would use NER models
        
        entities = {
            "products": [],
            "issues": [],
            "customer_sentiment": "neutral"
        }
        
        # Simple keyword matching for demonstration
        product_keywords = ["laptop", "phone", "tablet", "computer", "printer", "software"]
        issue_keywords = ["broken", "error", "not working", "issue", "problem", "bug", "crash"]
        
        text_lower = text.lower()
        
        for product in product_keywords:
            if product in text_lower:
                entities["products"].append(product)
                
        for issue in issue_keywords:
            if issue in text_lower:
                entities["issues"].append(issue)
        
        # Basic sentiment analysis
        positive_words = ["happy", "satisfied", "great", "excellent"]
        negative_words = ["unhappy", "disappointed", "frustrated", "angry"]
        
        positive_count = sum(1 for word in positive_words if word in text_lower)
        negative_count = sum(1 for word in negative_words if word in text_lower)
        
        if positive_count > negative_count:
            entities["customer_sentiment"] = "positive"
        elif negative_count > positive_count:
            entities["customer_sentiment"] = "negative"
        
        return entities
    
    @staticmethod
    def prepare_for_recommendation(conversation_summary: str, 
                                  extracted_actions: List[str],
                                  historical_data: pd.DataFrame) -> Dict[str, Any]:
        """Prepare data for resolution recommendation"""
        # This would typically involve feature extraction and preprocessing
        # Simplified for demo purposes
        
        return {
            "summary": conversation_summary,
            "actions": extracted_actions,
            "historical_data_sample": historical_data.sample(5).to_dict() if not historical_data.empty else {}
        }
    
    @staticmethod
    def segment_conversation(conversation: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Segment conversation into meaningful parts"""
        segments = []
        
        if 'messages' in conversation:
            current_segment = []
            for msg in conversation['messages']:
                current_segment.append(msg)
                
                # Segment when customer sends a message after agent response
                if (len(current_segment) >= 2 and 
                    current_segment[-1].get('sender') == 'Customer' and
                    current_segment[-2].get('sender') == 'Agent'):
                    segments.append(current_segment.copy())
                    current_segment = [msg]  # Start next segment with this message
            
            # Add any remaining messages as a segment
            if current_segment:
                segments.append(current_segment)
        
        return segments 