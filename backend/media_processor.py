from typing import Dict, Any, List
import requests
from PIL import Image
import base64
from io import BytesIO

class MediaProcessor:
    def __init__(self):
        self.ollama_url = "http://host.docker.internal:11434/api/generate"
        self.model = "llama2"  # or any other model you have in Ollama

    def process_video(self, video_path: str) -> List[Dict[str, Any]]:
        """
        Process a video file and extract key frames
        """
        # TODO: Implement key frame extraction
        return []
    
    def _analyze_frame(self, frame: Image.Image) -> Dict[str, Any]:
        """
        Analyze a single video frame using Ollama
        """
        try:
            # Convert image to base64
            buffered = BytesIO()
            frame.save(buffered, format="PNG")
            img_str = base64.b64encode(buffered.getvalue()).decode()
            
            # Prepare prompt for Ollama
            prompt = "Describe what you see in this image and extract any statements that could be considered claims."
            
            # Query Ollama
            payload = {
                "model": self.model,
                "prompt": prompt,
                "images": [img_str],
                "stream": False
            }
            
            response = requests.post(self.ollama_url, json=payload)
            response.raise_for_status()
            
            return {
                "description": response.json().get("response", ""),
                "confidence": 1.0
            }
            
        except Exception as e:
            print(f"Error analyzing frame: {str(e)}")
            return {
                "description": "",
                "confidence": 0.0
            }
