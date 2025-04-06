# Customer Support AI Streamlit Dashboard

This Streamlit dashboard provides a user-friendly web interface for the Customer Support AI system. It allows you to analyze customer support conversations, visualize the results, and explore insights from the AI processing.

## Features

- Analyze customer support conversations using AI
- View conversation summaries, sentiment analysis, and action items
- Get ticket routing recommendations and resolution time predictions
- Upload your own conversations or use pre-defined samples
- Browse previously processed conversations

## How to Run the App

1. Make sure you have installed all requirements:
   ```bash
   pip install -r requirements.txt
   ```

2. Start Ollama server (if using real LLM processing):
   ```bash
   ollama serve
   ```

3. Run the Streamlit app:
   ```bash
   streamlit run streamlit_app.py
   ```

4. Open your browser at `http://localhost:8501`

## Using the App

### Analyze a Conversation

1. Go to the "Analyze Conversation" page
2. Choose one of the following input methods:
   - **Sample Conversations**: Select a pre-defined sample and click "Analyze Sample"
   - **Upload File**: Upload a text or JSON file containing a conversation
   - **Paste Text**: Paste a conversation in the text area and click "Analyze Text"

### Text Format

If you're using the text input or uploading a text file, use the following format:

```
Conversation ID: TECH_001
Category: Technical Support
Sentiment: Frustrated | Priority: High
Customer: "Hi there! I've been trying to install the latest update..."
Agent: "Hello! Thank you for reaching out..."
Customer: "Sure, it's Windows 11. Here's the screenshot..."
Agent: "Thank you for the details. This is a known conflict..."
Customer: "Oh, disabling the antivirus worked! Installation completed..."
Agent: "You're welcome! Let us know if you need further assistance..."
```

### View Sample Results

Go to the "Sample Results" page to browse through previously processed conversations stored in the `results` directory.

## Troubleshooting

- If you see errors related to Ollama, make sure the Ollama server is running
- If the app fails to load, check that you have all the required packages installed
- If processing takes too long, consider using the `--simulate` flag in the underlying system

## Adding New Features

To extend the Streamlit app:

1. Edit `streamlit_app.py`
2. Add new tabs or sections in the `display_results` function
3. Create new visualization components as needed 