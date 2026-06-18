"""
Interview Preparation Assistant
Streamlit app: generates questions, records/accepts answers (speech-to-text),
scores them with an LLM + NLP signals, and gives structured feedback.
"""

import streamlit as st
from audio_recorder_streamlit import audio_recorder

from src.question_generator import QuestionGenerator
from src.speech_to_text import transcribe_audio
from src.scorer import AnswerScorer
from src.feedback import FeedbackGenerator
from src.utils import get_api_key, build_report


st.set_page_config(page_title="Interview Prep Assistant", page_icon="🎤", layout="centered")

# ---------- Session state ----------
defaults = {
    "questions": [],
    "current_index": 0,
    "results": [],
    "stage": "setup",  # setup -> interview -> report
    "role": "",
}
for key, value in defaults.items():
    if key not in st.session_state:
        st.session_state[key] = value


@st.cache_resource
def get_clients():
    api_key = get_api_key()
    return (
        QuestionGenerator(api_key),
        AnswerScorer(api_key),
        FeedbackGenerator(api_key),
    )


st.title("🎤 Interview Preparation Assistant")
st.caption("Practice mock interviews with AI-generated questions, speech-to-text answers, and instant scoring.")

# ---------- Setup stage ----------
if st.session_state.stage == "setup":
    with st.form("setup_form"):
        role = st.text_input("Target role", placeholder="e.g. AI/ML Engineer")
        experience = st.selectbox("Experience level", ["Fresher", "1-3 years", "3-5 years", "5+ years"])
        num_questions = st.slider("Number of questions", 3, 10, 5)
        mix = st.selectbox("Question focus", ["balanced", "technical", "behavioral"])
        submitted = st.form_submit_button("Generate questions")

    if submitted:
        if not role.strip():
            st.warning("Please enter a target role.")
        else:
            with st.spinner("Generating interview questions..."):
                qgen, _, _ = get_clients()
                questions = qgen.generate_questions(role, experience, num_questions, mix)
            st.session_state.questions = questions
            st.session_state.role = role
            st.session_state.current_index = 0
            st.session_state.results = []
            st.session_state.stage = "interview"
            st.rerun()

# ---------- Interview stage ----------
elif st.session_state.stage == "interview":
    idx = st.session_state.current_index
    questions = st.session_state.questions

    if idx >= len(questions):
        st.session_state.stage = "report"
        st.rerun()
    else:
        q = questions[idx]
        st.subheader(f"Question {idx + 1} of {len(questions)}")
        st.markdown(f"**[{q.get('type', 'general').title()} · {q.get('difficulty', 'medium').title()}]**")
        st.write(q["question"])

        answer_text = st.text_area("Type your answer (optional if recording audio)", key=f"text_{idx}")

        st.write("Or record your answer:")
        audio_bytes = audio_recorder(text="Click to record", icon_size="2x", key=f"audio_{idx}")

        transcribed = ""
        if audio_bytes:
            with st.spinner("Transcribing your answer..."):
                transcribed = transcribe_audio(audio_bytes)
            st.success("Transcribed answer:")
            st.write(transcribed)

        final_answer = transcribed.strip() if transcribed.strip() else answer_text.strip()

        if st.button("Submit answer", type="primary"):
            with st.spinner("Scoring your answer..."):
                _, scorer, feedback_gen = get_clients()
                scores = scorer.score_answer(q["question"], final_answer, st.session_state.role)
                feedback = feedback_gen.generate_feedback(q["question"], final_answer, scores, st.session_state.role)

            st.session_state.results.append({
                "question": q["question"],
                "answer": final_answer,
                "scores": scores,
                "feedback": feedback,
            })
            st.session_state.current_index += 1
            st.rerun()

# ---------- Report stage ----------
elif st.session_state.stage == "report":
    st.subheader("📊 Interview Report")
    results = st.session_state.results

    if results:
        avg_score = round(sum(r["scores"].get("overall", 0) for r in results) / len(results), 1)
        st.metric("Average score", f"{avg_score} / 10")

        for i, r in enumerate(results, start=1):
            with st.expander(f"Q{i}: {r['question']}"):
                st.write(f"**Your answer:** {r['answer'] or '_No answer given_'}")
                s = r["scores"]
                st.write(
                    f"Relevance: {s.get('relevance')} · Clarity: {s.get('clarity')} · "
                    f"Technical depth: {s.get('technical_depth')} · Communication: {s.get('communication')} "
                    f"→ **Overall: {s.get('overall')}/10**"
                )
                st.write(f"**Feedback:** {r['feedback']}")

        report_text = build_report(st.session_state.role, results)
        st.download_button("Download full report (.txt)", report_text, file_name="interview_report.txt")
    else:
        st.info("No answers recorded.")

    if st.button("Start a new mock interview"):
        for key, value in defaults.items():
            st.session_state[key] = value
        st.rerun()
