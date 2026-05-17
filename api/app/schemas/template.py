import json

from pydantic import BaseModel, Field, field_validator


class TemplateCreate(BaseModel):
    name: str = Field(..., min_length=1, max_length=100)
    category: str = Field(..., min_length=1, max_length=50)
    description: str = Field(default="", max_length=1000)
    cover_url: str = Field(default="", max_length=500)
    preview_url: str = Field(default="", max_length=500)
    prompt_template: str = Field(default="", max_length=5000)
    negative_prompt: str = Field(default="", max_length=2000)
    config: str = Field(default="{}", max_length=10000)
    sort_order: int = Field(default=0, ge=0)
    is_active: bool = True

    @field_validator("config")
    @classmethod
    def validate_config_json(cls, v: str) -> str:
        try:
            json.loads(v)
        except (json.JSONDecodeError, TypeError):
            raise ValueError("config 必须是合法的 JSON 字符串")
        return v


class TemplateUpdate(BaseModel):
    name: str | None = Field(default=None, min_length=1, max_length=100)
    category: str | None = Field(default=None, min_length=1, max_length=50)
    description: str | None = Field(default=None, max_length=1000)
    cover_url: str | None = Field(default=None, max_length=500)
    preview_url: str | None = Field(default=None, max_length=500)
    prompt_template: str | None = Field(default=None, max_length=5000)
    negative_prompt: str | None = Field(default=None, max_length=2000)
    config: str | None = Field(default=None, max_length=10000)
    sort_order: int | None = Field(default=None, ge=0)
    is_active: bool | None = None

    @field_validator("config")
    @classmethod
    def validate_config_json(cls, v: str | None) -> str | None:
        if v is None:
            return v
        try:
            json.loads(v)
        except (json.JSONDecodeError, TypeError):
            raise ValueError("config 必须是合法的 JSON 字符串")
        return v


class TemplateStatusUpdate(BaseModel):
    is_active: bool


class TemplateSortItem(BaseModel):
    id: int
    sort_order: int = Field(..., ge=0)


class TemplateSortUpdate(BaseModel):
    items: list[TemplateSortItem] = Field(..., max_length=200)
