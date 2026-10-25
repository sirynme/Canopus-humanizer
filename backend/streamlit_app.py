"""Turnitout Streamlit Multi-Page Web Application.

Adheres strictly to AGENTS.md:
- Python 3.14 file watcher safety.
- Lazy component loading.
- Complete 4-module suite: Humanizer, Citations, ZipPy Checker, Feedback.
"""

import sys
from pathlib import Path
import streamlit as st

# Ensure backend root is in sys.path
backend_root = Path(__file__).resolve().parent
src_dir = backend_root / "src"
if str(src_dir) not in sys.path:
    sys.path.insert(0, str(src_dir))

# Mandatory Streamlit config call at top level
st.set_page_config(
    page_title="Turnitout — Plagiarism & AI Footprint Removal Engine",
    page_icon="⚡",
    layout="wide",
    initial_sidebar_state="expanded"
)

from turnitout.ui.common import apply_custom_styles, render_footer

# Apply CSS styling
apply_custom_styles()

# Sidebar Navigation
st.sidebar.image(
    "https://raw.githubusercontent.com/AhmadHassan-BTed/Turnitout-Humanizer/main/docs/assets/logo.svg",
    width=180
)
st.sidebar.title("Turnitout Engine")
st.sidebar.caption("Deterministic Evasion & Citation Suite")

page_selection = st.sidebar.radio(
    "Navigation Menu",
    options=[
        "⚡ Plagiarism & AI Remover",
        "📜 Citation & Reference Generator",
        "🔍 AI Pattern & Signature Checker",
        "💬 Feature Request & Bug Reporter"
    ],
    index=0
)

st.sidebar.markdown("---")
st.sidebar.info(
    "💡 **Production Mode:** 100% In-Memory Execution. Uploaded files and text are never written to database or disk."
)

# Dynamic Page Router (Lazy imports)
if page_selection == "⚡ Plagiarism & AI Remover":
    from turnitout.ui.humanizer_ui import render_humanizer_page
    render_humanizer_page()
elif page_selection == "📜 Citation & Reference Generator":
    from turnitout.ui.citation_ui import render_citation_page
    render_citation_page()
elif page_selection == "🔍 AI Pattern & Signature Checker":
    from turnitout.ui.checker_ui import render_checker_page
    render_checker_page()
elif page_selection == "💬 Feature Request & Bug Reporter":
    from turnitout.ui.feedback_ui import render_feedback_page
    render_feedback_page()

# Persistent Global Footer
render_footer()
