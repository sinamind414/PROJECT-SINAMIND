"""Schémas Pydantic pour le Bac Blanc immersif."""

from typing import List, Literal
from pydantic import BaseModel


class BacSubjectSummary(BaseModel):
    subject_number: int
    title_ar: str
    themes_ar: List[str] = []
    estimated_minutes: int = 120
    nb_exercises: int = 0


class BacExercise(BaseModel):
    exercise_id: str
    title_ar: str
    verb_slug: str = ""
    doc_ref: str = ""
    prompt_ar: str
    placeholder_ar: str = ""
    model_answer_ar: str = ""
    points: int = 5


class BacSubjectDetail(BaseModel):
    subject_number: int
    title_ar: str
    themes_ar: List[str] = []
    estimated_minutes: int = 120
    exercises: List[BacExercise] = []


class StartBacRequest(BaseModel):
    annale_slug: str


class StartBacResponse(BaseModel):
    session_id: str
    subjects: List[BacSubjectSummary] = []


class ChooseSubjectRequest(BaseModel):
    session_id: str
    subject_choice: Literal[1, 2]


class ChooseSubjectResponse(BaseModel):
    session_id: str
    subject: BacSubjectDetail
    time_limit_sec: int = 7200


class SaveAnswerRequest(BaseModel):
    session_id: str
    exercise_id: str
    question_id: str
    answer_text: str = ""
    skipped: bool = False


class SubmitBacRequest(BaseModel):
    session_id: str


class ExerciseScore(BaseModel):
    exercise_id: str
    title_ar: str
    score: int
    score_max: int
    percentage: int
    skipped: bool = False


class VerbScore(BaseModel):
    verb_slug: str
    score: int
    score_max: int
    percentage: int


class SubmitBacResponse(BaseModel):
    session_id: str
    score_global: int
    time_used_sec: int
    scores_by_exercise: List[ExerciseScore] = []
    scores_by_verb: List[VerbScore] = []
    exercises_skipped: int = 0
    debrief_message: str = ""


class CorrectionAnswer(BaseModel):
    exercise_id: str
    question_id: str
    title_ar: str
    verb_slug: str = ""
    student_answer: str = ""
    model_answer: str = ""
    score: int
    score_max: int
    percentage: int
    feedback: str = ""
    skipped: bool = False


class CorrectionResponse(BaseModel):
    session_id: str
    corrections: List[CorrectionAnswer] = []
