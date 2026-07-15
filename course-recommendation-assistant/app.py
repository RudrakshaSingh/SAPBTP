"""Streamlit front end for the Course Recommendation Assistant (bonus #5).

Run with:
    streamlit run app.py
"""

import os

import streamlit as st
from dotenv import load_dotenv

from rag_assistant import CourseRecommendationAssistant

load_dotenv()

st.set_page_config(page_title="Course Recommendation Assistant", page_icon="🎓")


@st.cache_resource(show_spinner="Indexing course catalog…")
def get_assistant() -> CourseRecommendationAssistant:
    """Build the assistant once and reuse it across reruns."""
    return CourseRecommendationAssistant()


st.title("🎓 Course Recommendation Assistant")
st.caption("RAG over the SAP + AI course catalog — powered by LangChain & Gemini")

# --- Sidebar ------------------------------------------------------------- #
with st.sidebar:
    st.header("Setup")
    if os.getenv("GOOGLE_API_KEY"):
        st.success("GOOGLE_API_KEY detected")
    else:
        st.warning("Set GOOGLE_API_KEY in a .env file to enable the assistant.")

    st.markdown(
        "**Try asking:**\n"
        "- I'm an SAP ABAP developer with no AI experience. Where do I start?\n"
        "- I know Python and LLMs. How do I learn to build RAG apps?\n"
        "- What is the full path to building custom Joule agents?"
    )
    if st.button("Clear conversation"):
        st.session_state.pop("messages", None)
        get_assistant().history.clear()
        st.rerun()

# --- Conversation history (bonus #2) ------------------------------------- #
if "messages" not in st.session_state:
    st.session_state.messages = []

for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])

prompt = st.chat_input("Describe your background and what you want to learn…")

if prompt:
    st.session_state.messages.append({"role": "user", "content": prompt})
    with st.chat_message("user"):
        st.markdown(prompt)

    with st.chat_message("assistant"):
        try:
            assistant = get_assistant()
            with st.spinner("Thinking…"):
                rec = assistant.recommend(prompt)

            names = [s.course_name for s in rec.sources] or rec.recommended_courses
            st.markdown("**Recommended courses:** " + ", ".join(names))
            st.markdown(f"**Reason:** {rec.reason}")

            if rec.prerequisites:
                st.markdown("**Prerequisites:**")
                for pre in rec.prerequisites:
                    st.markdown(f"- {pre}")

            if rec.learning_sequence:
                st.markdown(
                    "**Learning sequence:** " + " → ".join(rec.learning_sequence)
                )

            col1, col2 = st.columns(2)
            col1.metric("Total learning hours", f"{rec.total_learning_hours} h")
            col2.metric("Confidence", f"{rec.confidence:.0%}")

            with st.expander("Sources (metadata)"):
                for src in rec.sources:
                    st.markdown(
                        f"- **{src.course_id}** — {src.course_name} "
                        f"· {src.experience_level} · {src.duration} "
                        f"· `{src.source}`"
                    )

            with st.expander("Raw structured output (Pydantic)"):
                st.json(rec.model_dump())

            # Store a compact summary for the visible chat transcript.
            summary = (
                f"**Recommended:** {', '.join(names)}\n\n{rec.reason}\n\n"
                f"_Total: {rec.total_learning_hours}h · "
                f"Confidence: {rec.confidence:.0%}_"
            )
            st.session_state.messages.append(
                {"role": "assistant", "content": summary}
            )
        except Exception as exc:  # noqa: BLE001 - surface any setup error to the UI
            st.error(f"Something went wrong: {exc}")
