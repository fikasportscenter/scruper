from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from scraper import fetch_stats_for_team
from predictor import predict_scoreline
import uvicorn

app = FastAPI(title="Football Prediction API")

class MatchRequest(BaseModel):
    home_team: str
    away_team: str

class PredictionResponse(BaseModel):
    home_team: str
    away_team: str
    predicted_score: str
    confidence: str
    home_stats: dict
    away_stats: dict

@app.post("/predict", response_model=PredictionResponse)
async def predict_match(request: MatchRequest):
    try:
        # Fetch stats for both teams
        home_stats = fetch_stats_for_team(request.home_team)
        away_stats = fetch_stats_for_team(request.away_team)
        
        if not home_stats or not away_stats:
            raise HTTPException(status_code=404, detail="Could not find recent stats for one or both teams.")
        
        # Predict
        prediction = predict_scoreline(home_stats, away_stats)
        
        if not prediction:
            raise HTTPException(status_code=500, detail="Prediction failed.")
            
        return PredictionResponse(
            home_team=request.home_team,
            away_team=request.away_team,
            predicted_score=prediction['predicted_score'],
            confidence=prediction['confidence'],
            home_stats=home_stats,
            away_stats=away_stats
        )
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)