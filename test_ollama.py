import requests
import json

def test_ollama_connection():
    """Test if Ollama is running and accessible"""
    try:
        # Test the generate endpoint
        response = requests.post(
            "http://localhost:11434/api/generate",
            json={
                "model": "llama2",
                "prompt": "Hello, how are you?",
                "stream": False
            }
        )
        response.raise_for_status()
        print("Ollama generate endpoint is working!")
        print("Response:", response.json())
        
        # Test the embeddings endpoint
        response = requests.post(
            "http://localhost:11434/api/embeddings",
            json={
                "model": "llama2",
                "prompt": "Test text for embeddings"
            }
        )
        response.raise_for_status()
        print("\nOllama embeddings endpoint is working!")
        print("Response:", response.json())
        
        return True
        
    except requests.exceptions.ConnectionError:
        print("Error: Could not connect to Ollama. Make sure it's running with 'ollama serve'")
        return False
    except requests.exceptions.RequestException as e:
        print(f"Error: {e}")
        return False

if __name__ == "__main__":
    print("Testing Ollama connection...")
    test_ollama_connection() 