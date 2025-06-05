import streamlit as st
import pandas as pd
import time

import streamlit as st

# Set default state if not present
if "menu_option" not in st.session_state:
    st.session_state.menu_option = "mcq"  # default
if "quiz_history" not in st.session_state:
    st.session_state.quiz_history = []
if "essay_mode" not in st.session_state:
    st.session_state.essay_mode = "menu"
if "essay_step" not in st.session_state:
    st.session_state.essay_step = 1
if "reviewed_essays" not in st.session_state:
    st.session_state.reviewed_essays = set()

# ===== MAIN MENU =====
st.image("Studbud1.png", use_column_width=True)
st.markdown("<h1 style='text-align: center;'>Main Menu</h1>", unsafe_allow_html=True)

col1, col2 = st.columns(2)

with col1:
    if st.button("📝 MCQ"):
        st.session_state.menu_option = "mcq"
    if st.button("📊 View Results"):
        st.session_state.menu_option = "results"
    if st.button("ℹ️ Important Info"):
        st.session_state.menu_option = "info"

with col2:
    if st.button("✍️ Essay"):
        st.session_state.menu_option = "essay"
    if st.button("📚 Study Guide"):
        st.session_state.menu_option = "guide"
    if st.button("🌐 GCAA Website"):
        st.session_state.menu_option = "website"

st.markdown("---")

# ===== PAGE LOGIC BLOCKS =====

if st.session_state.menu_option == "mcq":
    st.subheader("📝 MCQ Practice Quiz")
    st.write("👉 Insert your MCQ logic here.")

elif st.session_state.menu_option == "results":
    st.subheader("📊 Your Previous Results")
    st.write("👉 Display past quiz scores or performance history.")

elif st.session_state.menu_option == "essay":
    st.subheader("✍️ Essay Questions")
    st.write("👉 Insert your essay step-by-step logic here.")

elif st.session_state.menu_option == "guide":
    st.subheader("📚 Study Guide")
    st.write("👉 Upload, display or embed your documents here.")

elif st.session_state.menu_option == "info":
    st.subheader("ℹ️ Important Information")
    st.write("👉 Use this section to share app usage tips, GCAA disclaimers, or exam format advice.")

elif st.session_state.menu_option == "website":
    st.subheader("🌐 GCAA Website")
    st.markdown("[Visit GCAA Website](https://www.gcaa.gov.ae)", unsafe_allow_html=True)

# ====================== MCQ QUIZ ======================
if st.session_state.menu_option == "📝 Start MCQ Practice Quiz":
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
elif st.session_state.menu_option == "🧠 Essay Questions Review":
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

    elif st.session_state.essay_mode == "view":
        idx = st.session_state.selected_essay_index
        row = essays.iloc[idx]

        st.markdown(f"### ✍️ {row['Question']}")
        st.markdown("#### ✏️ Version 1 (Write down main points first)")
        st.markdown(row['Version_1'])

        if st.session_state.essay_step >= 2:
            st.markdown("---")
            st.markdown("#### ✏️ Version 2 (Start to elaborate on each point)")
            st.markdown(row['Version_2'])

        if st.session_state.essay_step == 3:
            st.markdown("---")
            st.markdown("#### ✅ Version 3 (Full Answer with Reference)")
            st.markdown(row['Version_3'])

            st.markdown(f"📘 **Reference**: *{row['Reference']}*")  # ✅ Show reference here

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

elif st.session_state.menu_option == "📊 View My Results":
    st.subheader("📊 My Quiz History")

    if not st.session_state.quiz_history:
        st.info("You haven’t taken any quizzes yet.")
    else:
        st.markdown("### 📝 Previous Attempts")
        st.table(st.session_state.quiz_history)

elif st.session_state.menu_option == "📚 Study Guide / References":
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

elif st.session_state.menu_option == "ℹ️ Important Info":
    st.subheader("Important")
    st.markdown("""
<h4 style='color:red;'>
⚠️ Important Notice: This tool is intended for training and self-study purposes only. 
It is not an official source of GCAA regulations, requirements, or policy. 
All users must refer to the latest official GCAA publications and regulatory documents 
for accurate and current information.
</h4>
""", unsafe_allow_html=True)

elif st.session_state.menu_option == "🌐 Visit GCAA Website":
    st.subheader("🌐 General Civil Aviation Authority (UAE)")
    st.markdown("""
    Visit the official GCAA website for up-to-date regulatory documents, safety publications, and contact information.
    
    👉 [Click here to open the GCAA Website](https://www.gcaa.gov.ae/en/pages/default.aspx)
    """, unsafe_allow_html=True)
