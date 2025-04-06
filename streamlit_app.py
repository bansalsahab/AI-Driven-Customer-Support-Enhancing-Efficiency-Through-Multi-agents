import streamlit as st
import json
import os
import pandas as pd
import matplotlib.pyplot as plt
import time
from io import StringIO
import re

# Import the Customer Support AI system
from app import CustomerSupportAI

# Set page configuration
st.set_page_config(
    page_title="Customer Support AI Dashboard",
    page_icon="📊",
    layout="wide"
)

# Initialize the Customer Support AI system
@st.cache_resource
def load_ai_system():
    return CustomerSupportAI(db_path='customer_support.db')

system = load_ai_system()

# Title and description
st.title("Customer Support AI Dashboard")
st.markdown("""
This dashboard allows you to analyze customer support conversations using a multi-agent AI system.
Upload a conversation or select a sample to see AI-powered insights.
""")

# Sidebar for navigation and options
st.sidebar.title("Navigation")
page = st.sidebar.radio("Go to", ["Analyze Conversation", "Sample Results", "About"])

# Function to parse custom conversation format
def parse_custom_conversation(text):
    lines = text.strip().split('\n')
    
    # Initialize variables
    conversation_id = "custom_" + str(int(time.time()))
    category = "Unknown"
    sentiment = "Unknown"
    priority = "Unknown"
    messages = []
    
    # Extract metadata if available
    if len(lines) >= 3 and ":" in lines[0]:
        conversation_id = lines[0].split(':', 1)[1].strip()
        if ":" in lines[1]:
            category = lines[1].split(':', 1)[1].strip()
        if ":" in lines[2] and "|" in lines[2]:
            sentiment_priority = lines[2].split(':', 1)[1].strip()
            sentiment = sentiment_priority.split('|')[0].strip()
            priority = sentiment_priority.split('|')[1].strip()
        
        # Start parsing messages from line 3
        start_line = 3
    else:
        # If no metadata, start parsing messages from line 0
        start_line = 0
    
    # Parse messages
    timestamp_base = "2023-07-15 "
    hour = 10
    minute = 0
    
    for i in range(start_line, len(lines)):
        line = lines[i].strip()
        if not line:
            continue
            
        # Try to extract sender and content
        match = re.match(r"(.*?)[\s]*:[\s]*(.*)", line)
        
        if match:
            sender = match.group(1).strip()
            content = match.group(2).strip().strip('"')
            
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

# Function to display conversation
def display_conversation(conversation):
    st.subheader("Conversation")
    
    # Display metadata
    col1, col2, col3 = st.columns(3)
    with col1:
        st.metric("Conversation ID", conversation.get("conversation_id", "Unknown"))
    with col2:
        st.metric("Category", conversation.get("category", "Unknown"))
    with col3:
        st.metric("Priority", conversation.get("priority", "Unknown"))
    
    # Display messages
    messages = conversation.get("messages", [])
    for msg in messages:
        sender = msg.get("sender", "Unknown")
        content = msg.get("content", "")
        timestamp = msg.get("timestamp", "")
        
        if sender.lower() == "customer" or sender.lower() == "user":
            st.markdown(f"""
            <div style='background-color: #f0f2f6; padding: 10px; border-radius: 10px; margin-bottom: 10px;'>
                <strong>{sender}</strong> <span style='color: gray; font-size: small;'>({timestamp})</span><br>
                {content}
            </div>
            """, unsafe_allow_html=True)
        else:
            st.markdown(f"""
            <div style='background-color: #e1f5fe; padding: 10px; border-radius: 10px; margin-bottom: 10px;'>
                <strong>{sender}</strong> <span style='color: gray; font-size: small;'>({timestamp})</span><br>
                {content}
            </div>
            """, unsafe_allow_html=True)

# Function to display analysis results
def display_results(results):
    st.subheader("Analysis Results")
    
    # Create tabs for different result sections
    tabs = st.tabs(["Summary", "Sentiment", "Actions", "Routing", "Recommendations", "Time Prediction"])
    
    # Summary tab
    with tabs[0]:
        st.markdown("### Conversation Summary")
        st.info(results.get("summary", "No summary available"))
        
        # Processing time
        processing_time = results.get("processing_time", {})
        if processing_time:
            st.markdown("#### Processing Time")
            steps = processing_time.get("steps", {})
            if steps:
                df = pd.DataFrame({
                    "Step": list(steps.keys()),
                    "Time (seconds)": list(steps.values())
                })
                st.bar_chart(df.set_index("Step"))
            
            total_time = processing_time.get("total", 0)
            st.metric("Total Processing Time", f"{total_time:.2f} seconds")
    
    # Sentiment tab
    with tabs[1]:
        st.markdown("### Sentiment Analysis")
        sentiment = results.get("sentiment_analysis", {})
        
        if sentiment:
            overall = sentiment.get("overall_sentiment", {})
            if overall:
                sentiment_score = overall.get("score", 0)
                sentiment_label = overall.get("sentiment", "neutral")
                
                # Display sentiment gauge
                fig, ax = plt.subplots(figsize=(10, 2))
                ax.barh([0], [sentiment_score], color='green' if sentiment_score > 0 else 'red' if sentiment_score < 0 else 'gray')
                ax.set_xlim(-1, 1)
                ax.set_yticks([])
                ax.set_xlabel("Negative ← Neutral → Positive")
                ax.axvline(x=0, color='black', linestyle='-', alpha=0.3)
                st.pyplot(fig)
                
                st.metric("Overall Sentiment", sentiment_label, f"Score: {sentiment_score}")
            
            # Sentiment progression
            progression = sentiment.get("progression", [])
            if progression:
                st.markdown("#### Sentiment Progression")
                df = pd.DataFrame(progression)
                st.line_chart(df.set_index("timestamp")["score"])
    
    # Actions tab
    with tabs[2]:
        st.markdown("### Action Items")
        actions = results.get("actions", {})
        
        if actions:
            action_items = actions.get("action_items", [])
            if action_items:
                # Group actions by priority
                high_priority = []
                medium_priority = []
                low_priority = []
                
                for item in action_items:
                    action = item.get("action", "")
                    priority = item.get("priority", "Low")
                    status = item.get("status", "Pending")
                    
                    if priority == "High":
                        high_priority.append((action, status))
                    elif priority == "Medium":
                        medium_priority.append((action, status))
                    else:
                        low_priority.append((action, status))
                
                # Display actions by priority
                col1, col2, col3 = st.columns(3)
                
                with col1:
                    st.markdown("#### High Priority")
                    for action, status in high_priority:
                        st.markdown(f"- **{action}** ({status})")
                
                with col2:
                    st.markdown("#### Medium Priority")
                    for action, status in medium_priority:
                        st.markdown(f"- **{action}** ({status})")
                
                with col3:
                    st.markdown("#### Low Priority")
                    for action, status in low_priority:
                        st.markdown(f"- **{action}** ({status})")
            
            total_actions = actions.get("total_actions", 0)
            st.metric("Total Actions", total_actions)
    
    # Routing tab
    with tabs[3]:
        st.markdown("### Ticket Routing")
        routing = results.get("routing", {})
        
        if routing:
            team = routing.get("recommended_team", "Unknown")
            confidence = routing.get("confidence", "Low")
            justification = routing.get("justification", "")
            
            st.info(f"Recommended Team: **{team}** (Confidence: {confidence})")
            st.markdown("#### Justification")
            st.write(justification)
            
            # Show similar conversations for reference
            similar = results.get("similar_conversations", [])
            if similar:
                st.markdown("#### Similar Conversations")
                for i, conv in enumerate(similar[:3]):  # Show top 3
                    with st.expander(f"Similar Conversation {i+1} (Similarity: {conv.get('similarity', 0):.2f})"):
                        st.write(conv.get("text", "No text available"))
    
    # Recommendations tab
    with tabs[4]:
        st.markdown("### Resolution Recommendations")
        recommendations = results.get("recommendations", {})
        
        if recommendations:
            immediate_steps = recommendations.get("immediate_steps", [])
            complete_path = recommendations.get("complete_resolution_path", [])
            reasoning = recommendations.get("reasoning", "")
            confidence = recommendations.get("confidence_score", 0)
            
            col1, col2 = st.columns(2)
            
            with col1:
                st.markdown("#### Immediate Steps")
                for step in immediate_steps:
                    if isinstance(step, dict):
                        action = step.get("action", "")
                        details = step.get("details", "")
                        st.markdown(f"- **{action}**")
                        if details:
                            st.markdown(f"  - {details}")
                    else:
                        st.markdown(f"- {step}")
            
            with col2:
                st.markdown("#### Complete Resolution Path")
                for step in complete_path:
                    if isinstance(step, dict):
                        action = step.get("action", "")
                        details = step.get("details", "")
                        st.markdown(f"- **{action}**")
                        if details:
                            st.markdown(f"  - {details}")
                    else:
                        st.markdown(f"- {step}")
            
            st.markdown("#### Reasoning")
            st.write(reasoning)
            st.metric("Confidence Score", f"{confidence:.2f}")
    
    # Time Prediction tab
    with tabs[5]:
        st.markdown("### Resolution Time Prediction")
        time_prediction = results.get("time_prediction", {})
        
        if time_prediction:
            category = time_prediction.get("resolution_time_category", "unknown")
            estimated_time = time_prediction.get("estimated_time", "unknown")
            explanation = time_prediction.get("explanation", "")
            
            st.info(f"Estimated Resolution Time: **{estimated_time}** (Category: {category})")
            st.markdown("#### Explanation")
            st.write(explanation)

# Page: Analyze Conversation
if page == "Analyze Conversation":
    st.header("Analyze a Conversation")
    
    # Choose input method
    input_method = st.radio("Choose input method", ["Sample Conversations", "Upload File", "Paste Text"])
    
    if input_method == "Sample Conversations":
        # Sample conversations from the data module
        sample_options = ["billing_issue", "technical_issue", "password_reset"]
        selected_sample = st.selectbox("Select a sample conversation", sample_options)
        
        if st.button("Analyze Sample"):
            with st.spinner("Processing conversation..."):
                # Import the get_conversation function
                from data.sample_conversations import get_conversation
                
                # Get the selected conversation
                conversation = get_conversation(selected_sample)
                
                if conversation:
                    # Display the conversation
                    display_conversation(conversation)
                    
                    # Process the conversation
                    results = system.process_conversation(conversation, verbose=False)
                    
                    # Display the results
                    display_results(results)
                else:
                    st.error("Could not load the selected conversation.")
    
    elif input_method == "Upload File":
        uploaded_file = st.file_uploader("Upload a conversation file", type=["txt", "json"])
        
        if uploaded_file is not None:
            # Read the file
            content = uploaded_file.read().decode()
            
            # Determine the file type
            if uploaded_file.name.endswith(".json"):
                try:
                    # Parse as JSON
                    conversation = json.loads(content)
                    st.success("JSON file loaded successfully.")
                except json.JSONDecodeError:
                    st.error("Invalid JSON file. Please upload a valid JSON conversation file.")
                    conversation = None
            else:
                # Parse as text format
                conversation = parse_custom_conversation(content)
                st.success("Text file parsed successfully.")
            
            if conversation and st.button("Analyze Conversation"):
                with st.spinner("Processing conversation..."):
                    # Display the conversation
                    display_conversation(conversation)
                    
                    # Process the conversation
                    results = system.process_conversation(conversation, verbose=False)
                    
                    # Display the results
                    display_results(results)
    
    elif input_method == "Paste Text":
        conversation_text = st.text_area("Paste conversation text here", height=300, 
                                        placeholder="Conversation ID: TECH_001\nCategory: Technical Support\nSentiment: Frustrated | Priority: High\nCustomer: \"Hi there! I've been trying to install the latest update...\"\nAgent: \"Hello! Thank you for reaching out...\"")
        
        if conversation_text and st.button("Analyze Text"):
            with st.spinner("Processing conversation..."):
                # Parse the text
                conversation = parse_custom_conversation(conversation_text)
                
                # Display the conversation
                display_conversation(conversation)
                
                # Process the conversation
                results = system.process_conversation(conversation, verbose=False)
                
                # Display the results
                display_results(results)

# Page: Sample Results
elif page == "Sample Results":
    st.header("Sample Analysis Results")
    
    # Get a list of result files
    results_dir = "results"
    if os.path.exists(results_dir):
        result_files = [f for f in os.listdir(results_dir) if f.endswith(".json")]
        
        if result_files:
            selected_file = st.selectbox("Select a result file", result_files)
            
            if selected_file:
                file_path = os.path.join(results_dir, selected_file)
                
                try:
                    with open(file_path, "r") as f:
                        results = json.load(f)
                    
                    # Get the conversation ID
                    conversation_id = results.get("conversation_id", "Unknown")
                    
                    # Find and load the conversation
                    conversation = None
                    
                    # Display the results
                    display_results(results)
                except Exception as e:
                    st.error(f"Error loading results: {e}")
        else:
            st.info("No result files found in the 'results' directory.")
    else:
        st.info("The 'results' directory does not exist.")

# Page: About
elif page == "About":
    st.header("About Customer Support AI")
    
    st.markdown("""
    ## Multi-Agent AI System for Customer Support

    A comprehensive AI system that automates key processes in customer support operations through multiple specialized agents. This system uses Ollama for local LLM processing, eliminating the need for external API services.

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
    - **Local Knowledge Base**: Provides relevant articles for customer issues
    - **Sentiment Analysis**: Analyzes customer sentiment throughout conversations

    ### Processing Pipeline

    1. Store conversation in database
    2. Analyze customer sentiment
    3. Generate conversation summary
    4. Extract action items
    5. Fetch relevant knowledge articles
    6. Determine ticket routing
    7. Generate conversation embeddings for similarity search
    8. Recommend resolution steps
    9. Predict resolution time
    """)

# Add footer
st.markdown("---")
st.markdown("Customer Support AI Dashboard • Built with Streamlit") 