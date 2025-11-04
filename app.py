"""
Tender Clause Analyzer (OpenAI GPT Version - Highlighted Clauses)
-----------------------------------------------------------------
Generates a professional tender analysis report with clean formatting,
highlighted clause titles, light executive summary box, and logo header/footer.
"""

import streamlit as st
import PyPDF2
import docx
from openai import OpenAI
from io import BytesIO
from datetime import datetime
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.platypus import (
    SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, Image
)
from reportlab.lib.enums import TA_CENTER, TA_JUSTIFY, TA_LEFT
from reportlab.lib import colors
from reportlab.lib.units import inch
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
import re
import os
from dotenv import load_dotenv

# -----------------------------
# CONFIGURATION
# -----------------------------
load_dotenv()
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
client = OpenAI(api_key=OPENAI_API_KEY)
LOGO_PATH = "company_logo.png"

# Register clean professional font
try:
    pdfmetrics.registerFont(TTFont("Arial", "arial.ttf"))
    FONT_NAME = "Arial"
except:
    FONT_NAME = "Helvetica"

# -----------------------------
# CLAUSE TABLE
# -----------------------------
CLAUSE_TABLE = """
1. Scope of Work (SOW) Definition
2. Defect Liability Period (DLP) and Warranty
3. Payment Terms and Milestones
4. Liquidated Damages (LDs) / Limitation of Liability
5. Termination Clauses
6. Indemnity and Insurance
7. Governing Law and Dispute Resolution
8. Intellectual Property (IP) Rights
"""

# -----------------------------
# TEXT EXTRACTION
# -----------------------------
def extract_text_from_pdf(file):
    reader = PyPDF2.PdfReader(file)
    return "\n".join(page.extract_text() or "" for page in reader.pages)

def extract_text_from_docx(file):
    doc = docx.Document(file)
    return "\n".join(p.text for p in doc.paragraphs)

# -----------------------------
# GPT ANALYSIS
# -----------------------------
def analyze_tender_with_clauses(tender_text):
    prompt = f"""
You are a senior contracts lawyer preparing a professional tender analysis report.

For each clause below, write in formal English with this structure:

Clause Title: [title]
Findings: [what is stated in the tender]
Risk Level: [Low / Medium / High]
Action Advice: [short, practical recommendation]

At the end, include:
Executive Summary
Overall Risk Rating
Top 3 Concerns
Recommended Action (Proceed / Proceed with Caution / Avoid Bid)

No emojis, no markdown symbols.

TENDER TEXT:
{tender_text[:15000]}

CLAUSES TO REVIEW:
{CLAUSE_TABLE}
"""
    response = client.chat.completions.create(
        model="gpt-4.1-mini",
        messages=[{"role": "user", "content": prompt}],
        temperature=0.3,
        max_tokens=1800
    )
    return response.choices[0].message.content.strip()

# -----------------------------
# PDF GENERATION
# -----------------------------
def generate_pdf_report(tender_name, analysis_text, reviewer_comment):
    buffer = BytesIO()
    doc = SimpleDocTemplate(
        buffer, pagesize=A4,
        rightMargin=0.75*inch, leftMargin=0.75*inch,
        topMargin=1*inch, bottomMargin=0.75*inch
    )

    styles = getSampleStyleSheet()
    title = ParagraphStyle("Title", parent=styles["Heading1"], fontName=FONT_NAME,
                           fontSize=16, alignment=TA_CENTER, textColor=colors.HexColor("#0D47A1"))
    header = ParagraphStyle("Header", parent=styles["Heading2"], fontName=FONT_NAME,
                            fontSize=12, textColor=colors.HexColor("#0D47A1"))
    clause_title_style = ParagraphStyle("ClauseTitle", parent=styles["Heading3"], fontName=FONT_NAME,
                                        fontSize=11, textColor=colors.white,
                                        backColor=colors.HexColor("#1A237E"),
                                        spaceBefore=6, spaceAfter=4,
                                        leftIndent=2, alignment=TA_LEFT)
    body = ParagraphStyle("Body", parent=styles["BodyText"], fontName=FONT_NAME,
                          fontSize=10, alignment=TA_JUSTIFY, spaceAfter=6)

    story = []

    # Add logo
    try:
        img = Image(LOGO_PATH, width=1.2*inch, height=1.2*inch)
        img.hAlign = 'CENTER'
        story.append(img)
        story.append(Spacer(1, 0.2*inch))
    except Exception:
        pass

    # Title
    story.append(Paragraph("TENDER LEGAL REVIEW REPORT", title))
    story.append(Spacer(1, 0.15*inch))
    story.append(Paragraph(f"Tender: {tender_name}", body))
    story.append(Paragraph(f"Date: {datetime.now().strftime('%B %d, %Y')}", body))
    story.append(Spacer(1, 0.3*inch))

    # Split analysis and summary
    if "Executive Summary" in analysis_text:
        parts = analysis_text.split("Executive Summary")
        clause_text = parts[0]
        exec_summary = "Executive Summary" + parts[1] if len(parts) > 1 else ""
    else:
        clause_text, exec_summary = analysis_text, ""

    # Format clause sections
    story.append(Paragraph("Detailed Clause Analysis", header))
    story.append(Spacer(1, 0.1*inch))

    # Regex to detect clause titles
    clause_blocks = re.split(r"(?=Clause Title:)", clause_text)
    for block in clause_blocks:
        block = block.strip()
        if not block:
            continue

        # Extract title if present
        if block.startswith("Clause Title:"):
            title_line, _, remainder = block.partition("\n")
            story.append(Paragraph(title_line.strip(), clause_title_style))
            story.append(Paragraph(remainder.strip(), body))
        else:
            story.append(Paragraph(block, body))

    # Executive Summary Box
    if exec_summary.strip():
        story.append(Spacer(1, 0.25*inch))
        story.append(Paragraph("Executive Summary", header))
        clean_summary = exec_summary.strip().replace("**", "").replace("##", "")
        data = [[Paragraph(clean_summary, body)]]
        table = Table(data, colWidths=[6.0 * inch])
        table.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, -1), colors.whitesmoke),
            ('BOX', (0, 0), (-1, -1), 0.5, colors.grey),
            ('INNERPADDING', (0, 0), (-1, -1), 8),
        ]))
        story.append(table)

    # Reviewer Comments
    if reviewer_comment.strip():
        story.append(Spacer(1, 0.3*inch))
        story.append(Paragraph("Reviewer Comments", header))
        story.append(Paragraph(reviewer_comment.strip(), body))

    # Disclaimer
    story.append(Spacer(1, 0.4*inch))
    story.append(Paragraph(
        "Disclaimer: This AI-generated report is for internal use only. Verify all details before making legal or financial decisions.",
        body,
    ))

    # Footer
    def add_footer(canvas, doc):
        canvas.saveState()
        canvas.setFont(FONT_NAME, 8)
        footer_text = f"Generated by Tender Analyzer | {datetime.now().strftime('%d-%b-%Y %H:%M')}"
        canvas.drawCentredString(A4[0] / 2.0, 0.5 * inch, footer_text)
        canvas.restoreState()

    doc.build(story, onFirstPage=add_footer, onLaterPages=add_footer)
    buffer.seek(0)
    return buffer

# -----------------------------
# STREAMLIT UI
# -----------------------------
def main():
    st.set_page_config(page_title="Tender Clause Analyzer", page_icon="📑", layout="wide")
    st.title("Tender Clause Analyzer")
    st.caption("Upload a tender document and generate a formal, structured clause-based legal report.")

    file = st.file_uploader("Upload Tender Document", type=["pdf", "docx"])
    if not file:
        st.info("Please upload a tender document to begin.")
        st.stop()

    text = extract_text_from_pdf(file) if file.name.endswith(".pdf") else extract_text_from_docx(file)
    if not text:
        st.error("Could not extract text from file.")
        st.stop()

    st.success(f"Extracted {len(text):,} characters from {file.name}")

    if st.button("Analyze Tender", type="primary", use_container_width=True):
        with st.spinner("Analyzing tender using GPT-4.1-mini..."):
            analysis = analyze_tender_with_clauses(text)
        st.session_state.analysis = analysis
        st.session_state.tender_name = file.name
        st.session_state.done = True

    if st.session_state.get("done"):
        st.subheader("Tender Analysis Result")
        st.markdown(st.session_state.analysis)

        st.markdown("---")
        reviewer_comment = st.text_area("Reviewer Comments (optional):", placeholder="Add internal remarks or observations.")
        pdf_buf = generate_pdf_report(st.session_state.tender_name, st.session_state.analysis, reviewer_comment)

        st.download_button(
            "Download PDF Report",
            pdf_buf,
            file_name=f"tender_analysis_{datetime.now().strftime('%Y%m%d_%H%M')}.pdf",
            mime="application/pdf",
            use_container_width=True
        )

if __name__ == "__main__":
    main()
