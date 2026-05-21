"""
Constants -- ALL magic strings, callback prefixes, states, and enums.
Single source of truth. No typos possible.
"""
from enum import Enum, IntEnum
# =======================================
# CALLBACK DATA PREFIXES (max 64 bytes)
# =======================================
class CB(str, Enum):
   """Callback data prefixes. Short to save bytes."""
   MENU = "m"
   BET = "b"
   MATCH = "mt"
   ROOM = "r"
   WALLET = "w"
   SETTINGS = "s"
   ADMIN = "a"
   CONFIRM = "ok"
   CANCEL = "no"
   PAGE = "pg"
   NOOP = "x"
   PREMIUM = "pr"
   HISTORY = "h"
   LEADERBOARD = "lb"
   SPIN = "sp"
   REFER = "rf"
   STATS = "st"
   NOTIFY = "nt"
   WITHDRAW = "wd"
   DEPOSIT = "dp"
   SUPPORT = "su"
   BET_TYPE = "bt"
   QUICK_BET = "qb"
# =======================================
# CONVERSATION STATES
# =======================================
class ConvState(IntEnum):
   """ConversationHandler states."""
   # Onboarding
   ONBOARD_NAME = 0
   ONBOARD_PHONE = 1
   # Betting flow
   BET_SELECT_MATCH = 10
   BET_SELECT_TYPE = 11
   BET_SELECT_TEAM = 12
   BET_ENTER_AMOUNT = 13
   BET_CONFIRM = 14
   # Withdrawal flow
   WITHDRAW_AMOUNT = 20
   WITHDRAW_UPI = 21
   WITHDRAW_CONFIRM = 22
   # Admin broadcast
   ADMIN_BROADCAST_MSG = 30
   ADMIN_BROADCAST_CONFIRM = 31
   # Admin settings



   ADMIN_EDIT_VALUE = 40

   # Support
   SUPPORT_MSG = 50

# =======================================
# BET TYPES
# =======================================
class BetType(str, Enum):
   """Types of bets available."""
   MATCH_WINNER = "winner" # Who wins the match
   TOSS_WINNER = "toss" # Who wins the toss
   TOP_SCORER = "top_scorer" # Top scorer prediction
   TOTAL_RUNS = "total_runs" # Over/under total runs
   FIRST_WICKET = "first_wicket" # First wicket over
   SIXES_COUNT = "sixes" # Total sixes over/under
# =======================================
# ROOM STATUSES
# =======================================
class RoomStatus(str, Enum):
   """Betting room lifecycle."""
   OPEN = "open"     # Accepting entries
   LOCKED = "locked" # Bets locked, match in progress
   SETTLED = "settled" # Winner decided, payouts done
   CANCELLED = "cancelled" # Match cancelled, refunds issued
   EXPIRED = "expired" # Room expired, no opponent joined
# =======================================
# MATCH STATUSES
# =======================================
class MatchStatus(str, Enum):
   """Cricket match statuses."""
   UPCOMING = "upcoming"
   LIVE = "live"
   COMPLETED = "completed"
   ABANDONED = "abandoned"
# =======================================
# TRANSACTION TYPES
# =======================================
class TxnType(str, Enum):
   """Wallet transaction types."""
   DEPOSIT = "deposit"
   WITHDRAWAL = "withdrawal"
   BET_PLACED = "bet_placed"
   BET_WON = "bet_won"
   BET_REFUND = "bet_refund"
   SIGNUP_BONUS = "signup_bonus"
   REFERRAL_BONUS = "referral_bonus"
   DAILY_BONUS = "daily_bonus"
   STREAK_BONUS = "streak_bonus"
   SPIN_WIN = "spin_win"
   COMMISSION = "commission"
   ADMIN_CREDIT = "admin_credit"
   ADMIN_DEBIT = "admin_debit"
# =======================================
# BET TIERS -- Admin-configurable defaults
# =======================================
DEFAULT_BET_TIERS = [
   {"amount": 3, "winner_gets": 5, "label": "? ?3 Entry -> Win ?5"},
   {"amount": 5, "winner_gets": 9, "label": "? ?5 Entry -> Win ?9"},
   {"amount": 10, "winner_gets": 18, "label": "? ?10 Entry -> Win ?18"},
   {"amount": 25, "winner_gets": 45, "label": "? ?25 Entry -> Win ?45"},
   {"amount": 50, "winner_gets": 90, "label": "? ?50 Entry -> Win ?90"},
   {"amount": 100, "winner_gets": 180, "label": "? ?100 Entry -> Win ?180"},
   {"amount": 500, "winner_gets": 900, "label": "? ?500 Entry -> Win ?900"},



   {"amount": 1000, "winner_gets": 1800, "label": "? ?1000 Entry -> Win ?1800"},
]
# =======================================
# LUCKY SPIN PRIZES
# =======================================
SPIN_PRIZES = [
   {"label": "?1", "amount": 1, "weight": 30, "emoji": "?"},
   {"label": "?2", "amount": 2, "weight": 25, "emoji": "?"},
   {"label": "?5", "amount": 5, "weight": 20, "emoji": "?"},
   {"label": "?10", "amount": 10, "weight": 12, "emoji": "?"},
   {"label": "?25", "amount": 25, "weight": 7, "emoji": "?"},
   {"label": "?50", "amount": 50, "weight": 4, "emoji": "?"},
   {"label": "?100", "amount": 100, "weight": 1.5, "emoji": "*"},
   {"label": "?500", "amount": 500, "weight": 0.5, "emoji": "?"},
]
# =======================================
# MESSAGES -- All user-facing text
# =======================================
MSG = {
   "welcome_new": (
     "? <b>Welcome to CricBet Arena, {name}!</b>\n\n"
     "You've just joined <b>{user_count:,}+ players</b> who are "
     "winning real money on cricket matches! ?\n\n"
     "? <b>Welcome Gift:</b> ?{bonus} added to your wallet!\n"
     "? <b>Daily Spin:</b> Win up to ?500 every day!\n"
     "? <b>Leaderboard:</b> Top players win weekly prizes!\n\n"
     "? <b>How it works:</b>\n"
     "1?? Pick a live/upcoming match\n"
     "2?? Choose your bet & entry amount\n"
     "3?? Get matched with an opponent\n"
     "4?? Winner takes the prize! ?\n\n"
     "? <i>Pro tip: Your first bet is on us -- "
     "use your ?{bonus} bonus now!</i>"
   ),
   "welcome_back": (
     "? <b>Welcome back, {name}!</b> ?\n\n"
     "? Wallet: <b>?{balance}</b>\n"
     "? Win Rate: <b>{win_rate}%</b>\n"
     "? Streak: <b>{streak} days</b>\n\n"
     "? <b>{live_count}</b> matches live now!\n"
     "? <b>{upcoming_count}</b> matches coming up!\n\n"
     "Ready to play? ?"
   ),
   "insufficient_balance": (
     "? <b>Not enough balance!</b>\n\n"
     "? Your balance: <b>?{balance}</b>\n"
     "? Required: <b>?{required}</b>\n\n"
     "Top up your wallet to keep winning! ?\n\n"
     "? <i>Or invite friends to earn ?{ref_bonus} per referral!</i>"
   ),
   "bet_placed": (
     "[OK] <b>Bet Placed Successfully!</b>\n\n"
     "? Match: <b>{match_name}</b>\n"
     "? Your Pick: <b>{pick}</b>\n"
     "? Entry: <b>?{amount}</b>\n"
     "? Win: <b>?{win_amount}</b>\n\n"
     "? Waiting for opponent to join...\n\n"
     "? <i>We'll notify you the moment someone accepts!</i>"
   ),
   "opponent_joined": (
     "?? <b>GAME ON!</b>\n\n"
     "Your opponent <b>{opponent}</b> has joined!\n\n"
     "? Match: <b>{match_name}</b>\n"
     "? You picked: <b>{your_pick}</b>\n"
     "? They picked: <b>{their_pick}</b>\n"
     "? Prize pool: <b>?{pool}</b>\n"
     "? Winner gets: <b>?{prize}</b>\n\n"
     "? <i>Sit back and watch! We'll settle automatically!</i>"
   ),
   "you_won": (
     "??? <b>YOU WON!</b> ???\n\n"



     "? Match: <b>{match_name}</b>\n"
     "[OK] Result: <b>{result}</b>\n"
     "? You won: <b>?{prize}</b>\n\n"
     "? New Balance: <b>?{balance}</b>\n"
     "? Win Streak: <b>{streak}</b>\n\n"
     "? <i>Winners play again! Bet now while you're hot! ?</i>"
   ),
   "you_lost": (
     "? <b>Better luck next time!</b>\n\n"
     "? Match: <b>{match_name}</b>\n"
     "[X] Result: <b>{result}</b>\n"
     "? Lost: <b>?{amount}</b>\n\n"
     "? Balance: <b>?{balance}</b>\n\n"
     "? <i>Top players lose sometimes too -- "
     "the comeback is always stronger! ?</i>\n\n"
     "? <i>Spin the wheel for a free boost!</i>"
   ),
   "banned": "? Your account has been suspended. Contact support.",
   "rate_limited": "?? Slow down! Wait {seconds}s before next action.",
   "maintenance": "? We're upgrading! Back in 5 minutes. Don't miss out!",
}
# =======================================
# ADMIN CONFIGURABLE KEYS
# =======================================
ADMIN_CONFIGURABLE = {
   "min_bet_amount": {
     "label": "Minimum Bet Amount (?)",
     "type": "int",
     "min": 1,
     "max": 100,
   },
   "platform_commission_pct": {
     "label": "Platform Commission (%)",
     "type": "float",
     "min": 1.0,
     "max": 50.0,
   },
   "max_bet_amount": {
     "label": "Maximum Bet Amount (?)",
     "type": "int",
     "min": 100,
     "max": 100000,
   },
   "free_credits_on_signup": {
     "label": "Signup Bonus (?)",
     "type": "int",
     "min": 0,
     "max": 1000,
   },
   "referral_bonus": {
     "label": "Referral Bonus (?)",
     "type": "int",
     "min": 0,
     "max": 500,
   },
   "daily_free_bet_amount": {
     "label": "Daily Free Bet (?)",
     "type": "int",
     "min": 0,
     "max": 100,
   },
   "min_withdrawal": {
     "label": "Min Withdrawal (?)",
     "type": "int",
     "min": 10,
     "max": 1000,
   },
   "bet_lock_before_match_mins": {
     "label": "Lock Bets Before Match (mins)",
     "type": "int",
     "min": 1,



     "max": 60,
   },
}
