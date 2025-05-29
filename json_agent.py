from llm_wrapper import llm_wrapper
from memory_module import shared_memory
import json

class JSONAgent:
    def __init__(self):
        self.llm = llm_wrapper
        self.memory = shared_memory

    def process_json(self, json_payload: str, thread_id: str):
        """
        Accepts JSON, extracts/reformats to a target schema, and flags anomalies.
        """
        try:
            data = json.loads(json_payload)
        except json.JSONDecodeError:
            print("JSON Agent: Invalid JSON payload.")
            self.memory.log_interaction(
                source="JSONAgent",
                input_type="JSON",
                intent="Error",
                extracted_values={"error": "Invalid JSON format"},
                thread_id=thread_id
            )
            return {"status": "error", "message": "Invalid JSON format"}

        # Define a target schema (example for an Invoice)
        # In a real system, this could be loaded from a configuration or dynamically determined.
        target_schema = {
            "invoice_number": None,
            "customer_name": None,
            "total_amount": None,
            "currency": None,
            "date_issued": None,
            "line_items": [] # Example for nested data
        }

        # Use LLM for extraction and reformatting
        system_prompt = f"""You are a JSON processing agent. Your task is to extract information from the provided JSON payload and reformat it according to the target schema.
        If a field is missing or an anomaly is detected (e.g., incorrect data type), note it.
        Return the output as a JSON object matching the target schema, with extracted values.
        Target Schema (example - adjust based on actual intent):
        ```json
        {json.dumps(target_schema, indent=2)}
        ```
        """
        user_prompt = f"Process the following JSON data:\n\n{json.dumps(data, indent=2)}"

        extracted_json_str = self.llm.generate_response(system_prompt, user_prompt, json_mode=True)
        
        if extracted_json_str:
            try:
                extracted_data = json.loads(extracted_json_str)
            except json.JSONDecodeError as e:
                print(f"JSON Agent: LLM returned invalid JSON: {e}")
                extracted_data = {"status": "error", "message": "LLM output invalid JSON"}
        else:
            extracted_data = {"status": "error", "message": "LLM extraction failed"}

        # Basic anomaly detection and flagging missing fields
        anomalies = []
        missing_fields = []
        
        for key, value in target_schema.items():
            if key not in extracted_data or extracted_data[key] is None:
                missing_fields.append(key)
            # Add more sophisticated anomaly checks here (e.g., type validation, range checks)
            
        if missing_fields:
            anomalies.append(f"Missing required fields: {', '.join(missing_fields)}")

        if anomalies:
            extracted_data["anomalies"] = anomalies
        
        # Log extracted data and anomalies
        self.memory.log_interaction(
            source="JSONAgent",
            input_type="JSON",
            intent="Processed JSON",
            extracted_values=extracted_data,
            thread_id=thread_id
        )
        
        print(f"JSON Agent: Processed JSON. Anomalies: {anomalies}")
        return extracted_data