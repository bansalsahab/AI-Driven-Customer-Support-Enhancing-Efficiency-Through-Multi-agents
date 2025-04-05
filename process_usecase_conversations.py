#!/usr/bin/env python3
"""
Process conversations from the Usecase 7 folder
This script reads conversation files from the Usecase 7 directory and processes them
with the Customer Support AI system.
"""

import os
import sys
import json
from typing import Dict, Any, List
import argparse
from app import CustomerSupportAI

def read_conversation_file(file_path: str) -> Dict[str, Any]:
    """
    Read a conversation file and convert it to the expected format
    
    Args:
        file_path: Path to the conversation file
        
    Returns:
        Dictionary containing the conversation data
    """
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            lines = f.readlines()
        
        if len(lines) < 3:
            print(f"Error: Invalid conversation file format: {file_path}")
            return None
        
        # Extract metadata
        conversation_id = lines[0].split(':')[1].strip() if len(lines[0].split(':')) > 1 else "unknown"
        category = lines[1].split(':')[1].strip() if len(lines[1].split(':')) > 1 else "unknown"
        
        # Parse sentiment and priority
        sentiment_priority = lines[2].split(':')[1].strip() if len(lines[2].split(':')) > 1 else ""
        sentiment = sentiment_priority.split('|')[0].strip() if '|' in sentiment_priority else ""
        priority = sentiment_priority.split('|')[1].strip() if '|' in sentiment_priority else ""
        
        # Parse messages
        messages = []
        timestamp_base = "2023-07-15 "
        hour = 10
        minute = 0
        
        for i in range(3, len(lines)):
            line = lines[i].strip()
            if not line:
                continue
                
            parts = line.split(':', 1)
            if len(parts) < 2:
                continue
                
            sender = parts[0].strip()
            content = parts[1].strip().strip('"')
            
            # Create a simple timestamp
            timestamp = f"{timestamp_base}{hour:02d}:{minute:02d}:00"
            minute += 5
            if minute >= 60:
                hour += 1
                minute = 0
            
            messages.append({
                "sender": sender,
                "content": content,
                "timestamp": timestamp
            })
        
        # Create conversation object
        conversation = {
            "conversation_id": conversation_id,
            "category": category,
            "sentiment": sentiment,
            "priority": priority,
            "messages": messages
        }
        
        return conversation
        
    except Exception as e:
        print(f"Error reading conversation file {file_path}: {e}")
        return None

def get_conversation_files(directory: str) -> List[str]:
    """
    Get all conversation files from the specified directory
    
    Args:
        directory: Directory to search
        
    Returns:
        List of file paths
    """
    files = []
    try:
        for filename in os.listdir(directory):
            if filename.endswith('.txt'):
                files.append(os.path.join(directory, filename))
    except Exception as e:
        print(f"Error listing directory {directory}: {e}")
    
    return files

def main():
    """Process conversation files with Customer Support AI"""
    parser = argparse.ArgumentParser(description='Process conversation files with Customer Support AI')
    parser.add_argument('--directory', type=str, 
                        default='[Usecase 7] AI-Driven Customer Support Enhancing Efficiency Through Multiagents/Conversation',
                        help='Directory containing conversation files')
    parser.add_argument('--output-dir', type=str, default='results',
                        help='Directory to save results')
    parser.add_argument('--verbose', action='store_true',
                        help='Show verbose output')
    args = parser.parse_args()
    
    # Initialize the system
    system = CustomerSupportAI(
        db_path='customer_support.db'
    )
    
    # Create output directory if it doesn't exist
    os.makedirs(args.output_dir, exist_ok=True)
    
    # Find conversation files
    conversation_files = get_conversation_files(args.directory)
    if not conversation_files:
        print(f"Error: No conversation files found in {args.directory}")
        return 1
    
    print(f"Found {len(conversation_files)} conversation files to process.")
    
    for file_path in conversation_files:
        file_name = os.path.basename(file_path)
        print(f"Processing {file_name}...")
        
        # Read conversation
        conversation = read_conversation_file(file_path)
        if not conversation:
            print(f"Skipping {file_name} due to errors.")
            continue
        
        # Process conversation
        try:
            results = system.process_conversation(conversation, verbose=args.verbose)
            
            # Save the results
            output_file = os.path.join(args.output_dir, f"{os.path.splitext(file_name)[0]}_results.json")
            with open(output_file, 'w') as f:
                json.dump(results, f, indent=2)
                
            print(f"Results saved to {output_file}")
            print(f"Total processing time: {results['processing_time']['total']:.2f} seconds")
            
            # Display errors
            if results.get('error'):
                print(f"Error: {results['error']}")
                
        except Exception as e:
            print(f"Error processing {file_name}: {e}")
    
    print("\nProcessing complete.")
    return 0

if __name__ == "__main__":
    sys.exit(main()) 