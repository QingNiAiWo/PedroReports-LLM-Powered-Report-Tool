# domain/models/requests.py
from pydantic import BaseModel, Field, validator
from typing import List
from datetime import datetime

class AnalysisRequest(BaseModel):
    """Request model for data analysis"""
    questions: List[str] = Field(
        ..., 
        description="List of analysis questions",
        min_items=1
    )
    reportTitle: str = Field(
        default="Data Analysis Report",
        description="Title for the analysis report"
    )

    @validator('questions')
    def validate_questions(cls, v):
        if not all(q.strip() for q in v):
            raise ValueError("Questions cannot be empty strings")
        return v

class FileUploadResponse(BaseModel):
    """Response model for file upload"""
    status: str = Field(..., example="success")
    filename: str
    path: str

class AnalysisDetails(BaseModel):
    """Details of analysis results"""
    visualizations: List[str]
    descriptions: int
    pdf_path: str

class AnalysisResponse(BaseModel):
    """Response model for analysis results"""
    status: str = Field(..., example="success")
    message: str
    request_id: str = Field(
        ...,
        description="Unique identifier for the analysis request"
    )
    details: AnalysisDetails
    timestamp: datetime = Field(default_factory=datetime.now)