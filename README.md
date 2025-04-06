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
- **Streamlit Web Interface**: User-friendly dashboard for analyzing conversations and visualizing results
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
├── app.py                       # Main application (CLI)
├── streamlit_app.py             # Streamlit web interface
├── streamlit_app_readme.md      # Streamlit app documentation
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
git clone https://github.com/bansalsahab/AI-Driven-Customer-Support-Enhancing-Efficiency-Through-Multi-agents.git
cd AI-Driven-Customer-Support-Enhancing-Efficiency-Through-Multi-agents
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

### Option 1: Using the Streamlit Web Interface (Recommended)

The Streamlit interface provides a user-friendly dashboard for conversation analysis and visualization.

```bash
# Start the Streamlit app
python -m streamlit run streamlit_app.py
```

This will open a web browser at `http://localhost:8501` with the dashboard.

**Features of the Streamlit interface:**
- Upload or paste conversations for analysis
- Interactive visualization of analysis results
- Tabbed interface for different aspects of the analysis (summary, sentiment, actions, etc.)
- Visual charts for sentiment, processing time, and other metrics
- Browse previously analyzed conversations

For more details, see the [Streamlit App Documentation](streamlit_app_readme.md).

### Option 2: Using the Command Line Interface

```bash
# Process a sample conversation
python app.py --conversation billing_issue --verbose

# Process conversations in the Usecase 7 folder
python process_usecase_conversations.py --verbose
```

This will process the conversation and display detailed output in the terminal.

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

### Streamlit Interface Issues

- Make sure you have installed streamlit: `pip install streamlit`
- If charts aren't displaying, check if matplotlib and plotly are installed
- For input parsing issues, check the conversation format in the documentation

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

## Agent Interaction Design

The Customer Support AI is designed as a multi-agent system where specialized agents work together to provide comprehensive analysis of support conversations. The system follows a sequential pipeline model with information flowing from one agent to the next.

### Agent Communication Flow

```
                          ┌─────────────────┐
                          │   Raw Support   │
                          │  Conversation   │
                          └────────┬────────┘
                                   ▼
                        ┌──────────────────────┐
                        │  Sentiment Analyzer  │◄───┐
                        └──────────┬───────────┘    │
                                   ▼                │
                      ┌─────────────────────────┐   │
                      │   Summarization Agent   │   │
                      └──────────┬──────────────┘   │
                                 ▼                  │
                     ┌──────────────────────────┐   │
                     │  Action Extraction Agent │   │
                     └──────────┬───────────────┘   │
                                ▼                   │
                     ┌──────────────────────────┐   │
                     │     Knowledge Base       │   │
                     │   Retrieval System       │   │
                                ▼                   │
                     ┌──────────────────────────┐   │
                     │      Routing Agent       │   │
                     └──────────┬───────────────┘   │
                                ▼                   │
                    ┌─────────────────────────────┐ │
                    │ Resolution Recommendation   │ │
                    │          Agent              │ │
                    └──────────┬─────────────────┘ │
                               ▼                   │
                    ┌─────────────────────────────┐│
                    │   Time Prediction Agent     ├┘
                    └─────────────────────────────┘
```

### Agent Coordination

The system uses a **Orchestrator Pattern** where the main application (app.py) coordinates the activities of all agents:

1. **Data Sharing**: Agents share information through the orchestrator
   - Each agent receives the conversation and outputs from previous agents
   - Results from each stage are stored in the database for persistence

2. **Independent Specialization**: Each agent is highly specialized
   - Summarization Agent focuses only on generating concise summaries
   - Action Extraction Agent identifies specific action items
   - Routing Agent determines which team should handle the ticket

3. **Loose Coupling**: Agents are designed with minimal dependencies
   - Each agent has a well-defined interface with clear inputs and outputs
   - Agents can be modified or replaced individually without affecting others

4. **Standardized Communication**: All agents use a common LLM interface
   - The LLMInterface class provides consistent access to language models
   - Standardized prompting patterns ensure consistent agent behavior

## Code Structure and Architecture

The codebase is organized using a modular architecture following these design principles:

### Core Components

1. **Main Application (app.py)**
   - Serves as the orchestrator for the entire system
   - Initializes all agents and tools
   - Manages the processing pipeline

2. **Agent Modules (agents/)**
   - Each agent is implemented as a separate class
   - All agents follow a common interface pattern
   - Each agent has a primary method that performs its specific task

3. **Utilities (utils/)**
   - **LLM Interface**: Abstraction layer for language model access
   - **Database**: Data persistence layer with SQL operations
   - **Data Processor**: Conversation formatting and processing
   - **Custom Tools**: Knowledge base, web scraping, sentiment analysis

4. **Web Interface (streamlit_app.py)**
   - Provides a user-friendly dashboard
   - Visualizes results from all agents
   - Allows for interactive conversation analysis

### Design Patterns

1. **Strategy Pattern**
   - Different LLM providers can be swapped (Ollama, simulated responses)
   - Processing strategies can be changed without modifying the core logic

2. **Repository Pattern**
   - Database class encapsulates all data access logic
   - Provides methods for storing and retrieving different types of data

3. **Facade Pattern**
   - The CustomerSupportAI class provides a simplified interface to the complex system
   - Clients interact with a single entry point rather than multiple subsystems

4. **Dependency Injection**
   - All agents receive their dependencies through constructors
   - Makes testing and configuration more flexible

### Code Organization

```python
# Example agent structure
class SummarizationAgent:
    def __init__(self, llm_interface):
        self.llm_interface = llm_interface
        self.data_processor = DataProcessor()
        
    def summarize(self, conversation):
        # Format the conversation
        formatted_text = self.data_processor.format_conversation_for_summarization(conversation)
        
        # Create the prompt
        prompt = self._create_summarization_prompt(formatted_text)
        
        # Generate the summary using the LLM
        summary = self.llm_interface.generate_response(prompt)
        
        return summary
        
    def _create_summarization_prompt(self, formatted_text):
        # Create a specialized prompt for summarization
        return f"""Generate a concise summary of the following customer support conversation.
        Focus on three key points:
        1. Main issue
        2. Attempted solutions
        3. Final outcome or current status
        
        Conversation:
        {formatted_text}
        """
```

This architecture allows for easy extension of the system with new agents or capabilities while maintaining a clear separation of concerns and flexibility in deployment options.

## Example Workflow

```bash
# Start Ollama server
ollama serve

# In a new terminal window:
cd AI-Driven-Customer-Support-Enhancing-Efficiency-Through-Multi-agents
source venv/bin/activate  # or venv\Scripts\activate on Windows

# Initialize the database
python init_db.py --sample-data

# Option 1: Run the Streamlit web interface
python -m streamlit run streamlit_app.py

# Option 2: Process a sample conversation via CLI
python app.py --conversation technical_issue --verbose

# Option 3: Process usecase conversations
python process_usecase_conversations.py --verbose
```


