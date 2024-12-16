from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPBasic, HTTPBasicCredentials
from fastapi.responses import HTMLResponse, RedirectResponse
from fastapi.templating import Jinja2Templates
from sqlalchemy.orm import Session
import secrets
import os
from dotenv import load_dotenv
from database import get_db, Player, Score

load_dotenv()

security = HTTPBasic()
templates = Jinja2Templates(directory="templates")

def verify_credentials(credentials: HTTPBasicCredentials = Depends(security)):
    correct_username = os.getenv("ADMIN_USERNAME", "admin")
    correct_password = os.getenv("ADMIN_PASSWORD", "pinbot")
    
    is_correct_username = secrets.compare_digest(credentials.username.encode("utf8"), correct_username.encode("utf8"))
    is_correct_password = secrets.compare_digest(credentials.password.encode("utf8"), correct_password.encode("utf8"))
    
    if not (is_correct_username and is_correct_password):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect username or password",
            headers={"WWW-Authenticate": "Basic"},
        )
    return credentials

async def admin_page(request, credentials: HTTPBasicCredentials = Depends(verify_credentials), db: Session = Depends(get_db)):
    players = db.query(Player).all()
    return templates.TemplateResponse("admin.html", {"request": request, "players": players})

async def delete_player(player_name: str, credentials: HTTPBasicCredentials = Depends(verify_credentials), db: Session = Depends(get_db)):
    player = db.query(Player).filter(Player.name == player_name).first()
    if player is None:
        raise HTTPException(status_code=404, detail="Player not found")
    
    # Delete all scores for the player
    db.query(Score).filter(Score.player_id == player.id).delete()
    # Delete the player
    db.delete(player)
    db.commit()
    return {"message": f"Player {player_name} deleted successfully"}

async def logout():
    response = RedirectResponse(url="/")
    response.headers["WWW-Authenticate"] = "Basic"
    response.status_code = 401
    return response
