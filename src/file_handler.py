from pathlib import Path
import os
from datetime import datetime

class FileHandler:
    def __init__(self, output_dir):
        self.output_dir = Path(output_dir)
        self.output_dir.mkdir(parents=True, exist_ok=True)

    def save_qa_text(self, qa_pairs, filename=None):
        """Save Q&A pairs to a text file"""
        if filename is None:
            filename = f"qa_session_{datetime.now().strftime('%Y%m%d_%H%M%S')}.txt"
        
        file_path = self.output_dir / filename
        try:
            with open(file_path, 'w') as f:
                f.writelines(qa_pairs)
            print(f"✅ Saved Q&A to {filename}")
            return filename
        except Exception as e:
            print(f"❌ Error saving Q&A file: {e}")
            return None 