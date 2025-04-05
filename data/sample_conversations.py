"""Sample customer support conversations for testing and demonstration"""

SAMPLE_CONVERSATIONS = {
    "password_reset": {
        "conversation_id": "conv123",
        "messages": [
            {
                "sender": "Customer",
                "content": "Hi, I'm having trouble logging into my account. It keeps saying invalid password even though I'm sure it's correct.",
                "timestamp": "2023-06-15 10:05:32"
            },
            {
                "sender": "Agent",
                "content": "Hello! I'm sorry to hear you're having trouble. Let me help you with that. Can you tell me when you last successfully logged in?",
                "timestamp": "2023-06-15 10:06:45"
            },
            {
                "sender": "Customer",
                "content": "I think it was yesterday. I haven't changed my password recently.",
                "timestamp": "2023-06-15 10:07:23"
            },
            {
                "sender": "Agent",
                "content": "Thank you for that information. Let's try resetting your password. I'll send a password reset link to your registered email address. Is that okay?",
                "timestamp": "2023-06-15 10:08:10"
            },
            {
                "sender": "Customer",
                "content": "Yes, that would be great. Thank you!",
                "timestamp": "2023-06-15 10:08:45"
            },
            {
                "sender": "Agent",
                "content": "You're welcome! I've sent the password reset link. Please check your email and follow the instructions to reset your password. Let me know if you need any further assistance.",
                "timestamp": "2023-06-15 10:09:30"
            },
            {
                "sender": "Customer",
                "content": "Got it. I'll check now.",
                "timestamp": "2023-06-15 10:10:05"
            }
        ]
    },
    
    "billing_issue": {
        "conversation_id": "conv456",
        "messages": [
            {
                "sender": "Customer",
                "content": "Hello, I noticed I was charged twice for my monthly subscription. Can you help me get a refund for the duplicate charge?",
                "timestamp": "2023-06-16 14:12:35"
            },
            {
                "sender": "Agent",
                "content": "I apologize for the inconvenience. Let me check your billing history to verify the duplicate charge. May I have your account email address please?",
                "timestamp": "2023-06-16 14:13:47"
            },
            {
                "sender": "Customer",
                "content": "It's customer@example.com",
                "timestamp": "2023-06-16 14:14:22"
            },
            {
                "sender": "Agent",
                "content": "Thank you. I can see that there was indeed a duplicate charge of $29.99 on June 15th. I'll initiate a refund for this amount right away. The refund should process within 3-5 business days.",
                "timestamp": "2023-06-16 14:16:50"
            },
            {
                "sender": "Customer",
                "content": "That's great, thank you. Do you know why this happened? I want to make sure it doesn't happen again next month.",
                "timestamp": "2023-06-16 14:17:33"
            },
            {
                "sender": "Agent",
                "content": "It appears there was a system glitch during a scheduled maintenance that affected some accounts. We've already fixed the issue, and I'm adding a note to your account to monitor for any similar issues. Rest assured, this shouldn't happen again.",
                "timestamp": "2023-06-16 14:19:21"
            },
            {
                "sender": "Customer",
                "content": "Okay, that's good to know. Thanks for resolving this quickly.",
                "timestamp": "2023-06-16 14:20:05"
            },
            {
                "sender": "Agent",
                "content": "You're welcome! I've sent you an email confirmation of the refund. Is there anything else I can assist you with today?",
                "timestamp": "2023-06-16 14:21:12"
            },
            {
                "sender": "Customer",
                "content": "No, that's all. Have a good day!",
                "timestamp": "2023-06-16 14:21:48"
            },
            {
                "sender": "Agent",
                "content": "Thank you for contacting us. Have a wonderful day!",
                "timestamp": "2023-06-16 14:22:15"
            }
        ]
    },
    
    "technical_issue": {
        "conversation_id": "conv789",
        "messages": [
            {
                "sender": "Customer",
                "content": "Hi there, I'm trying to upload files to my cloud storage, but I keep getting an error saying 'Upload failed: Network error'. I've tried multiple times.",
                "timestamp": "2023-06-17 09:31:22"
            },
            {
                "sender": "Agent",
                "content": "Hello! I'm sorry to hear you're experiencing issues with file uploads. Let's troubleshoot this together. What type of files are you trying to upload, and what browser and device are you using?",
                "timestamp": "2023-06-17 09:32:41"
            },
            {
                "sender": "Customer",
                "content": "I'm trying to upload PDF files, about 5MB each. I'm using Chrome on Windows 10 laptop.",
                "timestamp": "2023-06-17 09:33:28"
            },
            {
                "sender": "Agent",
                "content": "Thank you for that information. Let's try a few things. First, could you clear your browser cache and cookies, then restart your browser and try again?",
                "timestamp": "2023-06-17 09:34:52"
            },
            {
                "sender": "Customer",
                "content": "I just tried that, but I'm still getting the same error.",
                "timestamp": "2023-06-17 09:38:15"
            },
            {
                "sender": "Agent",
                "content": "I see. Let's check if it's a connection issue. Can you try uploading using a different network if possible, like switching from Wi-Fi to mobile hotspot?",
                "timestamp": "2023-06-17 09:39:30"
            },
            {
                "sender": "Customer",
                "content": "I just tried using my phone's hotspot, and it's still not working.",
                "timestamp": "2023-06-17 09:42:18"
            },
            {
                "sender": "Agent",
                "content": "Thank you for trying that. It seems this might be a more complex issue. I'm going to escalate this to our technical team for further investigation. They'll need remote access to diagnose the problem. Would that be okay with you?",
                "timestamp": "2023-06-17 09:43:45"
            },
            {
                "sender": "Customer",
                "content": "Yes, that's fine. When can they help me?",
                "timestamp": "2023-06-17 09:44:20"
            },
            {
                "sender": "Agent",
                "content": "I'll create a high-priority ticket right now. Our technical team will contact you within the next 2 hours via email to schedule a remote session. They'll also run some diagnostics on your account in the meantime.",
                "timestamp": "2023-06-17 09:45:33"
            },
            {
                "sender": "Customer",
                "content": "Great, thank you. I'll wait for their email.",
                "timestamp": "2023-06-17 09:46:10"
            }
        ]
    }
}

def get_conversation(conversation_id: str):
    """Get a sample conversation by ID"""
    for conv_id, conversation in SAMPLE_CONVERSATIONS.items():
        if conv_id == conversation_id or conversation.get("conversation_id") == conversation_id:
            return conversation
    return None

def get_all_conversations():
    """Get all sample conversations"""
    return SAMPLE_CONVERSATIONS 