# Next-Gen BA: The Q-Commerce Quest

An interactive learning platform to master Business Analysis, SQL, Python, and AI through real-world Q-commerce scenarios.

## Features
- **CLI Mode**: Interactive terminal-based learning with a rich dashboard.
- **Web Mode**: Streamlit-based dashboard with a "Simulation Lab" for deep-dives.
- **AI Tutor**: Powered by the Gemini 1.5 Flash SDK for adaptive lessons and profiling.
- **Mentality Profiling**: Tracks your thinking patterns (Strategy, Data, BA Core, PM).
- **XP System**: Earn 100 XP per milestone to reach "Legendary BA" status.
- **Export Notes**: Download your quest history as a Markdown study guide.

## Prerequisites
1. **Python 3.8+**
2. **Gemini API Key**: You need a Google Gemini API key.
   - Get one at: [https://aistudio.google.com/](https://aistudio.google.com/)

## Installation
1. Unzip the package.
2. Navigate to the directory:
   ```bash
   cd ba_course_cli
   ```
3. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```
4. Setup Environment:
   - Copy `.env.example` to `.env`.
   - Add your API key: `GEMINI_API_KEY=your_actual_key_here`

## Usage

### CLI Mode
To start the terminal-based quest:
```bash
python main.py
```

### Web Mode (Streamlit)
To start the web dashboard:
```bash
streamlit run streamlit_app.py
```

## Project Structure
- `main.py`: Entry point for the CLI application.
- `streamlit_app.py`: Entry point for the Streamlit web application.
- `tutor.py`: Logic for AI interaction via Gemini SDK.
- `syllabus.py`: The course content and milestones.
- `utils.py`: Centralized state and history management.
- `requirements.txt`: Python dependencies.
