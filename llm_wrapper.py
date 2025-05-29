import os
from dotenv import load_dotenv
import google.generativeai as genai # Import the Google Gemini library
import json # Import json for parsing/dumping if needed

load_dotenv() # Load environment variables from .env file

class LLMWrapper:
    def __init__(self, model="gemini-1.5-flash"): # Default to a robust and often free-tier friendly model
        self.model = os.getenv("GEMINI_MODEL", model) # Allow model to be overridden by env var
        
        # Configure the Google Generative AI client with your API key
        genai.configure(api_key=os.getenv("GOOGLE_API_KEY"))
        
        # Initialize the GenerativeModel instance
        self.client = genai.GenerativeModel(self.model)

    def generate_response(self, system_prompt: str, user_prompt: str, json_mode: bool = False):
        # Gemini's API typically handles system prompts by prepending them to the user prompt,
        # or by using specific roles in a chat history. For a single turn, prepending is common.
        full_prompt = f"{system_prompt}\n\n{user_prompt}"
        
        generation_config = {
            "temperature": 0.0, # Keep temperature low for deterministic tasks like classification/extraction
            "max_output_tokens": 2000, # Set a reasonable maximum output length
        }
        
        # Gemini does not have a direct 'response_format={"type": "json_object"}' parameter
        # like OpenAI. We instruct it in the prompt and then parse the output.
        if json_mode:
            full_prompt += "\nYour response MUST be a valid JSON object."
            # Optionally, you can add a hint to start the JSON block
            # full_prompt += "\n```json\n" # This can sometimes help the model output valid markdown JSON

        try:
            # Call the Gemini API to generate content
            response = self.client.generate_content(
                full_prompt,
                generation_config=generation_config
            )
            
            # Access the generated text from the response object
            content = response.text
            
            # If JSON mode was requested, attempt to parse the content
            if json_mode:
                try:
                    # Models often wrap JSON in markdown blocks, so try to strip them
                    if content.strip().startswith("```json"):
                        content = content.strip()[len("```json"):].strip()
                        if content.endswith("```"):
                            content = content[:-len("```")].strip()
                    elif content.strip().startswith("```"): # Generic markdown block
                        content = content.strip()[len("```"):].strip()
                        if content.endswith("```"):
                            content = content[:-len("```")].strip()
                            
                    # Attempt to load the JSON content
                    return json.dumps(json.loads(content)) # Ensure it's valid JSON, return as string
                except json.JSONDecodeError as e:
                    print(f"Warning: LLM did not return valid JSON despite instruction. Error: {e}. Content: {content[:500]}...")
                    # Fallback: if JSON parsing fails, return raw content; calling agent might handle or log error
                    return content 
            
            return content

        except Exception as e:
            # Catch specific Gemini API errors, like safety settings blocks
            if hasattr(e, 'response') and hasattr(e.response, 'prompt_feedback'):
                print(f"LLM Response blocked by safety settings: {e.response.prompt_feedback}")
            print(f"Error generating LLM response with Google Gemini: {e}")
            return None

# Re-instantiate the global LLM wrapper with the new client
llm_wrapper = LLMWrapper()