import random
from decimal import Decimal, InvalidOperation, ROUND_HALF_UP

import streamlit as st

# ============================================================
# PAGE CONFIG
# ============================================================
st.set_page_config(
    page_title="Math for the Trades - Practice Tutor",
    page_icon="📘",
    layout="centered"
)

# ============================================================
# DISPLAY HELPERS
# ============================================================
def format_decimal_fixed(value, places):
    """
    Format a number to a fixed number of decimal places for display.
    """
    return f"{value:.{places}f}"


def decimal_to_string(value):
    """
    Convert Decimal to a clean string without scientific notation.
    """
    value_str = format(value, "f")
    if "." in value_str:
        value_str = value_str.rstrip("0").rstrip(".")
    return value_str


def safe_decimal_from_string(text):
    """
    Safely convert learner input into Decimal.
    Accepts:
    .5
    0.5
    4
    4.217
    """
    cleaned = text.strip()
    if cleaned == "":
        return None
    try:
        return Decimal(cleaned)
    except InvalidOperation:
        return None


# ============================================================
# PROBLEM GENERATION
# ============================================================
def get_range(level):
    if level == 1:
        return (0.1, 3.9)
    if level == 2:
        return (0.1, 6.9)
    return (0.1, 9.9)


def generate_problem(level=1):
    """
    Generate decimal multiplication problems where the displayed values
    exactly match the values used in the calculation.
    """
    low, high = get_range(level)

    # Generate to thousandths so rounding to thousandths is meaningful.
    n1 = round(random.uniform(low, high), 3)
    n2 = round(random.uniform(low, high), 3)

    # Use the exact generated values in Decimal form.
    d1 = Decimal(f"{n1:.3f}")
    d2 = Decimal(f"{n2:.3f}")

    exact = d1 * d2

    return {
        "n1": d1,
        "n2": d2,
        "text": f"{format_decimal_fixed(float(d1), 3)} × {format_decimal_fixed(float(d2), 3)}",
        "exact": exact,
        "tenth": exact.quantize(Decimal("0.1"), rounding=ROUND_HALF_UP),
        "hundredth": exact.quantize(Decimal("0.01"), rounding=ROUND_HALF_UP),
        "thousandth": exact.quantize(Decimal("0.001"), rounding=ROUND_HALF_UP),
        "level": level
    }


# ============================================================
# SESSION STATE
# ============================================================
def init():
    if "level" not in st.session_state:
        st.session_state.level = 1

    if "problem" not in st.session_state:
        st.session_state.problem = generate_problem(st.session_state.level)

    if "answer" not in st.session_state:
        st.session_state.answer = ""

    if "feedback" not in st.session_state:
        st.session_state.feedback = ""

    if "feedback_type" not in st.session_state:
        st.session_state.feedback_type = ""

    if "checked" not in st.session_state:
        st.session_state.checked = False

    if "explanation" not in st.session_state:
        st.session_state.explanation = ""

    if "last_result" not in st.session_state:
        st.session_state.last_result = None

    if "rounding" not in st.session_state:
        st.session_state.rounding = "Nearest Hundredth"

    if "teacher" not in st.session_state:
        st.session_state.teacher = False

    if "thinking_1" not in st.session_state:
        st.session_state.thinking_1 = ""

    if "thinking_2" not in st.session_state:
        st.session_state.thinking_2 = ""

    if "thinking_3" not in st.session_state:
        st.session_state.thinking_3 = ""


def reset(level=None):
    if level is None:
        level = st.session_state.level

    st.session_state.problem = generate_problem(level)
    st.session_state.level = level
    st.session_state.answer = ""
    st.session_state.feedback = ""
    st.session_state.feedback_type = ""
    st.session_state.explanation = ""
    st.session_state.checked = False
    st.session_state.last_result = None


def clear_thinking():
    st.session_state.thinking_1 = ""
    st.session_state.thinking_2 = ""
    st.session_state.thinking_3 = ""


# ============================================================
# PLACE VALUE SUPPORT
# ============================================================
def get_place_info(rounding):
    if rounding == "Nearest Tenth":
        return {
            "target_place": "tenths",
            "target_plain": "the first number after the decimal point",
            "look_place": "hundredths",
            "look_plain": "the second number after the decimal point",
            "rounded_value_key": "tenth",
            "rounded_label": "Rounded to the nearest tenth"
        }

    if rounding == "Nearest Hundredth":
        return {
            "target_place": "hundredths",
            "target_plain": "the second number after the decimal point",
            "look_place": "thousandths",
            "look_plain": "the third number after the decimal point",
            "rounded_value_key": "hundredth",
            "rounded_label": "Rounded to the nearest hundredth"
        }

    if rounding == "Nearest Thousandth":
        return {
            "target_place": "thousandths",
            "target_plain": "the third number after the decimal point",
            "look_place": "ten-thousandths",
            "look_plain": "the fourth number after the decimal point",
            "rounded_value_key": "thousandth",
            "rounded_label": "Rounded to the nearest thousandth"
        }

    return None


# ============================================================
# EXPLANATION
# ============================================================
def explain(problem, rounding):
    exact = decimal_to_string(problem["exact"])

    if rounding == "Exact":
        return f"""
Exact product: **{exact}**

You selected **Exact**, so no rounding is needed.

- Write the full decimal product
- Do not change any digits
"""

    place_info = get_place_info(rounding)
    rounded_value = decimal_to_string(problem[place_info["rounded_value_key"]])

    return f"""
Exact product: **{exact}**

To round to the **nearest {place_info["target_place"]}**:

- Keep your eye on the **{place_info["target_place"]} place**
  👉 That is **{place_info["target_plain"]}**

- Then look at the **{place_info["look_place"]} place**
  👉 That is **{place_info["look_plain"]}**

- Use the digit in the **{place_info["look_place"]} place** to decide what to do

- If that digit is **5 or greater**, increase the digit in the **{place_info["target_place"]} place** by 1

- If that digit is **less than 5**, keep the digit in the **{place_info["target_place"]} place** the same

**{place_info["rounded_label"]}: {rounded_value}**
"""


# ============================================================
# ANSWER CHECKING
# ============================================================
def get_correct_answer(problem, rounding):
    if rounding == "Exact":
        return problem["exact"]
    if rounding == "Nearest Tenth":
        return problem["tenth"]
    if rounding == "Nearest Hundredth":
        return problem["hundredth"]
    return problem["thousandth"]


def check(answer_text):
    learner_value = safe_decimal_from_string(answer_text)

    if learner_value is None:
        return (
            "⚠️ Please enter a valid number.",
            "warning",
            "A valid decimal answer might look like **4.2**, **0.13**, **.13**, or **4.217**.",
            False
        )

    problem = st.session_state.problem
    correct = get_correct_answer(problem, st.session_state.rounding)
    explanation = explain(problem, st.session_state.rounding)

    if learner_value == correct:
        explanation += "\n\n**Why this is correct:** Your answer matches the required result."
        return "✅ Correct!", "success", explanation, True

    explanation += (
        f"\n\n**Your answer:** {decimal_to_string(learner_value)}"
        f"\n\n**Expected answer:** {decimal_to_string(correct)}"
        f"\n\n**Why this is not correct:** Check the place value word, then check how many places after the decimal point it represents."
    )

    return "❌ Not quite. Check the place value and rounding.", "error", explanation, False


# ============================================================
# SMART PRACTICE
# ============================================================
def next_level(current, correct):
    return min(current + 1, 3) if correct else current


# ============================================================
# INIT
# ============================================================
init()

# ============================================================
# UI HEADER
# ============================================================
st.title("📘 Guided AI Tutor")
st.subheader("Phase 4D: Decimals with Clear Place Value Explanations")

st.write(
    "This phase helps learners multiply decimals, use place-value vocabulary, "
    "round answers correctly, and practice with increasing precision."
)

# ============================================================
# SIDEBAR
# ============================================================
with st.sidebar:
    st.write("### Phase 4D")
    st.write("- Decimal multiplication")
    st.write("- Place value vocabulary")
    st.write("- Rounding to tenths")
    st.write("- Rounding to hundredths")
    st.write("- Rounding to thousandths")
    st.write("- Smart practice")

    st.checkbox("Show Teacher View", key="teacher")

    st.divider()
    st.write(f"**Current Difficulty Level:** {st.session_state.level}")

# ============================================================
# THINKING PROMPTS
# ============================================================
st.markdown("## Think Before Solving")

st.session_state.thinking_1 = st.text_area(
    "1. What is the problem asking you to find?",
    value=st.session_state.thinking_1,
    height=80
)

st.session_state.thinking_2 = st.text_area(
    "2. What information do you know?",
    value=st.session_state.thinking_2,
    height=80
)

st.session_state.thinking_3 = st.text_area(
    "3. What operation will you use?",
    value=st.session_state.thinking_3,
    height=80
)

st.divider()

# ============================================================
# PROBLEM
# ============================================================
st.markdown("## 🧮 Problem")
st.markdown(f"### **{st.session_state.problem['text']} = ?**")

# ============================================================
# ROUNDING SELECTION
# ============================================================
st.markdown("## 🎯 Rounding")

st.radio(
    "Choose how to give the answer:",
    ["Exact", "Nearest Tenth", "Nearest Hundredth", "Nearest Thousandth"],
    key="rounding"
)

# ============================================================
# ANSWER INPUT
# ============================================================
st.markdown("## ✏️ Your Answer")
st.session_state.answer = st.text_input(
    "Enter your answer:",
    value=st.session_state.answer
)

# ============================================================
# MAIN BUTTONS
# ============================================================
col1, col2 = st.columns(2)

with col1:
    if st.button("✅ Check Answer", use_container_width=True):
        feedback, feedback_type, explanation, correct = check(st.session_state.answer)
        st.session_state.feedback = feedback
        st.session_state.feedback_type = feedback_type
        st.session_state.explanation = explanation
        st.session_state.checked = True
        st.session_state.last_result = correct
        st.rerun()

with col2:
    if st.button("🔄 New Problem", use_container_width=True):
        reset()
        st.rerun()

# ============================================================
# FEEDBACK
# ============================================================
if st.session_state.checked:
    if st.session_state.feedback_type == "success":
        st.success(st.session_state.feedback)
    elif st.session_state.feedback_type == "warning":
        st.warning(st.session_state.feedback)
    else:
        st.error(st.session_state.feedback)

# ============================================================
# EXPLANATION
# ============================================================
if st.session_state.checked and st.session_state.explanation:
    st.markdown("## 📝 Explanation")
    st.markdown(st.session_state.explanation)

# ============================================================
# SMART PRACTICE
# ============================================================
if st.session_state.checked:
    new_level = next_level(st.session_state.level, st.session_state.last_result)

    st.markdown("## 🚀 Smart Practice")

    if st.session_state.last_result:
        st.info("Nice work. The next problem can be a little more challenging.")
        button_label = "⬆️ Try a Harder Problem"
    else:
        st.info("Let's practice with a similar problem at about the same difficulty.")
        button_label = "🔁 Try Similar Problem"

    if st.button(button_label, use_container_width=True):
        reset(new_level)
        st.rerun()

# ============================================================
# TOOLS
# ============================================================
st.markdown("## Tools")

tool1, tool2 = st.columns(2)

with tool1:
    if st.button("🧹 Clear Thinking Boxes", use_container_width=True):
        clear_thinking()
        st.rerun()

with tool2:
    if st.button("🧽 Clear Answer", use_container_width=True):
        st.session_state.answer = ""
        st.session_state.feedback = ""
        st.session_state.feedback_type = ""
        st.session_state.explanation = ""
        st.session_state.checked = False
        st.session_state.last_result = None
        st.rerun()

# ============================================================
# TEACHER VIEW
# ============================================================
if st.session_state.teacher:
    st.divider()
    st.markdown("## 👩‍🏫 Teacher View")
    p = st.session_state.problem
    st.write("**Problem:**", p["text"])
    st.write("**First Number:**", decimal_to_string(p["n1"]))
    st.write("**Second Number:**", decimal_to_string(p["n2"]))
    st.write("**Exact:**", decimal_to_string(p["exact"]))
    st.write("**Nearest Tenth:**", decimal_to_string(p["tenth"]))
    st.write("**Nearest Hundredth:**", decimal_to_string(p["hundredth"]))
    st.write("**Nearest Thousandth:**", decimal_to_string(p["thousandth"]))
    st.write("**Difficulty Level:**", p["level"])
    st.write("**Selected Rounding Mode:**", st.session_state.rounding)

# ============================================================
# FOOTER
# ============================================================
st.divider()
st.caption(
    "Phase 4D complete: learners now practice decimal multiplication with place-value vocabulary, "
    "rounding through thousandths, and smart practice support."
)