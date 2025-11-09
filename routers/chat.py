from fastapi import APIRouter, HTTPException
from fastapi.responses import StreamingResponse
from models import ChatMessage, UserPreferences, ChatMode, SportsClip
from services.openrouter import OpenRouterService
from services.sports_news import SportsNewsService
from services.clips_database import search_clips
from services.chat_history import ChatHistoryService
from logging_config import get_logger
import json
import httpx
from typing import AsyncGenerator

logger = get_logger(__name__)

router = APIRouter(prefix="/api/chat", tags=["chat"])
llm_service = OpenRouterService()
sports_service = SportsNewsService()
history_service = ChatHistoryService()


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

    full_response = ""
    try:
        async for token in llm_service.stream_chat_completion(messages, system_prompt):
            full_response += token
            yield f"data: {json.dumps({'type': 'token', 'content': token})}\n\n"

        # After text is done, send clips if any
        if clips:
            for clip in clips:
                yield f"data: {json.dumps({'type': 'clip', 'clip': clip})}\n\n"

        yield f"data: {json.dumps({'type': 'done'})}\n\n"

    except httpx.HTTPStatusError as e:
        logger.error(f"HTTP error in stream_llm_response: {e.response.status_code}")
        if e.response.status_code == 429:
            error_msg = "Rate limit exceeded. The free tier has limited requests. Please wait a moment and try again."
        elif e.response.status_code == 401:
            error_msg = "API authentication failed. Please check your OpenRouter API key."
        else:
            error_msg = f"API error ({e.response.status_code}). Please try again."
        yield f"data: {json.dumps({'type': 'error', 'content': error_msg})}\n\n"
    except httpx.RequestError as e:
        logger.error(f"Request error in stream_llm_response: {str(e)}")
        error_msg = "Network error. Please check your connection and try again."
        yield f"data: {json.dumps({'type': 'error', 'content': error_msg})}\n\n"
    except Exception as e:
        logger.error(f"Unexpected error in stream_llm_response: {str(e)}", exc_info=True)
        error_msg = f"An unexpected error occurred: {str(e)}"
        yield f"data: {json.dumps({'type': 'error', 'content': error_msg})}\n\n"


async def stream_with_history(
    user_id: str,
    user_message: str,
    generator: AsyncGenerator[str, None],
    clips: list[dict] = None
) -> AsyncGenerator[str, None]:
    """Wrapper that saves chat history while streaming."""
    full_response = ""

    async for chunk in generator:
        # Extract content from SSE data if present
        if chunk.startswith("data: "):
            try:
                data = json.loads(chunk[6:])
                if data.get("type") == "token" and "content" in data:
                    full_response += data["content"]
            except:
                pass
        yield chunk

    # Save to history after streaming is complete
    if full_response:
        history_service.add_message(user_id, "assistant", full_response, clips)
        logger.debug(f"Saved assistant response to history for user {user_id}")


@router.post("/stream")
async def chat_stream(chat_message: ChatMessage):
    """
    Main chat endpoint with SSE streaming.

    Handles both:
    - Reactive: User asks questions about sports lore
    - Proactive: System shares important news when relevant
    """
    user_id = chat_message.user_id
    logger.info(f"Chat stream request from user {user_id}: {chat_message.message[:50]}...")

    # Save user message to history
    history_service.add_message(user_id, "user", chat_message.message)

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
        logger.debug("Processing as news request")
        news_items = await sports_service.get_important_news(preferences)

        if not news_items:
            async def no_news_stream():
                content = "There's no major news right now for your teams. All quiet on the sports front! Check back later or ask me anything about sports history and lore."
                history_service.add_message(user_id, "assistant", content)
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
            stream_with_history(
                user_id,
                chat_message.message,
                stream_llm_response(messages, SPORTS_NEWS_SYSTEM_PROMPT)
            ),
            media_type="text/event-stream"
        )

    else:
        # Reactive mode: Answer user's question
        logger.debug("Processing as Q&A request")

        # Get conversation history for context
        conversation_history = history_service.get_context_for_llm(user_id, max_messages=8)
        logger.debug(f"Loaded {len(conversation_history)} messages from history for context")

        # Search for relevant clips
        relevant_clips = search_clips(chat_message.message, max_results=2)
        if relevant_clips:
            logger.debug(f"Found {len(relevant_clips)} relevant clips")

        # Add clip context to the current message if found
        current_message = chat_message.message
        if relevant_clips:
            clip_context = "\n\n[Note: Relevant video clips are available and will be shown to the user automatically]"
            current_message += clip_context

        # Combine history with current message
        messages = conversation_history + [
            {
                "role": "user",
                "content": current_message
            }
        ]

        return StreamingResponse(
            stream_with_history(
                user_id,
                chat_message.message,
                stream_llm_response(messages, SPORTS_LORE_SYSTEM_PROMPT, clips=relevant_clips),
                clips=relevant_clips
            ),
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


@router.get("/history/{user_id}")
async def get_chat_history(user_id: str, limit: int = 50):
    """
    Get chat history for a user.

    Args:
        user_id: User identifier
        limit: Maximum number of messages to return (default 50)

    Returns:
        List of messages with role, content, clips, and timestamp
    """
    logger.debug(f"Fetching chat history for user {user_id}, limit {limit}")

    try:
        history = history_service.get_conversation_history(
            user_id,
            limit=limit,
            include_clips=True
        )

        return {
            "user_id": user_id,
            "messages": history,
            "total": len(history)
        }
    except Exception as e:
        logger.error(f"Error fetching chat history: {str(e)}", exc_info=True)
        raise HTTPException(status_code=500, detail="Failed to fetch chat history")


@router.delete("/history/{user_id}")
async def clear_chat_history(user_id: str):
    """
    Clear all chat history for a user.

    Args:
        user_id: User identifier

    Returns:
        Number of messages deleted
    """
    logger.info(f"Clearing chat history for user {user_id}")

    try:
        deleted_count = history_service.clear_history(user_id)

        return {
            "user_id": user_id,
            "deleted_count": deleted_count,
            "status": "success"
        }
    except Exception as e:
        logger.error(f"Error clearing chat history: {str(e)}", exc_info=True)
        raise HTTPException(status_code=500, detail="Failed to clear chat history")
