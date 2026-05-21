"""
Rate Limiting Middleware.
Prevents spam and abuse. Premium users get higher limits.
"""
import logging
from telegram import Update
from telegram.ext import ContextTypes
from bot.services.rate_limiter import rate_limiter
logger = logging.getLogger(__name__)

async def rate_limit_middleware(
   update: Update, context: ContextTypes.DEFAULT_TYPE
) -> None:
   """Block users exceeding rate limit."""
   user = update.effective_user
   if user is None:
     return
   is_premium = context.user_data.get("is_premium", False)
   if not await rate_limiter.is_allowed(user.id, premium=is_premium):
     wait_time = await rate_limiter.get_wait_time(user.id)
     if update.effective_message:
       await update.effective_message.reply_text(
          f"?? Slow down! Wait {wait_time}s."
       )
