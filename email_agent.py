from llm_wrapper import llm_wrapper
from memory_module import shared_memory
import json

class EmailAgent:
    def __init__(self):
        self.llm = llm_wrapper
        self.memory = shared_memory

    def process_email(self, email_content: str, thread_id: str):
        """
        Accepts email content, extracts sender, intent, urgency, and formats for CRM.
        """
        system_prompt = """You are an email processing agent. Your task is to extract key information from the provided email content.
        Extract the sender's name and email, the email's subject, the primary intent (e.g., RFQ, Complaint, Inquiry), and the urgency (Low, Medium, High).
        Format the output as a JSON object with the following keys: 'sender_name', 'sender_email', 'subject', 'extracted_intent', 'urgency', 'summary'.
        For 'summary', provide a concise one-paragraph summary of the email's main content.
        If any field is not explicitly found, use "N/A" for strings or 0 for numbers.
        """
        user_prompt = f"Process the following email:\n\n{email_content}"

        extracted_email_info_str = self.llm.generate_response(system_prompt, user_prompt, json_mode=True)

        if extracted_email_info_str:
            try:
                extracted_email_info = json.loads(extracted_email_info_str)
            except json.JSONDecodeError as e:
                print(f"Email Agent: LLM returned invalid JSON: {e}")
                extracted_email_info = {"status": "error", "message": "LLM output invalid JSON"}
        else:
            extracted_email_info = {"status": "error", "message": "LLM extraction failed"}

        # Basic validation/cleanup (optional, LLM should handle most)
        extracted_email_info['extracted_intent'] = extracted_email_info.get('extracted_intent', 'Unknown').replace('.', '')
        
        # Log extracted data
        self.memory.log_interaction(
            source="EmailAgent",
            input_type="Email",
            intent=extracted_email_info.get('extracted_intent', 'Unknown'),
            extracted_values=extracted_email_info,
            thread_id=thread_id
        )
        
        print(f"Email Agent: Processed email from {extracted_email_info.get('sender_email')}")
        return extracted_email_info