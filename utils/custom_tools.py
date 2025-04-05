import os
import requests
import json
import logging
import time
from typing import Dict, Any, Optional, List, Union
from bs4 import BeautifulSoup
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

class APIClient:
    """Client for interacting with external APIs for knowledge base access"""
    
    def __init__(self, api_base_url: Optional[str] = None, api_key: Optional[str] = None):
        """
        Initialize the API client
        
        Args:
            api_base_url: Base URL for the API (not used, kept for compatibility)
            api_key: API key for authentication (not used, kept for compatibility)
        """
        # These parameters are kept for backward compatibility
        self.api_base_url = None
        self.api_key = None
        
        # Set up logging
        logging.basicConfig(level=logging.INFO, 
                           format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
        self.logger = logging.getLogger("APIClient")
    
    def get_knowledge_articles(self, query: str, max_results: int = 5) -> List[Dict[str, Any]]:
        """
        Return preloaded knowledge base articles related to a query
        
        Args:
            query: Search query
            max_results: Maximum number of results to return
            
        Returns:
            List of knowledge articles
        """
        self.logger.info(f"Retrieving local knowledge articles for query: {query}")
        
        # Determine which set of articles to return based on query keywords
        if "billing" in query.lower() or "charge" in query.lower() or "refund" in query.lower():
            return self._get_billing_articles()
        elif "technical" in query.lower() or "error" in query.lower() or "issue" in query.lower():
            return self._get_technical_articles()
        elif "account" in query.lower() or "login" in query.lower() or "password" in query.lower():
            return self._get_account_articles()
        else:
            # Default to generic articles
            return self._get_general_articles()
    
    def _get_billing_articles(self) -> List[Dict[str, Any]]:
        """Return preloaded billing-related articles"""
        return [
            {
                "title": "Billing and Refund Process",
                "content": "Standard process for handling duplicate charges: 1) Verify the duplicate charge in billing history 2) Initiate refund through the billing system 3) Send confirmation email to customer 4) Monitor account for similar issues",
                "url": "https://example.com/help/billing-refund",
                "relevance": 0.95
            },
            {
                "title": "Subscription Billing Issues",
                "content": "Common subscription billing issues and resolutions: - Duplicate charges during system maintenance - Failed payments - Subscription renewal problems - Refund processing times",
                "url": "https://example.com/help/subscription-billing",
                "relevance": 0.90
            },
            {
                "title": "Customer Account Monitoring",
                "content": "Best practices for monitoring customer accounts: 1) Set up alerts for unusual billing patterns 2) Document all billing-related issues 3) Regular account review for high-risk customers",
                "url": "https://example.com/help/account-monitoring",
                "relevance": 0.85
            }
        ]
    
    def _get_technical_articles(self) -> List[Dict[str, Any]]:
        """Return preloaded technical articles"""
        return [
            {
                "title": "Common Technical Issues and Solutions",
                "content": "Troubleshooting steps for common technical problems: 1) Clear browser cache 2) Try a different network 3) Update software 4) Restart the application",
                "url": "https://example.com/help/technical-issues",
                "relevance": 0.95
            },
            {
                "title": "Network Connectivity Problems",
                "content": "Solutions for network-related errors: - Check internet connection - Verify firewall settings - Test alternative networks - Reset network settings",
                "url": "https://example.com/help/network-connectivity",
                "relevance": 0.90
            },
            {
                "title": "Software Update Requirements",
                "content": "Guide to updating software: 1) Check current version 2) Download latest update 3) Install update 4) Verify successful update",
                "url": "https://example.com/help/software-updates",
                "relevance": 0.85
            }
        ]
    
    def _get_account_articles(self) -> List[Dict[str, Any]]:
        """Return preloaded account-related articles"""
        return [
            {
                "title": "Account Access Troubleshooting",
                "content": "Steps to resolve login issues: 1) Reset password 2) Verify email address 3) Check account status 4) Clear browser cookies",
                "url": "https://example.com/help/account-access",
                "relevance": 0.95
            },
            {
                "title": "Password Reset Process",
                "content": "How to reset your password: - Use the forgot password link - Check your email for the reset link - Create a strong new password - Update password in all devices",
                "url": "https://example.com/help/password-reset",
                "relevance": 0.90
            },
            {
                "title": "Account Security Best Practices",
                "content": "Recommendations for account security: 1) Use strong passwords 2) Enable two-factor authentication 3) Monitor account activity 4) Sign out from shared devices",
                "url": "https://example.com/help/account-security",
                "relevance": 0.85
            }
        ]
    
    def _get_general_articles(self) -> List[Dict[str, Any]]:
        """Return general knowledge articles"""
        return [
            {
                "title": "Customer Support Guide",
                "content": "Overview of customer support services: 1) Chat support 2) Email support 3) Phone support 4) Self-service options",
                "url": "https://example.com/help/support-guide",
                "relevance": 0.80
            },
            {
                "title": "Frequently Asked Questions",
                "content": "Answers to common questions about our products and services",
                "url": "https://example.com/help/faq",
                "relevance": 0.75
            },
            {
                "title": "Contact Information",
                "content": "How to reach different support departments: - Technical support - Billing support - Account management - General inquiries",
                "url": "https://example.com/help/contact",
                "relevance": 0.70
            }
        ]
    
    def get_entity_information(self, entity_type: str, entity_id: str) -> Dict[str, Any]:
        """
        Retrieve information about a specific entity (simulated)
        
        Args:
            entity_type: Type of entity (customer, product, etc.)
            entity_id: ID of the entity
            
        Returns:
            Entity information
        """
        self.logger.info(f"Retrieving simulated entity information for {entity_type} {entity_id}")
        
        # Return simulated entity information
        return {
            "id": entity_id,
            "type": entity_type,
            "attributes": {
                "name": "Sample Entity",
                "description": "This is a simulated entity for demonstration purposes."
            }
        }
    
    def send_notification(self, recipient: str, subject: str, message: str) -> bool:
        """
        Send a notification to a recipient (simulated)
        
        Args:
            recipient: The recipient of the notification (email, user ID, etc.)
            subject: Subject of the notification
            message: Body of the notification
            
        Returns:
            Whether the notification was sent successfully
        """
        self.logger.info(f"Simulating notification to {recipient}: {subject}")
        return True


class WebScraper:
    """Web scraper for fetching information from websites"""
    
    def __init__(self, user_agent: Optional[str] = None):
        """
        Initialize the web scraper
        
        Args:
            user_agent: User agent string to use for requests
        """
        self.user_agent = user_agent or "CustomerSupportAI/1.0"
        
        # Set up logging
        logging.basicConfig(level=logging.INFO, 
                           format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
        self.logger = logging.getLogger("WebScraper")
    
    def fetch_page(self, url: str) -> Optional[str]:
        """
        Fetch the content of a web page
        
        Args:
            url: URL of the page to fetch
            
        Returns:
            HTML content of the page, or None if fetching failed
        """
        try:
            headers = {
                "User-Agent": self.user_agent
            }
            
            response = requests.get(url, headers=headers, timeout=10)
            response.raise_for_status()
            
            self.logger.info(f"Fetched page: {url}")
            return response.text
            
        except requests.exceptions.RequestException as e:
            self.logger.error(f"Error fetching page {url}: {e}")
            return None
    
    def extract_article_content(self, html: str) -> Dict[str, Any]:
        """
        Extract article content from HTML
        
        Args:
            html: HTML content to parse
            
        Returns:
            Dictionary with title, content, and metadata
        """
        try:
            soup = BeautifulSoup(html, 'html.parser')
            
            # Extract title
            title = ""
            title_tag = soup.find('title')
            if title_tag:
                title = title_tag.text.strip()
            
            # Extract main content (this is a simplistic approach)
            content = ""
            article_tag = soup.find('article')
            if article_tag:
                content = article_tag.text.strip()
            else:
                # Try to find main content div
                main_content = soup.find('div', {'class': ['content', 'main', 'article', 'post']})
                if main_content:
                    content = main_content.text.strip()
                else:
                    # Fallback to body
                    body = soup.find('body')
                    if body:
                        content = body.text.strip()
            
            # Extract metadata
            metadata = {}
            meta_tags = soup.find_all('meta')
            for tag in meta_tags:
                if tag.get('name') and tag.get('content'):
                    metadata[tag['name']] = tag['content']
            
            return {
                "title": title,
                "content": content,
                "metadata": metadata
            }
            
        except Exception as e:
            self.logger.error(f"Error extracting article content: {e}")
            return {
                "title": "",
                "content": "",
                "metadata": {}
            }
    
    def search_knowledge_base(self, base_url: str, query: str) -> List[Dict[str, Any]]:
        """
        Search a knowledge base website for relevant articles
        
        Args:
            base_url: Base URL of the knowledge base
            query: Search query
            
        Returns:
            List of relevant articles
        """
        try:
            # Format the search URL
            search_url = f"{base_url}/search?q={query.replace(' ', '+')}"
            
            # Fetch the search results page
            html = self.fetch_page(search_url)
            if not html:
                return []
            
            # Parse the search results
            soup = BeautifulSoup(html, 'html.parser')
            
            # Extract search results (this is a generic approach that needs to be adapted for specific sites)
            results = []
            result_elements = soup.find_all('div', {'class': 'search-result'})
            
            for element in result_elements:
                title_tag = element.find('h3')
                link_tag = element.find('a')
                snippet_tag = element.find('div', {'class': 'snippet'})
                
                if title_tag and link_tag:
                    title = title_tag.text.strip()
                    url = link_tag.get('href', '')
                    if not url.startswith('http'):
                        url = base_url + url
                    
                    snippet = ""
                    if snippet_tag:
                        snippet = snippet_tag.text.strip()
                    
                    results.append({
                        "title": title,
                        "url": url,
                        "snippet": snippet
                    })
            
            self.logger.info(f"Found {len(results)} search results for query: {query}")
            return results
            
        except Exception as e:
            self.logger.error(f"Error searching knowledge base: {e}")
            return []


class SentimentAnalyzer:
    """Sentiment analysis tool using basic lexicon-based approach"""
    
    def __init__(self):
        """Initialize the sentiment analyzer"""
        # Simple lexicon of positive and negative words
        self.positive_words = set([
            "good", "great", "excellent", "amazing", "wonderful", "fantastic", "terrific",
            "outstanding", "superb", "brilliant", "perfect", "happy", "pleased", "satisfied",
            "impressed", "thankful", "appreciate", "helpful", "resolved", "solved", "fixed"
        ])
        
        self.negative_words = set([
            "bad", "terrible", "awful", "horrible", "disappointing", "poor", "inadequate",
            "unacceptable", "frustrated", "annoyed", "angry", "upset", "unhappy", "dissatisfied",
            "problem", "issue", "error", "failure", "broken", "useless", "waste", "difficult"
        ])
        
        # Set up logging
        logging.basicConfig(level=logging.INFO, 
                           format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
        self.logger = logging.getLogger("SentimentAnalyzer")
    
    def analyze_sentiment(self, text: str) -> Dict[str, Any]:
        """
        Analyze the sentiment of a text
        
        Args:
            text: Text to analyze
            
        Returns:
            Dictionary with sentiment analysis results
        """
        # Convert to lowercase and split into words
        words = text.lower().split()
        
        # Count positive and negative words
        positive_count = sum(1 for word in words if word in self.positive_words)
        negative_count = sum(1 for word in words if word in self.negative_words)
        
        # Calculate sentiment score (-1 to 1)
        total_count = positive_count + negative_count
        if total_count == 0:
            sentiment_score = 0
        else:
            sentiment_score = (positive_count - negative_count) / total_count
        
        # Determine sentiment label
        if sentiment_score > 0.2:
            sentiment = "positive"
        elif sentiment_score < -0.2:
            sentiment = "negative"
        else:
            sentiment = "neutral"
        
        # Get supporting evidence
        positive_evidence = [word for word in words if word in self.positive_words]
        negative_evidence = [word for word in words if word in self.negative_words]
        
        result = {
            "sentiment": sentiment,
            "score": sentiment_score,
            "positive_count": positive_count,
            "negative_count": negative_count,
            "positive_evidence": positive_evidence[:5],  # Limit to 5 examples
            "negative_evidence": negative_evidence[:5]   # Limit to 5 examples
        }
        
        self.logger.info(f"Analyzed sentiment: {sentiment} (score: {sentiment_score:.2f})")
        return result
    
    def analyze_conversation_sentiment(self, conversation: Dict[str, Any]) -> Dict[str, Any]:
        """
        Analyze the sentiment of a customer support conversation
        
        Args:
            conversation: Conversation to analyze
            
        Returns:
            Dictionary with sentiment analysis results
        """
        if "messages" not in conversation:
            self.logger.error("Invalid conversation format")
            return {"error": "Invalid conversation format"}
        
        # Analyze customer messages only
        customer_messages = [msg.get("content", "") 
                           for msg in conversation["messages"] 
                           if msg.get("sender", "").lower() == "customer"]
        
        customer_text = " ".join(customer_messages)
        overall_sentiment = self.analyze_sentiment(customer_text)
        
        # Track sentiment changes over time
        sentiment_progression = []
        for msg in conversation["messages"]:
            if msg.get("sender", "").lower() == "customer":
                message_sentiment = self.analyze_sentiment(msg.get("content", ""))
                sentiment_progression.append({
                    "timestamp": msg.get("timestamp", ""),
                    "sentiment": message_sentiment["sentiment"],
                    "score": message_sentiment["score"]
                })
        
        # Detect sentiment shifts
        sentiment_shifts = []
        for i in range(1, len(sentiment_progression)):
            prev_score = sentiment_progression[i-1]["score"]
            curr_score = sentiment_progression[i]["score"]
            shift = curr_score - prev_score
            
            if abs(shift) >= 0.5:  # Significant shift
                sentiment_shifts.append({
                    "from_timestamp": sentiment_progression[i-1]["timestamp"],
                    "to_timestamp": sentiment_progression[i]["timestamp"],
                    "shift_value": shift,
                    "direction": "positive" if shift > 0 else "negative"
                })
        
        return {
            "overall_sentiment": overall_sentiment,
            "progression": sentiment_progression,
            "shifts": sentiment_shifts
        }


# Use the tools when run directly
if __name__ == "__main__":
    # Test API client
    api_client = APIClient()
    articles = api_client.get_knowledge_articles("password reset")
    print(f"Found {len(articles)} knowledge articles")
    
    # Test web scraper
    scraper = WebScraper()
    html = scraper.fetch_page("https://example.com")
    if html:
        content = scraper.extract_article_content(html)
        print(f"Title: {content['title']}")
    
    # Test sentiment analyzer
    analyzer = SentimentAnalyzer()
    result = analyzer.analyze_sentiment("I'm very happy with the excellent service provided!")
    print(f"Sentiment: {result['sentiment']} (score: {result['score']:.2f})") 