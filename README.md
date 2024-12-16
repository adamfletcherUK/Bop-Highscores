# Pinball High Scores

A web application for tracking and displaying pinball high scores.

## Features

- Submit new high scores with player names
- Display top 10 high scores
- Automatic updates every 30 seconds
- Clean and modern UI
- Mobile-responsive design

## Setup

1. Install the required dependencies:
```bash
pip install -r requirements.txt
```

2. Run the application:
```bash
uvicorn app:app --reload --port 8080
```

3. Open your web browser and navigate to `http://localhost:8080`

## Technical Details

- Backend: FastAPI with SQLite database
- Frontend: HTML, CSS (Bootstrap), and JavaScript
- Data is stored in a local SQLite database (`highscores.db`)
- API Documentation available at `http://localhost:8080/docs`

## Usage

1. Enter your name and score in the form on the left
2. Click "Submit Score" to add your score to the database
3. The top 10 scores will be displayed on the right
4. Scores are automatically refreshed every 30 seconds
