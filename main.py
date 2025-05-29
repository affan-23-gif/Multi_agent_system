from classifier_agent import ClassifierAgent
from json_agent import JSONAgent
from email_agent import EmailAgent
from memory_module import shared_memory, SharedMemory # Import SharedMemory class for reset
import json # Make sure json is imported for printing results

class MultiAgentSystem:
    def __init__(self):
        self.classifier_agent = ClassifierAgent()
        self.json_agent = JSONAgent()
        self.email_agent = EmailAgent()
        self.memory = shared_memory

    def process_input(self, raw_input_content: str, thread_id: str = None):
        """
        Main entry point for processing input.
        """
        print("\n--- Starting New Input Processing ---")
        
        # Step 1: Classify Format and Intent
        input_format, intent, current_thread_id = self.classifier_agent.classify(raw_input_content, thread_id)
        
        # The ClassifierAgent's classify method already logs and returns the thread_id.
        # We should use this current_thread_id for further processing and return it.
        
        print(f"Routing to agent based on Format: {input_format}, Intent: {intent}")

        result_data = {} # Initialize a dictionary to hold the agent's result

        # Step 2: Route to appropriate Agent
        if input_format == "JSON":
            if intent and "invoice" in intent.lower():
                print("JSON Agent: Processing as potential Invoice JSON.")
            result_data = self.json_agent.process_json(raw_input_content, current_thread_id)
        elif input_format == "Email" or \
             (input_format == "Text" and intent is not None and ("email" in intent.lower() or "rfq" in intent.lower() or "complaint" in intent.lower() or "inquiry" in intent.lower())):
            print("Email Agent: Processing email/text content.")
            result_data = self.email_agent.process_email(raw_input_content, current_thread_id)
        # in main.py's process_input
# ...
        elif input_format == "PDF":
            print("PDF Agent: Processing PDF content.")
            # You'd pass the actual PDF file path or binary content here
            # For testing, you'd need a sample PDF file
            # For now, let's just use the placeholder as before, but note the change
            # This will still likely fail if pdf_input is not a real PDF file path/content
            # You would change the test case in __main__ to pass a valid PDF file.
            result_data = self.pdf_agent.process_pdf(raw_input_content, current_thread_id)
        # ...
        else: 
            print(f"No specific agent for format: {input_format} and intent: {intent}. Attempting generic processing if needed or re-evaluating.")
            self.memory.log_interaction(
                source="MultiAgentSystem",
                input_type=input_format,
                intent=intent if intent else "Unhandled",
                extracted_values={"message": f"No specific agent for {input_format}/{intent}"},
                thread_id=current_thread_id # Use the thread_id from classifier
            )
            result_data = {"status": "error", "message": "Unhandled format or intent"}
        
        # Append the thread_id to the result data for easy access in the test cases
        # This makes it easier to get the thread_id from the returned result.
        result_data["thread_id"] = current_thread_id 
        return result_data

# --- Example Usage ---
if __name__ == "__main__":
    system = MultiAgentSystem()
    
    # --- Test Case 1: Email RFQ ---
    print("\n--- Running Test Case 1: Email RFQ ---")
    email_rfq_content = """
    From: customer@example.com
    To: sales@yourcompany.com
    Subject: Urgent RFQ for Widgets

    Dear Sales Team,

    We are urgently looking for a quote on 500 units of your Model X widgets.
    Please provide your best price and lead time by end of day tomorrow.
    We are a new client and hope to build a long-term relationship.

    Thanks,
    John Doe
    Procurement Manager
    """
    email_result = system.process_input(email_rfq_content)
    print("\nEmail Agent Result:")
    print(json.dumps(email_result, indent=2))
    
    # Now, retrieve the thread_id directly from the returned result
    email_thread_id = email_result.get('thread_id')
    if email_thread_id:
        print(f"\nContext for Email Thread ({email_thread_id}):")
        print(json.dumps(shared_memory.get_context(email_thread_id), indent=2))
        print(f"\nLast Extracted Fields for Email Thread ({email_thread_id}):")
        print(json.dumps(shared_memory.get_last_extracted_fields(email_thread_id), indent=2))


    # --- Test Case 2: JSON Invoice ---
    print("\n--- Running Test Case 2: JSON Invoice ---")
    json_invoice_content = """
    {
      "document_type": "invoice",
      "invoice_data": {
        "invoice_number": "INV-2023-001",
        "customer_info": {
          "name": "Acme Corp",
          "address": "123 Main St"
        },
        "amount_due": 1250.75,
        "currency_code": "USD",
        "issue_date": "2023-10-26",
        "items": [
          {"description": "Product A", "quantity": 10, "unit_price": 100.00},
          {"description": "Service Fee", "quantity": 1, "unit_price": 250.75}
        ]
      }
    }
    """
    json_result = system.process_input(json_invoice_content)
    print("\nJSON Agent Result:")
    print(json.dumps(json_result, indent=2))
    
    # Retrieve the thread_id directly from the returned result
    json_thread_id = json_result.get('thread_id')
    if json_thread_id:
        print(f"\nContext for JSON Thread ({json_thread_id}):")
        print(json.dumps(shared_memory.get_context(json_thread_id), indent=2))
        print(f"\nLast Extracted Fields for JSON Thread ({json_thread_id}):")
        print(json.dumps(shared_memory.get_last_extracted_fields(json_thread_id), indent=2))


    # --- Test Case 3: Chaining (Complaint Email) ---
    print("\n--- Running Test Case 3: Chaining (Complaint Email) ---")
    complaint_email_content = """
    From: customer@example.com
    To: sales@yourcompany.com
    Subject: RE: Urgent RFQ for Widgets - Complaint Regarding Delay

    Dear Sales Team,

    I am writing to express my dissatisfaction with the delay in receiving the quote for Model X widgets.
    This is holding up our project. Please prioritize this.

    Sincerely,
    John Doe
    """
    # Pass the thread_id from the first email interaction to maintain context
    complaint_result = system.process_input(complaint_email_content, thread_id=email_thread_id)
    print("\nComplaint Email Agent Result:")
    print(json.dumps(complaint_result, indent=2))

    # Check the updated context for the chained interaction
    if email_thread_id:
        print(f"\nUpdated Context for Email Thread ({email_thread_id}) after Complaint:")
        print(json.dumps(shared_memory.get_context(email_thread_id), indent=2))
        print(f"\nLast Extracted Fields from Email Thread ({email_thread_id}):")
        print(json.dumps(shared_memory.get_last_extracted_fields(email_thread_id), indent=2))

    # --- Test Case 4: Unhandled Format (Simulated PDF Content - will be classified as Text) ---
    print("\n--- Running Test Case 4: Unhandled Format (PDF) ---")
    pdf_content_placeholder = "This is placeholder text for a PDF document. In a real scenario, this would be binary PDF data."
    pdf_result = system.process_input(pdf_content_placeholder)
    print("\nPDF Processing Result:")
    print(json.dumps(pdf_result, indent=2))
    
    # --- Test Case 5: General Text Input ---
    print("\n--- Running Test Case 5: General Text Input ---")
    general_text_content = "Can you tell me about your pricing for enterprise solutions?"
    general_text_result = system.process_input(general_text_content)
    print("\nGeneral Text Result:")
    print(json.dumps(general_text_result, indent=2))