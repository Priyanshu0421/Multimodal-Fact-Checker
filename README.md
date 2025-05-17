# Multimodal Fact-Checker for Social Media Posts

A powerful tool that analyzes social media posts (text, images, videos, and audio) to verify claims and provide credibility scores.

## Features

- **Multimodal Analysis**: Process text, images, videos, and audio content
- **Claim Extraction**: Automatically identify claims from various media types
- **Credibility Scoring**: Rate claims based on verified sources
- **Source Citation**: Provide references and evidence for fact-checking results

## Tech Stack

- **Frontend**: Next.js
- **Backend**: FastAPI
- **Models**:
  - Lighttricks/LTX-Video (Video understanding)
  - lodestones/Chroma (Image analysis)
  - parakeet-tdt-0.6b-v2 (Audio transcription)
- **Database**: Supabase

## Project Structure

```
/fact-checker/
├── backend/           # FastAPI backend
│   ├── main.py       # FastAPI app
│   ├── claim_extractor.py
│   ├── credibility_score.py
│   ├── models/
│   └── utils/
├── frontend/         # Next.js frontend
│   ├── pages/
│   ├── components/
│   └── styles/
├── data/            # Sample data and test cases
└── public/          # Static assets
```

## Setup Instructions

1. Clone the repository
2. Install backend dependencies:
   ```bash
   cd backend
   pip install -r requirements.txt
   ```
3. Install frontend dependencies:
   ```bash
   cd frontend
   npm install
   ```
4. Set up environment variables (see `.env.example`)
5. Run the development servers:
   - Backend: `uvicorn main:app --reload`
   - Frontend: `npm run dev`

## API Documentation

Once the server is running, visit `/docs` for the interactive API documentation.

## Contributing

Contributions are welcome! Please read our contributing guidelines before submitting pull requests.

## License

MIT License 