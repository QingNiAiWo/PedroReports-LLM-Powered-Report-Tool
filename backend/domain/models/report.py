# domain/models/report.py
from pydantic import BaseModel, Field
from typing import List
from datetime import datetime

class ReportMetadata(BaseModel):
    """Model for report metadata"""
    title: str
    generated_at: datetime = Field(default_factory=datetime.now)
    version: str = "1.0"
    author: str = "Data Analysis System"

class VisualizationInfo(BaseModel):
    """Model for visualization information"""
    file_name: str
    description: str
    type: str
    generated_at: datetime = Field(default_factory=datetime.now)

class ReportSection(BaseModel):
    """Model for report sections"""
    title: str
    content: str
    visualizations: List[VisualizationInfo] = []
    subsections: List['ReportSection'] = []

class Report(BaseModel):
    """Model for complete report"""
    metadata: ReportMetadata
    sections: List[ReportSection]
    summary: str
    keywords: List[str] = []