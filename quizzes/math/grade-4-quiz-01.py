
# Grade 4 Math Quiz
#
# Instructions:
# - Run from the workspace root:
#     python3 quizzes/math/grade-4-quiz-01.py [--no-shuffle] [--seed N]
# - The quiz runs interactively and will prompt for a single-letter answer (A, B, C, ...).
# - Invalid inputs are rejected and the script will re-prompt until a valid letter is entered.
# - Use `--seed N` to reproduce a particular shuffled order for testing.
# - Use `--no-shuffle` to disable shuffling of both questions and choices.
# - Use `--count N` to specify how many questions to ask in a session
#   (fixed questions are kept and generated questions will be added if needed).

import random
import argparse

parser = argparse.ArgumentParser(description="Grade 4 math quiz")
parser.add_argument('--no-shuffle', action='store_true', help='Disable shuffling of questions and choices')
parser.add_argument('--seed', type=int, default=None, help='Optional RNG seed for reproducible shuffling')
parser.add_argument('--count', type=int, default=None, help='Number of questions to ask in this session')
args = parser.parse_args()

print("====================================================")
print(" Quiz: Math club — Grade 4 Quiz 01 ".center(52))
print("====================================================")

# If a seed is provided, use it for reproducible shuffling; otherwise seed
# from system entropy so each run is different by default
if args.seed is not None:
    random.seed(args.seed)
else:
    random.seed()

# Enable shuffling of questions and choices (toggleable via --no-shuffle)
shuffle_questions = not args.no_shuffle
shuffle_choices = not args.no_shuffle

# Questions store choices as a list and a single 'correct' index
questions = [
    {
        "text": "What is 9 x 8?",
        "choices": ["72", "81", "64", "79"],
        "correct": 0
    },
    {
        "text": "What is 8/10 as a decimal?",
        "choices": ["0.8", "0.08", "8.0", "0.85"],
        "correct": 0
    },
    {
        "text": "What is 42 x 87?",
        "choices": ["3624", "3627", "3654", "3844"],
        "correct": 2
    },
    {
        "text": "What is 1833 x 5?",
        "choices": ["9165", "9185", "9125", "9195"],
        "correct": 0
    },
    {
        "text": "What is 9/12 as a fraction in simplest form?",
        "choices": ["3/4", "4/5", "2/3", "5/6"],
        "correct": 0
    }
]

if shuffle_questions:
    random.shuffle(questions)

score = 0

# --- Question generators -------------------------------------------------
def gen_multiplication(a_min=2, a_max=20, b_min=2, b_max=20):
    a = random.randint(a_min, a_max)
    b = random.randint(b_min, b_max)
    correct = a * b
    # generate 3 distractors
    distractors = set()
    attempts = 0
    while len(distractors) < 3 and attempts < 50:
        attempts += 1
        # small perturbation or swapped digits
        delta = random.choice([-3, -2, -1, 1, 2, 3, 10])
        cand = correct + delta
        if cand != correct and cand > 0:
            distractors.add(str(cand))
    choices = [str(correct)] + list(distractors)
    random.shuffle(choices)
    correct_index = choices.index(str(correct))
    return {"text": f"What is {a} x {b}?", "choices": choices, "correct": correct_index}

def gen_large_multiplication(a_min=100, a_max=200, b_min=2, b_max=9):
    a = random.randint(a_min, a_max)
    b = random.randint(b_min, b_max)
    correct = a * b
    distractors = set()
    attempts = 0
    while len(distractors) < 3 and attempts < 50:
        attempts += 1
        cand = correct + random.choice([-50, -10, 10, 50, 100])
        if cand != correct and cand > 0:
            distractors.add(str(cand))
    choices = [str(correct)] + list(distractors)
    random.shuffle(choices)
    correct_index = choices.index(str(correct))
    return {"text": f"What is {a} x {b}?", "choices": choices, "correct": correct_index}

def gen_fraction_decimal():
    # produce fraction with denominator 10 or 100 so decimal is exact
    denom = random.choice([10, 100])
    num = random.randint(1, denom - 1)
    correct = num / denom
    correct_str = str(correct).rstrip('0').rstrip('.') if denom == 100 and correct != int(correct) else str(correct)
    distractors = set()
    attempts = 0
    while len(distractors) < 3 and attempts < 50:
        attempts += 1
        d = num + random.choice([-3, -2, -1, 1, 2, 3])
        if 0 < d < denom:
            val = d / denom
            s = str(val).rstrip('0').rstrip('.')
            if s != correct_str:
                distractors.add(s)
    choices = [correct_str] + list(distractors)
    random.shuffle(choices)
    correct_index = choices.index(correct_str)
    return {"text": f"What is {num}/{denom} as a decimal?", "choices": choices, "correct": correct_index}

def gen_fraction_simplify():
    # generate numerator/denom with gcd>1
    while True:
        denom = random.randint(2, 12)
        num = random.randint(2, denom)
        from math import gcd
        g = gcd(num, denom)
        if g > 1:
            simp_num = num // g
            simp_den = denom // g
            break
    correct = f"{simp_num}/{simp_den}"
    distractors = set()
    attempts = 0
    while len(distractors) < 3 and attempts < 50:
        attempts += 1
        # produce incorrect simplifications
        a = random.randint(1, denom)
        b = random.randint(1, denom)
        s = f"{a}/{b}"
        if s != correct:
            distractors.add(s)
    choices = [correct] + list(distractors)
    random.shuffle(choices)
    correct_index = choices.index(correct)
    return {"text": f"What is {num}/{denom} as a fraction in simplest form?", "choices": choices, "correct": correct_index}

# pool of generator functions to create extra questions
GENERATORS = [gen_multiplication, gen_large_multiplication, gen_fraction_decimal, gen_fraction_simplify]

# Additional 4th-grade-level generators
def gen_addition():
    a = random.randint(0, 100)
    b = random.randint(0, 100)
    correct = a + b
    distractors = set()
    while len(distractors) < 3:
        cand = correct + random.choice([-10, -5, -1, 1, 2, 5, 10])
        if cand >= 0 and cand != correct:
            distractors.add(str(cand))
    choices = [str(correct)] + list(distractors)
    random.shuffle(choices)
    return {"text": f"What is {a} + {b}?", "choices": choices, "correct": choices.index(str(correct))}

def gen_subtraction():
    a = random.randint(0, 100)
    b = random.randint(0, a)
    correct = a - b
    distractors = set()
    while len(distractors) < 3:
        cand = correct + random.choice([-6, -3, -1, 1, 3, 6])
        if cand >= 0 and cand != correct:
            distractors.add(str(cand))
    choices = [str(correct)] + list(distractors)
    random.shuffle(choices)
    return {"text": f"What is {a} - {b}?", "choices": choices, "correct": choices.index(str(correct))}

def gen_division_exact():
    b = random.randint(2, 12)
    q = random.randint(2, 12)
    a = b * q
    correct = q
    distractors = set()
    while len(distractors) < 3:
        cand = correct + random.choice([-3, -2, -1, 1, 2, 3])
        if cand > 0 and cand != correct:
            distractors.add(str(cand))
    choices = [str(correct)] + list(distractors)
    random.shuffle(choices)
    return {"text": f"What is {a} ÷ {b}?", "choices": choices, "correct": choices.index(str(correct))}

def gen_missing_addend():
    b = random.randint(0, 50)
    x = random.randint(0, 50)
    total = x + b
    correct = x
    distractors = set()
    while len(distractors) < 3:
        cand = correct + random.choice([-5, -2, -1, 1, 2, 5])
        if cand >= 0 and cand != correct:
            distractors.add(str(cand))
    choices = [str(correct)] + list(distractors)
    random.shuffle(choices)
    return {"text": f"What number plus {b} equals {total}?", "choices": choices, "correct": choices.index(str(correct))}

def gen_round_tens():
    n = random.randint(10, 99)
    correct = str(round(n, -1))
    distractors = {str(max(0, round(n + d, -1))) for d in (-15, -7, 7, 15)}
    distractors.discard(correct)
    while len(distractors) < 3:
        distractors.add(str(round(n + random.choice([-12, -6, 6, 12]), -1)))
    choices = [correct] + list(distractors)[:3]
    random.shuffle(choices)
    return {"text": f"Round {n} to the nearest ten.", "choices": choices, "correct": choices.index(correct)}

def gen_time_add():
    hour = random.randint(1, 11)
    minute = random.choice([0, 5, 10, 15, 20, 25, 30, 35, 40, 45, 50, 55])
    add_m = random.choice([5, 10, 15, 20, 30, 45])
    total_min = hour * 60 + minute + add_m
    new_hour = ((total_min // 60 - 1) % 12) + 1
    new_min = total_min % 60
    correct = f"{new_hour}:{new_min:02d}"
    distractors = set()
    while len(distractors) < 3:
        m = (new_min + random.choice([-15, -10, -5, 5, 10, 15])) % 60
        h = new_hour
        if m > new_min and new_min - 30 > 0:
            h = (new_hour - 1 - 1) % 12 + 1
        cand = f"{h}:{m:02d}"
        if cand != correct:
            distractors.add(cand)
    choices = [correct] + list(distractors)
    random.shuffle(choices)
    return {"text": f"What time is {hour}:{minute:02d} plus {add_m} minutes?", "choices": choices, "correct": choices.index(correct)}

def gen_money_change():
    cost = random.choice([random.randint(1, 20) + random.choice([0, .25, .5, .75]) for _ in range(5)])
    paid = random.choice([round(cost + d, 2) for d in (0.25, 0.5, 1, 2, 5)])
    correct = round(paid - cost, 2)
    distractors = set()
    while len(distractors) < 3:
        cand = round(correct + random.choice([-1, -0.5, 0.5, 1, 2]), 2)
        if cand >= 0 and cand != correct:
            distractors.add(f"${cand:.2f}")
    choices = [f"${correct:.2f}"] + list(distractors)
    random.shuffle(choices)
    return {"text": f"You pay ${paid:.2f} for an item that costs ${cost:.2f}. How much change should you get?", "choices": choices, "correct": choices.index(f"${correct:.2f}")}

def gen_area_rectangle():
    l = random.randint(1, 12)
    w = random.randint(1, 12)
    correct = l * w
    distractors = set()
    while len(distractors) < 3:
        cand = correct + random.choice([-l, -w, -2, 2, l, w])
        if cand > 0 and cand != correct:
            distractors.add(str(cand))
    choices = [str(correct)] + list(distractors)
    random.shuffle(choices)
    return {"text": f"What is the area of a {l} by {w} rectangle (in square units)?", "choices": choices, "correct": choices.index(str(correct))}

def gen_compare_numbers():
    a = random.randint(1, 100)
    b = random.randint(1, 100)
    if a < b:
        corr = "<"
    elif a > b:
        corr = ">"
    else:
        corr = "="
    choices = ["<", ">", "="]
    random.shuffle(choices)
    return {"text": f"Which is true: {a} ? {b}", "choices": choices, "correct": choices.index(corr)}

# Extend GENERATORS with the new types
GENERATORS.extend([
    gen_addition,
    gen_subtraction,
    gen_division_exact,
    gen_missing_addend,
    gen_round_tens,
    gen_time_add,
    gen_money_change,
    gen_area_rectangle,
    gen_compare_numbers,
])

# Build final question list according to requested count and interleave generated questions
fixed = questions[:]  # keep original fixed pool
generated = []
desired = args.count if args.count is not None else len(fixed)

if desired > len(fixed):
    needed = desired - len(fixed)
    for _ in range(needed):
        gen = random.choice(GENERATORS)
        generated.append(gen())

# Optionally shuffle each pool before interleaving to keep randomness
if shuffle_questions:
    random.shuffle(fixed)
    random.shuffle(generated)

# Interleave fixed and generated questions
if generated:
    combined = []
    maxn = max(len(fixed), len(generated))
    for i in range(maxn):
        if i < len(fixed):
            combined.append(fixed[i])
        if i < len(generated):
            combined.append(generated[i])
else:
    combined = fixed

questions = combined[:desired]

quit_early = False

for i, q in enumerate(questions, start=1):
    # Shuffle choices while tracking where the correct answer ends up
    if shuffle_choices:
        indices = list(range(len(q["choices"])));
        random.shuffle(indices)
        shuffled_choices = [q["choices"][j] for j in indices]
        correct_index = indices.index(q["correct"])  # new position of the correct answer
    else:
        shuffled_choices = q["choices"][:]
        correct_index = q["correct"]

    # Build choices display dynamically for any number of options
    choices_display = " ".join(f"{chr(65 + idx)}) {text}" for idx, text in enumerate(shuffled_choices))
    print(f"Question {i}: {q['text']}", choices_display)

    # Valid letters depend on number of options
    valid_letters = [chr(65 + k) for k in range(len(shuffled_choices))]

    # Input validation: re-prompt until valid
    while True:
        try:
            answer = input(f"Enter your answer ({', '.join(valid_letters)}): ").strip().upper()
        except EOFError:
            # piped input ended; exit the quiz early but print current score
            print("\nNo more input detected — ending quiz early.")
            quit_early = True
            break
        if answer in valid_letters:
            break
        print(f"Please enter one of: {', '.join(valid_letters)}")

    if quit_early:
        break

    selected_index = ord(answer) - ord('A')
    if selected_index == correct_index:
        print("Correct!")
        score += 1
    else:
        correct_label = chr(65 + correct_index)
        correct_text = shuffled_choices[correct_index]
        print(f"Incorrect! The correct answer is {correct_label}) {correct_text}")

print("Your total score is:", score, "out of", len(questions))