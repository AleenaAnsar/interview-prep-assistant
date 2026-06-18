import streamlit as st
from audio_recorder_streamlit import audio_recorder

from src.question_generator import QuestionGenerator
from src.speech_to_text import transcribe_audio
from src.scorer import AnswerScorer
from src.feedback import FeedbackGenerator
from src.utils import get_api_key, build_report


st.set_page_config(
    page_title="Interview Prep Assistant",
    page_icon="🎤",
    layout="centered"
)

if "questions" not in st.session_state:
    st.session_state.questions = []
if "current_index" not in st.session_state:
    st.session_state.current_index = 0
if "results" not in st.session_state:
    st.session_state.results = []
if "stage" not in st.session_state:
    st.session_state.stage = "setup"
if "role" not in st.session_state:
    st.session_state.role = ""


@st.cache_resource
def get_clients():
    api_key = get_api_key()
    qgen = QuestionGenerator(api_key)
    scorer = AnswerScorer(api_key)
    feedback_gen = FeedbackGenerator(api_key)
    return qgen, scorer, feedback_gen


st.title("Interview Preparation Assistant")
st.caption("Practice mock interviews with AI-generated questions, speech-to-text answers, and instant scoring")
st.divider()

# SETUP STAGE
if st.session_state.stage == "setup":
    st.header("Configure Your Interview")
    
    role = st.selectbox(
        "Target Role",
        ["AI/ML Engineer", "Software Engineer", "Data Scientist", "Product Manager", "Web Developer", "Full Stack Developer", "DevOps Engineer", "Cloud Engineer"],
        key="selected_role"
    )
    
    experience = st.selectbox(
        "Experience Level",
        ["Fresher", "Intermediate", "Experienced"],
        key="selected_experience"
    )
    
    num_questions = st.slider(
        "Number of Questions",
        min_value=3,
        max_value=50,
        value=5,
        step=1,
        key="num_questions"
    )
    
    mix = st.selectbox(
        "Question Focus",
        ["balanced", "technical", "behavioral"],
        key="selected_mix"
    )
    
    st.divider()
    
    if st.button("Generate Interview Questions", type="primary", use_container_width=True):
        if not role:
            st.error("Please select a target role")
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

# INTERVIEW STAGE
elif st.session_state.stage == "interview":
    idx = st.session_state.current_index
    questions = st.session_state.questions
    
    if idx >= len(questions):
        st.session_state.stage = "report"
        st.rerun()
    
    q = questions[idx]
    
    st.progress((idx + 1) / len(questions))
    st.caption(f"Question {idx + 1} of {len(questions)}")
    st.divider()
    
    question_type = q.get('type', 'general').title()
    difficulty = q.get('difficulty', 'medium').title()
    st.markdown(f"**[{question_type} - {difficulty}]**")
    st.markdown(f"### {q['question']}")
    st.divider()
    
    # Answer field
    st.text_area("Type your answer (optional if recording audio)", key=f"text_{idx}", height=120)
    
    st.write("Or record your answer:")
    audio_recorder(text="Click to record", icon_size="2x", key=f"audio_{idx}")
    st.divider()
    
    # BUTTONS ROW - Submit, Review, Quit
    col1, col2, col3 = st.columns([2, 1, 1])
    
    with col1:
        submit_clicked = st.button("Submit Answer", type="primary", use_container_width=True)
    
    with col2:
        review_clicked = st.button("Review Answers", use_container_width=True)
    
    with col3:
        quit_clicked = st.button("Quit Interview", use_container_width=True)
    
    # Handle button clicks
    if review_clicked:
        st.session_state.stage = "review"
        st.rerun()
    
    if quit_clicked:
        st.session_state.stage = "quit"
        st.rerun()
    
    if submit_clicked:
        answer_text = st.session_state.get(f"text_{idx}", "")
        audio_bytes = st.session_state.get(f"audio_{idx}", None)
        
        transcribed = ""
        if audio_bytes:
            with st.spinner("Transcribing..."):
                transcribed = transcribe_audio(audio_bytes)
        
        final_answer = transcribed.strip() if transcribed.strip() else answer_text.strip()
        
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

# REVIEW STAGE
elif st.session_state.stage == "review":
    st.header("Review Your Answers")
    
    results = st.session_state.results
    
    if results:
        st.info(f"Answered **{len(results)}** of **{len(st.session_state.questions)}** questions")
        avg_score = round(sum(r["scores"].get("overall", 0) for r in results) / len(results), 1)
        st.metric("Current Average Score", f"{avg_score} / 10")
        st.divider()
        
        for i, r in enumerate(results, start=1):
            with st.expander(f"Q{i}: {r['question']}"):
                st.write(f"**Answer:** {r['answer'] or '_No answer_'}")
                s = r["scores"]
                st.write(f"**Scores:** Relevance={s.get('relevance')}, Clarity={s.get('clarity')}, Technical={s.get('technical_depth')}, Communication={s.get('communication')}, **Overall={s.get('overall')}/10**")
                st.write(f"**Feedback:** {r['feedback']}")
        
        st.divider()
        col1, col2 = st.columns(2)
        with col1:
            if st.button("Continue", type="primary", use_container_width=True):
                st.session_state.stage = "interview"
                st.rerun()
        with col2:
            if st.button("Quit", use_container_width=True):
                st.session_state.stage = "quit"
                st.rerun()
    else:
        st.warning("No answers yet")
        if st.button("Go Back", type="primary", use_container_width=True):
            st.session_state.stage = "interview"
            st.rerun()

# QUIT STAGE
elif st.session_state.stage == "quit":
    st.header("Quit Interview")
    
    results = st.session_state.results
    
    if results:
        st.info(f"Answered **{len(results)}** of **{len(st.session_state.questions)}** questions")
        avg_score = round(sum(r["scores"].get("overall", 0) for r in results) / len(results), 1)
        st.metric("Your Average Score", f"{avg_score} / 10")
        st.divider()
        
        col1, col2 = st.columns(2)
        with col1:
            if st.button("Review Answers", type="primary", use_container_width=True):
                st.session_state.stage = "review"
                st.rerun()
        with col2:
            if st.button("Start New", use_container_width=True):
                st.session_state.questions = []
                st.session_state.current_index = 0
                st.session_state.results = []
                st.session_state.stage = "setup"
                st.session_state.role = ""
                st.rerun()
    else:
        st.warning("No answers yet")
        if st.button("Start New Interview", type="primary", use_container_width=True):
            st.session_state.questions = []
            st.session_state.current_index = 0
            st.session_state.results = []
            st.session_state.stage = "setup"
            st.session_state.role = ""
            st.rerun()

# REPORT STAGE
elif st.session_state.stage == "report":
    st.header("Interview Report")
    
    results = st.session_state.results
    
    if results:
        avg_score = round(sum(r["scores"].get("overall", 0) for r in results) / len(results), 1)
        st.metric("Average Score", f"{avg_score} / 10")
        st.divider()
        
        for i, r in enumerate(results, start=1):
            with st.expander(f"Q{i}: {r['question']}"):
                st.write(f"**Answer:** {r['answer'] or '_No answer_'}")
                s = r["scores"]
                st.write(f"**Scores:** Relevance={s.get('relevance')}, Clarity={s.get('clarity')}, Technical={s.get('technical_depth')}, Communication={s.get('communication')}, **Overall={s.get('overall')}/10**")
                st.write(f"**Feedback:** {r['feedback']}")
        
        st.divider()
        report_text = build_report(st.session_state.role, results)
        st.download_button("Download Report (.txt)", report_text, file_name="interview_report.txt", use_container_width=True)
    else:
        st.info("No answers")
    
    st.divider()
    if st.button("Start New Interview", use_container_width=True):
        st.session_state.questions = []
        st.session_state.current_index = 0
        st.session_state.results = []
        st.session_state.stage = "setup"
        st.session_state.role = ""
        st.rerun()