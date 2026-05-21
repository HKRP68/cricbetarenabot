"""
Authentication & User Registration Middleware.
Runs BEFORE every handler. Registers new users and blocks banned ones.
"""
import logging
from telegram import Update
from telegram.ext import ContextTypes
from bot.database import db
logger = logging.getLogger(__name__)

async def auth_middleware(
   update: Update, context: ContextTypes.DEFAULT_TYPE
) -> None:
   """
   Pre-handler middleware:
   1. Extracts user from update
   2. Upserts user in database
   3. Blocks banned users
   4. Stores user data in context
   """
   user = update.effective_user
   if user is None:
     return
   if user.is_bot:
     return
   try:
     db_user = await db.upsert_user(
       telegram_id=user.id,
       username=user.username,
       first_name=user.first_name or "User",
       last_name=user.last_name,
       language_code=user.language_code,
     )
     # Block banned users
     if db_user.get("is_banned"):
       if update.effective_message:
          await update.effective_message.reply_text(
            "? Your account has been suspended."
          )
       logger.info("Blocked banned user: %d", user.id)
       return
     # Store in context for all handlers
     context.user_data["db_user"] = db_user
     context.user_data["is_premium"] = db_user.get("is_premium", False)
   except Exception as e:
     logger.error(
       "Auth middleware error for user %d: %s",
       user.id, e, exc_info=True,
     )
     # Continue even if DB fails (degraded mode)
