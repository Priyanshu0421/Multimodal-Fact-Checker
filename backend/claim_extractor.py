from transformers import pipeline, AutoTokenizer, AutoModelForSequenceClassification
from typing import Dict, Any, List, Optional
import torch
import numpy as np
from PIL import Image
import requests
from io import BytesIO
import base64
import re
from .claim_verifier import ClaimVerifier

def query_ollama(prompt: str, model: str = "llama3.2", image: Optional[Image.Image] = None) -> str:
    """
    Query the Ollama API with a prompt and optional image, return the response.
    """
    try:
        payload = {
            "model": model,
            "prompt": prompt,
            "stream": False
        }
        
        if image:
            buffered = BytesIO()
            image.save(buffered, format="PNG")
            img_str = base64.b64encode(buffered.getvalue()).decode()
            payload["images"] = [img_str]
        
        response = requests.post(
            "http://host.docker.internal:11434/api/generate", 
            json=payload
        )
        response.raise_for_status()
        return response.json().get("response", "")
    except Exception as e:
        print(f"Error querying Ollama: {str(e)}")
        return ""

class ClaimExtractor:
    def __init__(self):
        self.model = "llama3.2"

    async def extract_from_text(self, text: str) -> List[Dict[str, Any]]:
        """
        Extract claims from text content using Ollama
        """
        try:
            prompt = f"""Analyze the following text and extract the main claim or answer the question.
            If it's a question, provide a clear, factual answer.
            If it's a statement, extract the main claim.
            Be specific and accurate.
            Format the response as a single, definitive statement.
            
            Text: {text}
            
            Response:"""
            
            result = query_ollama(prompt, self.model)
            if not result:
                return [{'claim': text, 'confidence': 0.5}]

            claim = result.strip()
            
            # Clean up the response
            claim = re.sub(r'\s+', ' ', claim)
            claim = claim.replace('"', '').strip()
            
            # If the response is a question, convert it to a statement
            if claim.endswith('?'):
                claim = claim[:-1]
            if claim.lower().startswith(('is ', 'are ', 'was ', 'were ')):
                claim = claim.split(' ', 1)[1]
                
            return [{'claim': claim, 'confidence': 1.0}]
            
        except Exception as e:
            print(f"Error in extract_from_text: {str(e)}")
            return [{'claim': text, 'confidence': 0.5}]

    def _fallback_claims(self, text: str) -> List[str]:
        """
        Generic fallback if LLM fails to extract any claims.
        """
        cleaned = re.sub(r'[^\w\s]', '', text).strip()
        if not cleaned:
            return []
        return [f"{cleaned} is a valid claim.", f"{cleaned} is not a valid claim."]

    async def extract_from_image(self, image_path: str) -> Dict[str, Any]:
        """
        Extract claims from image content using Ollama
        """
        try:
            image = Image.open(requests.get(image_path, stream=True).raw) if image_path.startswith(('http://', 'https://')) else Image.open(image_path)

            prompt = """Describe what you see in this image and extract any statements that could be considered claims.
A claim is any statement that makes an assertion about what is shown in the image.
Include statements about objects, people, actions, or scenes visible in the image.
Format each claim as a single line starting with "- ".
Do not add explanations or commentary.

Claims:"""

            result = query_ollama(prompt, self.model, image)
            claims = []
            for line in result.split('\n'):
                line = line.strip()
                if line.startswith('- '):
                    claim = line[2:].strip()
                    if claim:
                        claims.append(claim)

            return {
                'claims': [{'text': claim, 'confidence': 1.0} for claim in claims],
                'image_path': image_path
            }

        except Exception as e:
            return {
                'error': str(e),
                'claims': [],
                'image_path': image_path
            }

    async def extract_from_video(self, video_path: str) -> Dict[str, Any]:
        return {
            'claims': [],
            'video_path': video_path,
            'error': 'Video analysis not implemented yet'
        }

    async def extract_from_audio(self, audio_path: str) -> Dict[str, Any]:
        return {
            'claims': [],
            'audio_path': audio_path,
            'error': 'Audio analysis not implemented yet'
        }