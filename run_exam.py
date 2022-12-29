"""
run a bar exam questionnaire where we ask the model to:
1. rank order its top three choices
"""

# imports
import datetime
import json
import time
from pathlib import Path
from typing import Iterator

# packages
import pandas
import openai
import tqdm

# set the key
openai.api_key = (Path(__file__).parent / ".openai_key").read_text()


def generate_prompt(row: dict) -> str:
    """Generate a prompt from a row of the question spreadsheet."""
    question_text = row["question_prompt"]
    question_text = question_text[(question_text.find(". ") + 1) :].strip()
    prompt = f"""Please answer the following Bar Exam question in the following rank order format: 
First Choice: <LETTER>
Second Choice: <LETTER>
Third Choice: <LETTER>

Question: {question_text}
(A) {row["choice_a"].strip()}
(B) {row["choice_b"].strip()}
(C) {row["choice_c"].strip()}
(D) {row["choice_d"].strip()}\nAnswer: """.strip()

    return prompt


def get_parameter_sets() -> Iterator[dict]:
    """Generate a set of parameter sets."""
    for temperature in [0.0, 0.5, 1.0]:
        for max_tokens in [
            16,
        ]:
            for top_p in [1, 0.75]:
                for best_of in [1, 2, 4]:
                    for frequency_penalty in [
                        0,
                    ]:
                        for presence_penalty in [
                            0,
                        ]:
                            yield {
                                "temperature": temperature,
                                "max_tokens": max_tokens,
                                "top_p": top_p,
                                "best_of": best_of,
                                "frequency_penalty": frequency_penalty,
                                "presence_penalty": presence_penalty,
                            }


def get_next_session_path() -> Path:
    """Get the next session path."""
    session_number = 1

    while True:
        session_id = f"bar-exam-{session_number:03d}"
        session_path = Path(__file__).parent / "sessions-008"
        session_path.mkdir(exist_ok=True)
        session_path = session_path / session_id

        # skip if exists
        if session_path.exists():
            session_number += 1
            continue

        # otherwise continue
        session_path.mkdir(exist_ok=True)
        return session_path


def main():
    """
    run a bar exam session
    """

    # set samples per value
    num_samples_per_set = 3

    # iterate through parameter values
    for parameter_kwargs in get_parameter_sets():
        print(f"Running with parameters: {parameter_kwargs}")
        for sample_id in range(num_samples_per_set):
            # set up the session path iteratively
            session_path = get_next_session_path()

            # load the questions
            question_df = pandas.read_csv(
                Path(__file__).parent.parent / "data" / "questions.csv"
            )
            print(f"Loaded {len(question_df)} questions.")

            # generate the prompts
            exam_data = {
                "parameters": parameter_kwargs,
                "start_time": datetime.datetime.now().isoformat(),
                "questions": [],
            }
            for row_id, row in tqdm.tqdm(
                question_df.iterrows(), total=question_df.shape[0]
            ):
                question_exam_data = {
                    "question_input": row.to_dict(),
                    "model_prompt": generate_prompt(row.to_dict()),
                    "model_response": None,
                }

                try:
                    question_exam_data["model_response"] = openai.Completion.create(
                        model="text-davinci-003",
                        prompt=question_exam_data["model_prompt"],
                        **parameter_kwargs,
                    )
                    print(question_exam_data["model_response"]["choices"][0]["text"])
                except Exception as e:
                    # try once more inside the loop after a brief pause
                    print(
                        f"Error while submitting question {row['question_number']}: {e}"
                    )
                    print(f"Pausing and retrying...")
                    time.sleep(10)
                    try:
                        question_exam_data["model_response"] = openai.Completion.create(
                            model="text-davinci-003",
                            prompt=question_exam_data["model_prompt"],
                            **parameter_kwargs,
                        )
                        print(
                            question_exam_data["model_response"]["choices"][0]["text"]
                        )
                    except Exception as f:
                        print(
                            f"Second error while submitting question {row['question_number']}: {e}"
                        )
                        question_exam_data["model_response"] = None
                finally:
                    # log the current state of the exam
                    exam_data["questions"].append(question_exam_data)
                    with open(
                        session_path / "exam_data.json", "wt", encoding="utf-8"
                    ) as output_file:
                        json.dump(exam_data, output_file)
            # save final state
            exam_data["end_time"] = datetime.datetime.now().isoformat()
            with open(
                session_path / "exam_data.json", "wt", encoding="utf-8"
            ) as output_file:
                json.dump(exam_data, output_file)


if __name__ == "__main__":
    main()
