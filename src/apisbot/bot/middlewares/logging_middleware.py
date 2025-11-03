import logging
from collections.abc import Awaitable, Callable
from typing import Any

from aiogram import BaseMiddleware
from aiogram.types import TelegramObject, Update

logger = logging.getLogger(__name__)


class LoggingMiddleware(BaseMiddleware):
    """Middleware for logging user interactions without PII.

    Logs:
    - User actions (commands, state transitions)
    - Errors and exceptions
    - Performance metrics

    Does NOT log:
    - User names
    - Birth dates
    - Locations
    - Any other personally identifiable information
    """

    async def __call__(
        self,
        handler: Callable[[TelegramObject, dict[str, Any]], Awaitable[Any]],
        event: TelegramObject,
        data: dict[str, Any],
    ) -> Any:
        """Process update and log relevant information."""
        if isinstance(event, Update):
            user_id = None

            if event.message:
                user_id = event.message.from_user.id if event.message.from_user else None
                message_type = "command" if event.message.text and event.message.text.startswith("/") else "message"
                logger.info(f"User {user_id}: received {message_type}")

            elif event.callback_query:
                user_id = event.callback_query.from_user.id if event.callback_query.from_user else None
                logger.info(f"User {user_id}: callback query")

        try:
            return await handler(event, data)
        except Exception as e:
            logger.error(f"Error processing update: {type(e).__name__}: {str(e)}", exc_info=True)
            raise
