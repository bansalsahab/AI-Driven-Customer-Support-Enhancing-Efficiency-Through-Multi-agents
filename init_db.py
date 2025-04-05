#!/usr/bin/env python3
"""
Database Initialization Script for Customer Support AI

This script initializes the SQLite database and populates it with sample data.

Usage:
    python init_db.py [--db-path DB_PATH] [--sample-data]
"""

import os
import sys
import argparse
import logging
from typing import Dict, Any, List, Optional
import json
from datetime import datetime

from utils.database import Database
from data.historical_data import generate_historical_data

def init_database(db_path: str, add_sample_data: bool = False) -> None:
    """
    Initialize the database with tables and optionally add sample data
    
    Args:
        db_path: Path to the SQLite database file
        add_sample_data: Whether to add sample historical data
    """
    logging.basicConfig(level=logging.INFO, 
                       format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
    logger = logging.getLogger("init_db")
    
    logger.info(f"Initializing database at {db_path}")
    
    # Create database and tables
    db = Database(db_path)
    
    # Add sample historical data if requested
    if add_sample_data:
        logger.info("Generating sample historical data...")
        sample_data = generate_historical_data(100)
        
        # Convert DataFrame to list of dictionaries
        records = sample_data.to_dict(orient='records')
        
        logger.info(f"Importing {len(records)} historical data records...")
        db.import_historical_data(records)
        
        # Add some sample embeddings
        logger.info("Adding sample embeddings...")
        add_sample_embeddings(db)
    
    logger.info(f"Database initialization complete at {db_path}")

def add_sample_embeddings(db: Database) -> None:
    """
    Add some sample embeddings to the database
    
    Args:
        db: Database instance
    """
    # Sample texts to embed
    sample_texts = [
        "Customer having login issues with their account",
        "User can't reset their password",
        "Billing issues with duplicate charges",
        "Problems with product installation",
        "Feature request for new functionality"
    ]
    
    # Simulate embeddings (10-dimensional vectors)
    import random
    for i, text in enumerate(sample_texts):
        # Create a sample embedding vector
        embedding = [random.random() for _ in range(10)]
        
        # Store the embedding
        db.store_embedding(
            source_type="sample",
            source_id=f"sample-{i}",
            text=text,
            embedding=embedding,
            model="sample-model"
        )

def main():
    """Main entry point for the script"""
    parser = argparse.ArgumentParser(description="Initialize the Customer Support AI database")
    parser.add_argument("--db-path", type=str, default="customer_support.db",
                       help="Path to the SQLite database file (default: customer_support.db)")
    parser.add_argument("--sample-data", action="store_true",
                       help="Add sample historical data to the database")
    
    args = parser.parse_args()
    
    # Initialize the database
    init_database(args.db_path, args.sample_data)
    
    return 0

if __name__ == "__main__":
    sys.exit(main()) 