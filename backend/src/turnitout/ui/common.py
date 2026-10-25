"""Common UI Utilities, Custom CSS & Attribution Footer for Turnitout."""

import streamlit as st
from turnitout.config import GLOBAL_CONFIG


def apply_custom_styles():
    """Injects high-end, responsive custom styling matching the project aesthetics."""
    st.markdown(
        """
        <style>
        /* Primary Branding & Typography */
        @import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700;800&family=JetBrains+Mono:wght@400;500&display=swap');
        
        html, body, [class*="css"] {
            font-family: 'Inter', -apple-system, BlinkMacSystemFont, sans-serif;
        }
        
        .main-header {
            font-size: 2.2rem;
            font-weight: 800;
            background: linear-gradient(135deg, #1D3557 0%, #457B9D 100%);
            -webkit-background-clip: text;
            -webkit-text-fill-color: transparent;
            margin-bottom: 0.2rem;
        }
        
        .sub-header {
            font-size: 1.05rem;
            color: #6c757d;
            margin-bottom: 1.5rem;
        }

        .metric-card {
            background: #f8f9fa;
            border: 1px solid #e9ecef;
            border-radius: 12px;
            padding: 16px;
            text-align: center;
            box-shadow: 0 2px 4px rgba(0,0,0,0.02);
        }

        .metric-value {
            font-size: 1.8rem;
            font-weight: 700;
            color: #1D3557;
        }

        .metric-label {
            font-size: 0.85rem;
            color: #6c757d;
            text-transform: uppercase;
            letter-spacing: 0.5px;
        }

        .stage-badge {
            display: inline-block;
            background: #EBF2FA;
            color: #1D3557;
            padding: 4px 10px;
            border-radius: 6px;
            font-size: 0.8rem;
            font-weight: 600;
            margin: 2px;
        }

        .footer-container {
            margin-top: 3.5rem;
            padding-top: 1.5rem;
            border-top: 1px solid #e9ecef;
            text-align: center;
            font-size: 0.95rem;
            color: #6c757d;
        }

        .footer-link {
            color: #1D3557;
            font-weight: 600;
            text-decoration: none;
        }

        .footer-link:hover {
            text-decoration: underline;
        }
        </style>
        """,
        unsafe_allow_html=True
    )


def render_footer():
    """Renders attribution footer and QuillBot verification banner as required by AGENTS.md."""
    st.markdown(
        """
        <div class="footer-container">
            <p>
                <strong>⚡ Turnitout Core v2.6.0</strong> — Built by 
                <a href="https://github.com/AhmadHassan-BTed" class="footer-link" target="_blank">Ahmad Hassan</a>.
                100% Deterministic & Privacy-Guaranteed.
            </p>
            <p style="background: #eef4f8; padding: 10px 16px; border-radius: 8px; display: inline-block; margin-top: 8px;">
                🔍 <strong>Verify AI Content:</strong> Paste your processed paragraph 
                <a href="https://quillbot.com/ai-content-detector" target="_blank" rel="noopener noreferrer" style="color: #05668D; font-weight: 700; text-decoration: underline;">
                    here on QuillBot AI Content Detector
                </a> to independently confirm 0% AI detection.
            </p>
        </div>
        """,
        unsafe_allow_html=True
    )
