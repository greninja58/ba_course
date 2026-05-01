import os
import google.generativeai as genai
import google.api_core.exceptions

SYSTEM_PROMPT = """
You are the 'Quest Master BA', a top-tier Management Consultant and Dynamic Profile Orchestrator.
Your mission: Adapt the course architecture in real-time based on the user's 'Mentality Profile' (PM, BA Core, Data, Strategy).

CRITICAL OPERATIONAL MODES:

1. EVALUATION MODE (Syllabus):
   - Evaluate if the user mastered the milestone.
   - Signal completion ONLY with 'MILESTONE_COMPLETE'.

2. LESSON MODE (Syllabus):
   - Deliver the next core mission from the syllabus.
   - Structure: ⚡ MISSION, 🏛️ BA FOUNDATION, 🇮🇳 ECOSYSTEM, 🎯 CHALLENGE.

3. WORKING SESSION MODE (Simulation & RCA):
   - Goal: Deep-dive into a specific scenario to build hypotheses and perform RCA.
   - Use simulated numbers and hypothetical data sets.
   - Tracking: Identify if the user is 'Stuck in the Maze' (linear thinking) or 'Out of the Box' (lateral thinking).
   - Interaction Style: Probing, Socratic, and Data-Driven.

4. QUICK MISSION MODE (High Velocity):
   - Goal: Rapidly progress through milestones with structured decision-making.
   - Presentation: Use a 'Decision Matrix' (Variables x Values).
   - Input: User selects a Code (e.g., A1, B2) + Optional Comment.
   - Logic: Evaluate the trade-offs defined by the combination and the user's comment.
   - Result: Can trigger 'MILESTONE_COMPLETE' or deeper probing.

5. CAT PREP MODE:
   - Goal: Generate a high-quality MBA entrance style aptitude question (QA, DILR, or VARC) related to the current module's theme.
   - Provide 4 options and evaluate the user's logic after they answer.

MENTALITY PROFILING:
- Use 'Interaction History' to build a SWOT.
- Use Emojis: 🏗️ (BA Core), 🎨 (PM Thinking), 🧪 (Data), 📈 (Strategy).
"""

class BATutor:
    def __init__(self):
        api_key = os.getenv("GEMINI_API_KEY")
        genai.configure(api_key=api_key)
        self.model = genai.GenerativeModel(
            model_name="gemini-1.5-flash",
            system_instruction=SYSTEM_PROMPT
        )

    def _call_gemini(self, prompt, stream=False):
        try:
            response = self.model.generate_content(prompt, stream=stream)
            if stream:
                return response
            if not response.text:
                return "❌ AI Error: Empty response from model."
            return response
        except google.api_core.exceptions.ResourceExhausted:
            return "⚠️ API quota reached. Your progress is saved locally. Please try again in a few minutes."
        except google.api_core.exceptions.ServiceUnavailable:
            return "⚠️ Gemini service is temporarily unavailable. Working offline — your input is saved."
        except Exception as e:
            return f"❌ AI Error: {str(e)}"

    def get_cat_question(self, skill_theme):
        prompt = f"Generate a CAT-style aptitude question (QA/DILR/VARC) specifically focusing on '{skill_theme}'. Include 4 options (A, B, C, D) and make it challenging but solvable in 2 minutes."
        res = self._call_gemini(prompt)
        return res.text if hasattr(res, 'text') else res

    def get_lesson(self, module_id, milestone_index, milestone_title, state_context, is_infinity=False):
        history = state_context.get("interaction_history", [])
        quick_mode = state_context.get("quick_mode", False)
        context_str = f"History: {history}. Current Milestone: {milestone_title}. Quick Mode: {quick_mode}"
        
        if is_infinity:
            prompt = f"{context_str}\n\nINFINITY MODE. Generate a Chaos Mission blending modes based on the user's Profile."
        else:
            mode_instruction = "Deliver in QUICK MISSION MODE using a Decision Matrix." if quick_mode else "Deliver an ADAPTIVE lesson and challenge."
            prompt = f"{context_str}\n\nModule {module_id}, Milestone {milestone_index+1}. {mode_instruction}"
        
        res = self._call_gemini(prompt)
        return res.text if hasattr(res, 'text') else res

    def get_working_session(self, state_context):
        history = state_context.get("interaction_history", [])
        completed = state_context.get("completed_milestones", [])
        quick_mode = state_context.get("quick_mode", False)
        
        mode_instruction = "Use QUICK MISSION MODE for the hypothesis phase." if quick_mode else "Ask them to form a hypothesis manually."
        
        prompt = f"""
        History: {history}. 
        Completed Milestones: {completed}.
        
        START A WORKING SESSION. 
        1. Pick a scenario based on their progress (e.g., if they just did CAC, pick a 'Referral Fraud' or 'Marketing Attribution' crisis).
        2. {mode_instruction}
        3. Provide 3-4 simulated data points/numbers.
        4. Challenge them to find the Root Cause.
        """
        res = self._call_gemini(prompt)
        return res.text if hasattr(res, 'text') else res

    def send_response(self, user_input, context, state_context, mode="syllabus", stream=False):
        history = state_context.get("interaction_history", [])
        quick_mode = state_context.get("quick_mode", False)
        context_str = f"History: {history}. Current Context: {context}. Mode: {mode}. Quick Mode: {quick_mode}."
        
        if mode == "working_session":
            prompt = f"{context_str}\n\nUser Input in Working Session: {user_input}\n\nGuide them through the simulation. Provide more data if needed. Analyze their cognitive patterns (Stuck vs Out-of-box)."
        else:
            prompt = f"{context_str}\n\nUser Response: {user_input}\n\nEvaluate and perform 'Mentality Profiling' for the next step. If in Quick Mode, analyze the choice code and the optional comment."
            
        return self._call_gemini(prompt, stream=stream)
