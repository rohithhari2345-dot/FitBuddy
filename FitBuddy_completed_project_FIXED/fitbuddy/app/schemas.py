from pydantic import BaseModel, Field, field_validator


class UserInput(BaseModel):
    username: str = Field(min_length=2, max_length=100)
    user_id: str = Field(min_length=1, max_length=100)
    age: int = Field(ge=18, le=100)
    weight: float = Field(gt=0, lt=500)
    goal: str = Field(min_length=2, max_length=100)
    intensity: str = Field(pattern=r"^(low|moderate|high)$")

    @field_validator("username", "user_id", "goal")
    @classmethod
    def clean_text(cls, value: str) -> str:
        return " ".join(value.strip().split())


class FeedbackRequest(BaseModel):
    record_id: int = Field(gt=0)
    feedback: str = Field(min_length=3, max_length=2000)
