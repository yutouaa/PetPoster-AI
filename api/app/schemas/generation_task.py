from pydantic import BaseModel, Field


class GenerationTaskCreate(BaseModel):
    template_id: int = Field(..., alias="templateId")
    user_id: str | None = Field(default=None, alias="userId")
    image_urls: list[str] = Field(..., min_length=1, max_length=5, alias="imageUrls")
