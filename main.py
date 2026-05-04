import sys
import json
from pathlib import Path
import streamlit as st

BASE_DIR = Path(__file__).parent
sys.path.insert(0, str(BASE_DIR / "src"))

from nlp_processor import process_input
from matcher import CareerMatcher, MatcherError
from roadmap_generator import generate_roadmap, RoadmapError
from recommender import recommend_resources, ResourceError

from visualizer import (
    plot_career_confidence,
    plot_weekly_workload,
    plot_skill_tier_distribution,
)

SKILLS_PATH    = BASE_DIR / "data" / "skills.json"
RESOURCES_PATH = BASE_DIR / "data" / "resources.csv"
CONFIDENCE_THRESHOLD = 30

st.set_page_config(page_title="Career Guidance System", page_icon="", layout="wide")
st.markdown("""
<style>
    body, .stApp { background-color: #1C1C2E; color: #ECEFF4; }
    .stTextArea textarea { background-color: #2A2A3E !important; color: #ECEFF4 !important; border: 1px solid #444466; border-radius: 8px; }
    .stButton>button { background: linear-gradient(135deg,#4A90D9,#2ECC71); color:#fff; border:none; border-radius:8px; padding:0.5rem 2rem; font-weight:bold; }
    .stButton>button:hover { opacity:0.9; }
    h1,h2,h3 { color:#ECEFF4 !important; }
</style>
""", unsafe_allow_html=True)

st.title("Career Guidance System")
st.caption("AI-powered career matching · Personalized roadmaps · Smart recommendations")
st.divider()

with st.sidebar:
    st.header("Settings")
    weeks = int(st.select_slider("Roadmap Duration (weeks)", options=[4, 8, 12], value=8))
    top_n = int(st.slider("Top career matches", 1, 5, 3))

    st.divider()
    st.markdown("**Skill Gap Mode**")
    known_input = st.text_area(
        "Skills you already know (comma-separated)",
        placeholder="e.g. Python, SQL, Git",
        height=80
    )
    known_skills = [s.strip().lower() for s in known_input.split(",") if s.strip()] if known_input else []
    st.caption(f"{len(known_skills)} skill(s) entered")

    st.divider()
    st.markdown("**Active Settings**")
    st.info(
        f"Duration: **{weeks} weeks**\n\n"
        f"Top matches: **{top_n}**\n\n"
        f"Known skills: **{len(known_skills)}** "
        + (f"({', '.join(known_skills[:3])}{'...' if len(known_skills) > 3 else ''})" if known_skills else "(none)")
    )

user_text = st.text_area(
    "Describe your interests, background, and goals",
    placeholder="e.g. I love building web apps and working with databases...",
    height=120
)

run_btn = st.button("Analyze & Generate Roadmap", use_container_width=True)

if run_btn:
    if not user_text.strip():
        st.error("Please enter a description.")
        st.stop()

    if not SKILLS_PATH.exists():
        st.error("skills.json not found.")
        st.stop()

    with st.spinner("Processing..."):
        nlp_result = process_input(user_text)

    with st.spinner("Matching careers..."):
        try:
            matcher = CareerMatcher(str(SKILLS_PATH))
            matches = matcher.match(nlp_result, top_n=top_n)
            matches = sorted(matches, key=lambda x: x["confidence_pct"], reverse=True)
            top_match = matches[0]

            if top_match["confidence_pct"] < CONFIDENCE_THRESHOLD:
                st.warning(
                    "We couldn't confidently match your input.\n\n"
                    "Try keywords like:\n"
                    "- web development\n"
                    "- machine learning\n"
                    "- data analysis\n"
                    "- cybersecurity"
                )
                st.stop()
        except MatcherError as e:
            st.error(str(e))
            st.stop()

    with st.spinner("Generating roadmap..."):
        try:
            top_career = matches[0]["career"]
            roadmap = generate_roadmap(
                career=top_career,
                skills_path=str(SKILLS_PATH),
                total_weeks=weeks,
                known_skills=known_skills,
            )
        except RoadmapError as e:
            st.error(str(e))
            st.stop()

    with open(SKILLS_PATH) as f:
        career_data = json.load(f)

    st.success(f"Best match: {top_career.replace('_', ' ').title()}")

    # Confirm sidebar settings are active
    col_a, col_b, col_c = st.columns(3)
    col_a.metric("Roadmap Duration", f"{weeks} weeks")
    col_b.metric("Top Matches Shown", top_n)
    col_c.metric("Known Skills Skipped", len(roadmap["meta"]["skipped_skills"]))
    if roadmap["meta"]["skipped_skills"]:
        st.caption(f"Skipped: {', '.join(roadmap['meta']['skipped_skills'])}")

    st.divider()

    tab1, tab2, tab3, tab4 = st.tabs(["Matches", "Roadmap", "Visualizations", "Resources"])

    with tab1:
        st.subheader("Career Matches")

        for rank, m in enumerate(matches, 1):
            with st.expander(f"#{rank} — {m['career']} ({m['confidence_pct']}%)", expanded=(rank == 1)):
                st.write(m)

        st.pyplot(plot_career_confidence(matches))

    with tab2:
        meta = roadmap["meta"]
        st.subheader(meta["career_display"])

        st.write(f"Duration: {meta['total_weeks']} weeks")
        st.write(f"Skills: {meta['total_skills']}")

        for week in roadmap["weekly_plan"]:
            with st.expander(f"Week {week['week']} — {week['theme']}"):
                st.write(week)

    with tab3:
        st.subheader("Visualizations")

        col1, col2 = st.columns(2)
        with col1:
            st.pyplot(plot_weekly_workload(roadmap))
        with col2:
            st.pyplot(plot_skill_tier_distribution(roadmap))

    with tab4:
        st.subheader("Resources")

        if RESOURCES_PATH.exists():
            recs = recommend_resources(
                [s for w in roadmap["weekly_plan"] for s in w["skills"]],
                str(RESOURCES_PATH)
            )
            for skill, items in recs.items():
                with st.expander(skill):
                    for r in items:
                        st.write(r["name"], "-", r["url"])
        else:
            st.info("resources.csv not found")

    st.download_button(
        label="Download Roadmap JSON",
        data=json.dumps(roadmap, indent=2),
        file_name="roadmap.json",
        mime="application/json",
    )
