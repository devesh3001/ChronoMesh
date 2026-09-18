import json
from datetime import datetime

class Exporter:
    def __init__(self, output_path: str):
        self.output_path = output_path
        self.checkpoints = []
        
    def add_checkpoint(self, checkpoint: dict):
        # Format dates as strings
        formatted = checkpoint.copy()
        if isinstance(formatted.get("as_of_time"), datetime):
            formatted["as_of_time"] = formatted["as_of_time"].isoformat() + "Z"
            
        # Enum string conversion
        for k, v in formatted.items():
            if hasattr(v, "value"):
                formatted[k] = v.value
                
        self.checkpoints.append(formatted)
        
    def save(self):
        with open(self.output_path, "w") as f:
            json.dump(self.checkpoints, f, indent=2)
