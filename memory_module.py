import uuid
import datetime
import json

class SharedMemory:
    def __init__(self):
        self.data = {} # Using a dictionary for in-memory storage. Keyed by thread_id or conversation_id

    def log_interaction(self, source: str, input_type: str, intent: str, extracted_values: dict, thread_id: str = None):
        """
        Logs an interaction, creating a new thread_id if not provided.
        """
        if thread_id is None:
            thread_id = str(uuid.uuid4()) # Generate a unique ID for new conversations

        timestamp = datetime.datetime.now().isoformat()
        
        # Ensure extracted_values is JSON serializable
        try:
            json.dumps(extracted_values)
        except TypeError:
            # Handle cases where extracted_values might contain non-serializable objects
            # For simplicity, we'll just stringify it. In a real system, you might
            # want more robust serialization or type checking.
            extracted_values = {k: str(v) for k, v in extracted_values.items()}
            
        entry = {
            "source": source,
            "input_type": input_type,
            "intent": intent,
            "timestamp": timestamp,
            "extracted_values": extracted_values
        }
        
        if thread_id not in self.data:
            self.data[thread_id] = []
        self.data[thread_id].append(entry)
        
        return thread_id # Return the thread_id for chaining

    def get_context(self, thread_id: str):
        """
        Retrieves all logged interactions for a given thread_id.
        """
        return self.data.get(thread_id, [])

    def get_last_extracted_fields(self, thread_id: str):
        """
        Retrieves the last set of extracted values for a given thread_id.
        Useful for maintaining context across chained operations.
        """
        context = self.get_context(thread_id)
        if context:
            return context[-1].get("extracted_values", {})
        return {}
    
    def reset(self):
        """
        Clears all memory for testing purposes.
        """
        self.data = {}

# Global instance of shared memory (or pass it around)
shared_memory = SharedMemory()