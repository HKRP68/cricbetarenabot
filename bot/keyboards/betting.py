"""
Betting Keyboards -- Match selection, bet types, amounts, and confirmations.
Designed with conversion psychology: minimize clicks to place a bet.
"""
from typing import Dict, Any, List, Optional
from telegram import InlineKeyboardButton, InlineKeyboardMarkup
from bot.constants import CB, BetType, DEFAULT_BET_TIERS

def build_matches_keyboard(
   matches: List[Dict[str, Any]],
   match_type: str = "live",
   page: int = 0,
   per_page: int = 5,
) -> InlineKeyboardMarkup:
   """Build match list keyboard with pagination."""
   start = page * per_page
   end = start + per_page
   page_matches = matches[start:end]
   total_pages = max(1, (len(matches) + per_page - 1) // per_page)
   keyboard = []
   if not page_matches:
     keyboard.append([
       InlineKeyboardButton(
          "? No matches right now",
          callback_data=f"{CB.NOOP}:empty",
       ),
     ])
   else:
     for m in page_matches:
       team1 = m.get("team1_short", "T1")
       team2 = m.get("team2_short", "T2")
       match_id = m.get("id", m.get("api_match_id", ""))
       status = m.get("status", "upcoming")
       # Status badge
       if status == "live":
          badge = "? LIVE"
       elif status == "upcoming":
          badge = "?"
       else:
          badge = "[OK]"
       # Score snippet
       score = m.get("score_text", "")
       score_display = f"\n? {score[:40]}" if score else ""
       button_text = f"{badge} {team1} vs {team2}{score_display}"
       keyboard.append([
          InlineKeyboardButton(
            button_text,
            callback_data=f"{CB.MATCH}:sel:{match_id[:20]}",
          ),
       ])
   # Pagination
   if total_pages > 1:
     nav = []



     if page > 0:
       nav.append(InlineKeyboardButton(
          "<? Prev",
          callback_data=f"{CB.PAGE}:{match_type}:{page-1}",
       ))
     nav.append(InlineKeyboardButton(
       f"? {page+1}/{total_pages}",
       callback_data=f"{CB.NOOP}:pg",
     ))
     if page < total_pages - 1:
       nav.append(InlineKeyboardButton(
          "Next >?",
          callback_data=f"{CB.PAGE}:{match_type}:{page+1}",
       ))
     keyboard.append(nav)
   # Back
   keyboard.append([
     InlineKeyboardButton(
       "? Main Menu",
       callback_data=f"{CB.MENU}:main",
     ),
   ])
   return InlineKeyboardMarkup(keyboard)
def build_match_detail_keyboard(
   match: Dict[str, Any],
) -> InlineKeyboardMarkup:
   """Show match details with bet options."""
   match_id = match.get("id", "")[:20]
   team1 = match.get("team1_short", "T1")
   team2 = match.get("team2_short", "T2")
   keyboard = [
     # Bet types
     [
       InlineKeyboardButton(
          "? Match Winner",
          callback_data=f"{CB.BET_TYPE}:winner:{match_id}",
       ),
     ],
     [
       InlineKeyboardButton(
          "? Toss Winner",
          callback_data=f"{CB.BET_TYPE}:toss:{match_id}",
       ),
     ],
     # Quick bet buttons (highest conversion -- one-click bets)
     [
       InlineKeyboardButton(
          f"? {team1} wins ?3",
          callback_data=f"{CB.QUICK_BET}:w:{match_id}:1:3",
       ),
       InlineKeyboardButton(
          f"? {team2} wins ?3",
          callback_data=f"{CB.QUICK_BET}:w:{match_id}:2:3",
       ),
     ],
     # View open rooms
     [
       InlineKeyboardButton(
          "? View Open Rooms",
          callback_data=f"{CB.ROOM}:list:{match_id}",
       ),
     ],
     [
       InlineKeyboardButton(
          "? Back to Matches",
          callback_data=f"{CB.MATCH}:live",
       ),
     ],



   ]

   return InlineKeyboardMarkup(keyboard)

def build_team_pick_keyboard(
   match: Dict[str, Any],
   bet_type: str,
) -> InlineKeyboardMarkup:
   """Pick which team/option to bet on."""
   match_id = match.get("id", "")[:20]
   team1 = match.get("team1", "Team 1")
   team2 = match.get("team2", "Team 2")
   keyboard = [
     [
       InlineKeyboardButton(
          f"? {team1}",
          callback_data=f"{CB.BET}:pick:{match_id}:{bet_type}:1",
       ),
     ],
     [
       InlineKeyboardButton(
          f"? {team2}",
          callback_data=f"{CB.BET}:pick:{match_id}:{bet_type}:2",
       ),
     ],
     [
       InlineKeyboardButton(
          "? Back",
          callback_data=f"{CB.MATCH}:sel:{match_id}",
       ),
     ],
   ]
   return InlineKeyboardMarkup(keyboard)
def build_amount_keyboard(
   match_id: str,
   bet_type: str,
   team_pick: str,
   tiers: Optional[List[Dict]] = None,
) -> InlineKeyboardMarkup:
   """Choose bet amount from predefined tiers."""
   if tiers is None:
     tiers = DEFAULT_BET_TIERS
   keyboard = []
   # Show tiers in pairs for compact layout
   for i in range(0, len(tiers), 2):
     row = []
     for tier in tiers[i:i+2]:
       row.append(InlineKeyboardButton(
          tier["label"],
          callback_data=(
            f"{CB.BET}:amt:{match_id[:12]}:"
            f"{bet_type}:{team_pick}:{tier['amount']}"
          ),
       ))
     keyboard.append(row)
   # Custom amount option
   keyboard.append([
     InlineKeyboardButton(
       "[edit]? Custom Amount",
       callback_data=(
          f"{CB.BET}:custom:{match_id[:12]}:"
          f"{bet_type}:{team_pick}"
       ),
     ),
   ])




   keyboard.append([
     InlineKeyboardButton(
       "? Back",
       callback_data=f"{CB.BET_TYPE}:{bet_type}:{match_id[:20]}",
     ),
   ])
   return InlineKeyboardMarkup(keyboard)
def build_confirm_bet_keyboard(
   room_data: Dict[str, Any],
) -> InlineKeyboardMarkup:
   """Confirm bet placement."""
   match_id = str(room_data.get("match_id", ""))[:12]
   amount = room_data.get("bet_amount", 0)
   keyboard = [
     [
       InlineKeyboardButton(
          f"[OK] Confirm Bet ?{amount}",
          callback_data=f"{CB.CONFIRM}:bet:{match_id}:{amount}",
       ),
     ],
     [
       InlineKeyboardButton(
          "[X] Cancel",
          callback_data=f"{CB.CANCEL}:bet",
       ),
     ],
   ]
   return InlineKeyboardMarkup(keyboard)
def build_open_rooms_keyboard(
   rooms: List[Dict[str, Any]],
   match_id: str,
) -> InlineKeyboardMarkup:
   """Show available rooms to join."""
   keyboard = []
   if not rooms:
     keyboard.append([
       InlineKeyboardButton(
          "? Create New Room",
          callback_data=f"{CB.MATCH}:sel:{match_id[:20]}",
       ),
     ])
     keyboard.append([
       InlineKeyboardButton(
          "? No open rooms yet",
          callback_data=f"{CB.NOOP}:norm",
       ),
     ])
   else:
     for room in rooms[:10]:
       room_id = room.get("id", "")[:15]
       amount = room.get("bet_amount", 0)
       win = room.get("win_amount", 0)
       pick = room.get("creator_pick", "")
       bet_type = room.get("bet_type", "winner")
       keyboard.append([
          InlineKeyboardButton(
            f"?? ?{amount} -> Win ?{win} | vs {pick} ({bet_type})",
            callback_data=f"{CB.ROOM}:join:{room_id}",
          ),
       ])
     keyboard.append([
       InlineKeyboardButton(
          "? Create Your Own Room",



          callback_data=f"{CB.MATCH}:sel:{match_id[:20]}",
       ),
     ])
   keyboard.append([
     InlineKeyboardButton(
       "? Back",
       callback_data=f"{CB.MATCH}:sel:{match_id[:20]}",
     ),
   ])
   return InlineKeyboardMarkup(keyboard)

def build_active_bets_keyboard(
   rooms: List[Dict[str, Any]],
) -> InlineKeyboardMarkup:
   """Show user's active bets."""
   keyboard = []
   if not rooms:
     keyboard.append([
       InlineKeyboardButton(
          "? Place a Bet Now!",
          callback_data=f"{CB.MATCH}:live",
       ),
     ])
   else:
     for room in rooms[:10]:
       room_id = room.get("id", "")[:15]
       amount = room.get("bet_amount", 0)
       status = room.get("status", "open")
       status_emoji = "?" if status == "open" else "?"
       keyboard.append([
          InlineKeyboardButton(
            f"{status_emoji} ?{amount} bet -- {status}",
            callback_data=f"{CB.ROOM}:view:{room_id}",
          ),
       ])
   keyboard.append([
     InlineKeyboardButton(
       "? Bet History",
       callback_data=f"{CB.HISTORY}:bets:0",
     ),
   ])
   keyboard.append([
     InlineKeyboardButton(
       "? Main Menu",
       callback_data=f"{CB.MENU}:main",
     ),
   ])
   return InlineKeyboardMarkup(keyboard)
def build_post_result_keyboard(
   show_spin: bool = False,
) -> InlineKeyboardMarkup:
   """Keyboard shown after win/loss -- maximize re-engagement."""
   keyboard = [
     [
       InlineKeyboardButton(
          "? Bet Again Now!",
          callback_data=f"{CB.MATCH}:live",
       ),
     ],
   ]
   if show_spin:
     keyboard.append([
       InlineKeyboardButton(



          "? Free Lucky Spin!",
          callback_data=f"{CB.SPIN}:go",
       ),
     ])
   keyboard.append([
     InlineKeyboardButton(
       "? Leaderboard",
       callback_data=f"{CB.LEADERBOARD}:top",
     ),
     InlineKeyboardButton(
       "? My Stats",
       callback_data=f"{CB.STATS}:me",
     ),
   ])
   keyboard.append([
     InlineKeyboardButton(
       "? Main Menu",
       callback_data=f"{CB.MENU}:main",
     ),
   ])
   return InlineKeyboardMarkup(keyboard)
