import instructor
from pydantic import BaseModel, Field, field_validator
from typing import List, Any, Optional
from app.utils import get_question_type, get_question_level, get_mark_distribution


class Option(BaseModel):
    id: str = Field(..., description="Letter identifier for the option")
    text: str = Field(..., description="Text content for the option")


class MultipleChoiceQuestion(BaseModel):
    question_text: str = Field(
        ..., min_length=1, description="The text of the multiple choice question."
    )
    options: List[Option] = Field(
        ..., min_length=2, description="A list of possible options."
    )
    correct_answer: str = Field(
        ..., description="The correct answer, which should be present in the options."
    )
    tags: List[str] = Field(
        ..., min_length=1, description="The topic tags associated with question."
    )

    @field_validator("correct_answer")
    def validate_correct_answer(cls, correct_answer, values):
        options = {choice.id for choice in values.data.get("options")}
        if correct_answer not in options:
            raise ValueError(f"correct_answer should be among {options}")

        return correct_answer


class MultipleSelectQuestion(BaseModel):
    question_text: str = Field(
        ...,
        min_length=1,
        description="The text of the multiple select question which can have 1 or more correct answers.",
    )
    options: List[Option] = Field(
        ..., min_length=2, description="A list of possible options."
    )
    correct_answer: List[str] = Field(
        ...,
        min_length=1,
        description="The list of correct answers, which should be present in the options.",
    )
    tags: List[str] = Field(
        ..., min_length=1, description="The topic tags associated with question."
    )

    @field_validator("correct_answer")
    def validate_correct_answers(cls, correct_answer, values):
        options = {choice.id for choice in values.data.get("options")}
        if not all(answer in options for answer in correct_answer):
            raise ValueError(f"correct_answer should be among {options}")

        return correct_answer


class NumericalAnswerQuestion(BaseModel):
    question_text: str = Field(
        ...,
        min_length=1,
        description="The text of the numerical answer type question which has a numeric answer.",
    )
    options: Optional[List[str]] = Field(
        ..., description="Placeholder for correct formatting. No inhererent use."
    )
    correct_answer: int = Field(..., description="The correct numeric answer.")
    tags: List[str] = Field(
        ..., min_length=1, description="The topic tags associated with question."
    )

    @field_validator("correct_answer")
    def validate_correct_answer(cls, correct_answer):
        if isinstance(correct_answer, (int)):
            return correct_answer

        raise ValueError(f"correct_answer should be a integer.")


def generate_quiz(
    course_name,
    course_level,
    course_objectives,
    title,
    description,
    difficulty_level,
    total_questions,
    total_marks,
):
    system_prompt = (
        "You generate objective exam questions strictly in JSON format."
        "Output ONLY JSON with a list of questions."
        f"The questions need to be generated for the course named {course_name} which is being offered at the {course_level} level."
        f"The title of the quiz set by teacher is {title}."
    )

    if course_objectives:
        system_prompt += f"The course objectives are as follows: <course_objective_start> {course_objectives} <course_objective_end>."

    if description:
        system_prompt += f"Additionally, the teacher has given this specific guidance to be kept in mind: <guidance start> {description} <guidance end>."

    generated_questions = []
    questions_list = []
    difficulty_list = []
    question_type_list = []

    client = instructor.from_provider("google/gemini-2.0-flash")

    for i in range(int(total_questions)):
        question_level = get_question_level(difficulty_level)
        question_type = get_question_type()

        if question_type == "mcq":
            prompt = (
                f"Generate 1 question of the difficulty level: {question_level}."
                "The question should be a multiple choice question with single correct answer."
                "The response should include: question_text, options, correct_answer and tags."
                "question_text is a string dictating the question."
                "options is a list of option, where each option has id and text. id should be of type A, B, C, D and so on. text includes the option text."
                "correct_answer should be a single option id letter for the correct answer which should be among the options."
                "tags is a list of strings that indicate the topic to which question belongs. Make the tags concise and general so that they can be aggregated later."
            )
            model = MultipleChoiceQuestion

        elif question_type == "msq":
            prompt = (
                f"Generate 1 question of the difficulty level: {question_level}."
                "The question should be a multiple select question with one or more correct answers."
                "The response should include: question_text, options, correct_answers and tags."
                "question_text is a string dictating the question."
                "options is a list of option, where each option has id and text. id should be of type A, B, C, D and so on. text includes the option text."
                "correct_answers should be a list of option id letters for the correct answers which should be among the options."
                "tags is a list of strings that indicate the topic to which question belongs. Make the tags concise and general so that they can be aggregated later."
            )
            model = MultipleSelectQuestion

        else:  # Numeric Type
            prompt = (
                f"Generate 1 question of the difficulty level: {question_level}."
                "The question should be a numeric answer type question with single correct answer."
                "The response should include: question_text, correct_answer and tags."
                "question_text is a string dictating the question."
                "correct_answer should strictly be an integer, no decimals allowed. Format the question accordingly."
                "tags is a list of strings that indicate the topic to which question belongs. Make the tags concise and general so that they can be aggregated later."
            )
            model = NumericalAnswerQuestion

        if generated_questions:
            prompt += f"The following questions are already generated. Don't repeat them. <questions start>"
            for i, j in enumerate(generated_questions):
                prompt += f"\nQuestion {i}: {j}."
            prompt += "<questions end>"

        response = client.chat.completions.create(
            response_model=model,
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": prompt},
            ],
        )

        questions_list.append(response.model_dump())
        difficulty_list.append(question_level)
        question_type_list.append(question_type)
        generated_questions.append(response.model_dump()["question_text"])

    question_marks_list = get_mark_distribution(difficulty_list, int(total_marks))

    result = []

    for i in range(int(total_questions)):
        question = questions_list[i]
        question["difficulty_level"] = difficulty_list[i]
        question["question_type"] = question_type_list[i]
        question["marks"] = question_marks_list[i]

        result.append(question)

    return result  # List of dictionaries
