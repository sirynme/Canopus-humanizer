"""Streamlit AI Signature & Entropy Checker UI View."""

import streamlit as st
from turnitout.core.checker import ZipPyChecker
from turnitout.core.winnowing import WinnowingEngine


def render_checker_page():
    """Renders 🔍 AI Pattern & Signature Checker page."""
    st.markdown('<div class="main-header">🔍 AI Pattern & Signature Checker</div>', unsafe_allow_html=True)
    st.markdown(
        '<div class="sub-header">ZipPy zlib/lzma Perplexity Entropy & Winnowing Similarity Audit Dashboard</div>',
        unsafe_allow_html=True,
    )

    tab_eval, tab_compare = st.tabs(["📊 Single-Text Entropy Audit", "🔄 Pairwise Similarity Comparison"])

    with tab_eval:
        sample_ai_text = (
            "In conclusion, it is important to delve into the comprehensive tapestry of modern neural networks. "
            "This study plays a pivotal role in illustrating that artificial intelligence stands as a testament "
            "to human innovation. Furthermore, the interplay between stochastic optimization and computational scalability "
            "provides a robust framework for subsequent empirical inquiries."
        )
        check_input = st.text_area("Paste Text to Audit", value=sample_ai_text, height=160)

        if st.button("🔎 Run Entropy & Signature Audit", type="primary", use_container_width=True):
            if not check_input.strip():
                st.warning("Please provide text to audit.")
            else:
                eval_res = ZipPyChecker.evaluate(check_input)
                
                c1, c2, c3, c4 = st.columns(4)
                c1.metric("AI Probability", f"{eval_res['ai_probability']}%")
                c2.metric("Human Confidence", f"{eval_res['human_score']}%")
                c3.metric("Shannon Entropy", f"{eval_res['shannon_entropy']} bits")
                c4.metric("zlib Ratio", f"{eval_res['zlib_compression_ratio']}")

                st.subheader(f"Risk Assessment: {eval_res['risk_rating']}")
                
                if eval_res["detected_markers"]:
                    st.warning(f"⚠️ Detected {len(eval_res['detected_markers'])} formulaic AI markers/clichés:")
                    for marker_info in eval_res["detected_markers"]:
                        st.write(f"- **\"{marker_info['marker']}\"** (x{marker_info['count']}): {marker_info['description']}")
                else:
                    st.success("🎉 Zero formulaic AI markers detected! The text exhibits high lexical diversity.")

    with tab_compare:
        st.caption("Measure similarity index between original document and modified document using Turnitin's Winnowing algorithm (k=5, w=4).")
        col_a, col_b = st.columns(2)
        with col_a:
            text_a = st.text_area("Original Passage", value="We analyze the results using finite difference methods and observe high convergence rates.", height=130)
        with col_b:
            text_b = st.text_area("Modified Passage", value="The results were scrutinized through finite difference schemes, manifesting appreciable convergence rates.", height=130)

        if st.button("⚖️ Compare Winnowing Fingerprints", use_container_width=True):
            winnow = WinnowingEngine(k=5, w=4)
            sim_pct, matches, total_fp = winnow.calculate_similarity(text_a, text_b)
            
            c_sim1, c_sim2, c_sim3 = st.columns(3)
            c_sim1.metric("Winnowing Similarity", f"{sim_pct}%")
            c_sim2.metric("Shared Hashes", matches)
            c_sim3.metric("Original Fingerprints", total_fp)

            if sim_pct < 15.0:
                st.success(f"🛡️ Plagiarism Safe! Similarity ({sim_pct}%) is well below Turnitin's 20% detection boundary.")
            else:
                st.warning(f"Similarity is {sim_pct}%. Consider running humanizer at higher intensity.")
