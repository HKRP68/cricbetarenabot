"""
Main Menu Keyboards -- Primary navigation for the bot.
Every button is psychologically optimized for engagement.
"""
from telegram import InlineKeyboardButton, InlineKeyboardMarkup
from bot.constants import CB

def build_main_menu(
   live_count: int = 0,
   has_active_bets: bool = False,
   is_premium: bool = False,
) -> InlineKeyboardMarkup:
   """Build the main menu with dynamic data."""
   live_badge = f" ? {live_count}" if live_count > 0 else ""
   keyboard = [
     # Row 1: Primary actions (highest conversion)
     [
       InlineKeyboardButton(
          f"? Live Matches{live_badge}",
          callback_data=f"{CB.MATCH}:live",
       ),
       InlineKeyboardButton(
          "? Upcoming",
          callback_data=f"{CB.MATCH}:upcoming",
       ),
     ],
     # Row 2: Quick bet (reduces friction -> more bets)
     [
       InlineKeyboardButton(
          "? Quick Bet ?3",
          callback_data=f"{CB.QUICK_BET}:3",
       ),
       InlineKeyboardButton(
          "? Quick Bet ?10",
          callback_data=f"{CB.QUICK_BET}:10",
       ),
     ],
     # Row 3: Engagement hooks
     [
       InlineKeyboardButton(
          "? Lucky Spin",
          callback_data=f"{CB.SPIN}:go",
       ),
       InlineKeyboardButton(
          "? Leaderboard",
          callback_data=f"{CB.LEADERBOARD}:top",
       ),
     ],
     # Row 4: Wallet & History
     [
       InlineKeyboardButton(
          "? Wallet",
          callback_data=f"{CB.WALLET}:main",
       ),
       InlineKeyboardButton(
          "? My Stats",
          callback_data=f"{CB.STATS}:me",
       ),
     ],
   ]




   # Active bets badge
   if has_active_bets:
     keyboard.insert(1, [
       InlineKeyboardButton(
          "? My Active Bets ?",
          callback_data=f"{CB.BET}:active",
       ),
     ])
   # Row 5: Referral & Settings
   keyboard.append([
     InlineKeyboardButton(
       "? Invite & Earn ?5",
       callback_data=f"{CB.REFER}:show",
     ),
     InlineKeyboardButton(
       "?? Settings",
       callback_data=f"{CB.SETTINGS}:main",
     ),
   ])
   # Row 6: Support & Help
   keyboard.append([
     InlineKeyboardButton(
       "? How to Play",
       callback_data=f"{CB.MENU}:help",
     ),
     InlineKeyboardButton(
       "? Support",
       callback_data=f"{CB.SUPPORT}:main",
     ),
   ])
   return InlineKeyboardMarkup(keyboard)
def build_settings_menu(
   notifications_on: bool = True,
   language: str = "en",
) -> InlineKeyboardMarkup:
   """Settings menu keyboard."""
   notif_text = "? Notifications: ON" if notifications_on else "? Notifications: OFF"
   keyboard = [
     [
       InlineKeyboardButton(
          notif_text,
          callback_data=f"{CB.SETTINGS}:notif",
       ),
     ],
     [
       InlineKeyboardButton(
          f"? Language: {language.upper()}",
          callback_data=f"{CB.SETTINGS}:lang",
       ),
     ],
     [
       InlineKeyboardButton(
          "? Terms & Conditions",
          callback_data=f"{CB.SETTINGS}:terms",
       ),
     ],
     [
       InlineKeyboardButton(
          "? Back to Menu",
          callback_data=f"{CB.MENU}:main",
       ),
     ],
   ]
   return InlineKeyboardMarkup(keyboard)
def build_help_menu() -> InlineKeyboardMarkup:



   """How-to-play help keyboard."""
   keyboard = [
     [
       InlineKeyboardButton(
          "? How Betting Works",
          callback_data=f"{CB.MENU}:help_bet",
       ),
     ],
     [
       InlineKeyboardButton(
          "? Deposits & Withdrawals",
          callback_data=f"{CB.MENU}:help_wallet",
       ),
     ],
     [
       InlineKeyboardButton(
          "? Leaderboard Rules",
          callback_data=f"{CB.MENU}:help_lb",
       ),
     ],
     [
       InlineKeyboardButton(
          "? Lucky Spin Rules",
          callback_data=f"{CB.MENU}:help_spin",
       ),
     ],
     [
       InlineKeyboardButton(
          "? Back to Menu",
          callback_data=f"{CB.MENU}:main",
       ),
     ],
   ]
   return InlineKeyboardMarkup(keyboard)
def build_wallet_menu(balance: int = 0) -> InlineKeyboardMarkup:
   """Wallet management keyboard."""
   keyboard = [
     [
       InlineKeyboardButton(
          f"? Balance: ?{balance:,}",
          callback_data=f"{CB.NOOP}:bal",
       ),
     ],
     [
       InlineKeyboardButton(
          "? Add Money",
          callback_data=f"{CB.DEPOSIT}:main",
       ),
       InlineKeyboardButton(
          "? Withdraw",
          callback_data=f"{CB.WITHDRAW}:start",
       ),
     ],
     [
       InlineKeyboardButton(
          "? Transaction History",
          callback_data=f"{CB.HISTORY}:txn:0",
       ),
     ],
     [
       InlineKeyboardButton(
          "? Earn via Referrals",
          callback_data=f"{CB.REFER}:show",
       ),
     ],
     [
       InlineKeyboardButton(
          "? Back to Menu",
          callback_data=f"{CB.MENU}:main",
       ),
     ],



   ]
   return InlineKeyboardMarkup(keyboard)
