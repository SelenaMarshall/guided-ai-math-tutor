import random
import re
from fractions import Fraction
from decimal import Decimal, ROUND_HALF_UP

import streamlit as st
from transformers import pipeline


# =========================
# PAGE SETUP
# =========================
st.set_page_config(
    page_title="Guided AI Math Tutor",
    page_icon="📘",
    layout="wide"
)


# =========================
# SESSION STATE
# =========================
if "problem_data" not in st.session_state:
    st.session_state.problem_data = None

if "problem_counter" not in st.session_state:
    st.session_state.problem_counter = 0

if "hint_level" not in st.session_state:
    st.session_state.hint_level = 0

if "strategy_revealed" not in st.session_state:
    st.session_state.strategy_revealed = False

if "wrong_attempts" not in st.session_state:
    st.session_state.wrong_attempts = 0

if "selected_palette" not in st.session_state:
    st.session_state.selected_palette = "Soft Sky"

if "selected_trade" not in st.session_state:
    st.session_state.selected_trade = "Electrician"

if "correct_count" not in st.session_state:
    st.session_state.correct_count = 0

if "attempted_count" not in st.session_state:
    st.session_state.attempted_count = 0

if "streak_count" not in st.session_state:
    st.session_state.streak_count = 0

if "level_points" not in st.session_state:
    st.session_state.level_points = 0

if "answer_revealed_this_round" not in st.session_state:
    st.session_state.answer_revealed_this_round = False


# =========================
# COLOR PALETTES
# =========================
PALETTES = {
    "Midnight Teal": {
        "section_title": "#d7fffb",
        "section_subtle": "#dbeafe",
        "step_bg": "rgba(45, 98, 112, 0.22)",
        "step_border": "rgba(91, 192, 190, 0.45)",
        "helper_bg": "rgba(31, 41, 55, 0.42)",
        "helper_border": "rgba(148, 163, 184, 0.28)",
        "feedback_bg": "rgba(120, 53, 15, 0.18)",
        "feedback_border": "rgba(251, 191, 36, 0.35)",
        "ai_bg": "rgba(15, 76, 92, 0.20)",
        "ai_border": "rgba(94, 234, 212, 0.30)",
        "round_bg": "rgba(20, 83, 45, 0.20)",
        "round_border": "rgba(74, 222, 128, 0.35)",
        "round_title": "#bbf7d0",
        "round_text": "#ecfdf5",
        "visual_bg": "rgba(8, 47, 73, 0.24)",
        "visual_border": "rgba(125, 211, 252, 0.35)",
        "visual_title": "#bae6fd",
        "visual_text": "#f0f9ff",
        "trade_bg": "linear-gradient(135deg, #0f172a, #134e4a)",
        "trade_border": "#5eead4",
        "trade_title": "#99f6e4",
        "trade_text": "#ecfeff",
        "celebrate_bg": "rgba(20, 83, 45, 0.25)",
        "celebrate_border": "rgba(74, 222, 128, 0.40)",
        "progress_bg": "rgba(15, 23, 42, 0.35)",
        "progress_border": "rgba(45, 212, 191, 0.28)",
        "progress_text": "#ecfeff"
    },
    "Deep Plum": {
        "section_title": "#f3e8ff",
        "section_subtle": "#ede9fe",
        "step_bg": "rgba(88, 28, 135, 0.20)",
        "step_border": "rgba(196, 181, 253, 0.35)",
        "helper_bg": "rgba(55, 48, 163, 0.20)",
        "helper_border": "rgba(165, 180, 252, 0.28)",
        "feedback_bg": "rgba(127, 29, 29, 0.18)",
        "feedback_border": "rgba(252, 165, 165, 0.35)",
        "ai_bg": "rgba(76, 29, 149, 0.20)",
        "ai_border": "rgba(216, 180, 254, 0.35)",
        "round_bg": "rgba(88, 28, 135, 0.24)",
        "round_border": "rgba(221, 214, 254, 0.40)",
        "round_title": "#e9d5ff",
        "round_text": "#faf5ff",
        "visual_bg": "rgba(67, 56, 202, 0.24)",
        "visual_border": "rgba(196, 181, 253, 0.35)",
        "visual_title": "#ddd6fe",
        "visual_text": "#f5f3ff",
        "trade_bg": "linear-gradient(135deg, #2e1065, #581c87)",
        "trade_border": "#c4b5fd",
        "trade_title": "#e9d5ff",
        "trade_text": "#faf5ff",
        "celebrate_bg": "rgba(74, 29, 150, 0.24)",
        "celebrate_border": "rgba(216, 180, 254, 0.35)",
        "progress_bg": "rgba(46, 16, 101, 0.28)",
        "progress_border": "rgba(196, 181, 253, 0.28)",
        "progress_text": "#faf5ff"
    },
    "Slate Blue": {
        "section_title": "#dbeafe",
        "section_subtle": "#e0f2fe",
        "step_bg": "rgba(30, 64, 175, 0.20)",
        "step_border": "rgba(147, 197, 253, 0.35)",
        "helper_bg": "rgba(51, 65, 85, 0.32)",
        "helper_border": "rgba(148, 163, 184, 0.28)",
        "feedback_bg": "rgba(146, 64, 14, 0.18)",
        "feedback_border": "rgba(253, 186, 116, 0.35)",
        "ai_bg": "rgba(37, 99, 235, 0.20)",
        "ai_border": "rgba(147, 197, 253, 0.35)",
        "round_bg": "rgba(8, 47, 73, 0.24)",
        "round_border": "rgba(103, 232, 249, 0.35)",
        "round_title": "#cffafe",
        "round_text": "#f0f9ff",
        "visual_bg": "rgba(15, 23, 42, 0.38)",
        "visual_border": "rgba(148, 163, 184, 0.35)",
        "visual_title": "#bfdbfe",
        "visual_text": "#eff6ff",
        "trade_bg": "linear-gradient(135deg, #0f172a, #1e3a8a)",
        "trade_border": "#93c5fd",
        "trade_title": "#dbeafe",
        "trade_text": "#eff6ff",
        "celebrate_bg": "rgba(30, 64, 175, 0.24)",
        "celebrate_border": "rgba(147, 197, 253, 0.35)",
        "progress_bg": "rgba(15, 23, 42, 0.34)",
        "progress_border": "rgba(147, 197, 253, 0.28)",
        "progress_text": "#eff6ff"
    },
    "Soft Sky": {
        "section_title": "#1e3a8a",
        "section_subtle": "#475569",
        "step_bg": "#e0f2fe",
        "step_border": "#7dd3fc",
        "helper_bg": "#f1f5f9",
        "helper_border": "#cbd5e1",
        "feedback_bg": "#fff7ed",
        "feedback_border": "#fdba74",
        "ai_bg": "#eef2ff",
        "ai_border": "#a5b4fc",
        "round_bg": "#ecfeff",
        "round_border": "#67e8f9",
        "round_title": "#0c4a6e",
        "round_text": "#0f172a",
        "visual_bg": "#f8fafc",
        "visual_border": "#cbd5e1",
        "visual_title": "#1e3a8a",
        "visual_text": "#0f172a",
        "trade_bg": "linear-gradient(135deg, #e0e7ff, #f0f9ff)",
        "trade_border": "#818cf8",
        "trade_title": "#1e40af",
        "trade_text": "#1e293b",
        "celebrate_bg": "#dcfce7",
        "celebrate_border": "#4ade80",
        "progress_bg": "#eff6ff",
        "progress_border": "#93c5fd",
        "progress_text": "#1e293b"
    }
}


# =========================
# SIDEBAR
# =========================
st.sidebar.title("Navigation")

topic = st.sidebar.selectbox(
    "Choose a topic",
    [
        "Decimal Addition",
        "Decimal Subtraction",
        "Decimal Multiplication",
        "Decimal Division",
        "Fraction Addition",
        "Fraction Subtraction",
        "Fraction Multiplication",
        "Fraction Division"
    ]
)

rounding_choice = st.sidebar.selectbox(
    "For decimal division or long decimal answers, round to:",
    ["No rounding instruction", "Nearest tenth", "Nearest hundredth", "Nearest thousandth"]
)

palette_name = st.sidebar.selectbox(
    "Choose a color palette",
    ["Soft Sky", "Deep Plum", "Slate Blue", "Midnight Teal"],
    key="selected_palette"
)

current_palette = PALETTES[palette_name]


# =========================
# CSS
# =========================
st.markdown(
    f"""
<style>
.section-title {{
    color: {current_palette["section_title"]};
    font-size: 2rem;
    font-weight: 800;
    letter-spacing: 0.2px;
    margin-top: 0.4rem;
    margin-bottom: 0.7rem;
}}

.mini-title {{
    color: {current_palette["section_title"]};
    font-size: 1.25rem;
    font-weight: 800;
    margin-top: 0.25rem;
    margin-bottom: 0.55rem;
}}

.topic-note {{
    color: {current_palette["section_subtle"]};
    font-size: 1rem;
    margin-bottom: 0.65rem;
}}

.step-box {{
    padding: 0.80rem;
    border-radius: 12px;
    background-color: {current_palette["step_bg"]};
    border: 1px solid {current_palette["step_border"]};
    margin-bottom: 0.55rem;
}}

.helper-box {{
    padding: 0.95rem;
    border-radius: 12px;
    background-color: {current_palette["helper_bg"]};
    border: 1px solid {current_palette["helper_border"]};
    margin-bottom: 0.55rem;
}}

.feedback-box {{
    padding: 1rem;
    border-radius: 12px;
    background-color: {current_palette["feedback_bg"]};
    border: 1px solid {current_palette["feedback_border"]};
    margin-top: 0.75rem;
}}

.ai-box {{
    padding: 1rem;
    border-radius: 12px;
    background-color: {current_palette["ai_bg"]};
    border: 1px solid {current_palette["ai_border"]};
    margin-top: 0.75rem;
}}

.rounding-box {{
    padding: 1rem;
    border-radius: 12px;
    background-color: {current_palette["round_bg"]};
    border: 1px solid {current_palette["round_border"]};
    margin-top: 0.75rem;
    margin-bottom: 0.75rem;
}}

.rounding-title {{
    color: {current_palette["round_title"]};
    font-weight: 700;
    margin-bottom: 0.45rem;
    font-size: 1.05rem;
}}

.rounding-text {{
    color: {current_palette["round_text"]};
    line-height: 1.65;
}}

.visual-shell {{
    padding: 1rem;
    border-radius: 12px;
    background-color: {current_palette["visual_bg"]};
    border: 1px solid {current_palette["visual_border"]};
    margin-top: 0.75rem;
    margin-bottom: 0.2rem;
}}

.visual-title {{
    color: {current_palette["visual_title"]};
    font-weight: 800;
    margin-bottom: 0.5rem;
    font-size: 1.05rem;
}}

.trade-box {{
    padding: 1.2rem;
    border-radius: 14px;
    background: {current_palette["trade_bg"]};
    border: 2px solid {current_palette["trade_border"]};
    margin-top: 1rem;
    margin-bottom: 1.2rem;
}}

.trade-title {{
    color: {current_palette["trade_title"]};
    font-weight: 900;
    font-size: 1.2rem;
    margin-bottom: 0.45rem;
}}

.trade-text {{
    color: {current_palette["trade_text"]};
    font-size: 1rem;
    line-height: 1.6;
}}

.celebrate-box {{
    padding: 1rem;
    border-radius: 14px;
    background-color: {current_palette["celebrate_bg"]};
    border: 1px solid {current_palette["celebrate_border"]};
    margin-top: 0.75rem;
    margin-bottom: 0.85rem;
    font-size: 1.1rem;
    font-weight: 700;
}}

.progress-box {{
    padding: 1rem;
    border-radius: 14px;
    background-color: {current_palette["progress_bg"]};
    border: 1px solid {current_palette["progress_border"]};
    margin-top: 0.5rem;
    margin-bottom: 1rem;
}}

.progress-text {{
    color: {current_palette["progress_text"]};
    font-size: 1rem;
    line-height: 1.6;
}}

.practice-note {{
    padding: 0.85rem;
    border-radius: 12px;
    background-color: rgba(255,255,255,0.03);
    border: 1px solid rgba(255,255,255,0.10);
    margin-top: 0.5rem;
}}
</style>
""",
    unsafe_allow_html=True
)


# =========================
# HUGGING FACE MODEL
# =========================
@st.cache_resource
def load_text_generator():
    try:
        return pipeline("text-generation", model="distilgpt2")
    except Exception:
        return None


text_generator = load_text_generator()


# =========================
# HELPERS
# =========================
def round_decimal_string(value, places):
    quantizers = {
        0: "1",
        1: "0.1",
        2: "0.01",
        3: "0.001",
    }
    d = Decimal(str(value))
    rounded = d.quantize(Decimal(quantizers[places]), rounding=ROUND_HALF_UP)
    return format(rounded, "f")


def format_fraction(frac):
    if isinstance(frac, Fraction):
        return f"{frac.numerator}/{frac.denominator}"
    return str(frac)


def mixed_number_string(frac):
    sign = -1 if frac < 0 else 1
    frac = abs(frac)
    whole = frac.numerator // frac.denominator
    remainder = frac.numerator % frac.denominator

    if remainder == 0:
        result = str(whole)
    elif whole == 0:
        result = f"{remainder}/{frac.denominator}"
    else:
        result = f"{whole} {remainder}/{frac.denominator}"

    if sign < 0 and result != "0":
        return f"-{result}"
    return result


def decimal_places_word(places):
    words = {
        1: "tenths",
        2: "hundredths",
        3: "thousandths"
    }
    return words.get(places, "decimal places")


def decimal_places_plain(places):
    plain = {
        1: "first digit after the decimal",
        2: "second digit after the decimal",
        3: "third digit after the decimal"
    }
    return plain.get(places, "digit after the decimal")


def get_place_value_words(number_string):
    if "." not in number_string:
        return []

    decimal_part = number_string.split(".")[1]
    labels = [
        ("first digit after the decimal", "tenths"),
        ("second digit after the decimal", "hundredths"),
        ("third digit after the decimal", "thousandths")
    ]
    results = []

    for i, digit in enumerate(decimal_part[:3]):
        if i < len(labels):
            plain_words, math_word = labels[i]
            results.append(f"{digit} is in the {plain_words} ({math_word} place)")

    return results


def compare_fraction_answers(user_text, correct_fraction):
    try:
        user_text = user_text.strip()

        if "/" in user_text:
            user_fraction = Fraction(user_text)
            return user_fraction == correct_fraction

        user_decimal = Decimal(user_text)
        correct_decimal = Decimal(str(float(correct_fraction)))
        return abs(user_decimal - correct_decimal) < Decimal("0.001")
    except Exception:
        return False


def compare_decimal_answers(user_text, correct_value, tolerance=0.001):
    try:
        return abs(float(user_text.strip()) - float(correct_value)) <= tolerance
    except Exception:
        return False


def get_rounding_places(rounding_choice):
    places_map = {
        "Nearest tenth": 1,
        "Nearest hundredth": 2,
        "Nearest thousandth": 3
    }
    return places_map.get(rounding_choice)


def reset_for_new_problem(problem):
    st.session_state.problem_data = problem
    st.session_state.problem_counter += 1
    st.session_state.hint_level = 0
    st.session_state.strategy_revealed = False
    st.session_state.wrong_attempts = 0
    st.session_state.answer_revealed_this_round = False


def generic_hint_from_problem(problem):
    if problem["type"] == "fraction":
        return "Focus on the top number, the bottom number, and whether the answer should be simplified."
    return "Focus on the decimal points and the digits after the decimal."


def get_topic_feedback(topic):
    feedback = {
        "Decimal Addition": {
            "mistake": "The decimal points may not be lined up.",
            "teach": "Line up the decimal points first. Then add from right to left.",
            "recheck": "Check the first and second digits after the decimal."
        },
        "Decimal Subtraction": {
            "mistake": "The decimal points may not be lined up, or regrouping may be off.",
            "teach": "Line up the decimal points. Then subtract from right to left. Borrow if needed.",
            "recheck": "Check each column carefully from right to left."
        },
        "Decimal Multiplication": {
            "mistake": "The decimal point may be in the wrong place.",
            "teach": "Multiply first like whole numbers. Then count the total digits after the decimal.",
            "recheck": "Check how many digits should be after the decimal in your answer."
        },
        "Decimal Division": {
            "mistake": "The divisor may not have been changed into a whole number first.",
            "teach": "Move the decimal to make the divisor a whole number. Move both numbers the same way.",
            "recheck": "Check that both numbers were moved the same amount."
        },
        "Fraction Addition": {
            "mistake": "The top numbers or the bottom number may have been handled the wrong way.",
            "teach": "Add the top numbers. Keep the bottom number the same.",
            "recheck": "Check that only the top numbers were added."
        },
        "Fraction Subtraction": {
            "mistake": "The subtraction may be off, or the bottom number may have changed.",
            "teach": "Subtract the top numbers. Keep the bottom number the same.",
            "recheck": "Check the top-number subtraction carefully."
        },
        "Fraction Multiplication": {
            "mistake": "You may not have multiplied straight across.",
            "teach": "Multiply top times top and bottom times bottom. Then simplify.",
            "recheck": "Check both multiplication steps."
        },
        "Fraction Division": {
            "mistake": "You may not have flipped the second fraction.",
            "teach": "Keep, change, flip. Then multiply.",
            "recheck": "Check whether you flipped the second fraction before multiplying."
        }
    }

    return feedback.get(topic, {
        "mistake": "Something needs another look.",
        "teach": "Follow the steps carefully.",
        "recheck": "Check each part again."
    })


def clean_ai_text(text):
    text = text.replace("\n", " ").replace("\r", " ").strip()
    text = re.sub(r"\s+", " ", text)

    if not text:
        return ""

    stop_markers = [
        "Question:",
        "Problem:",
        "Answer:",
        "Student:",
        "Tutor:",
        "Q:",
        "A:"
    ]
    for marker in stop_markers:
        if marker in text:
            text = text.split(marker)[0].strip()

    sentences = re.split(r'(?<=[.!?])\s+', text)
    cleaned_sentences = []

    for sentence in sentences:
        s = sentence.strip()

        if not s:
            continue

        lower_s = s.lower()

        if len(lower_s) < 4:
            continue

        if cleaned_sentences and lower_s == cleaned_sentences[-1].lower():
            continue

        cleaned_sentences.append(s)

        if len(cleaned_sentences) == 2:
            break

    final_text = " ".join(cleaned_sentences).strip()
    final_text = re.sub(r"\s+", " ", final_text)
    return final_text


def is_weak_ai_response(ai_text):
    if not ai_text:
        return True

    weak_phrases = [
        "use simple words",
        "be encouraging",
        "do not ask questions",
        "do not give the final answer",
        "write exactly",
        "short sentences",
        "math tutor",
        "problem type",
        "do not start a new problem"
    ]

    lower_text = ai_text.lower()

    if len(lower_text) < 18:
        return True

    for phrase in weak_phrases:
        if phrase in lower_text:
            return True

    if ":" in ai_text and len(ai_text.split()) < 10:
        return True

    return False


def fallback_ai_message(problem, support_type, rounding_choice):
    if problem["type"] == "fraction":
        answer_text = format_fraction(problem["answer"])
    else:
        answer_text = str(problem["answer"])

    if support_type == "success":
        if problem["type"] == "fraction":
            return (
                f"You solved the {problem['topic'].lower()} problem correctly. "
                f"The correct answer is {answer_text}, so your steps were on track."
            )
        return (
            f"You solved the {problem['topic'].lower()} problem correctly. "
            f"Your work matches the correct answer of {answer_text}."
        )

    if support_type == "mistake":
        feedback = get_topic_feedback(problem["topic"])
        return f"{feedback['teach']} {feedback['recheck']}"

    rounding_note = ""
    if problem["type"] == "decimal" and rounding_choice != "No rounding instruction":
        places = get_rounding_places(rounding_choice)
        rounding_note = f" Then round to the {decimal_places_word(places)} place if needed."

    return (
        f"For {problem['topic'].lower()}, follow the strategy one step at a time. "
        f"Check place value, operations, and simplification carefully.{rounding_note}"
    )


def get_ai_support(problem, support_type, rounding_choice):
    if text_generator is None:
        return fallback_ai_message(problem, support_type, rounding_choice)

    if support_type in ["mistake", "strategy"]:
        return fallback_ai_message(problem, support_type, rounding_choice)

    if problem["type"] == "fraction":
        answer_text = format_fraction(problem["answer"])
    else:
        answer_text = str(problem["answer"])

    rounding_text = ""
    if problem["type"] == "decimal" and rounding_choice != "No rounding instruction":
        places = get_rounding_places(rounding_choice)
        rounding_text = f" If needed, mention rounding to the {decimal_places_word(places)} place."

    prompt = (
        f"Math tutor response. "
        f"Problem type: {problem['topic']}. "
        f"Problem: {problem['question']}. "
        f"Correct answer: {answer_text}. "
        f"Write exactly 2 short sentences for a student. "
        f"Use simple words. Be encouraging. Do not ask questions. "
        f"Do not start a new problem.{rounding_text}"
    )

    try:
        response = text_generator(
            prompt,
            max_new_tokens=35,
            num_return_sequences=1,
            truncation=True,
            do_sample=False,
            temperature=0.0,
            pad_token_id=text_generator.tokenizer.eos_token_id
        )

        generated_text = response[0]["generated_text"]
        ai_text = generated_text[len(prompt):].strip()
        ai_text = clean_ai_text(ai_text)

        if is_weak_ai_response(ai_text):
            return fallback_ai_message(problem, support_type, rounding_choice)

        return ai_text
    except Exception:
        return fallback_ai_message(problem, support_type, rounding_choice)


def get_trade_context(trade_name):
    trade_contexts = {
        "Electrician": {
            "title": "Trade Focus: Electrician",
            "text": "Think about wire length, conduit runs, voltage readings, and precise measurements used in electrical work."
        },
        "Carpentry": {
            "title": "Trade Focus: Carpentry",
            "text": "Think about board cuts, framing, material estimates, and accurate fractions or decimals used in carpentry."
        },
        "Plumber": {
            "title": "Trade Focus: Plumber",
            "text": "Think about pipe length, fittings, slope, spacing, and accurate measurements used in plumbing."
        }
    }
    return trade_contexts.get(trade_name, trade_contexts["Electrician"])


def get_visual_support_text(problem):
    if problem["type"] == "decimal":
        if "Addition" in problem["topic"] or "Subtraction" in problem["topic"]:
            return (
                "Line up the decimal points.\n\n"
                "   12.86\n"
                "+   4.05\n"
                "--------\n"
                "   16.91\n\n"
                "Each column lines up:\n"
                "- Hundredths under hundredths\n"
                "- Tenths under tenths"
            )

        if "Multiplication" in problem["topic"]:
            return (
                "Multiply first like whole numbers:\n\n"
                "   2.4\n"
                "×  1.3\n"
                "------\n"
                "   72\n"
                "+ 24\n"
                "------\n"
                "  312\n\n"
                "Then place the decimal -> 3.12"
            )

        return (
            "Make the divisor a whole number first:\n\n"
            "4.8 ÷ 0.6 -> 48 ÷ 6\n\n"
            "Answer = 8"
        )

    if "Addition" in problem["topic"] or "Subtraction" in problem["topic"]:
        return (
            "Fraction reminder:\n\n"
            " numerator\n"
            "---------\n"
            "denominator\n\n"
            "For this kind of problem:\n"
            "- work with the top numbers\n"
            "- keep the bottom number the same"
        )

    if "Multiplication" in problem["topic"]:
        return (
            "Multiply straight across:\n\n"
            " a   c\n"
            "- × -\n"
            " b   d\n\n"
            "top × top\n"
            "bottom × bottom"
        )

    return (
        "Keep • Change • Flip\n\n"
        " a   c        a   d\n"
        "- ÷ -   =    - × -\n"
        " b   d        b   c"
    )


def reveal_answer_block(problem, rounding_choice):
    progress_placeholder = st.empty()
    progress_bar = st.progress(0)

    reveal_steps = [
        "Opening the answer...",
        "Showing the steps...",
        "Preparing the strategy summary..."
    ]

    for idx, step_text in enumerate(reveal_steps, start=1):
        progress_placeholder.info(step_text)
        progress_bar.progress(idx * 33)

    progress_placeholder.empty()
    progress_bar.empty()

    st.markdown("---")
    st.markdown('<div class="mini-title">Answer Revealed</div>', unsafe_allow_html=True)

    if problem["type"] == "fraction":
        st.write(f"**Simplified fraction:** {format_fraction(problem['answer'])}")
        st.write(f"**Mixed number form:** {mixed_number_string(problem['answer'])}")
        st.write(f"**Decimal form:** {round(float(problem['answer']), 3)}")
    else:
        st.write(f"**Exact answer:** {problem['answer']}")
        if rounding_choice != "No rounding instruction":
            places = get_rounding_places(rounding_choice)
            st.write(
                f"**Rounded to the {decimal_places_plain(places)} "
                f"({decimal_places_word(places)} place):** "
                f"{round_decimal_string(problem['answer'], places)}"
            )

    st.markdown('<div class="mini-title">Step-by-Step Solution</div>', unsafe_allow_html=True)
    for idx, step in enumerate(problem["steps"], start=1):
        st.markdown(f"**Step {idx}:** {step}")

    st.markdown('<div class="ai-box">', unsafe_allow_html=True)
    st.markdown('<div class="mini-title">Teacher Strategy Summary</div>', unsafe_allow_html=True)
    st.write(get_ai_support(problem, "strategy", rounding_choice))
    st.markdown("</div>", unsafe_allow_html=True)


def get_accuracy():
    if st.session_state.attempted_count == 0:
        return 0
    return round((st.session_state.correct_count / st.session_state.attempted_count) * 100)


def get_level_name(points):
    if points < 3:
        return "Starter"
    if points < 6:
        return "Builder"
    if points < 10:
        return "Skilled Learner"
    if points < 15:
        return "Trade Math Pro"
    return "Math Champion"


def progress_message():
    streak = st.session_state.streak_count
    points = st.session_state.level_points

    if streak >= 5:
        return f"🔥 Amazing! You are on a {streak}-problem streak."
    if streak >= 3:
        return f"👏 Great job! You are building momentum with a {streak}-problem streak."
    if points >= 10:
        return "🎯 You are leveling up fast. Keep going."
    return "⭐ Every problem you try builds your trade math skills."


# =========================
# PROBLEM GENERATORS
# =========================
def generate_decimal_addition(difficulty="normal"):
    if difficulty == "harder":
        a = round(random.uniform(10.125, 99.875), 3)
        b = round(random.uniform(10.125, 99.875), 3)
    else:
        a = round(random.uniform(1.1, 25.9), 2)
        b = round(random.uniform(1.1, 25.9), 2)

    answer = round(a + b, 3)

    return {
        "type": "decimal",
        "topic": "Decimal Addition",
        "question": f"{a} + {b}",
        "answer": answer,
        "difficulty": difficulty,
        "steps": [
            "Line up the decimal points.",
            "Add from right to left.",
            "Bring the decimal point straight down into the answer."
        ],
        "vocabulary": get_place_value_words(f"{a}") + get_place_value_words(f"{b}"),
        "hint1": "Line up the decimal points.",
        "hint2": "Add from right to left, then bring the decimal point straight down."
    }


def generate_decimal_subtraction(difficulty="normal"):
    if difficulty == "harder":
        a = round(random.uniform(20.125, 99.875), 3)
        b = round(random.uniform(5.125, 49.875), 3)
    else:
        a = round(random.uniform(10.0, 30.0), 2)
        b = round(random.uniform(1.0, 9.9), 2)

    if b > a:
        a, b = b, a

    answer = round(a - b, 3)

    return {
        "type": "decimal",
        "topic": "Decimal Subtraction",
        "question": f"{a} - {b}",
        "answer": answer,
        "difficulty": difficulty,
        "steps": [
            "Line up the decimal points.",
            "Subtract from right to left.",
            "Regroup if needed.",
            "Bring the decimal point straight down into the answer."
        ],
        "vocabulary": get_place_value_words(f"{a}") + get_place_value_words(f"{b}"),
        "hint1": "Line up the decimal points.",
        "hint2": "Subtract from right to left. Borrow if needed."
    }


def generate_decimal_multiplication(difficulty="normal"):
    if difficulty == "harder":
        a = round(random.uniform(2.125, 12.875), 3)
        b = round(random.uniform(2.125, 12.875), 3)
    else:
        a = round(random.uniform(1.1, 9.9), 2)
        b = round(random.uniform(1.1, 9.9), 2)

    answer = round(a * b, 3)

    return {
        "type": "decimal",
        "topic": "Decimal Multiplication",
        "question": f"{a} × {b}",
        "answer": answer,
        "difficulty": difficulty,
        "steps": [
            "Multiply as if the numbers were whole numbers.",
            "Count the total number of digits to the right of the decimal points in both factors.",
            "Place the decimal point in the product so it has that same total number of decimal places."
        ],
        "vocabulary": get_place_value_words(f"{a}") + get_place_value_words(f"{b}"),
        "hint1": "Multiply first like whole numbers.",
        "hint2": "Then count how many total digits are after the decimal."
    }


def generate_decimal_division(difficulty="normal"):
    if difficulty == "harder":
        divisor = round(random.uniform(1.25, 9.95), 2)
        quotient = round(random.uniform(2.125, 15.875), 3)
    else:
        divisor = round(random.uniform(1.1, 9.9), 1)
        quotient = round(random.uniform(1.2, 9.5), 2)

    dividend = round(divisor * quotient, 3)
    answer = round(dividend / divisor, 3)

    return {
        "type": "decimal",
        "topic": "Decimal Division",
        "question": f"{dividend} ÷ {divisor}",
        "answer": answer,
        "difficulty": difficulty,
        "steps": [
            "Move the decimal point in the divisor to make it a whole number.",
            "Move the decimal point in the dividend the same number of places.",
            "Divide as usual.",
            "Place the decimal point in the quotient directly above the decimal point in the dividend."
        ],
        "vocabulary": get_place_value_words(f"{dividend}") + get_place_value_words(f"{divisor}"),
        "hint1": "Make the divisor a whole number first.",
        "hint2": "Move both decimals the same amount, then divide."
    }


def generate_fraction_addition(difficulty="normal"):
    if difficulty == "harder":
        d = random.randint(6, 20)
    else:
        d = random.randint(2, 12)

    n1 = random.randint(1, d - 1)
    n2 = random.randint(1, d - 1)
    f1 = Fraction(n1, d)
    f2 = Fraction(n2, d)
    answer = f1 + f2

    return {
        "type": "fraction",
        "topic": "Fraction Addition",
        "question": f"{format_fraction(f1)} + {format_fraction(f2)}",
        "answer": answer,
        "difficulty": difficulty,
        "steps": [
            "The denominators are already the same.",
            "Add the numerators.",
            "Keep the denominator the same.",
            "Simplify if possible."
        ],
        "vocabulary": [
            "Numerator: the top number",
            "Denominator: the bottom number",
            "Like denominators: bottom numbers that are the same"
        ],
        "hint1": "Add the top numbers.",
        "hint2": "Keep the bottom number the same."
    }


def generate_fraction_subtraction(difficulty="normal"):
    if difficulty == "harder":
        d = random.randint(6, 20)
    else:
        d = random.randint(2, 12)

    n1 = random.randint(2, d)
    n2 = random.randint(1, n1 - 1)
    f1 = Fraction(n1, d)
    f2 = Fraction(n2, d)
    answer = f1 - f2

    return {
        "type": "fraction",
        "topic": "Fraction Subtraction",
        "question": f"{format_fraction(f1)} - {format_fraction(f2)}",
        "answer": answer,
        "difficulty": difficulty,
        "steps": [
            "The denominators are already the same.",
            "Subtract the numerators.",
            "Keep the denominator the same.",
            "Simplify if possible."
        ],
        "vocabulary": [
            "Numerator: the top number",
            "Denominator: the bottom number",
            "Difference: the answer to a subtraction problem"
        ],
        "hint1": "Subtract the top numbers.",
        "hint2": "Keep the bottom number the same."
    }


def generate_fraction_multiplication(difficulty="normal"):
    if difficulty == "harder":
        f1 = Fraction(random.randint(2, 12), random.randint(5, 15))
        f2 = Fraction(random.randint(2, 12), random.randint(5, 15))
    else:
        f1 = Fraction(random.randint(1, 8), random.randint(2, 9))
        f2 = Fraction(random.randint(1, 8), random.randint(2, 9))

    answer = f1 * f2

    return {
        "type": "fraction",
        "topic": "Fraction Multiplication",
        "question": f"{format_fraction(f1)} × {format_fraction(f2)}",
        "answer": answer,
        "difficulty": difficulty,
        "steps": [
            "Multiply the numerators.",
            "Multiply the denominators.",
            "Simplify if possible."
        ],
        "vocabulary": [
            "Product: the answer to a multiplication problem",
            "Simplify: write the fraction in lowest terms"
        ],
        "hint1": "Multiply top times top.",
        "hint2": "Multiply bottom times bottom, then simplify."
    }


def generate_fraction_division(difficulty="normal"):
    if difficulty == "harder":
        f1 = Fraction(random.randint(2, 12), random.randint(5, 15))
        f2 = Fraction(random.randint(2, 12), random.randint(5, 15))
    else:
        f1 = Fraction(random.randint(1, 8), random.randint(2, 9))
        f2 = Fraction(random.randint(1, 8), random.randint(2, 9))

    answer = f1 / f2

    return {
        "type": "fraction",
        "topic": "Fraction Division",
        "question": f"{format_fraction(f1)} ÷ {format_fraction(f2)}",
        "answer": answer,
        "difficulty": difficulty,
        "steps": [
            "Keep the first fraction.",
            "Change division to multiplication.",
            "Flip the second fraction (find the reciprocal).",
            "Multiply the numerators and denominators.",
            "Simplify if possible."
        ],
        "vocabulary": [
            "Reciprocal: flip the top and bottom numbers",
            "Quotient: the answer to a division problem"
        ],
        "hint1": "Use keep, change, flip.",
        "hint2": "Then multiply straight across."
    }


def generate_problem(topic_name, difficulty="normal"):
    generators = {
        "Decimal Addition": generate_decimal_addition,
        "Decimal Subtraction": generate_decimal_subtraction,
        "Decimal Multiplication": generate_decimal_multiplication,
        "Decimal Division": generate_decimal_division,
        "Fraction Addition": generate_fraction_addition,
        "Fraction Subtraction": generate_fraction_subtraction,
        "Fraction Multiplication": generate_fraction_multiplication,
        "Fraction Division": generate_fraction_division,
    }
    return generators[topic_name](difficulty)


# =========================
# APP HEADER
# =========================
st.title("Guided AI Math Tutor")
st.write(
    "Practice fractions and decimals with guided support, vocabulary, hints, "
    "step-by-step explanations, controlled AI support, and extra practice."
)


# =========================
# PROGRESS TRACKING
# =========================
accuracy = get_accuracy()
level_name = get_level_name(st.session_state.level_points)

st.markdown(
    f"""
    <div class="progress-box">
        <div class="mini-title">Your Progress</div>
        <div class="progress-text">
            ✅ Correct: <strong>{st.session_state.correct_count}</strong> &nbsp;&nbsp;
            📝 Attempted: <strong>{st.session_state.attempted_count}</strong> &nbsp;&nbsp;
            🎯 Accuracy: <strong>{accuracy}%</strong> &nbsp;&nbsp;
            🔥 Streak: <strong>{st.session_state.streak_count}</strong> &nbsp;&nbsp;
            ⭐ Points: <strong>{st.session_state.level_points}</strong> &nbsp;&nbsp;
            🏅 Level: <strong>{level_name}</strong>
        </div>
        <div class="progress-text" style="margin-top: 0.4rem;">{progress_message()}</div>
    </div>
    """,
    unsafe_allow_html=True
)

progress_fraction = min((st.session_state.level_points % 5) / 5, 1.0)
st.progress(progress_fraction, text=f"Progress to next level: {int(progress_fraction * 100)}%")


# =========================
# TOPIC INTRO
# =========================
topic_descriptions = {
    "Decimal Addition": "Add decimals by lining up decimal points and combining place values correctly.",
    "Decimal Subtraction": "Subtract decimals by lining up decimal points and regrouping when needed.",
    "Decimal Multiplication": "Multiply decimals by multiplying like whole numbers, then placing the decimal correctly.",
    "Decimal Division": "Divide decimals by making the divisor a whole number, then dividing.",
    "Fraction Addition": "Add fractions carefully and simplify your final answer when possible.",
    "Fraction Subtraction": "Subtract fractions carefully and simplify your final answer when possible.",
    "Fraction Multiplication": "Multiply across and simplify the product.",
    "Fraction Division": "Use keep-change-flip, then multiply and simplify."
}

st.markdown(f'<div class="section-title">Current Topic: {topic}</div>', unsafe_allow_html=True)
st.markdown(f'<div class="topic-note">{topic_descriptions[topic]}</div>', unsafe_allow_html=True)


# =========================
# TRADE SELECTOR BANNER
# =========================
st.markdown('<div class="mini-title">Choose a Trade Focus</div>', unsafe_allow_html=True)

trade_choice = st.radio(
    "Choose a Trade Focus",
    ["Electrician", "Carpentry", "Plumber"],
    horizontal=True,
    key="selected_trade",
    label_visibility="collapsed"
)

trade_context = get_trade_context(trade_choice)

st.markdown(
    f"""
    <div class="trade-box">
        <div class="trade-title">{trade_context["title"]}</div>
        <div class="trade-text">{trade_context["text"]}</div>
    </div>
    """,
    unsafe_allow_html=True
)


# =========================
# TOP BUTTONS
# =========================
top_col1, top_col2, top_col3, top_col4 = st.columns(4)

with top_col1:
    if st.button("Generate New Problem", use_container_width=True):
        reset_for_new_problem(generate_problem(topic, "normal"))

with top_col2:
    if st.button("Give Me a Similar Problem", use_container_width=True):
        reset_for_new_problem(generate_problem(topic, "normal"))

with top_col3:
    if st.button("Give Me a Harder Problem", use_container_width=True):
        reset_for_new_problem(generate_problem(topic, "harder"))

with top_col4:
    if st.button("Clear Current Problem", use_container_width=True):
        st.session_state.problem_data = None
        st.session_state.hint_level = 0
        st.session_state.strategy_revealed = False
        st.session_state.wrong_attempts = 0
        st.session_state.answer_revealed_this_round = False


# =========================
# GENERATE FIRST PROBLEM IF NEEDED
# =========================
if st.session_state.problem_data is None or st.session_state.problem_data["topic"] != topic:
    reset_for_new_problem(generate_problem(topic, "normal"))

problem = st.session_state.problem_data


# =========================
# DISPLAY PROBLEM
# =========================
st.divider()
st.markdown('<div class="section-title">Practice Problem</div>', unsafe_allow_html=True)
st.markdown(f"## {problem['question']}")

if problem.get("difficulty") == "harder":
    st.caption("Difficulty level: Harder")

st.caption(f"Trade connection: {trade_choice}")


# =========================
# GUIDED PROMPTS
# =========================
with st.expander("Think Before You Solve (Optional)", expanded=False):
    st.write("Use these prompts to guide your thinking before you answer.")

    st.text_input(
        "1. What is the problem asking you to find?",
        key=f"find_{st.session_state.problem_counter}"
    )

    st.text_area(
        "2. What information do you know?",
        key=f"know_{st.session_state.problem_counter}",
        height=100
    )

    st.text_input(
        "3. What operation(s) will you perform?",
        key=f"op_{st.session_state.problem_counter}"
    )


# =========================
# VOCABULARY + HELP
# =========================
left_col, right_col = st.columns(2)

with left_col:
    st.markdown('<div class="section-title">Vocabulary</div>', unsafe_allow_html=True)
    for item in problem["vocabulary"]:
        st.markdown(f"- {item}")

    visual_text = get_visual_support_text(problem)

    st.markdown(
        """
        <div class="visual-shell">
            <div class="visual-title">Visual Support</div>
        </div>
        """,
        unsafe_allow_html=True
    )
    st.code(visual_text)

with right_col:
    st.markdown('<div class="section-title">Strategy</div>', unsafe_allow_html=True)

    if st.session_state.strategy_revealed:
        for step in problem["steps"]:
            st.markdown(f'<div class="step-box">{step}</div>', unsafe_allow_html=True)
    else:
        st.markdown(
            '<div class="helper-box">Strategy is hidden for now. Try the problem first. It will appear after 2 hints or after a wrong answer.</div>',
            unsafe_allow_html=True
        )


# =========================
# ANSWER INPUT + ACTIONS
# =========================
st.divider()
st.markdown('<div class="section-title">Your Answer</div>', unsafe_allow_html=True)

user_answer = st.text_input(
    "Type your answer here",
    key=f"answer_{st.session_state.problem_counter}"
)

action_col1, action_col2, action_col3 = st.columns(3)

with action_col1:
    check_answer = st.button("Check My Answer", use_container_width=True)

with action_col2:
    get_hint = st.button("Get Hint", use_container_width=True)

with action_col3:
    show_solution = st.button("Show Step-by-Step Solution", use_container_width=True)


# =========================
# HINTS
# =========================
if get_hint:
    st.session_state.hint_level += 1

    if st.session_state.hint_level >= 2:
        st.session_state.strategy_revealed = True

if st.session_state.hint_level > 0:
    hint_text = (
        problem.get("hint1", generic_hint_from_problem(problem))
        if st.session_state.hint_level == 1
        else problem.get("hint2", generic_hint_from_problem(problem))
    )

    st.info(hint_text)

    if st.session_state.hint_level >= 2:
        st.caption("Strategy is now shown on the right.")


# =========================
# ROUNDING HELP
# =========================
if rounding_choice != "No rounding instruction":
    chosen_places = get_rounding_places(rounding_choice)

    st.markdown(
        f"""
        <div class="rounding-box">
            <div class="rounding-title">Instructions on How to Round</div>
            <div class="rounding-text">
                Round your answer to the {decimal_places_plain(chosen_places)} ({decimal_places_word(chosen_places)} place).<br><br>
                • Look at the digit to the right.<br>
                • If it is 5 or more, round up.<br>
                • If it is 4 or less, keep the digit the same.
            </div>
        </div>
        """,
        unsafe_allow_html=True
    )


# =========================
# CHECK ANSWER
# =========================
if check_answer:
    if not user_answer.strip():
        st.warning("Please type an answer first.")
    else:
        st.session_state.attempted_count += 1
        is_correct = False

        if problem["type"] == "fraction":
            is_correct = compare_fraction_answers(user_answer, problem["answer"])
        else:
            correct_value = problem["answer"]

            if rounding_choice == "No rounding instruction":
                is_correct = compare_decimal_answers(user_answer, correct_value)
            else:
                places = get_rounding_places(rounding_choice)
                rounded_correct = float(round_decimal_string(correct_value, places))
                is_correct = compare_decimal_answers(
                    user_answer,
                    rounded_correct,
                    tolerance=0.0001
                )

        if is_correct:
            st.session_state.correct_count += 1
            st.session_state.streak_count += 1
            st.session_state.level_points += 1
            st.session_state.wrong_attempts = 0
            st.balloons()

            st.markdown(
                '<div class="celebrate-box">🎉👏 Correct! Nice work. Fist bump! 👊✨</div>',
                unsafe_allow_html=True
            )

            if problem["type"] == "fraction":
                st.write(f"**Simplified answer:** {format_fraction(problem['answer'])}")
                st.write(f"**Mixed number form (if needed):** {mixed_number_string(problem['answer'])}")
            else:
                st.write(f"**Exact answer:** {problem['answer']}")
                if rounding_choice != "No rounding instruction":
                    places = get_rounding_places(rounding_choice)
                    st.write(f"**Rounded answer:** {round_decimal_string(problem['answer'], places)}")

            st.markdown('<div class="ai-box">', unsafe_allow_html=True)
            st.markdown('<div class="mini-title">Hugging Face AI Tutor</div>', unsafe_allow_html=True)
            st.write(get_ai_support(problem, "success", rounding_choice))
            st.markdown("</div>", unsafe_allow_html=True)

        else:
            st.session_state.streak_count = 0
            st.session_state.wrong_attempts += 1
            st.session_state.strategy_revealed = True

            st.error("Not quite yet.")

            feedback = get_topic_feedback(problem["topic"])

            st.markdown('<div class="feedback-box">', unsafe_allow_html=True)
            st.markdown('<div class="mini-title">Teacher Feedback</div>', unsafe_allow_html=True)
            st.write(f"**What to recheck:** {feedback['mistake']}")
            st.write(f"**Mini-lesson:** {feedback['teach']}")
            st.write(f"**Try this next:** {feedback['recheck']}")
            st.write("Strategy is now shown on the right to help you try again.")
            st.markdown("</div>", unsafe_allow_html=True)

            st.write("Also check these questions:")
            st.write("- Did you use the correct operation?")
            st.write("- Did you simplify the fraction if needed?")
            st.write("- Did you round the decimal the way the directions asked?")

            st.markdown('<div class="ai-box">', unsafe_allow_html=True)
            st.markdown('<div class="mini-title">Teacher Hint</div>', unsafe_allow_html=True)
            st.write(get_ai_support(problem, "mistake", rounding_choice))
            st.markdown("</div>", unsafe_allow_html=True)

            if st.session_state.wrong_attempts >= 2 and not st.session_state.answer_revealed_this_round:
                st.session_state.answer_revealed_this_round = True
                st.warning("You have had 2 tries on this problem, so the app will now show the answer and solution.")
                reveal_answer_block(problem, rounding_choice)


# =========================
# SHOW SOLUTION
# =========================
if show_solution:
    st.markdown('<div class="section-title">Step-by-Step Solution</div>', unsafe_allow_html=True)

    for idx, step in enumerate(problem["steps"], start=1):
        st.markdown(f"**Step {idx}:** {step}")

    st.markdown("---")
    st.markdown('<div class="mini-title">Answer</div>', unsafe_allow_html=True)

    if problem["type"] == "fraction":
        st.write(f"**Simplified fraction:** {format_fraction(problem['answer'])}")
        st.write(f"**Mixed number form:** {mixed_number_string(problem['answer'])}")
        st.write(f"**Decimal form:** {round(float(problem['answer']), 3)}")
    else:
        st.write(f"**Exact answer:** {problem['answer']}")

        if rounding_choice != "No rounding instruction":
            places = get_rounding_places(rounding_choice)
            st.write(
                f"**Rounded to the {decimal_places_plain(places)} "
                f"({decimal_places_word(places)} place):** "
                f"{round_decimal_string(problem['answer'], places)}"
            )

    st.markdown('<div class="ai-box">', unsafe_allow_html=True)
    st.markdown('<div class="mini-title">Teacher Strategy Summary</div>', unsafe_allow_html=True)
    st.write(get_ai_support(problem, "strategy", rounding_choice))
    st.markdown("</div>", unsafe_allow_html=True)


# =========================
# EXTRA PRACTICE
# =========================
st.divider()
st.markdown('<div class="section-title">Practice Again</div>', unsafe_allow_html=True)
st.markdown(
    '<div class="practice-note">Use <strong>Give Me a Similar Problem</strong> for another problem of the same type, or click <strong>Give Me a Harder Problem</strong> to level up.</div>',
    unsafe_allow_html=True
)