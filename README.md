# Multi-Agent AI System for Customer Support

A comprehensive AI system that automates key processes in customer support operations through multiple specialized agents. This system uses Ollama for local LLM processing, eliminating the need for external API services.

## Features

### Core Agents

- **Summarization Agent**: Generates concise summaries of customer conversations
- **Action Extraction Agent**: Identifies key action items from conversations
- **Routing Agent**: Decides which team should handle the ticket
- **Resolution Recommendation Agent**: Suggests solutions based on historical data
- **Time Prediction Agent**: Estimates resolution time for each ticket

### Enhanced Features

- **Ollama LLM Integration**: Uses local Ollama models for all LLM operations
- **Embeddings Support**: Generate and store embeddings for semantic search
- **SQLite Database**: Persistent storage for conversations, actions, and results
- **Custom Tools**:
  - Local Knowledge Base for article retrieval
  - Web Scraper for fetching information from websites
  - Sentiment Analyzer for customer sentiment analysis
- **Configuration**: Environment variables and command line options

## Project Structure

```
customer_support_ai/
├── agents/                      # Agent modules
│   ├── summarization_agent.py
│   ├── action_extraction_agent.py
│   ├── routing_agent.py
│   ├── resolution_recommendation_agent.py
│   └── time_prediction_agent.py
├── data/                        # Sample data
│   ├── sample_conversations.py
│   └── historical_data.py
├── [Usecase 7]/                 # Additional conversation examples
│   └── Conversation/            # Real-world conversation examples
├── results/                     # Stored processing results
├── utils/                       # Utility modules
│   ├── data_processor.py        # Data processing utilities
│   ├── llm_interface.py         # Interface for Ollama LLM
│   ├── database.py              # SQLite database interface
│   └── custom_tools.py          # Knowledge base, web scraper, sentiment analyzer
├── app.py                       # Main application
├── process_usecase_conversations.py # Script for processing usecase conversations
├── init_db.py                   # Database initialization script
├── requirements.txt             # Dependencies
├── .env.example                 # Example environment variables
└── README.md                    # Documentation
```

## Quick Start Guide

### Prerequisites

- Python 3.8 or higher
- [Ollama](https://ollama.com/) installed on your local machine

### Step 1: Clone the Repository

```bash
git clone https://github.com/your-username/customer-support-ai.git
cd customer-support-ai
```

### Step 2: Set Up Python Environment

```bash
# Create a virtual environment
python -m venv venv

# Activate the virtual environment
# On Windows:
venv\Scripts\activate
# On macOS/Linux:
source venv/bin/activate

# Install dependencies
pip install -r requirements.txt
```

### Step 3: Set Up Ollama

1. Install Ollama from [https://ollama.com/](https://ollama.com/)
2. Pull a language model (LLM):
   ```bash
   ollama pull llama2
   ```
3. Start the Ollama server:
   ```bash
   ollama serve
   ```
   The server will run on http://localhost:11434 by default.

### Step 4: Configure the Application

```bash
# Copy example environment file
cp .env.example .env
```

Edit the `.env` file with your preferred text editor. The minimal required settings are:

```
# Ollama API Settings
OLLAMA_API_URL=http://localhost:11434/api
OLLAMA_MODEL=llama2

# SQLite Database Settings
DB_PATH=customer_support.db

# Logging Settings
LOG_LEVEL=INFO
LOG_FILE=customer_support.log
```

### Step 5: Initialize the Database

```bash
python init_db.py --sample-data
```

## Running the Application

### Process a Sample Conversation

```bash
python app.py --conversation billing_issue --verbose
```

This will process a predefined billing issue conversation and display detailed output.

### Process Usecase Conversations

To process the conversation examples in the Usecase 7 folder:

```bash
# Process all conversations in the default directory
python process_usecase_conversations.py --verbose

# Process conversations in a specific directory
python process_usecase_conversations.py --directory "[Usecase 7] AI-Driven Customer Support Enhancing Efficiency Through Multiagents/Conversation" --verbose

# Specify a custom output directory
python process_usecase_conversations.py --output-dir custom_results --verbose
```

The results will be saved as JSON files in the output directory (default: `results/`).

### Command Line Options for app.py

- `--conversation`: Conversation ID or type (password_reset, billing_issue, technical_issue)
- `--verbose`: Print detailed processing information
- `--output`: Path to save results
- `--ollama-url`: URL for the Ollama API
- `--model-name`: Name of the LLM model to use
- `--db-path`: Path to the SQLite database file
- `--knowledge-base-url`: URL for knowledge base
- `--simulate`: Simulate LLM responses (for testing without Ollama)
- `--init-db`: Initialize the database before processing

### Command Line Options for process_usecase_conversations.py

- `--directory`: Directory containing conversation files
- `--output-dir`: Directory to save results
- `--verbose`: Show verbose output

## Troubleshooting

### Ollama Connection Issues

- Ensure Ollama is running: `ollama serve`
- Verify the OLLAMA_API_URL in your .env file matches where Ollama is running
- Check if the model is downloaded: `ollama list`

### Processing Errors

- Check the log file (default: `customer_support.log`)
- Increase verbosity with the `--verbose` flag
- Try running with the `--simulate` flag to test without using Ollama

## Processing Pipeline

The system processes each conversation through the following pipeline:

1. Store conversation in database
2. Analyze customer sentiment
3. Generate conversation summary
4. Extract action items
5. Fetch relevant knowledge articles
6. Determine ticket routing
7. Generate conversation embeddings for similarity search
8. Recommend resolution steps
9. Predict resolution time
10. Store all results in the database

## Example Workflow

```bash
# Start Ollama server
ollama serve

# In a new terminal window:
cd customer-support-ai
source venv/bin/activate  # or venv\Scripts\activate on Windows

# Initialize the database
python init_db.py --sample-data

# Process a sample conversation
python app.py --conversation technical_issue --verbose

# Process usecase conversations
python process_usecase_conversations.py --verbose

# View the results
cat results/Network_Connectivity_Issue_results.json
```

## Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

## License

This project is licensed under the MIT License - see the LICENSE file for details. 