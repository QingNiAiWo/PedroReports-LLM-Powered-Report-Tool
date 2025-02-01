from datetime import datetime
from pathlib import Path
from typing import List, Dict, Optional
from reportlab.lib import colors
from reportlab.lib.pagesizes import A4
from reportlab.lib.units import inch
from reportlab.platypus import (
    SimpleDocTemplate, 
    Paragraph, 
    Spacer, 
    Image, 
    PageBreak
)
import json
from dataclasses import dataclass

from core.config.paths import path_config
from core.config.constants import PDF_CONSTANTS
from core.logging.logger import get_logger, log_execution
from domain.exceptions.custom import PDFGenerationError
from .pdf_styles import get_custom_styles

logger = get_logger(__name__)


@dataclass
class TOCEntry:
    """Table of Contents entry"""
    title: str
    level: int
    page_number: Optional[int] = None
    parent_id: Optional[str] = None

class DynamicTOC:
    """Dynamic Table of Contents handler"""
    def __init__(self):
        self.entries: List[TOCEntry] = []
        self._current_page: int = 1
        self._last_section_id: Optional[str] = None

    @property
    def current_page(self) -> int:
        """Get current page number"""
        return self._current_page

    def add_entry(self, title: str, level: int) -> None:
        """Add a new entry to the TOC"""
        entry = TOCEntry(
            title=title,
            level=level,
            page_number=self._current_page,
            parent_id=self._last_section_id if level > 1 else None
        )
        
        if level == 1:
            self._last_section_id = title
            
        self.entries.append(entry)

    def increment_page(self, count: int = 1) -> None:
        """Increment the current page count"""
        self._current_page += count

    def get_entries(self) -> List[TOCEntry]:
        """Get all TOC entries"""
        return self.entries

    def get_section_entries(self, section_id: str) -> List[TOCEntry]:
        """Get all entries for a specific section"""
        return [
            entry for entry in self.entries 
            if entry.parent_id == section_id
        ]

    def reset_page_count(self) -> None:
        """Reset the page counter"""
        self._current_page = 1

    def update_page_numbers(self, offset: int) -> None:
        """Update all page numbers by an offset"""
        for entry in self.entries:
            if entry.page_number is not None:
                entry.page_number += offset


class PDFGenerator:
    """PDF Report Generator"""
    
    def __init__(self):
        self.styles = get_custom_styles()
        self.toc = DynamicTOC()
        self.figures_list = []
        self.report_title = "Data Analysis Report"
    
    def create_header_footer(self, canvas, doc):
        """Create header and footer on each page"""
        canvas.saveState()
        # Header
        header_text = self.report_title
        canvas.setFont('Helvetica', 9)
        canvas.setFillColor(colors.HexColor('#1F497D'))
        canvas.drawString(PDF_CONSTANTS['MARGIN'], 
                         A4[1] - 40, 
                         header_text)
        canvas.line(PDF_CONSTANTS['MARGIN'], 
                   A4[1] - 45, 
                   A4[0] - PDF_CONSTANTS['MARGIN'], 
                   A4[1] - 45)
        
        # Footer
        footer_text = f"Page {doc.page}"
        canvas.drawString(A4[0]/2 - 20, 30, footer_text)
        canvas.line(PDF_CONSTANTS['MARGIN'], 
                   50, 
                   A4[0] - PDF_CONSTANTS['MARGIN'], 
                   50)
        canvas.restoreState()

    def create_cover_page(self) -> List:
        """Create the report cover page"""
        elements = []
        elements.append(Spacer(1, 2*inch))
        
        self.toc.add_entry("Cover", 1)
        
        elements.append(Paragraph(self.report_title, 
                                self.styles['CustomMainTitle']))
        elements.append(Spacer(1, inch))
        
        date_str = datetime.now().strftime("%B %d, %Y")
        elements.append(Paragraph(date_str, 
                                self.styles['CustomHeader']))
        elements.append(Spacer(1, 2*inch))
        elements.append(PageBreak())
        
        self.toc.increment_page()
        return elements

    def create_executive_summary(self, analysis_data: List[Dict]) -> List:
        """Create executive summary section"""
        elements = []
        
        self.toc.add_entry("Executive Summary", 1)
        elements.append(Paragraph("Executive Summary", 
                            self.styles['CustomChapterTitle']))
        
        # Overview Section
        self.toc.add_entry("Overview", 2)
        elements.append(Paragraph("Overview", 
                            self.styles['CustomSectionTitle']))
        
        overview = """This report presents a comprehensive analysis of the provided data, 
        highlighting key patterns, trends, and actionable insights derived from the analysis."""
        elements.append(Paragraph(overview, 
                                self.styles['CustomBodyText']))
        
        # Key Findings Section
        self.toc.add_entry("Key Findings", 2)
        elements.append(Paragraph("Key Findings", 
                            self.styles['CustomSectionTitle']))
        
        for data in analysis_data:
            content = data.get('content', {})
            for section in content.get('sections', []):
                if section.get('heading') == 'Analysis Overview':
                    elements.append(Paragraph(
                        f"• {section.get('content', '')}",
                        self.styles['CustomBodyText']
                    ))
        
        # Key Conclusions Section
        self.toc.add_entry("Key Conclusions", 2)
        elements.append(Paragraph("Key Conclusions", 
                            self.styles['CustomSectionTitle']))
        
        for data in analysis_data:
            content = data.get('content', {})
            for section in content.get('sections', []):
                if section.get('heading') == 'Conclusions and Recommendations':
                    for conclusion in section.get('key_conclusions', []):
                        elements.append(Paragraph(
                            f"• Finding: {conclusion.get('finding', '')}",
                            self.styles['CustomDataPoint']
                        ))
                        elements.append(Paragraph(
                            f"  Impact: {conclusion.get('impact', '')}",
                            self.styles['CustomBodyText']
                        ))
                        elements.append(Paragraph(
                            f"  Recommendation: {conclusion.get('recommendation', '')}",
                            self.styles['CustomBodyText']
                        ))
        
        elements.append(PageBreak())
        self.toc.increment_page()
        return elements

    def create_table_of_contents(self) -> List:
        """Create table of contents with all sections and subsections"""
        elements = []
        elements.append(Paragraph("Table of Contents", 
                                self.styles['CustomChapterTitle']))
        elements.append(Spacer(1, 0.2*inch))
        
        for entry in self.toc.get_entries():
            # Calculate indentation based on level
            indent = "  " * (entry.level - 1)
            title = f"{indent}{entry.title}"
            
            # Calculate dots based on level-specific spacing
            available_space = 60 - len(title)  # Adjust total width as needed
            dots = "." * max(available_space, 3)
            
            # Create TOC line with appropriate style based on level
            toc_line = f"{title}{dots}{entry.page_number}"
            
            # Select style based on level
            if entry.level == 1:
                style = self.styles['CustomTOCEntry']
            elif entry.level == 2:
                style = self.styles['CustomTOCEntry2']
            else:
                style = self.styles['CustomTOCEntry3']
            
            elements.append(Paragraph(toc_line, style))
        
        elements.append(PageBreak())
        self.toc.increment_page()
        return elements

    def create_conclusions(self, analysis_data: List[Dict]) -> List:
        """Create conclusions and next steps section"""
        elements = []
        
        self.toc.add_entry("Limitations & Next Steps", 1)
        elements.append(Paragraph("Limitations & Next Steps", 
                            self.styles['CustomChapterTitle']))
        
        # Collect unique limitations and next steps
        limitations = set()
        next_steps = set()
        
        for data in analysis_data:
            content = data.get('content', {})
            for section in content.get('sections', []):
                if section.get('heading') == 'Conclusions and Recommendations':
                    limitations.update(section.get('limitations', []))
                    next_steps.update(section.get('next_steps', []))
        
        # Add Limitations
        if limitations:
            self.toc.add_entry("Limitations", 2)
            elements.append(Paragraph("Limitations", 
                                    self.styles['CustomSectionTitle']))
            for limitation in limitations:
                elements.append(Paragraph(
                    f"• {limitation}",
                    self.styles['CustomBodyText']
                ))
            elements.append(Spacer(1, 0.1*inch))
        
        # Add Next Steps
        if next_steps:
            self.toc.add_entry("Next Steps", 2)
            elements.append(Paragraph("Next Steps", 
                                    self.styles['CustomSectionTitle']))
            for step in next_steps:
                elements.append(Paragraph(
                    f"• {step}",
                    self.styles['CustomBodyText']
                ))
        
        elements.append(PageBreak())
        return elements

    def _format_analysis_section(self, section: Dict) -> List:
        """Format a single analysis section"""
        elements = []
        
        # Add content
        if content := section.get('content'):
            elements.append(Paragraph(content, 
                                    self.styles['CustomBodyText']))
        
        # Add data points
        if data_points := section.get('data_points'):
            for point in data_points:
                point_text = f"• {point.get('metric')}: {point.get('value')} ({point.get('significance')})"
                elements.append(Paragraph(point_text, 
                                        self.styles['CustomDataPoint']))
        
        # Add calculations
        if calculations := section.get('calculations'):
            elements.append(Spacer(1, 0.1*inch))
            for calc in calculations:
                name = calc.get('name', '')
                value = calc.get('value', '')
                if name and value:
                    elements.append(Paragraph(
                        f"• {name}: {value}",
                        self.styles['CustomCalculation']
                    ))
                    if interpretation := calc.get('interpretation'):
                        elements.append(Paragraph(
                            f"  {interpretation}", 
                            self.styles['CustomBodyText']
                        ))
        
        # Add key conclusions if present
        if key_conclusions := section.get('key_conclusions'):
            for conclusion in key_conclusions:
                elements.append(Paragraph(
                    f"• Finding: {conclusion.get('finding', '')}",
                    self.styles['CustomKeyFinding']
                ))
                if impact := conclusion.get('impact'):
                    elements.append(Paragraph(
                        f"  Impact: {impact}",
                        self.styles['CustomBodyText']
                    ))
                if recommendation := conclusion.get('recommendation'):
                    elements.append(Paragraph(
                        f"  Recommendation: {recommendation}",
                        self.styles['CustomBodyText']
                    ))
        
        elements.append(Spacer(1, 0.2*inch))
        return elements

    def create_analysis_chapters(self, analysis_data: List[Dict]) -> List:
        """Create analysis chapters with visualizations"""
        elements = []
        
        for i, data in enumerate(analysis_data, 1):  
            content = data.get('content', {})
            title = content.get('sections', [{}])[0].get('title', 
                    content.get('question', f'Analysis {i}'))
            
            chapter_title = f"{i}. {self._format_title(title)}"
            self.toc.add_entry(chapter_title, 1)
            
            # Add chapter title
            elements.append(Paragraph(chapter_title, 
                                    self.styles['CustomChapterTitle']))
            
            # Add visualization if available
            graph_path = data.get('graph_path')
            if graph_path and Path(graph_path).exists():
                img = Image(graph_path, 
                        width=PDF_CONSTANTS['MAX_IMAGE_WIDTH'],
                        height=0.75*PDF_CONSTANTS['MAX_IMAGE_WIDTH'])
                elements.append(img)
                
                figure_title = f"Figure {i}: {self._format_title(title)}"  # Changed from i-1 to i
                elements.append(Paragraph(figure_title, 
                                        self.styles['CustomCaption']))
                self.figures_list.append({
                    'title': figure_title,
                    'page': self.toc.current_page
                })
            
            # Add sections with proper headings
            if sections := content.get('sections', []):
                for section in sections:
                    # Add section heading
                    if heading := section.get('heading'):
                        elements.append(Paragraph(
                            heading,
                            self.styles['CustomSectionTitle']
                        ))
                        self.toc.add_entry(heading, 2)
                    
                    # Add section content
                    elements.extend(self._format_analysis_section(section))
            
            elements.append(PageBreak())
            self.toc.increment_page()
        
        return elements

    def _format_title(self, text: str) -> str:
        """Format title text"""
        if not text:
            return "Untitled Analysis"
        return ' '.join(word.capitalize() 
                       for word in text.replace('_', ' ').split())

    def _load_analysis_data(self) -> List[Dict]:
        """Load and sort analysis data from JSON files"""
        analysis_data = []
        json_files = sorted(path_config.DESCRIPTION_DIR.glob('*_analysis.json'))
        
        for json_file in json_files:
            try:
                with open(json_file, 'r') as file:
                    analysis = json.load(file)
                
                graph_path = path_config.GRAPHS_DIR / json_file.stem.replace(
                    '_analysis', '.png'
                )
                
                analysis_data.append({
                    "content": analysis,
                    "graph_path": str(graph_path)
                })
            except Exception as e:
                logger.error(f"Error loading analysis file {json_file}: {str(e)}")
        
        return analysis_data

    @log_execution
    def generate_pdf(self, report_title: str = "Data Analysis Report") -> str:
        """Generate the complete PDF report"""
        try:
            self.report_title = report_title
            self.toc = DynamicTOC()
            
            # Generate output filename
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            output_path = path_config.OUTPUT_DIR / f"analysis_report_{timestamp}.pdf"
            
            # Initialize document
            doc = SimpleDocTemplate(
                str(output_path),
                pagesize=A4,
                rightMargin=PDF_CONSTANTS['MARGIN'],
                leftMargin=PDF_CONSTANTS['MARGIN'],
                topMargin=PDF_CONSTANTS['MARGIN'],
                bottomMargin=PDF_CONSTANTS['MARGIN']
            )
            
            # Load data and create all sections first to build TOC
            analysis_data = self._load_analysis_data()
            
            # Create sections without TOC first to gather all entries
            cover_page = self.create_cover_page()
            exec_summary = self.create_executive_summary(analysis_data)
            analysis_chapters = self.create_analysis_chapters(analysis_data)
            conclusions = self.create_conclusions(analysis_data)
            
            # Now create TOC with all gathered entries
            table_of_contents = self.create_table_of_contents()
            
            # Combine all content
            content = []
            content.extend(cover_page)
            content.extend(table_of_contents)
            content.extend(exec_summary)
            content.extend(analysis_chapters)
            content.extend(conclusions)
            
            # Build PDF
            doc.build(
                content,
                onFirstPage=self.create_header_footer,
                onLaterPages=self.create_header_footer
            )
            
            logger.info(f"Generated PDF: {output_path}")
            return str(output_path)
            
        except Exception as e:
            logger.error(f"Failed to generate PDF: {str(e)}")
            raise PDFGenerationError(str(e))

@log_execution
def generate_pdf(report_title: str = "Data Analysis Report") -> str:
    """Main function to generate PDF report"""
    try:
        generator = PDFGenerator()
        return generator.generate_pdf(report_title=report_title)
    except Exception as e:
        logger.error(f"PDF generation failed: {str(e)}")
        raise PDFGenerationError(str(e))