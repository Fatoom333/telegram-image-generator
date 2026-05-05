from pydantic import BaseModel


class AIModelResponse(BaseModel):
    provider: str
    model_name: str
    title: str
    cost_credits: int
    image_cost_credits: int
    max_input_images: int