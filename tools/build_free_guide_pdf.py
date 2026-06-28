# -*- coding: utf-8 -*-
"""Build the downloadable pronunciation guide PDF."""

from __future__ import annotations

from html import escape
from pathlib import Path

from reportlab.graphics.barcode.qr import QrCodeWidget
from reportlab.graphics.shapes import Drawing
from reportlab.lib import colors
from reportlab.lib.enums import TA_CENTER, TA_LEFT
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import ParagraphStyle, getSampleStyleSheet
from reportlab.lib.units import mm
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
from reportlab.platypus import (
    Image,
    KeepTogether,
    PageBreak,
    Paragraph,
    SimpleDocTemplate,
    Spacer,
    Table,
    TableStyle,
)


ROOT = Path(__file__).resolve().parents[1]
OUTPUT = ROOT / "downloads" / "guia-pronunciacion-ingles-espanoles.pdf"
COVER_IMAGE = ROOT / "images" / "book-cover-600.png"

BASE_URL = "https://librodeingles.com"
GUIDE_URL = f"{BASE_URL}/articulos/guia-pronunciacion-ingles-espanoles.html"
BOOK_URL = "https://www.amazon.es/dp/B0DN6V5VDW"

TITLE = "Guía gratis de pronunciación en inglés para españoles"
SUBTITLE = "25 tips prácticos para sonar más claro sin borrar tu acento"
AUTHOR = "Javier Sanz"
BOOK_TITLE = "De FAK a Fluent"

BLUE = colors.HexColor("#1a4d86")
BLUE_DARK = colors.HexColor("#172b3a")
BLUE_SOFT = colors.HexColor("#eaf3ff")
RED = colors.HexColor("#b23a48")
GOLD = colors.HexColor("#f3c15f")
MUTED = colors.HexColor("#52616f")
LINE = colors.HexColor("#d9e4ee")
SURFACE_SOFT = colors.HexColor("#f7fafc")

PAGE_WIDTH, PAGE_HEIGHT = A4
MARGIN_X = 17 * mm
CONTENT_WIDTH = PAGE_WIDTH - (2 * MARGIN_X)


def register_fonts() -> tuple[str, str, str]:
    font_dir = Path("C:/Windows/Fonts")
    normal = font_dir / "arial.ttf"
    bold = font_dir / "arialbd.ttf"
    italic = font_dir / "ariali.ttf"

    if normal.exists() and bold.exists() and italic.exists():
        pdfmetrics.registerFont(TTFont("Arial", str(normal)))
        pdfmetrics.registerFont(TTFont("Arial-Bold", str(bold)))
        pdfmetrics.registerFont(TTFont("Arial-Italic", str(italic)))
        pdfmetrics.registerFontFamily(
            "Arial",
            normal="Arial",
            bold="Arial-Bold",
            italic="Arial-Italic",
            boldItalic="Arial-Bold",
        )
        return "Arial", "Arial-Bold", "Arial-Italic"

    return "Helvetica", "Helvetica-Bold", "Helvetica-Oblique"


FONT, FONT_BOLD, FONT_ITALIC = register_fonts()


def make_styles() -> dict[str, ParagraphStyle]:
    base = getSampleStyleSheet()
    return {
        "eyebrow": ParagraphStyle(
            "Eyebrow",
            parent=base["Normal"],
            fontName=FONT_BOLD,
            fontSize=8.5,
            leading=10,
            textColor=RED,
            uppercase=True,
            spaceAfter=6,
        ),
        "title": ParagraphStyle(
            "Title",
            parent=base["Title"],
            fontName=FONT_BOLD,
            fontSize=29,
            leading=33,
            textColor=BLUE_DARK,
            alignment=TA_LEFT,
            spaceAfter=12,
        ),
        "subtitle": ParagraphStyle(
            "Subtitle",
            parent=base["Normal"],
            fontName=FONT,
            fontSize=13.5,
            leading=19,
            textColor=MUTED,
            spaceAfter=18,
        ),
        "h1": ParagraphStyle(
            "Heading1",
            parent=base["Heading1"],
            fontName=FONT_BOLD,
            fontSize=18,
            leading=22,
            textColor=BLUE_DARK,
            spaceBefore=8,
            spaceAfter=10,
        ),
        "h2": ParagraphStyle(
            "Heading2",
            parent=base["Heading2"],
            fontName=FONT_BOLD,
            fontSize=13.5,
            leading=17,
            textColor=BLUE_DARK,
            spaceBefore=8,
            spaceAfter=6,
        ),
        "body": ParagraphStyle(
            "Body",
            parent=base["BodyText"],
            fontName=FONT,
            fontSize=10.1,
            leading=14.2,
            textColor=BLUE_DARK,
            spaceAfter=7,
        ),
        "small": ParagraphStyle(
            "Small",
            parent=base["BodyText"],
            fontName=FONT,
            fontSize=8.5,
            leading=11,
            textColor=MUTED,
            spaceAfter=4,
        ),
        "card": ParagraphStyle(
            "Card",
            parent=base["BodyText"],
            fontName=FONT,
            fontSize=8.8,
            leading=11.2,
            textColor=BLUE_DARK,
        ),
        "card_title": ParagraphStyle(
            "CardTitle",
            parent=base["BodyText"],
            fontName=FONT_BOLD,
            fontSize=9.4,
            leading=11.5,
            textColor=BLUE_DARK,
        ),
        "center": ParagraphStyle(
            "Center",
            parent=base["BodyText"],
            fontName=FONT,
            fontSize=9,
            leading=12,
            textColor=MUTED,
            alignment=TA_CENTER,
        ),
    }


STYLES = make_styles()


def para(text: str, style: str = "body") -> Paragraph:
    return Paragraph(text, STYLES[style])


def text(value: str) -> str:
    return escape(value, quote=False)


def link(label: str, url: str) -> str:
    return f'<a href="{escape(url, quote=True)}" color="#1a4d86">{text(label)}</a>'


def public_path(path: str) -> str:
    return f"{BASE_URL}{path}"


def short_path(path: str) -> str:
    return f"librodeingles.com{path}"


def qr_drawing(data: str, size: float = 31 * mm) -> Drawing:
    qr = QrCodeWidget(data)
    bounds = qr.getBounds()
    width = bounds[2] - bounds[0]
    height = bounds[3] - bounds[1]
    drawing = Drawing(size, size, transform=[size / width, 0, 0, size / height, 0, 0])
    drawing.add(qr)
    return drawing


def page_meta(canvas, _doc) -> None:
    canvas.setTitle(TITLE)
    canvas.setAuthor(AUTHOR)
    canvas.setSubject("Guía gratuita de pronunciación en inglés para españoles")
    canvas.setCreator("tools/build_free_guide_pdf.py")


def draw_footer(canvas, doc) -> None:
    page_meta(canvas, doc)
    canvas.saveState()
    canvas.setStrokeColor(LINE)
    canvas.setLineWidth(0.5)
    canvas.line(MARGIN_X, 14 * mm, PAGE_WIDTH - MARGIN_X, 14 * mm)
    canvas.setFillColor(MUTED)
    canvas.setFont(FONT, 7.6)
    canvas.drawString(MARGIN_X, 9 * mm, f"{BOOK_TITLE} | {AUTHOR}")
    canvas.drawRightString(PAGE_WIDTH - MARGIN_X, 9 * mm, f"Página {doc.page}")
    canvas.restoreState()


def audio_ref(path: str) -> str:
    return f'<br/><font size="7.6" color="#52616f">Audio: </font>{link(short_path(path), public_path(path))}'


TIPS = [
    (
        "La H no es una jota",
        "En hello o hard, expulsa aire suave, como si echaras vaho en una ventana. No lleves el sonido a la jota española.",
        "/audio/hello-hard.html",
    ),
    (
        "La V no debe convertirse en B",
        "Very necesita labio inferior y dientes superiores. Si suena como bery, pierdes una diferencia muy visible.",
        "/audio/very-good.html",
    ),
    (
        "La I corta no es una i española",
        "Bit, win y lip se acercan a una vocal relajada entre i y e. Evita que sit suene como seat.",
        "/audio/bit-big-win-lip-clip.html",
    ),
    (
        "Book y moon no comparten vocal",
        "Book tiene una vocal corta; moon es más larga. No pronuncies todas las dobles O como una u española.",
        "/audio/book-cook-look-foot-hook-took-cookie-correcto.html",
    ),
    (
        "Love no se lee con o española",
        "La vocal de love no es la de lobo. Compararla con move ayuda a notar que la ortografía engaña.",
        "/audio/love-clove-move.html",
    ),
    (
        "TH puede vibrar o no",
        "Think no vibra; they sí. Primero coloca la lengua entre los dientes, luego decide si añades voz.",
        "/audio/sonido-th-entre-dientes.html",
    ),
    (
        "No metas una e antes de S",
        "Spain no es espain. Empieza directamente en la S, aunque al principio te parezca brusco.",
        None,
    ),
    (
        "La R inglesa no se enrolla",
        "En red o right, no vibres la lengua como en perro. Recógela hacia atrás y evita el golpe español.",
        "/audio/red-car-around-right-sorry.html",
    ),
    (
        "La L final pesa más",
        "En feel, school o full, la L final no desaparece. Dale presencia sin añadir una vocal al final.",
        "/audio/skill-goal-ball-full-world-call-feel-school.html",
    ),
    (
        "La J inglesa no es nuestra Y",
        "Job, John y enjoy empiezan con un sonido más fuerte que una y española. Piensa en el inicio de la letra G en inglés.",
        "/audio/jump-john-job-jungle-enjoy.html",
    ),
    (
        "No pronuncies letras mudas",
        "Walk, talk, would y should esconden letras. Si lees todo lo escrito, la palabra se aleja del inglés real.",
        "/audio/walk-talk-half-calm-salmon-would-should-yolk-palm-chalk-walkie-talkie.html",
    ),
    (
        "OUGH no tiene una sola regla",
        "Though, through, tough y thought cambian mucho. Apréndelas por memoria auditiva, no por intuición visual.",
        "/audio/though-through-tough-cough-enough-bough-thought-plough.html",
    ),
    (
        "No todas las sílabas valen igual",
        "El inglés da más peso a palabras de contenido: nombres, verbos, adjetivos y adverbios. El español tiende a ser más plano.",
        None,
    ),
    (
        "Reduce palabras pequeñas",
        "To, of, and y for suelen sonar débiles dentro de una frase. Pronunciarlas todas con fuerza puede sonar artificial.",
        None,
    ),
    (
        "Going to se junta",
        "En conversación rápida, going to puede sonar como gonna. Reconocerlo mejora tu listening y tu fluidez.",
        "/audio/going-to.html",
    ),
    (
        "Want to también cambia",
        "I want to go no suele sonar palabra por palabra. Practica la frase completa, no solo want y to por separado.",
        "/audio/i-want-to-go-to-london.html",
    ),
    (
        "Give me puede sonar gimme",
        "No es hablar mal: es reconocer cómo se simplifican sonidos en conversaciones reales.",
        "/audio/give-me-that.html",
    ),
    (
        "Could have se comprime",
        "Could've, should've y would've no suenan como tres bloques. Ojo: no se escriben could of.",
        "/audio/could-have-should-have-would-have.html",
    ),
    (
        "Practica frases, no solo palabras",
        "Una palabra aislada puede salir bien; la prueba real es mantener el sonido dentro de una frase completa.",
        None,
    ),
    (
        "Usa respuestas reales",
        "Pretty good o doing well suenan más naturales que repetir siempre I am fine, thank you, and you?",
        "/audio/pretty-good.html",
    ),
    (
        "Grábate poco, pero a menudo",
        "Diez segundos al día bastan para detectar vocales españolas añadidas, sonidos finales perdidos o ritmo demasiado plano.",
        None,
    ),
    (
        "Exagera primero, suaviza después",
        "Para aprender un sonido nuevo, exagerarlo un poco ayuda a que la boca encuentre la posición. Después lo haces natural.",
        None,
    ),
    (
        "Imita el tono, no solo el sonido",
        "Copiar la melodía de una frase puede mejorar tu claridad más que repetir una palabra veinte veces.",
        None,
    ),
    (
        "No tengas vergüenza de sonar inglés",
        "Pronunciar mejor no es postureo. Es facilitar que te entiendan en una reunión, entrevista o conversación real.",
        None,
    ),
    (
        "Repite menos cosas, mejor",
        "Elige cinco audios útiles y repítelos muchos días. La constancia gana a la acumulación.",
        "/audios.html",
    ),
]


PRACTICE_PLAN = [
    ("Día 1", "H inicial", "/audio/hello-hard.html"),
    ("Día 2", "I corta: bit, big, win, lip, clip", "/audio/bit-big-win-lip-clip.html"),
    ("Día 3", "TH con y sin voz", "/articulos/sonido-th-ingles.html"),
    ("Día 4", "Letras mudas: walk, talk, would, should", "/articulos/letras-mudas-ingles.html"),
    ("Día 5", "OUGH: though, through, tough, thought", "/articulos/palabras-ough-pronunciacion-ingles.html"),
    ("Día 6", "Linking: gonna, wanna, gotta, lemme", "/articulos/ligar-palabras-ingles.html"),
    ("Día 7", "Mini conversación: How's it going? Pretty good.", "/audio/hows-it-going.html"),
]


def card(number: int, title: str, body: str, path: str | None) -> Paragraph:
    content = (
        f'<b><font color="#172b3a">{number}. {text(title)}</font></b><br/>'
        f'{text(body)}'
    )
    if path:
        content += audio_ref(path)
    return para(content, "card")


def add_tip_cards(story: list, tips: list[tuple[str, str, str | None]]) -> None:
    col_gap = 8 * mm
    col_width = (CONTENT_WIDTH - col_gap) / 2
    for i in range(0, len(tips), 2):
        left = card(i + 1, *tips[i])
        if i + 1 < len(tips):
            right = card(i + 2, *tips[i + 1])
            table = Table([[left, right]], colWidths=[col_width, col_width], hAlign="LEFT")
            style = [
                ("VALIGN", (0, 0), (-1, -1), "TOP"),
                ("BACKGROUND", (0, 0), (-1, -1), colors.white),
                ("BOX", (0, 0), (-1, -1), 0.6, LINE),
                ("LINEBEFORE", (0, 0), (-1, -1), 3, GOLD),
                ("LEFTPADDING", (0, 0), (-1, -1), 9),
                ("RIGHTPADDING", (0, 0), (-1, -1), 8),
                ("TOPPADDING", (0, 0), (-1, -1), 8),
                ("BOTTOMPADDING", (0, 0), (-1, -1), 8),
            ]
        else:
            table = Table([[left]], colWidths=[CONTENT_WIDTH], hAlign="LEFT")
            style = [
                ("VALIGN", (0, 0), (-1, -1), "TOP"),
                ("BACKGROUND", (0, 0), (-1, -1), colors.white),
                ("BOX", (0, 0), (-1, -1), 0.6, LINE),
                ("LINEBEFORE", (0, 0), (-1, -1), 3, GOLD),
                ("LEFTPADDING", (0, 0), (-1, -1), 9),
                ("RIGHTPADDING", (0, 0), (-1, -1), 8),
                ("TOPPADDING", (0, 0), (-1, -1), 8),
                ("BOTTOMPADDING", (0, 0), (-1, -1), 8),
            ]
        table.setStyle(TableStyle(style))
        story.append(KeepTogether([table, Spacer(1, 5)]))


def plan_table() -> Table:
    rows = [[para("<b>Día</b>", "small"), para("<b>Práctica</b>", "small"), para("<b>Enlace</b>", "small")]]
    for day, practice, path in PRACTICE_PLAN:
        rows.append([
            para(text(day), "small"),
            para(text(practice), "small"),
            para(link(short_path(path), public_path(path)), "small"),
        ])
    table = Table(rows, colWidths=[34 * mm, 73 * mm, CONTENT_WIDTH - 107 * mm], hAlign="LEFT")
    table.setStyle(TableStyle([
        ("BACKGROUND", (0, 0), (-1, 0), BLUE_SOFT),
        ("TEXTCOLOR", (0, 0), (-1, 0), BLUE_DARK),
        ("FONTNAME", (0, 0), (-1, 0), FONT_BOLD),
        ("GRID", (0, 0), (-1, -1), 0.45, LINE),
        ("VALIGN", (0, 0), (-1, -1), "TOP"),
        ("LEFTPADDING", (0, 0), (-1, -1), 7),
        ("RIGHTPADDING", (0, 0), (-1, -1), 7),
        ("TOPPADDING", (0, 0), (-1, -1), 6),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 6),
    ]))
    return table


def cover_block() -> list:
    cover = Image(str(COVER_IMAGE), width=72 * mm, height=44.5 * mm)
    qr = qr_drawing(GUIDE_URL, 31 * mm)
    qr_caption = para(
        f"<b>Abrir guía online y audios</b><br/>{link('librodeingles.com', BASE_URL)}",
        "center",
    )
    qr_box = Table([[qr], [qr_caption]], colWidths=[43 * mm], hAlign="CENTER")
    qr_box.setStyle(TableStyle([
        ("ALIGN", (0, 0), (-1, -1), "CENTER"),
        ("VALIGN", (0, 0), (-1, -1), "MIDDLE"),
        ("BOX", (0, 0), (-1, -1), 0.6, LINE),
        ("BACKGROUND", (0, 0), (-1, -1), SURFACE_SOFT),
        ("TOPPADDING", (0, 0), (-1, -1), 8),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 8),
    ]))

    intro = [
        para("RECURSO GRATIS", "eyebrow"),
        para(TITLE, "title"),
        para(SUBTITLE, "subtitle"),
        para(
            "Una checklist rápida para españoles que ya estudian inglés, pero quieren sonar más claros en conversaciones reales.",
            "body",
        ),
        para(
            f"Adaptado de ideas del libro <b>{BOOK_TITLE}</b>. Comparte este PDF libremente y usa la versión online para abrir los audios.",
            "body",
        ),
    ]
    left = intro + [Spacer(1, 8), cover]
    return [Table(
        [[left, qr_box]],
        colWidths=[CONTENT_WIDTH - 50 * mm, 50 * mm],
        hAlign="LEFT",
    )]


def build_story() -> list:
    story: list = []
    story.extend(cover_block())
    story.append(Spacer(1, 18))
    story.append(para("Cómo usarla", "h1"))
    story.append(para(
        "No leas los 25 consejos como teoría. Elige tres, practícalos durante una semana y vuelve. La pronunciación se entrena más como un gesto físico que como una lista de vocabulario.",
        "body",
    ))
    story.append(para(
        "<b>Rutina mínima:</b> escucha el audio, repite lento, repite a velocidad normal, di una frase completa y grábate diez segundos.",
        "body",
    ))
    story.append(para(
        f"Guía online: {link('librodeingles.com/articulos/guia-pronunciacion-ingles-espanoles.html', GUIDE_URL)}",
        "body",
    ))

    story.append(PageBreak())
    story.append(para("25 tips de pronunciación para españoles", "h1"))
    story.append(para(
        "Empieza por claridad, no por perfección. Estos son los sonidos y hábitos que suelen mejorar antes la comprensión.",
        "body",
    ))
    add_tip_cards(story, TIPS[:12])

    story.append(PageBreak())
    story.append(para("Ritmo, linking y habla real", "h1"))
    story.append(para(
        "Muchos españoles pronuncian palabra por palabra. El inglés natural reduce palabras pequeñas, junta sonidos y cambia el peso de las sílabas.",
        "body",
    ))
    add_tip_cards(story, TIPS[12:])

    story.append(PageBreak())
    story.append(para("Plan de práctica de 7 días", "h1"))
    story.append(para(
        "Si no sabes por dónde empezar, usa este plan. Son sesiones cortas: cinco o diez minutos bien repetidos valen más que una hora dispersa.",
        "body",
    ))
    story.append(plan_table())
    story.append(Spacer(1, 14))
    story.append(para("Siguiente paso", "h1"))
    story.append(para(
        f"Para ver todos los audios del libro, entra en {link('librodeingles.com/audios.html', f'{BASE_URL}/audios.html')}. "
        f"Para leer más ejemplos y comprar el libro, visita {link('Amazon - De FAK a Fluent', BOOK_URL)}.",
        "body",
    ))
    story.append(Spacer(1, 8))
    story.append(para(
        "Nota: esta guía no intenta borrar tu acento español. El objetivo es que tus palabras importantes sean reconocibles más rápido.",
        "body",
    ))
    return story


def build_pdf() -> None:
    OUTPUT.parent.mkdir(parents=True, exist_ok=True)
    doc = SimpleDocTemplate(
        str(OUTPUT),
        pagesize=A4,
        rightMargin=MARGIN_X,
        leftMargin=MARGIN_X,
        topMargin=18 * mm,
        bottomMargin=20 * mm,
        title=TITLE,
        author=AUTHOR,
    )
    doc.build(build_story(), onFirstPage=draw_footer, onLaterPages=draw_footer)
    print(f"Wrote {OUTPUT.relative_to(ROOT)}")


if __name__ == "__main__":
    build_pdf()
