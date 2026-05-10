from pydantic import BaseModel


class AIModelResponse(BaseModel):
    provider: str
    model_name: str
    title: str
    cost_credits: int
    reference_cost_credits: int
    max_input_assets: int