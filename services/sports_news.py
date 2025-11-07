import httpx
from typing import List
from datetime import datetime, timedelta
from models import NewsItem, UserPreferences, TeamPreference
from config import get_settings


class SportsNewsService:
    """Service for fetching sports news from ESPN API."""

    def __init__(self):
        self.settings = get_settings()
        self.base_url = self.settings.sports_api_base_url

        # Team mappings for Seattle defaults
        self.seattle_teams = {
            "baseball": {
                "name": "Seattle Mariners",
                "id": "12",
                "league": "mlb"
            },
            "football": {
                "name": "Seattle Seahawks",
                "id": "26",
                "league": "nfl"
            }
        }

    def get_default_preferences(self, location: str = "Seattle") -> UserPreferences:
        """Get default team preferences for a location."""
        if location.lower() == "seattle":
            teams = [
                TeamPreference(
                    team_name=self.seattle_teams["baseball"]["name"],
                    team_id=self.seattle_teams["baseball"]["id"],
                    sport="baseball",
                    is_local=True
                ),
                TeamPreference(
                    team_name=self.seattle_teams["football"]["name"],
                    team_id=self.seattle_teams["football"]["id"],
                    sport="football",
                    is_local=True
                )
            ]
            return UserPreferences(location=location, teams=teams)

        # For other locations, return empty (could expand this)
        return UserPreferences(location=location, teams=[])

    async def fetch_team_news(
        self,
        sport: str,
        team_id: str,
        team_name: str,
        is_local: bool = False
    ) -> List[NewsItem]:
        """Fetch news for a specific team."""
        news_items = []

        # Map sport to ESPN league
        league_map = {
            "baseball": "mlb",
            "football": "nfl",
            "basketball": "nba",
            "hockey": "nhl"
        }

        league = league_map.get(sport.lower())
        if not league:
            return news_items

        async with httpx.AsyncClient(timeout=30.0) as client:
            try:
                # Fetch team info and recent games
                url = f"{self.base_url}/{league}/teams/{team_id}"
                response = await client.get(url)
                response.raise_for_status()
                data = response.json()

                # Check for playoffs or important games
                team_data = data.get("team", {})

                # Fetch recent news/headlines
                news_url = f"{self.base_url}/{league}/news"
                news_response = await client.get(news_url)

                if news_response.status_code == 200:
                    news_data = news_response.json()
                    articles = news_data.get("articles", [])[:5]

                    for article in articles:
                        # Filter for team-related news
                        headline = article.get("headline", "")
                        description = article.get("description", "")

                        if team_name.lower() in headline.lower() or team_name.lower() in description.lower():
                            # Determine importance
                            importance = "local" if is_local else "general"
                            if any(keyword in headline.lower() for keyword in ["playoff", "championship", "finals", "wildcard"]):
                                importance = "playoff"

                            news_items.append(NewsItem(
                                title=headline,
                                description=description,
                                team=team_name,
                                sport=sport,
                                importance=importance,
                                link=article.get("links", {}).get("web", {}).get("href"),
                                published=article.get("published")
                            ))

            except Exception as e:
                print(f"Error fetching news for {team_name}: {e}")

        return news_items

    async def get_important_news(
        self,
        preferences: UserPreferences
    ) -> List[NewsItem]:
        """
        Get important news based on user preferences.

        Only returns playoff news or local team news.
        """
        all_news = []

        for team in preferences.teams:
            team_news = await self.fetch_team_news(
                sport=team.sport,
                team_id=team.team_id,
                team_name=team.team_name,
                is_local=team.is_local
            )
            all_news.extend(team_news)

        # Filter to only important news (playoff or local)
        important_news = [
            news for news in all_news
            if news.importance in ["playoff", "local"]
        ]

        # Sort by importance (playoff first) and limit
        important_news.sort(
            key=lambda x: (0 if x.importance == "playoff" else 1)
        )

        return important_news[:5]  # Limit to top 5 items

    async def check_for_proactive_news(
        self,
        preferences: UserPreferences
    ) -> tuple[bool, List[NewsItem]]:
        """
        Check if there's important news worth proactively sharing.

        Returns: (should_notify, news_items)
        """
        news = await self.get_important_news(preferences)

        # Only proactively notify if there's playoff news or significant local news
        should_notify = len(news) > 0 and any(
            item.importance == "playoff" for item in news
        )

        return should_notify, news
