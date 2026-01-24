
# Grade 4 Math Quiz
#
# Instructions:
# - Run from the workspace root:
#     python3 quizzes/math/grade-4-quiz-01.py [--no-shuffle] [--seed N]
# - The quiz runs interactively and will prompt for a single-letter answer (A, B, C, ...).
# - Invalid inputs are rejected and the script will re-prompt until a valid letter is entered.
# - Use `--seed N` to reproduce a particular shuffled order for testing.
# - Use `--no-shuffle` to disable shuffling of both questions and choices.

import random
import argparse

parser = argparse.ArgumentParser(description="Grade 4 math quiz")
parser.add_argument('--no-shuffle', action='store_true', help='Disable shuffling of questions and choices')
parser.add_argument('--seed', type=int, default=None, help='Optional RNG seed for reproducible shuffling')
args = parser.parse_args()

print("====================================================")
print(" Quiz: Math club — Grade 4 Quiz 01 ".center(52))
print("====================================================")

# If a seed is provided, use it for reproducible shuffling; otherwise do not set a seed
if args.seed is not None:
    random.seed(args.seed)

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
        answer = input(f"Enter your answer ({', '.join(valid_letters)}): ").strip().upper()
        if answer in valid_letters:
            break
        print(f"Please enter one of: {', '.join(valid_letters)}")

    selected_index = ord(answer) - ord('A')
    if selected_index == correct_index:
        print("Correct!")
        score += 1
    else:
        correct_label = chr(65 + correct_index)
        correct_text = shuffled_choices[correct_index]
        print(f"Incorrect! The correct answer is {correct_label}) {correct_text}")

print("Your total score is:", score, "out of", len(questions))