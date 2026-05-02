import os
import json
import sys
from rich.console import Console
from rich.panel import Panel
from rich.markdown import Markdown
from rich.prompt import Prompt, Confirm
from rich.progress import Progress, BarColumn, TextColumn
from rich.table import Table
from tutor import BATutor
from syllabus import SYLLABUS
from utils import load_state, save_state, validate_env

console = Console()

def display_dashboard(state):
    total_modules = len(SYLLABUS)
    is_infinity = state.get("infinity_mode", False)
    is_quick = state.get("quick_mode", False)
    xp = state.get("xp", 0)
    streak = state.get("streak", 1)
    
    table = Table(title="🚀 BA QUEST + CAT PREP DASHBOARD", show_header=False, border_style="bright_blue")
    
    if is_infinity:
        table.add_row("Mode", "[bold magenta]♾️ INFINITY MODE (Expert MBA Level)[/]")
        table.add_row("XP Level", f"Legendary BA ([bold gold1]XP: {xp}[/])")
        table.add_row("Streak", f"[bold orange3]🔥 {streak} Days[/]")
    else:
        module = SYLLABUS[state['current_module_index']]
        table.add_row("Current Module", f"[bold yellow]{module['title']}[/]")
        table.add_row("CAT Aptitude", f"[bold cyan]{module['cat_skill']}[/]")
        table.add_row("Career Focus", f"[bold magenta]{module.get('career_focus', 'General Management')}[/]")
        table.add_row("Quest Mode", f"[bold green]{'⚡ QUICK MISSION' if is_quick else '🏛️ STANDARD QUEST'}[/]")
        table.add_row("XP", f"[bold gold1]{xp}[/]")
        table.add_row("Streak", f"[bold orange3]🔥 {streak} Days[/]")
        table.add_row("Progress", f"Module {state['current_module_index'] + 1} of {total_modules}")
    
    console.print(table)

    if not is_infinity:
        total_milestones = sum(len(m['milestones']) for m in SYLLABUS)
        completed_milestones_count = len(state.get('completed_milestones', []))
        
        with Progress(
            TextColumn("[progress.description]{task.description}"),
            BarColumn(),
            TextColumn("[progress.percentage]{task.percentage:>3.0f}%"),
        ) as progress:
            task = progress.add_task("[cyan]Overall Quest Mastery", total=total_milestones)
            progress.update(task, completed=completed_milestones_count)

def display_welcome(state):
    # Calculate remaining time
    total_remaining_min = 0
    if not state.get("infinity_mode"):
        remaining_modules = SYLLABUS[state['current_module_index']:]
        for i, m in enumerate(remaining_modules):
            start_m = state['current_milestone_index'] if i == 0 else 0
            total_remaining_min += sum(milestone.get('est_minutes', 15) for milestone in m['milestones'][start_m:])
    
    welcome_text = f"""
# ⚡ NEXT-GEN BA: THE Q-COMMERCE QUEST ⚡
### Master SQL, Python, and AI in the fast lane.

**Why this is different:**
- 🏃 **Bite-sized:** 5-minute milestones. No fluff.
- 🏢 **Real-World:** Every lesson is a real dark-store crisis.
- 🤖 **AI-Driven:** Your tutor is a custom Gemini-powered Master BA.

**Quest Status:**
- 🔥 **Streak:** {state.get('streak', 1)} Days
- ⏳ **Remaining:** ~{total_remaining_min} mins to Mastery

*Type 'help' to see available commands.*
*Type 'quit' at any time to save your progress and exit.*
    """
    console.print(Panel(Markdown(welcome_text), border_style="magenta", expand=False))

def main():
    # 1. Validate Environment
    valid, status_msg = validate_env()
    if not valid:
        console.print(Panel(status_msg, title="❌ Setup Error", border_style="red"))
        sys.exit(1)
    elif status_msg:
        console.print(Panel(status_msg, title="⚠️ Fallback Active", border_style="yellow"))

    state = load_state()
    tutor = BATutor()
    
    display_welcome(state)
    
    while True:
        display_dashboard(state)
        is_infinity = state.get("infinity_mode", False)
        
        if not is_infinity:
            module = SYLLABUS[state["current_module_index"]]
            milestones = module["milestones"]
            
            while state["current_milestone_index"] < len(milestones):
                milestone_data = milestones[state["current_milestone_index"]]
                milestone_title = milestone_data["title"]
                est_time = milestone_data.get("est_minutes", 15)
                
                # Pass state for adaptive difficulty
                lesson = tutor.get_lesson(module["id"], state["current_milestone_index"], milestone_title, state)
                console.print(Panel(Markdown(lesson), title=f"Milestone {state['current_milestone_index']+1}: {milestone_title} (⏳ {est_time}m)", border_style="green"))
                
                milestone_done = False
                while not milestone_done:
                    user_input = Prompt.ask("\n[bold cyan]Input Your Response (or 'help' / 'quick' / 'save' / 'quit')[/]")
                    
                    if user_input.lower() in ['help', '?', '/help']:
                        help_text = """
### 🛠️ QUEST COMMANDS
- **quick**: Toggle Quick Mission Mode (Fast-track with Decision Matrix).
- **save**: Manually save your progress and AI context.
- **quit / exit**: Save and leave the quest.
- **help**: Show this menu.
                        """
                        console.print(Panel(Markdown(help_text), title="Help Menu", border_style="yellow"))
                        continue

                    if user_input.lower() == 'quick':
                        state["quick_mode"] = not state.get("quick_mode", False)
                        save_state(state)
                        console.print(f"[bold magenta]⚡ Quick Mission Mode {'Enabled' if state['quick_mode'] else 'Disabled'}![/]")
                        # Refresh lesson with new mode
                        lesson = tutor.get_lesson(module["id"], state["current_milestone_index"], milestone_title, state)
                        console.print(Panel(Markdown(lesson), title=f"Milestone {state['current_milestone_index']+1} (Updated)", border_style="green"))
                        continue

                    if user_input.lower() == 'save':
                        save_state(state)
                        console.print(Panel("💾 [bold green]CHECKPOINT REACHED![/] Progress and AI Context saved locally.", border_style="green"))
                        continue

                    if user_input.lower() in ['quit', 'exit']:
                        save_state(state)
                        console.print("[yellow]Progress saved. Exiting Quest...[/]")
                        sys.exit()
                    
                    context = f"Module: {module['title']}, Milestone: {milestone_title}"
                    # Pass state for adaptive evaluation
                    response = tutor.send_response(user_input, context, state)
                    console.print(Panel(Markdown(response), border_style="blue"))
                    
                    # Update interaction history for deeper profiling AND persistence
                    state.setdefault("interaction_history", []).append({
                        "milestone": milestone_title,
                        "user_input": user_input,
                        "tutor_response": response
                    })
                    
                    # Auto-save after every interaction for safety
                    save_state(state)

                    if "MILESTONE_COMPLETE" in response:
                        state["current_milestone_index"] += 1
                        state["xp"] = state.get("xp", 0) + 100
                        state.setdefault("completed_milestones", []).append(milestone_title)
                        save_state(state)
                        milestone_done = True
                        console.print("[bold green]✅ Milestone Reached! (+100 XP)[/]")

            # Level up logic
            console.print(Panel(f"🎉 LEVEL UP! Module '{module['title']}' Cleared!", style="bold gold1"))
            state["current_module_index"] += 1
            state["current_milestone_index"] = 0
            
            if state["current_module_index"] >= len(SYLLABUS):
                state["infinity_mode"] = True
                console.print(Panel("🏆 CORE COURSE COMPLETE! Entering ♾️ INFINITY MODE...", style="bold magenta"))
            
            save_state(state)
            if state["infinity_mode"]:
                 if not Confirm.ask("Ready to enter the Chaos of Infinity Mode?"):
                    break
            else:
                if not Confirm.ask("Proceed to the next Mission?"):
                    break
        else:
            # Infinity Mode Loop
            lesson = tutor.get_lesson(0, 0, "", state, is_infinity=True)
            console.print(Panel(Markdown(lesson), title="♾️ CHAOS MISSION", border_style="magenta"))
            
            mission_done = False
            while not mission_done:
                user_input = Prompt.ask("\n[bold cyan]How do you solve this chaos?[/]")
                if user_input.lower() in ['quit', 'exit']:
                    save_state(state)
                    console.print("[yellow]Progress saved. Exiting Infinity...[/]")
                    sys.exit()
                
                response = tutor.send_response(user_input, "INFINITY MODE CHAOS MISSION", state)
                console.print(Panel(Markdown(response), border_style="blue"))
                
                if "MILESTONE_COMPLETE" in response:
                    state.setdefault("completed_milestones", []).append("Chaos Mission")
                    save_state(state)
                    mission_done = True
                    console.print("[bold magenta]🔥 Chaos Managed! Legend status increasing...[/]")
            
            if not Confirm.ask("Ready for the next disaster?"):
                break
    
    console.print("\n[bold gold1]🏆 THE QUEST CONTINUES WHENEVER YOU RETURN! 🏆[/]")

if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        console.print("\n[yellow]Aborted. See you back in the trenches soon![/]")
        sys.exit()
