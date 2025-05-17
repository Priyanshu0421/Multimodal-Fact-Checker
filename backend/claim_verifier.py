from typing import Dict, Any
import requests
import json
import wikipediaapi
import re
import certifi
import ssl

class ClaimVerifier:
    def __init__(self):
        self.ollama_url = "http://host.docker.internal:11434/api/generate"
        # Create a custom SSL context with verified certificates
        ssl_context = ssl.create_default_context(cafile=certifi.where())
        self.wiki = wikipediaapi.Wikipedia(
            language='en',
            extract_format=wikipediaapi.ExtractFormat.WIKI,
            user_agent='FactChecker/1.0',
            ssl_context=ssl_context
        )

    def _get_wikipedia_info(self, claim: str) -> Dict[str, Any]:
        """
        Try to extract the most relevant topic from the claim for Wikipedia lookup.
        Naive fallback: use first noun phrase or capitalized word.
        """
        try:
            # For questions about classification, try to extract the subject
            if "is" in claim.lower() and ("a" in claim.lower() or "an" in claim.lower()):
                parts = claim.lower().split()
                if "is" in parts:
                    is_index = parts.index("is")
                    if is_index + 2 < len(parts):  # Ensure we have enough words after "is"
                        topic = parts[is_index + 1]  # Get the word after "is"
                        if topic in ["a", "an"] and is_index + 2 < len(parts):
                            topic = parts[is_index + 2]  # Get the word after "a" or "an"
            else:
                # For other claims, use the first capitalized word or first word
                words = claim.split()
                topic = None
                for word in words:
                    if word.istitle() or word.isupper():
                        topic = word
                        break
                topic = topic or claim.split()[0]

            page = self.wiki.page(topic)
            summary = page.summary if page.exists() else ""

            # Try to get family information if it's a plant
            family_info = ""
            if "family" in claim.lower():
                family_match = re.search(r'(\w+)\s+family', claim.lower())
                if family_match:
                    family_page = self.wiki.page(family_match.group(1) + " family")
                    if family_page.exists():
                        family_info = f"\nFamily Information: {family_page.summary}"

            return {
                "title": page.title if page.exists() else topic,
                "summary": summary + family_info,
                "url": page.fullurl if page.exists() else "",
                "exists": page.exists()
            }
        except Exception as e:
            print(f"Error in _get_wikipedia_info: {str(e)}")
            return {"exists": False, "summary": ""}

    async def verify_claim(self, claim: str) -> Dict[str, Any]:
        try:
            wiki_info = self._get_wikipedia_info(claim)
            wiki_context = wiki_info.get('summary', '')
            
            # For classification questions, add specific guidance
            if "is" in claim.lower() and ("a" in claim.lower() or "an" in claim.lower()):
                prompt = f"""You are a fact-checking expert specializing in scientific classification. For the claim below, you must:
1. Determine if the claim is true or false based on:
   - Scientific classification
   - Botanical definitions
   - Expert consensus
   - Reliable sources
2. Assign a credibility score (0-100):
   - 100: Completely true, scientifically proven
   - 75: Mostly true, minor classification nuances
   - 50: Partially true, depends on context
   - 25: Mostly false, some truth
   - 0: Completely false
3. Provide a clear explanation with scientific evidence
4. List authoritative sources

Claim: "{claim}"

Wikipedia Context: "{wiki_context}"

IMPORTANT: You must respond with a valid JSON object in this exact format:
{{
  "credibility_score": 100,
  "verdict": "True",
  "explanation": "Your explanation here",
  "sources": ["Source 1", "Source 2"]
}}

Do not include any text before or after the JSON object. The response must be parseable as JSON."""
            else:
                prompt = f"""You are a fact-checking expert. For the claim below, you must:
1. Determine if the claim is true or false based on:
   - Scientific consensus
   - Historical records
   - Expert opinions
   - Reliable sources
2. Assign a credibility score (0-100):
   - 100: Completely true, well-documented
   - 75: Mostly true, minor inaccuracies
   - 50: Partially true, needs context
   - 25: Mostly false, some truth
   - 0: Completely false
3. Provide a clear explanation with evidence
4. List authoritative sources

Claim: "{claim}"

Wikipedia Context: "{wiki_context}"

IMPORTANT: You must respond with a valid JSON object in this exact format:
{{
  "credibility_score": 100,
  "verdict": "True",
  "explanation": "Your explanation here",
  "sources": ["Source 1", "Source 2"]
}}

Do not include any text before or after the JSON object. The response must be parseable as JSON."""

            response = requests.post(
                self.ollama_url,
                json={
                    "model": "llama3.2",
                    "prompt": prompt,
                    "stream": False
                }
            )
            response.raise_for_status()
            raw = response.json().get("response", "")

            if not raw:
                raise ValueError("Empty response from Ollama")

            # Clean the response to ensure it's valid JSON
            raw = raw.strip()
            # Remove any text before the first {
            raw = raw[raw.find("{"):]
            # Remove any text after the last }
            raw = raw[:raw.rfind("}")+1]

            try:
                result = json.loads(raw)
            except json.JSONDecodeError as e:
                print(f"JSON decode error: {str(e)}")
                print(f"Raw response: {raw}")
                raise ValueError(f"Invalid JSON in response: {str(e)}")

            # Validate and set default values for required fields
            result = {
                "credibility_score": int(result.get("credibility_score", 0)),
                "verdict": str(result.get("verdict", "False")),
                "explanation": str(result.get("explanation", "No explanation provided.")),
                "sources": list(result.get("sources", []))
            }

            # Ensure credibility score is between 0 and 100
            result["credibility_score"] = max(0, min(100, result["credibility_score"]))

            # Add Wikipedia as a source if available
            if wiki_info.get("exists"):
                result["sources"].append({
                    "title": wiki_info["title"],
                    "url": wiki_info["url"]
                })

            return result

        except Exception as e:
            print(f"Error in verify_claim: {str(e)}")
            return {
                "credibility_score": 0,
                "verdict": "False",
                "explanation": f"Error during fact-checking: {str(e)}",
                "sources": []
            }
