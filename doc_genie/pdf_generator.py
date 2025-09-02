#!/usr/bin/env python3
"""
PDF Generator for GitHub Codebase Analyzer
==========================================

This module provides PDF generation capabilities for converting the analysis
results from Markdown to professional PDF documents.
"""

import os
import markdown2
from pathlib import Path
from datetime import datetime
from typing import Dict, List, Optional, Any

try:
    from reportlab.lib.pagesizes import letter, A4
    from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
    from reportlab.lib.units import inch
    from reportlab.lib.colors import HexColor, black, blue, grey
    from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, PageBreak
    from reportlab.platypus import Table, TableStyle, Image
    from reportlab.lib.enums import TA_CENTER, TA_LEFT, TA_RIGHT, TA_JUSTIFY
    from reportlab.pdfgen import canvas
    REPORTLAB_AVAILABLE = True
except ImportError:
    REPORTLAB_AVAILABLE = False
    print("⚠️ reportlab not available. Install with: pip install reportlab")

# Alternative PDF generation with WeasyPrint (imported when needed)
WEASYPRINT_AVAILABLE = False  # Determined dynamically when needed

class PDFGenerator:
    """Generate PDF documents from markdown content"""
    
    def __init__(self, output_dir: str = "output"):
        self.output_dir = Path(output_dir)
        self.pdf_dir = self.output_dir / "pdf"
        self.pdf_dir.mkdir(exist_ok=True)
        
        # Initialize styles if reportlab is available
        if REPORTLAB_AVAILABLE:
            self.styles = getSampleStyleSheet()
            self._setup_custom_styles()
    
    def _setup_custom_styles(self):
        """Setup custom PDF styles"""
        
        # Title style
        self.styles.add(ParagraphStyle(
            name='CustomTitle',
            parent=self.styles['Title'],
            fontSize=24,
            spaceAfter=30,
            textColor=HexColor('#2E86AB'),
            alignment=TA_CENTER
        ))
        
        # Heading 1 style
        self.styles.add(ParagraphStyle(
            name='CustomHeading1',
            parent=self.styles['Heading1'],
            fontSize=18,
            spaceAfter=12,
            spaceBefore=20,
            textColor=HexColor('#A23B72'),
            borderWidth=0,
            borderColor=HexColor('#A23B72'),
            borderPadding=2
        ))
        
        # Heading 2 style
        self.styles.add(ParagraphStyle(
            name='CustomHeading2',
            parent=self.styles['Heading2'],
            fontSize=14,
            spaceAfter=10,
            spaceBefore=15,
            textColor=HexColor('#F18F01')
        ))
        
        # Code style
        self.styles.add(ParagraphStyle(
            name='CustomCode',
            parent=self.styles['Code'],
            fontSize=10,
            fontName='Courier',
            backgroundColor=HexColor('#F5F5F5'),
            borderWidth=1,
            borderColor=HexColor('#CCCCCC'),
            borderPadding=8,
            leftIndent=20,
            rightIndent=20
        ))
        
        # Body text style
        self.styles.add(ParagraphStyle(
            name='CustomBody',
            parent=self.styles['Normal'],
            fontSize=11,
            spaceAfter=6,
            alignment=TA_JUSTIFY,
            textColor=HexColor('#333333')
        ))
        
        # List style
        self.styles.add(ParagraphStyle(
            name='CustomList',
            parent=self.styles['Normal'],
            fontSize=11,
            leftIndent=20,
            bulletIndent=10,
            spaceAfter=4
        ))
    
    def generate_all_pdfs(self, repo_name: str = "Repository") -> None:
        """Generate PDF versions of all documentation"""
        
        if not REPORTLAB_AVAILABLE:
            print("⚠️ PDF generation requires reportlab. Skipping PDF generation.")
            return
        
        print("📄 Generating PDF documentation...")
        
        # Generate individual PDFs
        self.generate_readme_pdf(repo_name)
        self.generate_technology_analysis_pdf(repo_name)
        self.generate_dependency_analysis_pdf(repo_name)
        self.generate_architecture_analysis_pdf(repo_name)
        self.generate_api_documentation_pdf(repo_name)
        
        # Generate combined PDF
        self.generate_combined_pdf(repo_name)
        
        print(f"✅ PDF documentation generated in '{self.pdf_dir}' directory")
    
    def generate_readme_pdf(self, repo_name: str) -> None:
        """Generate PDF from README.md"""
        
        readme_path = self.output_dir / "README.md"
        if not readme_path.exists():
            return
        
        with open(readme_path, 'r', encoding='utf-8') as f:
            content = f.read()
        
        pdf_path = self.pdf_dir / "README.pdf"
        self._create_pdf_from_markdown(content, pdf_path, f"{repo_name} - Project Documentation")
        print("✅ README.pdf generated")
    
    def generate_technology_analysis_pdf(self, repo_name: str) -> None:
        """Generate PDF from technology analysis"""
        
        tech_path = self.output_dir / "analysis" / "technology_analysis.md"
        if not tech_path.exists():
            return
        
        with open(tech_path, 'r', encoding='utf-8') as f:
            content = f.read()
        
        pdf_path = self.pdf_dir / "technology_analysis.pdf"
        self._create_pdf_from_markdown(content, pdf_path, f"{repo_name} - Technology Analysis")
        print("✅ technology_analysis.pdf generated")
    
    def generate_dependency_analysis_pdf(self, repo_name: str) -> None:
        """Generate PDF from dependency analysis"""
        
        dep_path = self.output_dir / "analysis" / "dependency_analysis.md"
        if not dep_path.exists():
            return
        
        with open(dep_path, 'r', encoding='utf-8') as f:
            content = f.read()
        
        pdf_path = self.pdf_dir / "dependency_analysis.pdf"
        self._create_pdf_from_markdown(content, pdf_path, f"{repo_name} - Dependency Analysis")
        print("✅ dependency_analysis.pdf generated")
    
    def generate_architecture_analysis_pdf(self, repo_name: str) -> None:
        """Generate PDF from architecture analysis"""
        
        arch_path = self.output_dir / "architecture" / "architecture_analysis.md"
        if not arch_path.exists():
            return
        
        with open(arch_path, 'r', encoding='utf-8') as f:
            content = f.read()
        
        pdf_path = self.pdf_dir / "architecture_analysis.pdf"
        self._create_pdf_from_markdown(content, pdf_path, f"{repo_name} - Architecture Analysis")
        print("✅ architecture_analysis.pdf generated")
    
    def generate_api_documentation_pdf(self, repo_name: str) -> None:
        """Generate PDF from API documentation"""
        
        api_path = self.output_dir / "api" / "api_specification.md"
        if not api_path.exists():
            return
        
        with open(api_path, 'r', encoding='utf-8') as f:
            content = f.read()
        
        pdf_path = self.pdf_dir / "api_documentation.pdf"
        self._create_pdf_from_markdown(content, pdf_path, f"{repo_name} - API Documentation")
        print("✅ api_documentation.pdf generated")
    
    def generate_combined_pdf(self, repo_name: str) -> None:
        """Generate a combined PDF with all documentation"""
        
        combined_content = f"""# {repo_name} - Complete Analysis Report

*Generated on {datetime.now().strftime("%Y-%m-%d %H:%M:%S")}*

---

"""
        
        # Combine all markdown files
        files_to_combine = [
            ("README.md", "Project Overview"),
            ("analysis/technology_analysis.md", "Technology Stack Analysis"),
            ("analysis/dependency_analysis.md", "Dependency Analysis"),
            ("architecture/architecture_analysis.md", "Architecture Documentation"),
            ("api/api_specification.md", "API Documentation")
        ]
        
        for file_path, section_title in files_to_combine:
            full_path = self.output_dir / file_path
            if full_path.exists():
                with open(full_path, 'r', encoding='utf-8') as f:
                    content = f.read()
                    # Remove the first header since we're adding our own
                    lines = content.split('\n')
                    if lines and lines[0].startswith('#'):
                        content = '\n'.join(lines[1:])
                    
                    combined_content += f"\n\n# {section_title}\n\n{content}\n\n---\n"
        
        pdf_path = self.pdf_dir / f"{repo_name}_complete_analysis.pdf"
        self._create_pdf_from_markdown(combined_content, pdf_path, f"{repo_name} - Complete Analysis Report")
        print(f"✅ {repo_name}_complete_analysis.pdf generated")
    
    def _create_pdf_from_markdown(self, markdown_content: str, output_path: Path, title: str) -> None:
        """Create PDF from markdown content using reportlab"""
        
        if not REPORTLAB_AVAILABLE:
            return
        
        try:
            # Create document
            doc = SimpleDocTemplate(
                str(output_path),
                pagesize=A4,
                rightMargin=72,
                leftMargin=72,
                topMargin=72,
                bottomMargin=18
            )
            
            # Parse markdown and convert to PDF elements
            story = []
            
            # Add title
            story.append(Paragraph(title, self.styles['CustomTitle']))
            story.append(Spacer(1, 20))
            
            # Process markdown content
            lines = markdown_content.split('\n')
            current_paragraph = []
            in_code_block = False
            code_block_lines = []
            
            for line in lines:
                line = line.rstrip()
                
                # Handle code blocks
                if line.startswith('```'):
                    if in_code_block:
                        # End code block
                        if code_block_lines:
                            code_text = '\n'.join(code_block_lines)
                            story.append(Paragraph(self._escape_html(code_text), self.styles['CustomCode']))
                            story.append(Spacer(1, 12))
                        code_block_lines = []
                        in_code_block = False
                    else:
                        # Start code block
                        if current_paragraph:
                            para_text = ' '.join(current_paragraph)
                            if para_text.strip():
                                story.append(Paragraph(self._process_markdown_line(para_text), self.styles['CustomBody']))
                                story.append(Spacer(1, 6))
                            current_paragraph = []
                        in_code_block = True
                    continue
                
                if in_code_block:
                    code_block_lines.append(line)
                    continue
                
                # Handle headers
                if line.startswith('#'):
                    # Add any pending paragraph
                    if current_paragraph:
                        para_text = ' '.join(current_paragraph)
                        if para_text.strip():
                            story.append(Paragraph(self._process_markdown_line(para_text), self.styles['CustomBody']))
                            story.append(Spacer(1, 6))
                        current_paragraph = []
                    
                    # Add header
                    level = len(line) - len(line.lstrip('#'))
                    header_text = line.lstrip('#').strip()
                    
                    if level == 1:
                        story.append(Spacer(1, 20))
                        story.append(Paragraph(header_text, self.styles['CustomHeading1']))
                        story.append(Spacer(1, 12))
                    elif level == 2:
                        story.append(Spacer(1, 15))
                        story.append(Paragraph(header_text, self.styles['CustomHeading2']))
                        story.append(Spacer(1, 8))
                    else:
                        story.append(Spacer(1, 10))
                        story.append(Paragraph(header_text, self.styles['CustomHeading2']))
                        story.append(Spacer(1, 6))
                    continue
                
                # Handle lists
                if line.startswith('- ') or line.startswith('* '):
                    # Add any pending paragraph
                    if current_paragraph:
                        para_text = ' '.join(current_paragraph)
                        if para_text.strip():
                            story.append(Paragraph(self._process_markdown_line(para_text), self.styles['CustomBody']))
                            story.append(Spacer(1, 6))
                        current_paragraph = []
                    
                    # Add list item
                    list_text = line[2:].strip()
                    story.append(Paragraph(f"• {self._process_markdown_line(list_text)}", self.styles['CustomList']))
                    continue
                
                # Handle empty lines
                if not line.strip():
                    if current_paragraph:
                        para_text = ' '.join(current_paragraph)
                        if para_text.strip():
                            story.append(Paragraph(self._process_markdown_line(para_text), self.styles['CustomBody']))
                            story.append(Spacer(1, 6))
                        current_paragraph = []
                    continue
                
                # Add to current paragraph
                current_paragraph.append(line)
            
            # Add any remaining paragraph
            if current_paragraph:
                para_text = ' '.join(current_paragraph)
                if para_text.strip():
                    story.append(Paragraph(self._process_markdown_line(para_text), self.styles['CustomBody']))
            
            # Add final code block if any
            if in_code_block and code_block_lines:
                code_text = '\n'.join(code_block_lines)
                story.append(Paragraph(self._escape_html(code_text), self.styles['CustomCode']))
            
            # Build PDF
            doc.build(story)
            
        except Exception as e:
            print(f"❌ Error generating PDF {output_path.name}: {e}")
    
    def _process_markdown_line(self, text: str) -> str:
        """Process markdown formatting in a line"""
        
        # Escape HTML
        text = self._escape_html(text)
        
        # Bold text
        text = self._replace_markdown_formatting(text, r'\*\*(.*?)\*\*', r'<b>\1</b>')
        text = self._replace_markdown_formatting(text, r'__(.*?)__', r'<b>\1</b>')
        
        # Italic text
        text = self._replace_markdown_formatting(text, r'\*(.*?)\*', r'<i>\1</i>')
        text = self._replace_markdown_formatting(text, r'_(.*?)_', r'<i>\1</i>')
        
        # Inline code
        text = self._replace_markdown_formatting(text, r'`(.*?)`', r'<font name="Courier" color="#333333">\1</font>')
        
        # Links
        text = self._replace_markdown_formatting(text, r'\[([^\]]+)\]\(([^)]+)\)', r'<link href="\2" color="blue">\1</link>')
        
        return text
    
    def _replace_markdown_formatting(self, text: str, pattern: str, replacement: str) -> str:
        """Replace markdown formatting with HTML tags"""
        import re
        return re.sub(pattern, replacement, text)
    
    def _escape_html(self, text: str) -> str:
        """Escape HTML characters"""
        return (text.replace('&', '&amp;')
                   .replace('<', '&lt;')
                   .replace('>', '&gt;')
                   .replace('"', '&quot;')
                   .replace("'", '&#x27;'))

class AlternativePDFGenerator:
    """Alternative PDF generator using weasyprint (HTML to PDF)"""
    
    def __init__(self, output_dir: str = "output"):
        self.output_dir = Path(output_dir)
        self.pdf_dir = self.output_dir / "pdf"
        self.pdf_dir.mkdir(exist_ok=True)
    
    def generate_all_pdfs(self, repo_name: str = "Repository") -> None:
        """Generate PDF versions using weasyprint"""
        
        try:
            import weasyprint
        except ImportError:
            print("⚠️ Alternative PDF generation requires weasyprint. Skipping.")
            return
        
        print("📄 Generating PDF documentation using weasyprint...")
        
        # CSS styles for PDF
        css_content = """
        <style>
        body {
            font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
            line-height: 1.6;
            color: #333;
            max-width: 800px;
            margin: 0 auto;
            padding: 20px;
        }
        h1 {
            color: #2E86AB;
            border-bottom: 3px solid #2E86AB;
            padding-bottom: 10px;
        }
        h2 {
            color: #A23B72;
            margin-top: 30px;
        }
        h3 {
            color: #F18F01;
        }
        code {
            background-color: #f4f4f4;
            padding: 2px 4px;
            border-radius: 3px;
            font-family: 'Courier New', Courier, monospace;
        }
        pre {
            background-color: #f4f4f4;
            padding: 15px;
            border-radius: 5px;
            border-left: 4px solid #2E86AB;
            overflow-x: auto;
        }
        ul, ol {
            margin-left: 20px;
        }
        table {
            border-collapse: collapse;
            width: 100%;
            margin: 20px 0;
        }
        th, td {
            border: 1px solid #ddd;
            padding: 8px;
            text-align: left;
        }
        th {
            background-color: #f2f2f2;
        }
        @page {
            margin: 1in;
            @top-center {
                content: "GitHub Codebase Analysis Report";
            }
            @bottom-center {
                content: counter(page);
            }
        }
        </style>
        """
        
        # Generate individual PDFs
        files_to_convert = [
            ("README.md", "README.pdf"),
            ("analysis/technology_analysis.md", "technology_analysis.pdf"),
            ("analysis/dependency_analysis.md", "dependency_analysis.pdf"),
            ("architecture/architecture_analysis.md", "architecture_analysis.pdf"),
            ("api/api_specification.md", "api_documentation.pdf")
        ]
        
        for md_file, pdf_file in files_to_convert:
            md_path = self.output_dir / md_file
            if md_path.exists():
                self._convert_markdown_to_pdf(md_path, self.pdf_dir / pdf_file, css_content)
        
        print(f"✅ Alternative PDF documentation generated in '{self.pdf_dir}' directory")
    
    def _convert_markdown_to_pdf(self, md_path: Path, pdf_path: Path, css_content: str) -> None:
        """Convert markdown file to PDF using weasyprint"""
        
        try:
            import weasyprint
            
            # Read markdown content
            with open(md_path, 'r', encoding='utf-8') as f:
                md_content = f.read()
            
            # Convert markdown to HTML
            html_content = markdown2.markdown(md_content, extras=['fenced-code-blocks', 'tables'])
            
            # Create complete HTML document
            full_html = f"""
            <!DOCTYPE html>
            <html>
            <head>
                <meta charset="UTF-8">
                <title>{md_path.stem}</title>
                {css_content}
            </head>
            <body>
                {html_content}
            </body>
            </html>
            """
            
            # Generate PDF
            weasyprint.HTML(string=full_html).write_pdf(str(pdf_path))
            print(f"✅ {pdf_path.name} generated using weasyprint")
            
        except ImportError:
            print(f"❌ WeasyPrint not available for PDF generation")
        except Exception as e:
            print(f"❌ Error generating PDF {pdf_path.name} with weasyprint: {e}")

def test_pdf_generation():
    """Test PDF generation capabilities"""
    
    print("Testing PDF Generation")
    print("======================")
    
    if REPORTLAB_AVAILABLE:
        print("✅ ReportLab available - Primary PDF generator ready")
    else:
        print("❌ ReportLab not available - Install with: pip install reportlab")
    
    if WEASYPRINT_AVAILABLE:
        print("✅ WeasyPrint available - Alternative PDF generator ready")
    else:
        print("❌ WeasyPrint not available - Install with: pip install weasyprint")
    
    if not REPORTLAB_AVAILABLE and not WEASYPRINT_AVAILABLE:
        print("⚠️ No PDF generators available. Install reportlab or weasyprint.")
        return False
    
    return True

if __name__ == "__main__":
    test_pdf_generation()
