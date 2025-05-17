from fastapi import FastAPI, UploadFile, File, Form, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from typing import Dict, Any, List, Optional
import uvicorn
from backend.claim_extractor import ClaimExtractor
from backend.claim_verifier import ClaimVerifier
from backend.media_processor import MediaProcessor

app = FastAPI(
    title="Fact Checker API",
    description="API for extracting and verifying claims from text, images, and videos",
    version="1.0.0"
)

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Initialize components
claim_extractor = ClaimExtractor()
claim_verifier = ClaimVerifier()
media_processor = MediaProcessor()

@app.get("/")
async def root():
    return {"message": "Welcome to Fact Checker API"}

@app.post("/extract-text-claims")
async def extract_text_claims(text: str = Form(...)) -> Dict[str, Any]:
    try:
        # Extract claims
        claims_data = await claim_extractor.extract_from_text(text)
        
        if not claims_data:
            return {
                "claims": [],
                "error": "No claims could be extracted from the text"
            }
        
        # Verify each claim
        verified_claims = []
        for claim_data in claims_data:
            try:
                verification = await claim_verifier.verify_claim(claim_data["claim"])
                verified_claims.append({
                    "claim": claim_data["claim"],
                    "confidence": claim_data["confidence"],
                    "verification": verification
                })
            except Exception as e:
                print(f"Error verifying claim: {str(e)}")
                verified_claims.append({
                    "claim": claim_data["claim"],
                    "confidence": claim_data["confidence"],
                    "verification": {
                        "credibility_score": 0,
                        "verdict": "Error",
                        "explanation": f"Error during verification: {str(e)}",
                        "sources": []
                    }
                })
        
        return {"claims": verified_claims}
    
    except Exception as e:
        print(f"Error in extract_text_claims: {str(e)}")
        raise HTTPException(
            status_code=500,
            detail=f"Error processing request: {str(e)}"
        )

@app.post("/extract-image-claims")
async def extract_image_claims(image: UploadFile = File(...)) -> Dict[str, Any]:
    try:
        # Extract claims from image
        claims = await claim_extractor.extract_from_image(image)
        
        if not claims:
            return {
                "claims": [],
                "error": "No claims could be extracted from the image"
            }
        
        # Verify each claim
        verified_claims = []
        for claim in claims:
            try:
                verification = await claim_verifier.verify_claim(claim["claim"])
                verified_claims.append({
                    "claim": claim["claim"],
                    "confidence": claim["confidence"],
                    "verification": verification
                })
            except Exception as e:
                print(f"Error verifying claim: {str(e)}")
                verified_claims.append({
                    "claim": claim["claim"],
                    "confidence": claim["confidence"],
                    "verification": {
                        "credibility_score": 0,
                        "verdict": "Error",
                        "explanation": f"Error during verification: {str(e)}",
                        "sources": []
                    }
                })
        
        return {"claims": verified_claims}
    
    except Exception as e:
        print(f"Error in extract_image_claims: {str(e)}")
        raise HTTPException(
            status_code=500,
            detail=f"Error processing request: {str(e)}"
        )

@app.post("/api/claims/video")
async def extract_video_claims(video: UploadFile = File(...)):
    """
    Extract claims from video content
    """
    # Save the uploaded video temporarily
    video_path = f"temp_{video.filename}"
    with open(video_path, "wb") as buffer:
        content = await video.read()
        buffer.write(content)
    
    try:
        claims = await claim_extractor.extract_from_video(video_path)
        return claims
    finally:
        # Clean up temporary file
        import os
        if os.path.exists(video_path):
            os.remove(video_path)

@app.post("/api/claims/verify")
async def verify_claims(claims: List[Dict[str, Any]]):
    """
    Verify a list of claims and return their credibility scores
    """
    results = []
    for claim in claims:
        verification = await claim_verifier.verify_claim(claim["text"])
        results.append({
            "claim": claim["text"],
            "verification": verification
        })
    return results

@app.post("/api/analyze/text")
async def analyze_text(text: str = Form(...)):
    """
    Analyze text content and return extracted claims with verification
    """
    # Extract claims
    claims_data = await claim_extractor.extract_from_text(text)
    claims = claims_data.get("claims", [])
    
    # Verify each claim
    verified_claims = []
    for claim in claims:
        verification = await claim_verifier.verify_claim(claim["text"])
        verified_claims.append({
            "claim": claim["text"],
            "confidence": claim["confidence"],
            "verification": verification
        })
    
    return {
        "claims": verified_claims,
        "original_text": text
    }

@app.post("/api/analyze/image")
async def analyze_image(image: UploadFile = File(...)):
    """
    Analyze image content and return extracted claims with verification
    """
    # Save the uploaded image temporarily
    image_path = f"temp_{image.filename}"
    with open(image_path, "wb") as buffer:
        content = await image.read()
        buffer.write(content)
    
    try:
        # Extract claims
        claims_data = await claim_extractor.extract_from_image(image_path)
        claims = claims_data.get("claims", [])
        
        # Verify each claim
        verified_claims = []
        for claim in claims:
            verification = await claim_verifier.verify_claim(claim["text"])
            verified_claims.append({
                "claim": claim["text"],
                "confidence": claim["confidence"],
                "verification": verification
            })
        
        return {
            "claims": verified_claims,
            "image_path": image_path
        }
    finally:
        # Clean up temporary file
        import os
        if os.path.exists(image_path):
            os.remove(image_path)

if __name__ == "__main__":
    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True)
