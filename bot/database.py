"""
Database module -- All Supabase interactions.
Uses async client for non-blocking operations.
Every query is parameterized. Zero SQL injection vectors.
"""
import logging
from datetime import datetime, timedelta, date, timezone
from typing import Any, Dict, List, Optional, Tuple
from decimal import Decimal
from supabase import AsyncClient, acreate_client
from bot.config import config
from bot.constants import (
   RoomStatus, TxnType, MatchStatus, DEFAULT_BET_TIERS, SPIN_PRIZES
)
logger = logging.getLogger(__name__)
class Database:
   """Async Supabase database wrapper with all bot operations."""

   def __init__(self):
     self._client: Optional[AsyncClient] = None
   async def init(self) -> None:
     """Initialize the async Supabase client."""
     try:
       self._client = await acreate_client(
          config.SUPABASE_URL,
          config.SUPABASE_KEY,
       )
       logger.info("Database connection established")
     except Exception as e:
       logger.critical("Failed to connect to Supabase: %s", e)
       raise
   @property
   def client(self) -> AsyncClient:
     if self._client is None:
       raise RuntimeError("Database not initialized. Call db.init() first.")
     return self._client
   async def health_check(self) -> bool:
     """Quick health check -- used by /health endpoint."""
     try:
       result = await (
          self.client.table("users")
          .select("id", count="exact")
          .limit(1)
          .execute()
       )
       return True
     except Exception as e:
       logger.error("Health check failed: %s", e)
       return False
   # =======================================
   # USER OPERATIONS
   # =======================================
   async def upsert_user(



     self,
     telegram_id: int,
     username: Optional[str],
     first_name: str,
     last_name: Optional[str] = None,
     language_code: Optional[str] = None,
   ) -> Dict[str, Any]:
     """Create or update user. Returns user dict."""
     try:
       data = {
          "telegram_id": telegram_id,
          "username": username or "",
          "first_name": first_name or "User",
          "last_name": last_name or "",
          "language_code": language_code or "en",
          "last_seen": datetime.now(timezone.utc).isoformat(),
          "last_active_date": date.today().isoformat(),
       }
       result = await (
          self.client.table("users")
          .upsert(data, on_conflict="telegram_id")
          .execute()
       )
       if result.data:
          return result.data[0]
       return data
     except Exception as e:
       logger.error("upsert_user error for %d: %s", telegram_id, e)
       raise
   async def get_user(self, telegram_id: int) -> Optional[Dict[str, Any]]:
     """Get user by telegram_id."""
     try:
       result = await (
          self.client.table("users")
          .select("*")
          .eq("telegram_id", telegram_id)
          .limit(1)
          .execute()
       )
       return result.data[0] if result.data else None
     except Exception as e:
       logger.error("get_user error: %s", e)
       return None
   async def get_user_count(self) -> int:
     """Get total registered user count."""
     try:
       result = await (
          self.client.table("users")
          .select("id", count="exact")
          .execute()
       )
       return result.count or 0
     except Exception:
       return 0
   async def update_user(
     self, telegram_id: int, data: Dict[str, Any]
   ) -> Optional[Dict[str, Any]]:
     """Update user fields."""
     try:
       result = await (
          self.client.table("users")
          .update(data)
          .eq("telegram_id", telegram_id)
          .execute()
       )
       return result.data[0] if result.data else None
     except Exception as e:
       logger.error("update_user error: %s", e)
       return None



   async def ban_user(self, telegram_id: int) -> bool:
     """Ban a user."""
     try:
       await (
          self.client.table("users")
          .update({"is_banned": True})
          .eq("telegram_id", telegram_id)
          .execute()
       )
       return True
     except Exception as e:
       logger.error("ban_user error: %s", e)
       return False
   async def unban_user(self, telegram_id: int) -> bool:
     """Unban a user."""
     try:
       await (
          self.client.table("users")
          .update({"is_banned": False})
          .eq("telegram_id", telegram_id)
          .execute()
       )
       return True
     except Exception as e:
       logger.error("unban_user error: %s", e)
       return False
   # =======================================
   # WALLET OPERATIONS
   # =======================================
   async def get_balance(self, telegram_id: int) -> int:
     """Get user's wallet balance."""
     user = await self.get_user(telegram_id)
     if user:
       return user.get("balance", 0)
     return 0
   async def credit_wallet(
     self,
     telegram_id: int,
     amount: int,
     txn_type: TxnType,
     description: str = "",
     reference_id: str = "",
   ) -> Tuple[bool, int]:
     """
     Add money to user's wallet with transaction record.
     Returns (success, new_balance).
     Uses RPC for atomic operation.
     """
     try:
       # Record transaction first
       txn_data = {
          "user_id": telegram_id,
          "amount": amount,
          "txn_type": txn_type.value,
          "direction": "credit",
          "description": description,
          "reference_id": reference_id,
       }
       await self.client.table("transactions").insert(txn_data).execute()
       # Update balance atomically using RPC
       result = await self.client.rpc(
          "credit_balance",
          {"p_telegram_id": telegram_id, "p_amount": amount}
       ).execute()
       new_balance = result.data if isinstance(result.data, int) else amount
       return True, new_balance



     except Exception as e:
       logger.error(
          "credit_wallet error user=%d amount=%d: %s",
          telegram_id, amount, e
       )
       return False, 0
   async def debit_wallet(
     self,
     telegram_id: int,
     amount: int,
     txn_type: TxnType,
     description: str = "",
     reference_id: str = "",
   ) -> Tuple[bool, int]:
     """
     Remove money from wallet. Checks balance first.
     Returns (success, new_balance).
     """
     try:
       # Check balance first
       current = await self.get_balance(telegram_id)
       if current < amount:
          return False, current
       txn_data = {
          "user_id": telegram_id,
          "amount": amount,
          "txn_type": txn_type.value,
          "direction": "debit",
          "description": description,
          "reference_id": reference_id,
       }
       await self.client.table("transactions").insert(txn_data).execute()
       result = await self.client.rpc(
          "debit_balance",
          {"p_telegram_id": telegram_id, "p_amount": amount}
       ).execute()
       new_balance = result.data if isinstance(result.data, int) else (current - amount)
       return True, new_balance
     except Exception as e:
       logger.error(
          "debit_wallet error user=%d amount=%d: %s",
          telegram_id, amount, e
       )
       return False, 0
   async def get_transactions(
     self,
     telegram_id: int,
     limit: int = 20,
     offset: int = 0,
   ) -> List[Dict[str, Any]]:
     """Get user's transaction history."""
     try:
       result = await (
          self.client.table("transactions")
          .select("*")
          .eq("user_id", telegram_id)
          .order("created_at", desc=True)
          .range(offset, offset + limit - 1)
          .execute()
       )
       return result.data or []
     except Exception as e:
       logger.error("get_transactions error: %s", e)
       return []
   # =======================================
   # MATCH OPERATIONS



   # =======================================

   async def upsert_match(self, match_data: Dict[str, Any]) -> Dict[str, Any]:
     """Insert or update match from cricket API."""
     try:
       result = await (
          self.client.table("matches")
          .upsert(match_data, on_conflict="api_match_id")
          .execute()
       )
       return result.data[0] if result.data else match_data
     except Exception as e:
       logger.error("upsert_match error: %s", e)
       raise
   async def get_live_matches(self) -> List[Dict[str, Any]]:
     """Get currently live matches."""
     try:
       result = await (
          self.client.table("matches")
          .select("*")
          .eq("status", MatchStatus.LIVE.value)
          .order("match_start", desc=False)
          .execute()
       )
       return result.data or []
     except Exception as e:
       logger.error("get_live_matches error: %s", e)
       return []
   async def get_upcoming_matches(self, limit: int = 20) -> List[Dict[str, Any]]:
     """Get upcoming matches."""
     try:
       now = datetime.now(timezone.utc).isoformat()
       result = await (
          self.client.table("matches")
          .select("*")
          .eq("status", MatchStatus.UPCOMING.value)
          .gte("match_start", now)
          .order("match_start", desc=False)
          .limit(limit)
          .execute()
       )
       return result.data or []
     except Exception as e:
       logger.error("get_upcoming_matches error: %s", e)
       return []
   async def get_match(self, match_id: str) -> Optional[Dict[str, Any]]:
     """Get single match by ID."""
     try:
       result = await (
          self.client.table("matches")
          .select("*")
          .eq("id", match_id)
          .limit(1)
          .execute()
       )
       return result.data[0] if result.data else None
     except Exception as e:
       logger.error("get_match error: %s", e)
       return None
   async def get_match_by_api_id(
     self, api_match_id: str
   ) -> Optional[Dict[str, Any]]:
     """Get match by external API ID."""
     try:
       result = await (
          self.client.table("matches")
          .select("*")
          .eq("api_match_id", api_match_id)
          .limit(1)



          .execute()
       )
       return result.data[0] if result.data else None
     except Exception as e:
       logger.error("get_match_by_api_id error: %s", e)
       return None
   # =======================================
   # BETTING ROOM OPERATIONS
   # =======================================
   async def create_room(
     self,
     match_id: str,
     creator_id: int,
     bet_type: str,
     bet_amount: int,
     win_amount: int,
     creator_pick: str,
   ) -> Optional[Dict[str, Any]]:
     """Create a new betting room."""
     try:
       room_data = {
          "match_id": match_id,
          "creator_id": creator_id,
          "bet_type": bet_type,
          "bet_amount": bet_amount,
          "win_amount": win_amount,
          "pool_amount": bet_amount,
          "creator_pick": creator_pick,
          "status": RoomStatus.OPEN.value,
          "max_players": 2,
       }
       result = await (
          self.client.table("rooms")
          .insert(room_data)
          .execute()
       )
       return result.data[0] if result.data else None
     except Exception as e:
       logger.error("create_room error: %s", e)
       return None
   async def join_room(
     self,
     room_id: str,
     joiner_id: int,
     joiner_pick: str,
   ) -> Optional[Dict[str, Any]]:
     """Join an existing room. Atomic check-and-update."""
     try:
       # First verify room is still open and not by same user
       room = await self.get_room(room_id)
       if not room:
          return None
       if room["status"] != RoomStatus.OPEN.value:
          return None
       if room["creator_id"] == joiner_id:
          return None
       if room.get("joiner_id"):
          return None
       # Update room
       update_data = {
          "joiner_id": joiner_id,
          "joiner_pick": joiner_pick,
          "status": RoomStatus.LOCKED.value,
          "pool_amount": room["bet_amount"] * 2,
          "joined_at": datetime.now(timezone.utc).isoformat(),
       }
       result = await (
          self.client.table("rooms")
          .update(update_data)



          .eq("id", room_id)
          .eq("status", RoomStatus.OPEN.value) # Optimistic lock
          .execute()
       )
       return result.data[0] if result.data else None
     except Exception as e:
       logger.error("join_room error: %s", e)
       return None
   async def get_room(self, room_id: str) -> Optional[Dict[str, Any]]:
     """Get room by ID."""
     try:
       result = await (
          self.client.table("rooms")
          .select("*")
          .eq("id", room_id)
          .limit(1)
          .execute()
       )
       return result.data[0] if result.data else None
     except Exception as e:
       logger.error("get_room error: %s", e)
       return None
   async def get_open_rooms(
     self,
     match_id: str,
     bet_type: Optional[str] = None,
     exclude_user: Optional[int] = None,
   ) -> List[Dict[str, Any]]:
     """Get open rooms for a match."""
     try:
       query = (
          self.client.table("rooms")
          .select("*")
          .eq("match_id", match_id)
          .eq("status", RoomStatus.OPEN.value)
       )
       if bet_type:
          query = query.eq("bet_type", bet_type)
       if exclude_user:
          query = query.neq("creator_id", exclude_user)
       result = await query.order("created_at", desc=False).execute()
       return result.data or []
     except Exception as e:
       logger.error("get_open_rooms error: %s", e)
       return []
   async def get_user_active_rooms(
     self, telegram_id: int
   ) -> List[Dict[str, Any]]:
     """Get all active rooms for a user (as creator or joiner)."""
     try:
       # Rooms where user is creator
       r1 = await (
          self.client.table("rooms")
          .select("*")
          .eq("creator_id", telegram_id)
          .in_("status", [RoomStatus.OPEN.value, RoomStatus.LOCKED.value])
          .execute()
       )
       # Rooms where user is joiner
       r2 = await (
          self.client.table("rooms")
          .select("*")
          .eq("joiner_id", telegram_id)
          .in_("status", [RoomStatus.OPEN.value, RoomStatus.LOCKED.value])
          .execute()
       )
       rooms = (r1.data or []) + (r2.data or [])
       return rooms
     except Exception as e:



       logger.error("get_user_active_rooms error: %s", e)
       return []
   async def settle_room(
     self,
     room_id: str,
     winner_id: int,
     result_text: str,
   ) -> bool:
     """Settle a room -- declare winner and update status."""
     try:
       update_data = {
          "status": RoomStatus.SETTLED.value,
          "winner_id": winner_id,
          "result_text": result_text,
          "settled_at": datetime.now(timezone.utc).isoformat(),
       }
       await (
          self.client.table("rooms")
          .update(update_data)
          .eq("id", room_id)
          .execute()
       )
       return True
     except Exception as e:
       logger.error("settle_room error: %s", e)
       return False
   async def cancel_room(self, room_id: str, reason: str = "") -> bool:
     """Cancel a room and mark for refund."""
     try:
       await (
          self.client.table("rooms")
          .update({
            "status": RoomStatus.CANCELLED.value,
            "result_text": f"Cancelled: {reason}",
            "settled_at": datetime.now(timezone.utc).isoformat(),
          })
          .eq("id", room_id)
          .execute()
       )
       return True
     except Exception as e:
       logger.error("cancel_room error: %s", e)
       return False
   async def expire_stale_rooms(self, minutes: int = 30) -> List[Dict[str, Any]]:
     """Expire rooms that have been open too long without opponent."""
     try:
       cutoff = (
          datetime.now(timezone.utc) - timedelta(minutes=minutes)
       ).isoformat()
       result = await (
          self.client.table("rooms")
          .update({
            "status": RoomStatus.EXPIRED.value,
            "result_text": "Expired: No opponent joined",
            "settled_at": datetime.now(timezone.utc).isoformat(),
          })
          .eq("status", RoomStatus.OPEN.value)
          .is_("joiner_id", "null")
          .lt("created_at", cutoff)
          .execute()
       )
       return result.data or []
     except Exception as e:
       logger.error("expire_stale_rooms error: %s", e)
       return []
   async def get_rooms_for_match(
     self, match_id: str
   ) -> List[Dict[str, Any]]:
     """Get all locked rooms for a match (for settlement)."""



     try:
       result = await (
          self.client.table("rooms")
          .select("*")
          .eq("match_id", match_id)
          .eq("status", RoomStatus.LOCKED.value)
          .execute()
       )
       return result.data or []
     except Exception as e:
       logger.error("get_rooms_for_match error: %s", e)
       return []
   # =======================================
   # BET HISTORY
   # =======================================
   async def get_user_bet_history(
     self,
     telegram_id: int,
     limit: int = 20,
     offset: int = 0,
   ) -> List[Dict[str, Any]]:
     """Get user's bet history with match details."""
     try:
       # Get rooms where user participated
       r1 = await (
          self.client.table("rooms")
          .select("*, matches(*)")
          .eq("creator_id", telegram_id)
          .order("created_at", desc=True)
          .range(offset, offset + limit - 1)
          .execute()
       )
       r2 = await (
          self.client.table("rooms")
          .select("*, matches(*)")
          .eq("joiner_id", telegram_id)
          .order("created_at", desc=True)
          .range(offset, offset + limit - 1)
          .execute()
       )
       all_rooms = (r1.data or []) + (r2.data or [])
       all_rooms.sort(key=lambda x: x.get("created_at", ""), reverse=True)
       return all_rooms[:limit]
     except Exception as e:
       logger.error("get_user_bet_history error: %s", e)
       return []
   async def get_user_stats(self, telegram_id: int) -> Dict[str, Any]:
     """Get comprehensive user stats."""
     try:
       user = await self.get_user(telegram_id)
       if not user:
          return {}
       # Count wins
       wins_r = await (
          self.client.table("rooms")
          .select("id", count="exact")
          .eq("winner_id", telegram_id)
          .eq("status", RoomStatus.SETTLED.value)
          .execute()
       )
       wins = wins_r.count or 0
       # Count total settled bets
       total_c = await (
          self.client.table("rooms")
          .select("id", count="exact")
          .eq("creator_id", telegram_id)
          .eq("status", RoomStatus.SETTLED.value)
          .execute()



       )
       total_j = await (
          self.client.table("rooms")
          .select("id", count="exact")
          .eq("joiner_id", telegram_id)
          .eq("status", RoomStatus.SETTLED.value)
          .execute()
       )
       total = (total_c.count or 0) + (total_j.count or 0)
       win_rate = round((wins / total * 100), 1) if total > 0 else 0.0
       return {
          **user,
          "total_bets": total,
          "wins": wins,
          "losses": total - wins,
          "win_rate": win_rate,
       }
     except Exception as e:
       logger.error("get_user_stats error: %s", e)
       return {}
   # =======================================
   # LEADERBOARD
   # =======================================
   async def get_leaderboard(
     self, limit: int = 10
   ) -> List[Dict[str, Any]]:
     """Get top winners leaderboard."""
     try:
       result = await (
          self.client.table("users")
          .select("telegram_id, username, first_name, total_winnings, wins_count, streak_days")
          .order("total_winnings", desc=True)
          .gt("total_winnings", 0)
          .limit(limit)
          .execute()
       )
       return result.data or []
     except Exception as e:
       logger.error("get_leaderboard error: %s", e)
       return []
   # =======================================
   # STREAKS & ENGAGEMENT
   # =======================================
   async def update_streak(self, telegram_id: int) -> int:
     """Update daily streak. Returns new streak count."""
     try:
       user = await self.get_user(telegram_id)
       if not user:
          return 0
       today = date.today()
       last_active = user.get("last_active_date")
       if last_active:
          if isinstance(last_active, str):
            last_active = date.fromisoformat(last_active)
          if last_active == today:
            return user.get("streak_days", 0)
          elif last_active == today - timedelta(days=1):
            new_streak = user.get("streak_days", 0) + 1
          else:
            new_streak = 1
       else:
          new_streak = 1
       await self.update_user(telegram_id, {



          "streak_days": new_streak,
          "last_active_date": today.isoformat(),
       })
       return new_streak
     except Exception as e:
       logger.error("update_streak error: %s", e)
       return 0
   async def record_spin(self, telegram_id: int, prize: int) -> bool:
     """Record a lucky spin."""
     try:
       await (
          self.client.table("spins")
          .insert({
            "user_id": telegram_id,
            "prize_amount": prize,
          })
          .execute()
       )
       return True
     except Exception as e:
       logger.error("record_spin error: %s", e)
       return False
   async def can_spin(self, telegram_id: int) -> bool:
     """Check if user can spin (cooldown check)."""
     try:
       cutoff = (
          datetime.now(timezone.utc) -
          timedelta(hours=config.LUCKY_SPIN_COOLDOWN_HOURS)
       ).isoformat()
       result = await (
          self.client.table("spins")
          .select("id", count="exact")
          .eq("user_id", telegram_id)
          .gte("created_at", cutoff)
          .execute()
       )
       return (result.count or 0) == 0
     except Exception as e:
       logger.error("can_spin error: %s", e)
       return False
   # =======================================
   # REFERRALS
   # =======================================
   async def process_referral(
     self, new_user_id: int, referrer_code: str
   ) -> Optional[int]:
     """Process a referral. Returns referrer's telegram_id or None."""
     try:
       # Find referrer
       result = await (
          self.client.table("users")
          .select("telegram_id")
          .eq("referral_code", referrer_code)
          .limit(1)
          .execute()
       )
       if not result.data:
          return None
       referrer_id = result.data[0]["telegram_id"]
       if referrer_id == new_user_id:
          return None # Can't refer yourself
       # Update new user's referred_by
       await self.update_user(new_user_id, {
          "referred_by": referrer_id,
       })
       # Credit referrer



       await self.credit_wallet(
          referrer_id,
          config.REFERRAL_BONUS,
          TxnType.REFERRAL_BONUS,
          f"Referral bonus for inviting user {new_user_id}",
       )
       return referrer_id
     except Exception as e:
       logger.error("process_referral error: %s", e)
       return None
   # =======================================
   # ADMIN OPERATIONS
   # =======================================
   async def get_dashboard_stats(self) -> Dict[str, Any]:
     """Get admin dashboard statistics."""
     try:
       result = await (
          self.client.table("dashboard_stats")
          .select("*")
          .execute()
       )
       if result.data:
          return result.data[0]
       return {}
     except Exception as e:
       logger.error("get_dashboard_stats error: %s", e)
       return {}
   async def get_platform_config(self) -> Dict[str, Any]:
     """Get admin-configurable settings from DB."""
     try:
       result = await (
          self.client.table("platform_config")
          .select("*")
          .limit(1)
          .execute()
       )
       return result.data[0] if result.data else {}
     except Exception as e:
       logger.error("get_platform_config error: %s", e)
       return {}
   async def update_platform_config(
     self, key: str, value: Any
   ) -> bool:
     """Update a platform config value."""
     try:
       await (
          self.client.table("platform_config")
          .update({key: value})
          .eq("id", 1)
          .execute()
       )
       return True
     except Exception as e:
       logger.error("update_platform_config error: %s", e)
       return False
   async def get_all_active_user_ids(self) -> List[int]:
     """Get all non-banned user IDs for broadcast."""
     try:
       result = await (
          self.client.table("users")
          .select("telegram_id")
          .eq("is_banned", False)
          .eq("has_blocked_bot", False)
          .execute()
       )
       return [u["telegram_id"] for u in (result.data or [])]
     except Exception as e:



       logger.error("get_all_active_user_ids error: %s", e)
       return []
   async def get_bet_tiers(self) -> List[Dict[str, Any]]:
     """Get configured bet tiers from DB or defaults."""
     try:
       result = await (
          self.client.table("bet_tiers")
          .select("*")
          .eq("is_active", True)
          .order("amount", desc=False)
          .execute()
       )
       if result.data:
          return result.data
       return DEFAULT_BET_TIERS
     except Exception as e:
       logger.error("get_bet_tiers error: %s", e)
       return DEFAULT_BET_TIERS
   # =======================================
   # WITHDRAWAL REQUESTS
   # =======================================
   async def create_withdrawal(
     self,
     telegram_id: int,
     amount: int,
     upi_id: str,
   ) -> Optional[Dict[str, Any]]:
     """Create a withdrawal request."""
     try:
       data = {
          "user_id": telegram_id,
          "amount": amount,
          "upi_id": upi_id,
          "status": "pending",
       }
       result = await (
          self.client.table("withdrawals")
          .insert(data)
          .execute()
       )
       return result.data[0] if result.data else None
     except Exception as e:
       logger.error("create_withdrawal error: %s", e)
       return None
   async def get_pending_withdrawals(self) -> List[Dict[str, Any]]:
     """Get all pending withdrawal requests (admin)."""
     try:
       result = await (
          self.client.table("withdrawals")
          .select("*, users(username, first_name)")
          .eq("status", "pending")
          .order("created_at", desc=False)
          .execute()
       )
       return result.data or []
     except Exception as e:
       logger.error("get_pending_withdrawals error: %s", e)
       return []
   async def process_withdrawal(
     self, withdrawal_id: str, status: str, admin_note: str = ""
   ) -> bool:
     """Approve or reject a withdrawal (admin)."""
     try:
       await (
          self.client.table("withdrawals")
          .update({
            "status": status,
            "admin_note": admin_note,



            "processed_at": datetime.now(timezone.utc).isoformat(),
          })
          .eq("id", withdrawal_id)
          .execute()
       )
       return True
     except Exception as e:
       logger.error("process_withdrawal error: %s", e)
       return False
# Singleton
db = Database()
