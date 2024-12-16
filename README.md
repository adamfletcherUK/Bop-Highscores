# Bop Highscores

A FastAPI-based web application for tracking pinball high scores with profanity filtering.

## Features

- Track and display pinball high scores
- Profanity filtering for player names
- Real-time score updates
- Clean, modern interface
- Admin authentication for data management

## Setup

1. **Create, activate, and setup virtual environment**
   ```bash
   python -m venv .venv
   source .venv/bin/activate  # On Windows use: .venv\Scripts\activate
   pip install -r requirements.txt
   ```

2. **Set up environment variables**
   Create a `.env` file in the root directory with:
   ```
   ADMIN_USERNAME=your_admin_username
   ADMIN_PASSWORD=your_admin_password
   HOSTNAME=your_hostname
   ```

3. **Run the application**
   ```bash
   python app.py
   ```

   The app will be available at:
   - Locally: `http://localhost:8080`
   - Other devices: `http://<HOSTNAME>:8080` (e.g., `http://Adams-MacBook-Pro-2.local:8080`)

   To find your computer's IP address:
   - Mac/Linux: Run `ifconfig` in terminal
   - Windows: Run `ipconfig` in command prompt

## Usage

- **View High Scores**: Visit the homepage to see the current high scores
- **Submit Score**: Enter player name and score in the submission form
- **Admin Access**: Use `/admin` endpoint with your credentials to manage scores

## Development

- The application uses SQLite for data storage
- FastAPI for the backend API
- Basic authentication for admin access
- Better-profanity for filtering inappropriate usernames

## Requirements

- Python 3.11+
- FastAPI
- SQLAlchemy
- Better-profanity
- Python-dotenv

## Contributing

1. Fork the repository
2. Create your feature branch (`git checkout -b feature/AmazingFeature`)
3. Commit your changes (`git commit -m 'Add some AmazingFeature'`)
4. Push to the branch (`git push origin feature/AmazingFeature`)
5. Open a Pull Request
