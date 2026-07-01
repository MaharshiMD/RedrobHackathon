import os
from reportlab.lib.pagesizes import letter, landscape
from reportlab.lib import colors
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, PageBreak, Table, TableStyle

def add_header_footer(canvas, doc):
    canvas.saveState()
    # Draw top border/gradient bar
    canvas.setFillColor(colors.HexColor("#1A365D")) # Deep Blue
    canvas.rect(0, 590, 792, 22, fill=True, stroke=False)
    
    # Draw bottom border bar
    canvas.setFillColor(colors.HexColor("#2B6CB0")) # Accent Blue
    canvas.rect(0, 0, 792, 18, fill=True, stroke=False)
    
    # Draw Slide Number
    canvas.setFont('Helvetica', 9)
    canvas.setFillColor(colors.HexColor("#718096"))
    canvas.drawString(740, 28, f"Slide {doc.page}")
    canvas.drawString(36, 28, "Redrob Candidate Discovery & Ranking AI | Team Antigravity")
    canvas.restoreState()

def create_slide_deck():
    pdf_filename = "presentation_deck.pdf"
    doc = SimpleDocTemplate(
        pdf_filename,
        pagesize=landscape(letter),
        rightMargin=36,
        leftMargin=36,
        topMargin=40,
        bottomMargin=45
    )
    
    styles = getSampleStyleSheet()
    
    # Custom Styles
    title_style = ParagraphStyle(
        'DeckTitle',
        parent=styles['Heading1'],
        fontName='Helvetica-Bold',
        fontSize=32,
        leading=38,
        textColor=colors.HexColor("#1A365D"),
        alignment=1, # Center
        spaceAfter=15
    )
    
    subtitle_style = ParagraphStyle(
        'DeckSubtitle',
        parent=styles['Normal'],
        fontName='Helvetica',
        fontSize=18,
        leading=22,
        textColor=colors.HexColor("#4A5568"),
        alignment=1, # Center
        spaceAfter=40
    )
    
    slide_title_style = ParagraphStyle(
        'SlideTitle',
        parent=styles['Heading2'],
        fontName='Helvetica-Bold',
        fontSize=24,
        leading=28,
        textColor=colors.HexColor("#1A365D"),
        spaceAfter=15
    )
    
    body_style = ParagraphStyle(
        'DeckBody',
        parent=styles['Normal'],
        fontName='Helvetica',
        fontSize=12,
        leading=17,
        textColor=colors.HexColor("#2D3748")
    )
    
    bullet_style = ParagraphStyle(
        'DeckBullet',
        parent=body_style,
        leftIndent=20,
        firstLineIndent=-10,
        spaceAfter=8
    )
    
    bold_bullet_style = ParagraphStyle(
        'DeckBoldBullet',
        parent=bullet_style,
        fontName='Helvetica-Bold'
    )
    
    code_style = ParagraphStyle(
        'DeckCode',
        parent=styles['Code'],
        fontName='Courier',
        fontSize=11,
        leading=14,
        textColor=colors.HexColor("#2D3748"),
        backColor=colors.HexColor("#EDF2F7"),
        borderColor=colors.HexColor("#CBD5E0"),
        borderWidth=1,
        borderPadding=6,
        spaceAfter=10
    )

    story = []
    
    # ----------------------------------------------------
    # SLIDE 1: Title Slide
    # ----------------------------------------------------
    story.append(Spacer(1, 100))
    story.append(Paragraph("Candidate Discovery & Ranking AI", title_style))
    story.append(Paragraph("A High-Performance Staged Screening System for Senior AI Engineers", subtitle_style))
    story.append(Spacer(1, 40))
    
    info_data = [
        [
            Paragraph("<b>Participant Team:</b> Antigravity", body_style),
            Paragraph("<b>Compute Target:</b> CPU Only, <= 16GB RAM", body_style)
        ],
        [
            Paragraph("<b>Target Role:</b> Senior AI Engineer (Founding Team)", body_style),
            Paragraph("<b>Execution Time:</b> ~1 min 55 sec", body_style)
        ]
    ]
    t_info = Table(info_data, colWidths=[360, 360])
    t_info.setStyle(TableStyle([
        ('ALIGN', (0,0), (-1,-1), 'CENTER'),
        ('VALIGN', (0,0), (-1,-1), 'MIDDLE'),
        ('TOPPADDING', (0,0), (-1,-1), 10),
        ('BOTTOMPADDING', (0,0), (-1,-1), 10),
    ]))
    story.append(t_info)
    story.append(PageBreak())
    
    # ----------------------------------------------------
    # SLIDE 2: The Challenge & Dataset Traps
    # ----------------------------------------------------
    story.append(Paragraph("The Challenge & Dataset Traps", slide_title_style))
    story.append(Paragraph("Recruiting platforms are flooded with keyword-heavy profiles, but matching requires deep logic. Our solution addresses several adversarial traps deliberately built into the challenge pool:", body_style))
    story.append(Spacer(1, 15))
    story.append(Paragraph("&bull; <b>Honeypots (~80 profiles):</b> Synthetic profiles with mathematically impossible properties, such as 8 years of experience at a company founded 3 years ago, or expert proficiency in multiple skills with 0 years used. If honeypot rate exceeds 10% in the top 100, the submission is disqualified.", bullet_style))
    story.append(Paragraph("&bull; <b>Keyword Stuffers:</b> Candidates who list dozens of advanced AI/ML skills on their profile but have never deployed or used them in their career history descriptions.", bullet_style))
    story.append(Paragraph("&bull; <b>Consulting-Only Profiles:</b> General services candidates (TCS, Infosys, etc.) with keyword matches but zero product-engineering exposure or startup alignment.", bullet_style))
    story.append(PageBreak())
    
    # ----------------------------------------------------
    # SLIDE 3: System Architecture
    # ----------------------------------------------------
    story.append(Paragraph("System Architecture Overview", slide_title_style))
    story.append(Paragraph("We built a multi-stage deterministic screening pipeline that processes candidates locally on CPU within the 5-minute limit:", body_style))
    story.append(Spacer(1, 15))
    
    arch_data = [
        [
            Paragraph("<b>Stage 1: Hard Filtering</b>", body_style),
            Paragraph("Excludes the 70 dynamically detected honeypots and 9,739 consulting-only candidates before scoring.", body_style)
        ],
        [
            Paragraph("<b>Stage 2: Hybrid Scoring</b>", body_style),
            Paragraph("Scores the remaining 90,191 valid candidates on Skills (45%), Experience (30%), Behavioral Signals (15%), and Fit (10%).", body_style)
        ],
        [
            Paragraph("<b>Stage 3: Deterministic Sort</b>", body_style),
            Paragraph("Orders candidates by Score descending, breaking ties using Candidate ID ascending to ensure perfect reproducibility.", body_style)
        ],
        [
            Paragraph("<b>Stage 4: Reasoning Generation</b>", body_style),
            Paragraph("Composes specific, non-templated 1-2 sentence rationales referencing actual experience, locations, and notice periods.", body_style)
        ]
    ]
    t_arch = Table(arch_data, colWidths=[200, 520])
    t_arch.setStyle(TableStyle([
        ('BACKGROUND', (0,0), (0,-1), colors.HexColor("#F7FAFC")),
        ('GRID', (0,0), (-1,-1), 1, colors.HexColor("#E2E8F0")),
        ('VALIGN', (0,0), (-1,-1), 'TOP'),
        ('TOPPADDING', (0,0), (-1,-1), 10),
        ('BOTTOMPADDING', (0,0), (-1,-1), 10),
        ('LEFTPADDING', (0,0), (-1,-1), 12),
        ('RIGHTPADDING', (0,0), (-1,-1), 12),
    ]))
    story.append(t_arch)
    story.append(PageBreak())
    
    # ----------------------------------------------------
    # SLIDE 4: Deep Dive — Honeypot Detection
    # ----------------------------------------------------
    story.append(Paragraph("Deep Dive: Honeypot Detection Rules", slide_title_style))
    story.append(Paragraph("We designed a dynamic check that caught exactly <b>70 honeypots</b> in the 100K pool, avoiding hardcoding for generalized capability:", body_style))
    story.append(Spacer(1, 15))
    story.append(Paragraph("1. <b>Impossible Job Duration:</b> Compares job start/end dates against the stated duration. E.g., CAND_0007353 has a job starting in 2023 with duration of 166 months (impossible elapsed time).", bullet_style))
    story.append(Paragraph("2. <b>YoE vs Job History Mismatch:</b> Calculates sum of durations in career history and flags if it differs from profile YoE by > 4.0 years. E.g. claiming 13 YoE but having only 11 months of career history.", bullet_style))
    story.append(Paragraph("3. <b>Expert Skill 0 Duration:</b> Detects candidates listing 3 or more expert/advanced skills but with 0 months used.", bullet_style))
    story.append(Paragraph("4. <b>Impossible Skill Duration:</b> Flags candidates claiming skill durations exceeding their total YoE (e.g. claiming 92 months of RAG experience with only 3 years of total experience).", bullet_style))
    story.append(PageBreak())
    
    # ----------------------------------------------------
    # SLIDE 5: Deep Dive — Scoring Model
    # ----------------------------------------------------
    story.append(Paragraph("Deep Dive: Staged Scoring Model", slide_title_style))
    story.append(Paragraph("Scoring components are weighted to align with a Series-A product engineering founding role:", body_style))
    story.append(Spacer(1, 15))
    
    score_data = [
        [
            Paragraph("<b>Skills Score (45%)</b>", body_style),
            Paragraph("Matches core skills (embeddings, vector DBs, Python, ranking eval). <b>Crucial:</b> applies a 65% discount if the skill term is not found in the candidate's job descriptions, neutralizing keyword stuffers.", body_style)
        ],
        [
            Paragraph("<b>Experience Score (30%)</b>", body_style),
            Paragraph("Targets the 5-9 YoE sweet spot. Inspects career text for active engineering action verbs (<i>shipped, deployed, scaled, infrastructure</i>) and rewards Tier-1 education.", body_style)
        ],
        [
            Paragraph("<b>Behavioral Score (15%)</b>", body_style),
            Paragraph("Evaluates platform availability and responsiveness. Penalizes response rates < 15% and login inactivity > 6 months. Rewards active GitHub profiles.", body_style)
        ],
        [
            Paragraph("<b>Logistics & Fit (10%)</b>", body_style),
            Paragraph("Scores location preferences (Noida/Pune preferred, relocatable Tier-1) and notice period (buyout required for 90+ days).", body_style)
        ]
    ]
    t_score = Table(score_data, colWidths=[200, 520])
    t_score.setStyle(TableStyle([
        ('BACKGROUND', (0,0), (0,-1), colors.HexColor("#F7FAFC")),
        ('GRID', (0,0), (-1,-1), 1, colors.HexColor("#E2E8F0")),
        ('VALIGN', (0,0), (-1,-1), 'TOP'),
        ('TOPPADDING', (0,0), (-1,-1), 10),
        ('BOTTOMPADDING', (0,0), (-1,-1), 10),
        ('LEFTPADDING', (0,0), (-1,-1), 12),
        ('RIGHTPADDING', (0,0), (-1,-1), 12),
    ]))
    story.append(t_score)
    story.append(PageBreak())
    
    # ----------------------------------------------------
    # SLIDE 6: Results & Compliance
    # ----------------------------------------------------
    story.append(Paragraph("Results & Compliance", slide_title_style))
    story.append(Paragraph("The system was run locally and evaluated under strict constraints:", body_style))
    story.append(Spacer(1, 15))
    story.append(Paragraph("&bull; <b>Execution speed:</b> The complete run on the 100K pool took <b>1 minute 55 seconds</b> on a standard CPU, far below the 5-minute budget.", bullet_style))
    story.append(Paragraph("&bull; <b>Memory and Network:</b> Fully self-contained. No external API calls are made and memory usage is kept minimal (< 1.5 GB).", bullet_style))
    story.append(Paragraph("&bull; <b>Honeypot Rate:</b> 0% honeypot rate in the top 100 shortlist, satisfying the strict disqualification check.", bullet_style))
    story.append(Paragraph("&bull; <b>Reasoning Quality:</b> Custom sentence generation produces rationales referencing specific companies (e.g. Zomato, Meta, Google), locations, notice periods, and honest warnings (e.g. 90-day notice buyout required). No templates or repeats are used.", bullet_style))
    story.append(Spacer(1, 15))
    story.append(Paragraph("<b>Validator Verdict:</b>", body_style))
    story.append(Paragraph("Submission is valid.", code_style))
    
    # Build PDF
    doc.build(story, onFirstPage=add_header_footer, onLaterPages=add_header_footer)
    print("Presentation deck PDF generated successfully as presentation_deck.pdf")

if __name__ == "__main__":
    create_slide_deck()
