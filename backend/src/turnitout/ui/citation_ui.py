"""Streamlit Citation Inserter & BibTeX / JSON / LaTeX Generator UI View."""

import streamlit as st
from turnitout.core.citation_engine import CitationEngine


def render_citation_page():
    """Renders 📜 Citation Inserter & Reference Generator page."""
    st.markdown('<div class="main-header">📜 Citation Inserter & Reference Generator</div>', unsafe_allow_html=True)
    st.markdown(
        '<div class="sub-header">Contextual Academic Reference Placement & Auto-Executing BibTeX Packaging</div>',
        unsafe_allow_html=True,
    )

    col_ctrl, col_main = st.columns([1, 2.5], gap="medium")

    with col_ctrl:
        st.subheader("📚 Citation Parameters")
        citation_count_mode = st.radio("Density Mode", options=["Auto Contextual", "Exact Count"], index=0)
        
        count_val = 2
        if citation_count_mode == "Exact Count":
            count_val = st.number_input("Target Citation Count", min_value=1, max_value=20, value=3, step=1)
        
        format_choice = st.selectbox(
            "Citation Marker Format",
            options=["IEEE [1]", "APA (Author, Year)", "LaTeX \\cite{key}"],
            index=0
        )
        discipline_choice = st.selectbox(
            "Discipline Taxonomy",
            options=[
                "Auto-Detect Field",
                "Computer Science & AI",
                "Engineering & Physics",
                "Mathematics & Statistics",
                "Quantitative Finance",
                "Medical & Life Sciences"
            ],
            index=0
        )

        disc_key = None
        if discipline_choice == "Computer Science & AI":
            disc_key = "computer_science"
        elif discipline_choice == "Engineering & Physics":
            disc_key = "engineering_physics"
        elif discipline_choice == "Mathematics & Statistics":
            disc_key = "mathematics_statistics"
        elif discipline_choice == "Quantitative Finance":
            disc_key = "quantitative_finance"
        elif discipline_choice == "Medical & Life Sciences":
            disc_key = "medical_life_sciences"

    with col_main:
        sample_cite_text = (
            "Machine learning architectures provide notable improvements in analyzing genomic sequences "
            "and predicting protein tertiary structures. Furthermore, stochastic optimization algorithms "
            "guarantee stable convergence across high-dimensional parameter spaces. Quantitative models "
            "allow researchers to evaluate derivative pricing surfaces under jump diffusion."
        )
        input_text = st.text_area("Input Document Paragraphs", value=sample_cite_text, height=180)

        if st.button("✨ Insert Contextual Citations", type="primary", use_container_width=True):
            if not input_text.strip():
                st.warning("Please provide text for citation insertion.")
            else:
                engine = CitationEngine()
                target_count = count_val if citation_count_mode == "Exact Count" else max(2, len(input_text.split(".")) // 2)
                res = engine.insert_citations(
                    text=input_text,
                    citation_count=target_count,
                    citation_format=format_choice,
                    discipline=disc_key
                )

                st.success(f"✅ Contextually inserted {res['citation_count']} citations (Discipline: {res['discipline']})")

                st.subheader("📖 Text with Embedded Citations")
                st.text_area("", value=res["cited_text"], height=160, key="cited_output_disp")

                tab_bib, tab_json, tab_records = st.tabs(["BibTeX (citations.bib)", "JSON Package", "Citation Table"])

                with tab_bib:
                    st.code(res["bib_text"], language="bibtex")
                    st.download_button(
                        label="📥 Download BibTeX (citations.bib)",
                        data=res["bib_text"],
                        file_name="citations.bib",
                        mime="text/plain",
                        use_container_width=True
                    )

                with tab_json:
                    import json
                    json_str = json.dumps(res["citations"], indent=2)
                    st.code(json_str, language="json")
                    st.download_button(
                        label="📥 Download Structured JSON (citations.json)",
                        data=json_str,
                        file_name="citations.json",
                        mime="application/json",
                        use_container_width=True
                    )

                with tab_records:
                    if res["citations"]:
                        st.table(res["citations"])
