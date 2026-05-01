# Changelog

## [1.1.0] - 2026-05-02
### Added
- **Resilience**: API error handling for Gemini (Quota, Service Unavailable).
- **Stickiness**: Daily study streak tracker 🔥.
- **Tokens Awareness**: Real-time token usage tracking in the sidebar.
- **Certificate of Mastery**: Downloadable PDF certificate upon reaching Infinity Mode 🏆.
- **UX Polish**: Per-message feedback (👍/👎) for tutor responses.
- **Estimated Time**: Granular "Time to Mastery" counters on welcome screens and sidebars.
- **CLI Dashboard Improvements**: Color-coded XP and streak display.
- **History Rotation**: `full_history.json` now rotates at 500 entries to prevent bloating.

## [1.0.0] - 2026-05-02
### Added
- **AI Tutor**: Integrated `google-generativeai` SDK for adaptive learning.
- **Two Interfaces**: CLI and Streamlit Web versions.
- **Syllabus**: 8 modules covering Business Analysis, Unit Economics, and Python/SQL.
- **Working Sessions**: Adaptive simulation lab for hands-on root cause analysis.
- **XP & Badges**: Gamification system to track progress and achievements.
- **Analytics**: Visual progress tracking and cognitive mentality profiling.
- **Quick Mode**: High-velocity decision-matrix learning mode.
- **State Management**: Robust persistence for quest progress and simulation history.
