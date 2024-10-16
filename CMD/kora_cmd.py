import requests

# Command details
__author__ = "Suleiman"
__name__ = "Kora"
__description__ = "Get response from Kora AI"

def handle_command(query):
    """Fetch a response from Kora AI based on the user query."""
    
    # URL for Kora AI with dynamic query input
    Sman_Url = f"https://kora-ai-sh1p.onrender.com/koraai?query={query}"
    
    # Send a GET request to Kora AI
    try:
        response = requests.get(Sman_Url)
        
        # Check if the request was successful
        if response.status_code == 200:
            return f"Kora 😎: {response.text}"
        else:
            return "Kora is currently unavailable. Please try again later."
    
    except Exception as e:
        return f"An error occurred while connecting to Kora: {str(e)}"
