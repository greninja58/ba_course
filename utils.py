import os
import json
from datetime import date, timedelta
from dotenv import load_dotenv

# Load environment variables globally
load_dotenv()

STATE_FILE = "course_state.json"
FULL_HISTORY_FILE = "full_history.json"

DEFAULT_STATE = {
    "current_module_index": 0, 
    "current_milestone_index": 0,
    "completed_milestones": [],
    "interaction_history": [],
    "infinity_mode": False,
    "working_session_history": [],
    "quick_mode": False,
    "xp": 0,
    "badges": [],
    "session_start_time": None,
    "total_tokens": 0,
    "streak": 0,
    "last_visit_date": None,
    "feedback": []
}

def validate_env():
    """Checks if critical environment variables or fallbacks are set."""
    import shutil
    if not os.getenv("GEMINI_API_KEY"):
        # Check for fallbacks
        if shutil.which("gemini") or shutil.which("gemini.cmd") or shutil.which("claude"):
            return True, "⚠️ GEMINI_API_KEY not found. Running in CLI Fallback Mode."
        return False, "❌ GEMINI_API_KEY not found and no AI CLI (Gemini/Claude) detected."
    return True, ""

def load_state():
    state = DEFAULT_STATE.copy()
    if os.path.exists(STATE_FILE):
        try:
            with open(STATE_FILE, "r") as f:
                saved_state = json.load(f)
                state.update(saved_state)
        except (json.JSONDecodeError, IOError):
            pass
    
    # --- Streak Logic ---
    today = str(date.today())
    last_visit = state.get("last_visit_date")
    
    if last_visit:
        if last_visit == str(date.today() - timedelta(days=1)):
            state["streak"] = state.get("streak", 0) + 1
        elif last_visit != today:
            state["streak"] = 1 # Reset if more than 1 day missed
    else:
        state["streak"] = 1
        
    state["last_visit_date"] = today
    return state

def save_state(state):
    # 1. Update full history with rotation
    full_history = state.get("interaction_history", [])
    
    existing_full = []
    if os.path.exists(FULL_HISTORY_FILE):
        try:
            with open(FULL_HISTORY_FILE, "r") as f:
                existing_full = json.load(f)
        except:
            pass

    # Simplified merge and rotation (cap at 500)
    # Note: In a real app we'd append only new ones, but here interaction_history is small
    # Let's just keep the last 500 overall
    combined = (existing_full + full_history)[-500:]
    
    with open(FULL_HISTORY_FILE, "w") as f:
        json.dump(combined, f, indent=2)

    # 2. Trim history for the main state file (AI context window optimization)
    if len(full_history) > 10:
        state["interaction_history"] = full_history[-10:]
    
    ws_history = state.get("working_session_history", [])
    if len(ws_history) > 10:
        state["working_session_history"] = ws_history[-10:]
        
    with open(STATE_FILE, "w") as f:
        json.dump(state, f)
