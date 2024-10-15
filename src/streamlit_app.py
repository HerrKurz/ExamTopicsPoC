import streamlit as st
import json


def load_questions():
    with open("./questions/aws.json", "r") as file:
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


if "current_question" not in st.session_state:
    st.session_state.questions = load_questions()
    st.session_state.current_question = 0
    st.session_state.score = 0
    st.session_state.total_questions = len(st.session_state.questions)
    st.session_state.submitted = False
    st.session_state.user_answers = []
    st.session_state.attempts = 0
    st.session_state.answered = False


def run_quiz():
    st.title("AWS Data Engineer Associate Quiz")

    st.sidebar.header("Score Tracker")
    st.sidebar.write(
        f"Current Score: {st.session_state.score}/{st.session_state.attempts}"
    )
    if st.session_state.attempts > 0:
        st.sidebar.progress(st.session_state.score / st.session_state.attempts)
    else:
        st.sidebar.progress(0)

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
        st.write(
            f"Your final score: {st.session_state.score} out of {st.session_state.total_questions}"
        )

        if st.button("Restart Quiz"):
            st.session_state.current_question = 0
            st.session_state.score = 0
            st.session_state.submitted = False
            st.session_state.user_answers = []
            st.session_state.attempts = 0
            st.session_state.answered = False
            st.rerun()


if __name__ == "__main__":
    run_quiz()
