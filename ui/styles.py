import streamlit as st


def load_styles() -> None:
    st.markdown(
        """
        <style>
        @import url('https://fonts.googleapis.com/css2?family=DM+Mono:wght@400;500&family=Manrope:wght@400;500;600;700;800&display=swap');
        :root { --ink:#15211f; --muted:#6c7773; --line:#dce4df; --paper:#f5f7f1; --white:#fffefa; --teal:#0f6b62; --coral:#e2735b; }
        .stApp { background:var(--paper); color:var(--ink); font-family:'Manrope',sans-serif; }
        .stApp::before { content:''; position:fixed; inset:0; pointer-events:none; opacity:.3; background-image:linear-gradient(rgba(15,107,98,.05) 1px,transparent 1px),linear-gradient(90deg,rgba(15,107,98,.05) 1px,transparent 1px); background-size:38px 38px; mask-image:linear-gradient(to bottom,black,transparent 70%); }
        [data-testid='stHeader'] { background:transparent; }
        [data-testid='stSidebar'] { background:#e9f0e9; border-right:1px solid var(--line); }
        [data-testid='stSidebar'] > div:first-child { padding:2.7rem 1.65rem; }
        .brand-mark { font-size:2.4rem; font-weight:800; color:var(--teal); line-height:.8; letter-spacing:-3px; }
        .brand-mark span { color:var(--coral); font-size:1.1rem; vertical-align:top; letter-spacing:0; }
        .brand-name { font-size:1.1rem; font-weight:800; letter-spacing:-.5px; margin-top:.3rem; }
        .stCaption, [data-testid='stSidebar'] .stMarkdown p { color:var(--muted); }
        h1 { font-size:clamp(2.6rem,5vw,5.1rem); letter-spacing:-3px; line-height:.98; margin:.4rem 0 1.15rem; max-width:760px; font-weight:800; }
        h1 em { color:var(--coral); font-style:normal; }
        h2 { font-size:1.8rem; letter-spacing:-1px; margin:.7rem 0 .5rem; }
        .lede { color:#5d6964; font-size:1.05rem; max-width:630px; line-height:1.7; margin-bottom:2.1rem; }
        .eyebrow,.section-kicker { color:var(--teal); font:500 .7rem 'DM Mono',monospace; letter-spacing:1.4px; }
        .section-kicker { margin-top:2.1rem; margin-bottom:.7rem; }
        .stButton > button { border:1px solid #cbd7d0; border-radius:3px; background:rgba(255,254,250,.7); color:var(--ink); font-weight:600; min-height:2.7rem; transition:all .2s ease; }
        .stButton > button:hover { border-color:var(--teal); color:var(--teal); transform:translateY(-1px); }
        .stButton > button[kind='primary'] { background:var(--teal); border-color:var(--teal); color:white; }
        .stButton > button[kind='primary']:hover { background:#09554e; color:white; }
        [data-testid='stTextArea'] textarea, [data-baseweb='select'] > div, [data-testid='stTextInput'] input { border-radius:3px; border-color:#cbd7d0; background:var(--white); }
        .right-panel { background:#173c38; color:#f6fbf4; padding:2rem; margin-top:2.3rem; min-height:435px; position:relative; overflow:hidden; }
        .right-panel::after { content:'N'; position:absolute; right:-.1rem; bottom:-3.7rem; font-size:16rem; line-height:1; color:rgba(255,255,255,.045); font-weight:800; }
        .right-panel .section-kicker { color:#a7d1c3; }
        .right-panel p { color:#c4d7d0; line-height:1.65; }
        .layer { display:flex; gap:1rem; border-top:1px solid rgba(255,255,255,.16); padding:1rem 0; position:relative; z-index:1; }
        .layer b { color:#e8a18e; font:500 .72rem 'DM Mono',monospace; padding-top:.15rem; }
        .layer span { display:flex; flex-direction:column; gap:.25rem; }
        .layer small { color:#b5cec6; }
        .topic-cloud { border-top:1px solid var(--line); margin-top:1.5rem; padding-top:.4rem; }
        .topic-cloud p { color:var(--muted); line-height:1.7; font-size:.88rem; }
        .connection-status { margin-top:.9rem; font:500 .72rem 'DM Mono',monospace; display:flex; align-items:center; gap:.5rem; }
        .connection-status span { width:7px; height:7px; border-radius:50%; display:inline-block; }
        .status-online { color:var(--teal); }.status-online span { background:#42a47e; }.status-offline { color:var(--muted); }.status-offline span { background:#acb6b1; }
        .side-note { border-left:2px solid var(--coral); padding:.15rem 0 .15rem .8rem; font-size:.8rem; line-height:1.6; color:#52615b; }
        .privacy-note { margin-top:5rem; padding-top:1rem; border-top:1px solid #d1ddd4; color:#718078; font:500 .7rem 'DM Mono',monospace; line-height:1.8; }.privacy-note strong { color:var(--teal); font-weight:500; }
        .keyboard-hint { color:var(--muted); font:400 .7rem 'DM Mono',monospace; padding:.9rem 0; }
        .answer-label { margin-top:3.5rem; }.answer-meta { color:var(--muted); font:400 .72rem 'DM Mono',monospace; border-bottom:1px solid var(--line); padding-bottom:.8rem; margin-bottom:1.3rem; }.answer-meta span { color:var(--coral); padding:0 .4rem; }
        @media (max-width: 900px) { h1 { font-size:3rem; letter-spacing:-2px; }.right-panel { margin-top:1rem; }.privacy-note { margin-top:2rem;} }
        </style>
        """,
        unsafe_allow_html=True,
    )
