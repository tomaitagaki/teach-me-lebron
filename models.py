from pydantic import BaseModel
from typing import List, Optional
from enum import Enum


class TeamPreference(BaseModel):
    """User's preferred team."""
    team_name: str
    team_id: str
    sport: str
    is_local: bool = False


class UserPreferences(BaseModel):
    """User preferences including teams and location."""
    location: str = "Seattle"
    teams: List[TeamPreference] = []

    class Config:
        json_schema_extra = {
            "example": {
                "location": "Seattle",
                "teams": [
                    {
                        "team_name": "Seattle Mariners",
                        "team_id": "12",
                        "sport": "baseball",
                        "is_local": True
                    },
                    {
                        "team_name": "Seattle Seahawks",
                        "team_id": "26",
                        "sport": "football",
                        "is_local": True
                    }
                ]
            }
        }


class ChatMessage(BaseModel):
    """Chat message from user."""
    message: str
    user_id: str = "default_user"
    preferences: Optional[UserPreferences] = None


class NewsItem(BaseModel):
    """Sports news item."""
    title: str
    description: str
    team: str
    sport: str
    importance: str  # "playoff" or "local"
    link: Optional[str] = None
    published: Optional[str] = None


class ChatMode(str, Enum):
    """Chat interaction mode."""
    REACTIVE = "reactive"  # User asks question
    PROACTIVE = "proactive"  # System provides news
