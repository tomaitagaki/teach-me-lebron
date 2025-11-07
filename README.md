# 🏀 Teach Me LeBron - Sports Lore Chatbot

A modern, AI-powered chatbot that helps you keep up with sports conversations at work. Get sports news and lore explained in simple, layman's terms so you can confidently chat with your normie coworkers.

## Features

### 🎯 Reactive Chat
- Ask questions about sports history, players, rules, and terminology
- Get explanations in simple, jargon-free language
- Perfect for understanding what everyone's talking about at the water cooler

### 🎥 Infamous Sports Clips
- **20+ iconic sports moments** automatically shown when relevant
- Includes: Kawhi's bounce, JR Smith's blunder, Beast Quake, Malcolm Butler INT
- Also: 28-3 comeback, Butt Fumble, Malice at Palace, and more
- YouTube embeds with context and explanations
- Keyword-based search matches your questions to clips

### 📰 Proactive News
- Automatically get updates on important sports news
- Focused on **playoff games** and **local team news** only
- No spam - only the stuff you actually need to know

### 🌐 Smart Onboarding
- Select your location to automatically follow local teams
- **Seattle default**: Mariners (MLB), Seahawks (NFL)
- Easily customizable for other locations

### ⚡ Clean, Functional UI
- **Minimal design** inspired by Meta internal tooling
- Simple gray/white color scheme with blue accents
- Real-time streaming responses using Server-Sent Events (SSE)
- Token-by-token streaming for instant feedback
- No clutter, no distractions - just information

## Tech Stack

- **Backend**: FastAPI (Python) with async/await
- **LLM**: OpenRouter API (supports multiple models)
- **Sports Data**: ESPN API (free, no key required)
- **Streaming**: Server-Sent Events (SSE)
- **Frontend**: Vanilla JavaScript with modern ES6+

## Prerequisites

- Python 3.8+
- OpenRouter API key (get one at [openrouter.ai](https://openrouter.ai))

## Quick Start

### 1. Clone and Setup

```bash
cd teach-me-lebron
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
pip install -r requirements.txt
```

### 2. Configure Environment

```bash
cp .env.example .env
```

Edit `.env` and add your OpenRouter API key:

```env
OPENROUTER_API_KEY=your_key_here
OPENROUTER_MODEL=google/gemini-2.0-flash-exp:free
```

### 3. Run the Server

```bash
python main.py
```

The server will start at `http://localhost:8000`

### 4. Open the Chat Interface

Navigate to `http://localhost:8000` in your browser and start chatting!

## API Endpoints

### Chat Endpoints

#### `POST /api/chat/stream`
Main chat endpoint with SSE streaming.

**Request:**
```json
{
  "message": "What's the latest news?",
  "user_id": "default_user",
  "preferences": {
    "location": "Seattle",
    "teams": [...]
  }
}
```

**Response:** SSE stream with tokens

#### `POST /api/chat/check-news`
Check for important proactive news.

**Request:**
```json
{
  "location": "Seattle",
  "teams": [...]
}
```

**Response:**
```json
{
  "should_notify": true,
  "news_count": 3,
  "news_items": [...]
}
```

### Onboarding Endpoints

#### `GET /api/onboarding/default-teams/{location}`
Get default team preferences for a location.

#### `GET /api/onboarding/available-locations`
Get list of supported locations.

#### `POST /api/onboarding/preferences`
Save user preferences (validates and returns).

## Usage Examples

### Ask About Sports Lore
```
User: "Who is LeBron James?"
Bot: "LeBron James is one of the greatest basketball players of all time..."
```

### Get Latest News
```
User: "What's the latest news?"
Bot: "Here's what's happening with your teams:
• Seattle Mariners are in playoff contention..."
```

### See Infamous Moments
```
User: "Tell me about the Kawhi Leonard shot"
Bot: "In Game 7 of the 2019 playoffs, Kawhi hit a buzzer beater that bounced FOUR times..."
[YouTube video automatically appears below]
```

### Understand Terminology
```
User: "What's a wildcard in baseball?"
Bot: "A wildcard is like a second chance to make the playoffs..."
```

## Configuration

### Changing the LLM Model

Edit `.env` to use different models:

```env
# Free options
OPENROUTER_MODEL=google/gemini-2.0-flash-exp:free
OPENROUTER_MODEL=google/gemini-2.0-flash-thinking-exp:free

# Paid options (better quality)
OPENROUTER_MODEL=anthropic/claude-3.5-sonnet
OPENROUTER_MODEL=openai/gpt-4-turbo
```

### Adding More Locations

Edit `services/sports_news.py` to add more location defaults:

```python
self.other_city_teams = {
    "baseball": {
        "name": "Team Name",
        "id": "espn_team_id",
        "league": "mlb"
    }
}
```

### Adding More Clips

Edit `services/clips_database.py` to add new infamous moments:

```python
"your_clip_id": {
    "keywords": ["keyword1", "keyword2", "phrase"],
    "title": "Display Title",
    "description": "Brief context about what happened",
    "youtube_id": "YouTubeVideoID",
    "timestamp": None  # or seconds to start at
}
```

Current clips include:
- **NBA**: Kawhi's bounce, JR Smith blunder, Malice at Palace, LeBron's block, Ray Allen's three
- **NFL**: Beast Quake, Malcolm Butler INT, 28-3 comeback, Butt Fumble, Helmet Catch
- **MLB**: 1995 Mariners comeback
- **Other**: Zidane headbutt, Minneapolis Miracle, Double Doink

## Project Structure

```
teach-me-lebron/
├── main.py                 # FastAPI application entry point
├── config.py              # Configuration and settings
├── models.py              # Pydantic data models
├── requirements.txt       # Python dependencies
├── routers/
│   ├── chat.py           # Chat endpoints with SSE streaming
│   └── onboarding.py     # User onboarding endpoints
├── services/
│   ├── openrouter.py     # OpenRouter LLM integration
│   ├── sports_news.py    # ESPN API integration
│   └── clips_database.py # Infamous sports clips database
└── static/
    ├── index.html        # Chat interface
    ├── chat.js          # Frontend logic with SSE handling
    └── styles.css       # Minimal Meta-style UI
```

## How It Works

### Reactive Mode (Q&A)
1. User asks a question
2. Backend streams response from OpenRouter LLM
3. Frontend displays tokens in real-time using SSE
4. System prompt ensures layman-friendly explanations

### Proactive Mode (News)
1. User requests news or system checks automatically
2. Backend fetches from ESPN API
3. Filters for playoff or local team news only
4. LLM summarizes in simple terms
5. Streams summary to user

### Streaming Architecture
- Uses SSE (Server-Sent Events) for one-way streaming
- Tokens arrive as `data:` prefixed JSON events
- Frontend parses and displays incrementally
- Provides ChatGPT-like streaming UX

## Customization

### System Prompts

Edit `routers/chat.py` to customize how the bot responds:

- `SPORTS_LORE_SYSTEM_PROMPT` - For Q&A mode
- `SPORTS_NEWS_SYSTEM_PROMPT` - For news summaries

### News Filtering

Edit `services/sports_news.py`:

```python
# Change what counts as "important"
important_news = [
    news for news in all_news
    if news.importance in ["playoff", "local", "your_custom_importance"]
]
```

## Development

### Run with Auto-reload
```bash
python main.py  # Already includes reload=True
```

### Run with Custom Port
```bash
# Edit .env
PORT=3000
```

### API Documentation
Visit `http://localhost:8000/docs` for interactive API documentation (Swagger UI)

## Deployment

### Production Considerations

1. **Environment Variables**: Never commit `.env` file
2. **CORS**: Update CORS origins in `main.py` for your domain
3. **Database**: Currently stores preferences in memory - add database for production
4. **Rate Limiting**: Add rate limiting for API endpoints
5. **Caching**: Add caching for sports news to reduce API calls

### Example Docker Deployment

```dockerfile
FROM python:3.11-slim
WORKDIR /app
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt
COPY . .
CMD ["python", "main.py"]
```

## Contributing

Contributions welcome! Areas for improvement:

- [ ] Add more city/team defaults
- [ ] Implement user authentication
- [ ] Add database for persistent preferences
- [ ] Support more sports leagues
- [ ] Add dark mode
- [ ] Mobile app

## License

MIT License - feel free to use this for your own projects!

## Credits

- Built with [FastAPI](https://fastapi.tiangolo.com/)
- LLM powered by [OpenRouter](https://openrouter.ai)
- Sports data from [ESPN API](https://www.espn.com/apis/devcenter)
- Inspired by the need to survive water cooler sports talk

---

**Made with ❤️ for people who just want to fit in at work**
