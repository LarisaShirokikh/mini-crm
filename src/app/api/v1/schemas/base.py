
from pydantic import BaseModel, ConfigDict


class BaseSchema(BaseModel):

    model_config = ConfigDict(
        from_attributes=True,
        populate_by_name=True,
    )


class PaginationParams(BaseModel):

    page: int = 1
    page_size: int = 20

    @property
    def skip(self) -> int:
        return (self.page - 1) * self.page_size

    @property
    def limit(self) -> int:
        return self.page_size


class PaginatedResponse(BaseSchema):

    total: int
    page: int
    page_size: int
    pages: int


class ErrorResponse(BaseModel):

    error: dict

    class Config:
        json_schema_extra = {
            "example": {
                "error": {
                    "code": "NOT_FOUND",
                    "message": "Resource not found",
                }
            }
        }