# test_fact_checker.py

import asyncio
from credibility_score import CredibilityScorer

async def run_tests():
    scorer = CredibilityScorer()
    claims = [
        "The Earth is flat",
        "Albert Einstein developed the theory of relativity",
        "Bananas are a type of vegetable"
    ]

    for claim in claims:
        result = await scorer.score_claim(claim)
        print(f"\nClaim: {result['claim']}")
        print(f"Credibility Score: {result['score']}/100")
        print(f"Sources: {result['sources']}")
        print(f"Explanation: {result['explanation']}")
        print("-" * 50)

if __name__ == "__main__":
    asyncio.run(run_tests())
