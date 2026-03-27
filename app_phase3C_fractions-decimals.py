import streamlit as st
import random
from fractions import Fraction

st.title("Math for the Trades - Practice Tutor")


# -----------------------------
# Vertical formatting helpers
# -----------------------------
def format_vertical(a, b, operation, answer=None):
    a_str = str(a)
    b_str = str(b)
    width = max(len(a_str), len(b_str)) + 2

    top = a_str.rjust(width)
    middle = f"{operation} {b_str.rjust(width - 2)}"
    line = "-" * width

    if answer is not None:
        bottom = str(answer).rjust(width)
        return f"{top}\n{middle}\n{line}\n{bottom}"

    return f"{top}\n{middle}\n{line}"


def format_decimal_vertical(a, b, operation, answer=None):
    a_str = f"{a:.2f}"
    b_str = f"{b:.2f}"
    width = max(len(a_str), len(b_str)) + 2

    top = a_str.rjust(width)
    middle = f"{operation} {b_str.rjust(width - 2)}"
    line = "-" * width

    if answer is not None:
        bottom = f"{answer:.2f}".rjust(width)
        return f"{top}\n{middle}\n{line}\n{bottom}"

    return f"{top}\n{middle}\n{line}"


def format_fraction_vertical(a, b, operation, result=None):
    width = max(len(str(a)), len(str(b))) + 4

    line1 = str(a).rjust(width)
    line2 = f"{operation} {str(b)}".rjust(width)
    divider = "-" * width

    if result:
        line3 = str(result).rjust(width)
        return f"{line1}\n{line2}\n{divider}\n{line3}"

    return f"{line1}\n{line2}\n{divider}"


# -----------------------------
# Hint Builder
# -----------------------------
def build_hint(problem_type, operation, a=None, b=None):
    if problem_type == "fraction":
        if a and b and a.denominator == b.denominator:
            return "Hint: The denominators are the same. Add or subtract the numerators only."
        return "Hint: Multiply the denominators to get a common denominator, then rewrite each fraction."

    if problem_type == "decimal":
        return "Hint: Line up the decimal points first."

    return "Hint: Line up the numbers and solve carefully."


# -----------------------------
# Step Builders
# -----------------------------
def build_whole_steps(a, b, operation):
    result = a + b if operation == "+" else a - b

    return [
        ("text", f"Problem: {a} {operation} {b}"),
        ("text", "Step 1: Line up the whole numbers vertically."),
        ("work", format_vertical(a, b, operation)),
        ("text", f"Step 2: {'Add' if operation == '+' else 'Subtract'} the numbers."),
        ("work", format_vertical(a, b, operation, result)),
        ("text", f"Final Answer: {result}")
    ]


def build_fraction_steps(a, b, operation):
    steps = []
    steps.append(("text", f"Problem: {a} {operation} {b}"))

    d1, d2 = a.denominator, b.denominator

    if d1 == d2:
        result_num = a.numerator + b.numerator if operation == "+" else a.numerator - b.numerator
        result = Fraction(result_num, d1)

        steps.append(("text", f"Step 1: Denominators are the same ({d1})."))
        steps.append(("text", "Step 2: Work with the numerators only."))

        steps.append(("work", format_fraction_vertical(a, b, operation)))

        steps.append(("text", f"{a.numerator} {'+' if operation=='+' else '-'} {b.numerator} = {result_num}"))
        steps.append(("text", f"Keep denominator: {d1}"))
        steps.append(("text", f"Final Answer: {result}"))

    else:
        common_den = d1 * d2

        new_a_num = a.numerator * d2
        new_b_num = b.numerator * d1
        result_num = new_a_num + new_b_num if operation == "+" else new_a_num - new_b_num
        result = Fraction(result_num, common_den)

        steps.append(("text", "Step 1: Multiply denominators to find a common denominator."))
        steps.append(("text", f"{d1} × {d2} = {common_den}"))

        steps.append(("text", "Step 2: Rewrite fractions."))
        steps.append(("text", f"{a} → {new_a_num}/{common_den}"))
        steps.append(("text", f"{b} → {new_b_num}/{common_den}"))

        steps.append(("work", format_fraction_vertical(f"{new_a_num}/{common_den}", f"{new_b_num}/{common_den}", operation)))

        steps.append(("text", f"{new_a_num} {'+' if operation=='+' else '-'} {new_b_num} = {result_num}"))
        steps.append(("text", f"Final Answer: {result}"))

    return steps


def build_decimal_steps(a, b, operation):
    result = round(a + b, 2) if operation == "+" else round(a - b, 2)

    return [
        ("text", f"Problem: {a:.2f} {operation} {b:.2f}"),
        ("text", "Step 1: Line up decimal points."),
        ("work", format_decimal_vertical(a, b, operation)),
        ("text", "Step 2: Solve."),
        ("work", format_decimal_vertical(a, b, operation, result)),
        ("text", f"Final Answer: {result:.2f}")
    ]


# -----------------------------
# Problem Generator
# -----------------------------
def generate_problem():
    problem_type = random.choice(["whole", "fraction", "decimal"])

    if problem_type == "whole":
        a, b = random.randint(1, 20), random.randint(1, 20)
        op = random.choice(["+", "-"])
        if op == "-" and a < b:
            a, b = b, a
        return f"{a} {op} {b}", a+b if op=="+" else a-b, "whole", build_whole_steps(a,b,op), build_hint("whole",op,a,b)

    elif problem_type == "fraction":
        a = Fraction(random.randint(1,4), random.randint(2,6))
        b = Fraction(random.randint(1,4), random.randint(2,6))
        op = random.choice(["+", "-"])
        if op == "-" and a < b:
            a, b = b, a
        return f"{a} {op} {b}", a+b if op=="+" else a-b, "fraction", build_fraction_steps(a,b,op), build_hint("fraction",op,a,b)

    else:
        a, b = round(random.uniform(0.1,9.9),2), round(random.uniform(0.1,9.9),2)
        op = random.choice(["+", "-"])
        if op == "-" and a < b:
            a, b = b, a
        return f"{a:.2f} {op} {b:.2f}", round(a+b,2) if op=="+" else round(a-b,2), "decimal", build_decimal_steps(a,b,op), build_hint("decimal",op,a,b)


# -----------------------------
# Session State
# -----------------------------
if "question" not in st.session_state:
    q,a,t,s,h = generate_problem()
    st.session_state.update({"question":q,"answer":a,"type":t,"steps":s,"hint":h,"attempts":0,"feedback":None,"show_steps":False})


# -----------------------------
# UI
# -----------------------------
st.subheader("Solve this problem:")
st.write(f"### {st.session_state.question}")

user_input = st.text_input("Enter your answer:")

if st.button("Check Answer"):
    st.session_state.attempts += 1
    st.session_state.show_steps = False

    try:
        if st.session_state.type == "fraction":
            correct = Fraction(user_input) == st.session_state.answer
        elif st.session_state.type == "decimal":
            correct = abs(float(user_input) - st.session_state.answer) < 0.01
        else:
            correct = int(user_input) == st.session_state.answer

        if correct:
            st.session_state.feedback = "correct"
            st.session_state.show_steps = True
        else:
            st.session_state.feedback = "hint" if st.session_state.attempts == 1 else "incorrect"
            st.session_state.show_steps = st.session_state.attempts > 1

    except:
        st.session_state.feedback = "invalid"


# -----------------------------
# Feedback
# -----------------------------
if st.session_state.feedback == "correct":
    st.success("✅ Correct! Great job!")

elif st.session_state.feedback == "hint":
    st.warning("Try again.")
    st.info(st.session_state.hint)

elif st.session_state.feedback == "incorrect":
    st.error("❌ Let's go through it step-by-step.")

elif st.session_state.feedback == "invalid":
    st.error("⚠️ Please enter a valid answer.")


st.write(f"Attempts: {st.session_state.attempts}")


# -----------------------------
# Steps (FIXED)
# -----------------------------
if st.session_state.show_steps:
    st.subheader("Step-by-Step")

    for step_type, content in st.session_state.steps:
        if step_type == "text":
            st.write(content)
        elif step_type == "work":
            st.code(content, language="text")


# -----------------------------
# New Problem
# -----------------------------
if st.button("New Problem"):
    q,a,t,s,h = generate_problem()
    st.session_state.update({"question":q,"answer":a,"type":t,"steps":s,"hint":h,"attempts":0,"feedback":None,"show_steps":False})
    st.rerun()