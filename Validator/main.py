import os
from typing import Dict
import groq
import json
from dotenv import load_dotenv
import logging
import re

# Load environment variables
load_dotenv()

# Configure logging
logging.basicConfig(level=logging.INFO)

class ScamDetector:
    def __init__(self, api_key: str):
        """Initialize the ScamDetector with Groq API key."""
        self.client = groq.Client(api_key=api_key)
        
    def analyze_text(self, text: str) -> Dict:
        """
        Analyze text for potential scam indicators.
        
        Args:
            text (str): The text to analyze
            
        Returns:
            Dict containing classification results and confidence score
        """
        # Construct our prompt
        prompt = f"""Analyze the following text and determine if it shows signs of being a scam. 
        Consider common scam indicators like:
        - Urgency or pressure tactics
        - Requests for sensitive information
        - Unrealistic promises or rewards
        - Poor grammar or spelling
        - Suspicious links or contacts
        
        Text to analyze: "{text}"
        
        Provide your analysis in the following JSON format:
        {{
            "is_scam": true/false,
            "confidence": 0-100,
            "indicators": ["list", "of", "suspicious", "elements"],
            "explanation": "Brief explanation of classification"
        }}
        """
        
        # Call Groq API
        try:
            response = self.client.chat.completions.create(
                messages=[
                    {
                        "role": "system",
                        "content": "You are a scam detection expert. Analyze text for scam indicators and respond in JSON format."
                    },
                    {
                        "role": "user",
                        "content": prompt
                    }
                ],
                model="llama-3.1-8b-instant",
                temperature=0.1,
                max_tokens=1000
            )
            
            # Log the raw response for debugging
            logging.info(f"Raw API response: {response}")
            
            # Extract JSON content from the response
            if response.choices and response.choices[0].message.content:
                content = response.choices[0].message.content
                
                # Use regex to extract the JSON block from the Markdown
                json_match = re.search(r'```json\s*({.*?})\s*```', content, re.DOTALL)
                if json_match:
                    json_str = json_match.group(1)
                    result = json.loads(json_str)
                    return result
                else:
                    return {
                        "error": "No valid JSON found in API response",
                        "is_scam": None,
                        "confidence": 0,
                        "indicators": [],
                        "explanation": "Unable to extract JSON from response"
                    }
            else:
                return {
                    "error": "Empty or invalid response from API",
                    "is_scam": None,
                    "confidence": 0,
                    "indicators": [],
                    "explanation": "Unable to complete analysis"
                }
            
        except json.JSONDecodeError as e:
            logging.error(f"JSON decode error: {e}")
            return {
                "error": f"JSON decode error: {str(e)}",
                "is_scam": None,
                "confidence": 0,
                "indicators": [],
                "explanation": "Unable to parse API response"
            }
        except Exception as e:
            logging.error(f"API call failed: {e}")
            return {
                "error": f"Analysis failed: {str(e)}",
                "is_scam": None,
                "confidence": 0,
                "indicators": [],
                "explanation": "Unable to complete analysis"
            }

def main():
    # Example usage
    api_key = os.getenv("GROQ_API_KEY")
    if not api_key:
        raise ValueError("Please set GROQ_API_KEY environment variable")
        
    detector = ScamDetector(api_key)
    
    # Example text to analyze
    sample_text = """URGENT: Your account has been compromised! 
    Click here immediately to verify your details: http://suspicious-link.com
    You must act within 24 hours or your account will be permanently closed."""
    
    result = detector.analyze_text(sample_text)
    print(json.dumps(result, indent=2))

if __name__ == "__main__":
    main()