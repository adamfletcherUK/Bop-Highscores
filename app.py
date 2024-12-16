from fastapi import FastAPI, Request, HTTPException, Depends
from fastapi.responses import HTMLResponse, RedirectResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from fastapi.security import HTTPBasic, HTTPBasicCredentials
from sqlalchemy import create_engine, Column, Integer, String, DateTime, desc, func
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from datetime import datetime
from pydantic import BaseModel, validator
from better_profanity import profanity
import os
import secrets
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Configure profanity filter
profanity.load_censor_words()

app = FastAPI()
templates = Jinja2Templates(directory="templates")
app.mount("/static", StaticFiles(directory="static"), name="static")
security = HTTPBasic()

# Database setup
SQLALCHEMY_DATABASE_URL = os.getenv("SQLALCHEMY_DATABASE_URL", "sqlite:///./highscores.db")
engine = create_engine(SQLALCHEMY_DATABASE_URL, connect_args={"check_same_thread": False})
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()

def verify_admin(credentials: HTTPBasicCredentials = Depends(security)):
    correct_username = secrets.compare_digest(
        credentials.username, 
        os.getenv("ADMIN_USERNAME", "admin")
    )
    correct_password = secrets.compare_digest(
        credentials.password, 
        os.getenv("ADMIN_PASSWORD", "pinbot")
    )
    
    if not (correct_username and correct_password):
        raise HTTPException(
            status_code=401,
            detail="Incorrect username or password",
            headers={"WWW-Authenticate": "Basic"},
        )
    return credentials

class HighScore(Base):
    __tablename__ = "high_score"
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(50))
    score = Column(Integer)
    date = Column(DateTime, default=datetime.utcnow)

Base.metadata.create_all(bind=engine)

class ScoreCreate(BaseModel):
    name: str
    score: int
    submission_time: datetime = datetime.utcnow()

    @validator('name')
    def name_must_be_clean(cls, v):
        # Check for profanity
        if profanity.contains_profanity(v):
            raise ValueError('Player name contains inappropriate language')
        
        # Check length
        if len(v) > 20:
            raise ValueError('Player name must be 20 characters or less')
            
        # Check for valid characters (letters, numbers, and some special characters)
        import re
        if not re.match(r'^[a-zA-Z0-9_\- ]+$', v):
            raise ValueError('Player name can only contain letters, numbers, spaces, underscores, and hyphens')
            
        return v

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

@app.get("/", response_class=HTMLResponse)
async def index(request: Request):
    return templates.TemplateResponse("index.html", {"request": request})

@app.get("/player/{name}", response_class=HTMLResponse)
async def player_scores(request: Request, name: str):
    return templates.TemplateResponse("player.html", {"request": request, "player_name": name})

@app.get("/api/scores")
def get_scores():
    db = SessionLocal()
    
    # Create a subquery to get the highest score for each player
    subquery = (
        db.query(
            HighScore.name,
            func.max(HighScore.score).label('max_score')
        )
        .group_by(HighScore.name)
        .subquery()
    )
    
    # Join with the original table to get the full record including date
    scores = (
        db.query(HighScore)
        .join(
            subquery,
            (HighScore.name == subquery.c.name) & 
            (HighScore.score == subquery.c.max_score)
        )
        .order_by(desc(HighScore.score))
        .limit(10)
        .all()
    )
    
    db.close()
    return [{
        'name': score.name,
        'score': score.score,
        'date': score.date.strftime('%Y-%m-%d %H:%M:%S')
    } for score in scores]

@app.get("/api/player/{name}/scores")
def get_player_scores(name: str):
    db = SessionLocal()
    try:
        # Get all scores to calculate percentiles
        all_scores = db.query(HighScore.score).all()
        all_scores = [score[0] for score in all_scores]
        
        # Get player's scores with daily averages
        player_scores = (
            db.query(HighScore)
            .filter(HighScore.name == name)
            .order_by(desc(HighScore.score))
            .all()
        )
        
        if not player_scores:
            raise HTTPException(status_code=404, detail="Player not found")
        
        # Calculate daily averages
        daily_averages = {}
        all_scores_by_date = db.query(
            func.date(HighScore.date).label('date'),
            func.avg(HighScore.score).label('avg_score')
        ).group_by(func.date(HighScore.date)).all()
        
        for date, avg in all_scores_by_date:
            daily_averages[str(date)] = round(avg)
        
        # Prepare response with percentiles and daily averages
        scores_data = []
        for score in player_scores:
            score_date = score.date.date()
            percentile = (sum(1 for s in all_scores if s < score.score) / len(all_scores)) * 100
            
            scores_data.append({
                'score': score.score,
                'date': score.date.strftime('%Y-%m-%d %H:%M:%S'),
                'percentile': round(percentile, 1),
                'daily_average': daily_averages.get(str(score_date), 0)
            })
        
        # Calculate average score
        average_score = sum(score.score for score in player_scores) / len(player_scores)
        
        return {
            'name': name,
            'scores': scores_data,
            'average_score': round(average_score)
        }
    finally:
        db.close()

@app.post("/api/scores")
def add_score(score: ScoreCreate):
    db = SessionLocal()
    # Double check profanity just in case
    if profanity.contains_profanity(score.name):
        raise HTTPException(
            status_code=400, 
            detail={"message": "Please choose a nicer username!", "error_type": "profanity"}
        )
        
    db_score = HighScore(
        name=score.name,
        score=score.score,
        date=score.submission_time
    )
    db.add(db_score)
    db.commit()
    db.refresh(db_score)
    db.close()
    return {"message": "Score added successfully"}

@app.get("/admin", response_class=HTMLResponse)
async def admin_page(request: Request, credentials: HTTPBasicCredentials = Depends(verify_admin)):
    db = SessionLocal()
    players = db.query(HighScore.name).distinct().all()
    players = [player[0] for player in players]
    db.close()
    return templates.TemplateResponse("admin.html", {
        "request": request,
        "players": players
    })

@app.delete("/api/admin/player/{name}")
async def delete_player(name: str, credentials: HTTPBasicCredentials = Depends(verify_admin)):
    db = SessionLocal()
    try:
        deleted = db.query(HighScore).filter(HighScore.name == name).delete()
        if not deleted:
            raise HTTPException(status_code=404, detail="Player not found")
        db.commit()
        return {"message": f"Player {name} and all their scores have been deleted"}
    finally:
        db.close()

@app.get("/logout")
async def logout():
    response = RedirectResponse(url="/")
    response.headers["WWW-Authenticate"] = "Basic"
    response.status_code = 401
    return response

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8080)
