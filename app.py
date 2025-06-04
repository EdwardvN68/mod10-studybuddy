import streamlit as st
import pandas as pd
import time

# ✅ Make sure quiz history exists before it's used
if "quiz_history" not in st.session_state:
    st.session_state.quiz_history = []

if "quiz_logged" not in st.session_state:
    st.session_state.quiz_logged = False

# ✅ Load essay questions from your CSV file
@st.cache_data
def load_essays():
    return pd.read_csv("Mod10_Essay_questions.csv")

# ✅ Set up memory for essay mode screen switching
if "essay_mode" not in st.session_state:
    st.session_state.essay_mode = "menu"  # can be "menu" or "view"
    st.session_state.selected_essay_index = None
    # ✅ Keep track of which essays the user has reviewed
if "reviewed_essays" not in st.session_state:
    st.session_state.reviewed_essays = set()

# Page config – always first
st.set_page_config(page_title="Mod 10 Study Buddy")

# 🧼 Reset quiz state if user is not on quiz menu
if st.session_state.get("menu_option") != "📝 Start MCQ Practice Quiz":
    for key in ["quiz_questions", "current_question", "score", "answers", "advance", "start_time"]:
        st.session_state.pop(key, None)

# App Title
st.title("🛠️ Mod 10 Study Buddy")
st.markdown("Welcome! Please choose a study mode:")

# Menu
menu_option = st.radio(
    "Main Menu",
    (
        "📝 Start MCQ Practice Quiz",
        "🧠 Essay Questions Review",
        "📊 View My Results",
        "📚 Study Guide / References",
        "ℹ️ About This App",
        "🌐 Visit GCAA Website"
    ),
    index=None,
    key="menu_option"
)

# ====================== MCQ QUIZ ======================
if menu_option == "📝 Start MCQ Practice Quiz":
    try:
        df = pd.read_csv("module10_questions.csv")
    except Exception as e:
        st.error(f"❌ Could not load questions: {e}")
        st.stop()

    # ✅ Setup session state variables if not already present
    if "quiz_questions" not in st.session_state:
        st.session_state.quiz_questions = df.sample(n=min(20, len(df)), replace=False).reset_index(drop=True)
        st.session_state.start_time = time.time()
        st.session_state.current_question = 0
        st.session_state.score = 0
        st.session_state.answers = []
        st.session_state.advance = False

    if "quiz_history" not in st.session_state:
        st.session_state.quiz_history = []

    if "quiz_logged" not in st.session_state:
        st.session_state.quiz_logged = False

    quiz_questions = st.session_state.quiz_questions
    elapsed = int(time.time() - st.session_state.start_time)
    remaining = max(0, 1200 - elapsed)
    min_left, sec_left = divmod(remaining, 60)

    st.markdown(f"⏳ **Time Remaining: {min_left:02d}:{sec_left:02d}**")
    st.markdown("<h4 style='color:red;'>Disclaimer: This app is for training purposes only. All information must be verified with official GCAA publications.</h4>", unsafe_allow_html=True)
    st.markdown("<h4 style='color:brown;'>🕒 Note: You have 20 minutes only to complete this MCQ exam</h4>", unsafe_allow_html=True)
    st.markdown("<h4 style='color:darkblue;'>✅ Pass Mark: You must score at least 75% (15 out of 20) to pass this exam</h4>", unsafe_allow_html=True)

    if remaining <= 0:
        st.warning("⏱️ Time is up! Showing your results.")
        st.session_state.current_question = len(quiz_questions)

    if st.session_state.current_question >= len(quiz_questions):
        st.success(f"🎉 You scored {st.session_state.score} out of {len(quiz_questions)}")
        st.markdown("### ❌ Questions you got wrong:")
        for idx, (q, your_ans, correct_ans, ref) in enumerate(st.session_state.answers):
            if your_ans != correct_ans:
                st.markdown(f"**Q{idx+1}: {q}**  \nYour answer: `{your_ans}`  \nCorrect answer: `{correct_ans}`  \nReference: `{ref}`")

        # ✅ Add result to quiz history (only once)
        from datetime import datetime
        if not st.session_state.quiz_logged:
            result = {
                "Date": datetime.now().strftime("%Y-%m-%d %H:%M"),
                "Score": f"{st.session_state.score} / {len(quiz_questions)}",
                "Status": "✅ Pass" if st.session_state.score >= 15 else "❌ Fail"
            }
            st.session_state.quiz_history.append(result)
            st.session_state.quiz_logged = True

        if st.button("🔁 Retry Quiz"):
            for key in ["quiz_questions", "current_question", "score", "answers", "advance", "start_time", "quiz_logged"]:
                st.session_state.pop(key, None)
            st.rerun()

        st.stop()

    if st.session_state.advance:
        st.session_state.advance = False
        st.rerun()

    q_index = st.session_state.current_question
    row = quiz_questions.iloc[q_index]
    st.markdown(f"### Q{q_index + 1}: {row['question']}")
    options = [row['option_a'], row['option_b'], row['option_c']]

    def handle_choice():
        choice = st.session_state[f"q_{q_index}"]
        correct_letter = row['correct_answer'].strip().lower()
        correct = row.get(f"option_{correct_letter}", "")
        if choice == correct:
            st.session_state.score += 1
        reference = row.get('reference', 'N/A')  # <-- safe access
        st.session_state.answers.append((row['question'], choice, correct, reference))
        st.session_state.current_question += 1
        st.session_state.advance = True

    st.radio("Choose one:", options, key=f"q_{q_index}", index=None, on_change=handle_choice)

# ====================== OTHER MENUS ======================
elif menu_option == "🧠 Essay Questions Review":
    essays = pd.read_csv("GCAA_Mod10_Essays_All_With_Titles.csv", encoding="latin1")

    # Session state setup
    if "essay_mode" not in st.session_state:
        st.session_state.essay_mode = "menu"
    if "selected_essay_index" not in st.session_state:
        st.session_state.selected_essay_index = None
    if "essay_step" not in st.session_state:
        st.session_state.essay_step = 1
    if "reviewed_essays" not in st.session_state:
        st.session_state.reviewed_essays = set()

    # === Essay Menu ===
    if st.session_state.essay_mode == "menu":
        st.subheader("📚 Essay Topics")
        st.markdown("Select a topic to view its essay:")

        for i, row in essays.iterrows():
            label = row['Title']
            if i in st.session_state.reviewed_essays:
                label = f"✅ {label}"
            if st.button(label, key=f"topic_{i}"):
                st.session_state.selected_essay_index = i
                st.session_state.essay_mode = "view"
                st.session_state.essay_step = 1
                st.rerun()

    # === Essay View (Step-by-step reveal) ===
    elif st.session_state.essay_mode == "view":
    idx = st.session_state.selected_essay_index
    row = essays.iloc[idx]

    st.markdown(f"### ✍️ {row['Question']}")
    st.markdown("#### ✏️ Version 1 (Student Draft Style)")
    st.markdown(row['Version_1'])

    if st.session_state.essay_step >= 2:
        st.markdown("---")
        st.markdown("#### ✏️ Version 2 (Mid-Level Answer)")
        st.markdown(row['Version_2'])

    if st.session_state.essay_step == 3:
        st.markdown("---")
        st.markdown("#### ✅ Version 3 (Full Answer with Reference)")
        st.markdown(row['Version_3'])

        if st.button("🔙 Return to Menu"):
            st.session_state.reviewed_essays.add(idx)
            st.session_state.essay_mode = "menu"
            st.session_state.selected_essay_index = None
            st.session_state.essay_step = 1
            st.rerun()

    elif st.session_state.essay_step == 2:
        if st.button("➡️ Continue to Version 3"):
            st.session_state.essay_step = 3
            st.rerun()

    elif st.session_state.essay_step == 1:
        if st.button("➡️ Continue to Version 2"):
            st.session_state.essay_step = 2
            st.rerun()

elif menu_option == "📊 View My Results":
    st.subheader("📊 My Quiz History")

    if not st.session_state.quiz_history:
        st.info("You haven’t taken any quizzes yet.")
    else:
        st.markdown("### 📝 Previous Attempts")
        st.table(st.session_state.quiz_history)

elif menu_option == "📚 Study Guide / References":
    st.subheader("📚 Study Guide & References")

    st.markdown("The following documents are provided to help you prepare for the GCAA Module 10 essay exam:")

    # ✅ Document 1
    with open("GCAA Module 10 Essay Exam guidance.docx", "rb") as f:
        st.download_button(
            label="📥 Download: GCAA Module 10 Essay Exam Guidance",
            data=f,
            file_name="GCAA Module 10 Essay Exam guidance.docx",
            mime="application/vnd.openxmlformats-officedocument.wordprocessingml.document"
        )
    st.markdown("**Summary of Key Guidance:**")
    st.markdown("""
    - Answer the question that was asked, not what you wish was asked.
    - Structure your essay like an engineer:
      - Introduction → Bullet point body → Conclusion
    - Always cite the regulation (e.g. CAR M.901, CAR 145.55)
    - Write like a certifying staff member, not a student.
    - Understand and explain — don’t just remember.
    """)

    # ✅ Document 2
    with open("Writing a GCAA Module 10 Essay.docx", "rb") as f:
        st.download_button(
            label="📥 Download: Writing a GCAA Module 10 Essay",
            data=f,
            file_name="Writing a GCAA Module 10 Essay.docx",
            mime="application/vnd.openxmlformats-officedocument.wordprocessingml.document"
        )
    st.markdown("**Summary of Writing Advice:**")
    st.markdown("""
    - You have **20 minutes total for 2 essays**.
    - Use your time:
      - 30s to understand the question
      - 1m to plan
      - 8m to write
      - 30s to check
    - Include:
      - What, Who, When, and under what **regulation**
    - Write clearly, use technical language, and avoid guessing
    """)

elif menu_option == "ℹ️ About This App":
    st.subheader("About")
    st.markdown("""
<h4 style='color:red;'>
⚠️ Important Notice: This tool is intended for training and self-study purposes only. 
It is not an official source of GCAA regulations, requirements, or policy. 
All users must refer to the latest official GCAA publications and regulatory documents 
for accurate and current information.
</h4>
""", unsafe_allow_html=True)

elif menu_option == "🌐 Visit GCAA Website":
    st.subheader("🌐 General Civil Aviation Authority (UAE)")
    st.markdown("""
    Visit the official GCAA website for up-to-date regulatory documents, safety publications, and contact information.
    
    👉 [Click here to open the GCAA Website](https://www.gcaa.gov.ae/en/pages/default.aspx)
    """, unsafe_allow_html=True)
