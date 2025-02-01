from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.enums import TA_CENTER, TA_JUSTIFY, TA_LEFT
from reportlab.lib.colors import HexColor

from core.logging.logger import get_logger
from domain.exceptions.custom import PDFGenerationError

logger = get_logger(__name__)

def get_custom_styles():
    """Generate custom styles for PDF report"""
    try:
        styles = getSampleStyleSheet()

        # Color scheme
        PRIMARY_COLOR = HexColor('#1F497D')    # Dark blue
        SECONDARY_COLOR = HexColor('#4F81BD')  # Medium blue
        TEXT_COLOR = HexColor('#2F2F2F')      # Dark gray
        ACCENT_COLOR = HexColor('#95B3D7')    # Light blue

        # Main Title Style
        styles.add(ParagraphStyle(
            name='CustomMainTitle',
            parent=styles['Heading1'],
            fontSize=28,
            spaceAfter=30,
            spaceBefore=30,
            textColor=PRIMARY_COLOR,
            alignment=TA_CENTER,
            leading=32
        ))

        # Chapter Title Style
        styles.add(ParagraphStyle(
            name='CustomChapterTitle',
            parent=styles['Heading1'],
            fontSize=20,
            spaceBefore=20,
            spaceAfter=20,
            textColor=PRIMARY_COLOR,
            leading=24,
            keepWithNext=True
        ))

        # Section Title Style
        styles.add(ParagraphStyle(
            name='CustomSectionTitle',
            parent=styles['Heading2'],
            fontSize=16,
            spaceBefore=15,
            spaceAfter=10,
            textColor=SECONDARY_COLOR,
            leading=20,
            keepWithNext=True
        ))

        # Subsection Title Style
        styles.add(ParagraphStyle(
            name='CustomSubsectionTitle',
            parent=styles['Heading3'],
            fontSize=14,
            spaceBefore=10,
            spaceAfter=8,
            textColor=SECONDARY_COLOR,
            leading=16,
            keepWithNext=True
        ))

        # Body Text Style
        styles.add(ParagraphStyle(
            name='CustomBodyText',
            parent=styles['Normal'],
            fontSize=11,
            textColor=TEXT_COLOR,
            alignment=TA_JUSTIFY,
            leading=16,
            spaceBefore=6,
            spaceAfter=6,
            firstLineIndent=0
        ))

        # TOC Entry Style
        styles.add(ParagraphStyle(
            name='CustomTOCEntry',
            parent=styles['Normal'],
            fontSize=11,
            textColor=TEXT_COLOR,
            leading=16,
            spaceAfter=6,
            firstLineIndent=0,
            alignment=TA_LEFT
        ))

        # TOC Level 2 Entry Style
        styles.add(ParagraphStyle(
            name='CustomTOCEntry2',
            parent=styles['CustomTOCEntry'],
            leftIndent=20,
            firstLineIndent=0
        ))

        # TOC Level 3 Entry Style
        styles.add(ParagraphStyle(
            name='CustomTOCEntry3',
            parent=styles['CustomTOCEntry'],
            leftIndent=40,
            firstLineIndent=0
        ))

        # Data Points Style
        styles.add(ParagraphStyle(
            name='CustomDataPoint',
            parent=styles['Normal'],
            fontSize=11,
            textColor=TEXT_COLOR,
            leading=16,
            leftIndent=30,
            spaceAfter=3,
            bulletIndent=15,
            fontName='Helvetica-Bold'
        ))

        # Calculation Style
        styles.add(ParagraphStyle(
            name='CustomCalculation',
            parent=styles['Normal'],
            fontSize=11,
            textColor=SECONDARY_COLOR,
            leading=16,
            leftIndent=45,
            spaceBefore=2,
            spaceAfter=2,
            fontName='Helvetica-Oblique'
        ))

        # Caption Style
        styles.add(ParagraphStyle(
            name='CustomCaption',
            parent=styles['Normal'],
            fontSize=10,
            textColor=SECONDARY_COLOR,
            alignment=TA_CENTER,
            leading=14,
            spaceBefore=6,
            spaceAfter=20
        ))

        # Header Style
        styles.add(ParagraphStyle(
            name='CustomHeader',
            parent=styles['Normal'],
            fontSize=9,
            textColor=PRIMARY_COLOR,
            alignment=TA_CENTER,
            leading=11
        ))

        # Executive Summary Style
        styles.add(ParagraphStyle(
            name='CustomExecutiveSummary',
            parent=styles['CustomBodyText'],
            spaceBefore=12,
            spaceAfter=12,
            leftIndent=20,
            rightIndent=20
        ))

        # Key Finding Style
        styles.add(ParagraphStyle(
            name='CustomKeyFinding',
            parent=styles['CustomBodyText'],
            leftIndent=20,
            bulletIndent=0,
            spaceBefore=6,
            spaceAfter=6
        ))

        # Conclusion Style
        styles.add(ParagraphStyle(
            name='CustomConclusion',
            parent=styles['CustomBodyText'],
            leftIndent=20,
            bulletIndent=0,
            spaceBefore=6,
            spaceAfter=6,
            textColor=SECONDARY_COLOR
        ))

        # Next Steps Style
        styles.add(ParagraphStyle(
            name='CustomNextSteps',
            parent=styles['CustomBodyText'],
            leftIndent=20,
            bulletIndent=0,
            spaceBefore=6,
            spaceAfter=6,
            textColor=SECONDARY_COLOR
        ))

        logger.info("Custom styles generated successfully")
        return styles
    except Exception as e:
        logger.error(f"Failed to generate custom styles: {str(e)}")
        raise PDFGenerationError(f"Style generation failed: {str(e)}")