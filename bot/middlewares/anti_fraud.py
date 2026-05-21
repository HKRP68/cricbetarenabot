"""
Anti-Fraud Middleware -- Advanced fraud detection.
Detects suspicious patterns and prevents exploitation.
"""
import logging
import time
from collections import defaultdict
from typing import Dict, List, Set
from telegram import Update
from telegram.ext import ContextTypes
from bot.config import config
from bot.database import db
logger = logging.getLogger(__name__)

class AntiFraudEngine:
   """Detects and prevents various fraud patterns."""
   def __init__(self):
     # Track rapid betting patterns
     self._bet_timestamps: Dict[int, List[float]] = defaultdict(list)
     # Track devices/sessions per user
     self._suspicious_users: Set[int] = set()
     # Multi-account detection (same first interaction patterns)
     self._recent_starts: Dict[str, List[int]] = defaultdict(list)
   async def check_bet_fraud(
     self, user_id: int, amount: int, match_id: str
   ) -> tuple[bool, str]:
     """
     Check for suspicious betting patterns.
     Returns (is_safe, reason).
     """
     now = time.time()
     # 1. Rapid fire bet detection
     self._bet_timestamps[user_id].append(now)
     recent = [
       t for t in self._bet_timestamps[user_id]
       if now - t < 60 # Last 60 seconds
     ]
     self._bet_timestamps[user_id] = recent
     if len(recent) > 10:
       logger.warning(
          "FRAUD: Rapid betting detected user=%d, "
          "%d bets in 60s", user_id, len(recent)
       )
       return False, "Too many bets too quickly. Please slow down."
     # 2. Self-matching prevention
     # (Already handled in DB layer: can't join own room)
     # 3. Suspicious high-value bets from new users
     user = await db.get_user(user_id)
     if user:
       from datetime import datetime, timezone, timedelta
       created = user.get("created_at", "")
       if created:
          try:



            created_dt = datetime.fromisoformat(
              created.replace("Z", "+00:00")
            )
            age_hours = (
              datetime.now(timezone.utc) - created_dt
            ).total_seconds() / 3600
            if age_hours < 1 and amount > 100:
              logger.warning(
                 "FRAUD: New user %d placing large bet "
                 "?%d within first hour", user_id, amount
              )
              return False, (
                 "New accounts must wait 1 hour before "
                 "placing bets over ?100."
              )
          except (ValueError, TypeError):
            pass
       # 4. Check total bets today (abuse limit)
       total_today = user.get("bets_today", 0)
       max_daily = 100 # Max 100 bets per day
       if total_today > max_daily:
          return False, (
            f"Daily bet limit reached ({max_daily}/day). "
            f"Try again tomorrow!"
          )
     # 5. Check if user is in suspicious list
     if user_id in self._suspicious_users:
       logger.warning(
          "FRAUD: Suspicious user %d attempting bet", user_id
       )
       return False, "Account under review. Contact support."
     return True, ""
   def flag_user(self, user_id: int) -> None:
     """Flag a user as suspicious."""
     self._suspicious_users.add(user_id)
     logger.warning("FRAUD: User %d flagged as suspicious", user_id)
   def unflag_user(self, user_id: int) -> None:
     """Remove suspicious flag."""
     self._suspicious_users.discard(user_id)
   async def check_multi_account(
     self, user_id: int, referral_code: str = ""
   ) -> bool:
     """
     Detect multi-account abuse.
     Checks for suspicious patterns in rapid account creation.
     """
     if referral_code:
       now = time.time()
       self._recent_starts[referral_code].append(user_id)
       # Cleanup old entries
       self._recent_starts[referral_code] = [
          uid for uid in self._recent_starts[referral_code]
       ][-20:] # Keep last 20
       # If more than 5 signups with same referral in short time
       if len(self._recent_starts[referral_code]) > 5:
          logger.warning(
            "FRAUD: Possible multi-account via referral %s: "
            "%d signups",
            referral_code,
            len(self._recent_starts[referral_code]),
          )
          return False
     return True





# Singleton
anti_fraud = AntiFraudEngine()

async def anti_fraud_middleware(
   update: Update, context: ContextTypes.DEFAULT_TYPE
) -> None:
   """Anti-fraud check middleware. Runs on every update."""
   user = update.effective_user
   if user is None:
     return
   if user.id in anti_fraud._suspicious_users:
     if update.effective_message:
       await update.effective_message.reply_text(
          "[!]? Your account is under review. "
          "Contact support for assistance."
       )
