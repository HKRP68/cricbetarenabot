"""
Main Entry Point -- Application bootstrap, handler registration,
webhook/polling setup, and graceful shutdown.
"""
import logging
import sys
from datetime import time, timezone, timedelta
from telegram import Update
from telegram.ext import (
   Application,
   CommandHandler,
   CallbackQueryHandler,
   MessageHandler,
   filters,
)
from bot.config import config
from bot.database import db
from bot.services.cricket_api import cricket_api
from bot.services.scheduler import (
   sync_matches_job,
   expire_rooms_job,
   engagement_notifications_job,
   daily_bonus_job,
   leaderboard_announcement_job,
)
# --- Configure Logging ---
logging.basicConfig(
   format="%(asctime)s | %(name)s | %(levelname)s | %(message)s",
   level=getattr(logging, config.LOG_LEVEL, logging.INFO),
   handlers=[logging.StreamHandler(sys.stdout)],
)
# Reduce noise from httpx/httpcore
logging.getLogger("httpx").setLevel(logging.WARNING)
logging.getLogger("httpcore").setLevel(logging.WARNING)
logger = logging.getLogger(__name__)
async def post_init(application: Application) -> None:
   """Initialize services after application starts."""
   logger.info("Initializing services...")
   # Initialize database
   await db.init()
   logger.info("[OK] Database initialized")
   # Initialize cricket API service
   await cricket_api.init()
   logger.info("[OK] Cricket API initialized")
   # Set bot commands
   await application.bot.set_my_commands([
     ("start", "? Start / Main Menu"),
     ("matches", "? Live & Upcoming Matches"),
     ("wallet", "? Your Wallet"),
     ("stats", "? Your Statistics"),
     ("leaderboard", "? Top Players"),
     ("help", "? How to Play"),
   ])



   logger.info("[OK] Bot commands set")

async def post_shutdown(application: Application) -> None:
   """Cleanup on shutdown."""
   logger.info("Shutting down services...")
   await cricket_api.close()
   logger.info("[OK] Services shut down")

async def error_handler(
   update: object, context
) -> None:
   """Global error handler. Catches all unhandled exceptions."""
   logger.error(
     "Unhandled exception: %s",
     context.error,
     exc_info=context.error,
   )
   # Try to notify user
   if isinstance(update, Update) and update.effective_message:
     try:
       await update.effective_message.reply_text(
          "[!]? Something went wrong. Please try /start again.\n"
          "If the problem persists, contact /support"
       )
     except Exception:
       pass
   # Notify admin
   if config.ADMIN_CHAT_ID:
     try:
       error_text = str(context.error)[:500]
       user_info = ""
       if isinstance(update, Update) and update.effective_user:
          user_info = (
            f"\nUser: {update.effective_user.id} "
            f"(@{update.effective_user.username})"
          )
       await context.bot.send_message(
          chat_id=config.ADMIN_CHAT_ID,
          text=(
            f"? <b>Bot Error</b>{user_info}\n\n"
            f"<code>{error_text}</code>"
          ),
          parse_mode="HTML",
       )
     except Exception:
       pass
def build_application() -> Application:
   """Build and configure the Telegram bot application."""
   logger.info("Building application...")
   builder = Application.builder().token(config.BOT_TOKEN)
   app = builder.build()
   # --- Post-init & Shutdown ---
   app.post_init = post_init
   app.post_shutdown = post_shutdown
   # --- Import Handlers ---
   from bot.handlers.start import (
     start_command,
     help_command,
     matches_command,
     wallet_command,
     stats_command,
     leaderboard_command,



   )
   from bot.handlers.callbacks import master_callback_handler
   from bot.handlers.admin import admin_command, handle_admin_text
   from bot.handlers.betting import handle_custom_bet_amount
   from bot.handlers.wallet import handle_withdraw_text
   # --- Import Middlewares ---
   from bot.middlewares.auth import auth_middleware
   from bot.middlewares.rate_limit import rate_limit_middleware
   from bot.middlewares.anti_fraud import anti_fraud_middleware
   # ===================================
   # MIDDLEWARE REGISTRATION (lower group = runs first)
   # ===================================
   # Group -2: Rate limiting (first -- cheapest check)
   app.add_handler(
     MessageHandler(filters.ALL, rate_limit_middleware),
     group=-2,
   )
   # Group -1: Authentication (register/update user)
   app.add_handler(
     MessageHandler(filters.ALL, auth_middleware),
     group=-1,
   )
   # ===================================
   # COMMAND HANDLERS (Group 0 -- default)
   # ===================================
   app.add_handler(CommandHandler("start", start_command))
   app.add_handler(CommandHandler("help", help_command))
   app.add_handler(CommandHandler("matches", matches_command))
   app.add_handler(CommandHandler("wallet", wallet_command))
   app.add_handler(CommandHandler("stats", stats_command))
   app.add_handler(CommandHandler("leaderboard", leaderboard_command))
   app.add_handler(CommandHandler("admin", admin_command))
   # ===================================
   # CALLBACK QUERY HANDLER (handles ALL buttons)
   # ===================================
   app.add_handler(CallbackQueryHandler(master_callback_handler))
   # ===================================
   # MESSAGE HANDLERS (Group 0 -- after commands)
   # ===================================
   # Admin text handler (broadcasts, config edits, etc.)
   app.add_handler(
     MessageHandler(
       filters.TEXT & ~filters.COMMAND & filters.User(
          user_id=config.ADMIN_IDS
       ),
       handle_admin_text,
     ),
     group=1,
   )
   # Custom bet amount text handler
   app.add_handler(
     MessageHandler(
       filters.TEXT & ~filters.COMMAND & filters.ChatType.PRIVATE,
       handle_custom_bet_amount,
     ),
     group=2,
   )
   # Withdrawal text handler
   app.add_handler(
     MessageHandler(
       filters.TEXT & ~filters.COMMAND & filters.ChatType.PRIVATE,



       handle_withdraw_text,
     ),
     group=3,
   )
   # ===================================
   # ERROR HANDLER
   # ===================================
   app.add_error_handler(error_handler)
   # ===================================
   # SCHEDULED JOBS
   # ===================================
   if app.job_queue:
     # Sync matches every 2 minutes
     app.job_queue.run_repeating(
       sync_matches_job,
       interval=120,
       first=10,
       name="sync_matches",
     )
     # Expire stale rooms every 5 minutes
     app.job_queue.run_repeating(
       expire_rooms_job,
       interval=300,
       first=30,
       name="expire_rooms",
     )
     # Engagement notifications every 6 hours
     app.job_queue.run_repeating(
       engagement_notifications_job,
       interval=21600,
       first=3600,
       name="engagement",
     )
     # Daily bonus at 9:00 AM IST (3:30 AM UTC)
     ist_offset = timedelta(hours=5, minutes=30)
     bonus_time = time(hour=3, minute=30, tzinfo=timezone.utc)
     app.job_queue.run_daily(
       daily_bonus_job,
       time=bonus_time,
       name="daily_bonus",
     )
     # Weekly leaderboard announcement (Sunday 8 PM IST = 2:30 PM UTC)
     lb_time = time(hour=14, minute=30, tzinfo=timezone.utc)
     app.job_queue.run_daily(
       leaderboard_announcement_job,
       time=lb_time,
       days=(6,), # Sunday
       name="weekly_leaderboard",
     )
     logger.info("[OK] Scheduled jobs registered")
   else:
     logger.warning("JobQueue not available -- scheduled jobs disabled")
   logger.info("[OK] Application built successfully")
   return app
def main() -> None:
   """Entry point. Runs webhook in production, polling in development."""
   app = build_application()
   if config.WEBHOOK_URL:
     # --- WEBHOOK MODE (Production/Render) ---
     logger.info(



       "Starting webhook on port %d at %s",
       config.PORT, config.WEBHOOK_URL,
     )
     webhook_url = f"{config.WEBHOOK_URL}{config.WEBHOOK_PATH}"

     app.run_webhook(
       listen="0.0.0.0",
       port=config.PORT,
       url_path=config.WEBHOOK_PATH,
       webhook_url=webhook_url,
       secret_token=config.WEBHOOK_SECRET or None,
       allowed_updates=Update.ALL_TYPES,
     )
   else:
     # --- POLLING MODE (Development) ---
     logger.info("Starting polling mode (development)...")
     app.run_polling(
       allowed_updates=Update.ALL_TYPES,
       drop_pending_updates=True,
     )
if __name__ == "__main__":
   main()
