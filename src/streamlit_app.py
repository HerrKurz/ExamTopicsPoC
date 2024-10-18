import streamlit as st
import json
import os


def format_exam_name(filename):
    name = filename[:-5] if filename.endswith(".json") else filename
    return " ".join(word.capitalize() for word in name.split("_"))


def load_vendors():
    return [
        d
        for d in os.listdir("./questions")
        if os.path.isdir(os.path.join("./questions", d))
    ]


def load_exams(vendor):
    exams = []
    vendor_dir = os.path.join("./questions", vendor)
    for filename in os.listdir(vendor_dir):
        if filename.endswith(".json"):
            exam_name = filename[:-5]
            formatted_name = format_exam_name(exam_name)
            exams.append({"file": exam_name, "display": formatted_name})
    return exams


def load_questions(vendor, exam_name):
    with open(f"./questions/{vendor}/{exam_name}.json", "r") as file:
        data = json.load(file)

    questions = []
    for item in data:
        question_text = item.get("question")
        choices = item.get("choices", [])
        user_data = item.get("user_data", [])
        if user_data:
            most_voted = max(user_data, key=lambda x: x.get("vote_count", 0))
            correct_answers = list(most_voted.get("voted_answers", ""))
        else:
            correct_answers = []

        if question_text and choices:
            questions.append(
                {
                    "question": question_text,
                    "choices": choices,
                    "correct_answers": correct_answers,
                }
            )

    return questions


def initialize_session_state():
    if "vendors" not in st.session_state:
        st.session_state.vendors = load_vendors()
    if "selected_vendor" not in st.session_state:
        st.session_state.selected_vendor = None
    if "exams" not in st.session_state:
        st.session_state.exams = []
    if "selected_exam" not in st.session_state:
        st.session_state.selected_exam = None
    if "questions" not in st.session_state:
        st.session_state.questions = []
    if "current_question" not in st.session_state:
        st.session_state.current_question = 0
    if "total_questions" not in st.session_state:
        st.session_state.total_questions = 0
    if "user_answers" not in st.session_state:
        st.session_state.user_answers = {}
    if "correct_answers" not in st.session_state:
        st.session_state.correct_answers = set()
    if "quiz_started" not in st.session_state:
        st.session_state.quiz_started = False
    if "quiz_completed" not in st.session_state:
        st.session_state.quiz_completed = False


def calculate_score():
    return len(st.session_state.correct_answers)


def run_quiz():
    st.title("Exam Quiz App")

    initialize_session_state()

    if not st.session_state.quiz_started:
        st.write("Select a vendor and exam to start the quiz:")

        selected_vendor = st.selectbox("Choose a vendor", st.session_state.vendors)

        if selected_vendor != st.session_state.selected_vendor:
            st.session_state.selected_vendor = selected_vendor
            st.session_state.exams = load_exams(selected_vendor)
            st.session_state.selected_exam = None

        if st.session_state.selected_vendor:
            exam_options = {
                exam["display"]: exam["file"] for exam in st.session_state.exams
            }
            selected_exam_display = st.selectbox(
                "Choose an exam", list(exam_options.keys())
            )
            selected_exam_file = exam_options[selected_exam_display]

            if st.button("Start Quiz"):
                st.session_state.selected_exam = selected_exam_file
                st.session_state.questions = load_questions(
                    st.session_state.selected_vendor, selected_exam_file
                )
                st.session_state.total_questions = len(st.session_state.questions)
                st.session_state.quiz_started = True
                st.session_state.user_answers = {}
                st.session_state.correct_answers = set()
                st.rerun()

    if st.session_state.quiz_started and not st.session_state.quiz_completed:
        quiz_title = f"{st.session_state.selected_vendor} - {format_exam_name(st.session_state.selected_exam)} Quiz"
        st.title(quiz_title)

        st.sidebar.header("Progress")
        progress = (
            len(st.session_state.correct_answers) / st.session_state.total_questions
        )
        st.sidebar.progress(progress)
        st.sidebar.write(
            f"Correct Answers: {len(st.session_state.correct_answers)} / {st.session_state.total_questions}"
        )

        question = st.session_state.questions[st.session_state.current_question]
        st.markdown(
            f"<h2>Question {st.session_state.current_question + 1} of {st.session_state.total_questions}</h2>",
            unsafe_allow_html=True,
        )
        st.write(question["question"])

        user_answer = st.session_state.user_answers.get(
            st.session_state.current_question, []
        )
        for i, choice in enumerate(question["choices"]):
            if st.checkbox(
                choice,
                key=f"q{st.session_state.current_question}_choice{i}",
                value=chr(65 + i) in user_answer,
            ):
                if chr(65 + i) not in user_answer:
                    user_answer.append(chr(65 + i))
            elif chr(65 + i) in user_answer:
                user_answer.remove(chr(65 + i))
        st.session_state.user_answers[st.session_state.current_question] = user_answer

        if st.button("Submit Answer"):
            if set(user_answer) == set(question["correct_answers"]):
                st.success("Correct!")
                st.session_state.correct_answers.add(st.session_state.current_question)
            else:
                st.error(
                    f"Incorrect. The correct answer(s) are: {', '.join(question['correct_answers'])}"
                )

        col1, col2, col3, col4 = st.columns(4)
        with col1:
            if st.button("⏪ First"):
                st.session_state.current_question = 0
                st.rerun()
        with col2:
            if st.button("◀️ Previous") and st.session_state.current_question > 0:
                st.session_state.current_question -= 1
                st.rerun()
        with col3:
            if (
                st.button("Next ▶️")
                and st.session_state.current_question
                < st.session_state.total_questions - 1
            ):
                st.session_state.current_question += 1
                st.rerun()
        with col4:
            if st.button("Last ⏩"):
                st.session_state.current_question = st.session_state.total_questions - 1
                st.rerun()

        new_question = st.number_input(
            "Go to question",
            min_value=1,
            max_value=st.session_state.total_questions,
            value=st.session_state.current_question + 1,
        )
        if new_question != st.session_state.current_question + 1:
            st.session_state.current_question = new_question - 1
            st.rerun()

        # Finish quiz button with warning
        if st.button("End Quiz Early"):
            if st.session_state.current_question < st.session_state.total_questions - 1:
                if st.warning(
                    "Are you sure you want to end the quiz early? You haven't answered all questions."
                ):
                    st.session_state.quiz_completed = True
                    st.rerun()
            else:
                st.session_state.quiz_completed = True
                st.rerun()

    if st.session_state.quiz_completed:
        st.write("Quiz completed!")
        final_score = calculate_score()
        final_percentage = (final_score / st.session_state.total_questions) * 100
        st.write(
            f"Your final score: {final_score} out of {st.session_state.total_questions}"
        )
        st.write(f"Final Percentage: {final_percentage:.2f}%")

        if st.button("Review Answers"):
            for i, question in enumerate(st.session_state.questions):
                st.write(f"Question {i + 1}: {question['question']}")
                user_answer = st.session_state.user_answers.get(i, [])
                st.write(f"Your answer: {', '.join(user_answer)}")
                st.write(f"Correct answer: {', '.join(question['correct_answers'])}")
                if i in st.session_state.correct_answers:
                    st.success("Correct")
                else:
                    st.error("Incorrect")
                st.write("---")

        if st.button("Start New Quiz"):
            for key in list(st.session_state.keys()):
                del st.session_state[key]
            st.rerun()


if __name__ == "__main__":
    run_quiz()
