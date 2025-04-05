import sqlite3
import json
import os
import logging
from typing import Dict, Any, List, Optional, Tuple, Union
from datetime import datetime

class Database:
    """SQLite database interface for storing customer support data"""
    
    def __init__(self, db_path: str = "customer_support.db"):
        """
        Initialize the database interface
        
        Args:
            db_path: Path to the SQLite database file
        """
        self.db_path = db_path
        
        # Set up logging
        logging.basicConfig(level=logging.INFO, 
                           format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
        self.logger = logging.getLogger("Database")
        
        # Create tables if they don't exist
        self._initialize_database()
    
    def _get_connection(self) -> sqlite3.Connection:
        """Get a connection to the SQLite database"""
        return sqlite3.connect(self.db_path)
    
    def _initialize_database(self) -> None:
        """Create the necessary tables if they don't exist"""
        try:
            conn = self._get_connection()
            cursor = conn.cursor()
            
            # Create conversations table
            cursor.execute('''
            CREATE TABLE IF NOT EXISTS conversations (
                conversation_id TEXT PRIMARY KEY,
                raw_data TEXT,
                summary TEXT,
                timestamp TEXT,
                metadata TEXT
            )
            ''')
            
            # Create actions table
            cursor.execute('''
            CREATE TABLE IF NOT EXISTS actions (
                action_id INTEGER PRIMARY KEY AUTOINCREMENT,
                conversation_id TEXT,
                action TEXT,
                priority TEXT,
                status TEXT,
                timestamp TEXT,
                FOREIGN KEY (conversation_id) REFERENCES conversations(conversation_id)
            )
            ''')
            
            # Create routing_decisions table
            cursor.execute('''
            CREATE TABLE IF NOT EXISTS routing_decisions (
                decision_id INTEGER PRIMARY KEY AUTOINCREMENT,
                conversation_id TEXT,
                recommended_team TEXT,
                confidence TEXT,
                justification TEXT,
                timestamp TEXT,
                FOREIGN KEY (conversation_id) REFERENCES conversations(conversation_id)
            )
            ''')
            
            # Create resolution_recommendations table
            cursor.execute('''
            CREATE TABLE IF NOT EXISTS resolution_recommendations (
                recommendation_id INTEGER PRIMARY KEY AUTOINCREMENT,
                conversation_id TEXT,
                immediate_steps TEXT,
                complete_resolution_path TEXT,
                reasoning TEXT,
                confidence_score REAL,
                timestamp TEXT,
                FOREIGN KEY (conversation_id) REFERENCES conversations(conversation_id)
            )
            ''')
            
            # Create time_predictions table
            cursor.execute('''
            CREATE TABLE IF NOT EXISTS time_predictions (
                prediction_id INTEGER PRIMARY KEY AUTOINCREMENT,
                conversation_id TEXT,
                predicted_category TEXT,
                estimated_hours INTEGER,
                confidence_score REAL,
                factors TEXT,
                timestamp TEXT,
                FOREIGN KEY (conversation_id) REFERENCES conversations(conversation_id)
            )
            ''')
            
            # Create historical_data table
            cursor.execute('''
            CREATE TABLE IF NOT EXISTS historical_data (
                record_id INTEGER PRIMARY KEY AUTOINCREMENT,
                ticket_id TEXT,
                issue_type TEXT,
                assigned_team TEXT,
                status TEXT,
                priority TEXT,
                resolution_time_hours INTEGER,
                resolution_details TEXT,
                customer_satisfaction INTEGER,
                created_date TEXT
            )
            ''')
            
            # Create embeddings table for semantic search
            cursor.execute('''
            CREATE TABLE IF NOT EXISTS embeddings (
                embedding_id INTEGER PRIMARY KEY AUTOINCREMENT,
                source_type TEXT,  -- conversations, historical_data, etc.
                source_id TEXT,    -- conversation_id, record_id, etc.
                text TEXT,         -- The text that was embedded
                embedding BLOB,    -- The serialized embedding vector
                embedding_model TEXT,
                timestamp TEXT
            )
            ''')
            
            conn.commit()
            self.logger.info("Database tables initialized successfully")
            
        except sqlite3.Error as e:
            self.logger.error(f"Database initialization error: {e}")
            raise
        finally:
            conn.close()
    
    def store_conversation(self, conversation: Dict[str, Any], metadata: Optional[Dict[str, Any]] = None) -> None:
        """
        Store a conversation in the database
        
        Args:
            conversation: The conversation to store
            metadata: Optional metadata about the conversation
        """
        try:
            conversation_id = conversation.get("conversation_id", str(datetime.now().timestamp()))
            
            conn = self._get_connection()
            cursor = conn.cursor()
            
            cursor.execute(
                "INSERT OR REPLACE INTO conversations (conversation_id, raw_data, timestamp, metadata) VALUES (?, ?, ?, ?)",
                (
                    conversation_id,
                    json.dumps(conversation),
                    datetime.now().isoformat(),
                    json.dumps(metadata) if metadata else "{}"
                )
            )
            
            conn.commit()
            self.logger.info(f"Stored conversation {conversation_id}")
            
        except sqlite3.Error as e:
            self.logger.error(f"Error storing conversation: {e}")
            raise
        finally:
            conn.close()
    
    def update_conversation_summary(self, conversation_id: str, summary: str) -> None:
        """
        Update the summary of a conversation
        
        Args:
            conversation_id: The ID of the conversation
            summary: The summary to store
        """
        try:
            conn = self._get_connection()
            cursor = conn.cursor()
            
            cursor.execute(
                "UPDATE conversations SET summary = ? WHERE conversation_id = ?",
                (summary, conversation_id)
            )
            
            conn.commit()
            self.logger.info(f"Updated summary for conversation {conversation_id}")
            
        except sqlite3.Error as e:
            self.logger.error(f"Error updating conversation summary: {e}")
            raise
        finally:
            conn.close()
    
    def store_actions(self, conversation_id: str, actions: Dict[str, Any]) -> None:
        """
        Store extracted actions for a conversation
        
        Args:
            conversation_id: The ID of the conversation
            actions: The extracted actions
        """
        try:
            conn = self._get_connection()
            cursor = conn.cursor()
            
            # First, delete any existing actions for this conversation
            cursor.execute("DELETE FROM actions WHERE conversation_id = ?", (conversation_id,))
            
            # Insert new actions
            if "action_items" in actions:
                for action_item in actions["action_items"]:
                    cursor.execute(
                        "INSERT INTO actions (conversation_id, action, priority, status, timestamp) VALUES (?, ?, ?, ?, ?)",
                        (
                            conversation_id,
                            action_item.get("action", ""),
                            action_item.get("priority", "Medium"),
                            action_item.get("status", "Pending"),
                            datetime.now().isoformat()
                        )
                    )
            
            conn.commit()
            self.logger.info(f"Stored actions for conversation {conversation_id}")
            
        except sqlite3.Error as e:
            self.logger.error(f"Error storing actions: {e}")
            raise
        finally:
            conn.close()
    
    def store_routing_decision(self, conversation_id: str, routing: Dict[str, Any]) -> None:
        """
        Store routing decision for a conversation
        
        Args:
            conversation_id: The ID of the conversation
            routing: The routing decision
        """
        try:
            conn = self._get_connection()
            cursor = conn.cursor()
            
            # First, delete any existing routing decisions for this conversation
            cursor.execute("DELETE FROM routing_decisions WHERE conversation_id = ?", (conversation_id,))
            
            # Insert new routing decision
            cursor.execute(
                "INSERT INTO routing_decisions (conversation_id, recommended_team, confidence, justification, timestamp) VALUES (?, ?, ?, ?, ?)",
                (
                    conversation_id,
                    routing.get("recommended_team", "Unknown"),
                    routing.get("confidence", "Medium"),
                    routing.get("justification", ""),
                    routing.get("timestamp", datetime.now().isoformat())
                )
            )
            
            conn.commit()
            self.logger.info(f"Stored routing decision for conversation {conversation_id}")
            
        except sqlite3.Error as e:
            self.logger.error(f"Error storing routing decision: {e}")
            raise
        finally:
            conn.close()
    
    def store_resolution_recommendation(self, conversation_id: str, recommendation: Dict[str, Any]) -> None:
        """
        Store resolution recommendation for a conversation
        
        Args:
            conversation_id: The ID of the conversation
            recommendation: The resolution recommendation
        """
        try:
            conn = self._get_connection()
            cursor = conn.cursor()
            
            # First, delete any existing recommendations for this conversation
            cursor.execute("DELETE FROM resolution_recommendations WHERE conversation_id = ?", (conversation_id,))
            
            # Insert new recommendation
            cursor.execute(
                "INSERT INTO resolution_recommendations (conversation_id, immediate_steps, complete_resolution_path, reasoning, confidence_score, timestamp) VALUES (?, ?, ?, ?, ?, ?)",
                (
                    conversation_id,
                    json.dumps(recommendation.get("immediate_steps", [])),
                    json.dumps(recommendation.get("complete_resolution_path", [])),
                    recommendation.get("reasoning", ""),
                    recommendation.get("confidence_score", 0.0),
                    recommendation.get("timestamp", datetime.now().isoformat())
                )
            )
            
            conn.commit()
            self.logger.info(f"Stored resolution recommendation for conversation {conversation_id}")
            
        except sqlite3.Error as e:
            self.logger.error(f"Error storing resolution recommendation: {e}")
            raise
        finally:
            conn.close()
    
    def store_time_prediction(self, conversation_id: str, prediction: Dict[str, Any]) -> None:
        """
        Store time prediction for a conversation
        
        Args:
            conversation_id: The ID of the conversation
            prediction: The time prediction
        """
        try:
            conn = self._get_connection()
            cursor = conn.cursor()
            
            # First, delete any existing predictions for this conversation
            cursor.execute("DELETE FROM time_predictions WHERE conversation_id = ?", (conversation_id,))
            
            # Insert new prediction
            cursor.execute(
                "INSERT INTO time_predictions (conversation_id, predicted_category, estimated_hours, confidence_score, factors, timestamp) VALUES (?, ?, ?, ?, ?, ?)",
                (
                    conversation_id,
                    prediction.get("predicted_category", "unknown"),
                    prediction.get("estimated_hours", 0),
                    prediction.get("confidence_score", 0.0),
                    json.dumps(prediction.get("factors", [])),
                    prediction.get("timestamp", datetime.now().isoformat())
                )
            )
            
            conn.commit()
            self.logger.info(f"Stored time prediction for conversation {conversation_id}")
            
        except sqlite3.Error as e:
            self.logger.error(f"Error storing time prediction: {e}")
            raise
        finally:
            conn.close()
    
    def store_embedding(self, source_type: str, source_id: str, text: str, embedding: List[float], model: str) -> None:
        """
        Store an embedding vector in the database
        
        Args:
            source_type: Type of the source (e.g., "conversation", "historical_data")
            source_id: ID of the source (e.g., conversation_id, record_id)
            text: The text that was embedded
            embedding: The embedding vector
            model: The embedding model used
        """
        try:
            conn = self._get_connection()
            cursor = conn.cursor()
            
            cursor.execute(
                "INSERT INTO embeddings (source_type, source_id, text, embedding, embedding_model, timestamp) VALUES (?, ?, ?, ?, ?, ?)",
                (
                    source_type,
                    source_id,
                    text,
                    json.dumps(embedding),  # Store as JSON string
                    model,
                    datetime.now().isoformat()
                )
            )
            
            conn.commit()
            self.logger.info(f"Stored embedding for {source_type} {source_id}")
            
        except sqlite3.Error as e:
            self.logger.error(f"Error storing embedding: {e}")
            raise
        finally:
            conn.close()
    
    def find_similar_embeddings(self, embedding: List[float], source_type: Optional[str] = None, limit: int = 5) -> List[Dict[str, Any]]:
        """
        Find similar embeddings using dot product similarity
        
        Args:
            embedding: The query embedding vector
            source_type: Optional filter for source type
            limit: Maximum number of results to return
            
        Returns:
            List of similar items with similarity scores
        """
        try:
            conn = self._get_connection()
            conn.create_function("dot_product", 2, self._dot_product)
            cursor = conn.cursor()
            
            query = """
            SELECT source_type, source_id, text, dot_product(embedding, ?) as similarity
            FROM embeddings
            """
            params = [json.dumps(embedding)]
            
            if source_type:
                query += " WHERE source_type = ?"
                params.append(source_type)
            
            query += " ORDER BY similarity DESC LIMIT ?"
            params.append(limit)
            
            cursor.execute(query, params)
            results = cursor.fetchall()
            
            similar_items = []
            for source_type, source_id, text, similarity in results:
                similar_items.append({
                    "source_type": source_type,
                    "source_id": source_id,
                    "text": text,
                    "similarity": similarity
                })
            
            return similar_items
            
        except sqlite3.Error as e:
            self.logger.error(f"Error finding similar embeddings: {e}")
            return []
        finally:
            conn.close()
    
    def _dot_product(self, embedding1_json: str, embedding2_json: str) -> float:
        """
        Calculate dot product between two embedding vectors stored as JSON strings
        
        Args:
            embedding1_json: First embedding vector as JSON string
            embedding2_json: Second embedding vector as JSON string
            
        Returns:
            Dot product similarity
        """
        embedding1 = json.loads(embedding1_json)
        embedding2 = json.loads(embedding2_json)
        
        # Calculate dot product
        if len(embedding1) != len(embedding2):
            return 0.0
        
        return sum(a * b for a, b in zip(embedding1, embedding2))
    
    def import_historical_data(self, historical_data: List[Dict[str, Any]]) -> None:
        """
        Import historical support data into the database
        
        Args:
            historical_data: List of historical support records
        """
        try:
            conn = self._get_connection()
            cursor = conn.cursor()
            
            for record in historical_data:
                cursor.execute(
                    """
                    INSERT INTO historical_data 
                    (ticket_id, issue_type, assigned_team, status, priority, 
                     resolution_time_hours, resolution_details, customer_satisfaction, created_date)
                    VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
                    """,
                    (
                        record.get("ticket_id", ""),
                        record.get("issue_type", ""),
                        record.get("assigned_team", ""),
                        record.get("status", ""),
                        record.get("priority", ""),
                        record.get("resolution_time_hours", 0),
                        record.get("resolution_details", ""),
                        record.get("customer_satisfaction", 0),
                        record.get("created_date", datetime.now().isoformat())
                    )
                )
            
            conn.commit()
            self.logger.info(f"Imported {len(historical_data)} historical data records")
            
        except sqlite3.Error as e:
            self.logger.error(f"Error importing historical data: {e}")
            raise
        finally:
            conn.close()
    
    def get_similar_historical_issues(self, issue_type: str, limit: int = 5) -> List[Dict[str, Any]]:
        """
        Get historical records for similar issues
        
        Args:
            issue_type: The type of issue to find similar records for
            limit: Maximum number of records to return
            
        Returns:
            List of similar historical records
        """
        try:
            conn = self._get_connection()
            cursor = conn.cursor()
            
            cursor.execute(
                """
                SELECT * FROM historical_data
                WHERE issue_type = ?
                ORDER BY created_date DESC
                LIMIT ?
                """,
                (issue_type, limit)
            )
            
            columns = [col[0] for col in cursor.description]
            results = cursor.fetchall()
            
            similar_issues = []
            for row in results:
                similar_issues.append(dict(zip(columns, row)))
            
            return similar_issues
            
        except sqlite3.Error as e:
            self.logger.error(f"Error getting similar historical issues: {e}")
            return []
        finally:
            conn.close()
    
    def get_conversation(self, conversation_id: str) -> Optional[Dict[str, Any]]:
        """
        Get a conversation by ID
        
        Args:
            conversation_id: The ID of the conversation to retrieve
            
        Returns:
            The conversation or None if not found
        """
        try:
            conn = self._get_connection()
            cursor = conn.cursor()
            
            cursor.execute(
                "SELECT conversation_id, raw_data, summary, timestamp, metadata FROM conversations WHERE conversation_id = ?",
                (conversation_id,)
            )
            
            result = cursor.fetchone()
            if not result:
                return None
            
            conversation_id, raw_data, summary, timestamp, metadata = result
            
            return {
                "conversation_id": conversation_id,
                "conversation": json.loads(raw_data),
                "summary": summary,
                "timestamp": timestamp,
                "metadata": json.loads(metadata)
            }
            
        except sqlite3.Error as e:
            self.logger.error(f"Error getting conversation: {e}")
            return None
        finally:
            conn.close()
    
    def get_processing_results(self, conversation_id: str) -> Dict[str, Any]:
        """
        Get all processing results for a conversation
        
        Args:
            conversation_id: The ID of the conversation
            
        Returns:
            Dictionary with all processing results
        """
        results = {
            "conversation_id": conversation_id,
            "summary": None,
            "actions": {"action_items": []},
            "routing": {},
            "recommendations": {},
            "time_prediction": {}
        }
        
        try:
            conn = self._get_connection()
            cursor = conn.cursor()
            
            # Get conversation summary
            cursor.execute(
                "SELECT summary FROM conversations WHERE conversation_id = ?",
                (conversation_id,)
            )
            result = cursor.fetchone()
            if result:
                results["summary"] = result[0]
            
            # Get actions
            cursor.execute(
                "SELECT action, priority, status FROM actions WHERE conversation_id = ?",
                (conversation_id,)
            )
            actions = cursor.fetchall()
            results["actions"]["action_items"] = [
                {"action": action, "priority": priority, "status": status}
                for action, priority, status in actions
            ]
            results["actions"]["total_actions"] = len(results["actions"]["action_items"])
            
            # Get routing decision
            cursor.execute(
                "SELECT recommended_team, confidence, justification, timestamp FROM routing_decisions WHERE conversation_id = ? ORDER BY timestamp DESC LIMIT 1",
                (conversation_id,)
            )
            routing = cursor.fetchone()
            if routing:
                team, confidence, justification, timestamp = routing
                results["routing"] = {
                    "recommended_team": team,
                    "confidence": confidence,
                    "justification": justification,
                    "timestamp": timestamp
                }
            
            # Get resolution recommendation
            cursor.execute(
                "SELECT immediate_steps, complete_resolution_path, reasoning, confidence_score, timestamp FROM resolution_recommendations WHERE conversation_id = ? ORDER BY timestamp DESC LIMIT 1",
                (conversation_id,)
            )
            recommendation = cursor.fetchone()
            if recommendation:
                immediate_steps, complete_path, reasoning, confidence, timestamp = recommendation
                results["recommendations"] = {
                    "immediate_steps": json.loads(immediate_steps),
                    "complete_resolution_path": json.loads(complete_path),
                    "reasoning": reasoning,
                    "confidence_score": confidence,
                    "timestamp": timestamp
                }
            
            # Get time prediction
            cursor.execute(
                "SELECT predicted_category, estimated_hours, confidence_score, factors, timestamp FROM time_predictions WHERE conversation_id = ? ORDER BY timestamp DESC LIMIT 1",
                (conversation_id,)
            )
            prediction = cursor.fetchone()
            if prediction:
                category, hours, confidence, factors, timestamp = prediction
                results["time_prediction"] = {
                    "predicted_category": category,
                    "estimated_hours": hours,
                    "confidence_score": confidence,
                    "factors": json.loads(factors),
                    "timestamp": timestamp
                }
            
            return results
            
        except sqlite3.Error as e:
            self.logger.error(f"Error getting processing results: {e}")
            return results
        finally:
            conn.close()


# Initialize the database when run directly
if __name__ == "__main__":
    db = Database("customer_support.db")
    print(f"Database initialized at {db.db_path}") 