from pydantic import BaseModel


class EvaluateRequest(BaseModel):
    question_id: str
    reponse_eleve: str
    tentative: int = 1
    lang: str = "fr"
    include_methodology: bool = True
