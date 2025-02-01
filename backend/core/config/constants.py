# core/config/constants.py
from enum import Enum

class Environment(str, Enum):
    """Application environment types"""
    DEVELOPMENT = "development"
    STAGING = "staging"
    PRODUCTION = "production"

class LogLevel(str, Enum):
    """Logging level options"""
    DEBUG = "DEBUG"
    INFO = "INFO"
    WARNING = "WARNING"
    ERROR = "ERROR"
    CRITICAL = "CRITICAL"

# Analysis Constants
ANALYSIS_CONSTANTS = {
    "CORRELATION_THRESHOLDS": {
        "VERY_WEAK": 0.2,
        "WEAK": 0.4,
        "MODERATE": 0.6,
        "STRONG": 0.8,
        "VERY_STRONG": 1.0
    },
    "SIGNIFICANCE_LEVEL": 0.05,
    "MIN_SAMPLE_SIZE": 30,
    "OUTLIER_THRESHOLD": 1.5
}

# PDF Generation Constants
PDF_CONSTANTS = {
    "PAGE_WIDTH": 595.27,  # A4 width in points
    "PAGE_HEIGHT": 841.89,  # A4 height in points
    "MARGIN": 72,  # 1 inch margins
    "MAX_IMAGE_WIDTH": 450,
    "FONT_SIZE": {
        "TITLE": 24,
        "HEADING": 18,
        "SUBHEADING": 14,
        "BODY": 11
    }
}