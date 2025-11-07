from fastapi import APIRouter, HTTPException
from models import UserPreferences, TeamPreference
from services.sports_news import SportsNewsService
from typing import List

router = APIRouter(prefix="/api/onboarding", tags=["onboarding"])
sports_service = SportsNewsService()


@router.get("/default-teams/{location}")
async def get_default_teams(location: str) -> UserPreferences:
    """
    Get default team preferences for a location.

    Currently supports:
    - Seattle: Mariners (MLB), Seahawks (NFL)
    """
    preferences = sports_service.get_default_preferences(location)

    if not preferences.teams:
        raise HTTPException(
            status_code=404,
            detail=f"No default teams configured for location: {location}"
        )

    return preferences


@router.post("/preferences")
async def save_preferences(preferences: UserPreferences) -> dict:
    """
    Save user preferences.

    In a real app, this would save to a database.
    For now, it just validates and returns the preferences.
    """
    return {
        "status": "success",
        "message": "Preferences saved successfully",
        "preferences": preferences
    }


@router.get("/available-locations")
async def get_available_locations() -> List[dict]:
    """Get list of available locations with team coverage."""
    return [
        {
            "name": "Seattle",
            "teams": ["Seattle Mariners (MLB)", "Seattle Seahawks (NFL)"]
        }
    ]
