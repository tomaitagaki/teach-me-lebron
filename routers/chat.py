from fastapi import APIRouter, HTTPException
from fastapi.responses import StreamingResponse
from models import ChatMessage, UserPreferences, ChatMode, SportsClip
from services.openrouter import OpenRouterService
from services.sports_news import SportsNewsService
from services.clips_database import search_clips
import json
from typing import AsyncGenerator

router = APIRouter(prefix="/api/chat", tags=["chat"])
llm_service = OpenRouterService()
sports_service = SportsNewsService()


SPORTS_LORE_SYSTEM_PROMPT = """You are a sports expert who explains sports concepts, history, and lore in simple, clear terms.

Your goal is to help people who don't follow sports understand enough to participate in casual work conversations.

Guidelines:
- Explain things simply, avoiding jargon or explaining any jargon you use
- Use analogies and comparisons to make concepts relatable
- Keep responses concise but informative
- Add context about why something matters or is significant
- When relevant video clips are available, they will be shown automatically

Your audience wants to blend in at work, not become sports analysts. Keep it simple and practical."""

SPORTS_NEWS_SYSTEM_PROMPT = """You are a sports news summarizer who presents important sports news in simple, conversational language.

Your goal is to give busy people the key sports updates they need to know to chat with coworkers.

Guidelines:
- Summarize the news in 2-3 sentences per item
- Explain WHY it matters (playoffs implications, rivalry, historic achievement, etc.)
- Avoid technical jargon; use everyday language
- Focus on what someone would actually talk about at work
- For playoff news, explain what's at stake
- For local team news, add local context

Keep it brief, relatable, and conversational."""


async def create_sse_stream(content: str) -> AsyncGenerator[str, None]:
    """Create SSE formatted stream from static content."""
    yield f"data: {json.dumps({'type': 'start'})}\n\n"

    # Simulate token streaming for static content
    words = content.split()
    for i, word in enumerate(words):
        token = word if i == len(words) - 1 else word + " "
        yield f"data: {json.dumps({'type': 'token', 'content': token})}\n\n"

    yield f"data: {json.dumps({'type': 'done'})}\n\n"


async def stream_llm_response(
    messages: list[dict],
    system_prompt: str,
    clips: list[dict] = None
) -> AsyncGenerator[str, None]:
    """Stream LLM response as SSE events, optionally including video clips."""
    yield f"data: {json.dumps({'type': 'start'})}\n\n"

    try:
        async for token in llm_service.stream_chat_completion(messages, system_prompt):
            yield f"data: {json.dumps({'type': 'token', 'content': token})}\n\n"

        # After text is done, send clips if any
        if clips:
            for clip in clips:
                yield f"data: {json.dumps({'type': 'clip', 'clip': clip})}\n\n"

        yield f"data: {json.dumps({'type': 'done'})}\n\n"

    except Exception as e:
        error_msg = f"Error: {str(e)}"
        yield f"data: {json.dumps({'type': 'error', 'content': error_msg})}\n\n"


@router.post("/stream")
async def chat_stream(chat_message: ChatMessage):
    """
    Main chat endpoint with SSE streaming.

    Handles both:
    - Reactive: User asks questions about sports lore
    - Proactive: System shares important news when relevant
    """
    # Get user preferences (use defaults if not provided)
    preferences = chat_message.preferences
    if not preferences:
        preferences = sports_service.get_default_preferences("Seattle")

    # Detect if this is a request for news or a question
    message_lower = chat_message.message.lower()
    is_news_request = any(
        keyword in message_lower
        for keyword in ["news", "update", "happening", "latest", "recent", "what's new"]
    )

    if is_news_request:
        # Proactive mode: Fetch and summarize news
        news_items = await sports_service.get_important_news(preferences)

        if not news_items:
            async def no_news_stream():
                content = "There's no major news right now for your teams. All quiet on the sports front! Check back later or ask me anything about sports history and lore."
                async for chunk in create_sse_stream(content):
                    yield chunk

            return StreamingResponse(
                no_news_stream(),
                media_type="text/event-stream"
            )

        # Format news for LLM
        news_summary = "Here are the latest important sports updates:\n\n"
        for item in news_items:
            news_summary += f"**{item.team}** ({item.sport.upper()}) - {item.importance.upper()}\n"
            news_summary += f"Headline: {item.title}\n"
            if item.description:
                news_summary += f"Details: {item.description}\n"
            news_summary += "\n"

        messages = [
            {
                "role": "user",
                "content": f"Please summarize this sports news in a friendly, easy-to-understand way:\n\n{news_summary}"
            }
        ]

        return StreamingResponse(
            stream_llm_response(messages, SPORTS_NEWS_SYSTEM_PROMPT),
            media_type="text/event-stream"
        )

    else:
        # Reactive mode: Answer user's question

        # Search for relevant clips
        relevant_clips = search_clips(chat_message.message, max_results=2)

        # Add clip context to the message if found
        message_content = chat_message.message
        if relevant_clips:
            clip_context = "\n\n[Note: Relevant video clips are available and will be shown to the user automatically]"
            message_content += clip_context

        messages = [
            {
                "role": "user",
                "content": message_content
            }
        ]

        return StreamingResponse(
            stream_llm_response(messages, SPORTS_LORE_SYSTEM_PROMPT, clips=relevant_clips),
            media_type="text/event-stream"
        )


@router.post("/check-news")
async def check_proactive_news(preferences: UserPreferences):
    """
    Check if there's important news to proactively share.

    Returns whether to notify and a list of news items.
    """
    should_notify, news_items = await sports_service.check_for_proactive_news(preferences)

    return {
        "should_notify": should_notify,
        "news_count": len(news_items),
        "news_items": news_items
    }
