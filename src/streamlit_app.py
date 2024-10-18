import streamlit as st
import json
import os


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
            exams.append(filename[:-5])  # Remove .json extension
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
    if "score" not in st.session_state:
        st.session_state.score = 0
    if "total_questions" not in st.session_state:
        st.session_state.total_questions = 0
    if "submitted" not in st.session_state:
        st.session_state.submitted = False
    if "user_answers" not in st.session_state:
        st.session_state.user_answers = []
    if "attempts" not in st.session_state:
        st.session_state.attempts = 0
    if "answered" not in st.session_state:
        st.session_state.answered = False
    if "quiz_started" not in st.session_state:
        st.session_state.quiz_started = False


def calculate_percentage(score, total):
    return (score / total) * 100 if total > 0 else 0


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
            selected_exam = st.selectbox("Choose an exam", st.session_state.exams)

            if st.button("Start Quiz"):
                st.session_state.selected_exam = selected_exam
                st.session_state.questions = load_questions(
                    st.session_state.selected_vendor, selected_exam
                )
                st.session_state.total_questions = len(st.session_state.questions)
                st.session_state.quiz_started = True
                st.rerun()

    if st.session_state.quiz_started:
        st.sidebar.header("Score Tracker")
        percentage = calculate_percentage(
            st.session_state.score, st.session_state.attempts
        )
        st.sidebar.write(
            f"Current Score: {st.session_state.score}/{st.session_state.attempts}"
        )
        st.sidebar.write(f"Percentage: {percentage:.2f}%")
        if st.session_state.attempts > 0:
            st.sidebar.progress(st.session_state.score / st.session_state.attempts)
        else:
            st.sidebar.progress(0)

        if st.sidebar.button("End Quiz Early"):
            st.session_state.current_question = st.session_state.total_questions
            st.rerun()

        if st.session_state.current_question < st.session_state.total_questions:
            question = st.session_state.questions[st.session_state.current_question]

            st.write(
                f"Question {st.session_state.current_question + 1} of {st.session_state.total_questions}"
            )
            st.write(question["question"])

            st.session_state.user_answers = []
            for i, choice in enumerate(question["choices"]):
                if st.checkbox(
                    choice, key=f"q{st.session_state.current_question}_choice{i}"
                ):
                    st.session_state.user_answers.append(chr(65 + i))

            if st.button("Submit Answer"):
                if not st.session_state.answered:
                    st.session_state.submitted = True
                    st.session_state.attempts += 1
                    st.session_state.answered = True
                    st.rerun()

            if st.session_state.submitted:
                correct_set = set(question["correct_answers"])
                user_set = set(st.session_state.user_answers)

                if user_set == correct_set:
                    st.success("Correct!")
                    if st.session_state.answered:
                        st.session_state.score += 1
                        st.session_state.answered = False
                else:
                    st.error(
                        f"Wrong! Correct answer(s): {', '.join(question['correct_answers'])}"
                    )

                st.write("Your answer(s): " + ", ".join(st.session_state.user_answers))

                if st.button("Next Question"):
                    st.session_state.current_question += 1
                    st.session_state.submitted = False
                    st.session_state.user_answers = []
                    st.session_state.answered = False
                    st.rerun()

        else:
            st.write("Quiz completed!")
            final_percentage = calculate_percentage(
                st.session_state.score, st.session_state.attempts
            )
            st.write(
                f"Your final score: {st.session_state.score} out of {st.session_state.attempts}"
            )
            st.write(f"Final Percentage: {final_percentage:.2f}%")

            col1, col2 = st.columns(2)
            with col1:
                if st.button("Restart Quiz"):
                    st.session_state.current_question = 0
                    st.session_state.score = 0
                    st.session_state.submitted = False
                    st.session_state.user_answers = []
                    st.session_state.attempts = 0
                    st.session_state.answered = False
                    st.rerun()
            with col2:
                if st.button("Choose Different Vendor/Exam"):
                    st.session_state.quiz_started = False
                    st.session_state.selected_vendor = None
                    st.session_state.selected_exam = None
                    st.rerun()


if __name__ == "__main__":
    run_quiz()
