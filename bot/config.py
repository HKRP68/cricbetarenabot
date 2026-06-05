"""
Configuration module -- Single source of truth for ALL settings.
Reads from environment variables with sane defaults.
Every config value is validated on startup.
"""
import os
import sys
import logging
from dataclasses import dataclass, field
from typing import List, Optional
from urllib.parse import urlparse
logger = logging.getLogger(__name__)
@dataclass(frozen=True)
class Config:
   """Immutable application configuration."""
   # --- Telegram ---
   BOT_TOKEN: str = ""
   BOT_USERNAME: str = ""
   WEBHOOK_URL: str = ""
   WEBHOOK_SECRET: str = ""
   WEBHOOK_PATH: str = "/webhook"
   PORT: int = 8080
   # --- Supabase ---
   SUPABASE_URL: str = ""
   SUPABASE_KEY: str = "" # service_role key for full access
   # --- Cricket API (CricAPI v1) ---
   CRICKET_API_KEY: str = ""
   CRICKET_API_BASE: str = "https://api.cricapi.com/v1"
   # --- Admin ---
   ADMIN_IDS: List[int] = field(default_factory=list)
   ADMIN_CHAT_ID: int = 0
   # --- Betting Defaults (admin-editable via DB) ---
   MIN_BET_AMOUNT: int = 3 # ?3 minimum entry
   PLATFORM_COMMISSION_PCT: float = 16.67 # ~1? from 6? pool -> winner gets 5?
   MAX_BET_AMOUNT: int = 10000 # ?10,000 max single bet
   MAX_PLAYERS_PER_ROOM: int = 2 # Head-to-head default
   BET_LOCK_BEFORE_MATCH_MINS: int = 5 # Lock bets 5 min before match
   AUTO_CLOSE_ROOM_MINS: int = 30 # Auto-close unclaimed rooms
   # --- Rate Limiting ---
   RATE_LIMIT_MESSAGES: int = 20 # messages per window
   RATE_LIMIT_WINDOW: int = 60 # window in seconds
   RATE_LIMIT_PREMIUM_MULTI: float = 3.0 # premium users get 3x
   # --- Features ---
   FREE_CREDITS_ON_SIGNUP: int = 10 # ?10 welcome bonus
   REFERRAL_BONUS: int = 5 # ?5 per referral
   STREAK_BONUS_MULTIPLIER: float = 0.1 # 10% bonus per streak day
   MAX_STREAK_BONUS: float = 1.0 # Cap at 100% bonus
   DAILY_FREE_BET_AMOUNT: int = 1 # ?1 daily free bet
   LUCKY_SPIN_COOLDOWN_HOURS: int = 24
   MIN_WITHDRAWAL: int = 50 # ?50 minimum withdrawal
   # --- Notifications ---
   ENGAGEMENT_24H: bool = True
   ENGAGEMENT_72H: bool = True



   ENGAGEMENT_7D: bool = True

   # --- Logging ---
   LOG_LEVEL: str = "INFO"

   @property
   def normalized_webhook_path(self) -> str:
     """Return the webhook path without a leading slash for PTB routing."""
     return self.WEBHOOK_PATH.strip("/")

   @property
   def normalized_webhook_url(self) -> str:
     """Return a Telegram-compatible HTTPS webhook URL."""
     if not self.WEBHOOK_URL:
       return ""

     base_url = self.WEBHOOK_URL.strip().rstrip("/")
     if not urlparse(base_url).scheme:
       base_url = f"https://{base_url}"

     return f"{base_url}/{self.normalized_webhook_path}"

   def validate(self) -> bool:
     """Validate all required config values exist."""
     errors = []
     if not self.BOT_TOKEN:
       errors.append("BOT_TOKEN is required")
     if not self.SUPABASE_URL:
       errors.append("SUPABASE_URL is required")
     if not self.SUPABASE_KEY:
       errors.append("SUPABASE_KEY is required")
     if not self.CRICKET_API_KEY:
       errors.append("CRICKET_API_KEY is required")
     if not self.ADMIN_IDS:
       errors.append("ADMIN_IDS is required (comma-separated)")
     if self.WEBHOOK_URL and not self.normalized_webhook_path:
       errors.append("WEBHOOK_PATH must contain at least one non-slash character")
     if errors:
       for e in errors:
          logger.critical("CONFIG ERROR: %s", e)
       return False
     return True
def _parse_int_list(raw: str) -> List[int]:
   """Parse comma-separated string to list of ints."""
   if not raw:
     return []
   result = []
   for part in raw.split(","):
     part = part.strip()
     if part.isdigit():
       result.append(int(part))
   return result
def load_config() -> Config:
   """Load configuration from environment variables."""
   cfg = Config(
     BOT_TOKEN=os.getenv("BOT_TOKEN", ""),
     BOT_USERNAME=os.getenv("BOT_USERNAME", ""),
     WEBHOOK_URL=os.getenv("WEBHOOK_URL", ""),
     WEBHOOK_SECRET=os.getenv("WEBHOOK_SECRET", ""),
     WEBHOOK_PATH=os.getenv("WEBHOOK_PATH", "/webhook"),
     PORT=int(os.getenv("PORT", "8080")),
     SUPABASE_URL=os.getenv("SUPABASE_URL", ""),
     SUPABASE_KEY=os.getenv("SUPABASE_KEY", ""),
     CRICKET_API_KEY=os.getenv("CRICKET_API_KEY", ""),
     CRICKET_API_BASE=os.getenv(
       "CRICKET_API_BASE", "https://api.cricapi.com/v1"
     ),
     ADMIN_IDS=_parse_int_list(os.getenv("ADMIN_IDS", "")),
     ADMIN_CHAT_ID=int(os.getenv("ADMIN_CHAT_ID", "0")),
     MIN_BET_AMOUNT=int(os.getenv("MIN_BET_AMOUNT", "3")),
     PLATFORM_COMMISSION_PCT=float(
       os.getenv("PLATFORM_COMMISSION_PCT", "16.67")
     ),
     MAX_BET_AMOUNT=int(os.getenv("MAX_BET_AMOUNT", "10000")),
     MAX_PLAYERS_PER_ROOM=int(os.getenv("MAX_PLAYERS_PER_ROOM", "2")),
     BET_LOCK_BEFORE_MATCH_MINS=int(
       os.getenv("BET_LOCK_BEFORE_MATCH_MINS", "5")
     ),
     AUTO_CLOSE_ROOM_MINS=int(os.getenv("AUTO_CLOSE_ROOM_MINS", "30")),
     RATE_LIMIT_MESSAGES=int(os.getenv("RATE_LIMIT_MESSAGES", "20")),
     RATE_LIMIT_WINDOW=int(os.getenv("RATE_LIMIT_WINDOW", "60")),
     RATE_LIMIT_PREMIUM_MULTI=float(



       os.getenv("RATE_LIMIT_PREMIUM_MULTI", "3.0")
     ),
     FREE_CREDITS_ON_SIGNUP=int(
       os.getenv("FREE_CREDITS_ON_SIGNUP", "10")
     ),
     REFERRAL_BONUS=int(os.getenv("REFERRAL_BONUS", "5")),
     STREAK_BONUS_MULTIPLIER=float(
       os.getenv("STREAK_BONUS_MULTIPLIER", "0.1")
     ),
     MAX_STREAK_BONUS=float(os.getenv("MAX_STREAK_BONUS", "1.0")),
     DAILY_FREE_BET_AMOUNT=int(
       os.getenv("DAILY_FREE_BET_AMOUNT", "1")
     ),
     LUCKY_SPIN_COOLDOWN_HOURS=int(
       os.getenv("LUCKY_SPIN_COOLDOWN_HOURS", "24")
     ),
     MIN_WITHDRAWAL=int(os.getenv("MIN_WITHDRAWAL", "50")),
     LOG_LEVEL=os.getenv("LOG_LEVEL", "INFO"),
   )
   if not cfg.validate():
     logger.critical("Configuration validation failed. Exiting.")
     sys.exit(1)
   return cfg
# Singleton -- import this everywhere
config = load_config()
