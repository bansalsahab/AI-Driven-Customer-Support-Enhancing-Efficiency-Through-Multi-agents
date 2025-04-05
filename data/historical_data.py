"""Sample historical support data for resolution recommendations and time predictions"""

import pandas as pd
from datetime import datetime, timedelta
import random
import json
import os

def generate_historical_data(num_samples=1000):
    """
    Generate synthetic historical support data
    
    Args:
        num_samples: Number of historical records to generate
        
    Returns:
        DataFrame with historical support data
    """
    # Define possible values for categorical fields
    issue_types = [
        "Login Problem", "Password Reset", "Account Access", "Billing Issue", 
        "Refund Request", "Subscription Cancellation", "Technical Error",
        "Feature Request", "Bug Report", "Product Question", "Service Outage",
        "Mobile App Issue", "Browser Compatibility", "Data Migration", "API Error"
    ]
    
    teams = [
        "Technical Support", "Billing Support", "Account Management", 
        "Product Support", "Security Team", "Escalations Team", "General Support"
    ]
    
    statuses = ["Resolved", "Pending", "Escalated", "Closed", "Reopened"]
    
    priorities = ["Low", "Medium", "High", "Critical"]
    
    customer_types = ["Free", "Basic", "Premium", "Enterprise"]
    
    # Generate random data
    data = {
        "ticket_id": [f"TICK-{i+1000}" for i in range(num_samples)],
        "issue_type": [random.choice(issue_types) for _ in range(num_samples)],
        "assigned_team": [random.choice(teams) for _ in range(num_samples)],
        "status": [random.choice(statuses) for _ in range(num_samples)],
        "priority": [random.choice(priorities) for _ in range(num_samples)],
        "customer_type": [random.choice(customer_types) for _ in range(num_samples)],
        "first_response_time_minutes": [random.randint(1, 120) for _ in range(num_samples)],
        "resolution_time_hours": [random.randint(1, 72) for _ in range(num_samples)],
        "customer_satisfaction": [random.randint(1, 5) for _ in range(num_samples)],
        "created_date": [(datetime.now() - timedelta(days=random.randint(1, 180))).strftime("%Y-%m-%d") for _ in range(num_samples)]
    }
    
    # Add resolution details (simplified for demo)
    resolution_templates = {
        "Login Problem": ["Reset user password", "Cleared browser cache", "Updated user credentials"],
        "Password Reset": ["Sent password reset link", "Reset password manually", "Verified security questions"],
        "Billing Issue": ["Processed refund", "Corrected billing information", "Applied account credit"],
        "Technical Error": ["Applied software patch", "Cleared user data cache", "Reinstalled application"]
    }
    
    resolutions = []
    for issue in data["issue_type"]:
        # Get templates for this issue type or use a default template
        templates = resolution_templates.get(issue, ["Issue investigated and resolved", "Applied standard fix"])
        resolutions.append(random.choice(templates))
    
    data["resolution_details"] = resolutions
    
    # Create DataFrame
    df = pd.DataFrame(data)
    
    # Add some correlations to make the data more realistic
    # Higher priority usually means faster response
    for i, priority in enumerate(df["priority"]):
        if priority == "Critical":
            df.at[i, "first_response_time_minutes"] = random.randint(1, 30)
        elif priority == "High":
            df.at[i, "first_response_time_minutes"] = random.randint(15, 60)
    
    # Technical issues often take longer to resolve
    for i, issue_type in enumerate(df["issue_type"]):
        if "Technical" in issue_type or "Bug" in issue_type:
            df.at[i, "resolution_time_hours"] = random.randint(4, 72)
        elif "Password" in issue_type or "Login" in issue_type:
            df.at[i, "resolution_time_hours"] = random.randint(1, 4)
    
    return df

def save_historical_data(output_path="historical_support_data.csv", num_samples=1000):
    """Generate and save historical data to CSV file"""
    df = generate_historical_data(num_samples)
    
    # Create directory if it doesn't exist
    os.makedirs(os.path.dirname(os.path.abspath(output_path)), exist_ok=True)
    
    # Save to CSV
    df.to_csv(output_path, index=False)
    print(f"Saved {num_samples} historical support records to {output_path}")
    return output_path

def get_similar_issues(issue_type, num_samples=5):
    """
    Get sample historical data for similar issues
    
    Args:
        issue_type: Type of issue to find similar records for
        num_samples: Number of similar records to return
        
    Returns:
        DataFrame with similar historical issues
    """
    df = generate_historical_data(100)  # Generate some random data
    
    # Filter for similar issues (simplistic approach for demo)
    similar = df[df["issue_type"] == issue_type]
    
    # If no exact matches, get random samples
    if len(similar) < num_samples:
        return df.sample(num_samples)
    
    return similar.head(num_samples)

if __name__ == "__main__":
    # Generate and save sample historical data when run directly
    save_historical_data("../data/historical_support_data.csv", 100) 