import asyncio
from claim_extractor import ClaimExtractor

async def test_text_extraction():
    extractor = ClaimExtractor()
    
    # Test cases
    test_texts = [
        "NASA has discovered evidence of water on Mars.",
        "The Earth is flat and NASA is hiding the truth.",
        "COVID-19 vaccines contain microchips for tracking.",
        "The Great Wall of China is visible from space.",
        "Drinking lemon water cures cancer."
    ]
    
    print("\n=== Testing Text Claim Extraction ===")
    for text in test_texts:
        result = await extractor.extract_from_text(text)
        print(f"\nInput: {text}")
        print(f"Claims found: {len(result['claims'])}")
        for claim in result['claims']:
            print(f"- Claim: {claim['text']}")

async def test_image_extraction():
    extractor = ClaimExtractor()
    
    # Test cases - using some sample image URLs
    test_images = [
        "https://picsum.photos/800/600",  # Random image
        "https://raw.githubusercontent.com/pytorch/hub/master/images/dog.jpg",  # Sample dog image
        "https://upload.wikimedia.org/wikipedia/commons/thumb/e/e7/Leucanthemum_vulgare_%27Filigran%27_Flower_2200px.jpg/800px-Leucanthemum_vulgare_%27Filigran%27_Flower_2200px.jpg"  # Flower image
    ]
    
    print("\n=== Testing Image Claim Extraction ===")
    for image_url in test_images:
        result = await extractor.extract_from_image(image_url)
        print(f"\nImage URL: {image_url}")
        print(f"Claims found: {len(result['claims'])}")
        for claim in result['claims']:
            print(f"- Claim: {claim['text']}")

async def main():
    print("Starting Claim Extractor Tests...")
    await test_text_extraction()
    await test_image_extraction()

if __name__ == "__main__":
    asyncio.run(main()) 