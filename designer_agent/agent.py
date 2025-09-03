import os
from google.adk.agents import Agent
from google.genai import types
import warnings
import logging
import io
from reportlab.lib.pagesizes import letter
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, PageBreak
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import inch
from reportlab.pdfgen.canvas import Canvas

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
    Genera un PDF local con márgenes configurables, borde por página y paginado automático.
    - pdf_text: texto a colocar (usa líneas en blanco para separar párrafos)
    - file_path: ruta de salida
    - margin_in: margen interno en pulgadas (controla el "tamaño" del marco)
    - border_width: grosor de la línea del borde en puntos
    - line_spacing: factor de interlineado para mejorar legibilidad
    """

    styles = getSampleStyleSheet()
    base = styles["Normal"]

    normal_style = ParagraphStyle(
        "Body",
        parent=base,
        fontName="Helvetica",
        fontSize=11,
        leading=int(11 * line_spacing),
        spaceAfter=6
    )


    story = []

    blocks = pdf_text.replace("\r\n", "\n").split("\f")
    for i, block in enumerate(blocks):

        for para in [p for p in block.split("\n\n") if p.strip()]:
            story.append(Paragraph(para.strip().replace("\n", "<br/>"), normal_style))
            story.append(Spacer(1, 6))
        if i < len(blocks) - 1:
            story.append(PageBreak())


    PAGE_W, PAGE_H = letter
    margin = margin_in * inch


    def draw_border(canv: Canvas, doc):
        canv.saveState()
        canv.setLineWidth(border_width)

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