import streamlit as st
import json
import os
import time
import io
from tutor import BATutor
from syllabus import SYLLABUS
from utils import load_state, save_state, validate_env
from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import letter

@st.cache_resource
def get_tutor():
    return BATutor()

# 1. Validate Environment
valid, error_msg = validate_env()
if not valid:
    st.error(error_msg)
    st.info("Please create a `.env` file with your `GEMINI_API_KEY`.")
    st.stop()

# Initialize session state
if 'state' not in st.session_state:
    st.session_state.state = load_state()
    if not st.session_state.state.get("session_start_time"):
        st.session_state.state["session_start_time"] = time.time()
        save_state(st.session_state.state)

if 'tutor' not in st.session_state:
    st.session_state.tutor = get_tutor()

if 'quest_messages' not in st.session_state:
    st.session_state.quest_messages = []

if 'ws_messages' not in st.session_state:
    # 2. Persist Working Session History across refresh
    saved_ws = st.session_state.state.get("working_session_history", [])
    st.session_state.ws_messages = []
    for h in saved_ws:
        st.session_state.ws_messages.append({"role": "user", "content": h["user_input"]})
        st.session_state.ws_messages.append({"role": "assistant", "content": h["tutor_response"]})

# --- UI Configuration ---
st.set_page_config(page_title="Next-Gen BA: The Q-Commerce Quest", page_icon="⚡", layout="wide")

# --- Badge Logic ---
BADGES = {
    "first_blood": ("🩸 First Blood", "Complete your first milestone"),
    "speed_demon": ("⚡ Speed Demon", "Complete 3 milestones in Quick Mode"),
    "data_wizard": ("🧪 Data Wizard", "Complete Module 6"),
    "infinity": ("♾️ Infinity Unlocked", "Complete all 8 modules"),
}

def check_badges(state):
    new_badges = []
    completed_count = len(state.get("completed_milestones", []))
    current_badges = state.get("badges", [])
    
    if completed_count >= 1 and BADGES["first_blood"][0] not in current_badges:
        new_badges.append(BADGES["first_blood"][0])
    
    if state.get("current_module_index", 0) >= 6 and BADGES["data_wizard"][0] not in current_badges:
        new_badges.append(BADGES["data_wizard"][0])
        
    if state.get("infinity_mode") and BADGES["infinity"][0] not in current_badges:
        new_badges.append(BADGES["infinity"][0])
        
    if new_badges:
        state["badges"].extend(new_badges)
        for b in new_badges:
            st.toast(f"🏆 Badge Unlocked: {b}!", icon="✨")
        save_state(state)

def generate_certificate(name):
    buffer = io.BytesIO()
    c = canvas.Canvas(buffer, pagesize=letter)
    width, height = letter
    
    # Simple Stylized Certificate
    c.setStrokeColorRGB(0.1, 0.1, 0.3)
    c.setLineWidth(5)
    c.rect(20, 20, width-40, height-40)
    
    c.setFont("Helvetica-Bold", 30)
    c.drawCentredString(width/2, height - 100, "CERTIFICATE OF MASTERY")
    
    c.setFont("Helvetica", 18)
    c.drawCentredString(width/2, height - 160, "This is to certify that")
    
    c.setFont("Helvetica-BoldOblique", 24)
    c.drawCentredString(width/2, height - 210, name.upper())
    
    c.setFont("Helvetica", 18)
    c.drawCentredString(width/2, height - 260, "has successfully completed the")
    
    c.setFont("Helvetica-Bold", 20)
    c.drawCentredString(width/2, height - 300, "NEXT-GEN BA: THE Q-COMMERCE QUEST")
    
    c.setFont("Helvetica", 14)
    c.drawCentredString(width/2, height - 380, f"Awarded on: {time.strftime('%Y-%m-%d')}")
    c.drawCentredString(width/2, height - 410, "Quest Master AI")
    
    c.showPage()
    c.save()
    buffer.seek(0)
    return buffer

# --- Sidebar: Dashboard ---
with st.sidebar:
    st.title("🚀 DASHBOARD")
    state = st.session_state.state
    is_infinity = state.get("infinity_mode", False)
    
    # Streak and Token Awareness
    col1, col2 = st.columns(2)
    col1.metric("🔥 Streak", f"{state.get('streak', 1)} Days")
    col2.metric("🔢 Tokens", f"{state.get('total_tokens', 0):,}")
    
    # XP & Badges
    col3, col4 = st.columns(2)
    col3.metric("⚡ Total XP", state.get("xp", 0))
    col4.metric("🏆 Badges", len(state.get("badges", [])))
    
    # Check for badges
    check_badges(state)
    
    # Trophy Shelf
    if state.get("badges"):
        with st.expander("🎖️ Trophy Shelf", expanded=True):
            for badge in state["badges"]:
                st.write(badge)

    # Quick Mode Toggle
    new_quick_mode = st.toggle("⚡ Quick Mission Mode", value=state.get("quick_mode", False))
    if new_quick_mode != state.get("quick_mode"):
        st.session_state.state["quick_mode"] = new_quick_mode
        save_state(st.session_state.state)
        st.rerun()
    
    if state.get("quick_mode"):
        st.info("⏱️ Target: 5 Minutes per Milestone")

    if is_infinity:
        st.subheader("♾️ INFINITY MODE")
        st.write("**Expert MBA Level**")
        st.metric("Missions Cleared", len(state.get('completed_milestones', [])))
        
        # Download Certificate
        st.write("---")
        name = st.text_input("Enter your name for the certificate:", "Strategist")
        if st.download_button(
            label="🏆 Download Mastery Certificate",
            data=generate_certificate(name),
            file_name="BA_Quest_Mastery.pdf",
            mime="application/pdf"
        ):
            st.toast("Congratulations, Master BA!")
    else:
        module = SYLLABUS[state['current_module_index']]
        st.subheader(f"Module {state['current_module_index'] + 1}")
        st.info(f"**{module['title']}**")
        
        # Est Time Remaining
        remaining_modules = SYLLABUS[state['current_module_index']:]
        total_remaining_min = 0
        for i, m in enumerate(remaining_modules):
            start_m = state['current_milestone_index'] if i == 0 else 0
            total_remaining_min += sum(milestone.get('est_minutes', 15) for milestone in m['milestones'][start_m:])
        st.caption(f"⏳ Est. {total_remaining_min} mins left to Infinity")

        # 3. CAT Prep Sidebar
        st.write("---")
        st.write(f"🎓 **CAT Prep: {module['cat_skill']}**")
        if st.button("🧠 Quick CAT Question"):
            with st.spinner("Generating question..."):
                q = st.session_state.tutor.get_cat_question(module['cat_skill'])
                st.session_state.cat_question = q
        
        if "cat_question" in st.session_state:
            with st.expander("📝 Practice Question", expanded=True):
                st.markdown(st.session_state.cat_question)
                if st.button("Close Question"):
                    del st.session_state.cat_question
                    st.rerun()

        st.write("---")
        total_milestones = sum(len(m['milestones']) for m in SYLLABUS)
        progress_val = (len(state.get('completed_milestones', [])) / total_milestones)
        st.progress(progress_val, text=f"Overall Mastery: {int(progress_val*100)}%")
        
        st.write(f"**Current Milestone:** {state['current_milestone_index'] + 1} of {len(module['milestones'])}")
        milestone_data = module['milestones'][state['current_milestone_index']]
        st.write(f"📍 {milestone_data['title']} (⏳ {milestone_data.get('est_minutes', 15)}m)")

        # 4. Milestone Skip / Revisit
        with st.expander("🗺️ Jump to Milestone"):
            milestone_titles = [m['title'] for m in module['milestones']]
            selected = st.selectbox("Select milestone:", milestone_titles, index=state['current_milestone_index'])
            if st.button("↩️ Revisit/Jump"):
                new_idx = milestone_titles.index(selected)
                st.session_state.state['current_milestone_index'] = new_idx
                save_state(st.session_state.state)
                st.session_state.quest_messages = []
                st.rerun()

    if st.button("💾 Save Progress"):
        save_state(st.session_state.state)
        st.success("Checkpoint Reached! Progress saved.")

    # Mentality Profile detection
    profile_emojis = {"🏗️": "BA Core", "🎨": "PM Thinking", "🧪": "Data", "📈": "Strategy"}
    detected = [f"{k} {v}" for k, v in profile_emojis.items() 
                if any(k in msg["content"] for msg in st.session_state.quest_messages)]
    if detected:
        st.write("---")
        st.write("**🧠 Detected Mentality:**")
        for trait in detected:
            st.write(f"  {trait}")

    # Export Learnings
    if st.button("📥 Export My Quest Notes"):
        history = st.session_state.state.get("interaction_history", [])
        if history:
            md_content = "# BA Quest Study Notes\n\n"
            for h in history:
                md_content += f"## Milestone: {h['milestone']}\n"
                md_content += f"**User:** {h['user_input']}\n\n"
                md_content += f"**Tutor:** {h['tutor_response']}\n\n---\n\n"
            st.download_button("Download Markdown", data=md_content, file_name="ba_quest_notes.md", mime="text/markdown")
        else:
            st.warning("No history to export yet.")

    # Reset Logic
    if st.button("🔄 Reset Course (Warning!)"):
        st.session_state.confirm_reset = True

    if st.session_state.get("confirm_reset"):
        st.warning("Are you sure? This will wipe everything.")
        col1, col2 = st.columns(2)
        with col1:
            if st.button("✅ Yes, Reset"):
                st.session_state.state = {
                    "current_module_index": 0, 
                    "current_milestone_index": 0,
                    "completed_milestones": [],
                    "interaction_history": [],
                    "infinity_mode": False,
                    "working_session_history": [],
                    "quick_mode": False,
                    "xp": 0,
                    "badges": [],
                    "session_start_time": time.time(),
                    "total_tokens": 0,
                    "streak": 1,
                    "last_visit_date": time.strftime('%Y-%m-%d'),
                    "feedback": []
                }
                save_state(st.session_state.state)
                st.session_state.quest_messages = []
                st.session_state.ws_messages = []
                st.session_state.confirm_reset = False
                st.rerun()
        with col2:
            if st.button("❌ Cancel"):
                st.session_state.confirm_reset = False
                st.rerun()

# --- Main UI Tabs ---
tab1, tab2, tab3 = st.tabs(["🎯 Core Quest", "🧪 Simulation Lab", "📊 Analytics"])

with tab1:
    st.title("⚡ THE Q-COMMERCE QUEST ⚡")
    
    # Welcome Panel
    if not st.session_state.quest_messages:
        st.markdown("""
        ### Welcome back, Strategist.
        Your missions are updated based on your latest performance.
        """)
        if st.button("🚀 Resume Mission"):
            state = st.session_state.state
            module = SYLLABUS[state["current_module_index"]]
            milestone_data = module["milestones"][state["current_milestone_index"]]
            
            res = st.session_state.tutor.get_lesson(module["id"], state["current_milestone_index"], milestone_data["title"], state)
            if hasattr(res, 'usage_metadata'):
                state["total_tokens"] += res.usage_metadata.total_token_count
            lesson = res.text if hasattr(res, 'text') else res
            st.session_state.quest_messages.append({"role": "assistant", "content": lesson})
            st.rerun()

    # Display Quest History
    for i, msg in enumerate(st.session_state.quest_messages):
        with st.chat_message(msg["role"]):
            st.markdown(msg["content"])
            if msg["role"] == "assistant":
                col1, col2, _ = st.columns([1, 1, 15])
                with col1:
                    if st.button("👍", key=f"up_{i}"):
                        state.setdefault("feedback", []).append({"msg": msg["content"][:50], "vote": 1})
                        st.toast("Thanks for the feedback!", icon="💖")
                with col2:
                    if st.button("👎", key=f"dn_{i}"):
                        state.setdefault("feedback", []).append({"msg": msg["content"][:50], "vote": -1})
                        st.toast("We'll improve!", icon="🛠️")

    # Chat Input for Quest
    if quest_prompt := st.chat_input("Solve the mission...", key="quest_input"):
        st.session_state.quest_messages.append({"role": "user", "content": quest_prompt})
        with st.chat_message("user"):
            st.markdown(quest_prompt)
        
        state = st.session_state.state
        is_infinity = state.get("infinity_mode", False)
        
        if not is_infinity:
            module = SYLLABUS[state["current_module_index"]]
            milestone_title = module["milestones"][state["current_milestone_index"]]["title"]
            context = f"Module: {module['title']}, Milestone: {milestone_title}"
        else:
            context = "INFINITY MODE CHAOS MISSION"
            milestone_title = "Chaos Mission"
            
        with st.chat_message("assistant"):
            stream = st.session_state.tutor.send_response(quest_prompt, context, state, stream=True)
            # st.write_stream doesn't provide token usage, so we'll collect it manually
            full_response = ""
            message_placeholder = st.empty()
            for chunk in stream:
                full_response += chunk.text
                message_placeholder.markdown(full_response + "▌")
            message_placeholder.markdown(full_response)
            
            # Update tokens from last chunk if available (SDK behavior varies)
            if hasattr(stream, 'usage_metadata'):
                 state["total_tokens"] += stream.usage_metadata.total_token_count
            elif hasattr(chunk, 'usage_metadata'): # Sometimes it's in the last chunk
                 state["total_tokens"] += chunk.usage_metadata.total_token_count
            
            response = full_response
            
        state.setdefault("interaction_history", []).append({
            "milestone": milestone_title,
            "user_input": quest_prompt,
            "tutor_response": response
        })
        
        st.session_state.quest_messages.append({"role": "assistant", "content": response})
            
        if "MILESTONE_COMPLETE" in response:
            state["xp"] = state.get("xp", 0) + 100
            if not is_infinity:
                state["current_milestone_index"] += 1
                state.setdefault("completed_milestones", []).append(milestone_title)
                
                if state["current_milestone_index"] >= len(module["milestones"]):
                    state["current_module_index"] += 1
                    state["current_milestone_index"] = 0
                    if state["current_module_index"] >= len(SYLLABUS):
                        state["infinity_mode"] = True
                        st.balloons()
                    else:
                        st.toast(f"🎉 LEVEL UP!", icon="🔥")
                
                if not state["infinity_mode"]:
                    next_module = SYLLABUS[state["current_module_index"]]
                    next_milestone = next_module["milestones"][state["current_milestone_index"]]["title"]
                    res = st.session_state.tutor.get_lesson(next_module["id"], state["current_milestone_index"], next_milestone, state)
                    if hasattr(res, 'usage_metadata'):
                        state["total_tokens"] += res.usage_metadata.total_token_count
                    next_lesson = res.text if hasattr(res, 'text') else res
                    st.session_state.quest_messages.append({"role": "assistant", "content": next_lesson})
                    st.rerun()
            else:
                st.toast("🔥 Chaos Managed!", icon="👑")
                res = st.session_state.tutor.get_lesson(0, 0, "", state, is_infinity=True)
                if hasattr(res, 'usage_metadata'):
                        state["total_tokens"] += res.usage_metadata.total_token_count
                next_lesson = res.text if hasattr(res, 'text') else res
                st.session_state.quest_messages.append({"role": "assistant", "content": next_lesson})
                st.rerun()

        save_state(state)

with tab2:
    st.title("🧪 SIMULATION LAB")
    st.markdown("""
    *Deep-dive into scenarios, test hypotheses, and analyze simulated data.*
    """)
    
    col1, col2 = st.columns([6, 1])
    if col2.button("🔄 New Scenario"):
        with st.spinner("Generating..."):
            res = st.session_state.tutor.get_working_session(st.session_state.state)
            if hasattr(res, 'usage_metadata'):
                st.session_state.state["total_tokens"] += res.usage_metadata.total_token_count
            session_start = res.text if hasattr(res, 'text') else res
            st.session_state.ws_messages = [{"role": "assistant", "content": session_start}]
            st.session_state.state["working_session_history"] = []
            save_state(st.session_state.state)
            st.rerun()

    if not st.session_state.ws_messages:
        if st.button("🛠️ Start Simulation"):
            with st.spinner("Generating scenario..."):
                res = st.session_state.tutor.get_working_session(st.session_state.state)
                if hasattr(res, 'usage_metadata'):
                    st.session_state.state["total_tokens"] += res.usage_metadata.total_token_count
                session_start = res.text if hasattr(res, 'text') else res
                st.session_state.ws_messages.append({"role": "assistant", "content": session_start})
                st.rerun()

    # Display WS History
    for msg in st.session_state.ws_messages:
        with st.chat_message(msg["role"]):
            st.markdown(msg["content"])

    # Chat Input for Working Session
    if ws_prompt := st.chat_input("Test your hypothesis...", key="ws_input"):
        st.session_state.ws_messages.append({"role": "user", "content": ws_prompt})
        with st.chat_message("user"):
            st.markdown(ws_prompt)
        
        with st.chat_message("assistant"):
            state = st.session_state.state
            stream = st.session_state.tutor.send_response(ws_prompt, "Working Session Simulation", state, mode="working_session", stream=True)
            
            full_response = ""
            message_placeholder = st.empty()
            for chunk in stream:
                full_response += chunk.text
                message_placeholder.markdown(full_response + "▌")
            message_placeholder.markdown(full_response)
            
            if hasattr(stream, 'usage_metadata'):
                 state["total_tokens"] += stream.usage_metadata.total_token_count
            elif hasattr(chunk, 'usage_metadata'):
                 state["total_tokens"] += chunk.usage_metadata.total_token_count
            
            response = full_response
            
            # Store in a separate WS history in state
            state.setdefault("working_session_history", []).append({
                "user_input": ws_prompt,
                "tutor_response": response
            })
            
            st.session_state.ws_messages.append({"role": "assistant", "content": response})
            save_state(state)
            st.rerun()

with tab3:
    st.title("📊 SESSION ANALYTICS")
    state = st.session_state.state
    
    col1, col2, col3 = st.columns(3)
    
    if state.get("session_start_time"):
        elapsed = int((time.time() - state["session_start_time"]) / 60)
        col1.metric("⏱️ Active Minutes", elapsed)
    
    total_m = sum(len(m['milestones']) for m in SYLLABUS)
    comp_m = len(state.get("completed_milestones", []))
    col2.metric("🎯 Milestones Done", comp_m)
    col3.metric("🔥 XP Multiplier", "1.2x" if state.get("quick_mode") else "1.0x")
    
    st.write("---")
    st.subheader("📈 Progress Overview")
    
    module_names = [m["title"] for m in SYLLABUS]
    module_progress = []
    for i, m in enumerate(SYLLABUS):
        if state["current_module_index"] > i:
            module_progress.append(100)
        elif state["current_module_index"] == i:
            module_progress.append(int((state["current_milestone_index"] / len(m["milestones"])) * 100))
        else:
            module_progress.append(0)
            
    st.bar_chart(data=dict(zip(module_names, module_progress)))
    
    st.write("---")
    st.subheader("🧠 Cognitive Fingerprint")
    st.info("Based on your interactions, the Quest Master evaluates your current mental profile.")
    
    if detected:
        st.write("You are currently indexing high on:")
        for trait in detected:
            st.success(f"✅ {trait}")
    else:
        st.write("Continue through more missions to unlock your Mentality Profile.")
