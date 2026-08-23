from __future__ import annotations

import streamlit as st

from core.catalog import TOPIC_GROUPS
from core.prompts import build_explanation_prompt
from providers.clients import PROVIDERS, ProviderError, create_provider
from ui.styles import load_styles


st.set_page_config(
    page_title="Nexora | AI learning studio",
    page_icon="N",
    layout="wide",
    initial_sidebar_state="expanded",
)
load_styles()

if "provider_keys" not in st.session_state:
    st.session_state.provider_keys = {}
if "answer" not in st.session_state:
    st.session_state.answer = None
if "last_request" not in st.session_state:
    st.session_state.last_request = None


def remember_key(provider_id: str, value: str) -> None:
    if value.strip():
        st.session_state.provider_keys[provider_id] = value.strip()


def render_sidebar() -> tuple[str, str]:
    with st.sidebar:
        st.markdown("<div class='brand-mark'>N<span>•</span></div>", unsafe_allow_html=True)
        st.markdown("<div class='brand-name'>Nexora</div>", unsafe_allow_html=True)
        st.caption("A private study room for complex ideas")
        st.divider()
        st.markdown("#### AI connection")
        st.caption("Keys are held in this browser session only. They are never saved by this app.")
        provider_id = st.selectbox(
            "Choose a model provider",
            options=list(PROVIDERS),
            format_func=lambda key: PROVIDERS[key].label,
            label_visibility="collapsed",
        )
        provider = PROVIDERS[provider_id]
        key_value = st.text_input(
            provider.key_label,
            type="password",
            value="" if provider_id not in st.session_state.provider_keys else "Stored for this session",
            disabled=provider_id in st.session_state.provider_keys,
            placeholder=provider.key_placeholder,
            help="This value is only retained in Streamlit session state until this tab session ends.",
        )
        key_col, forget_col = st.columns(2)
        with key_col:
            if st.button("Connect", use_container_width=True, type="primary"):
                if key_value and key_value != "Stored for this session":
                    remember_key(provider_id, key_value)
                    st.success("Connected for this session.")
                elif provider_id in st.session_state.provider_keys:
                    st.info("Already connected.")
                else:
                    st.warning("Enter an API key first.")
        with forget_col:
            if st.button("Forget keys", use_container_width=True):
                st.session_state.provider_keys.clear()
                st.session_state.answer = None
                st.rerun()

        connected = provider_id in st.session_state.provider_keys
        status = "Connected for this session" if connected else "Not connected"
        status_class = "status-online" if connected else "status-offline"
        st.markdown(f"<div class='connection-status {status_class}'><span></span>{status}</div>", unsafe_allow_html=True)
        st.divider()
        st.markdown("#### Learning path")
        st.markdown("<div class='side-note'>Pick a subject, set the depth, and ask for an explanation shaped around the way you learn.</div>", unsafe_allow_html=True)
        st.markdown("<div class='privacy-note'>Session privacy<br><strong>Keys disappear with this session.</strong></div>", unsafe_allow_html=True)
    return provider_id, st.session_state.provider_keys.get(provider_id, "")


def render_topic_picker() -> str:
    st.markdown("<div class='eyebrow'>LEARNING STUDIO / 01</div>", unsafe_allow_html=True)
    st.markdown("<h1>Make the hard stuff <em>click.</em></h1>", unsafe_allow_html=True)
    st.markdown("<p class='lede'>A focused explainer for deep learning, NLP, and agentic AI. Start with a path below or bring your own question.</p>", unsafe_allow_html=True)
    selected_group = st.selectbox("Learning path", list(TOPIC_GROUPS), label_visibility="collapsed")
    topics = TOPIC_GROUPS[selected_group]
    cols = st.columns(4)
    for index, topic in enumerate(topics):
        with cols[index % 4]:
            if st.button(topic, key=f"topic-{selected_group}-{topic}", use_container_width=True):
                st.session_state.topic_text = topic
    return st.session_state.get("topic_text", "")


def render_controls(topic: str) -> tuple[str, str, str, bool]:
    st.markdown("<div class='section-kicker'>YOUR QUESTION</div>", unsafe_allow_html=True)
    question = st.text_area(
        "Topic or question",
        value=topic,
        height=110,
        placeholder="Try: Explain attention mechanisms to me as if I understand linear algebra but not neural networks.",
        label_visibility="collapsed",
    )
    control_cols = st.columns([1, 1, 1, 1.3])
    with control_cols[0]:
        level = st.selectbox("Depth", ["Foundations", "Working knowledge", "Deep dive"])
    with control_cols[1]:
        style = st.selectbox("Voice", ["Clear and practical", "Socratic tutor", "Technical and precise", "Exam prep"])
    with control_cols[2]:
        format_choice = st.selectbox("Format", ["Structured lesson", "Short briefing", "Study notes", "Interview answer"])
    with control_cols[3]:
        analogy = st.toggle("Add a memorable analogy", value=True)
    return question, level, style + " | " + format_choice, analogy


def main() -> None:
    provider_id, api_key = render_sidebar()
    left, right = st.columns([1.55, 1], gap="large")
    with left:
        topic = render_topic_picker()
        question, level, style, analogy = render_controls(topic)
        action_col, hint_col = st.columns([1, 2])
        with action_col:
            explain = st.button("Explain this topic  →", type="primary", use_container_width=True)
        with hint_col:
            st.markdown("<div class='keyboard-hint'>Your response will be generated by the selected provider.</div>", unsafe_allow_html=True)
        if explain:
            if not question.strip():
                st.warning("Add a topic or question first.")
            elif not api_key:
                st.error("Connect an API provider in the sidebar before asking for an explanation.")
            else:
                with st.spinner("Building your explanation..."):
                    try:
                        prompt = build_explanation_prompt(question, level, style, analogy)
                        client = create_provider(provider_id, api_key)
                        st.session_state.answer = client.explain(prompt)
                        st.session_state.last_request = (question, provider_id)
                    except ProviderError as error:
                        st.error(str(error))
        if st.session_state.answer:
            st.markdown("<div class='section-kicker answer-label'>YOUR EXPLANATION</div>", unsafe_allow_html=True)
            last_question, last_provider = st.session_state.last_request
            st.markdown(f"<div class='answer-meta'>{PROVIDERS[last_provider].label} <span>·</span> {last_question}</div>", unsafe_allow_html=True)
            st.markdown(st.session_state.answer)
    with right:
        st.markdown("<div class='right-panel'><div class='section-kicker'>HOW TO USE IT</div><h2>Learn in layers.</h2><p>Good explanations reveal the structure first, then add detail only when it earns its place.</p><div class='layer'><b>01</b><span><strong>Orient</strong><small>What problem does it solve?</small></span></div><div class='layer'><b>02</b><span><strong>Build</strong><small>How does it work under the hood?</small></span></div><div class='layer'><b>03</b><span><strong>Apply</strong><small>When should you use it?</small></span></div><div class='layer'><b>04</b><span><strong>Check</strong><small>Can you explain it back?</small></span></div></div>", unsafe_allow_html=True)
        st.markdown("<div class='topic-cloud'><div class='section-kicker'>COVERED PATHS</div><p>Optimization · RNNs · Transformers · GANs · NLP · Embeddings · Attention · RAG · Agents · Evaluation · Safety</p></div>", unsafe_allow_html=True)


if __name__ == "__main__":
    main()
