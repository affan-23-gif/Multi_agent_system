from llm_wrapper import llm_wrapper
from memory_module import shared_memory
import json
import re # For basic email/JSON detection
from pypdf import PdfReader # For PDF detection
import os

class ClassifierAgent:
    def __init__(self):
        self.llm = llm_wrapper
        self.memory = shared_memory

    def classify(self, raw_input: str, thread_id: str = None):
        """
        Classifies the format and intent of the raw input.
        """
        # Step 1: Detect Format Heuristically first for efficiency
        input_format = self._detect_format(raw_input)
        
        # Step 2: Use LLM for Intent Classification
        system_prompt = f"""You are an intelligent classification agent. Your task is to accurately identify the intent of the user's input.
        Possible intents include: Invoice, RFQ (Request for Quote), Complaint, Regulation, General Inquiry, Other.
        Respond ONLY with the identified intent word."""

        user_prompt = f"Given the following content, what is its primary intent?\n\nContent: {raw_input[:1000]}..." # Limit input length for LLM

        intent = self.llm.generate_response(system_prompt, user_prompt)
        
        if intent:
            intent = intent.strip().replace('.', '') # Clean up LLM output

        # Step 3: Log in Shared Memory
        thread_id = self.memory.log_interaction(
            source="ClassifierAgent",
            input_type=input_format,
            intent=intent if intent else "Unknown",
            extracted_values={"format": input_format, "intent": intent},
            thread_id=thread_id
        )
        
        print(f"Classifier: Detected Format: {input_format}, Intent: {intent}")
        return input_format, intent, thread_id

    def _detect_format(self, raw_input: str) -> str:
        """
        Heuristically detects the input format (PDF, JSON, Email, Text).
        This is a pre-processing step before LLM classification for efficiency.
        """
        # Check for PDF by trying to read it (basic check)
        # This is a very basic check. A robust system would require file upload handling
        # For this exercise, assume raw_input might be a path to a PDF file or its content.
        # If it's the content, then it's trickier to detect without magic bytes.
        # For simplicity, we'll assume the input is the actual content for now,
        # but a real system would take a file object/path.
        
        # If raw_input is a path:
        if isinstance(raw_input, str) and os.path.exists(raw_input) and raw_input.lower().endswith('.pdf'):
            try:
                reader = PdfReader(raw_input)
                if len(reader.pages) > 0:
                    return "PDF"
            except Exception:
                pass # Not a valid PDF or corrupted

        # Check for JSON structure
        try:
            json.loads(raw_input)
            return "JSON"
        except json.JSONDecodeError:
            pass

        # Check for common email headers (From:, To:, Subject:)
        if re.search(r"^(From:|To:|Subject:|Date:)", raw_input, re.MULTILINE | re.IGNORECASE):
            return "Email"
        
        # Default to Text if none of the above
        return "Text"