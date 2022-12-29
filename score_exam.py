"""
read the exam session JSON output and output a CSV file with the question category, number,
selected choice, and explanation if available
"""

# imports
import datetime
import json
from pathlib import Path

# packages
import pandas
import tqdm


def load_answer_key(answer_key_path: Path) -> pandas.DataFrame:
    """
    load a copy of the answer key for comparison
    :param answer_key_path:
    :return:
    """
    answer_key_df = pandas.read_csv(answer_key_path, encoding="utf-8", low_memory=False)
    answer_key_df.columns = ["question_category", "question_number", "correct_answer"]
    return answer_key_df


def parse_gpt_response(response: str) -> dict:
    """parse teh gpt response like:
    Answer: (C)
    Backup Answer: (D)
    Explanation: The answer is C because ...

    to return

    {
        "answer": "C",
        "backup_answer": "D",
        "explanation": "The answer is C because ..."
    }
    """
    response_data = {
        "answer": None,
        "second_answer": None,
        "third_answer": None,
        "reason": None,
    }
    response_lines = response.strip().splitlines()

    for i, line in enumerate(response_lines):
        line = line.strip()

        if line.startswith("First Choice"):
            response_data["answer"] = (
                line.split()
                .pop()
                .replace("(", "")
                .replace(")", "")
                .replace(".", "")
                .strip()
            )
        elif line.startswith("Second Choice"):
            response_data["second_answer"] = (
                line.split()
                .pop()
                .replace("(", "")
                .replace(")", "")
                .replace(".", "")
                .strip()
            )
        elif line.startswith("Third Choice"):
            response_data["third_answer"] = (
                line.split()
                .pop()
                .replace("(", "")
                .replace(")", "")
                .replace(".", "")
                .strip()
            )

    return response_data


def get_complete_session_folders() -> list[Path]:
    """
    get a list of completed session folders
    :return:
    """
    session_path = Path(__file__).parent / "sessions-008"
    session_list = []
    for session_id in session_path.iterdir():
        if (session_id / "exam_data.json").exists():
            session_list.append(session_id)
    return sorted(session_list)


if __name__ == "__main__":
    # load the answer key
    answer_key_df = load_answer_key(
        Path(__file__).parent.parent / "data" / "answer_key_category.csv"
    )

    # get the list of completed sessions
    session_list = get_complete_session_folders()
    exam_session_output = []
    for session_path in tqdm.tqdm(session_list):
        session_name = session_path.name
        session_file = session_path / "exam_data.json"
        if not session_file.exists():
            raise ValueError("Session file does not exist")
        session_data = json.loads(session_file.read_text())

        # get parameters from the session data
        session_parameters = session_data["parameters"]
        try:
            session_duration = (
                datetime.datetime.fromisoformat(session_data["end_time"])
                - datetime.datetime.fromisoformat(session_data["start_time"])
            ).total_seconds()
        except:
            session_duration = None

        for question in session_data["questions"]:
            # get the correct answer first
            question_category = question["question_input"]["question_category"]
            question_number = question["question_input"]["question_number"]
            answer_key_match = answer_key_df.loc[
                (answer_key_df["question_category"] == question_category)
                & (answer_key_df["question_number"] == question_number)
            ]
            if answer_key_match.shape[0] > 1:
                raise ValueError(
                    f"Answer key match is not unique for category={question_category},"
                    f" number={question_number}"
                )
            elif answer_key_match.shape == 0:
                raise ValueError(
                    f"Answer key match is not found for category={question_category},"
                    f" number={question_number}"
                )
            correct_answer = answer_key_match["correct_answer"].values[0]

            if question["model_response"] is not None:
                # get the raw response
                if len(question["model_response"]["choices"]) != 1:
                    print(
                        f"category={question['category']}, number={question['number']} has more than one choice response."
                    )
                    continue

                # get the text and parse it
                response_text = question["model_response"]["choices"][0]["text"]
                question_response_data = parse_gpt_response(response_text)

                exam_session_output.append(
                    (
                        session_name,
                        question_category,
                        question_number,
                        question_response_data["answer"],
                        question_response_data["second_answer"],
                        question_response_data["third_answer"],
                        correct_answer,
                        # first, second, and third correct booleans
                        question_response_data["answer"] == correct_answer,
                        question_response_data["second_answer"] == correct_answer,
                        question_response_data["third_answer"] == correct_answer,
                        # top two correct
                        (question_response_data["answer"] == correct_answer)
                        or (question_response_data["second_answer"] == correct_answer),
                        # top three correct
                        (question_response_data["answer"] == correct_answer)
                        or (question_response_data["second_answer"] == correct_answer)
                        or (question_response_data["third_answer"] == correct_answer),
                        # add the parameters here
                        session_parameters["temperature"],
                        session_parameters["max_tokens"],
                        session_parameters["top_p"],
                        session_parameters["best_of"],
                        session_parameters["frequency_penalty"],
                        session_parameters["presence_penalty"],
                        session_duration,
                    )
                )
            else:
                exam_session_output.append(
                    (
                        session_name,
                        question["question_input"]["question_category"],
                        question["question_input"]["question_number"],
                        None,
                        None,
                        None,
                        correct_answer,
                        False,
                        False,
                        False,
                        False,
                        False,
                        session_parameters["temperature"],
                        session_parameters["max_tokens"],
                        session_parameters["top_p"],
                        session_parameters["best_of"],
                        session_parameters["frequency_penalty"],
                        session_parameters["presence_penalty"],
                        session_duration,
                    )
                )

    # save the exam session output
    exam_session_output_df = pandas.DataFrame(
        exam_session_output,
        columns=[
            "exam_session",
            "category",
            "number",
            "answer",
            "second_answer",
            "third_answer",
            "correct_answer",
            "first_correct",
            "second_correct",
            "third_correct",
            "top_two_correct",
            "top_three_correct",
            "temperature",
            "max_tokens",
            "top_p",
            "best_of",
            "frequency_penalty",
            "presence_penalty",
            "session_duration",
        ],
    )
    exam_session_output_df.to_csv(
        Path(__file__).parent / "all_exam_summary_008.csv", index=False
    )
