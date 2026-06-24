from pydantic import BaseModel, Field


class SchemaEvalRequest(BaseModel):
    schema_id: str
    image_base64: str = Field(min_length=100)
