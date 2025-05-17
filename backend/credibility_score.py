# credibility_scorer.py

from typing import Dict, Any, List
from transformers import pipeline
from credibility_checker import CredibilityChecker

class CredibilityScorer:
    def __init__(self):
        self.similarity_model = pipeline("sentence-similarity", model="sentence-transformers/all-MiniLM-L6-v2")
        self.checker = CredibilityChecker()

    async def score_claim(self, claim: str) -> Dict[str, Any]:
        wikipedia_result = await self.checker.check_claim(claim)

        similarity_scores = []
        for match in wikipedia_result['matches']:
            try:
                sim = self.similarity_model(claim, match['extract'])[0]['score']
                similarity_scores.append(sim)
            except:
                continue

        average_similarity = sum(similarity_scores) / len(similarity_scores) if similarity_scores else 0

        final_score = 0.7 * wikipedia_result['score'] + 30 * average_similarity

        explanation = "Wikipedia relevance and sentence similarity were used to score this claim."

        return {
            "claim": claim,
            "score": round(final_score, 2),
            "sources": wikipedia_result['sources'],
            "explanation": explanation
        }
