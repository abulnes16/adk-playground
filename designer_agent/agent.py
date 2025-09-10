import os
from google.adk.agents import Agent
from google.genai import types
import warnings
import logging
import io
import re
from reportlab.lib.pagesizes import letter
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, PageBreak, Table, TableStyle
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import inch
from reportlab.pdfgen.canvas import Canvas
from reportlab.lib import colors
from reportlab.lib.enums import TA_LEFT, TA_CENTER, TA_JUSTIFY

# Load environment variables from .env file
from dotenv import load_dotenv
load_dotenv()

warnings.filterwarnings("ignore")
GOOGLE_API_KEY = os.environ["GOOGLE_API_KEY"]
GOOGLE_GENAI_USE_VERTEXAI=os.environ["GOOGLE_GENAI_USE_VERTEXAI"]
ROOT_AGENT_NAME = "adk_designer_agent"
logger = logging.getLogger(__name__)

PROPOSAL_DOCUMENT_FILE_NAME =  "proposal_document_for_user.pdf"
MODEL_NAME = "gemini-2.5-flash-lite"

'''
Tools Definition Starts:
'''

def store_pdf_local(
    pdf_text: str,
    file_path: str = PROPOSAL_DOCUMENT_FILE_NAME,
    margin_in: float = 0.75,        
    border_width: float = 1.0,      
    line_spacing: float = 1.25      
) -> str:
    """
    Genera un PDF local con soporte para markdown, márgenes configurables, borde por página y paginado automático.
    - pdf_text: texto en markdown a convertir a PDF
    - file_path: ruta de salida
    - margin_in: margen interno en pulgadas (controla el "tamaño" del marco)
    - border_width: grosor de la línea del borde en puntos
    - line_spacing: factor de interlineado para mejorar legibilidad
    """

    def parse_markdown_to_html(text: str) -> str:
        """Convierte markdown básico a HTML para ReportLab"""
        # Limpiar el texto
        text = text.replace("\r\n", "\n")
        
        # Convertir títulos
        text = re.sub(r'^# (.+)$', r'<para style="title1">\1</para>', text, flags=re.MULTILINE)
        text = re.sub(r'^## (.+)$', r'<para style="title2">\1</para>', text, flags=re.MULTILINE)
        text = re.sub(r'^### (.+)$', r'<para style="title3">\1</para>', text, flags=re.MULTILINE)
        text = re.sub(r'^#### (.+)$', r'<para style="title4">\1</para>', text, flags=re.MULTILINE)
        
        # Convertir negritas
        text = re.sub(r'\*\*(.+?)\*\*', r'<b>\1</b>', text)
        text = re.sub(r'__(.+?)__', r'<b>\1</b>', text)
        
        # Convertir cursivas
        text = re.sub(r'\*(.+?)\*', r'<i>\1</i>', text)
        text = re.sub(r'_(.+?)_', r'<i>\1</i>', text)
        
        # Convertir listas con viñetas
        lines = text.split('\n')
        in_list = False
        result_lines = []
        
        for line in lines:
            stripped = line.strip()
            if re.match(r'^[-*+]\s+', stripped):
                if not in_list:
                    result_lines.append('<ul>')
                    in_list = True
                item_text = re.sub(r'^[-*+]\s+', '', stripped)
                result_lines.append(f'<li>{item_text}</li>')
            elif re.match(r'^\d+\.\s+', stripped):
                if not in_list:
                    result_lines.append('<ol>')
                    in_list = True
                item_text = re.sub(r'^\d+\.\s+', '', stripped)
                result_lines.append(f'<li>{item_text}</li>')
            else:
                if in_list:
                    result_lines.append('</ul>' if 'ul>' in result_lines[-2] else '</ol>')
                    in_list = False
                result_lines.append(line)
        
        if in_list:
            result_lines.append('</ul>')
        
        text = '\n'.join(result_lines)
        
        # Convertir saltos de línea
        text = text.replace('\n', '<br/>')
        
        return text

    # Crear estilos personalizados
    styles = getSampleStyleSheet()
    
    # Estilo para títulos
    title1_style = ParagraphStyle(
        "title1",
        parent=styles["Heading1"],
        fontName="Helvetica-Bold",
        fontSize=18,
        spaceAfter=12,
        spaceBefore=12,
        textColor=colors.darkblue,
        alignment=TA_LEFT
    )
    
    title2_style = ParagraphStyle(
        "title2",
        parent=styles["Heading2"],
        fontName="Helvetica-Bold",
        fontSize=16,
        spaceAfter=10,
        spaceBefore=10,
        textColor=colors.darkblue,
        alignment=TA_LEFT
    )
    
    title3_style = ParagraphStyle(
        "title3",
        parent=styles["Heading3"],
        fontName="Helvetica-Bold",
        fontSize=14,
        spaceAfter=8,
        spaceBefore=8,
        textColor=colors.darkblue,
        alignment=TA_LEFT
    )
    
    title4_style = ParagraphStyle(
        "title4",
        parent=styles["Heading4"],
        fontName="Helvetica-Bold",
        fontSize=12,
        spaceAfter=6,
        spaceBefore=6,
        textColor=colors.darkblue,
        alignment=TA_LEFT
    )
    
    # Estilo para párrafos normales
    normal_style = ParagraphStyle(
        "Body",
        parent=styles["Normal"],
        fontName="Helvetica",
        fontSize=11,
        leading=int(11 * line_spacing),
        spaceAfter=6,
        alignment=TA_JUSTIFY
    )
    
    # Estilo para listas
    list_style = ParagraphStyle(
        "List",
        parent=styles["Normal"],
        fontName="Helvetica",
        fontSize=10,
        leading=int(10 * line_spacing),
        spaceAfter=3,
        leftIndent=20,
        bulletIndent=10
    )

    story = []
    
    # Convertir markdown a HTML
    html_content = parse_markdown_to_html(pdf_text)
    
    # Dividir en bloques por saltos de página
    blocks = html_content.split("\f")
    
    for i, block in enumerate(blocks):
        # Dividir en párrafos
        paragraphs = [p.strip() for p in block.split("<br/><br/>") if p.strip()]
        
        for para in paragraphs:
            if para.startswith('<para style="title1">'):
                content = para.replace('<para style="title1">', '').replace('</para>', '')
                story.append(Paragraph(content, title1_style))
            elif para.startswith('<para style="title2">'):
                content = para.replace('<para style="title2">', '').replace('</para>', '')
                story.append(Paragraph(content, title2_style))
            elif para.startswith('<para style="title3">'):
                content = para.replace('<para style="title3">', '').replace('</para>', '')
                story.append(Paragraph(content, title3_style))
            elif para.startswith('<para style="title4">'):
                content = para.replace('<para style="title4">', '').replace('</para>', '')
                story.append(Paragraph(content, title4_style))
            elif para.startswith('<ul>') or para.startswith('<ol>'):
                # Manejar listas
                list_items = re.findall(r'<li>(.*?)</li>', para)
                for item in list_items:
                    story.append(Paragraph(f"• {item}", list_style))
            else:
                # Párrafo normal
                story.append(Paragraph(para, normal_style))
            
            story.append(Spacer(1, 6))
        
        if i < len(blocks) - 1:
            story.append(PageBreak())

    PAGE_W, PAGE_H = letter
    margin = margin_in * inch

    def draw_border(canv: Canvas, doc):
        canv.saveState()
        canv.setLineWidth(border_width)
        canv.setStrokeColor(colors.darkblue)
        
        x = margin
        y = margin
        w = PAGE_W - 2 * margin
        h = PAGE_H - 2 * margin
        canv.rect(x, y, w, h) 
        canv.restoreState()

    doc = SimpleDocTemplate(
        file_path,
        pagesize=letter,
        leftMargin=margin,
        rightMargin=margin,
        topMargin=margin,
        bottomMargin=margin
    )
    
    doc.build(story, onFirstPage=draw_border, onLaterPages=draw_border)
    return f"PDF guardado en {file_path}"

'''
Tools Definition Ends
'''




# Proposal Agent Definition

root_agent = Agent(
   model=MODEL_NAME,
   name="proposal_agent",
   description="Agent that creates the Airbnb design proposal pdf for the customer based on a few details that the user provides about the design request.",
   instruction= f"""
   Act as an expert interior designer and veteran Airbnb Superhost. Your task is to generate a comprehensive, actionable, step-by-step plan to design, paint, and organize my Airbnb property based on the specific details provided at the end of this prompt.
Your response should include the following five sections:
High-Level Action Plan: A chronological, step-by-step plan from initial prep work to the final touches, outlining the most efficient order of operations (e.g., decluttering, painting, furniture assembly, decorating).
Design & Mood Board Concept: A detailed description of a specific design theme and vibe that will attract my target guest. Describe the key elements, textures, and feelings this design should evoke.
Paint & Color Palette: Recommend a specific and cohesive color palette. Please provide names of paint shades for the primary (main walls), secondary (accent walls), and trim colors that fit the recommended theme.
Room-by-Room Breakdown: For each room (Living Room, Bedroom(s), Kitchen, Bathroom), provide specific, practical suggestions for:
Furniture: Key pieces needed (e.g., "Queen-sized bed with an upholstered headboard," "round dining table to seat 4").
Decor: Ideas for wall art, lighting, rugs, and textiles (curtains, pillows) that will make the space feel inviting and memorable.
Organization: Smart storage solutions and organizational hacks to maximize space and ensure a clutter-free experience for guests.
Essential Amenities Checklist: A curated list of must-have amenities tailored specifically to my target guest, ensuring a 5-star experience.
Now, generate the full plan based on my specific property details.
   """,
   generate_content_config=types.GenerateContentConfig(temperature=0.2),
   tools=[store_pdf_local],
)