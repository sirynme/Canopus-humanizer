"""Streamlit Humanizer & Plagiarism Remover UI View."""

import streamlit as st
from turnitout.config import ConfigNamespace
from turnitout.core.doc_processor import DocumentProcessor
from turnitout.core.modifier import DocumentModifier


def render_humanizer_page():
    """Renders ⚡ Plagiarism & AI Remover page."""
    st.markdown('<div class="main-header">⚡ Plagiarism & AI Remover</div>', unsafe_allow_html=True)
    st.markdown(
        '<div class="sub-header">Zero-Generative-AI Footprint Removal Engine — In-Place DOCX, LaTeX & Text Disruption</div>',
        unsafe_allow_html=True,
    )

    col_settings, col_content = st.columns([1, 2.5], gap="medium")

    with col_settings:
        st.subheader("⚙️ Evasion Parameters")
        intensity = st.slider(
            "Paraphrasing Intensity",
            min_value=10.0,
            max_value=100.0,
            value=70.0,
            step=5.0,
            help="Higher intensity increases synonym aggressiveness and syntactic permutations."
        )
        style = st.selectbox(
            "Writing Register",
            options=["academic", "conversational", "technical"],
            index=0
        )
        
        with st.expander("🛠️ Advanced Stage Toggles", expanded=False):
            enable_voice = st.checkbox("Active ↔ Passive Voice Inversion", value=True)
            enable_fusion = st.checkbox("Sentence Fusion (Anti-Burstiness)", value=True)
            enable_transition = st.checkbox("Transition Phrase Injection", value=True)
            enable_reorder = st.checkbox("Clause Word Reordering", value=True)
            enable_nominal = st.checkbox("Nominalization (Verb ↔ Noun)", value=True)
            enable_appositive = st.checkbox("Appositive Injection (Entropy Bomb)", value=True)
            enable_discourse = st.checkbox("Discourse Marker Rotation", value=True)
            enable_ngram = st.checkbox("Winnowing 5-Gram Audit", value=True)

        protected_input = st.text_area(
            "🔒 Protected Terms (comma-separated)",
            value="ResNet-50, PyTorch, CRISPR-Cas9",
            help="Terms that must never be altered or replaced."
        )
        protected_set = {t.strip() for t in protected_input.split(",") if t.strip()}

    with col_content:
        tab_text, tab_file = st.tabs(["✍️ Direct Text", "📁 Single & Multi-File Upload"])

        with tab_text:
            sample_text = (
                "Furthermore, our experimental findings demonstrate that deep learning models "
                "frequently introduce formulaic syntax across large datasets. This study plays a "
                "pivotal role in illustrating that artificial intelligence stands as a testament "
                "to human innovation. In conclusion, it is important to delve into the comprehensive "
                "tapestry of modern neural networks."
            )
            user_text = st.text_area("Input Document / Text", value=sample_text, height=180)

            if st.button("🚀 Humanize Text", type="primary", use_container_width=True):
                if not user_text.strip():
                    st.warning("Please enter text to humanize.")
                else:
                    cfg = ConfigNamespace()
                    cfg.INTENSITY = intensity
                    cfg.STYLE = style
                    cfg.ENABLE_VOICE_TRANSFORM = enable_voice
                    cfg.ENABLE_SENTENCE_FUSION = enable_fusion
                    cfg.ENABLE_TRANSITION_INJECT = enable_transition
                    cfg.ENABLE_WORD_REORDER = enable_reorder
                    cfg.ENABLE_NOMINALIZATION = enable_nominal
                    cfg.ENABLE_APPOSITIVE = enable_appositive
                    cfg.ENABLE_DISCOURSE_ROTATE = enable_discourse
                    cfg.ENABLE_NGRAM_AUDIT = enable_ngram

                    modifier = DocumentModifier(config=cfg)
                    result_text = modifier.modify_document(user_text, protected_terms=protected_set)

                    st.success("✅ Document Humanized Successfully!")

                    # Metrics Row
                    m1, m2, m3, m4 = st.columns(4)
                    m1.metric("Words", len(user_text.split()))
                    m2.metric("Transforms", modifier.total_transforms)
                    m3.metric("Voice Flips", modifier.voice_transform_count)
                    m4.metric("Appositives", modifier.appositive_count)

                    col_orig, col_res = st.columns(2)
                    with col_orig:
                        st.caption("Original")
                        st.text_area("", value=user_text, height=220, disabled=True, key="orig_disp")
                    with col_res:
                        st.caption("Humanized (0% AI / Turnitin Proof)")
                        st.text_area("", value=result_text, height=220, key="humanized_disp")

                    st.download_button(
                        label="📥 Download Humanized Text",
                        data=result_text,
                        file_name="turnitout_humanized.txt",
                        mime="text/plain",
                        use_container_width=True
                    )

        with tab_file:
            uploaded_files = st.file_uploader(
                "Upload .docx, .tex, .md, or .txt files",
                type=["docx", "tex", "md", "txt"],
                accept_multiple_files=True
            )
            if uploaded_files and st.button("⚡ Process All Uploaded Files", type="primary"):
                cfg = ConfigNamespace()
                cfg.INTENSITY = intensity
                cfg.STYLE = style
                modifier = DocumentModifier(config=cfg)
                processor = DocumentProcessor(modifier=modifier)

                processed_archive_files = []
                progress_bar = st.progress(0)

                for idx, file in enumerate(uploaded_files):
                    name = file.name
                    raw_bytes = file.read()
                    ext = name.split(".")[-1].lower()

                    if ext == "docx":
                        out_bytes = processor.process_docx(raw_bytes, protected_terms=protected_set)
                        processed_archive_files.append((f"humanized_{name}", out_bytes))
                    elif ext == "tex":
                        text_str = raw_bytes.decode("utf-8", errors="ignore")
                        out_str = processor.process_latex(text_str, protected_terms=protected_set)
                        processed_archive_files.append((f"humanized_{name}", out_str.encode("utf-8")))
                    elif ext == "md":
                        text_str = raw_bytes.decode("utf-8", errors="ignore")
                        out_str = processor.process_markdown(text_str, protected_terms=protected_set)
                        processed_archive_files.append((f"humanized_{name}", out_str.encode("utf-8")))
                    else:
                        text_str = raw_bytes.decode("utf-8", errors="ignore")
                        out_str = processor.process_plain_text(text_str, protected_terms=protected_set)
                        processed_archive_files.append((f"humanized_{name}", out_str.encode("utf-8")))

                    progress_bar.progress((idx + 1) / len(uploaded_files))

                zip_name, zip_bytes = processor.create_in_memory_zip(processed_archive_files)
                st.success(f"🎉 Processed {len(uploaded_files)} files in-place!")

                st.download_button(
                    label=f"📦 Download Branded ZIP Package ({zip_name})",
                    data=zip_bytes,
                    file_name=zip_name,
                    mime="application/zip",
                    use_container_width=True
                )
