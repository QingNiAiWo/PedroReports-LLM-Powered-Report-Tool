# domain/models/analysis.py
from pydantic import BaseModel, Field
from typing import List, Optional, Dict, Any
from datetime import datetime

class StatisticalMeasure(BaseModel):
    """Model for statistical measurements"""
    name: str
    value: Any
    interpretation: Optional[str] = None

class DataPoint(BaseModel):
    """Model for data points in analysis"""
    metric: str
    value: Any
    significance: str

class Calculation(BaseModel):
    """Model for statistical calculations"""
    name: str
    value: Any
    interpretation: str

class KeyConclusion(BaseModel):
    """Model for analysis conclusions"""
    finding: str
    impact: str
    recommendation: str

class AnalysisSection(BaseModel):
    """Model for analysis sections"""
    title: Optional[str] = None
    heading: str
    content: str
    data_points: Optional[List[DataPoint]] = None
    calculations: Optional[List[Calculation]] = None
    key_conclusions: Optional[List[KeyConclusion]] = None
    limitations: Optional[List[str]] = None
    next_steps: Optional[List[str]] = None

class AnalysisOutput(BaseModel):
    """Model for complete analysis output"""
    graph_name: str
    question: str
    stats_file: str
    sections: List[AnalysisSection]
    timestamp: datetime = Field(default_factory=datetime.now)