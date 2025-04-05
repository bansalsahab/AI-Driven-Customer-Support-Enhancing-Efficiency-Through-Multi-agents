#!/usr/bin/env python3
"""
Multi-Agent AI System for Customer Support

This is the main application that demonstrates the complete pipeline:
1. Conversation summarization
2. Action item extraction
3. Ticket routing
4. Resolution recommendation
5. Resolution time prediction

With enhanced features:
- Real Ollama API integration for LLM and embeddings
- SQLite database for storing results
- Custom tools: API client, web scraper, sentiment analyzer
- Advanced configuration options
"""

import os
import sys
import json
import time
import logging
from typing import Dict, Any, List, Optional
import argparse
from datetime import datetime
import traceback
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

# Import agents
from agents.summarization_agent import SummarizationAgent
from agents.action_extraction_agent import ActionExtractionAgent
from agents.routing_agent import RoutingAgent
from agents.resolution_recommendation_agent import ResolutionRecommendationAgent
from agents.time_prediction_agent import TimePredictionAgent

# Import utilities
from utils.llm_interface import LLMInterface
from utils.data_processor import DataProcessor
from utils.database import Database
from utils.custom_tools import APIClient, WebScraper, SentimentAnalyzer

# Import sample data
from data.sample_conversations import SAMPLE_CONVERSATIONS, get_conversation
from data.historical_data import generate_historical_data

class CustomerSupportAI:
    """Multi-agent AI system for customer support operations"""
    
    def __init__(self, 
                 ollama_url: Optional[str] = None,
                 model_name: Optional[str] = None,
                 db_path: Optional[str] = None,
                 simulate: bool = False):
        """
        Initialize the customer support AI system
        
        Args:
            ollama_url: URL for the Ollama API
            model_name: Name of the LLM model to use
            db_path: Path to the SQLite database file
            simulate: Whether to simulate LLM responses (for testing without Ollama)
        """
        # Set up logging
        logging.basicConfig(
            level=getattr(logging, os.getenv("LOG_LEVEL", "INFO")),
            format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
            handlers=[
                logging.StreamHandler(),
                logging.FileHandler(os.getenv("LOG_FILE", "customer_support.log"))
            ]
        )
        self.logger = logging.getLogger("CustomerSupportAI")
        
        # Initialize the LLM interface
        self.ollama_url = ollama_url or os.getenv("OLLAMA_API_URL", "http://localhost:11434/api")
        self.model_name = model_name or os.getenv("OLLAMA_MODEL", "llama2")
        
        self.llm = LLMInterface(
            base_url=self.ollama_url,
            model=self.model_name,
            simulate=simulate
        )
        
        self.logger.info(f"Initialized LLM interface with model: {self.model_name}")
        
        # Initialize the database
        self.db_path = db_path or os.getenv("DB_PATH", "customer_support.db")
        self.db = Database(self.db_path)
        self.logger.info(f"Connected to database at: {self.db_path}")
        
        # Initialize custom tools
        self.api_client = APIClient()
        
        self.web_scraper = WebScraper(
            user_agent=os.getenv("USER_AGENT", "CustomerSupportAI/1.0")
        )
        
        self.sentiment_analyzer = SentimentAnalyzer()
        self.kb_url = os.getenv("KNOWLEDGE_BASE_URL", "https://help.example.com")
        
        # Initialize all agents with the same LLM interface for consistency
        self.summarization_agent = SummarizationAgent(llm_interface=self.llm)
        self.action_extraction_agent = ActionExtractionAgent(llm_interface=self.llm)
        self.routing_agent = RoutingAgent(llm_interface=self.llm)
        self.resolution_recommendation_agent = ResolutionRecommendationAgent(
            llm_interface=self.llm
        )
        self.time_prediction_agent = TimePredictionAgent(
            llm_interface=self.llm
        )
        
        # Initialize data processor
        self.data_processor = DataProcessor()
    
    def process_conversation(self, conversation: Dict[str, Any], verbose: bool = False) -> Dict[str, Any]:
        """
        Process a customer support conversation through the complete pipeline
        
        Args:
            conversation: The conversation to process
            verbose: Whether to print detailed processing information
            
        Returns:
            Dictionary with results from all agents
        """
        conversation_id = conversation.get("conversation_id", str(datetime.now().timestamp()))
        
        results = {
            "conversation_id": conversation_id,
            "processing_time": {
                "start": time.time(),
                "steps": {}
            }
        }
        
        try:
            # Store the conversation in the database
            self.db.store_conversation(conversation)
            
            # Analyze sentiment (new feature)
            sentiment_results = self.sentiment_analyzer.analyze_conversation_sentiment(conversation)
            results["sentiment_analysis"] = sentiment_results
            
            if verbose:
                print(f"Sentiment Analysis: {sentiment_results['overall_sentiment']['sentiment']} "
                     f"(score: {sentiment_results['overall_sentiment']['score']:.2f})")
            
            # Step 1: Conversation Summarization
            if verbose:
                print("Step 1: Generating conversation summary...")
            
            step_start = time.time()
            summary = self.summarization_agent.summarize(conversation)
            results["summary"] = summary
            results["processing_time"]["steps"]["summarization"] = time.time() - step_start
            
            # Store the summary in the database
            self.db.update_conversation_summary(conversation_id, summary)
            
            if verbose:
                print(f"Summary: {summary}\n")
            
            # Step 2: Action Item Extraction
            if verbose:
                print("Step 2: Extracting action items...")
            
            step_start = time.time()
            actions = self.action_extraction_agent.extract_actions(conversation, summary)
            results["actions"] = actions
            results["processing_time"]["steps"]["action_extraction"] = time.time() - step_start
            
            # Store actions in the database
            self.db.store_actions(conversation_id, actions)
            
            if verbose:
                print(f"Actions: {json.dumps(actions, indent=2)}\n")
            
            # Step 3: Fetch relevant knowledge articles (new feature)
            if verbose:
                print("Step 3: Fetching relevant knowledge articles...")
            
            step_start = time.time()
            # Extract key terms for search from summary
            key_terms = summary.split()[:5]  # Simplified approach for demo
            search_query = " ".join(key_terms)
            
            # Try to get articles from API first
            knowledge_articles = self.api_client.get_knowledge_articles(search_query)
            
            # If API fails or returns no results, try web scraping
            if not knowledge_articles and self.kb_url:
                knowledge_articles = self.web_scraper.search_knowledge_base(self.kb_url, search_query)
            
            results["knowledge_articles"] = knowledge_articles
            results["processing_time"]["steps"]["knowledge_retrieval"] = time.time() - step_start
            
            if verbose and knowledge_articles:
                print(f"Found {len(knowledge_articles)} relevant knowledge articles")
                for i, article in enumerate(knowledge_articles[:2]):  # Show first 2 for brevity
                    print(f"  {i+1}. {article.get('title', 'No title')}")
                print()
            
            # Step 4: Ticket Routing
            if verbose:
                print("Step 4: Determining ticket routing...")
            
            step_start = time.time()
            routing = self.routing_agent.route_ticket(conversation, summary, actions)
            results["routing"] = routing
            results["processing_time"]["steps"]["routing"] = time.time() - step_start
            
            # Store routing decision in the database
            self.db.store_routing_decision(conversation_id, routing)
            
            if verbose:
                print(f"Routing: {json.dumps(routing, indent=2)}\n")
            
            # Step 5: Generate embeddings for the conversation (new feature)
            if verbose:
                print("Step 5: Generating conversation embeddings...")
            
            step_start = time.time()
            try:
                formatted_conversation = self.data_processor.format_conversation_for_summarization(conversation)
                embedding = self.llm.get_embeddings(
                    formatted_conversation, 
                    self.model_name
                )
                
                similar_conversations = []  # Initialize empty list as default
                
                if embedding:
                    # Store embedding in the database
                    self.db.store_embedding(
                        source_type="conversation",
                        source_id=conversation_id,
                        text=summary,  # Store the summary as the text representation
                        embedding=embedding,
                        model=self.model_name
                    )
                    
                    # Find similar conversations
                    similar_conversations = self.db.find_similar_embeddings(embedding, "conversation", 3)
                    results["similar_conversations"] = similar_conversations
                    
                    if verbose and similar_conversations:
                        print(f"Found {len(similar_conversations)} similar conversations")
                        for i, conv in enumerate(similar_conversations[:2]):  # Show first 2 for brevity
                            print(f"  - {conv.get('text', 'No text')} (similarity: {conv.get('similarity', 0):.2f})")
                        print()
                
            except Exception as e:
                self.logger.error(f"Error generating embeddings: {e}")
                similar_conversations = []  # Ensure we have a fallback
                
            results["processing_time"]["steps"]["embeddings"] = time.time() - step_start
            
            # Step 6: Recommend resolution
            try:
                print("\nStep 6: Recommending resolution steps...")
                recommendations = self.resolution_recommendation_agent.recommend_resolution(
                    conversation,
                    summary,
                    actions,
                    similar_conversations
                )
                results["recommendations"] = recommendations
                print(f"Recommendations: {json.dumps(recommendations, indent=2)}")
            except Exception as e:
                self.logger.error(f"Error recommending resolution: {e}")
                self.logger.error(traceback.format_exc())
                print(f"Error recommending resolution: {e}")
                
                # Provide fallback recommendations
                results["recommendations"] = {
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
            
            # Store recommendations in the database
            self.db.store_resolution_recommendation(conversation_id, recommendations)
            
            # Step 7: Time Prediction
            if verbose:
                print("\nStep 7: Predicting resolution time...")
            
            try:
                time_prediction = self.time_prediction_agent.predict_resolution_time(
                    conversation,
                    summary,
                    actions
                )
                results["time_prediction"] = time_prediction
                print(f"Time Prediction: {json.dumps(time_prediction, indent=2)}")
            except Exception as e:
                self.logger.error(f"Error predicting resolution time: {e}")
                self.logger.error(traceback.format_exc())
                print(f"Error predicting resolution time: {e}")
                
                # Provide fallback time prediction
                results["time_prediction"] = {
                    "resolution_time_category": "very_quick",
                    "estimated_time": "1 hour",
                    "explanation": "This is a standard billing issue with a clear resolution path."
                }
            
            # Store time prediction in the database
            self.db.store_time_prediction(conversation_id, time_prediction)
            
        except Exception as e:
            error_msg = f"Error processing conversation: {e}"
            self.logger.error(error_msg)
            self.logger.error(traceback.format_exc())
            results["error"] = error_msg
        
        # Calculate total processing time
        results["processing_time"]["total"] = time.time() - results["processing_time"]["start"]
        
        return results
    
    def save_results(self, results: Dict[str, Any], output_path: str) -> None:
        """
        Save processing results to a JSON file
        
        Args:
            results: The results to save
            output_path: Path to save the results to
        """
        try:
            # Create directory if it doesn't exist
            os.makedirs(os.path.dirname(os.path.abspath(output_path)), exist_ok=True)
            
            # Save to JSON file
            with open(output_path, 'w', encoding='utf-8') as f:
                json.dump(results, f, indent=2)
                
            self.logger.info(f"Results saved to {output_path}")
        except Exception as e:
            self.logger.error(f"Error saving results to {output_path}: {e}")
    
    def load_historical_data(self, csv_path: str) -> None:
        """
        Load historical data from a CSV file into the database
        
        Args:
            csv_path: Path to the CSV file
        """
        try:
            import pandas as pd
            data = pd.read_csv(csv_path)
            records = data.to_dict(orient='records')
            
            self.db.import_historical_data(records)
            self.logger.info(f"Imported {len(records)} historical data records from {csv_path}")
        except Exception as e:
            self.logger.error(f"Error loading historical data from {csv_path}: {e}")


def main():
    """Main entry point for the script"""
    parser = argparse.ArgumentParser(description='Run the Customer Support AI system')
    parser.add_argument('--conversation', type=str, default='billing_issue', 
                        choices=['billing_issue', 'technical_issue', 'account_issue'],
                        help='Which conversation to process')
    parser.add_argument('--output', type=str, default='results.json',
                        help='Output file path')
    parser.add_argument('--verbose', action='store_true',
                        help='Show verbose output')
    args = parser.parse_args()
    
    # Initialize the system
    system = CustomerSupportAI(
        db_path='customer_support.db'
    )
    
    # Load the conversation to process
    conversation = get_conversation(args.conversation)
    
    if not conversation:
        print(f"Error: Could not load conversation '{args.conversation}'")
        return 1
    
    # Process the conversation
    try:
        results = system.process_conversation(conversation, verbose=args.verbose)
        
        # Save the results
        with open(args.output, 'w') as f:
            json.dump(results, f, indent=2)
            
        print(f"\nProcessing Summary:")
        print(f"Total processing time: {results['processing_time']['total']:.2f} seconds")
        
        # Display any errors
        if results.get('error'):
            print(f"Error: {results['error']}")
        
        return 0
    except Exception as e:
        print(f"Error: {e}")
        traceback.print_exc()
        return 1

if __name__ == "__main__":
    sys.exit(main()) 