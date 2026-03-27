import streamlit as st
import random
from fractions import Fraction
from decimal import Decimal, ROUND_HALF_UP

st.set_page_config(page_title="Math for the Trades - Practice Tutor", layout="centered")

st.title("Math for the Trades - Practice Tutor")

# -----------------------------
# Rounding choices
# -----------------------------
ROUNDING_OPTIONS = {
    "Nearest Tenth": {
        "places": 1,
        "quantize": "0.1",
        "label": "nearest tenth",
    },
    "Nearest Hundredth": {
        "places": 2,
        "quantize": "0.01",
        "label": "nearest hundredth",
    },
    "Nearest Thousandth": {
        "places": 3,
        "quantize": "0.001",
        "label": "nearest thousandth",
    },
}


# -----------------------------
# Helpers
# -----------------------------
def simplify_fraction(numerator, denominator):
    frac = Fraction(numerator, denominator)
    return frac.numerator, frac.denominator


def random_fraction():
    numerator = random.randint(1, 9)
    denominator = random.randint(2, 9)
    return numerator, denominator


def random_decimal():
    return round(random.uniform(0.2, 9.9), 2)


def school_round(value, quantize_str):
    return float(
        Decimal(str(value)).quantize(
            Decimal(quantize_str),
            rounding=ROUND_HALF_UP,
        )
    )


def render_fraction(n, d):
    st.latex(rf"\frac{{{n}}}{{{d}}}")


def render_fraction_operation(n1, d1, n2, d2, operation):
    if operation == "×":
        symbol = r"\times"
    elif operation == "÷":
        symbol = r"\div"
    else:
        symbol = operation

    st.latex(rf"\frac{{{n1}}}{{{d1}}} {symbol} \frac{{{n2}}}{{{d2}}}")


def format_decimal_for_display(value, places):
    return f"{value:.{places}f}"


# -----------------------------
# Session State
# -----------------------------
if "problem_type" not in st.session_state:
    st.session_state.problem_type = "Fraction to Decimal"

if "current_problem" not in st.session_state:
    st.session_state.current_problem = None

if "show_help" not in st.session_state:
    st.session_state.show_help = False

if "answer_checked" not in st.session_state:
    st.session_state.answer_checked = False

if "answer_feedback" not in st.session_state:
    st.session_state.answer_feedback = ""

if "student_num" not in st.session_state:
    st.session_state.student_num = ""

if "student_den" not in st.session_state:
    st.session_state.student_den = ""

if "student_decimal" not in st.session_state:
    st.session_state.student_decimal = ""

if "extra_hint" not in st.session_state:
    st.session_state.extra_hint = ""

if "rounding_choice" not in st.session_state:
    st.session_state.rounding_choice = "Nearest Hundredth"

if "show_rounding_help" not in st.session_state:
    st.session_state.show_rounding_help = False


# -----------------------------
# Problem Generator
# -----------------------------
def generate_problem(problem_type, quantize_str):
    if problem_type == "Mixed Practice":
        problem_type = random.choice(
            [
                "Fraction to Decimal",
                "Decimal to Fraction",
                "Multiply Fractions",
                "Divide Fractions",
                "Multiply Decimals",
                "Divide Decimals",
            ]
        )

    if problem_type == "Fraction to Decimal":
        n, d = random_fraction()
        raw_answer = n / d
        return {
            "type": problem_type,
            "n": n,
            "d": d,
            "raw_answer": raw_answer,
            "answer": school_round(raw_answer, quantize_str),
        }

    elif problem_type == "Decimal to Fraction":
        dec = random.choice([0.25, 0.5, 0.75, 1.2, 1.5, 2.5, 3.75])
        frac = Fraction(str(dec)).limit_denominator()
        return {
            "type": problem_type,
            "decimal": dec,
            "num": frac.numerator,
            "den": frac.denominator,
        }

    elif problem_type == "Multiply Fractions":
        n1, d1 = random_fraction()
        n2, d2 = random_fraction()
        num = n1 * n2
        den = d1 * d2
        simp_num, simp_den = simplify_fraction(num, den)
        return {
            "type": problem_type,
            "n1": n1,
            "d1": d1,
            "n2": n2,
            "d2": d2,
            "num": num,
            "den": den,
            "simp_num": simp_num,
            "simp_den": simp_den,
        }

    elif problem_type == "Divide Fractions":
        n1, d1 = random_fraction()
        n2, d2 = random_fraction()
        num = n1 * d2
        den = d1 * n2
        simp_num, simp_den = simplify_fraction(num, den)
        return {
            "type": problem_type,
            "n1": n1,
            "d1": d1,
            "n2": n2,
            "d2": d2,
            "num": num,
            "den": den,
            "simp_num": simp_num,
            "simp_den": simp_den,
        }

    elif problem_type == "Multiply Decimals":
        a = random_decimal()
        b = random_decimal()
        raw_answer = a * b
        return {
            "type": problem_type,
            "a": a,
            "b": b,
            "raw_answer": raw_answer,
            "answer": school_round(raw_answer, quantize_str),
        }

    elif problem_type == "Divide Decimals":
        b = random.choice([0.2, 0.4, 0.5, 1.25, 2.5])
        raw_answer = round(random.uniform(1, 12), 4)
        a = round(b * raw_answer, 4)
        actual = a / b
        return {
            "type": problem_type,
            "a": a,
            "b": b,
            "raw_answer": actual,
            "answer": school_round(actual, quantize_str),
        }


def reset_attempt_fields():
    st.session_state.show_help = False
    st.session_state.answer_checked = False
    st.session_state.answer_feedback = ""
    st.session_state.student_num = ""
    st.session_state.student_den = ""
    st.session_state.student_decimal = ""
    st.session_state.extra_hint = ""
    st.session_state.show_rounding_help = False


# -----------------------------
# Sidebar
# -----------------------------
st.sidebar.header("Choose a Skill")

problem_type = st.sidebar.selectbox(
    "Problem Type",
    [
        "Fraction to Decimal",
        "Decimal to Fraction",
        "Multiply Fractions",
        "Divide Fractions",
        "Multiply Decimals",
        "Divide Decimals",
        "Mixed Practice",
    ],
)

rounding_choice = st.sidebar.selectbox(
    "Decimal Rounding",
    list(ROUNDING_OPTIONS.keys()),
    index=list(ROUNDING_OPTIONS.keys()).index(st.session_state.rounding_choice),
)

if st.session_state.rounding_choice != rounding_choice:
    st.session_state.rounding_choice = rounding_choice
    st.session_state.current_problem = None
    reset_attempt_fields()

round