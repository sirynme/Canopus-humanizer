"""Streamlit In-App Feature Request & Bug Reporter Hub."""

import streamlit as st


def render_feedback_page():
    """Renders 💬 Feature Request & Bug Reporter Hub page."""
    st.markdown('<div class="main-header">💬 Feature Request & Bug Reporter Hub</div>', unsafe_allow_html=True)
    st.markdown(
        '<div class="sub-header">Direct Developer Feedback — Report Bugs, Request Discipline Taxonomies, or Suggest Features</div>',
        unsafe_allow_html=True,
    )

    with st.form("feedback_form", clear_on_submit=True):
        fb_type = st.selectbox("Feedback Category", options=["Bug Report", "New Academic Taxonomy Request", "Feature Request", "Other"], index=0)
        user_email = st.text_input("Your Email or GitHub Username (optional)")
        subject = st.text_input("Summary / Subject", placeholder="e.g., Support for Chemistry reaction equations")
        details = st.text_area("Detailed Description & Steps to Reproduce", height=150)
        
        submitted = st.form_submit_button("📨 Submit Feedback", use_container_width=True)
        if submitted:
            if not subject.strip() or not details.strip():
                st.warning("Please fill in both the summary and detailed description.")
            else:
                st.success("🎉 Thank you! Your feedback has been recorded locally. You can also open an issue directly on GitHub.")
                st.info(
                    f"**GitHub Direct Pathway:** [Open GitHub Issue](https://github.com/AhmadHassan-BTed/Turnitout-Humanizer/issues/new) "
                    f"or contact developer on [WhatsApp](https://wa.me/923225522383)."
                )
