import asyncio
from credibility_checker import CredibilityChecker

async def test_credibility_checker():
    checker = CredibilityChecker()
    
    # Test cases with varying levels of credibility
    test_claims = [
        "The Great Wall of China is visible from space",  # Common misconception
        "Water boils at 100 degrees Celsius at sea level",  # Scientific fact
        "The Earth is flat",  # Debunked theory
        "The Moon landing was faked",  # Conspiracy theory
        "Albert Einstein won the Nobel Prize in Physics"  # Historical fact
    ]
    
    print("\n=== Testing Wikipedia Credibility Checker ===")
    for claim in test_claims:
        print(f"\nChecking claim: {claim}")
        result = await checker.check_claim(claim)
        
        print(f"Credibility Score: {result['score']}/100")
        print("\nMatching Articles:")
        for match in result['matches']:
            print(f"\nTitle: {match['title']}")
            print(f"URL: {match['url']}")
            print(f"Last Modified: {match['last_modified']}")
            print(f"Extract: {match['extract'][:200]}...")  # Show first 200 chars
        print("-" * 80)

if __name__ == "__main__":
    asyncio.run(test_credibility_checker()) 