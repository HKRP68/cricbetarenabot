"""
Admin Keyboards -- Admin panel navigation.
"""
from typing import Dict, Any, List
from telegram import InlineKeyboardButton, InlineKeyboardMarkup
from bot.constants import CB, ADMIN_CONFIGURABLE


def build_admin_menu() -> InlineKeyboardMarkup:
   """Admin main panel."""
   keyboard = [
     [
       InlineKeyboardButton(
          "? Dashboard",
          callback_data=f"{CB.ADMIN}:dash",
       ),
     ],
     [
       InlineKeyboardButton(
          "? User Management",
          callback_data=f"{CB.ADMIN}:users",
       ),
       InlineKeyboardButton(
          "? Withdrawals",
          callback_data=f"{CB.ADMIN}:wd",
       ),
     ],
     [
       InlineKeyboardButton(
          "?? Bot Settings",
          callback_data=f"{CB.ADMIN}:config",
       ),
       InlineKeyboardButton(
          "? Broadcast",
          callback_data=f"{CB.ADMIN}:bcast",
       ),
     ],
     [
       InlineKeyboardButton(
          "? Match Management",
          callback_data=f"{CB.ADMIN}:matches",
       ),
       InlineKeyboardButton(
          "? Bet Tiers",
          callback_data=f"{CB.ADMIN}:tiers",
       ),
     ],
     [
       InlineKeyboardButton(
          "? Revenue Report",
          callback_data=f"{CB.ADMIN}:revenue",
       ),
       InlineKeyboardButton(
          "? Force Sync",
          callback_data=f"{CB.ADMIN}:sync",
       ),
     ],
     [
       InlineKeyboardButton(
          "? Main Menu",
          callback_data=f"{CB.MENU}:main",



       ),
     ],
   ]
   return InlineKeyboardMarkup(keyboard)

def build_config_keyboard(
   current_config: Dict[str, Any],
) -> InlineKeyboardMarkup:
   """Show all configurable settings."""
   keyboard = []
   for key, meta in ADMIN_CONFIGURABLE.items():
     current_value = current_config.get(key, "N/A")
     keyboard.append([
       InlineKeyboardButton(
          f"{meta['label']}: {current_value}",
          callback_data=f"{CB.ADMIN}:edit:{key}",
       ),
     ])
   keyboard.append([
     InlineKeyboardButton(
       "? Admin Panel",
       callback_data=f"{CB.ADMIN}:main",
     ),
   ])
   return InlineKeyboardMarkup(keyboard)
def build_user_management_keyboard() -> InlineKeyboardMarkup:
   """User management options."""
   keyboard = [
     [
       InlineKeyboardButton(
          "? Search User",
          callback_data=f"{CB.ADMIN}:usearch",
       ),
     ],
     [
       InlineKeyboardButton(
          "? Ban User",
          callback_data=f"{CB.ADMIN}:ban",
       ),
       InlineKeyboardButton(
          "[OK] Unban User",
          callback_data=f"{CB.ADMIN}:unban",
       ),
     ],
     [
       InlineKeyboardButton(
          "? Credit User",
          callback_data=f"{CB.ADMIN}:credit",
       ),
       InlineKeyboardButton(
          "? Debit User",
          callback_data=f"{CB.ADMIN}:debit",
       ),
     ],
     [
       InlineKeyboardButton(
          "? Recent Signups",
          callback_data=f"{CB.ADMIN}:recent",
       ),
     ],
     [
       InlineKeyboardButton(
          "? Admin Panel",
          callback_data=f"{CB.ADMIN}:main",
       ),
     ],
   ]
   return InlineKeyboardMarkup(keyboard)





def build_withdrawal_list_keyboard(
   withdrawals: List[Dict[str, Any]],
) -> InlineKeyboardMarkup:
   """Show pending withdrawal requests."""
   keyboard = []
   if not withdrawals:
     keyboard.append([
       InlineKeyboardButton(
          "[OK] No pending withdrawals",
          callback_data=f"{CB.NOOP}:nowd",
       ),
     ])
   else:
     for wd in withdrawals[:10]:
       wd_id = str(wd.get("id", ""))[:15]
       amount = wd.get("amount", 0)
       user_info = wd.get("users", {})
       name = user_info.get("first_name", "Unknown") if user_info else "Unknown"
       keyboard.append([
          InlineKeyboardButton(
            f"? {name} -- ?{amount}",
            callback_data=f"{CB.ADMIN}:wdview:{wd_id}",
          ),
       ])
   keyboard.append([
     InlineKeyboardButton(
       "? Admin Panel",
       callback_data=f"{CB.ADMIN}:main",
     ),
   ])
   return InlineKeyboardMarkup(keyboard)
def build_withdrawal_action_keyboard(
   withdrawal_id: str,
) -> InlineKeyboardMarkup:
   """Approve or reject a withdrawal."""
   wd_id = withdrawal_id[:15]
   keyboard = [
     [
       InlineKeyboardButton(
          "[OK] Approve",
          callback_data=f"{CB.ADMIN}:wdok:{wd_id}",
       ),
       InlineKeyboardButton(
          "[X] Reject",
          callback_data=f"{CB.ADMIN}:wdno:{wd_id}",
       ),
     ],
     [
       InlineKeyboardButton(
          "? Back",
          callback_data=f"{CB.ADMIN}:wd",
       ),
     ],
   ]
   return InlineKeyboardMarkup(keyboard)
