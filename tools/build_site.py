# -*- coding: utf-8 -*-
"""Generate crawlable article and audio pages for librodeingles.com."""

from __future__ import annotations

import html
import json
import re
import unicodedata
from pathlib import Path
from urllib.parse import quote
from xml.sax.saxutils import escape as xml_escape


ROOT = Path(__file__).resolve().parents[1]
BASE_URL = "https://librodeingles.com"
AMAZON_URL = "https://www.amazon.es/dp/B0DN6V5VDW"
FIRST_PUBLISHED = "2026-06-28"
TODAY = "2026-10-11"
BOOK_TITLE = "De FAK a Fluent"
AUTHOR = "Javier Sanz"
AUTHOR_URL = f"{BASE_URL}/contacto.html"
AUTHOR_ID = f"{BASE_URL}/#javier-sanz"
WEBSITE_ID = f"{BASE_URL}/#website"
ORGANIZATION_ID = f"{BASE_URL}/#organization"
BOOK_ID = f"{BASE_URL}/#book"
PRONUNCIATION_GUIDE_PDF = "/downloads/guia-pronunciacion-ingles-espanoles.pdf"
COVER_IMAGE = "/images/book-cover-520.webp"
COVER_WIDTH, COVER_HEIGHT = 520, 322
OG_IMAGE = f"{BASE_URL}/images/og-default.jpg"
LOGO_IMAGE = f"{BASE_URL}/images/icon-192.png"
INDEXNOW_KEY = "6f1d3c9a8b2e4f7a9c0d5e1b3a7f2c64"
MONTHS_ES = ["enero", "febrero", "marzo", "abril", "mayo", "junio", "julio", "agosto",
             "septiembre", "octubre", "noviembre", "diciembre"]
PLAUSIBLE_SNIPPET = """    <!-- Privacy-friendly analytics by Plausible -->
    <script async src="https://plausible.io/js/pa-4T40IxASAXWTjmNAWDMvd.js"></script>
    <script>
      window.plausible=window.plausible||function(){(plausible.q=plausible.q||[]).push(arguments)},plausible.init=plausible.init||function(i){plausible.o=i||{}};
      plausible.init()
    </script>"""


def slugify(value: str) -> str:
    value = unicodedata.normalize("NFKD", value)
    value = value.encode("ascii", "ignore").decode("ascii")
    value = value.lower()
    value = value.replace("'", "")
    value = re.sub(r"[^a-z0-9]+", "-", value)
    return value.strip("-")


def audio_slug(filename: str) -> str:
    return slugify(Path(filename).stem.replace("_", " ").replace(".", " "))


def esc(value: str) -> str:
    return html.escape(value, quote=True)


def json_ld(data: dict) -> str:
    return json.dumps(data, ensure_ascii=False, indent=8)


def write(path: str, content: str) -> None:
    target = ROOT / path
    target.parent.mkdir(parents=True, exist_ok=True)
    target.write_text(content.strip() + "\n", encoding="utf-8", newline="\n")


def human_date(iso_date: str) -> str:
    year, month, day = (int(part) for part in iso_date.split("-"))
    return f"{day} de {MONTHS_ES[month - 1]} de {year}"


def page_head(
    *,
    title: str,
    description: str,
    canonical: str | None,
    og_type: str,
    schema: dict,
    robots: str = "index, follow, max-image-preview:large, max-snippet:-1",
    published: str | None = None,
    modified: str | None = None,
) -> str:
    article_meta = ""
    if published:
        article_meta += f'\n    <meta property="article:published_time" content="{published}T00:00:00+00:00">'
    if modified:
        article_meta += f'\n    <meta property="article:modified_time" content="{modified}T00:00:00+00:00">'
    if published or modified:
        article_meta += f'\n    <meta property="article:author" content="{AUTHOR_URL}">'
    canonical_tag = f'\n    <link rel="canonical" href="{esc(canonical)}">' if canonical else ""
    og_url = f'\n    <meta property="og:url" content="{esc(canonical)}">' if canonical else ""
    return f"""<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>{esc(title)}</title>
    <meta name="description" content="{esc(description)}">
    <meta name="robots" content="{esc(robots)}">
    <meta name="author" content="{AUTHOR}">{canonical_tag}
    <link rel="icon" href="/favicon.ico" sizes="48x48">
    <link rel="icon" type="image/png" sizes="96x96" href="/images/icon-96.png">
    <link rel="apple-touch-icon" href="/images/apple-touch-icon.png">
    <meta property="og:locale" content="es_ES">
    <meta property="og:site_name" content="{BOOK_TITLE}">
    <meta property="og:title" content="{esc(title)}">
    <meta property="og:description" content="{esc(description)}">
    <meta property="og:image" content="{OG_IMAGE}">
    <meta property="og:image:width" content="1200">
    <meta property="og:image:height" content="630">
    <meta property="og:image:alt" content="Libro {BOOK_TITLE}, de {AUTHOR}">
    <meta property="og:type" content="{esc(og_type)}">{og_url}{article_meta}
    <meta name="twitter:card" content="summary_large_image">
    <meta name="twitter:title" content="{esc(title)}">
    <meta name="twitter:description" content="{esc(description)}">
    <meta name="twitter:image" content="{OG_IMAGE}">
    <link rel="stylesheet" href="/styles.css?v={TODAY}">
    <script type="application/ld+json">
    {json_ld(schema)}
    </script>
{PLAUSIBLE_SNIPPET}
</head>"""


def cover_img(css_class: str, *, eager: bool = False) -> str:
    loading = 'fetchpriority="high"' if eager else 'loading="lazy"'
    class_attr = f' class="{css_class}"' if css_class else ""
    return (
        f'<img{class_attr} src="{COVER_IMAGE}" width="{COVER_WIDTH}" height="{COVER_HEIGHT}" '
        f'{loading} decoding="async" alt="Portada de {BOOK_TITLE}">'
    )


def schema_author() -> dict:
    return {"@type": "Person", "@id": AUTHOR_ID, "name": AUTHOR, "url": AUTHOR_URL}


def schema_publisher() -> dict:
    return {
        "@type": "Organization",
        "@id": ORGANIZATION_ID,
        "name": BOOK_TITLE,
        "url": f"{BASE_URL}/",
        "logo": {"@type": "ImageObject", "url": LOGO_IMAGE, "width": 192, "height": 192},
    }


def schema_breadcrumbs(trail: list[tuple[str, str]]) -> dict:
    return {
        "@type": "BreadcrumbList",
        "itemListElement": [
            {"@type": "ListItem", "position": index + 1, "name": name, "item": f"{BASE_URL}{path}"}
            for index, (name, path) in enumerate(trail)
        ],
    }


def schema_faq(faq: list) -> dict:
    return {
        "@type": "FAQPage",
        "mainEntity": [
            {
                "@type": "Question",
                "name": question,
                "acceptedAnswer": {"@type": "Answer", "text": strip_tags(answer)},
            }
            for question, answer in faq
        ],
    }


def strip_tags(value: str) -> str:
    text = re.sub(r"<[^>]+>", "", value)
    return re.sub(r"\s+", " ", html.unescape(text)).strip()


def render_breadcrumbs(trail: list[tuple[str, str]]) -> str:
    parts = []
    for index, (name, path) in enumerate(trail):
        if index == len(trail) - 1:
            parts.append(f'<span aria-current="page">{esc(name)}</span>')
        else:
            parts.append(f'<a href="{esc(path)}">{esc(name)}</a>')
    separator = ' <span aria-hidden="true">›</span> '
    return f'<nav class="breadcrumbs" aria-label="Migas de pan">{separator.join(parts)}</nav>'


def wrap_tables(fragment: str) -> str:
    fragment = fragment.replace('<table class="data-table">', '<div class="table-wrap"><table class="data-table">')
    return fragment.replace("</table>", "</table></div>")


def render_quick_answer(answer: str | None) -> str:
    if not answer:
        return ""
    return f"""
                <div class="quick-answer">
                    <p class="quick-answer-label">Respuesta rápida</p>
                    <p>{answer}</p>
                </div>
"""


def render_faq(faq: list | None) -> str:
    if not faq:
        return ""
    items = "\n".join(
        f"""                    <div class="faq-item">
                        <h3>{esc(question)}</h3>
                        <p>{answer}</p>
                    </div>"""
        for question, answer in faq
    )
    return f"""
                <section class="faq" aria-labelledby="preguntas-frecuentes">
                    <h2 id="preguntas-frecuentes">Preguntas frecuentes</h2>
{items}
                </section>
"""


def site_header(active: str) -> str:
    items = [
        ("/", "Inicio", "inicio"),
        ("/audios.html", "Audios", "audios"),
        ("/articulos.html", "Artículos", "articulos"),
        ("/contacto.html", "Autor", "contacto"),
    ]
    link_lines = []
    for href, label, key in items:
        current = ' aria-current="page"' if key == active else ""
        link_lines.append(f'                <a href="{href}"{current}>{label}</a>')
    links = "\n".join(link_lines)
    return f"""<header class="site-header">
        <div class="nav-shell">
            <a class="brand" href="/">
                <img src="/images/icon-96.png" width="42" height="42" alt="" aria-hidden="true">
                <span>{BOOK_TITLE}</span>
            </a>
            <nav class="site-nav" aria-label="Principal">
{links}
            </nav>
        </div>
    </header>"""


def site_footer() -> str:
    return """<footer class="site-footer">
        <div class="footer-shell">
            <p>© De FAK a Fluent. Todos los derechos reservados</p>
            <nav class="footer-links" aria-label="Pie de página">
                <a href="/articulos.html">Artículos</a>
                <a href="/audios.html">Audios</a>
                <a href="/articulos/guia-pronunciacion-ingles-espanoles.html">Guía gratis</a>
                <a href="/contacto.html">Autor</a>
            </nav>
        </div>
    </footer>"""


ARTICLES: list[dict] = [
    {
        "slug": "guia-pronunciacion-ingles-espanoles",
        "category": "Pronunciación",
        "title": "Guía de pronunciación en inglés para españoles: 25 tips prácticos (PDF gratis)",
        "seo_title": "Guía de pronunciación en inglés: 25 tips para españoles",
        "description": "Guía gratis de pronunciación en inglés para españoles: 25 consejos sobre vocales, H, TH, R, ritmo y linking, con audios y un PDF para descargar.",
        "lede": "25 consejos concretos para que tu inglés suene más claro sin intentar borrar tu acento. Para leer online, guardar en PDF y compartir.",
        "reading": "8 minutos",
        "published": "2026-06-28",
        "download_pdf": PRONUNCIATION_GUIDE_PDF,
        "toc": [
            ("como-usarla", "Cómo usarla"),
            ("sonidos", "Sonidos clave (1-12)"),
            ("ritmo", "Ritmo y linking (13-25)"),
            ("por-donde-empezar", "Por dónde empezar"),
            ("plan", "Plan de 7 días"),
        ],
        "related": [
            "pronunciacion-ingles-para-espanoles",
            "vocales-ingles-cortas-largas",
            "sonido-th-ingles",
            "alfabeto-fonetico-ingles",
        ],
        "quick_answer": "Para mejorar tu pronunciación en inglés siendo español, empieza por lo que más bloquea la comprensión: la H suave (no jota), la I corta de <em>bit</em>, la TH, no decir <em>espain</em> por <em>Spain</em> y no dar el mismo peso a todas las sílabas. Practica pocos sonidos, con audio y dentro de frases.",
        "faq": [
            ("¿Qué consejos de pronunciación en inglés son más útiles para españoles?", "Los que más mejoran la claridad son: no añadir una e delante de S + consonante (<em>espain</em>), hacer la H con aire y no como jota, distinguir la I corta de la larga (<em>ship</em> y <em>sheep</em>), colocar la lengua entre los dientes para la TH y no dar a todas las sílabas el mismo peso."),
            ("¿Se puede mejorar la pronunciación en inglés siendo adulto?", "Sí. Es posible que conserves algo de acento español, y no pasa nada, pero la claridad mejora mucho con práctica concreta: escuchar un modelo, repetir en voz alta, grabarte y corregir pocos sonidos cada vez."),
            ("¿Cuánto tiempo al día hay que practicar la pronunciación?", "No hay una cifra mágica. Diez o quince minutos diarios de práctica en voz alta con audio suelen rendir más que una sesión larga a la semana, porque la pronunciación es un hábito físico que necesita repetición."),
            ("¿Hace falta aprender el alfabeto fonético (IPA) para pronunciar bien?", "No es imprescindible, pero ayuda mucho: te permite ver en un diccionario qué sonido lleva una palabra aunque la ortografía engañe, sobre todo con sonidos que no existen en español, como <span class=\"ipa\">/ɪ/</span>, <span class=\"ipa\">/ə/</span> o <span class=\"ipa\">/ð/</span>."),
            ("¿La guía de pronunciación en PDF es gratis?", "Sí. La versión en PDF de esta guía, con los 25 tips y los enlaces a los audios, es gratuita y puedes descargarla, imprimirla y compartirla libremente."),
        ],
        "body": """
                <p>Esta guía de pronunciación en inglés está pensada para españoles que ya estudian inglés, pero sienten que al hablar todavía suenan demasiado planos, demasiado españoles o poco claros. No necesitas sonar nativo. Necesitas que las palabras importantes se reconozcan rápido.</p>
                <p>Guárdala, pásasela a alguien que esté aprendiendo inglés y úsala como checklist. Cada punto es pequeño a propósito: si intentas corregir todo a la vez, no corriges nada.</p>
                <div class="lesson-box"><strong>Idea central:</strong> la pronunciación no mejora leyendo reglas. Mejora escuchando, repitiendo, exagerando un poco y llevando el sonido a frases reales.</div>
                <h2 id="como-usarla">Cómo usar esta guía</h2>
                <p>No leas los 25 consejos como teoría. Elige tres, practícalos durante una semana y vuelve. La pronunciación se entrena más como un gesto físico que como una lista de vocabulario.</p>
                <ol>
                <li>Escoge un sonido o hábito que te cueste.</li>
                <li>Abre el audio relacionado.</li>
                <li>Repite en voz alta tres veces: lento, normal y dentro de una frase.</li>
                <li>Grábate durante diez segundos y compara.</li>
                </ol>
                <p>Si no sabes cuáles elegir, más abajo tienes una propuesta <a href="#por-donde-empezar">según tu nivel</a> y una tabla con los errores que más se notan.</p>
                <h2 id="sonidos">25 tips de pronunciación en inglés para españoles</h2>
                <p>Los doce primeros consejos son sonidos concretos; los trece siguientes tienen que ver con ritmo, hábitos y actitud.</p>
                <div class="example-grid">
                <div class="mini-card"><strong>1. La H no es una jota</strong><span>En <em>hello</em> o <em>hard</em>, expulsa aire suave, como si echaras vaho en una ventana. No lleves el sonido a la jota española. Practica con <a href="/audio/hello-hard.html">hello y hard</a>.</span></div>
                <div class="mini-card"><strong>2. No conviertas la V en B</strong><span><em>Very</em> necesita labio inferior y dientes superiores. Si suena como <em>bery</em>, pierdes una diferencia muy visible. Escucha <a href="/audio/very-good.html">very good</a>.</span></div>
                <div class="mini-card"><strong>3. La I corta no es una i española</strong><span><em>Bit</em>, <em>win</em> y <em>lip</em> se acercan a una vocal relajada entre i y e. Evita que <em>sit</em> suene como <em>seat</em>. Escucha <a href="/audio/bit-big-win-lip-clip.html">bit, big, win, lip, clip</a>.</span></div>
                <div class="mini-card"><strong>4. Book y moon no comparten vocal</strong><span><em>Book</em> tiene una vocal corta; <em>moon</em>, una más larga. No pronuncies todas las dobles O como una u española. Compara <a href="/audio/book-cook-look-foot-hook-took-cookie-correcto.html">book, cook, look</a> con <a href="/audio/moon-food-room-school-tool-noodle-cool.html">moon, food, room</a>.</span></div>
                <div class="mini-card"><strong>5. Love no se lee con o española</strong><span>La vocal de <em>love</em> no es la de <em>lobo</em>. Compararla con <em>move</em> ayuda a notar que la ortografía engaña. Practica con <a href="/audio/love-clove-move.html">love, clove, move</a>.</span></div>
                <div class="mini-card"><strong>6. TH puede vibrar o no</strong><span><em>Think</em> no vibra; <em>they</em> sí. Primero coloca la lengua entre los dientes, luego decide si añades voz. Empieza con <a href="/audio/sonido-th-entre-dientes.html">TH entre dientes</a> y <a href="/audio/sonido-th-paladar.html">TH frente a D</a>.</span></div>
                <div class="mini-card"><strong>7. No metas una e antes de S</strong><span><em>Spain</em> no es <em>espain</em>. Empieza directamente en la S, aunque al principio te parezca brusco. Prueba con <a href="/audio/i-am-spanish.html">I am Spanish</a>.</span></div>
                <div class="mini-card"><strong>8. La R inglesa no se enrolla</strong><span>En <em>red</em> o <em>right</em>, no vibres la lengua como en <em>perro</em>. Recógela hacia atrás y evita el golpe español. Escucha <a href="/audio/red-car-around-right-sorry.html">red, car, around, right, sorry</a>.</span></div>
                <div class="mini-card"><strong>9. La L final pesa más</strong><span>En <em>feel</em>, <em>school</em> o <em>full</em>, la L final no desaparece. Dale presencia sin añadir una vocal al final. Practica con <a href="/audio/skill-goal-ball-full-world-call-feel-school.html">skill, goal, ball, full</a>.</span></div>
                <div class="mini-card"><strong>10. La J inglesa no es nuestra Y</strong><span><em>Job</em>, <em>John</em> y <em>enjoy</em> empiezan con un sonido más fuerte que una y española: el del nombre de la letra G en inglés. Escucha <a href="/audio/jump-john-job-jungle-enjoy.html">jump, John, job, jungle, enjoy</a>.</span></div>
                <div class="mini-card"><strong>11. No pronuncies letras mudas</strong><span><em>Walk</em>, <em>talk</em>, <em>would</em> y <em>should</em> esconden letras. Si lees todo lo escrito, la palabra se aleja del inglés real. Practica con <a href="/audio/walk-talk-half-calm-salmon-would-should-yolk-palm-chalk-walkie-talkie.html">letras mudas</a>.</span></div>
                <div class="mini-card"><strong>12. OUGH no tiene una sola regla</strong><span><em>Though</em>, <em>through</em>, <em>tough</em> y <em>thought</em> cambian mucho. Apréndelas por memoria auditiva, no por intuición visual. Escucha <a href="/audio/though-through-tough-cough-enough-bough-thought-plough.html">palabras con OUGH</a>.</span></div>
                </div>
                <h2 id="ritmo">Ritmo, acento y palabras que se juntan</h2>
                <p>Muchos españoles pronuncian las palabras una por una, con el mismo peso. El inglés real no funciona así: algunas palabras se comen, otras se estiran y muchas se unen.</p>
                <div class="example-grid">
                <div class="mini-card"><strong>13. No todas las sílabas valen igual</strong><span>El inglés da más peso a las palabras de contenido: nombres, verbos, adjetivos y adverbios. El español tiende a ser más plano.</span></div>
                <div class="mini-card"><strong>14. Reduce palabras pequeñas</strong><span><em>To</em>, <em>of</em>, <em>and</em> y <em>for</em> suelen sonar débiles dentro de una frase. Pronunciarlas todas con fuerza puede sonar artificial.</span></div>
                <div class="mini-card"><strong>15. Going to se junta</strong><span>En conversación rápida, <em>going to</em> puede sonar como <em>gonna</em>. Reconocerlo mejora tu listening y tu fluidez. Practica con <a href="/audio/going-to.html">going to</a>.</span></div>
                <div class="mini-card"><strong>16. Want to también cambia</strong><span><em>I want to go</em> no suele sonar palabra por palabra. Practica la frase completa, no solo <em>want</em> y <em>to</em> por separado. Escucha <a href="/audio/i-want-to-go-to-london.html">I want to go to London</a>.</span></div>
                <div class="mini-card"><strong>17. Give me puede sonar gimme</strong><span>No es hablar mal: es reconocer cómo se simplifican los sonidos en conversaciones reales. Escucha <a href="/audio/give-me-that.html">Give me that</a>.</span></div>
                <div class="mini-card"><strong>18. Could have no suena como tres bloques</strong><span><em>Could've</em>, <em>should've</em> y <em>would've</em> se comprimen mucho al hablar. Ojo: no se escriben <em>could of</em>. Escucha <a href="/audio/could-have-should-have-would-have.html">could have, should have, would have</a>.</span></div>
                <div class="mini-card"><strong>19. Practica frases, no solo palabras</strong><span>Una palabra aislada puede salir bien; la prueba real es mantener el sonido dentro de una frase completa.</span></div>
                <div class="mini-card"><strong>20. Usa respuestas reales</strong><span><em>Pretty good</em> o <em>doing well</em> suenan más naturales que repetir siempre <em>I am fine, thank you, and you?</em> Escucha <a href="/audio/pretty-good.html">pretty good</a> y <a href="/audio/doing-well.html">doing well</a>.</span></div>
                <div class="mini-card"><strong>21. Grábate poco, pero a menudo</strong><span>Diez segundos al día bastan para detectar vocales españolas añadidas, sonidos finales perdidos o un ritmo demasiado plano.</span></div>
                <div class="mini-card"><strong>22. Exagera primero, suaviza después</strong><span>Para aprender un sonido nuevo, exagerarlo un poco ayuda a que la boca encuentre la posición. Después lo haces natural.</span></div>
                <div class="mini-card"><strong>23. Imita el tono, no solo el sonido</strong><span>Copiar la melodía de una frase puede mejorar tu claridad más que repetir una palabra veinte veces.</span></div>
                <div class="mini-card"><strong>24. No tengas vergüenza de sonar inglés</strong><span>Pronunciar mejor no es postureo. Es facilitar que te entiendan en una reunión, una entrevista o una conversación real.</span></div>
                <div class="mini-card"><strong>25. Repite menos cosas, mejor</strong><span>Elige cinco audios útiles y repítelos muchos días. La constancia gana a la acumulación. Tienes 60 gratis en la <a href="/audios.html">colección de audios</a>.</span></div>
                </div>
                <h2 id="por-donde-empezar">¿Por dónde empezar según tu nivel?</h2>
                <p>Los 25 tips sirven para cualquiera, pero no todos rinden igual en cada momento. Esta es una forma razonable de priorizar:</p>
                <div class="example-grid">
                <div class="mini-card"><strong>Nivel básico (A2-B1)</strong><span>Tips 1, 3, 7 y 20. La H, la I corta y la S sin e delante son errores muy visibles y fáciles de corregir pronto. Aprende también un par de respuestas reales para <em>How are you?</em></span></div>
                <div class="mini-card"><strong>Nivel intermedio (B1-B2)</strong><span>Tips 4, 5, 6, 11, 12 y 13. Vocales que engañan, TH, letras mudas, OUGH y el acento de las palabras. Añade las terminaciones en <a href="/articulos/pronunciacion-ed-ingles.html">-ed</a>, que delatan mucho.</span></div>
                <div class="mini-card"><strong>Nivel avanzado (B2-C1)</strong><span>Tips 14 a 18 y 23. Formas débiles, palabras que se ligan y entonación: la diferencia entre “se te entiende” y “suenas natural”. Sigue con <a href="/articulos/ligar-palabras-ingles.html">cómo ligar palabras</a>.</span></div>
                <div class="mini-card"><strong>Tienes una entrevista pronto</strong><span>Tips 13, 19, 21 y 24. Prepara las frases que vas a decir seguro, practícalas enteras, grábate y escucha si las palabras clave se reconocen. La confianza también se entrena.</span></div>
                </div>
                <p>Si quieres entender símbolos como <span class="ipa">/ɪ/</span> o <span class="ipa">/θ/</span>, que verás en cualquier diccionario, tienes una explicación sencilla en el <a href="/articulos/alfabeto-fonetico-ingles.html">alfabeto fonético inglés para españoles</a>.</p>
                <h3>Los errores que más delatan a un español (y qué tip los arregla)</h3>
                <p>Una forma rápida de usar la guía al revés: busca el error que reconoces en ti y salta al tip correspondiente. Cuando hay una sola transcripción, vale para británico y americano.</p>
                <table class="data-table">
                <thead><tr><th>Lo que decimos</th><th>Lo que debería sonar</th><th>Tip</th></tr></thead>
                <tbody>
                <tr><td><em>espain</em>, <em>estudent</em></td><td><em>Spain</em> <span class="ipa">/speɪn/</span>, empezando en la S</td><td>7</td></tr>
                <tr><td><em>jelou</em>, con jota</td><td><em>hello</em> <span class="ipa">/heˈləʊ/</span> (UK) · <span class="ipa">/heˈloʊ/</span> (US), con H de aire</td><td>1</td></tr>
                <tr><td><em>bery gud</em></td><td><em>very</em> <span class="ipa">/ˈveri/</span>, con labio y dientes</td><td>2</td></tr>
                <tr><td><em>sit</em> que suena a <em>seat</em></td><td><span class="ipa">/sɪt/</span>, con i corta y relajada</td><td>3</td></tr>
                <tr><td><em>tink</em> o <em>sink</em> por <em>think</em></td><td><span class="ipa">/θɪŋk/</span>, lengua entre los dientes</td><td>6</td></tr>
                <tr><td><em>walk</em> con L</td><td><span class="ipa">/wɔːk/</span> (UK) · <span class="ipa">/wɑːk/</span> (US), sin L</td><td>11</td></tr>
                <tr><td>Todas las sílabas con la misma fuerza</td><td>Palabras clave fuertes y palabras pequeñas débiles</td><td>13 y 14</td></tr>
                <tr><td><em>I am fine, thank you, and you?</em></td><td><em>Pretty good</em>, <em>Doing well, yourself?</em></td><td>20</td></tr>
                </tbody>
                </table>
                <h2 id="plan">Plan de práctica de 7 días</h2>
                <p>Si no sabes por dónde empezar, usa este plan rápido:</p>
                <ol>
                <li><strong>Día 1:</strong> H inicial con <a href="/audio/hello-hard.html">hello y hard</a>.</li>
                <li><strong>Día 2:</strong> I corta con <a href="/audio/bit-big-win-lip-clip.html">bit, big, win, lip, clip</a>.</li>
                <li><strong>Día 3:</strong> TH con y sin voz con <a href="/articulos/sonido-th-ingles.html">la guía del sonido TH</a>.</li>
                <li><strong>Día 4:</strong> letras mudas con <a href="/articulos/letras-mudas-ingles.html">walk, talk, would y should</a>.</li>
                <li><strong>Día 5:</strong> OUGH con <a href="/articulos/palabras-ough-pronunciacion-ingles.html">though, through, tough y thought</a>.</li>
                <li><strong>Día 6:</strong> linking con <a href="/articulos/ligar-palabras-ingles.html">gonna, wanna, gotta y lemme</a>.</li>
                <li><strong>Día 7:</strong> una mini conversación con <a href="/audio/hows-it-going.html">How's it going?</a> y <a href="/audio/pretty-good.html">Pretty good</a>.</li>
                </ol>
                <div class="lesson-box"><strong>Para compartir:</strong> si alguien te dice “entiendo inglés, pero me da vergüenza hablar”, mándale esta guía. Empieza por claridad, no por perfección.</div>
                <p>Si prefieres tenerla impresa o enviarla por WhatsApp, <a href="/downloads/guia-pronunciacion-ingles-espanoles.pdf">descarga la guía en PDF</a>: tiene los mismos 25 tips y los enlaces a los audios. Cuando termines la semana, elige otros tres consejos y repite el ciclo. Así, poco a poco, es como se nota.</p>
        """,
    },
    {
        "slug": "pronunciacion-ingles-para-espanoles",
        "category": "Pronunciación",
        "title": "Pronunciación en inglés para españoles: los 10 errores más comunes y cómo corregirlos",
        "seo_title": "Pronunciación en inglés para españoles: 10 errores típicos",
        "description": "Los errores de pronunciación en inglés más típicos de los españoles: vocales, schwa, H, TH, V/B, espain, -ed y acento. Con IPA, ejemplos y audios gratis.",
        "lede": "Si tu gramática es suficiente, pero no te entienden, el problema casi nunca es una regla más: es sonido, ritmo y confianza al imitar.",
        "reading": "9 minutos",
        "published": "2026-06-28",
        "toc": [
            ("por-que", "Por qué cuesta"),
            ("sonidos", "Los 10 errores"),
            ("resumen", "Tabla resumen"),
            ("acento", "Acento"),
            ("practica", "Cómo mejorar"),
        ],
        "related": [
            "guia-pronunciacion-ingles-espanoles",
            "vocales-ingles-cortas-largas",
            "sonido-th-ingles",
            "palabras-ingles-mal-pronunciadas",
        ],
        "quick_answer": "Los errores de pronunciación en inglés más típicos de los españoles son: leer las vocales como en español (sobre todo la I corta y la schwa), convertir la H en jota, cambiar la TH por T, D o S, decir <em>espain</em>, perder consonantes finales y terminaciones -s/-ed, y acentuar mal las palabras.",
        "faq": [
            ("¿Cuál es el error de pronunciación más común de los españoles en inglés?", "Uno de los más reconocibles es añadir una e delante de S + consonante (<em>espain</em>, <em>estudent</em>), pero el que más confusiones provoca suele ser leer las vocales como en español, por ejemplo pronunciar <em>ship</em> igual que <em>sheep</em> o <em>live</em> igual que <em>leave</em>."),
            ("¿Se puede quitar el acento español al hablar inglés?", "Se puede reducir mucho, pero no es necesario eliminarlo. El objetivo útil es la inteligibilidad: que las palabras clave se reconozcan sin esfuerzo. Muchos hablantes con acento extranjero se comunican perfectamente porque dominan los sonidos y el ritmo que importan."),
            ("¿Qué es la schwa en inglés?", "La schwa, <span class=\"ipa\">/ə/</span>, es una vocal neutra, corta y relajada que aparece en muchísimas sílabas sin acento, como la primera de <em>about</em> o la última de <em>doctor</em>. Los españoles tendemos a pronunciar esas vocales enteras, y eso hace que el ritmo suene muy español."),
            ("¿Cómo puedo mejorar mi pronunciación en inglés en casa?", "Elige un sonido, escucha un modelo con audio, repite en voz alta, grábate unos segundos y compara. Practica con pares de palabras como <em>ship/sheep</em> y lleva cada sonido a frases completas. Diez minutos diarios suelen funcionar mejor que una hora a la semana."),
            ("¿Es mejor aprender pronunciación británica o americana?", "Cualquiera de las dos es válida. Lo práctico es elegir la que más escuchas (series, trabajo, viajes) y usarla como modelo para imitar. Lo importante es ser claro y razonablemente coherente, no sonar de un sitio concreto."),
        ],
        "body": """
                <p>La pronunciación es el filtro de entrada de una conversación. Puedes cometer errores de gramática y aun así comunicarte, pero si una palabra clave suena como otra palabra, o como algo que no existe en inglés, el interlocutor no tiene suficiente información para ayudarte.</p>
                <p>Para un español, el reto de la pronunciación en inglés no es sonar perfecto ni borrar su acento. El objetivo útil es que las palabras importantes sean reconocibles para un hablante nativo. Eso se consigue priorizando los errores que más diferencia producen, y esta página los reúne con ejemplos, transcripción fonética y audios para practicar.</p>
                <h2 id="por-que">¿Por qué a los españoles nos cuesta tanto la pronunciación inglesa?</h2>
                <p>En español tenemos cinco vocales muy estables. En inglés, esas mismas cinco letras producen muchos más sonidos: en el inglés británico estándar se suelen contar unos veinte sonidos vocálicos entre vocales simples y diptongos. Por eso dos palabras que a un español le parecen casi idénticas pueden sonar completamente distintas para un nativo.</p>
                <p>A eso se suman tres hábitos que traemos del español sin darnos cuenta:</p>
                <ul>
                <li><strong>Leemos como se escribe.</strong> En español funciona; en inglés, la ortografía avisa poco (piensa en <em>though</em>, <em>through</em> y <em>tough</em>).</li>
                <li><strong>Damos un peso parecido a todas las sílabas.</strong> El inglés alterna sílabas fuertes y débiles, y esa música es parte de lo que el oyente reconoce.</li>
                <li><strong>Nuestras palabras tienen otra forma.</strong> En español las palabras no empiezan por S + consonante (por eso decimos <em>España</em>, <em>escuela</em>, <em>estudiar</em>) y casi ninguna termina en grupos como <em>-sts</em> o <em>-kt</em>. El inglés está lleno de ellos.</li>
                </ul>
                <div class="lesson-box"><strong>Regla práctica:</strong> no practiques palabras aisladas solo leyendo. Escucha, repite y compárate con el audio. El ojo manda demasiado cuando la ortografía inglesa no coincide con el sonido.</div>
                <h2 id="sonidos">Los 10 errores de pronunciación en inglés más comunes en españoles</h2>
                <p>Cuando hay una sola transcripción fonética, coincide en inglés británico y americano.</p>
                <h3>1. Leer las vocales como en español (y olvidar la schwa)</h3>
                <p>Es el error con más consecuencias. La I corta de <em>ship</em> <span class="ipa">/ʃɪp/</span> no es la I larga de <em>sheep</em> <span class="ipa">/ʃiːp/</span>, y <em>live</em> <span class="ipa">/lɪv/</span> (vivir) no es <em>leave</em> <span class="ipa">/liːv/</span> (irse). La vocal de <em>up</em> o <em>love</em> <span class="ipa">/lʌv/</span> no es nuestra u ni nuestra o. Y casi todas las sílabas débiles se reducen a la <strong>schwa</strong> <span class="ipa">/ə/</span>, una vocal neutra y cortísima: <em>about</em> <span class="ipa">/əˈbaʊt/</span>, <em>today</em> <span class="ipa">/təˈdeɪ/</span>. Si pronuncias cada vocal entera, el ritmo se rompe. Aquí vive también el clásico error de <em>beach</em>, del que se ríe el subtítulo del libro.</p>
                <p>Practica con <a href="/audio/bit-big-win-lip-clip.html">bit, big, win, lip, clip</a>, <a href="/audio/live-leave-leaf.html">live, leave, leaf</a> y <a href="/audio/microsoft-up-us-uncle-umbrella.html">Microsoft, up, us, uncle, umbrella</a>, y lee la guía de <a href="/articulos/vocales-ingles-cortas-largas.html">vocales cortas, largas y schwa</a>.</p>
                <h3>2. Convertir la H en jota (o hacerla muda)</h3>
                <p>La H de <em>hello</em> <span class="ipa">/heˈləʊ/</span> (UK) · <span class="ipa">/heˈloʊ/</span> (US) o <em>hard</em> <span class="ipa">/hɑːd/</span> (UK) · <span class="ipa">/hɑːrd/</span> (US) no rasca en la garganta como nuestra jota. Es solo aire, como cuando echas vaho en una ventana. El error contrario también existe: como en español la h es muda, a veces la borramos y decimos <em>ello</em>. Eso sí, hay unas pocas palabras con H muda también en inglés: <em>hour</em>, <em>honest</em>, <em>heir</em>. Practica con <a href="/audio/hello-hard.html">hello y hard</a>.</p>
                <h3>3. Cambiar la TH por T, D o S</h3>
                <p>Hay dos TH: la sorda <span class="ipa">/θ/</span> de <em>think</em> y <em>three</em>, y la sonora <span class="ipa">/ð/</span> de <em>this</em>, <em>they</em> y <em>the</em>. Las dos se hacen con la lengua entre los dientes. La buena noticia: si en tu español distingues <em>casa</em> de <em>caza</em>, la c de <em>cena</em> ya es exactamente <span class="ipa">/θ/</span>. El error típico es decir <em>tree</em> (árbol) cuando quieres decir <em>three</em>, o <em>day</em> cuando quieres decir <em>they</em>. Lo tienes todo en la guía del <a href="/articulos/sonido-th-ingles.html">sonido TH</a>, en <a href="/articulos/como-se-pronuncia-the.html">cómo se pronuncia THE</a> y en el audio de <a href="/audio/sonido-th-entre-dientes.html">TH entre dientes</a>.</p>
                <h3>4. La V y la B suenan igual</h3>
                <p>En español, <em>vaca</em> y <em>baca</em> se pronuncian igual. En inglés no: la <span class="ipa">/v/</span> se hace apoyando los dientes de arriba en el labio inferior, con voz; la <span class="ipa">/b/</span> junta los dos labios. Si no las separas, <em>very</em> <span class="ipa">/ˈveri/</span> suena a <em>berry</em> <span class="ipa">/ˈberi/</span> (baya), <em>vest</em> (chaleco) a <em>best</em> y <em>van</em> a <em>ban</em>. Escucha <a href="/audio/very-good.html">very good</a> y exagera el contacto entre labio y dientes las primeras veces.</p>
                <h3>5. La e fantasma: espain, estudent, espeak</h3>
                <p>Como en español ninguna palabra empieza por S + consonante, el cerebro mete una e de apoyo: <em>espain</em>, <em>eschool</em>, <em>Estarbucks</em>. En inglés, <em>Spain</em> <span class="ipa">/speɪn/</span>, <em>speak</em> <span class="ipa">/spiːk/</span> o <em>school</em> <span class="ipa">/skuːl/</span> empiezan directamente en la S. Truco: alarga la S como un siseo (<em>sssspain</em>) y ve acortándola. Practica con <a href="/audio/i-am-spanish.html">I am Spanish</a> y <a href="/audio/i-am-from-spain-and-i-am-33.html">I am from Spain and I am 33</a>.</p>
                <h3>6. Comerse las consonantes finales (y las terminaciones -s y -ed)</h3>
                <p>Las palabras españolas suelen terminar en vocal o en una consonante suave. Las inglesas, no: <em>texts</em> <span class="ipa">/teksts/</span>, <em>desks</em> <span class="ipa">/desks/</span>, <em>costs</em> <span class="ipa">/kɒsts/</span> (UK) · <span class="ipa">/kɑːsts/</span> (US). Si las recortas, <em>card</em> suena a <em>car</em> y <em>he works</em> a <em>he work</em>. Con el pasado pasa lo contrario: tendemos a pronunciar la -ed como una sílaba más, cuando normalmente no lo es. <em>Worked</em> es <span class="ipa">/wɜːkt/</span> (UK) · <span class="ipa">/wɝːkt/</span> (US), una sola sílaba; en los verbos regulares, la sílaba extra <span class="ipa">/ɪd/</span> solo aparece tras T o D, como en <em>wanted</em>. Practica con <a href="/audio/texts-guests-desks-costs.html">texts, guests, desks, costs</a> y la guía de <a href="/articulos/pronunciacion-ed-ingles.html">pronunciación de -ed</a>.</p>
                <h3>7. Poner el acento en la sílaba equivocada</h3>
                <p>La sílaba fuerte de una palabra inglesa no siempre está donde la pondría un español, sobre todo en palabras parecidas a las nuestras. <em>Chocolate</em> lleva la fuerza al principio: <span class="ipa">/ˈtʃɒklət/</span> (UK) · <span class="ipa">/ˈtʃɑːklət/</span> (US). Y en muchos pares el acento cambia la palabra: <em>a <strong>re</strong>cord</em> (un disco, un récord) frente a <em>to re<strong>cord</strong></em> (grabar), o <em>a <strong>pre</strong>sent</em> (un regalo) frente a <em>to pre<strong>sent</strong></em> (presentar). Las palabras largas son buen entrenamiento: escucha <a href="/audio/education-individual-gradual-schedule-procedure-residual.html">education, individual, gradual, schedule, procedure, residual</a> y fíjate en dónde cae el golpe.</p>
                <h3>8. La R española</h3>
                <p>La R de <em>red</em> <span class="ipa">/red/</span> o <em>right</em> <span class="ipa">/raɪt/</span> no vibra ni golpea: la lengua se recoge un poco hacia atrás sin tocar el paladar. Si haces la erre de <em>perro</em> en <em>sorry</em> o <em>around</em>, se nota muchísimo. Además, en el inglés británico estándar la R después de vocal normalmente no se pronuncia (<em>car</em> <span class="ipa">/kɑː/</span>), mientras que en el americano sí (<span class="ipa">/kɑːr/</span>). Curiosidad útil: en inglés americano, la T entre vocales de <em>water</em> o <em>better</em> se parece mucho a nuestra r suave de <em>pero</em>. Escucha <a href="/audio/red-car-around-right-sorry.html">red, car, around, right, sorry</a>.</p>
                <h3>9. Pronunciar palabra por palabra, sin ligar</h3>
                <p>En inglés hablado las palabras se unen: <em>pick it up</em> suena casi como una sola palabra, <em>going to</em> se convierte en <em>gonna</em> y las palabras pequeñas (<em>to</em>, <em>of</em>, <em>and</em>) se debilitan. Si lo dices todo separado y con la misma fuerza, se te entiende, pero suenas a lectura en voz alta. Practica con <a href="/audio/pick-it-up.html">pick it up</a> y <a href="/audio/going-to.html">going to</a>, y lee <a href="/articulos/ligar-palabras-ingles.html">cómo ligar palabras en inglés</a>.</p>
                <h3>10. Fiarse de la ortografía: letras mudas y palabras trampa</h3>
                <p><em>Walk</em> y <em>talk</em> no suenan con L, <em>island</em> <span class="ipa">/ˈaɪlənd/</span> no suena con S y <em>though</em>, <em>through</em> y <em>tough</em> no riman entre sí. Este tipo de palabras se aprende de memoria, con audio y por familias. Empieza por las <a href="/articulos/letras-mudas-ingles.html">letras mudas</a>, las <a href="/articulos/palabras-ough-pronunciacion-ingles.html">palabras con OUGH</a> y la lista de <a href="/articulos/palabras-ingles-mal-pronunciadas.html">palabras que los españoles pronuncian mal</a>.</p>
                <p>Dos más que conviene vigilar aunque no entren en el top 10: la J de <em>job</em> o <em>John</em>, más fuerte que nuestra y (<a href="/audio/jump-john-job-jungle-enjoy.html">jump, John, job, jungle, enjoy</a>), y la Y de <em>yes</em> o <em>yellow</em>, que no debe sonar a <em>Jess</em> ni a <em>jello</em> (<a href="/audio/yellow-young-you-yes.html">yellow, young, you, yes</a>).</p>
                <h2 id="resumen">Tabla resumen: error, ejemplo y solución</h2>
                <table class="data-table">
                <thead><tr><th>Error</th><th>Ejemplo</th><th>Solución rápida</th></tr></thead>
                <tbody>
                <tr><td>Vocales españolas</td><td><em>ship</em> suena a <em>sheep</em></td><td>I corta y relajada; schwa en sílabas débiles</td></tr>
                <tr><td>H como jota</td><td><em>jelou</em></td><td>Solo aire, sin rascar</td></tr>
                <tr><td>TH como T, D o S</td><td><em>tree</em> por <em>three</em></td><td>Lengua entre los dientes</td></tr>
                <tr><td>V igual que B</td><td><em>berry</em> por <em>very</em></td><td>Dientes de arriba sobre el labio inferior</td></tr>
                <tr><td>S con e delante</td><td><em>espain</em></td><td>Empieza con un siseo: <em>sss-pain</em></td></tr>
                <tr><td>Finales perdidos</td><td><em>car</em> por <em>card</em></td><td>Cierra cada palabra; -ed sin sílaba extra salvo tras T o D</td></tr>
                <tr><td>Acento de palabra</td><td><em>cho-co-LA-te</em></td><td>Comprueba dónde cae el golpe y exagéralo</td></tr>
                <tr><td>R vibrante</td><td><em>sorry</em> con la erre de <em>perro</em></td><td>Lengua recogida, sin tocar el paladar</td></tr>
                <tr><td>Sin ligar</td><td><em>pick / it / up</em></td><td>Une la consonante final con la vocal siguiente</td></tr>
                <tr><td>Leer como se escribe</td><td><em>walk</em> con L</td><td>Aprende familias de palabras con audio</td></tr>
                </tbody>
                </table>
                <h2 id="acento">Tu acento importa, pero no por postureo</h2>
                <p>En España muchas personas sienten vergüenza al pronunciar bien, como si imitar un acento inglés o americano fuera exagerado. Esa barrera social es cara: en una entrevista, llamada o reunión, una pronunciación clara transmite seguridad y reduce fricción.</p>
                <p>La meta no es parecer de Londres, Boston o Dublín. La meta es que tu interlocutor no tenga que descifrarte. Puedes conservar parte de tu acento español y, a la vez, trabajar los sonidos que desbloquean la comprensión. Elige un modelo, británico o americano, el que más escuches, y úsalo como referencia para imitar.</p>
                <h2 id="practica">¿Cómo mejorar la pronunciación en inglés? Método en 5 pasos</h2>
                <ol>
                <li><strong>Elige un sonido, no veinte.</strong> Por ejemplo, la H inicial o la I corta durante una semana.</li>
                <li><strong>Escucha pares de palabras donde el error cambie el significado:</strong> <em>ship/sheep</em>, <em>three/tree</em>, <em>very/berry</em>.</li>
                <li><strong>Repite en voz alta y grábate.</strong> Diez segundos bastan para oír lo que al hablar no notas.</li>
                <li><strong>Llévalo a frases completas.</strong> Una palabra aislada puede salir bien; la prueba real es mantener el sonido con ritmo natural.</li>
                <li><strong>Comprueba en un diccionario con audio.</strong> El <a href="https://dictionary.cambridge.org/es/" target="_blank" rel="noopener noreferrer">diccionario de Cambridge</a> da la pronunciación británica y americana de cada palabra; si aprendes a leer el <a href="/articulos/alfabeto-fonetico-ingles.html">alfabeto fonético</a>, dejarás de depender de la ortografía.</li>
                </ol>
                <p>Si solo tienes tiempo para tres cosas, empieza por las vocales cortas, la S sin e delante y las consonantes finales. Después, usa la <a href="/articulos/guia-pronunciacion-ingles-espanoles.html">guía de 25 tips de pronunciación</a> como checklist y la colección de <a href="/audios.html">audios de pronunciación</a> para practicar cada día un poco.</p>
        """,
    },
    {
        "slug": "alfabeto-fonetico-ingles",
        "category": "Pronunciación",
        "title": "Alfabeto fonético inglés (IPA) para españoles: todos los símbolos con ejemplos",
        "seo_title": "Alfabeto fonético inglés (IPA): símbolos y ejemplos",
        "description": "Alfabeto fonético inglés para españoles: todos los símbolos IPA con ejemplos, qué sonidos existen en español, diferencias UK/US y audios para practicar.",
        "lede": "Los símbolos raros del diccionario no son decoración: te dicen exactamente cómo suena cada palabra. Aquí los tienes todos, explicados desde el español y con audios.",
        "reading": "12 minutos",
        "published": "2026-10-11",
        "from_book": False,
        "toc": [
            ("que-es", "Qué es"),
            ("vocales", "Vocales"),
            ("diptongos", "Diptongos"),
            ("consonantes", "Consonantes"),
            ("americano-britanico", "Americano vs británico"),
            ("diccionario", "Leer el diccionario"),
            ("practica", "Cómo aprenderlo"),
        ],
        "related": [
            "vocales-ingles-cortas-largas",
            "sonido-th-ingles",
            "pronunciacion-ed-ingles",
            "guia-pronunciacion-ingles-espanoles",
        ],
        "quick_answer": "El <strong>alfabeto fonético inglés</strong> es el conjunto de símbolos del IPA que usan los diccionarios para indicar la pronunciación. El modelo británico estándar tiene <strong>44 sonidos</strong>: 12 vocales, 8 diptongos y 24 consonantes. Para un español, los más difíciles son los que no existen en nuestro idioma, como /ɪ/, /æ/, /ʌ/, /ə/, /v/, /z/, /ʃ/ y /h/.",
        "faq": [
            ("¿Cuántas vocales tiene el inglés?", "Cinco letras vocales, pero unos 20 sonidos vocálicos en el modelo británico estándar: 12 vocales simples (7 cortas y 5 largas) y 8 diptongos. Por eso leer el inglés con las cinco vocales del español cambia unas palabras por otras, como <em>ship</em> y <em>sheep</em>."),
            ("¿Qué es la schwa (ə) en inglés?", "La schwa, <span class=\"ipa\">/ə/</span>, es una vocal neutra y relajada que aparece en sílabas sin acento, como la primera de <em>about</em> (<span class=\"ipa\">/əˈbaʊt/</span>). Es el sonido vocálico más frecuente del inglés y no existe en español, por eso tendemos a sustituirlo por una vocal clara."),
            ("¿Qué significan los dos puntos (ː) en fonética inglesa?", "Indican que la vocal es larga, como en <em>sheep</em> <span class=\"ipa\">/ʃiːp/</span> frente a <em>ship</em> <span class=\"ipa\">/ʃɪp/</span>. Pero en inglés la diferencia no es solo de duración: también cambia la calidad del sonido, así que no basta con alargar una vocal española."),
            ("¿Qué diferencia hay entre la fonética británica y la americana?", "Las más visibles son el diptongo de <em>go</em> (<span class=\"ipa\">/əʊ/</span> en UK, <span class=\"ipa\">/oʊ/</span> en US), la r después de vocal (en EE. UU. siempre se pronuncia), la vocal de <em>bath</em> (<span class=\"ipa\">/ɑː/</span> frente a <span class=\"ipa\">/æ/</span>), la de <em>hot</em> y la t americana entre vocales, que suena como nuestra r de “pero”."),
            ("¿Hace falta saber fonética para pronunciar bien en inglés?", "No es imprescindible, pero acelera mucho el proceso: te permite saber cómo suena cualquier palabra mirando el diccionario, sin depender de que alguien te la diga. Funciona mejor combinada con audio, escuchando y repitiendo en voz alta."),
        ],
        "body": """
                <p>Buscas <em>though</em> en un diccionario y te encuentras esto: <span class="ipa">/ðəʊ/</span> (en británico; en americano, <span class="ipa">/ðoʊ/</span>). Si te suena a jeroglífico, es normal. Es el <strong>alfabeto fonético internacional</strong> (IPA, por sus siglas en inglés), y es la herramienta más útil que puedes aprender para pronunciar inglés sin depender de que alguien te lo diga en voz alta.</p>
                <p>Esta guía de fonética inglesa para españoles recorre todos los símbolos con ejemplos, responde a la pregunta que de verdad importa (¿existe este sonido en español?) y te lleva a audios para escuchar los más difíciles.</p>

                <h2 id="que-es">¿Qué es el alfabeto fonético inglés y para qué sirve?</h2>
                <p>El IPA asigna un símbolo a cada sonido, y solo a uno. En inglés eso vale oro, porque la ortografía no avisa: la misma combinación <em>ough</em> suena distinta en <em>though</em>, <em>through</em> y <em>tough</em> (lo vemos en <a href="/articulos/palabras-ough-pronunciacion-ingles.html">palabras con OUGH</a>), y el mismo sonido <span class="ipa">/iː/</span> se escribe <em>ee</em> en <em>see</em>, <em>ea</em> en <em>sea</em> e <em>ie</em> en <em>piece</em>. Con los símbolos sabes exactamente qué decir, sin adivinar.</p>
                <p>Los 44 sonidos del modelo británico estándar se reparten en tres tablas: vocales, diptongos y consonantes. El inglés americano usa un inventario algo distinto, que verás más abajo. Para un español, el gran choque está en las vocales: nosotros tenemos cinco y nos sobran; el inglés juega con muchas más.</p>
                <div class="lesson-box"><strong>Barras, corchetes y pequeñas variaciones:</strong> los diccionarios escriben la pronunciación entre barras, <span class="ipa">/kæt/</span>. Si ves corchetes, <span class="ipa">[kʰæt]</span>, es una transcripción más detallada que no necesitas para empezar. Ten en cuenta que cada diccionario tiene pequeñas diferencias de notación: algunos escriben <span class="ipa">/ɛ/</span> en lugar de <span class="ipa">/e/</span> para la vocal de <em>bed</em>, y la r inglesa aparece como <span class="ipa">/r/</span> aunque técnicamente sea <span class="ipa">[ɹ]</span>. Aquí seguimos el estilo de Cambridge y Oxford.</div>

                <h2 id="vocales">Vocales inglesas: los 12 sonidos y cuáles tenemos en español</h2>
                <p>Siete vocales cortas y cinco largas. Las largas llevan dos puntitos, <span class="ipa">ː</span>. Las que más te van a cambiar el inglés son las que no tenemos: <span class="ipa">/ɪ/</span>, <span class="ipa">/æ/</span>, <span class="ipa">/ʌ/</span>, <span class="ipa">/ʊ/</span>, <span class="ipa">/ɜː/</span> y <span class="ipa">/ə/</span>.</p>
                <table class="data-table">
                <thead><tr><th>Símbolo</th><th>Ejemplo</th><th>IPA del ejemplo</th><th>¿Existe en español?</th><th>Pista</th></tr></thead>
                <tbody>
                <tr><td><span class="ipa">/iː/</span></td><td>see</td><td>UK y US /siː/</td><td>Casi</td><td>Como nuestra i, pero más larga y tensa, con los labios estirados. Escucha <a href="/audio/live-leave-leaf.html">leave y leaf</a>.</td></tr>
                <tr><td><span class="ipa">/ɪ/</span></td><td>bit</td><td>UK y US /bɪt/</td><td>No</td><td>Corta y relajada, entre i y e. Con una i española, <em>bit</em> se acerca a <em>beat</em>. Audio: <a href="/audio/bit-big-win-lip-clip.html">bit, big, win, lip, clip</a>.</td></tr>
                <tr><td><span class="ipa">/e/</span></td><td>bed</td><td>UK y US /bed/</td><td>Sí</td><td>Muy parecida a nuestra e.</td></tr>
                <tr><td><span class="ipa">/æ/</span></td><td>cat</td><td>UK y US /kæt/</td><td>No</td><td>Abre la boca como para decir a, pero pensando en e. Audio: <a href="/audio/lack-lock-look-luke.html">lack</a>.</td></tr>
                <tr><td><span class="ipa">/ʌ/</span></td><td>cup</td><td>UK y US /kʌp/</td><td>No (se acerca a una a)</td><td>Una a corta, relajada y poco abierta. Audio: <a href="/audio/microsoft-up-us-uncle-umbrella.html">up, us, uncle, umbrella</a> y <a href="/audio/love-clove-move.html">love</a>.</td></tr>
                <tr><td><span class="ipa">/ɑː/</span></td><td>car</td><td>UK /kɑː/<br>US /kɑːr/</td><td>Parecida</td><td>Una a larga y abierta, con la lengua atrás. Está en <em>calm</em> y <em>palm</em>, del <a href="/audio/walk-talk-half-calm-salmon-would-should-yolk-palm-chalk-walkie-talkie.html">audio de letras mudas</a>.</td></tr>
                <tr><td><span class="ipa">/ɒ/</span></td><td>hot</td><td>UK /hɒt/<br>US /hɑːt/</td><td>Parecida (solo UK)</td><td>Una o corta y abierta. En EE. UU. estas palabras van con /ɑː/. Audio: <a href="/audio/lack-lock-look-luke.html">lock</a> y <a href="/audio/bomb-tomb-comb.html">bomb</a>.</td></tr>
                <tr><td><span class="ipa">/ɔː/</span></td><td>door</td><td>UK /dɔː/<br>US /dɔːr/</td><td>Parecida</td><td>Una o larga, con los labios bien redondeados. Audio: <a href="/audio/door-floor-score-shore-roar-soar.html">door, floor, score, shore</a>.</td></tr>
                <tr><td><span class="ipa">/ʊ/</span></td><td>book</td><td>UK y US /bʊk/</td><td>No</td><td>Una u corta y relajada, con los labios poco redondeados. Audio: <a href="/audio/book-cook-look-foot-hook-took-cookie-correcto.html">book, cook, look</a> (y el <a href="/audio/book-cook-look-foot-hook-took-cookie-lol.html">error típico</a>).</td></tr>
                <tr><td><span class="ipa">/uː/</span></td><td>food</td><td>UK y US /fuːd/</td><td>Casi</td><td>Como nuestra u, pero más larga. Audio: <a href="/audio/moon-food-room-school-tool-noodle-cool.html">moon, food, room, school</a>.</td></tr>
                <tr><td><span class="ipa">/ɜː/</span></td><td>bird</td><td>UK /bɜːd/<br>US /bɝːd/</td><td>No</td><td>Boca relajada y medio abierta: ni e ni o. En EE. UU. lleva r. Audio: <a href="/audio/bird-bear-beer-beard.html">bird</a>.</td></tr>
                <tr><td><span class="ipa">/ə/</span></td><td>about</td><td>UK y US /əˈbaʊt/</td><td>No</td><td>La schwa: vocal neutra y débil de las sílabas átonas. La oirás en formas débiles como <a href="/audio/could-have-should-have-would-have.html">could have</a>.</td></tr>
                </tbody>
                </table>
                <div class="lesson-box"><strong>Cuatro vocales en una escalera:</strong> el audio de <a href="/audio/lack-lock-look-luke.html">lack, lock, look y Luke</a> recorre cuatro vocales distintas con la misma estructura: <em>lack</em> <span class="ipa">/læk/</span>, <em>look</em> <span class="ipa">/lʊk/</span> y <em>Luke</em> <span class="ipa">/luːk/</span> (iguales en UK y US), y <em>lock</em>, que es UK <span class="ipa">/lɒk/</span> · US <span class="ipa">/lɑːk/</span>. Si los cuatro te suenan distintos al decirlos, vas muy bien.</div>
                <p>Dos símbolos más que verás a menudo: <span class="ipa">/i/</span> sin puntos, en la sílaba final débil de palabras como <em>happy</em> (<span class="ipa">/ˈhæpi/</span> en UK y US), y <span class="ipa">/ɚ/</span>, la schwa con r del inglés americano, en palabras como <em>teacher</em> (UK <span class="ipa">/ˈtiːtʃə/</span>, US <span class="ipa">/ˈtiːtʃɚ/</span>). Para trabajar las vocales a fondo tienes la guía de <a href="/articulos/vocales-ingles-cortas-largas.html">vocales inglesas que confunden a los españoles</a>.</p>

                <h2 id="diptongos">Diptongos: dos vocales en una sílaba</h2>
                <p>Un diptongo empieza en una vocal y se desliza hacia otra dentro de la misma sílaba. Aquí los españoles tenemos ventaja: cuatro de los ocho existen casi igual en español.</p>
                <table class="data-table">
                <thead><tr><th>Símbolo</th><th>Ejemplo</th><th>IPA del ejemplo</th><th>¿Existe en español?</th><th>Pista</th></tr></thead>
                <tbody>
                <tr><td><span class="ipa">/eɪ/</span></td><td>day</td><td>UK y US /deɪ/</td><td>Sí</td><td>Como el “ei” de “rey”. Está en <em>late</em>, del audio <a href="/audio/light-love-listen-like-late-learn-laugh.html">light, love, listen...</a></td></tr>
                <tr><td><span class="ipa">/aɪ/</span></td><td>my</td><td>UK y US /maɪ/</td><td>Sí</td><td>Como el “ai” de “baile”. Audio: <a href="/audio/time.html">time</a>.</td></tr>
                <tr><td><span class="ipa">/ɔɪ/</span></td><td>boy</td><td>UK y US /bɔɪ/</td><td>Sí</td><td>Como el “oy” de “hoy”. Audio: <a href="/audio/jump-john-job-jungle-enjoy.html">enjoy</a>.</td></tr>
                <tr><td><span class="ipa">/aʊ/</span></td><td>now</td><td>UK y US /naʊ/</td><td>Sí</td><td>Como el “au” de “causa”. Audio: <a href="/audio/how-are-you.html">How are you?</a></td></tr>
                <tr><td><span class="ipa">/əʊ/</span> · <span class="ipa">/oʊ/</span></td><td>go</td><td>UK /ɡəʊ/<br>US /ɡoʊ/</td><td>No</td><td>No es una o pura: se desliza hacia u (“góu”). En UK empieza en schwa. Audio: <a href="/audio/focus.html">focus</a>.</td></tr>
                <tr><td><span class="ipa">/ɪə/</span></td><td>beer</td><td>UK /bɪə/<br>US /bɪr/</td><td>No</td><td>Una I corta que se apaga en schwa. En EE. UU., /ɪr/. Audio: <a href="/audio/bird-bear-beer-beard.html">beer, beard</a>.</td></tr>
                <tr><td><span class="ipa">/eə/</span></td><td>bear</td><td>UK /beə/<br>US /ber/</td><td>No</td><td>Una e abierta que se apaga en schwa. En EE. UU., /er/. Audio: <a href="/audio/bird-bear-beer-beard.html">bear</a>.</td></tr>
                <tr><td><span class="ipa">/ʊə/</span></td><td>tour</td><td>UK /tʊə/<br>US /tʊr/</td><td>No</td><td>Una u corta que se apaga en schwa. Muchos británicos dicen /tɔː/.</td></tr>
                </tbody>
                </table>
                <p>El diptongo de <em>go</em> es el que más delata a un español: decimos una o pura y corta. Piensa en “góu”, con un final que se cierra hacia la u, y practica con <a href="/audio/bomb-tomb-comb.html">comb</a> o <a href="/audio/focus.html">focus</a>.</p>

                <h2 id="consonantes">Consonantes: cuáles tenemos en español y cuáles no</h2>
                <p>Las consonantes son mejor noticia: la mayoría existen en español o se parecen mucho. Los problemas se concentran en unas pocas, sobre todo <span class="ipa">/v/</span>, <span class="ipa">/z/</span>, <span class="ipa">/ʃ/</span>, <span class="ipa">/ʒ/</span>, <span class="ipa">/dʒ/</span>, <span class="ipa">/h/</span> y la <span class="ipa">/r/</span> inglesa.</p>
                <table class="data-table">
                <thead><tr><th>Símbolo</th><th>Ejemplo</th><th>IPA del ejemplo</th><th>¿Existe en español?</th><th>Pista</th></tr></thead>
                <tbody>
                <tr><td><span class="ipa">/p/</span></td><td>pen</td><td>UK y US /pen/</td><td>Sí</td><td>Al principio de sílaba tónica sale con un golpe de aire. Audio: <a href="/audio/pick-it-up.html">pick it up</a>.</td></tr>
                <tr><td><span class="ipa">/b/</span></td><td>bad</td><td>UK y US /bæd/</td><td>Sí</td><td>En inglés no se suaviza entre vocales como en “haba”.</td></tr>
                <tr><td><span class="ipa">/t/</span></td><td>tea</td><td>UK y US /tiː/</td><td>Parecida</td><td>Con la lengua en los alveolos, no en los dientes, y con golpe de aire. Audio: <a href="/audio/time.html">time</a>.</td></tr>
                <tr><td><span class="ipa">/d/</span></td><td>day</td><td>UK y US /deɪ/</td><td>Parecida</td><td>Alveolar, y nunca se suaviza como en “nada”. Compárala con el TH en <a href="/audio/sonido-th-paladar.html">este audio</a>.</td></tr>
                <tr><td><span class="ipa">/k/</span></td><td>key</td><td>UK y US /kiː/</td><td>Sí</td><td>Con golpe de aire al principio de sílaba tónica.</td></tr>
                <tr><td><span class="ipa">/ɡ/</span></td><td>get</td><td>UK y US /ɡet/</td><td>Sí</td><td>Como en “gato”, sin suavizarse entre vocales.</td></tr>
                <tr><td><span class="ipa">/tʃ/</span></td><td>chip</td><td>UK y US /tʃɪp/</td><td>Sí</td><td>La ch de “chico”. Audio: <a href="/audio/walk-talk-half-calm-salmon-would-should-yolk-palm-chalk-walkie-talkie.html">chalk</a>.</td></tr>
                <tr><td><span class="ipa">/dʒ/</span></td><td>job</td><td>UK /dʒɒb/<br>US /dʒɑːb/</td><td>No (como sonido propio)</td><td>Recuerda a la y enfática de “¡yo!” en algunos hablantes. Audio: <a href="/audio/jump-john-job-jungle-enjoy.html">jump, John, job</a>.</td></tr>
                <tr><td><span class="ipa">/f/</span></td><td>fish</td><td>UK y US /fɪʃ/</td><td>Sí</td><td>Igual que la nuestra.</td></tr>
                <tr><td><span class="ipa">/v/</span></td><td>van</td><td>UK y US /væn/</td><td>No</td><td>Labio inferior contra dientes superiores, como una f con voz. Audio: <a href="/audio/live-leave-leaf.html">live, leave, leaf</a>.</td></tr>
                <tr><td><span class="ipa">/θ/</span></td><td>think</td><td>UK y US /θɪŋk/</td><td>Sí, en casi toda España</td><td>La z de “zapato”. Ventaja española. Audio: <a href="/audio/sonido-th-entre-dientes.html">TH entre dientes</a>.</td></tr>
                <tr><td><span class="ipa">/ð/</span></td><td>this</td><td>UK y US /ðɪs/</td><td>Casi</td><td>Como la d suave de “nada”, pero con la lengua entre los dientes y más firme. Audio: <a href="/audio/sonido-th-entre-dientes.html">TH entre dientes</a>.</td></tr>
                <tr><td><span class="ipa">/s/</span></td><td>sun</td><td>UK y US /sʌn/</td><td>Sí</td><td>Como la nuestra.</td></tr>
                <tr><td><span class="ipa">/z/</span></td><td>zoo</td><td>UK y US /zuː/</td><td>No (como sonido propio)</td><td>Un zumbido de abeja. Es la s de “mismo” en la pronunciación de mucha gente.</td></tr>
                <tr><td><span class="ipa">/ʃ/</span></td><td>she</td><td>UK y US /ʃiː/</td><td>No</td><td>El “sh” de pedir silencio. Audio: <a href="/audio/door-floor-score-shore-roar-soar.html">shore</a>.</td></tr>
                <tr><td><span class="ipa">/ʒ/</span></td><td>vision</td><td>UK y US /ˈvɪʒən/</td><td>No</td><td>Una /ʃ/ con vibración, parecida a la ll de muchos argentinos.</td></tr>
                <tr><td><span class="ipa">/h/</span></td><td>hat</td><td>UK y US /hæt/</td><td>No</td><td>No es la j española, que raspa: es solo aire, como echar vaho en un cristal. Audio: <a href="/audio/hello-hard.html">hello, hard</a>.</td></tr>
                <tr><td><span class="ipa">/m/</span></td><td>man</td><td>UK y US /mæn/</td><td>Sí</td><td>Como la nuestra.</td></tr>
                <tr><td><span class="ipa">/n/</span></td><td>net</td><td>UK y US /net/</td><td>Sí</td><td>Como la nuestra.</td></tr>
                <tr><td><span class="ipa">/ŋ/</span></td><td>sing</td><td>UK y US /sɪŋ/</td><td>Sí, pero solo antes de k o g</td><td>La n de “tengo”. En inglés aparece al final sin g detrás. Audio: <a href="/audio/hanging.html">hanging</a>.</td></tr>
                <tr><td><span class="ipa">/l/</span></td><td>leg</td><td>UK y US /leɡ/</td><td>Sí, a principio de sílaba</td><td>Clara al principio (<a href="/audio/light-love-listen-like-late-learn-laugh.html">light, love</a>) y oscura al final (<a href="/audio/skill-goal-ball-full-world-call-feel-school.html">skill, ball, feel</a>).</td></tr>
                <tr><td><span class="ipa">/r/</span></td><td>red</td><td>UK y US /red/</td><td>No</td><td>No vibra ni golpea: la lengua se recoge hacia atrás sin tocar nada. Audio: <a href="/audio/red-car-around-right-sorry.html">red, right, sorry</a>.</td></tr>
                <tr><td><span class="ipa">/j/</span></td><td>yes</td><td>UK y US /jes/</td><td>Sí</td><td>Como la i de “bien”, más suave que nuestra y: ni “jes” ni “dyes”. Audio: <a href="/audio/yellow-young-you-yes.html">yellow, young, you, yes</a>.</td></tr>
                <tr><td><span class="ipa">/w/</span></td><td>wet</td><td>UK y US /wet/</td><td>Sí</td><td>Como la u de “bueno”, sin meter una g delante. Está en <em>walk</em> y <em>would</em>, del audio de letras mudas.</td></tr>
                </tbody>
                </table>
                <div class="lesson-box"><strong>La ventaja española que nadie te cuenta:</strong> si eres de una zona donde se distingue “casa” de “caza”, ya pronuncias <span class="ipa">/θ/</span> todos los días. El sonido de <em>think</em> es tu z. Y la d suave de “nada” está muy cerca de <span class="ipa">/ð/</span>: solo te falta sacar un poco la lengua. Lo explicamos con detalle en el artículo del <a href="/articulos/sonido-th-ingles.html">sonido TH</a>.</div>

                <h2 id="americano-britanico">Fonética americana y británica: las diferencias clave</h2>
                <p>Los diccionarios suelen dar dos transcripciones, UK y US. Estas son las diferencias que más vas a ver:</p>
                <table class="data-table">
                <thead><tr><th>Diferencia</th><th>Ejemplos</th><th>UK</th><th>US</th></tr></thead>
                <tbody>
                <tr><td>El diptongo de <em>go</em></td><td>go, home</td><td>/ɡəʊ/, /həʊm/</td><td>/ɡoʊ/, /hoʊm/</td></tr>
                <tr><td>La r después de vocal</td><td>car, bird, teacher</td><td>/kɑː/, /bɜːd/, /ˈtiːtʃə/</td><td>/kɑːr/, /bɝːd/, /ˈtiːtʃɚ/</td></tr>
                <tr><td>La vocal de <em>bath</em></td><td>bath, ask, dance</td><td>/bɑːθ/, /ɑːsk/, /dɑːns/</td><td>/bæθ/, /æsk/, /dæns/</td></tr>
                <tr><td>La vocal de <em>hot</em></td><td>hot, stop</td><td>/hɒt/, /stɒp/</td><td>/hɑːt/, /stɑːp/</td></tr>
                <tr><td>La t entre vocales</td><td>better, city</td><td>/ˈbetə/, /ˈsɪti/</td><td>/ˈbet̬ɚ/, /ˈsɪt̬i/</td></tr>
                </tbody>
                </table>
                <ul>
                <li><strong>La r rótica:</strong> el inglés americano pronuncia la r siempre que está escrita. El británico estándar solo la pronuncia delante de vocal: <em>car</em> es <span class="ipa">/kɑː/</span>, pero en <em>car is</em> la r reaparece para enlazar. En ningún acento vibra como la nuestra; practícala con <a href="/audio/red-car-around-right-sorry.html">red, car, around, right y sorry</a>.</li>
                <li><strong>Diptongos que se convierten en vocal + r:</strong> por eso <em>beer</em>, <em>bear</em> y <em>tour</em> son <span class="ipa">/bɪr/</span>, <span class="ipa">/ber/</span> y <span class="ipa">/tʊr/</span> en EE. UU.</li>
                <li><strong>La flap T:</strong> en americano, la t entre vocales (cuando la sílaba siguiente es átona) se convierte en un toque rápido, casi idéntico a nuestra r de “pero”: <em>better</em> suena parecido a “bérer”. Cambridge lo marca con <span class="ipa">t̬</span>. En palabras como <em>button</em> o <em>mountain</em>, en cambio, la t americana suele convertirse en un pequeño corte en la garganta. Practica con <a href="/audio/mountain-button-cotton-manhattan.html">mountain, button, cotton y Manhattan</a>.</li>
                <li><strong>Palabras que cambian por completo:</strong> <em>either</em> se oye como <span class="ipa">/ˈiːðɚ/</span> y como <span class="ipa">/ˈaɪðə/</span>. La primera domina en EE. UU. y la segunda es muy común en Reino Unido, aunque las dos se usan en ambos países. Escúchalas en <a href="/audio/either-american-either-british.html">either americano y británico</a>.</li>
                </ul>
                <p>¿Cuál aprender? Ninguna es más correcta. Elige un modelo para hablar (el que más escuches) y acostúmbrate a entender los dos.</p>

                <h2 id="acento-longitud">Los símbolos que no son sonidos: ˈ, ˌ y ː</h2>
                <p>Tres marcas pequeñas que cambian mucho:</p>
                <ul>
                <li><strong><span class="ipa">ˈ</span> (acento principal):</strong> va <em>delante</em> de la sílaba fuerte, no encima de la vocal como nuestra tilde. <em>Hotel</em> es UK <span class="ipa">/həʊˈtel/</span>, US <span class="ipa">/hoʊˈtel/</span>: el peso cae en “tel”.</li>
                <li><strong><span class="ipa">ˌ</span> (acento secundario):</strong> una sílaba con algo de fuerza, menos que la principal. <em>Education</em> es UK <span class="ipa">/ˌedʒuˈkeɪʃən/</span>, US <span class="ipa">/ˌedʒəˈkeɪʃən/</span>. Escúchala en el audio de <a href="/audio/education-individual-gradual-schedule-procedure-residual.html">education, individual, gradual...</a>, palabras que además suelen llevar <span class="ipa">/dʒ/</span>.</li>
                <li><strong><span class="ipa">ː</span> (vocal larga):</strong> <em>ship</em> <span class="ipa">/ʃɪp/</span> frente a <em>sheep</em> <span class="ipa">/ʃiːp/</span>; <em>full</em> <span class="ipa">/fʊl/</span> frente a <em>fool</em> <span class="ipa">/fuːl/</span> (iguales en UK y US). Ojo: no solo cambia la duración, también la calidad de la vocal. Alargar una i española no te convierte <em>ship</em> en <em>sheep</em>.</li>
                </ul>
                <p>Un caso que enseña mucho: <em>pronounce</em> es <span class="ipa">/prəˈnaʊns/</span>, pero <em>pronunciation</em> es <span class="ipa">/prəˌnʌnsiˈeɪʃən/</span> (las dos, iguales en UK y US). Sin “noun” en medio: el sustantivo lleva <span class="ipa">/ʌ/</span>.</p>

                <h2 id="diccionario">¿Cómo se lee una entrada de diccionario? Ejemplo con Cambridge</h2>
                <p>Busca <em>computer</em> en el <a href="https://dictionary.cambridge.org/es/" target="_blank" rel="noopener noreferrer">diccionario Cambridge</a> y verás dos transcripciones, cada una con su botón de audio: UK <span class="ipa">/kəmˈpjuː.təʳ/</span> y US <span class="ipa">/kəmˈpjuː.t̬ɚ/</span>. Así se leen:</p>
                <ol>
                <li><strong>Las barras</strong> marcan el principio y el final de la transcripción.</li>
                <li><strong>Los puntos</strong> separan sílabas: kəm · pjuː · tə. Tres sílabas.</li>
                <li><strong><span class="ipa">ˈ</span></strong> va delante de la sílaba fuerte: com-PU-ter. Nunca “cómputer”.</li>
                <li><strong><span class="ipa">kəm</span></strong>: la primera vocal es una schwa, débil. No es “com” con o española.</li>
                <li><strong><span class="ipa">pjuː</span></strong>: la <span class="ipa">/j/</span> es la i de “bien” y <span class="ipa">ː</span> indica u larga. Suena “piu”.</li>
                <li><strong><span class="ipa">təʳ</span></strong> (UK): schwa final. La r pequeña y elevada indica que solo se pronuncia si la palabra siguiente empieza por vocal.</li>
                <li><strong><span class="ipa">t̬ɚ</span></strong> (US): la t es el toque rápido tipo “pero” y la vocal final lleva r. Algo así como “kəm-PIU-rɚ”.</li>
                </ol>
                <p>Con estas siete claves puedes leer casi cualquier entrada. Y si te pierdes, pulsa el altavoz: el símbolo te dice qué buscar y el audio te lo confirma.</p>

                <h2 id="practica">Cómo aprender fonética inglesa sin agobiarte</h2>
                <p>No hace falta memorizar los 44 símbolos de golpe. Para principiantes, este orden funciona:</p>
                <ol>
                <li><strong>Primero, los que ya tienes.</strong> <span class="ipa">/p/</span>, <span class="ipa">/b/</span>, <span class="ipa">/m/</span>, <span class="ipa">/f/</span>, <span class="ipa">/s/</span>, <span class="ipa">/tʃ/</span>, <span class="ipa">/θ/</span>, <span class="ipa">/eɪ/</span>, <span class="ipa">/aɪ/</span>... Te los aprendes en una tarde porque ya los usas.</li>
                <li><strong>Después, las cuatro vocales que más rentan:</strong> <span class="ipa">/ɪ/</span>, <span class="ipa">/ə/</span>, <span class="ipa">/æ/</span> y <span class="ipa">/ʌ/</span>. Aparecen en muchísimas palabras frecuentes.</li>
                <li><strong>Luego, las consonantes que no tenemos:</strong> <span class="ipa">/v/</span>, <span class="ipa">/z/</span>, <span class="ipa">/ʃ/</span>, <span class="ipa">/dʒ/</span>, <span class="ipa">/h/</span> y la <span class="ipa">/r/</span> inglesa.</li>
                <li><strong>Cada vez que busques una palabra, lee la transcripción antes de pulsar el audio.</strong> Intenta decirla y luego compruébala. En dos semanas lo harás sin pensar.</li>
                </ol>
                <p>Para ver los símbolos en acción con casos muy prácticos, sigue con la <a href="/articulos/pronunciacion-ed-ingles.html">pronunciación de -ed</a> (/t/, /d/, /ɪd/) o con <a href="/articulos/como-se-pronuncia-the.html">cómo se pronuncia THE</a>, donde la schwa y la <span class="ipa">/ð/</span> trabajan juntas.</p>
        """,
    },
    {
        "slug": "pronunciacion-ed-ingles",
        "category": "Pronunciación",
        "title": "Pronunciación de -ed en inglés: cuándo suena /t/, /d/ o /ɪd/",
        "seo_title": "Pronunciación de -ed en inglés: regla /t/, /d/ y /ɪd/",
        "description": "Pronunciación de la terminación -ed en inglés: cuándo suena /t/, /d/ o /ɪd/, el truco de la garganta, listas de verbos y 15 ejercicios resueltos.",
        "lede": "Worked, played y wanted terminan igual por escrito, pero no suenan igual. La regla de -ed es corta, casi no tiene excepciones y se aprende con la mano en la garganta.",
        "reading": "10 minutos",
        "published": "2026-10-11",
        "from_book": False,
        "toc": [
            ("regla", "La regla"),
            ("vibra", "Truco de la garganta"),
            ("listas", "Listas de verbos"),
            ("errores", "Errores típicos"),
            ("adjetivos", "Adjetivos en -ed"),
            ("ejercicios", "Ejercicios"),
            ("practica", "Práctica"),
        ],
        "related": [
            "alfabeto-fonetico-ingles",
            "ligar-palabras-ingles",
            "vocales-ingles-cortas-largas",
            "pronunciacion-ingles-para-espanoles",
        ],
        "quick_answer": "La terminación <strong>-ed</strong> se pronuncia de tres formas según el último sonido del verbo: <strong>/ɪd/</strong> si acaba en /t/ o /d/ (<em>wanted</em>, <em>needed</em>); <strong>/t/</strong> si acaba en un sonido sordo como /p/, /k/, /f/, /s/, /ʃ/ o /tʃ/ (<em>stopped</em>, <em>worked</em>); y <strong>/d/</strong> en el resto de casos (<em>played</em>, <em>lived</em>).",
        "faq": [
            ("¿Cuándo se pronuncia la -ed como /ɪd/?", "Cuando el verbo base termina en sonido /t/ o /d/, como <em>wanted</em>, <em>needed</em>, <em>started</em> o <em>decided</em>. Es el único caso en el que la -ed añade una sílaba. Aparte, unos pocos adjetivos como <em>naked</em> o <em>wicked</em> también suenan con /ɪd/."),
            ("¿Por qué worked no se pronuncia “work-ed”?", "Porque <em>work</em> termina en /k/, un sonido sordo, y la -ed se adapta convirtiéndose en una simple /t/ pegada al final: <span class=\"ipa\">/wɜːkt/</span> en británico y <span class=\"ipa\">/wɝːkt/</span> en americano. <em>Worked</em> tiene una sola sílaba, igual que <em>work</em>."),
            ("¿Cómo se pronuncia used to?", "<em>Used to</em> (solía) se pronuncia con /s/ y /t/, aproximadamente <span class=\"ipa\">/ˈjuːs tə/</span>, tanto en británico como en americano. En cambio, <em>used</em> como pasado de <em>use</em> (usé, utilicé) suena <span class=\"ipa\">/juːzd/</span>, con /z/ y /d/."),
            ("¿Los adjetivos terminados en -ed se pronuncian igual que los verbos?", "Casi siempre sí: <em>tired</em> suena con /d/, <em>relaxed</em> con /t/ e <em>interested</em> con /ɪd/. Pero algunos adjetivos suenan con /ɪd/ aunque no les toque, como <em>naked</em>, <em>wicked</em> o <em>crooked</em>, y otros cambian según el uso, como <em>learned</em>, <em>aged</em> o <em>blessed</em>."),
            ("¿La -s del plural sigue la misma regla que la -ed?", "Sí, con la misma lógica: suena /s/ después de un sonido sordo (<em>cats</em>), /z/ después de un sonido sonoro (<em>dogs</em>) e /ɪz/ después de /s/, /z/, /ʃ/, /ʒ/, /tʃ/ o /dʒ/ (<em>buses</em>, <em>watches</em>). Lo mismo vale para la tercera persona del presente: <em>works</em>, <em>plays</em>, <em>watches</em>."),
        ],
        "body": """
                <p>La terminación <strong>-ed</strong> del pasado de los verbos regulares tiene truco: siempre se escribe igual, pero se pronuncia de tres maneras distintas. <em>Worked</em> termina en <span class="ipa">/t/</span>, <em>played</em> en <span class="ipa">/d/</span> y <em>wanted</em> en <span class="ipa">/ɪd/</span>. Lo que casi nunca hace es sonar “e-d”, como la leeríamos en español.</p>
                <p>La buena noticia es que la regla de pronunciación de -ed es de las pocas del inglés que funcionan casi siempre. Cuando la entiendes con el cuerpo (literalmente: con la mano en la garganta), deja de ser teoría.</p>

                <h2 id="regla">¿Cómo se pronuncia -ed en inglés? La regla de los tres sonidos</h2>
                <p>Todo depende del <strong>último sonido</strong> del verbo base, no de la última letra:</p>
                <table class="data-table">
                <thead><tr><th>Si el verbo termina en...</th><th>La -ed suena</th><th>Ejemplos</th></tr></thead>
                <tbody>
                <tr><td>/t/ o /d/</td><td><span class="ipa">/ɪd/</span> (añade una sílaba)</td><td>wanted, needed, decided</td></tr>
                <tr><td>Un sonido sordo: /p/, /k/, /f/, /s/, /ʃ/, /tʃ/, /θ/</td><td><span class="ipa">/t/</span></td><td>stopped, worked, laughed, missed, washed, watched</td></tr>
                <tr><td>Un sonido sonoro: cualquier vocal, /b/, /ɡ/, /v/, /z/, /ʒ/, /dʒ/, /ð/, /m/, /n/, /ŋ/, /l/, /r/</td><td><span class="ipa">/d/</span></td><td>played, lived, called, cleaned, closed</td></tr>
                </tbody>
                </table>
                <p>Fíjate en que el inglés solo añade una sílaba en el primer caso. Tiene lógica: si el verbo ya acaba en /t/ o /d/, pegarle otra /t/ o /d/ no se oiría, así que se mete una vocal en medio. En los demás casos, la -ed se pega a la consonante final sin ninguna vocal: <em>worked</em> tiene una sola sílaba, igual que <em>work</em>.</p>

                <h2 id="vibra">El truco de la garganta: sonidos que vibran y sonidos que no</h2>
                <p>La diferencia entre /t/ y /d/ depende de si el sonido final del verbo es <strong>sordo</strong> (las cuerdas vocales no vibran) o <strong>sonoro</strong> (sí vibran). Suena técnico, pero se comprueba en cinco segundos:</p>
                <ol>
                <li>Pon los dedos sobre la garganta, a la altura de la nuez.</li>
                <li>Di “sssss”, como una serpiente. No notas nada: es un sonido sordo.</li>
                <li>Ahora haz un zumbido de abeja, “zzzzz”. Notas un cosquilleo: es sonoro.</li>
                <li>Di una vocal larga, “aaaaa”. También vibra: <strong>todas las vocales son sonoras</strong>.</li>
                </ol>
                <p>Cuidado con un detalle muy español: nuestra Z de “zapato” no es ese zumbido, sino el sonido de <em>think</em>. El zumbido de abeja es la /z/ inglesa de <em>zoo</em>. Es el mismo truco que se usa para distinguir los dos tipos de <a href="/articulos/sonido-th-ingles.html">sonido TH</a>.</p>
                <p>Ahora aplica el truco al final del verbo. Di <em>stop</em> y quédate en la /p/: no vibra, así que la -ed tampoco vibrará y sonará /t/. Di <em>live</em> y alarga la /v/: vibra, así que la -ed será /d/. La garganta no quiere encender y apagar la voz en mitad de un grupo de consonantes: si el sonido anterior vibra, la -ed vibra; si no, tampoco.</p>
                <div class="lesson-box"><strong>Atento a las letras que engañan:</strong> lo que cuenta es el sonido. <em>Fixed</em> acaba en la letra x, pero en el sonido /s/ (<em>fix</em> es <span class="ipa">/fɪks/</span>), así que suena /t/. <em>Laughed</em> acaba en gh, que aquí suena /f/: también /t/. <em>Closed</em> y <em>missed</em> se escriben con s, pero <em>close</em> acaba en /z/ (sonoro: /d/) y <em>miss</em> en /s/ (sordo: /t/). Y <em>played</em> o <em>studied</em> terminan en vocal: /d/.</div>

                <h2 id="listas">Listas de verbos regulares por sonido</h2>
                <h3>-ed como /t/: worked, stopped, watched...</h3>
                <table class="data-table">
                <thead><tr><th>Pasado</th><th>El verbo base termina en</th><th>Significado</th></tr></thead>
                <tbody>
                <tr><td>worked</td><td>/k/</td><td>trabajé</td></tr>
                <tr><td>stopped</td><td>/p/</td><td>paré, dejé de</td></tr>
                <tr><td>watched</td><td>/tʃ/</td><td>vi (la tele, una peli)</td></tr>
                <tr><td>laughed</td><td>/f/</td><td>me reí</td></tr>
                <tr><td>missed</td><td>/s/</td><td>eché de menos, perdí (el bus)</td></tr>
                <tr><td>fixed</td><td>/s/ (de /ks/)</td><td>arreglé</td></tr>
                <tr><td>washed</td><td>/ʃ/</td><td>lavé</td></tr>
                <tr><td>helped</td><td>/p/</td><td>ayudé</td></tr>
                <tr><td>looked</td><td>/k/</td><td>miré, parecía</td></tr>
                <tr><td>talked</td><td>/k/ (la l es muda)</td><td>hablé</td></tr>
                </tbody>
                </table>
                <h3>-ed como /d/: played, lived, called...</h3>
                <table class="data-table">
                <thead><tr><th>Pasado</th><th>El verbo base termina en</th><th>Significado</th></tr></thead>
                <tbody>
                <tr><td>played</td><td>vocal (/eɪ/)</td><td>jugué, toqué (un instrumento)</td></tr>
                <tr><td>lived</td><td>/v/</td><td>viví</td></tr>
                <tr><td>called</td><td>/l/</td><td>llamé</td></tr>
                <tr><td>cleaned</td><td>/n/</td><td>limpié</td></tr>
                <tr><td>opened</td><td>/n/</td><td>abrí</td></tr>
                <tr><td>loved</td><td>/v/</td><td>me encantó, quise</td></tr>
                <tr><td>studied</td><td>vocal (/i/)</td><td>estudié</td></tr>
                <tr><td>cried</td><td>vocal (/aɪ/)</td><td>lloré</td></tr>
                <tr><td>listened</td><td>/n/</td><td>escuché</td></tr>
                <tr><td>closed</td><td>/z/</td><td>cerré</td></tr>
                </tbody>
                </table>
                <h3>-ed como /ɪd/: wanted, needed, decided...</h3>
                <table class="data-table">
                <thead><tr><th>Pasado</th><th>El verbo base termina en</th><th>Significado</th></tr></thead>
                <tbody>
                <tr><td>wanted</td><td>/t/</td><td>quise, quería</td></tr>
                <tr><td>needed</td><td>/d/</td><td>necesité</td></tr>
                <tr><td>decided</td><td>/d/</td><td>decidí</td></tr>
                <tr><td>started</td><td>/t/</td><td>empecé</td></tr>
                <tr><td>visited</td><td>/t/</td><td>visité</td></tr>
                <tr><td>ended</td><td>/d/</td><td>terminó, acabó</td></tr>
                <tr><td>waited</td><td>/t/</td><td>esperé</td></tr>
                <tr><td>added</td><td>/d/</td><td>añadí</td></tr>
                <tr><td>hated</td><td>/t/</td><td>odié, odiaba</td></tr>
                <tr><td>invited</td><td>/t/</td><td>invité</td></tr>
                </tbody>
                </table>
                <p>La vocal de <span class="ipa">/ɪd/</span> es la I corta de <em>bit</em>: relajada, a medio camino entre nuestra i y nuestra e, nunca una e española clara. Practícala con el audio de <a href="/audio/bit-big-win-lip-clip.html">bit, big, win, lip y clip</a>. En inglés americano suele sonar todavía más neutra, y algunos diccionarios americanos la transcriben como <span class="ipa">/əd/</span>.</p>
                <h3>Transcripciones de referencia</h3>
                <table class="data-table">
                <thead><tr><th>Verbo</th><th>UK</th><th>US</th></tr></thead>
                <tbody>
                <tr><td>worked</td><td>/wɜːkt/</td><td>/wɝːkt/</td></tr>
                <tr><td>stopped</td><td>/stɒpt/</td><td>/stɑːpt/</td></tr>
                <tr><td>laughed</td><td>/lɑːft/</td><td>/læft/</td></tr>
                <tr><td>missed</td><td>/mɪst/</td><td>/mɪst/</td></tr>
                <tr><td>played</td><td>/pleɪd/</td><td>/pleɪd/</td></tr>
                <tr><td>lived</td><td>/lɪvd/</td><td>/lɪvd/</td></tr>
                <tr><td>closed</td><td>/kləʊzd/</td><td>/kloʊzd/</td></tr>
                <tr><td>cleaned</td><td>/kliːnd/</td><td>/kliːnd/</td></tr>
                <tr><td>needed</td><td>/ˈniːdɪd/</td><td>/ˈniːdɪd/</td></tr>
                <tr><td>decided</td><td>/dɪˈsaɪdɪd/</td><td>/dɪˈsaɪdɪd/</td></tr>
                <tr><td>added</td><td>/ˈædɪd/</td><td>/ˈædɪd/</td></tr>
                </tbody>
                </table>
                <p>¿Los símbolos te suenan a jeroglífico? Tienes la tabla completa explicada en el <a href="/articulos/alfabeto-fonetico-ingles.html">alfabeto fonético inglés para españoles</a>.</p>

                <h2 id="errores">Los errores típicos de los españoles con -ed</h2>
                <h3>1. Añadir una sílaba: “work-ed”</h3>
                <p>Es el error estrella. Leemos <em>worked</em> como se escribe y sale “uor-ked”, con dos sílabas. Al nativo le suena raro y le obliga a hacer un esfuerzo extra para entenderte. Recuerda: solo los verbos que terminan en /t/ o /d/ ganan una sílaba. <em>Worked</em>, <em>stopped</em>, <em>played</em>, <em>lived</em> o <em>cleaned</em> tienen exactamente las mismas sílabas que <em>work</em>, <em>stop</em>, <em>play</em>, <em>live</em> o <em>clean</em>.</p>
                <p>Prueba rápida: cuenta las sílabas con palmadas. <em>Work</em>, una palmada; <em>worked</em>, una. <em>Want</em>, una; <em>wanted</em>, dos.</p>
                <h3>2. Comerse la consonante final</h3>
                <p>El error contrario es igual de frecuente. En español, las consonantes finales son débiles (decimos “Madrí” o “verdá” y no pasa nada), así que tendemos a perder la /t/ o la /d/ del final. Resultado: <em>I worked yesterday</em> suena como <em>I work yesterday</em>, y parece que no sabes usar el pasado cuando sí sabes. Hazla corta, pero que exista.</p>
                <p>Los grupos de consonantes finales, como el /lpt/ de <em>helped</em> o el /kst/ de <em>fixed</em>, son un buen entrenamiento. Practica ese tipo de final con el audio de <a href="/audio/texts-guests-desks-costs.html">texts, guests, desks y costs</a>: si puedes con esas palabras, puedes con cualquier pasado.</p>
                <h3>3. Pronunciar la -ed separada de la palabra siguiente</h3>
                <p>En la conversación real, la -ed se engancha a la palabra que viene detrás, sobre todo si empieza por vocal:</p>
                <div class="example-grid">
                <div class="mini-card"><strong>worked out</strong><span>Suena casi como “work-tout”. <em>It worked out</em> = salió bien.</span></div>
                <div class="mini-card"><strong>stopped it</strong><span>Casi “stop-tit”. <em>I stopped it</em> = lo paré.</span></div>
                <div class="mini-card"><strong>lived in</strong><span>Casi “liv-din”. <em>I lived in Dublin</em> = viví en Dublín.</span></div>
                <div class="mini-card"><strong>picked up</strong><span>Casi “pick-tup”. <em>She picked up the phone</em> = cogió el teléfono.</span></div>
                </div>
                <p>Cuando la palabra siguiente empieza por consonante, la /t/ o la /d/ a veces casi no se oye en habla rápida (<em>I watched TV</em>, <em>I missed the bus</em>). Por eso el contexto importa tanto para entender a un nativo. Lo explicamos a fondo en <a href="/articulos/ligar-palabras-ingles.html">cómo ligar palabras en inglés</a>, y puedes practicar el enganche con <a href="/audio/pick-it-up.html">pick it up</a>.</p>

                <h2 id="adjetivos">Adjetivos en -ed que suenan /ɪd/ aunque “no toque”</h2>
                <p>La mayoría de los adjetivos terminados en -ed siguen la regla normal: <em>tired</em> y <em>bored</em> suenan con /d/, <em>relaxed</em> con /t/, e <em>interested</em> o <em>excited</em> con /ɪd/ porque la raíz acaba en /t/. Pero hay un grupo pequeño que suena <span class="ipa">/ɪd/</span> aunque el sonido anterior no sea /t/ ni /d/:</p>
                <table class="data-table">
                <thead><tr><th>Adjetivo</th><th>UK</th><th>US</th><th>Significado y matices</th></tr></thead>
                <tbody>
                <tr><td>naked</td><td>/ˈneɪkɪd/</td><td>/ˈneɪkɪd/</td><td>desnudo</td></tr>
                <tr><td>wicked</td><td>/ˈwɪkɪd/</td><td>/ˈwɪkɪd/</td><td>malvado (y, en argot, “genial”)</td></tr>
                <tr><td>crooked</td><td>/ˈkrʊkɪd/</td><td>/ˈkrʊkɪd/</td><td>torcido; también corrupto</td></tr>
                <tr><td>beloved</td><td>/bɪˈlʌvɪd/, /bɪˈlʌvd/</td><td>/bɪˈlʌvɪd/, /bɪˈlʌvd/</td><td>querido, amado; se oyen las dos pronunciaciones</td></tr>
                <tr><td>learned (adj.)</td><td>/ˈlɜːnɪd/</td><td>/ˈlɝːnɪd/</td><td>erudito, culto. El verbo <em>learned</em> (aprendí) es /lɜːnd/ o /lɜːnt/ en UK y /lɝːnd/ en US</td></tr>
                <tr><td>aged (adj.)</td><td>/ˈeɪdʒɪd/</td><td>/ˈeɪdʒɪd/</td><td>anciano (<em>my aged parents</em>). En cambio, <em>aged 30</em> (de 30 años) es /eɪdʒd/</td></tr>
                <tr><td>blessed (adj.)</td><td>/ˈblesɪd/</td><td>/ˈblesɪd/</td><td>bendito, sagrado. Como verbo es /blest/, y en <em>I feel blessed</em> mucha gente también dice /blest/</td></tr>
                </tbody>
                </table>
                <p>En la misma familia entran <em>ragged</em> (andrajoso), <em>rugged</em> (escarpado, robusto) o <em>wretched</em> (desdichado), todos con /ɪd/. Y lo mismo pasa con algunos adverbios en <em>-edly</em>: <em>supposedly</em> (supuestamente), <em>allegedly</em> (presuntamente) o <em>deservedly</em> (merecidamente) pronuncian la -ed como /ɪd/, aunque <em>supposed</em> o <em>alleged</em> suenen con /d/.</p>

                <h2 id="ejercicios">Ejercicios de pronunciación de -ed (con soluciones)</h2>
                <p>Di cada verbo en voz alta, decide si la -ed suena /t/, /d/ o /ɪd/ y después abre la solución. Mano en la garganta si hace falta.</p>
                <details class="exercise"><summary>1. jumped</summary><p><strong>/t/</strong>: <span class="ipa">/dʒʌmpt/</span> (UK y US). <em>Jump</em> termina en /p/, que no vibra. Una sola sílaba.</p></details>
                <details class="exercise"><summary>2. danced</summary><p><strong>/t/</strong>: UK <span class="ipa">/dɑːnst/</span>, US <span class="ipa">/dænst/</span>. La e final es muda y la c suena /s/: sonido sordo.</p></details>
                <details class="exercise"><summary>3. changed</summary><p><strong>/d/</strong>: <span class="ipa">/tʃeɪndʒd/</span> (UK y US). <em>Change</em> termina en /dʒ/, que vibra. Nada de “chein-ched”.</p></details>
                <details class="exercise"><summary>4. painted</summary><p><strong>/ɪd/</strong>: <em>paint</em> termina en /t/, así que la -ed añade una sílaba: <em>pain-tid</em>.</p></details>
                <details class="exercise"><summary>5. hoped</summary><p><strong>/t/</strong>: UK <span class="ipa">/həʊpt/</span>, US <span class="ipa">/hoʊpt/</span>. <em>Hope</em> termina en /p/; la e escrita no suena.</p></details>
                <details class="exercise"><summary>6. arrived</summary><p><strong>/d/</strong>: <span class="ipa">/əˈraɪvd/</span> (UK y US). <em>Arrive</em> termina en /v/, sonora.</p></details>
                <details class="exercise"><summary>7. included</summary><p><strong>/ɪd/</strong>: <span class="ipa">/ɪnˈkluːdɪd/</span> (UK y US). <em>Include</em> termina en /d/.</p></details>
                <details class="exercise"><summary>8. coughed</summary><p><strong>/t/</strong>: UK <span class="ipa">/kɒft/</span>, US <span class="ipa">/kɑːft/</span>. La gh de <em>cough</em> suena /f/, sorda.</p></details>
                <details class="exercise"><summary>9. smiled</summary><p><strong>/d/</strong>: <span class="ipa">/smaɪld/</span> (UK y US). <em>Smile</em> termina en /l/, que vibra.</p></details>
                <details class="exercise"><summary>10. shouted</summary><p><strong>/ɪd/</strong>: <em>shout</em> termina en /t/, así que suena con dos sílabas: <em>shou-tid</em>.</p></details>
                <details class="exercise"><summary>11. asked</summary><p><strong>/t/</strong>: UK <span class="ipa">/ɑːskt/</span>, US <span class="ipa">/æskt/</span>. Termina en /k/. En habla rápida la k a veces casi desaparece, pero nunca suena “ask-ed”.</p></details>
                <details class="exercise"><summary>12. enjoyed</summary><p><strong>/d/</strong>: <span class="ipa">/ɪnˈdʒɔɪd/</span> (UK y US). Termina en vocal (el diptongo /ɔɪ/), y las vocales siempre vibran.</p></details>
                <details class="exercise"><summary>13. landed</summary><p><strong>/ɪd/</strong>: <span class="ipa">/ˈlændɪd/</span> (UK y US). <em>Land</em> termina en /d/.</p></details>
                <details class="exercise"><summary>14. used (I used your pen)</summary><p><strong>/d/</strong>: <span class="ipa">/juːzd/</span> (UK y US). El verbo <em>use</em> termina en /z/. Ojo: <em>used to</em> (solía) es otra historia y suena con /s/ y /t/.</p></details>
                <details class="exercise"><summary>15. baked</summary><p><strong>/t/</strong>: <span class="ipa">/beɪkt/</span> (UK y US). <em>Bake</em> termina en /k/; la e final es muda.</p></details>
                <p>¿Más de 12 aciertos? Ya tienes la regla. Si fallaste sobre todo con /t/ y /d/, vuelve al truco de la garganta; si fallaste con /ɪd/, repasa qué verbos acaban en /t/ o /d/.</p>

                <h2 id="practica">Cómo practicar la pronunciación de -ed</h2>
                <ol>
                <li><strong>Agrupa por sonido.</strong> Di diez verbos /t/ seguidos, luego diez /d/ y luego diez /ɪd/. El cerebro aprende antes el patrón que la excepción.</li>
                <li><strong>Cuenta sílabas con palmadas.</strong> Si <em>worked</em> te sale con dos palmadas, algo falla.</li>
                <li><strong>Cuéntate tu día en pasado.</strong> <em>I worked, I called my mum, I watched a series, I needed a nap.</em> En voz alta, mientras cocinas.</li>
                <li><strong>Grábate</strong> y escucha si las consonantes finales existen de verdad.</li>
                </ol>
                <p>La -ed es un buen ejemplo de algo que se repite en todo el inglés: lo escrito no manda, manda el sonido. Si quieres seguir por ahí, la guía de <a href="/articulos/pronunciacion-ingles-para-espanoles.html">pronunciación en inglés para españoles</a> te dice qué atacar después, y las <a href="/articulos/vocales-ingles-cortas-largas.html">vocales cortas y largas</a> son el siguiente gran salto.</p>
        """,
    },
    {
        "slug": "palabras-ingles-mal-pronunciadas",
        "category": "Pronunciación",
        "title": "40 palabras en inglés que los españoles pronunciamos mal (y cómo decirlas bien)",
        "seo_title": "Palabras en inglés mal pronunciadas en España: 40 ejemplos",
        "description": "Palabras en inglés mal pronunciadas en España: Nike, Colgate, comfortable, Wednesday, footing… 40 ejemplos con IPA y cómo decirlas bien.",
        "lede": "De Nike a Wednesday, pasando por beach y el famoso footing: la lista para dejar de sonar a español justo en las palabras que más repites.",
        "reading": "10 minutos",
        "published": "2026-10-11",
        "from_book": False,
        "toc": [
            ("marcas", "Marcas"),
            ("palabras-cotidianas", "Palabras de cada día"),
            ("lios", "Las que meten en líos"),
            ("ingles-falso", "Inglés falso"),
            ("por-que", "Por qué pasa"),
            ("comprobar", "Cómo comprobarlo"),
        ],
        "related": [
            "letras-mudas-ingles",
            "vocales-ingles-cortas-largas",
            "alfabeto-fonetico-ingles",
            "pronunciacion-ingles-para-espanoles",
        ],
        "quick_answer": "Las palabras en inglés que más pronunciamos mal en España son marcas como <strong>Nike</strong> (<span class=\"ipa\">/ˈnaɪki/</span>, no “naik”), <strong>Colgate</strong> o <strong>McDonald's</strong> y palabras como <em>comfortable</em>, <em>vegetable</em>, <em>Wednesday</em>, <em>develop</em> o <em>beach</em>. Casi siempre fallamos por lo mismo: leer como se escribe, cargar la fuerza en otra sílaba y usar solo cinco vocales.",
        "faq": [
            ("¿Cómo se pronuncia Nike en inglés?", "Se pronuncia <span class=\"ipa\">/ˈnaɪki/</span> en británico y en americano, en dos sílabas: “NÁI-ki”. Decir “naik”, en una sola sílaba, es el error típico en España. El nombre viene de Niké, la diosa griega de la victoria, y por eso la E final suena."),
            ("¿Cómo se pronuncia McDonald's en inglés?", "<span class=\"ipa\">/məkˈdɒnəldz/</span> en británico y <span class=\"ipa\">/məkˈdɑːnəldz/</span> en americano. La primera sílaba es muy débil (“mek”), la fuerza va en DON y la palabra termina en <em>-ldz</em>."),
            ("¿Cómo se pronuncia comfortable en inglés?", "<span class=\"ipa\">/ˈkʌmftəbl/</span> en británico, en tres sílabas: “KÁMF-te-bl”. En americano también se oye <span class=\"ipa\">/ˈkʌmftərbl/</span>. En ningún caso se dice “com-for-téi-bol”."),
            ("¿Está mal decir Nike o Colgate a la española?", "Cuando hablas en español, no: es la pronunciación habitual en España. Cuando hablas en inglés, conviene usar la pronunciación inglesa, porque la versión española puede no reconocerse a la primera."),
            ("¿Se dice parking en inglés?", "<em>Parking</em> existe, pero significa la acción de aparcar o el sitio disponible para hacerlo. Para el lugar se dice <em>car park</em> en Reino Unido y <em>parking lot</em> (o <em>parking garage</em>, si es un edificio) en Estados Unidos."),
        ],
        "body": """
                <p>Hay palabras en inglés que en España llevamos años diciendo a nuestra manera: <em>naik</em>, <em>colgáte</em>, <em>mac-dó-nals</em>, <em>comfortéibol</em>… Dentro de una conversación en español no pasa nada; es lo normal. El problema llega cuando las usas hablando inglés y la otra persona tarda dos segundos de más en entenderte, o te entiende otra cosa.</p>
                <p>Esta lista reúne 40 palabras en inglés mal pronunciadas en España, agrupadas por tipo de error: marcas, palabras de cada día, pares que pueden meterte en un lío e “inglés” que solo existe aquí. Cada una lleva su pronunciación en IPA (británica y americana), la versión española típica y cómo arreglarla. Si los símbolos te suenan a jeroglífico, echa antes un vistazo al <a href="/articulos/alfabeto-fonetico-ingles.html">alfabeto fonético inglés para españoles</a>.</p>
                <div class="lesson-box"><strong>Cómo leer las tablas:</strong> el símbolo <span class="ipa">ˈ</span> va delante de la sílaba fuerte. Las pistas en mayúsculas (NÁI-ki) son solo una aproximación con letras españolas para orientarte; el sonido de verdad está en la IPA y en los audios.</div>
                <h2 id="marcas">¿Cómo se pronuncian las marcas en inglés?</h2>
                <p>Las marcas son las más traicioneras porque las hemos oído toda la vida a la española, a veces incluso en los anuncios. Estas son las que más delatan a un español en Londres o en Nueva York:</p>
                <table class="data-table">
                    <thead>
                        <tr><th>Palabra</th><th>Pronunciación (IPA)</th><th>Error típico en España</th><th>Cómo arreglarlo</th></tr>
                    </thead>
                    <tbody>
                        <tr><td><strong>McDonald's</strong></td><td>UK <span class="ipa">/məkˈdɒnəldz/</span><br>US <span class="ipa">/məkˈdɑːnəldz/</span></td><td><em>mac-DÓ-nals</em>, con una “mac” muy abierta</td><td>La primera sílaba casi desaparece (“mek”) y la fuerza va en DON. Termina en <em>-ldz</em>. <a href="/audio/mcdonalds.html">Escúchalo</a>.</td></tr>
                        <tr><td><strong>Microsoft</strong></td><td>UK <span class="ipa">/ˈmaɪkrəsɒft/</span><br>US <span class="ipa">/ˈmaɪkroʊsɑːft/</span></td><td><em>micro-SÓF</em> o <em>maicro-SÓF</em>, con la fuerza al final y sin T</td><td>Fuerza en la primera sílaba (MÁI-kro-soft), empieza por “mai” y la T final se oye. <a href="/audio/microsoft-up-us-uncle-umbrella.html">Escúchalo</a>.</td></tr>
                        <tr><td><strong>Nike</strong></td><td>UK y US <span class="ipa">/ˈnaɪki/</span></td><td><em>naik</em>, en una sola sílaba</td><td>Dos sílabas: NÁI-ki. El nombre viene de Niké, la diosa griega de la victoria.</td></tr>
                        <tr><td><strong>Adidas</strong></td><td>UK <span class="ipa">/ˈædɪdæs/</span><br>US <span class="ipa">/əˈdiːdəs/</span></td><td><em>a-DÍ-das</em> con vocales españolas, que en realidad se acerca a la versión americana</td><td>En Reino Unido la fuerza va en la primera sílaba, con una /æ/ abierta: Á-di-das. Las dos versiones son correctas.</td></tr>
                        <tr><td><strong>Colgate</strong></td><td>UK <span class="ipa">/ˈkəʊlɡeɪt/</span><br>US <span class="ipa">/ˈkoʊlɡeɪt/</span></td><td><em>col-GÁ-te</em>, en tres sílabas</td><td>Dos sílabas y fuerza al principio: KÓUL-geit. La E final no suena.</td></tr>
                        <tr><td><strong>Levi's</strong></td><td>UK y US <span class="ipa">/ˈliːvaɪz/</span></td><td><em>LÉ-vis</em></td><td>LÍ-vais: la E suena como una i larga y la I es “ai”.</td></tr>
                        <tr><td><strong>Google</strong></td><td>UK y US <span class="ipa">/ˈɡuːɡl/</span></td><td><em>GÚ-guel</em>, con la segunda G suave</td><td>Las dos G son duras y no hay E: la L final cierra la palabra, GÚ-gl.</td></tr>
                        <tr><td><strong>YouTube</strong></td><td>UK <span class="ipa">/ˈjuːtjuːb/</span><br>US <span class="ipa">/ˈjuːtuːb/</span></td><td><em>lliú-tub</em>, con una Y española fuerte</td><td>La Y inglesa es suave, casi una i breve, como en <a href="/audio/yellow-young-you-yes.html">you y yes</a>. En británico, “tiub”; en americano, “tub”.</td></tr>
                        <tr><td><strong>Netflix</strong></td><td>UK y US <span class="ipa">/ˈnetflɪks/</span></td><td><em>NÉ-flis</em>, sin T y sin K</td><td>Mantén la T, aunque sea breve, y termina en /ks/, como en <em>taxi</em>.</td></tr>
                        <tr><td><strong>IKEA</strong></td><td>UK y US <span class="ipa">/aɪˈkiːə/</span></td><td><em>i-KÉ-a</em></td><td>En inglés se dice ai-KÍ-a. Con “ikéa” te entenderán, pero sonará claramente a español.</td></tr>
                        <tr><td><strong>Spotify</strong></td><td>UK <span class="ipa">/ˈspɒtɪfaɪ/</span><br>US <span class="ipa">/ˈspɑːtɪfaɪ/</span></td><td><em>es-po-ti-FÁI</em></td><td>Sin E delante de la S y con la fuerza en la primera: SPÓ-ti-fai.</td></tr>
                    </tbody>
                </table>
                <p>Adidas es el caso curioso: si la dices “adídas”, como se oye a menudo en España, estás más cerca de la pronunciación americana que de la británica. Aquí no hay error, solo dos acentos.</p>
                <h2 id="palabras-cotidianas">Palabras en inglés mal pronunciadas en España: las de todos los días</h2>
                <p>Aquí no hay marcas, solo vocabulario que usas cada semana. Los errores se repiten en tres patrones, así que las agrupo por patrón: si entiendes el patrón, corriges muchas más palabras que las de la lista.</p>
                <h3>Sílabas que sobran y letras que no suenan</h3>
                <p>El cerebro español quiere pronunciar todas las letras. El inglés se come sílabas enteras y deja letras escritas solo por tradición (tienes más ejemplos en <a href="/articulos/letras-mudas-ingles.html">letras mudas en inglés</a>).</p>
                <table class="data-table">
                    <thead>
                        <tr><th>Palabra</th><th>Pronunciación (IPA)</th><th>Error típico en España</th><th>Cómo arreglarlo</th></tr>
                    </thead>
                    <tbody>
                        <tr><td><strong>comfortable</strong></td><td>UK <span class="ipa">/ˈkʌmftəbl/</span><br>US <span class="ipa">/ˈkʌmftərbl/</span></td><td><em>com-for-TÉI-bol</em></td><td>Tres sílabas y fuerza en la primera: KÁMF-te-bl. La sílaba “for” desaparece.</td></tr>
                        <tr><td><strong>vegetable</strong></td><td>UK y US <span class="ipa">/ˈvedʒtəbl/</span></td><td><em>ve-ge-TÉI-bol</em></td><td>VÉCH-te-bl, con la J de <a href="/audio/jump-john-job-jungle-enjoy.html">job</a>: la segunda E no suena y <em>-table</em> no se lee como la mesa.</td></tr>
                        <tr><td><strong>chocolate</strong></td><td>UK <span class="ipa">/ˈtʃɒklət/</span><br>US <span class="ipa">/ˈtʃɑːklət/</span></td><td><em>cho-co-LA-te</em></td><td>Dos sílabas: CHÓK-let. La O del medio y la E final no suenan.</td></tr>
                        <tr><td><strong>interesting</strong></td><td>UK y US <span class="ipa">/ˈɪntrəstɪŋ/</span></td><td><em>in-te-RÉS-ting</em></td><td>Fuerza en la primera y, normalmente, tres sílabas: ÍN-tres-ting.</td></tr>
                        <tr><td><strong>Wednesday</strong></td><td>UK y US <span class="ipa">/ˈwenzdeɪ/</span></td><td><em>uéd-nes-dei</em></td><td>UÉNS-dei: la primera D y la segunda E son pura decoración.</td></tr>
                        <tr><td><strong>clothes</strong></td><td>UK <span class="ipa">/kləʊðz/</span><br>US <span class="ipa">/kloʊðz/</span></td><td><em>CLÓ-zes</em>, en dos sílabas</td><td>Una sola sílaba. Muchos nativos la simplifican a <span class="ipa">/kləʊz/</span> (US <span class="ipa">/kloʊz/</span>), igual que <em>close</em>.</td></tr>
                        <tr><td><strong>island</strong></td><td>UK y US <span class="ipa">/ˈaɪlənd/</span></td><td><em>ÍS-land</em></td><td>ÁI-lend. La S es muda, igual que en <em>aisle</em>.</td></tr>
                        <tr><td><strong>salmon</strong></td><td>UK y US <span class="ipa">/ˈsæmən/</span></td><td><em>SAL-mon</em></td><td>SÁ-men, sin L. Escúchala en el <a href="/audio/walk-talk-half-calm-salmon-would-should-yolk-palm-chalk-walkie-talkie.html">audio de letras mudas</a>.</td></tr>
                        <tr><td><strong>queue</strong></td><td>UK y US <span class="ipa">/kjuː/</span></td><td><em>cue-ue</em> o <em>kiu-é</em></td><td>Suena exactamente como la letra Q: “kiu”. En EE. UU. se usa más <em>line</em>.</td></tr>
                        <tr><td><strong>Worcestershire</strong> (sauce)</td><td>UK <span class="ipa">/ˈwʊstəʃə/</span><br>US <span class="ipa">/ˈwʊstərʃər/</span></td><td><em>uor-ces-ter-SHÁI-re</em></td><td>En británico, UÚS-te-sha: tres sílabas para catorce letras. Es la salsa que en España mucha gente llama “salsa Perrins”.</td></tr>
                    </tbody>
                </table>
                <h3>La fuerza en la sílaba equivocada</h3>
                <p>En inglés, cargar la fuerza en otra sílaba puede volver irreconocible una palabra que pronuncias perfecta en todo lo demás. Y no hay tildes que te avisen.</p>
                <table class="data-table">
                    <thead>
                        <tr><th>Palabra</th><th>Pronunciación (IPA)</th><th>Error típico en España</th><th>Cómo arreglarlo</th></tr>
                    </thead>
                    <tbody>
                        <tr><td><strong>develop</strong></td><td>UK y US <span class="ipa">/dɪˈveləp/</span></td><td><em>de-ve-LÓP</em></td><td>di-VÉ-lep: la fuerza va en la segunda sílaba y las otras dos vocales son débiles.</td></tr>
                        <tr><td><strong>determine</strong></td><td>UK <span class="ipa">/dɪˈtɜːmɪn/</span><br>US <span class="ipa">/dɪˈtɝːmɪn/</span></td><td><em>de-ter-MÁIN</em>, como si acabara en <em>mine</em></td><td>di-TÉR-min. El final es un “min” corto, nunca “main”.</td></tr>
                        <tr><td><strong>event</strong></td><td>UK y US <span class="ipa">/ɪˈvent/</span></td><td><em>É-vent</em></td><td>i-VÉNT: la primera vocal es débil y la fuerza va al final.</td></tr>
                        <tr><td><strong>colleague</strong></td><td>UK <span class="ipa">/ˈkɒliːɡ/</span><br>US <span class="ipa">/ˈkɑːliːɡ/</span></td><td><em>co-LÍG</em> o <em>co-LÉ-gue</em></td><td>KÓ-liig: fuerza en la primera, i larga en la segunda y sin E final.</td></tr>
                        <tr><td><strong>recipe</strong></td><td>UK y US <span class="ipa">/ˈresəpi/</span></td><td><em>ri-SÁIP</em>, leída como si rimara con <em>type</em></td><td>Tres sílabas: RÉ-se-pi. La E final sí suena, como una i.</td></tr>
                        <tr><td><strong>idea</strong></td><td>UK <span class="ipa">/aɪˈdɪə/</span><br>US <span class="ipa">/aɪˈdiːə/</span></td><td><em>i-DÉ-a</em></td><td>ai-DÍ-a: empieza por “ai” y la fuerza va en la segunda sílaba.</td></tr>
                    </tbody>
                </table>
                <h3>Sonidos que el español no tiene (o no ahí)</h3>
                <table class="data-table">
                    <thead>
                        <tr><th>Palabra</th><th>Pronunciación (IPA)</th><th>Error típico en España</th><th>Cómo arreglarlo</th></tr>
                    </thead>
                    <tbody>
                        <tr><td><strong>women</strong></td><td>UK y US <span class="ipa">/ˈwɪmɪn/</span></td><td><em>UÓ-men</em>, igual que <em>woman</em></td><td>UÍ-min. El singular <em>woman</em> es <span class="ipa">/ˈwʊmən/</span>; al escribir cambia la segunda vocal (a → e), pero al hablar lo que más se nota es el cambio de la primera: <span class="ipa">/ʊ/</span> → <span class="ipa">/ɪ/</span>.</td></tr>
                        <tr><td><strong>suite</strong></td><td>UK y US <span class="ipa">/swiːt/</span></td><td><em>suit</em>, como el traje</td><td>Suena igual que <em>sweet</em>. El traje, <em>suit</em>, es <span class="ipa">/suːt/</span>.</td></tr>
                        <tr><td><strong>hotel</strong></td><td>UK <span class="ipa">/həʊˈtel/</span><br>US <span class="ipa">/hoʊˈtel/</span></td><td><em>otél</em> o <em>jotél</em></td><td>El acento coincide con el español; lo que falla es la H: aire suave, como al empañar un cristal. Practica con <a href="/audio/hello-hard.html">hello y hard</a>.</td></tr>
                        <tr><td><strong>schedule</strong></td><td>UK <span class="ipa">/ˈʃedjuːl/</span><br>US <span class="ipa">/ˈskedʒuːl/</span></td><td><em>es-ke-DÚL</em></td><td>Sin E inicial y con la fuerza en la primera. En Reino Unido también se oye <span class="ipa">/ˈskedʒuːl/</span>. Escúchala en <a href="/audio/education-individual-gradual-schedule-procedure-residual.html">este audio</a>.</td></tr>
                        <tr><td><strong>pronunciation</strong></td><td>UK y US <span class="ipa">/prəˌnʌnsiˈeɪʃn/</span></td><td><em>pro-naun-sia-ción</em>, copiando el verbo <em>pronounce</em></td><td>El verbo es <em>pronounce</em> (<span class="ipa">/prəˈnaʊns/</span>), pero el sustantivo dice “nan”: pro-nan-si-ÉI-shen. La ironía es evidente.</td></tr>
                    </tbody>
                </table>
                <div class="lesson-box"><strong>La E fantasma:</strong> delante de S + consonante, el español mete una E: <em>estop</em>, <em>espanish</em>, <em>eskedul</em>. En inglés la palabra empieza directamente en la S. Practica con <a href="/audio/stop.html">stop</a> y <a href="/audio/i-am-spanish.html">I am Spanish</a>.</div>
                <h2 id="lios">¿Qué palabras en inglés pueden meterte en un lío?</h2>
                <p>Luego están los pares en los que una vocal mal medida convierte una palabra inocente en una palabrota. El subtítulo de <em>De FAK a Fluent</em> lo confiesa en la portada: “Consejos de un español que también confundió ‘beach’ con otra cosa”. No eres el primero ni serás el último.</p>
                <table class="data-table">
                    <thead>
                        <tr><th>Palabra</th><th>Pronunciación (IPA)</th><th>Error típico en España</th><th>Cómo arreglarlo</th></tr>
                    </thead>
                    <tbody>
                        <tr><td><strong>beach</strong></td><td>UK y US <span class="ipa">/biːtʃ/</span></td><td>Una i corta, que la acerca a <em>bitch</em> (<span class="ipa">/bɪtʃ/</span>), un insulto</td><td>I larga y tensa, estirando los labios como al sonreír: “biich”.</td></tr>
                        <tr><td><strong>sheet</strong></td><td>UK y US <span class="ipa">/ʃiːt/</span></td><td><em>chit</em>, o una i corta que la acerca a <em>shit</em> (<span class="ipa">/ʃɪt/</span>)</td><td>I larga y la SH de mandar callar (“shhh”). Imprescindible si trabajas con hojas de cálculo: <em>spreadsheet</em>.</td></tr>
                        <tr><td><strong>focus</strong></td><td>UK <span class="ipa">/ˈfəʊkəs/</span><br>US <span class="ipa">/ˈfoʊkəs/</span></td><td><em>FÓ-kus</em>, con O y U españolas</td><td>La primera vocal es un diptongo (“ou”) y la segunda, una vocal neutra: FÓU-kes. Si la acortas, puede sonar a algo bastante menos profesional. <a href="/audio/focus.html">Escúchala</a>.</td></tr>
                    </tbody>
                </table>
                <p>Casi todo se reduce a distinguir la <span class="ipa">/iː/</span> larga de la <span class="ipa">/ɪ/</span> corta. Para entrenar la corta, empieza con <a href="/audio/bit-big-win-lip-clip.html">bit, big, win, lip y clip</a> y repasa la teoría en <a href="/articulos/vocales-ingles-cortas-largas.html">vocales cortas y largas en inglés</a>. Y si te preguntas de dónde sale el título del libro, <a href="/audio/fak-fuck.html">este audio</a> compara el “fak” a la española con la palabrota inglesa original. Avisado quedas.</p>
                <h2 id="ingles-falso">Inglés que solo existe en España: footing, puenting, parking…</h2>
                <p>Estas palabras no es que se pronuncien mal: es que en inglés no significan lo mismo, o directamente no existen. Son préstamos que el español ha adaptado a su manera. Si las usas en inglés, como poco te mirarán raro.</p>
                <table class="data-table">
                    <thead>
                        <tr><th>En España</th><th>En inglés se dice</th><th>Pronunciación (IPA)</th><th>Ojo</th></tr>
                    </thead>
                    <tbody>
                        <tr><td><strong>footing</strong></td><td><em>jogging</em> o <em>go for a run</em></td><td>UK <span class="ipa">/ˈdʒɒɡɪŋ/</span><br>US <span class="ipa">/ˈdʒɑːɡɪŋ/</span></td><td><em>Footing</em> existe, pero significa equilibrio o base: <em>I lost my footing</em> (perdí el equilibrio).</td></tr>
                        <tr><td><strong>puenting</strong></td><td><em>bungee jumping</em></td><td>UK y US <span class="ipa">/ˈbʌndʒi dʒʌmpɪŋ/</span></td><td><em>Puenting</em> no existe en inglés. Lo más parecido que entenderá un nativo es <em>bungee jumping</em>.</td></tr>
                        <tr><td><strong>un parking</strong></td><td>UK <em>car park</em><br>US <em>parking lot</em></td><td>UK <span class="ipa">/ˈkɑː pɑːk/</span><br>US <span class="ipa">/ˈpɑːrkɪŋ lɑːt/</span></td><td><em>Parking</em> es la acción de aparcar o el sitio disponible: <em>Is there parking?</em> (¿hay sitio para aparcar?) sí es correcto.</td></tr>
                        <tr><td><strong>un smoking</strong> (esmoquin)</td><td>UK <em>dinner jacket</em><br>US <em>tuxedo</em></td><td>UK <span class="ipa">/ˈdɪnə dʒækɪt/</span><br>US <span class="ipa">/tʌkˈsiːdoʊ/</span></td><td><em>Smoking</em> significa “fumar”. <em>No smoking</em> no es un código de vestimenta.</td></tr>
                        <tr><td><strong>un camping</strong></td><td>UK <em>campsite</em><br>US <em>campground</em></td><td>UK <span class="ipa">/ˈkæmpsaɪt/</span><br>US <span class="ipa">/ˈkæmpɡraʊnd/</span></td><td><em>Camping</em> es la actividad: <em>We went camping</em> (fuimos de acampada).</td></tr>
                    </tbody>
                </table>
                <h2 id="por-que">¿Por qué nos pasa a los españoles?</h2>
                <ul>
                    <li><strong>Leemos como se escribe.</strong> En español funciona; en inglés, la ortografía y el sonido van por caminos distintos.</li>
                    <li><strong>Tenemos cinco vocales.</strong> El inglés tiene muchos más sonidos vocálicos, y cuando no los distingues, <em>beach</em> y <em>bitch</em> se acercan peligrosamente.</li>
                    <li><strong>No hay tildes.</strong> Nada te avisa de dónde va la fuerza de <em>develop</em> o <em>colleague</em>; hay que aprenderla con cada palabra.</li>
                    <li><strong>Las hemos oído a la española.</strong> Marcas y anglicismos llegan ya adaptados, y esa versión se queda grabada.</li>
                </ul>
                <p>Si quieres atacar estos problemas de raíz, la guía de <a href="/articulos/pronunciacion-ingles-para-espanoles.html">pronunciación en inglés para españoles</a> explica qué sonidos conviene trabajar primero.</p>
                <h2 id="comprobar">Cómo comprobar la pronunciación de cualquier palabra</h2>
                <ol>
                    <li>Búscala en el <a href="https://dictionary.cambridge.org/es/" target="_blank" rel="noopener noreferrer">Diccionario Cambridge</a>: tiene IPA y audio en versión británica y americana.</li>
                    <li>Fíjate en el símbolo <span class="ipa">ˈ</span>: marca la sílaba fuerte.</li>
                    <li>Cuenta las sílabas que oyes, no las que lees.</li>
                    <li>Repite en voz alta tres veces y después dentro de una frase.</li>
                </ol>
                <p>A veces hay dos pronunciaciones válidas, y ninguna es la “buena”: escucha <a href="/audio/either-american-either-british.html">either en versión americana y británica</a>.</p>
                <h3>Mini test</h3>
                <details class="exercise">
                    <summary>¿Cuántas sílabas tiene <em>comfortable</em>?</summary>
                    <p>Tres en la pronunciación más habitual: <span class="ipa">/ˈkʌmftəbl/</span>. La sílaba “for” desaparece.</p>
                </details>
                <details class="exercise">
                    <summary>¿Dónde va la fuerza en <em>develop</em>?</summary>
                    <p>En la segunda sílaba: di-VÉ-lep, <span class="ipa">/dɪˈveləp/</span>.</p>
                </details>
                <details class="exercise">
                    <summary>¿Qué palabra suena igual que <em>suite</em>?</summary>
                    <p><em>Sweet</em>: las dos se pronuncian <span class="ipa">/swiːt/</span>.</p>
                </details>
                <details class="exercise">
                    <summary>¿Qué letras no suenan en <em>Wednesday</em>?</summary>
                    <p>La primera D y la segunda E: <span class="ipa">/ˈwenzdeɪ/</span>.</p>
                </details>
                <details class="exercise">
                    <summary>¿Cómo preguntarías por un parking en Londres?</summary>
                    <p><em>Is there a car park near here?</em> En Estados Unidos dirías <em>parking lot</em>.</p>
                </details>
                <p>No intentes corregir las 40 a la vez. Elige cinco, las que más uses en el trabajo o de viaje, y practícalas esta semana en voz alta. Cuando salgan solas, elige otras cinco. Para entrenar el oído, tienes todos los <a href="/audios.html">audios de pronunciación gratis</a> de la web.</p>
        """,
    },
    {
        "slug": "como-se-pronuncia-the",
        "category": "Pronunciación",
        "title": "Cómo se pronuncia THE en inglés: /ðə/, /ði/ y el sonido TH (con ejemplos)",
        "seo_title": "Cómo se pronuncia THE en inglés: /ðə/, /ði/ y el sonido TH",
        "description": "Cómo se pronuncia the en inglés: cuándo es /ðə/ y cuándo /ði/, cómo hacer la TH sonora y cómo se dicen this, that, they, there o three.",
        "lede": "La palabra que más vas a decir en inglés tiene tres pronunciaciones y un sonido que, aunque no lo parezca, ya usas en español.",
        "reading": "8 minutos",
        "published": "2026-10-11",
        "from_book": False,
        "toc": [
            ("como-se-pronuncia", "/ðə/ o /ði/"),
            ("sonido-no-letra", "Sonido, no letra"),
            ("forma-fuerte", "Forma fuerte"),
            ("sonido-th", "La TH sonora"),
            ("palabras-th", "Palabras con TH"),
            ("ejercicio", "Ejercicio"),
        ],
        "related": [
            "sonido-th-ingles",
            "alfabeto-fonetico-ingles",
            "palabras-ough-pronunciacion-ingles",
            "vocales-ingles-cortas-largas",
        ],
        "quick_answer": "<strong>The</strong> se pronuncia normalmente <strong><span class=\"ipa\">/ðə/</span></strong> delante de sonido consonante (<em>the car</em>, <em>the university</em>) y <strong><span class=\"ipa\">/ði/</span></strong> delante de sonido vocálico (<em>the apple</em>, <em>the hour</em>). Para enfatizar se dice <span class=\"ipa\">/ðiː/</span>. La TH es sonora: lengua entre los dientes y garganta vibrando, parecida a la D suave de “nada”.",
        "faq": [
            ("¿The se pronuncia “de” o “da”?", "Ni una ni otra. La pronunciación más habitual es <span class=\"ipa\">/ðə/</span>: TH sonora, con la lengua entre los dientes y la garganta vibrando, seguida de una vocal muy breve y relajada. Delante de sonido vocálico se dice <span class=\"ipa\">/ði/</span>."),
            ("¿Cómo se pronuncia thank you en inglés?", "<span class=\"ipa\">/ˈθæŋk juː/</span>. La TH es sorda y muy parecida a la Z castellana de “zapato”, así que el “zenkiu” español va bien encaminado; lo que más falla es la vocal, porque <span class=\"ipa\">/æ/</span> es más abierta que una e. Lo que hay que evitar es “tenkiu”, con T."),
            ("¿The se pronuncia igual en inglés británico y americano?", "Sí, en lo esencial: <span class=\"ipa\">/ðə/</span> delante de consonante, <span class=\"ipa\">/ði/</span> delante de vocal y <span class=\"ipa\">/ðiː/</span> para enfatizar, en los dos acentos. Lo que cambia entre acentos es la pronunciación de la palabra que va detrás, no la del artículo."),
            ("¿Qué diferencia hay entre this y these al pronunciar?", "<em>This</em> es <span class=\"ipa\">/ðɪs/</span>, con una i corta y relajada y una S final sin vibración. <em>These</em> es <span class=\"ipa\">/ðiːz/</span>, con una i larga y una Z final que vibra."),
            ("¿There, their y they're se pronuncian igual?", "Normalmente sí: <span class=\"ipa\">/ðeə/</span> en inglés británico y <span class=\"ipa\">/ðer/</span> en americano. Se distinguen por el contexto al hablar y por la ortografía al escribir."),
        ],
        "body": """
                <p><em>The</em> es la palabra más frecuente del inglés, así que la vas a decir constantemente. Si la pronuncias “de”, “da” o “ze”, nadie dejará de entenderte, pero es uno de esos detalles que hacen que tu inglés suene más español de lo necesario, precisamente en la palabra que más repites.</p>
                <p>La buena noticia: pronunciar bien <em>the</em> depende solo de dos cosas. Qué vocal lleva, que cambia según la palabra que va detrás, y cómo se hace la TH sonora. Y con esa TH, un español tiene ventaja aunque no lo sepa.</p>
                <h2 id="como-se-pronuncia">¿Cómo se pronuncia the en inglés?</h2>
                <p>Tiene tres pronunciaciones, y las tres empiezan por el mismo sonido, <span class="ipa">/ð/</span>. En esto el inglés británico y el americano coinciden:</p>
                <table class="data-table">
                    <thead>
                        <tr><th>Pronunciación</th><th>Cuándo</th><th>Ejemplos</th></tr>
                    </thead>
                    <tbody>
                        <tr><td><span class="ipa">/ðə/</span> (forma débil)</td><td>Delante de <strong>sonido consonante</strong>. Es la más frecuente.</td><td><em>the car, the book, the people, the university</em></td></tr>
                        <tr><td><span class="ipa">/ði/</span> (también <span class="ipa">/ðɪ/</span>)</td><td>Delante de <strong>sonido vocálico</strong>.</td><td><em>the apple, the end, the hour</em></td></tr>
                        <tr><td><span class="ipa">/ðiː/</span> (forma fuerte)</td><td>Para enfatizar, o cuando dudas a mitad de frase.</td><td><em>This is THE place to go.</em></td></tr>
                    </tbody>
                </table>
                <p>La <span class="ipa">/ə/</span> de la forma débil es la <em>schwa</em>, la vocal más relajada del inglés: una especie de “e” muy corta y floja, sin abrir apenas la boca. Por eso <span class="ipa">/ðə/</span> no es ni “de” ni “da”: la vocal casi no se oye y el <em>the</em> se pega a la palabra siguiente, como si <em>the car</em> fuera una sola palabra.</p>
                <div class="lesson-box"><strong>En el habla real:</strong> en conversación rápida también oirás a muchos nativos decir <span class="ipa">/ðə/</span> delante de vocal. No es un error, pero la opción que verás en los diccionarios, y la más segura para ti, es <span class="ipa">/ði/</span>.</div>
                <h2 id="sonido-no-letra">¿The apple o the university? Manda el sonido, no la letra</h2>
                <p>La regla mira el sonido con el que empieza la palabra siguiente, no cómo se escribe. Es la misma lógica que <em>a</em> y <em>an</em>: <em>an hour</em>, pero <em>a university</em>.</p>
                <table class="data-table">
                    <thead>
                        <tr><th>Frase</th><th>Empieza por</th><th>The se dice</th></tr>
                    </thead>
                    <tbody>
                        <tr><td><em>the apple</em></td><td><span class="ipa">/æ/</span>, vocal</td><td><span class="ipa">/ði/</span></td></tr>
                        <tr><td><em>the hour</em></td><td><span class="ipa">/aʊ/</span>, vocal (la H es muda)</td><td><span class="ipa">/ði/</span></td></tr>
                        <tr><td><em>the umbrella</em></td><td><span class="ipa">/ʌ/</span>, vocal</td><td><span class="ipa">/ði/</span></td></tr>
                        <tr><td><em>the FBI</em></td><td><span class="ipa">/e/</span>, vocal (se lee “ef”)</td><td><span class="ipa">/ði/</span></td></tr>
                        <tr><td><em>the house</em></td><td><span class="ipa">/h/</span>, consonante</td><td><span class="ipa">/ðə/</span></td></tr>
                        <tr><td><em>the university</em></td><td><span class="ipa">/j/</span>, consonante</td><td><span class="ipa">/ðə/</span></td></tr>
                        <tr><td><em>the European Union</em></td><td><span class="ipa">/j/</span>, consonante</td><td><span class="ipa">/ðə/</span></td></tr>
                        <tr><td><em>the one</em></td><td><span class="ipa">/w/</span>, consonante</td><td><span class="ipa">/ðə/</span></td></tr>
                        <tr><td><em>the USA</em></td><td><span class="ipa">/j/</span>, consonante (se lee “yu”)</td><td><span class="ipa">/ðə/</span></td></tr>
                    </tbody>
                </table>
                <p>Los dos casos que más dudas generan, completos: <em>the university</em> se pronuncia <span class="ipa">/ðə ˌjuːnɪˈvɜːsəti/</span> (UK) o <span class="ipa">/ðə ˌjuːnɪˈvɝːsəti/</span> (US), y <em>the European</em>, <span class="ipa">/ðə ˌjʊərəˈpiːən/</span> (UK) o <span class="ipa">/ðə ˌjʊrəˈpiːən/</span> (US). Ese <span class="ipa">/j/</span> inicial es el mismo sonido que la i de “bien”: funciona como consonante aunque se escriba con vocal. Lo oyes en <a href="/audio/yellow-young-you-yes.html">yellow, young, you y yes</a>.</p>
                <h2 id="forma-fuerte">¿Cuándo se pronuncia /ðiː/?</h2>
                <ul>
                    <li><strong>Para enfatizar</strong> que algo es el auténtico o el mejor: <em>This is THE place to eat paella in London</em> (este es EL sitio para comer paella en Londres).</li>
                    <li><strong>Para mostrar sorpresa</strong> ante alguien famoso: <em>Wait, you met THE Paul McCartney?</em> (¿el mismísimo Paul McCartney?).</li>
                    <li><strong>Cuando dudas</strong> a mitad de frase: <em>I left it in the… the… the kitchen.</em> Es habitual alargar el <em>the</em> mientras piensas.</li>
                    <li><strong>Cuando hablas de la propia palabra</strong>: <em>“The” is the most common word in English.</em></li>
                </ul>
                <p>Fuera de estos casos, decir siempre <span class="ipa">/ðiː/</span> suena a lectura en voz alta en clase.</p>
                <h2 id="sonido-th">¿Cómo se hace la TH de the? Ya la usas en español</h2>
                <p>La TH de <em>the</em> es <strong>sonora</strong> (<span class="ipa">/ð/</span>): la garganta vibra. Y aquí viene la ventaja: en castellano ya producimos un sonido muy parecido. Di despacio <em>nada</em>, <em>cada</em> o <em>dedo</em> y fíjate en la D que va entre vocales: es suave, casi sin contacto. Ese sonido está muy cerca de la <span class="ipa">/ð/</span> inglesa; solo le falta que la lengua vaya un poco más adelante, entre los dientes.</p>
                <p>Lo que nos pasa es que, al principio de palabra o después de una pausa, el español usa una D dura, con la lengua apoyada detrás de los dientes de arriba (la de <em>dame</em> o <em>dónde</em>). Y <em>the</em> casi siempre va al principio de algo.</p>
                <ol>
                    <li>Di <em>nada</em> despacio y quédate en la segunda D.</li>
                    <li>Adelanta la punta de la lengua hasta que asome un poco entre los dientes o toque el borde de los de arriba.</li>
                    <li>Pon la mano en el cuello: tiene que vibrar.</li>
                    <li>Ahora di solo el principio, <span class="ipa">/ðə/</span>, y luego dentro de frases: <em>the car, the end, the one</em>.</li>
                </ol>
                <div class="lesson-box"><strong>Escúchalo:</strong> compara la TH sonora y la sorda en <a href="/audio/sonido-th-entre-dientes.html">TH entre dientes</a> y la diferencia entre la D y la TH en <a href="/audio/sonido-th-paladar.html">day frente a they</a>.</div>
                <p>La otra TH, la <strong>sorda</strong> (<span class="ipa">/θ/</span>) de <em>think</em> o <em>three</em>, es aún más fácil para la mayoría de los españoles: está muy cerca de la Z castellana de <em>zapato</em>. Si en tu zona no se distingue la Z de la S, como en Canarias o en partes de Andalucía, tendrás que practicarla un poco más. Escúchala dos veces en <a href="/audio/i-am-from-spain-and-i-am-33.html">I am from Spain and I am 33</a> (<em>thirty-three</em>).</p>
                <h2 id="errores">Errores típicos: “de”, “da” y “ze”</h2>
                <ul>
                    <li><strong>“De”:</strong> la D dura española. Con la lengua escondida detrás de los dientes, <em>the</em> se acerca a la D de <em>day</em>.</li>
                    <li><strong>“Da”:</strong> D dura más una A abierta. La vocal de <span class="ipa">/ðə/</span> es mucho más débil.</li>
                    <li><strong>“Ze”:</strong> usar la Z castellana. La lengua está bien colocada, pero ese es el sonido de <em>think</em>: falta la vibración. Añade voz.</li>
                    <li><strong>“Di” delante de todo:</strong> usar <span class="ipa">/ði/</span> también delante de consonante. No es grave, pero suena forzado.</li>
                    <li><strong>Separarlo:</strong> <em>the</em> se une a lo que va detrás. Si haces una pausa después, suena a palabra suelta. Tienes más sobre esto en <a href="/articulos/ligar-palabras-ingles.html">cómo se ligan las palabras en inglés</a>.</li>
                </ul>
                <h2 id="palabras-th">¿Cómo se pronuncian this, that, these, those, they o there?</h2>
                <p>Un truco que funciona casi siempre: las palabras gramaticales que empiezan por TH (artículos, pronombres, demostrativos, conectores) llevan la TH sonora, como <em>the</em>. Los sustantivos, verbos y números que empiezan por TH suelen llevar la sorda, como <em>think</em>. En medio o al final de palabra no hay atajo: hay que aprenderlas una a una.</p>
                <table class="data-table">
                    <thead>
                        <tr><th>Palabra</th><th>UK</th><th>US</th><th>TH</th></tr>
                    </thead>
                    <tbody>
                        <tr><td><strong>the</strong></td><td><span class="ipa">/ðə/</span>, <span class="ipa">/ði/</span></td><td><span class="ipa">/ðə/</span>, <span class="ipa">/ði/</span></td><td>sonora <span class="ipa">/ð/</span></td></tr>
                        <tr><td><strong>this</strong></td><td><span class="ipa">/ðɪs/</span></td><td><span class="ipa">/ðɪs/</span></td><td>sonora <span class="ipa">/ð/</span></td></tr>
                        <tr><td><strong>that</strong></td><td><span class="ipa">/ðæt/</span></td><td><span class="ipa">/ðæt/</span></td><td>sonora <span class="ipa">/ð/</span></td></tr>
                        <tr><td><strong>these</strong></td><td><span class="ipa">/ðiːz/</span></td><td><span class="ipa">/ðiːz/</span></td><td>sonora <span class="ipa">/ð/</span></td></tr>
                        <tr><td><strong>those</strong></td><td><span class="ipa">/ðəʊz/</span></td><td><span class="ipa">/ðoʊz/</span></td><td>sonora <span class="ipa">/ð/</span></td></tr>
                        <tr><td><strong>they</strong></td><td><span class="ipa">/ðeɪ/</span></td><td><span class="ipa">/ðeɪ/</span></td><td>sonora <span class="ipa">/ð/</span></td></tr>
                        <tr><td><strong>them</strong></td><td><span class="ipa">/ðem/</span></td><td><span class="ipa">/ðem/</span></td><td>sonora <span class="ipa">/ð/</span></td></tr>
                        <tr><td><strong>there</strong></td><td><span class="ipa">/ðeə/</span></td><td><span class="ipa">/ðer/</span></td><td>sonora <span class="ipa">/ð/</span></td></tr>
                        <tr><td><strong>their</strong></td><td><span class="ipa">/ðeə/</span></td><td><span class="ipa">/ðer/</span></td><td>sonora <span class="ipa">/ð/</span></td></tr>
                        <tr><td><strong>then</strong></td><td><span class="ipa">/ðen/</span></td><td><span class="ipa">/ðen/</span></td><td>sonora <span class="ipa">/ð/</span></td></tr>
                        <tr><td><strong>than</strong></td><td><span class="ipa">/ðæn/</span></td><td><span class="ipa">/ðæn/</span></td><td>sonora <span class="ipa">/ð/</span></td></tr>
                        <tr><td><strong>though</strong></td><td><span class="ipa">/ðəʊ/</span></td><td><span class="ipa">/ðoʊ/</span></td><td>sonora <span class="ipa">/ð/</span></td></tr>
                        <tr><td><strong>with</strong></td><td><span class="ipa">/wɪð/</span>, <span class="ipa">/wɪθ/</span></td><td><span class="ipa">/wɪð/</span>, <span class="ipa">/wɪθ/</span></td><td>las dos son correctas</td></tr>
                        <tr><td><strong>think</strong></td><td><span class="ipa">/θɪŋk/</span></td><td><span class="ipa">/θɪŋk/</span></td><td>sorda <span class="ipa">/θ/</span></td></tr>
                        <tr><td><strong>thank you</strong></td><td><span class="ipa">/ˈθæŋk juː/</span></td><td><span class="ipa">/ˈθæŋk juː/</span></td><td>sorda <span class="ipa">/θ/</span></td></tr>
                        <tr><td><strong>three</strong></td><td><span class="ipa">/θriː/</span></td><td><span class="ipa">/θriː/</span></td><td>sorda <span class="ipa">/θ/</span></td></tr>
                        <tr><td><strong>thing</strong></td><td><span class="ipa">/θɪŋ/</span></td><td><span class="ipa">/θɪŋ/</span></td><td>sorda <span class="ipa">/θ/</span></td></tr>
                        <tr><td><strong>thirty</strong></td><td><span class="ipa">/ˈθɜːti/</span></td><td><span class="ipa">/ˈθɝːti/</span></td><td>sorda <span class="ipa">/θ/</span></td></tr>
                        <tr><td><strong>Thursday</strong></td><td><span class="ipa">/ˈθɜːzdeɪ/</span></td><td><span class="ipa">/ˈθɝːzdeɪ/</span></td><td>sorda <span class="ipa">/θ/</span></td></tr>
                        <tr><td><strong>month</strong></td><td><span class="ipa">/mʌnθ/</span></td><td><span class="ipa">/mʌnθ/</span></td><td>sorda <span class="ipa">/θ/</span></td></tr>
                        <tr><td><strong>both</strong></td><td><span class="ipa">/bəʊθ/</span></td><td><span class="ipa">/boʊθ/</span></td><td>sorda <span class="ipa">/θ/</span></td></tr>
                        <tr><td><strong>maths</strong> (UK) / <strong>math</strong> (US)</td><td><span class="ipa">/mæθs/</span></td><td><span class="ipa">/mæθ/</span></td><td>sorda <span class="ipa">/θ/</span></td></tr>
                    </tbody>
                </table>
                <p>Tres detalles más. <em>This</em> lleva una i corta y <em>these</em> una i larga (tienes la diferencia explicada en <a href="/articulos/vocales-ingles-cortas-largas.html">vocales cortas y largas</a>). <em>That</em>, <em>than</em> y <em>them</em> se debilitan dentro de la frase: en <em>better than me</em>, <em>than</em> suele sonar <span class="ipa">/ðən/</span>. Y <em>though</em> (sonora) no se parece a <em>thought</em> (<span class="ipa">/θɔːt/</span> en UK, <span class="ipa">/θɑːt/</span> en US; sorda): las palabras con OUGH tienen <a href="/articulos/palabras-ough-pronunciacion-ingles.html">su propia guía</a>. Si algún símbolo te frena, consulta el <a href="/articulos/alfabeto-fonetico-ingles.html">alfabeto fonético inglés</a>.</p>
                <h2 id="ejercicio">Ejercicio: ¿/ðə/ o /ði/?</h2>
                <p>Decide cómo se pronuncia <em>the</em> en cada caso y abre para comprobarlo:</p>
                <details class="exercise">
                    <summary>the orange</summary>
                    <p><span class="ipa">/ði/</span>: <em>orange</em> empieza por sonido vocálico (<span class="ipa">/ˈɒrɪndʒ/</span> UK, <span class="ipa">/ˈɔːrɪndʒ/</span> US).</p>
                </details>
                <details class="exercise">
                    <summary>the uniform</summary>
                    <p><span class="ipa">/ðə/</span>: <em>uniform</em> empieza por <span class="ipa">/j/</span> (“yu”), un sonido consonante.</p>
                </details>
                <details class="exercise">
                    <summary>the hour</summary>
                    <p><span class="ipa">/ði/</span>: la H es muda y la palabra empieza por <span class="ipa">/aʊ/</span>.</p>
                </details>
                <details class="exercise">
                    <summary>the one</summary>
                    <p><span class="ipa">/ðə/</span>: <em>one</em> empieza por <span class="ipa">/w/</span>, aunque se escriba con O.</p>
                </details>
                <details class="exercise">
                    <summary>the umbrella</summary>
                    <p><span class="ipa">/ði/</span>: empieza por la vocal <span class="ipa">/ʌ/</span>. Escucha <em>umbrella</em> en <a href="/audio/microsoft-up-us-uncle-umbrella.html">este audio</a>.</p>
                </details>
                <details class="exercise">
                    <summary>the year</summary>
                    <p><span class="ipa">/ðə/</span>: <em>year</em> empieza por <span class="ipa">/j/</span>.</p>
                </details>
                <details class="exercise">
                    <summary>the MBA</summary>
                    <p><span class="ipa">/ði/</span>: se lee “em”, que empieza por vocal.</p>
                </details>
                <details class="exercise">
                    <summary>¿Sonora o sorda? <em>there, thirty, than, thing</em></summary>
                    <p><em>There</em> y <em>than</em>, sonoras (son palabras gramaticales); <em>thirty</em> y <em>thing</em>, sordas.</p>
                </details>
                <p>Para cerrar, una frase que mezcla las dos TH: <em>They think the three of them are there.</em> Dila despacio tres veces, grábate y compara. Si quieres seguir entrenando el sonido, la guía del <a href="/articulos/sonido-th-ingles.html">sonido TH en inglés</a> tiene más pares y ejercicios.</p>
        """,
    },
    {
        "slug": "palabras-ough-pronunciacion-ingles",
        "category": "Pronunciación",
        "title": "Cómo se pronuncia OUGH en inglés: though, through, tough, thought y más",
        "seo_title": "Cómo se pronuncia though, through, tough y thought",
        "description": "Cómo se pronuncia though, through, tough, enough, cough y thought: tabla de palabras con OUGH con IPA americana y británica, grupos de sonido y ejercicio.",
        "lede": "La ortografía inglesa no siempre avisa. OUGH puede sonar de siete maneras distintas en palabras comunes, así que estas palabras se aprenden mejor por familias y con audio.",
        "reading": "7 minutos",
        "published": "2026-06-28",
        "toc": [
            ("lista", "Tabla OUGH"),
            ("grupos", "Los 7 sonidos"),
            ("errores", "Though, through, thought"),
            ("metodo", "Método"),
            ("ejercicio", "Ejercicio"),
            ("contexto", "Por qué pasa"),
        ],
        "related": [
            "sonido-th-ingles",
            "letras-mudas-ingles",
            "palabras-ingles-mal-pronunciadas",
            "vocales-ingles-cortas-largas",
        ],
        "quick_answer": "<strong>Though</strong> se pronuncia /ðoʊ/ (US) o /ðəʊ/ (UK) y rima con <em>go</em>; <strong>through</strong> es /θruː/ y rima con <em>too</em>; <strong>tough</strong> es /tʌf/, como <em>stuff</em>; <strong>cough</strong> es /kɒf/ (UK) o /kɑːf/ (US); y <strong>thought</strong> es /θɔːt/ (UK) o /θɑːt/ (US). OUGH no tiene una regla única: se aprende por grupos de sonido.",
        "faq": [
            ("¿Cómo se pronuncia though en inglés?", "<em>Though</em> se pronuncia <span class=\"ipa\">/ðoʊ/</span> en inglés americano y <span class=\"ipa\">/ðəʊ/</span> en británico: TH sonora, con la lengua entre los dientes, y una vocal como la de <em>go</em>. La GH no suena. Significa “aunque” o, al final de la frase, “sin embargo”."),
            ("¿Qué diferencia hay entre though, through y thought?", "<em>Though</em> (<span class=\"ipa\">/ðoʊ/</span> US, <span class=\"ipa\">/ðəʊ/</span> UK) significa “aunque” y rima con <em>go</em>; <em>through</em> (<span class=\"ipa\">/θruː/</span>) significa “a través de” y rima con <em>too</em>; <em>thought</em> (<span class=\"ipa\">/θɑːt/</span> US, <span class=\"ipa\">/θɔːt/</span> UK) es “pensamiento” o el pasado de <em>think</em>. Las dos últimas llevan TH sorda."),
            ("¿Cómo se pronuncia enough?", "<em>Enough</em> se pronuncia <span class=\"ipa\">/ɪˈnʌf/</span> en británico y <span class=\"ipa\">/əˈnʌf/</span> en americano, con el acento en la segunda sílaba. La GH suena como una F, igual que en <em>tough</em> y <em>rough</em>."),
            ("¿Hay alguna regla para pronunciar OUGH?", "No hay una regla única, pero sí tendencias: <em>-ought</em> suele sonar como en <em>thought</em> (<em>bought</em>, <em>brought</em>, <em>fought</em>), con la excepción de <em>drought</em>, que rima con <em>now</em>. Lo más fiable es aprender las palabras frecuentes por grupos de sonido y con audio."),
            ("¿Through y threw se pronuncian igual?", "Sí. <em>Through</em> (a través de) y <em>threw</em> (pasado de <em>throw</em>, lanzar) son homófonos: las dos se pronuncian <span class=\"ipa\">/θruː/</span>, tanto en británico como en americano."),
        ],
        "body": """
                <p>Si buscas una prueba rápida de que el inglés no se pronuncia como se escribe, mira la combinación <strong>ough</strong>. Aparece en palabras muy comunes, como <em>though</em>, <em>through</em>, <em>tough</em> o <em>thought</em>, pero no mantiene un sonido único: solo en palabras de uso diario puede sonar de siete maneras distintas.</p>
                <p>La solución no es frustrarse ni buscar una regla perfecta. La solución práctica es agrupar, escuchar y memorizar las palabras de más uso. Aquí tienes la tabla completa, los grupos de sonido y un ejercicio para comprobar si ya no caes en la trampa.</p>
                <h2 id="lista">Tabla: cómo se pronuncian las palabras con OUGH</h2>
                <p>La primera columna fonética es la pronunciación americana (US) y la segunda, la británica (UK).</p>
                <table class="data-table">
                <thead><tr><th>Palabra</th><th>IPA US</th><th>IPA UK</th><th>Significado</th><th>Grupo de sonido</th></tr></thead>
                <tbody>
                <tr><td><strong>though</strong></td><td><span class="ipa">/ðoʊ/</span></td><td><span class="ipa">/ðəʊ/</span></td><td>aunque; sin embargo</td><td>1 · como <em>go</em></td></tr>
                <tr><td><strong>dough</strong></td><td><span class="ipa">/doʊ/</span></td><td><span class="ipa">/dəʊ/</span></td><td>masa (de pan, de pizza)</td><td>1 · como <em>go</em></td></tr>
                <tr><td><strong>through</strong></td><td><span class="ipa">/θruː/</span></td><td><span class="ipa">/θruː/</span></td><td>a través de, por</td><td>2 · como <em>too</em></td></tr>
                <tr><td><strong>tough</strong></td><td><span class="ipa">/tʌf/</span></td><td><span class="ipa">/tʌf/</span></td><td>duro, difícil</td><td>3 · como <em>stuff</em></td></tr>
                <tr><td><strong>rough</strong></td><td><span class="ipa">/rʌf/</span></td><td><span class="ipa">/rʌf/</span></td><td>áspero; brusco; aproximado</td><td>3 · como <em>stuff</em></td></tr>
                <tr><td><strong>enough</strong></td><td><span class="ipa">/əˈnʌf/</span></td><td><span class="ipa">/ɪˈnʌf/</span></td><td>suficiente, bastante</td><td>3 · como <em>stuff</em></td></tr>
                <tr><td><strong>cough</strong></td><td><span class="ipa">/kɑːf/</span></td><td><span class="ipa">/kɒf/</span></td><td>tos; toser</td><td>4 · como <em>off</em></td></tr>
                <tr><td><strong>bough</strong></td><td><span class="ipa">/baʊ/</span></td><td><span class="ipa">/baʊ/</span></td><td>rama gruesa de un árbol</td><td>5 · como <em>now</em></td></tr>
                <tr><td><strong>plough</strong></td><td><span class="ipa">/plaʊ/</span></td><td><span class="ipa">/plaʊ/</span></td><td>arado; arar (en EE. UU. se escribe <em>plow</em>)</td><td>5 · como <em>now</em></td></tr>
                <tr><td><strong>thought</strong></td><td><span class="ipa">/θɑːt/</span></td><td><span class="ipa">/θɔːt/</span></td><td>pensamiento; pasado de <em>think</em></td><td>6 · como <em>caught</em></td></tr>
                <tr><td><strong>bought</strong></td><td><span class="ipa">/bɑːt/</span></td><td><span class="ipa">/bɔːt/</span></td><td>pasado de <em>buy</em> (comprar)</td><td>6 · como <em>caught</em></td></tr>
                <tr><td><strong>brought</strong></td><td><span class="ipa">/brɑːt/</span></td><td><span class="ipa">/brɔːt/</span></td><td>pasado de <em>bring</em> (traer)</td><td>6 · como <em>caught</em></td></tr>
                <tr><td><strong>taught</strong></td><td><span class="ipa">/tɑːt/</span></td><td><span class="ipa">/tɔːt/</span></td><td>pasado de <em>teach</em> (enseñar); se escribe con AUGH</td><td>6 · como <em>caught</em></td></tr>
                <tr><td><strong>thorough</strong></td><td><span class="ipa">/ˈθɝːoʊ/</span></td><td><span class="ipa">/ˈθʌrə/</span></td><td>minucioso, exhaustivo</td><td>7 · final débil</td></tr>
                <tr><td><strong>borough</strong></td><td><span class="ipa">/ˈbɝːoʊ/</span></td><td><span class="ipa">/ˈbʌrə/</span></td><td>distrito, municipio</td><td>7 · final débil</td></tr>
                </tbody>
                </table>
                <p><em>Taught</em> no se escribe con OUGH sino con AUGH, pero está aquí a propósito: rima con <em>thought</em> y <em>bought</em>, y se confunde muchísimo con ellos.</p>
                <h2 id="grupos">Los 7 sonidos de OUGH, agrupados</h2>
                <p>Memorizar quince palabras sueltas cuesta. Memorizar siete grupos, cada uno con una palabra fácil de referencia, cuesta mucho menos.</p>
                <ol>
                <li><strong>Como <em>go</em>: <span class="ipa">/oʊ/</span> (US), <span class="ipa">/əʊ/</span> (UK).</strong> <em>Though</em>, <em>dough</em> y también <em>although</em>. La GH no suena. En Estados Unidos, <em>doughnut</em> se escribe a menudo <em>donut</em>, que es justo como suena.</li>
                <li><strong>Como <em>too</em>: <span class="ipa">/uː/</span>.</strong> <em>Through</em> y <em>throughout</em>. En notas informales verás <em>thru</em>. Ojo: <em>through</em> suena igual que <em>threw</em>, el pasado de <em>throw</em> (lanzar).</li>
                <li><strong>Como <em>stuff</em>: <span class="ipa">/ʌf/</span>.</strong> <em>Tough</em>, <em>rough</em>, <em>enough</em>. Aquí la GH suena como una F, y la vocal es la de <em>love</em> o <em>cup</em>, no una o española.</li>
                <li><strong>Como <em>off</em>: <span class="ipa">/ɒf/</span> (UK), <span class="ipa">/ɑːf/</span> (US).</strong> <em>Cough</em> y la menos frecuente <em>trough</em> (abrevadero). También acaba en F, pero con otra vocal.</li>
                <li><strong>Como <em>now</em>: <span class="ipa">/aʊ/</span>.</strong> <em>Bough</em>, <em>plough</em> y <em>drought</em> (sequía), que se pronuncia <span class="ipa">/draʊt/</span> aunque parezca de la familia de <em>thought</em>.</li>
                <li><strong>Como <em>caught</em>: <span class="ipa">/ɔː/</span> (UK), <span class="ipa">/ɑː/</span> (US).</strong> <em>Thought</em>, <em>bought</em>, <em>brought</em>, <em>fought</em>, <em>ought</em>. Es el grupo más útil, porque incluye pasados muy frecuentes. En gran parte de Estados Unidos esta vocal se acerca a una a larga y abierta; por eso las transcripciones americanas usan <span class="ipa">/ɑː/</span>.</li>
                <li><strong>Final débil: <span class="ipa">/ə/</span> (UK), <span class="ipa">/oʊ/</span> (US).</strong> <em>Thorough</em> y <em>borough</em> tienen dos sílabas. En británico, OUGH se reduce a una schwa; en americano, suena como el final de <em>go</em>. Nueva York, por ejemplo, está dividida en cinco <em>boroughs</em>.</li>
                </ol>
                <div class="lesson-box"><strong>Dos curiosidades:</strong> en Irlanda, <em>lough</em> (lago) se pronuncia con un sonido muy parecido a nuestra jota, que es más o menos como sonaba la GH hace siglos. Y <em>hiccough</em> es una grafía antigua de <em>hiccup</em> (hipo), y se pronuncia igual: <span class="ipa">/ˈhɪkʌp/</span>.</div>
                <h2 id="errores">El error típico: confundir though, through, thought y tough</h2>
                <p>La tentación para un hispanohablante es leer todas estas palabras con un patrón estable. El problema es que <em>though</em>, <em>through</em>, <em>tough</em> y <em>thought</em> no funcionan como una familia fonética limpia: cambia la vocal, cambia el final y hasta cambia la TH.</p>
                <table class="data-table">
                <thead><tr><th>Palabra</th><th>Empieza con</th><th>Termina en</th><th>Pista</th></tr></thead>
                <tbody>
                <tr><td><em>though</em></td><td>TH sonora <span class="ipa">/ð/</span></td><td><span class="ipa">/oʊ/</span> (US), <span class="ipa">/əʊ/</span> (UK)</td><td>rima con <em>go</em></td></tr>
                <tr><td><em>through</em></td><td>TH sorda + R <span class="ipa">/θr/</span></td><td><span class="ipa">/uː/</span></td><td>rima con <em>too</em></td></tr>
                <tr><td><em>thought</em></td><td>TH sorda <span class="ipa">/θ/</span></td><td><span class="ipa">/ɑːt/</span> (US), <span class="ipa">/ɔːt/</span> (UK)</td><td>rima con <em>caught</em></td></tr>
                <tr><td><em>taught</em></td><td>T normal <span class="ipa">/t/</span></td><td><span class="ipa">/ɑːt/</span> (US), <span class="ipa">/ɔːt/</span> (UK)</td><td>como <em>thought</em>, pero con T</td></tr>
                <tr><td><em>tough</em></td><td>T normal <span class="ipa">/t/</span></td><td><span class="ipa">/ʌf/</span></td><td>rima con <em>stuff</em></td></tr>
                </tbody>
                </table>
                <p>Fíjate en el par <em>thought</em> / <em>taught</em>: solo cambia el primer sonido. Si no haces bien la TH, “pensé” y “enseñé” suenan igual. Por eso conviene practicar cada palabra dentro de una frase corta: no quieres recordar solo una transcripción aproximada; quieres que la boca la encuentre cuando estés hablando. Si la TH te cuesta, repasa la guía del <a href="/articulos/sonido-th-ingles.html">sonido TH en inglés</a>.</p>
                <h2 id="metodo">Método de práctica</h2>
                <ol>
                <li>Escucha la lista completa sin leer, para que el sonido llegue antes que la ortografía.</li>
                <li>Repite palabra por palabra, exagerando el sonido difícil.</li>
                <li>Añade una frase mínima: <em>That was tough</em>, <em>I've had enough</em>, <em>Go through the door</em>, <em>I thought so</em>, <em>She brought cake</em>.</li>
                <li>Vuelve al audio y comprueba si ya distingues los cambios.</li>
                </ol>
                <div class="lesson-box"><strong>Practica ahora:</strong> escucha <a href="/audio/though-through-tough-cough-enough-bough-thought-plough.html">though, through, tough, cough, enough, bough, thought y plough</a>, y después el contraste corto de <a href="/audio/though-tough-thought-taught.html">though, tough, thought y taught</a>.</div>
                <h2 id="ejercicio">Ejercicio: ¿con qué rima?</h2>
                <p>Responde en voz alta antes de abrir cada solución.</p>
                <details class="exercise"><summary>1. ¿<em>Though</em> rima con <em>go</em>, con <em>too</em> o con <em>off</em>?</summary><p>Con <em>go</em>: <span class="ipa">/ðoʊ/</span> (US), <span class="ipa">/ðəʊ/</span> (UK). La GH no suena.</p></details>
                <details class="exercise"><summary>2. ¿Cuál no rima con las demás: <em>tough</em>, <em>rough</em>, <em>enough</em>, <em>cough</em>?</summary><p><em>Cough</em>. Las otras tres terminan en <span class="ipa">/ʌf/</span>; <em>cough</em> es <span class="ipa">/kɒf/</span> (UK) o <span class="ipa">/kɑːf/</span> (US).</p></details>
                <details class="exercise"><summary>3. ¿Qué otra palabra inglesa suena exactamente igual que <em>through</em>?</summary><p><em>Threw</em>, el pasado de <em>throw</em>. Las dos se pronuncian <span class="ipa">/θruː/</span>.</p></details>
                <details class="exercise"><summary>4. ¿<em>Bough</em> rima con <em>cow</em> o con <em>cough</em>?</summary><p>Con <em>cow</em>: <span class="ipa">/baʊ/</span>. Igual que <em>plough</em>.</p></details>
                <details class="exercise"><summary>5. <em>I ___ you were coming</em> (pensé) / <em>She ___ me to swim</em> (me enseñó).</summary><p><em>Thought</em> y <em>taught</em>. Se distinguen solo por el primer sonido: TH sorda <span class="ipa">/θ/</span> frente a T.</p></details>
                <details class="exercise"><summary>6. <em>Brought</em>: ¿es el pasado de <em>bring</em> o de <em>buy</em>?</summary><p>De <em>bring</em> (traer). El pasado de <em>buy</em> es <em>bought</em>. Riman entre sí, así que la única pista es la R.</p></details>
                <details class="exercise"><summary>7. ¿Cuántas sílabas tiene <em>thorough</em>? ¿Y <em>through</em>?</summary><p><em>Thorough</em> tiene dos: <span class="ipa">/ˈθʌrə/</span> (UK), <span class="ipa">/ˈθɝːoʊ/</span> (US). <em>Through</em> tiene una: <span class="ipa">/θruː/</span>.</p></details>
                <h2 id="contexto">¿Por qué OUGH tiene tantas pronunciaciones?</h2>
                <p>El inglés ha absorbido palabras y sonidos de muchos orígenes, y su ortografía conserva capas antiguas. En el caso de OUGH, la GH representaba hace siglos un sonido parecido a nuestra jota. Con el tiempo, ese sonido desapareció en unas palabras (<em>though</em>, <em>thought</em>) y se convirtió en F en otras (<em>tough</em>, <em>enough</em>), mientras las vocales también evolucionaban de forma desigual. La escritura, en cambio, se quedó fija. Para aprenderlo, la memoria auditiva suele ser más fiable que la intuición visual.</p>
                <p>La buena noticia es que no necesitas dominar todas las excepciones a la vez. Empieza por las que aparecen en conversaciones, vídeos, trabajo y viajes: <em>though</em>, <em>through</em>, <em>enough</em>, <em>thought</em>, <em>bought</em> y <em>brought</em>. Si te gustan este tipo de trampas, sigue con las <a href="/articulos/letras-mudas-ingles.html">letras mudas</a> y las <a href="/articulos/palabras-ingles-mal-pronunciadas.html">palabras que los españoles pronuncian mal</a>.</p>
        """,
    },
    {
        "slug": "how-are-you-respuestas-ingles",
        "category": "Conversación",
        "title": "Cómo responder a How are you en inglés (sin sonar como un workbook)",
        "seo_title": "Qué responder a How are you: respuestas formales e informales",
        "description": "Qué responder a How are you en inglés: más de 15 respuestas formales e informales, diferencias por país y qué contestar a How’s it going o What’s up.",
        "lede": "La respuesta correcta depende de contexto, país y relación. No necesitas una frase perfecta; necesitas varias respuestas naturales y saber devolver la pregunta.",
        "reading": "7 minutos",
        "published": "2026-06-28",
        "toc": [
            ("saludo", "¿Pregunta o saludo?"),
            ("respuestas", "Respuestas por registro"),
            ("pais", "Por país"),
            ("preguntas", "Otras preguntas"),
            ("plantillas", "Plantillas"),
            ("errores", "Errores típicos"),
        ],
        "related": [
            "como-decir-de-nada-en-ingles",
            "ligar-palabras-ingles",
            "sure-en-ingles",
            "i-mean-en-ingles",
        ],
        "quick_answer": "Las <strong>respuestas a How are you</strong> más naturales son <em>Good, thanks. You?</em>, <em>I’m doing well</em>, <em>Pretty good</em> o <em>Not bad</em>; en contextos formales, <em>I’m very well, thank you</em>. Casi siempre funciona como saludo: responde breve, en positivo o neutro, y devuelve la pregunta con <em>And you?</em> o <em>How about you?</em>",
        "faq": [
            ("¿Se puede responder I’m fine, thank you, and you?", "Sí, es correcto, pero suena a libro de texto si lo usas siempre, y <em>fine</em> dicho con tono plano puede parecer que no estás muy bien. Una versión más natural es <em>Fine, thanks. You?</em> o <em>Good, thanks. How about you?</em>"),
            ("¿Es correcto decir I’m good o hay que decir I’m well?", "Las dos son correctas. <em>I’m good</em> es muy común en conversación, sobre todo en Estados Unidos, e <em>I’m well</em> suena algo más cuidado. Algunos puristas critican <em>I’m good</em>, pero es la respuesta normal en el inglés hablado."),
            ("¿Qué se responde a What’s up?", "Lo natural es <em>Not much</em>, <em>Nothing much, you?</em> o contar brevemente qué estás haciendo. <em>What’s up?</em> significa “¿qué hay?”, no “¿cómo estás?”, aunque dicho a alguien con mala cara significa “¿qué te pasa?”."),
            ("¿Qué responder a How are you si no estás bien?", "Puedes ser honesto sin dramatizar: <em>Hanging in there</em> (aquí, tirando), <em>Could be better</em> (podría ir mejor) o <em>Not great, to be honest</em>. Con desconocidos basta una respuesta breve; con gente de confianza puedes explicar más."),
            ("¿Qué significa How are you going?", "Es un saludo típico de Australia que significa lo mismo que <em>How are you?</em>. Se responde igual: <em>Good, thanks. You?</em> o <em>Not bad</em>."),
        ],
        "body": """
                <p>Muchos españoles aprendimos una única respuesta para <em>How are you?</em>: <em>I’m fine, thank you, and you?</em> La frase existe y es correcta, pero en conversaciones reales puede sonar demasiado formal, automática o poco natural, como si la estuvieras leyendo de un workbook.</p>
                <p>La respuesta adecuada depende del contexto, del país y de la relación. No necesitas una frase perfecta; necesitas cuatro o cinco respuestas naturales que te salgan sin pensar. Aquí tienes las <strong>respuestas a How are you en inglés</strong> ordenadas por registro, y también qué contestar a <em>How’s it going?</em>, <em>What’s up?</em> o <em>How have you been?</em>.</p>
                <h2 id="saludo">¿How are you es una pregunta o un saludo?</h2>
                <p>En inglés, igual que en español, preguntar qué tal estás no siempre busca una respuesta profunda. A veces es un saludo, a veces abre una conversación y a veces solo mantiene la cortesía.</p>
                <p>En Estados Unidos es habitual que el cajero del supermercado te diga <em>Hi, how are you?</em>. Espera algo como <em>Good, thanks. You?</em>, no un resumen de tu semana: es nuestro “¿qué tal?” dicho de pasada. Con un amigo al que no ves desde hace meses, en cambio, la misma pregunta sí invita a contar algo.</p>
                <div class="lesson-box"><strong>La fórmula segura:</strong> respuesta corta + gracias (opcional) + devolver la pregunta. <em>Pretty good, thanks. How about you?</em></div>
                <h2 id="respuestas">Respuestas a How are you según el registro</h2>
                <p>Estas cuatro te sirven para casi todo:</p>
                <div class="example-grid">
                <div class="mini-card"><strong>I’m good</strong><span>Muy común en Estados Unidos para una respuesta breve y positiva.</span></div>
                <div class="mini-card"><strong>Doing well</strong><span>Suena natural porque responde a la idea completa de <em>How are you doing?</em></span></div>
                <div class="mini-card"><strong>Pretty good</strong><span>Informal, útil con compañeros o gente que ves a menudo.</span></div>
                <div class="mini-card"><strong>Hanging in there</strong><span>Honesta y conversacional: no estás mal, pero tampoco celebrando la vida.</span></div>
                </div>
                <p>Y aquí tienes el mapa completo, de más formal a más sincera:</p>
                <table class="data-table">
                <thead><tr><th>Registro</th><th>Respuesta</th><th>Qué transmite</th></tr></thead>
                <tbody>
                <tr><td>Formal</td><td>I’m very well, thank you. And you?</td><td>Educada y algo clásica. Se oye más en Reino Unido.</td></tr>
                <tr><td>Formal</td><td>I’m doing well, thank you.</td><td>Profesional y cálida. Perfecta en el trabajo.</td></tr>
                <tr><td>Neutro</td><td>Good, thanks. You?</td><td>La respuesta comodín.</td></tr>
                <tr><td>Neutro</td><td>Fine, thanks.</td><td>Correcta, pero con tono plano puede sonar seca.</td></tr>
                <tr><td>Neutro</td><td>Not bad. / Not too bad.</td><td>“No me va mal”. Muy habitual en Reino Unido e Irlanda.</td></tr>
                <tr><td>Informal</td><td>Pretty good. / All good.</td><td>Relajada, entre compañeros y amigos.</td></tr>
                <tr><td>Informal</td><td>Great! / Can’t complain.</td><td>Positiva; <em>can’t complain</em> es “no me puedo quejar”.</td></tr>
                <tr><td>Negativa educada</td><td>Hanging in there.</td><td>“Aquí, tirando”.</td></tr>
                <tr><td>Negativa educada</td><td>Could be better.</td><td>“Podría ir mejor”. Invita a que te pregunten.</td></tr>
                <tr><td>Negativa educada</td><td>Not great, to be honest.</td><td>Sincera; mejor con gente de confianza.</td></tr>
                </tbody>
                </table>
                <p><em>I’m good</em> e <em>I’m well</em> son correctas. Algunos puristas prefieren <em>well</em> porque hablas de cómo estás, pero <em>I’m good</em> es totalmente normal en conversación. <em>Very good</em> también vale, con un punto más entusiasta. Y usa la versión contraída: <em>I am good</em>, con todas sus letras, suena rígido salvo que quieras enfatizar.</p>
                <p>Escucha cómo suenan <a href="/audio/very-good.html">very good</a>, <a href="/audio/pretty-good.html">pretty good</a>, <a href="/audio/doing-well.html">doing well</a> y <a href="/audio/hanging.html">hanging in there</a>.</p>
                <h2 id="pais">Diferencias por país: EE. UU., Reino Unido, Irlanda y Australia</h2>
                <p>En Irlanda es habitual escuchar respuestas como <em>I’m grand</em> (“bien”, sin más) o <em>not too bad</em>. En Estados Unidos se oyen mucho <em>I’m good</em>, <em>doing well</em> y <em>great</em>. En Reino Unido puede aparecer más la respuesta formal, pero también respuestas cortas como <em>I’m alright</em>, <em>not bad</em> o <em>very well</em>.</p>
                <p>Cada sitio tiene además sus propios saludos. En Inglaterra es frecuente <em>You alright?</em> como simple “hola”, y se contesta <em>Yeah, you?</em>, no con tu estado de salud. En Irlanda oirás <em>What’s the craic?</em> (“¿qué se cuenta?”), y en Australia, <em>How are you going?</em>, que significa lo mismo que <em>How are you?</em> y se responde <em>Good, thanks</em>.</p>
                <p>No hace falta copiar un país entero. Lo útil es reconocer las variantes para no bloquearte cuando no escuches la fórmula del libro de texto. Y recuerda que son tendencias, no reglas: dentro de cada país cambia mucho según la región, la edad y la persona.</p>
                <h2 id="preguntas">¿Qué responder a How are you doing?, How’s it going? y What’s up?</h2>
                <p>Cada pregunta tiene su respuesta natural, y casi siempre es un eco de la propia pregunta:</p>
                <table class="data-table">
                <thead><tr><th>Pregunta</th><th>Respuesta natural</th><th>Detalle</th></tr></thead>
                <tbody>
                <tr><td><a href="/audio/how-are-you.html">How are you?</a></td><td>Good, thanks. You?</td><td>La más neutra.</td></tr>
                <tr><td>How are you doing?</td><td>Doing well, thanks. / I’m doing great.</td><td>Repite <em>doing</em> en la respuesta.</td></tr>
                <tr><td><a href="/audio/hows-it-going.html">How’s it going?</a></td><td>Pretty good. / It’s going well.</td><td>Informal, con gente conocida.</td></tr>
                <tr><td><a href="/audio/whats-up.html">What’s up?</a></td><td>Not much. / Nothing much, you?</td><td>No es “¿cómo estás?”, sino “¿qué hay?”.</td></tr>
                <tr><td><a href="/audio/whats-going-on.html">What’s going on?</a></td><td>Not much. / Just working.</td><td>Como <em>What’s up?</em>, o “¿qué pasa aquí?” si algo va mal.</td></tr>
                <tr><td><a href="/audio/howve-you-been.html">How’ve you been?</a></td><td>I’ve been good, thanks. / Busy, but good.</td><td>Para alguien a quien no ves desde hace tiempo.</td></tr>
                <tr><td><a href="/audio/hows-it-been.html">How’s it been?</a></td><td>It’s been good. / It’s been busy.</td><td>Sobre un periodo o algo concreto: el trabajo nuevo, la mudanza.</td></tr>
                <tr><td><a href="/audio/hows-everything.html">How’s everything?</a></td><td>Everything’s good. / All good.</td><td>Invita a una respuesta un poco más amplia.</td></tr>
                <tr><td><a href="/audio/hows-your-day-going.html">How’s your day going?</a></td><td>So far, so good. / Busy, but good.</td><td>Buena opción a mitad del día.</td></tr>
                </tbody>
                </table>
                <p>Fíjate en el tiempo verbal: si te preguntan con <em>have been</em>, responde con <em>I’ve been</em>; si te preguntan con <em>going</em>, contesta con <em>going</em>. Es más fácil de lo que parece.</p>
                <div class="lesson-box"><strong>El error clásico:</strong> contestar <em>I’m fine</em> a <em>What’s up?</em>. No es un drama, pero suele sonar descolocado: te han preguntado qué hay de nuevo, no cómo estás. Lo natural es <em>Not much</em> o <em>Nothing much, you?</em>. Eso sí, si alguien te ve con mala cara y te dice <em>What’s up?</em>, te está preguntando qué te pasa.</div>
                <h2 id="plantillas">Cómo devolver la pregunta: plantillas seguras</h2>
                <p>Si no sabes qué decir, usa respuestas cortas con una repregunta. Son naturales y no te obligan a improvisar demasiado.</p>
                <div class="lesson-box">
                <p><strong>Contexto formal:</strong> I’m doing well, thank you. And yourself?</p>
                <p><strong>Contexto informal:</strong> Pretty good. How about you?</p>
                <p><strong>Hace tiempo que no os veis:</strong> I’ve been good, thanks. What about you?</p>
                <p><strong>Día difícil:</strong> Hanging in there. How are things with you?</p>
                </div>
                <p>Para devolver la pregunta valen <em>And you?</em>, <em>You?</em>, <em>How about you?</em>, <em>What about you?</em> y <em>And yourself?</em>, algo más cortés. Escucha <a href="/audio/doing-well-yourself.html">Doing well, yourself?</a> y repítelo hasta que te salga del tirón. Que suene a pregunta de verdad: si la dices plana, parece que no te interesa la respuesta.</p>
                <p>Si quieres seguir la conversación, añade una pregunta concreta: <em>How was your weekend?</em> (¿qué tal el finde?), <em>Busy day?</em> (¿mucho lío hoy?) o <em>How’s work?</em> (¿qué tal el trabajo?). Con eso pasas del saludo a una charla de verdad.</p>
                <h2 id="errores">Errores típicos al responder a How are you</h2>
                <ul>
                <li><strong>Usar siempre la misma frase.</strong> <em>I’m fine, thank you, and you?</em> funciona, pero repetida a todo el mundo suena aprendida de memoria.</li>
                <li><strong>Contar demasiado a un desconocido.</strong> En la caja del súper, una respuesta de tres palabras basta.</li>
                <li><strong>No devolver la pregunta.</strong> Responder y quedarte callado puede parecer frío.</li>
                <li><strong>Pronunciar palabra por palabra.</strong> En la vida real, <em>How are you?</em> sale casi como un solo bloque, y <em>How have you been?</em> se contrae en <em>How’ve you been?</em>. Lo explicamos en <a href="/articulos/ligar-palabras-ingles.html">cómo ligar palabras en inglés</a>.</li>
                </ul>
                <p>Elige hoy dos respuestas, una neutra y una informal, y úsalas hasta que te salgan solas. La próxima vez que alguien te pregunte qué tal, no tendrás que pensar: solo responder y devolver la pregunta.</p>
        """,
    },
    {
        "slug": "make-vs-do",
        "category": "Gramática real",
        "title": "Make vs do: cuándo usar cada verbo si los dos significan “hacer”",
        "seo_title": "Make vs do: diferencia, tabla de expresiones y ejercicio",
        "description": "Make or do: la diferencia entre make y do, una tabla con las expresiones que más dudas dan (the bed, homework, a trip...) y ejercicio con soluciones.",
        "lede": "En español decimos “hacer” para casi todo. En inglés, make y do se reparten ese territorio, y la diferencia se aprende mejor con patrones y bloques que con reglas sueltas.",
        "reading": "9 minutos",
        "published": "2026-06-28",
        "toc": [
            ("diferencia", "La diferencia"),
            ("do", "Usar do"),
            ("make", "Usar make"),
            ("tabla", "Tabla make or do"),
            ("phrasal", "Phrasal verbs"),
            ("ejercicio", "Ejercicio"),
            ("aprender", "Aprender bloques"),
        ],
        "related": [
            "fun-vs-funny",
            "how-are-you-respuestas-ingles",
            "preposiciones-in-on-at",
            "ligar-palabras-ingles",
        ],
        "quick_answer": "<strong>Do</strong> se usa para actividades y tareas (<em>do homework</em>, <em>do the dishes</em>); <strong>make</strong>, cuando creas o provocas algo (<em>make a cake</em>, <em>make a decision</em>, <em>make a mistake</em>). Muchas combinaciones son fijas: se dice <em>make the bed</em>, y un viaje no es make ni do, sino <em>take a trip</em>.",
        "faq": [
            ("¿Se dice make or do homework?", "Se dice <em>do homework</em>: <em>I have to do my homework</em>. <em>Homework</em> es incontable, así que nunca lleva plural (<em>homeworks</em> es incorrecto)."),
            ("¿Se dice make the bed o do the bed?", "Se dice <em>make the bed</em> (hacer la cama). Es una combinación fija, aunque en realidad no estés creando nada; <em>do the bed</em> no se usa."),
            ("¿Se dice make exercise o do exercise?", "Lo correcto es <em>do exercise</em>, <em>get exercise</em> o simplemente el verbo <em>exercise</em>: <em>I exercise three times a week</em>. En registro informal también se dice <em>work out</em>. <em>Make exercise</em> es un error típico de hispanohablantes."),
            ("¿Se dice make a trip o take a trip?", "Para un viaje de vacaciones o de trabajo se dice <em>take a trip</em> o <em>go on a trip</em>. <em>Make a trip</em> solo suena natural para desplazamientos prácticos, como <em>make two trips to the car</em> (hacer dos viajes al coche)."),
            ("¿Se dice make a favor o do a favor?", "Se dice <em>do someone a favor</em> (<em>favour</em> en inglés británico): <em>Can you do me a favor?</em> Para pedir un favor se usa <em>ask</em>: <em>Can I ask you a favor?</em>"),
        ],
        "body": """
                <p><strong>Make</strong> y <strong>do</strong> se traducen muchas veces como “hacer”, pero no son intercambiables. Si intentas traducir palabra por palabra desde el español, tarde o temprano dirás una combinación que suena rara: <em>do a mistake</em>, <em>make the homework</em>, <em>make a photo</em>. Por eso la duda “make or do” aparece en cuanto empiezas a hablar en serio.</p>
                <p>La regla mental más útil es esta: <strong>do</strong> se asocia con realizar una acción o completar una tarea; <strong>make</strong> se asocia con crear, producir, causar o lograr algo. Esa regla explica la mayoría de casos, pero no todos: muchas combinaciones son fijas y hay que aprenderlas como bloques. Aquí tienes las dos cosas: la lógica y la tabla.</p>

                <h2 id="diferencia">¿Cuál es la diferencia entre make y do?</h2>
                <p>Antes de elegir, hazte una pregunta: <strong>¿al final hay algo que antes no existía?</strong> Si la respuesta es sí (una tarta, un plan, un ruido, un error, un amigo nuevo), lo normal es <em>make</em>. Si lo que hay es una actividad, una obligación o un trabajo que se lleva a cabo (los deberes, la colada, un curso), lo normal es <em>do</em>.</p>
                <p>Otra pista: cuando no dices qué acción concreta es, el inglés usa <em>do</em>. <em>What are you doing?</em> (¿Qué haces?), <em>I have nothing to do</em> (No tengo nada que hacer). Y ojo con <em>What do you do?</em>: no significa “¿qué estás haciendo?”, sino “¿a qué te dedicas?”.</p>

                <h2 id="do">¿Cuándo se usa do?</h2>
                <p>Usa <em>do</em> cuando el foco está en la actividad, el proceso o la tarea. No estás fabricando un objeto nuevo; estás llevando a cabo algo.</p>
                <ul>
                <li><strong>Tareas de casa:</strong> <em>do the dishes</em>, <em>do the laundry</em>, <em>do the ironing</em>, <em>do the cleaning</em>.</li>
                <li><strong>Estudios y trabajo:</strong> <em>do a course</em>, <em>do business</em>, <em>do a good job</em>, <em>do well</em> (salir bien: <em>She did well in the exam</em>).</li>
                <li><strong>Efectos buenos o malos:</strong> <em>do your best</em> (hacer todo lo posible), <em>do harm</em> (perjudicar), <em>do good</em> (hacer bien).</li>
                <li><strong>Arreglarse:</strong> <em>do your hair</em> (peinarse), <em>do your nails</em> (hacerse las uñas).</li>
                </ul>
                <div class="example-grid">
                <div class="mini-card"><strong>do the dishes</strong><span>Fregar o lavar los platos.</span></div>
                <div class="mini-card"><strong>do your homework</strong><span>Hacer los deberes.</span></div>
                <div class="mini-card"><strong>do me a favor</strong><span>Hacerme un favor.</span></div>
                <div class="mini-card"><strong>do research</strong><span>Investigar, llevar a cabo una investigación.</span></div>
                </div>
                <div class="lesson-box"><strong>Deportes:</strong> con deportes de pelota se usa <em>play</em> (<em>play tennis</em>); con actividades en <em>-ing</em>, normalmente <em>go</em> (<em>go swimming</em>); y con muchas de las demás, <em>do</em> (<em>do yoga</em>, <em>do judo</em>). Es una tendencia, no una ley, pero acierta casi siempre.</div>

                <h2 id="make">¿Cuándo se usa make?</h2>
                <p>Usa <em>make</em> cuando hay creación, resultado, efecto o consecución. A veces el resultado es físico, como comida (<em>make dinner</em>, <em>make coffee</em>); otras veces es abstracto, como una decisión o una diferencia (<em>make a difference</em>, <em>make a suggestion</em>, <em>make a complaint</em>, <em>make an effort</em>).</p>
                <div class="example-grid">
                <div class="mini-card"><strong>make a decision</strong><span>Tomar una decisión. En Reino Unido también <em>take a decision</em>.</span></div>
                <div class="mini-card"><strong>make money</strong><span>Ganar dinero.</span></div>
                <div class="mini-card"><strong>make a mistake</strong><span>Cometer un error.</span></div>
                <div class="mini-card"><strong>make progress</strong><span>Progresar.</span></div>
                </div>
                <p><em>Make</em> también traduce “hacer” + infinitivo: <strong>make + persona + verbo sin to</strong>. <em>She made me laugh</em> (Me hizo reír), no <em>made me to laugh</em>. Solo en pasiva aparece el <em>to</em>: <em>We were made to wait</em>. Con adjetivos significa “poner”: <em>It makes me nervous</em> (Me pone nervioso).</p>

                <h2 id="tabla">¿Make or do? Tabla de expresiones que más dudas generan</h2>
                <p>Estas son las combinaciones por las que más se pregunta. Algunas siguen la regla y otras son fijas sin más; léelas en voz alta como bloques completos.</p>
                <table class="data-table">
                <thead><tr><th>En español</th><th>En inglés</th><th>Ojo</th></tr></thead>
                <tbody>
                <tr><td>Hacer la cama</td><td><strong>make</strong> the bed</td><td>Fija. Nunca <em>do the bed</em>.</td></tr>
                <tr><td>Hacer los deberes</td><td><strong>do</strong> (your) homework</td><td>Incontable: nada de <em>homeworks</em>.</td></tr>
                <tr><td>Hacer un favor</td><td><strong>do</strong> someone a favor</td><td><em>favour</em> en Reino Unido. Pedirlo: <em>ask a favor</em>.</td></tr>
                <tr><td>Hacer una reserva</td><td><strong>make</strong> a reservation / a booking</td><td>También <em>book a table</em>.</td></tr>
                <tr><td>Hacer ejercicio</td><td><strong>do</strong> / <strong>get</strong> exercise</td><td>O el verbo <em>exercise</em>. Nunca <em>make exercise</em>.</td></tr>
                <tr><td>Hacer una lista</td><td><strong>make</strong> a list</td><td>También <em>write a list</em>.</td></tr>
                <tr><td>Hacer amigos</td><td><strong>make</strong> friends</td><td><em>make friends with someone</em>.</td></tr>
                <tr><td>Hacer un viaje</td><td><strong>take</strong> / <strong>go on</strong> a trip</td><td>Ni <em>make</em> ni <em>do</em> (mira la nota).</td></tr>
                <tr><td>Hacer un examen</td><td><strong>take</strong> an exam</td><td>Reino Unido: también <em>do</em> o <em>sit</em>. Nunca <em>make</em>.</td></tr>
                <tr><td>Hacer la compra</td><td><strong>do</strong> the shopping</td><td>EE. UU.: <em>do the grocery shopping</em>.</td></tr>
                <tr><td>Hacer la colada</td><td><strong>do</strong> the laundry</td><td>Reino Unido: también <em>do the washing</em>.</td></tr>
                <tr><td>Hacer ruido</td><td><strong>make</strong> (a) noise</td><td><em>Don't make so much noise!</em></td></tr>
                <tr><td>Hacer una llamada</td><td><strong>make</strong> a call</td><td>Recibirla: <em>take a call</em>.</td></tr>
                <tr><td>Hacer daño</td><td><strong>do</strong> damage / harm</td><td>Daño físico a alguien: <em>hurt</em>.</td></tr>
                <tr><td>Hacer planes</td><td><strong>make</strong> plans</td><td><em>Any plans for the weekend?</em></td></tr>
                <tr><td>Pedir cita</td><td><strong>make</strong> an appointment</td><td>Médico, dentista, peluquería.</td></tr>
                <tr><td>Tener sentido</td><td><strong>make</strong> sense</td><td>Nunca <em>have sense</em>.</td></tr>
                <tr><td>Hacer lo posible</td><td><strong>do</strong> your best</td><td><em>I'll do my best.</em></td></tr>
                </tbody>
                </table>
                <div class="lesson-box"><strong>El caso del viaje:</strong> para irte de vacaciones o de viaje de trabajo, lo natural es <em>take a trip</em> o <em>go on a trip</em>. <em>Do a trip</em> se oye a veces en conversación muy informal, pero no es la opción segura. <em>Make a trip</em> existe, aunque para desplazamientos prácticos: <em>I had to make three trips to carry all the bags</em> (tuve que hacer tres viajes para llevar las bolsas).</div>

                <h2 id="ni-make-ni-do">Cuando “hacer” no es ni make ni do</h2>
                <p>Muchos errores vienen de suponer que “hacer” siempre tiene que ser uno de los dos. Las trampas más frecuentes:</p>
                <div class="example-grid">
                <div class="mini-card"><strong>take a photo</strong><span>Hacer una foto.</span></div>
                <div class="mini-card"><strong>ask a question</strong><span>Hacer una pregunta.</span></div>
                <div class="mini-card"><strong>have a party</strong><span>Hacer una fiesta (también <em>throw a party</em>).</span></div>
                <div class="mini-card"><strong>It's cold</strong><span>Hace frío: el tiempo va con <em>be</em>.</span></div>
                <div class="mini-card"><strong>two years ago</strong><span>Hace dos años.</span></div>
                <div class="mini-card"><strong>You never listen to me</strong><span>Nunca me haces caso.</span></div>
                </div>

                <h2 id="matiz">El matiz de make it</h2>
                <p><em>Make it</em> añade una idea de conseguir algo que no era automático. Puede hablar de llegar a tiempo, lograr entrar en un lugar, asistir a un evento o triunfar en un entorno competitivo.</p>
                <div class="lesson-box">
                <p><strong>I made it to the airport on time.</strong> Llegué al aeropuerto a tiempo, probablemente con cierta dificultad.</p>
                <p><strong>He made it in Hollywood.</strong> Logró triunfar en Hollywood.</p>
                <p><strong>I could not make it to the party.</strong> No pude ir a la fiesta.</p>
                </div>
                <p>También se usa para quedar: <em>Can you make it on Friday?</em> (¿Puedes el viernes?) o <em>Let's make it eight</em> (Mejor a las ocho).</p>

                <h2 id="phrasal">Phrasal verbs y expresiones con make y do</h2>
                <table class="data-table">
                <thead><tr><th>Expresión</th><th>Significado</th><th>Ejemplo</th></tr></thead>
                <tbody>
                <tr><td>make sure</td><td>asegurarse</td><td><em>Make sure you lock the door.</em></td></tr>
                <tr><td>make sense</td><td>tener sentido</td><td><em>It doesn't make sense.</em></td></tr>
                <tr><td>make up</td><td>inventar; reconciliarse</td><td><em>He made up an excuse.</em> / <em>They've made up.</em></td></tr>
                <tr><td>make up your mind</td><td>decidirte</td><td><em>Make up your mind!</em></td></tr>
                <tr><td>make out</td><td>distinguir o entender con dificultad</td><td><em>I couldn't make out what she said.</em></td></tr>
                <tr><td>make out (with someone)</td><td>en inglés americano informal, enrollarse, besarse</td><td>Cuidado con el contexto.</td></tr>
                <tr><td>make do (with)</td><td>apañarse con lo que hay</td><td><em>We made do with what we had.</em></td></tr>
                <tr><td>make fun of</td><td>burlarse de</td><td><em>Don't make fun of him.</em></td></tr>
                <tr><td>do without</td><td>arreglárselas sin</td><td><em>I can't do without coffee.</em></td></tr>
                <tr><td>could do with</td><td>venir bien</td><td><em>I could do with a break.</em></td></tr>
                <tr><td>have nothing to do with</td><td>no tener nada que ver con</td><td><em>It has nothing to do with you.</em></td></tr>
                </tbody>
                </table>
                <p><em>Make fun of</em> parece diversión, pero significa burlarse; lo explico en <a href="/articulos/fun-vs-funny.html">fun vs funny</a>. Y en el habla, estos verbos se pegan a la palabra siguiente: <em>make it up</em> suena casi como una sola palabra, igual que <a href="/audio/pick-it-up.html">pick it up</a> o <a href="/audio/take-it-off.html">take it off</a>. Tienes más sobre ese fenómeno en <a href="/articulos/ligar-palabras-ingles.html">cómo ligar palabras en inglés</a>.</p>

                <h2 id="ejercicio">Ejercicio: ¿make or do?</h2>
                <p>Completa cada frase con la forma correcta de <em>make</em> o <em>do</em>, o con otro verbo si ninguno encaja. Pulsa para ver la solución.</p>
                <details class="exercise"><summary>1. Can you ___ me a favor?</summary><p><strong>do</strong>. Los favores se hacen con <em>do</em> (en inglés británico se escribe <em>favour</em>).</p></details>
                <details class="exercise"><summary>2. I always ___ the bed before breakfast.</summary><p><strong>make</strong>. <em>Make the bed</em> es una combinación fija.</p></details>
                <details class="exercise"><summary>3. Have you ___ your homework yet?</summary><p><strong>done</strong>. Los deberes son una tarea: <em>do your homework</em>.</p></details>
                <details class="exercise"><summary>4. We'd like to ___ a reservation for two at nine.</summary><p><strong>make</strong>. <em>Make a reservation</em>, o simplemente <em>book a table</em>.</p></details>
                <details class="exercise"><summary>5. My doctor says I should ___ more exercise.</summary><p><strong>do</strong> (o <strong>get</strong>). Nunca <em>make exercise</em>.</p></details>
                <details class="exercise"><summary>6. Let me ___ a list so I don't forget anything.</summary><p><strong>make</strong>. Al final hay algo que antes no existía: la lista.</p></details>
                <details class="exercise"><summary>7. It isn't easy to ___ friends in a new city.</summary><p><strong>make</strong>. <em>Make friends</em>, y “hacerse amigo de alguien” es <em>make friends with someone</em>.</p></details>
                <details class="exercise"><summary>8. Sorry, I think I've ___ a mistake.</summary><p><strong>made</strong>. <em>Do a mistake</em> es uno de los errores más típicos.</p></details>
                <details class="exercise"><summary>9. That doesn't ___ any sense.</summary><p><strong>make</strong>. <em>It doesn't make sense</em>; nunca <em>have sense</em>.</p></details>
                <details class="exercise"><summary>10. Last summer we ___ a trip to Scotland.</summary><p><strong>took</strong> o <strong>went on</strong>. Para un viaje de vacaciones, ni <em>make</em> ni <em>do</em>.</p></details>

                <h2 id="aprender">Cómo aprenderlos sin memorizar listas infinitas</h2>
                <p>No intentes aprender make y do como una regla matemática. Aprende bloques frecuentes: <em>make sure</em>, <em>make sense</em>, <em>do your best</em>, <em>do nothing</em>. Cuando memorizas la combinación completa, la frase sale más rápido y con menos traducción mental.</p>
                <p>Luego añade tus propias frases. Por ejemplo: <em>I need to make time to practice English</em> o <em>I will do my best in the interview</em>. Si la frase conecta con tu vida, se queda.</p>
                <p><em>Do</em> también vive en saludos como <em>How are you doing?</em>, que se contesta con algo como <a href="/audio/doing-well.html">Doing well</a> (más respuestas en <a href="/articulos/how-are-you-respuestas-ingles.html">How are you y cómo responder</a>). Para esta semana: elige cinco expresiones de la tabla que uses de verdad y dilas en voz alta cada vez que hagas esa actividad.</p>
        """,
    },
    {
        "slug": "preposiciones-in-on-at",
        "category": "Preposiciones",
        "title": "In, on, at en inglés: cuándo se usa cada una (tiempo, lugar y ejemplos)",
        "seo_title": "In, on, at en inglés: cuándo se usa cada una (con ejemplos)",
        "description": "In, on, at: cuándo se usa cada preposición con horas, días, meses, lugares y transportes, excepciones como at night y un ejercicio con soluciones.",
        "lede": "In, on y at son difíciles porque las tres pueden traducirse como “en”. La salida es dejar de traducir y pensar en espacio, superficie o punto concreto.",
        "reading": "10 minutos",
        "published": "2026-06-28",
        "toc": [
            ("tiempo", "Tiempo"),
            ("lugar", "Lugar"),
            ("transporte", "Transporte"),
            ("excepciones", "Excepciones"),
            ("ejercicio", "Ejercicio"),
            ("truco", "Truco mental"),
        ],
        "related": [
            "preposiciones-to-for-by-from-with",
            "make-vs-do",
            "some-vs-any",
            "ligar-palabras-ingles",
        ],
        "quick_answer": "Con el tiempo, <strong>in</strong> va con periodos largos (<em>in May</em>), <strong>on</strong> con días y fechas (<em>on Monday</em>) y <strong>at</strong> con horas (<em>at 7 p.m.</em>). Con lugares, <em>in</em> es dentro (<em>in the kitchen</em>), <em>on</em> es encima (<em>on the table</em>) y <em>at</em> es un punto concreto (<em>at the bus stop</em>).",
        "faq": [
            ("¿Se dice in the weekend, on the weekend o at the weekend?", "En inglés británico se dice <em>at the weekend</em> y en inglés americano <em>on the weekend</em>; las dos son correctas. <em>In the weekend</em> no es la forma habitual, así que mejor evítala."),
            ("¿Por qué se dice in the morning pero at night?", "Es un uso fijo: las partes del día van con <em>in</em> (<em>in the morning</em>, <em>in the afternoon</em>, <em>in the evening</em>), pero <em>night</em> va con <em>at</em>. <em>In the night</em> también existe para algo que pasa durante una noche concreta."),
            ("¿Cuál es la diferencia entre on time e in time?", "<em>On time</em> significa puntual, a la hora prevista: <em>The bus arrived on time</em>. <em>In time</em> significa a tiempo, con margen suficiente para algo: <em>We arrived in time for dinner</em>."),
            ("¿Se dice in the bus o on the bus?", "Se dice <em>on the bus</em>, igual que <em>on the train</em> y <em>on the plane</em>. Con vehículos pequeños en los que solo te sientas se usa <em>in</em>: <em>in a car</em>, <em>in a taxi</em>. Para el medio en general, <em>by bus</em>."),
            ("¿Qué preposición va con las fechas en inglés?", "Con una fecha completa o un día concreto se usa <em>on</em>: <em>on 4 July</em> (UK) u <em>on July 4</em> (US). Si solo dices el mes o el año, <em>in</em>: <em>in July</em>, <em>in 2026</em>."),
        ],
        "body": """
                <p>Para un hispanohablante, <strong>in</strong>, <strong>on</strong> y <strong>at</strong> tienen una trampa: en muchos casos las tres se traducen como “en”. Si dependes de la traducción, cada frase parece una apuesta. Y como además sirven para el tiempo y para el lugar, la pregunta “in, on, at: ¿cuándo se usa cada una?” aparece en cuanto empiezas a hablar.</p>
                <p>La forma práctica de mejorar es asociar cada preposición con una imagen mental. <em>In</em> suele apuntar a estar dentro de algo o en un marco amplio. <em>On</em> suele apuntar a superficie, día o línea. <em>At</em> suele apuntar a un punto concreto.</p>
                <div class="example-grid">
                <div class="mini-card"><strong>IN = una caja</strong><span>Dentro de un espacio o de un periodo largo: <em>in the box</em>, <em>in Madrid</em>, <em>in July</em>.</span></div>
                <div class="mini-card"><strong>ON = una superficie</strong><span>Encima de algo, sobre una línea o en un día: <em>on the table</em>, <em>on the coast</em>, <em>on Monday</em>.</span></div>
                <div class="mini-card"><strong>AT = un punto</strong><span>Un punto en el mapa o en el reloj: <em>at the door</em>, <em>at the station</em>, <em>at 7 p.m.</em></span></div>
                <div class="mini-card"><strong>El embudo del tiempo</strong><span><em>in 2026</em> → <em>in July</em> → <em>on Monday</em> → <em>at 7 p.m.</em> Cuanto más concreto, más bajas.</span></div>
                </div>

                <h2 id="tiempo">¿Cuándo se usa in, on y at con el tiempo?</h2>
                <table class="data-table">
                <thead><tr><th>Preposición</th><th>Se usa con</th><th>Ejemplos</th></tr></thead>
                <tbody>
                <tr><td><strong>in</strong></td><td>Meses, años, décadas, siglos</td><td>in May, in 2026, in the nineties, in the 19th century</td></tr>
                <tr><td><strong>in</strong></td><td>Estaciones</td><td>in summer, in the winter</td></tr>
                <tr><td><strong>in</strong></td><td>Partes del día</td><td>in the morning, in the afternoon, in the evening</td></tr>
                <tr><td><strong>in</strong></td><td>Plazo futuro (“dentro de”)</td><td>in ten minutes, in two weeks</td></tr>
                <tr><td><strong>on</strong></td><td>Días de la semana</td><td>on Monday, on Fridays</td></tr>
                <tr><td><strong>on</strong></td><td>Fechas</td><td>on 12 October (UK), on October 12 (US)</td></tr>
                <tr><td><strong>on</strong></td><td>Días especiales</td><td>on my birthday, on Christmas Day</td></tr>
                <tr><td><strong>on</strong></td><td>Día + parte del día</td><td>on Monday morning, on Friday night</td></tr>
                <tr><td><strong>at</strong></td><td>Horas exactas</td><td>at 7 o'clock, at 8:30, at noon, at midnight</td></tr>
                <tr><td><strong>at</strong></td><td>La noche</td><td>at night</td></tr>
                <tr><td><strong>at</strong></td><td>Fiestas como periodo</td><td>at Christmas, at Easter</td></tr>
                <tr><td><strong>at</strong></td><td>El fin de semana</td><td>at the weekend (UK) / on the weekend (US)</td></tr>
                <tr><td><strong>at</strong></td><td>Momentos puntuales</td><td>at the moment, at lunchtime, at the same time</td></tr>
                </tbody>
                </table>
                <p>Fíjate en el salto entre <em>in the morning</em> y <em>on Monday morning</em>: en cuanto la parte del día pertenece a un día concreto, manda el día y pasas a <em>on</em>. Lo mismo con <em>at Christmas</em> (las fiestas en general) frente a <em>on Christmas Day</em> (el día 25).</p>
                <p>Y ojo con <em>in</em> + periodo en futuro: significa “dentro de”. <em>The train leaves in ten minutes</em> es “sale dentro de diez minutos”. Para “en un plazo de”, usa <em>within</em>.</p>
                <div class="lesson-box"><strong>Sin preposición:</strong> con <em>this</em>, <em>next</em>, <em>last</em> y <em>every</em> no se pone <em>in</em>, <em>on</em> ni <em>at</em>: <em>See you next Monday</em>, <em>I went there last year</em>, <em>I work every day</em>. Tampoco con <em>today</em>, <em>tomorrow</em>, <em>yesterday</em> o <em>tonight</em>. Decir <em>on next Monday</em> o <em>in last summer</em> es uno de los errores más típicos.</div>

                <h2 id="lugar">¿Cuándo se usa in, on y at con lugares?</h2>
                <p>Para los lugares vuelve la imagen mental. A veces el mismo sitio admite dos preposiciones según cómo lo mires: <em>I'm in the station</em> (dentro del edificio) frente a <em>I'm at the station</em> (la estación como punto de referencia, dentro o en la puerta).</p>
                <table class="data-table">
                <thead><tr><th>Preposición</th><th>Imagen</th><th>Ejemplos</th></tr></thead>
                <tbody>
                <tr><td><strong>in</strong></td><td>Dentro de un espacio con límites</td><td>in the kitchen, in the park, in Madrid, in Spain</td></tr>
                <tr><td><strong>in</strong></td><td>Dentro de imágenes y textos</td><td>in the photo, in the book, in the mirror</td></tr>
                <tr><td><strong>on</strong></td><td>Superficie</td><td>on the table, on the wall, on the floor</td></tr>
                <tr><td><strong>on</strong></td><td>Línea: calles, costas, ríos</td><td>on Main Street, on the coast, on the river</td></tr>
                <tr><td><strong>on</strong></td><td>Pisos, lados, páginas</td><td>on the first floor, on the left, on page 20</td></tr>
                <tr><td><strong>on</strong></td><td>Medios</td><td>on TV, on the radio, on the phone, on the internet</td></tr>
                <tr><td><strong>at</strong></td><td>Punto concreto</td><td>at the door, at the bus stop, at 25 Baker Street</td></tr>
                <tr><td><strong>at</strong></td><td>Lugar por su función</td><td>at home, at work, at school, at the doctor's</td></tr>
                <tr><td><strong>at</strong></td><td>Eventos</td><td>at the party, at the concert, at a meeting</td></tr>
                </tbody>
                </table>
                <p>Ojo: para el movimiento hacia un sitio no se usa ninguna de las tres, sino <em>to</em>. Escúchalo en <a href="/audio/i-want-to-go-to-london.html">I want to go to London</a>; una vez allí, ya dirás <em>I'm in London</em>. Tienes el resto de preposiciones de movimiento en <a href="/articulos/preposiciones-to-for-by-from-with.html">to, for, by, from y with</a>.</p>

                <h3 id="in">In: dentro de un espacio</h3>
                <p>Usa <em>in</em> para espacios cerrados, lugares grandes y cualquier cosa con límites claros.</p>
                <div class="example-grid">
                <div class="mini-card"><strong>I'm in the kitchen</strong><span>Estoy en la cocina. Hay idea de interior.</span></div>
                <div class="mini-card"><strong>She lives in Spain</strong><span>Países, ciudades y zonas grandes usan <em>in</em>.</span></div>
                <div class="mini-card"><strong>I'm still in bed</strong><span>Sigo en la cama. Sin artículo cuando es para dormir o descansar.</span></div>
                <div class="mini-card"><strong>Who's that in the photo?</strong><span>Fotos, cuadros, espejos y libros van con <em>in</em>.</span></div>
                </div>
                <p>Dos diferencias regionales: en Reino Unido los niños juegan <em>in the street</em> y en EE. UU. <em>on the street</em>; y alguien ingresado está <em>in hospital</em> en Reino Unido e <em>in the hospital</em> en EE. UU.</p>

                <h3 id="on">On: superficie, calle o línea</h3>
                <p>Usa <em>on</em> para superficies (aunque sean verticales, como una pared), calles y todo lo que se entiende como una línea.</p>
                <div class="example-grid">
                <div class="mini-card"><strong>The book is on the table</strong><span>El libro está sobre la mesa.</span></div>
                <div class="mini-card"><strong>There's a map on the wall</strong><span>La pared también es una superficie.</span></div>
                <div class="mini-card"><strong>On Main Street</strong><span>Calles y avenidas suelen usar <em>on</em>; en Reino Unido también se oye <em>in</em>.</span></div>
                <div class="mini-card"><strong>On the first floor</strong><span>Pisos de un edificio. En EE. UU., <em>first floor</em> es la planta baja.</span></div>
                </div>

                <h3 id="at">At: un punto concreto</h3>
                <p>Usa <em>at</em> para puntos concretos: una localización específica, un lugar definido por lo que haces allí o un evento.</p>
                <div class="example-grid">
                <div class="mini-card"><strong>At home</strong><span>Casa como punto de referencia, aunque estés en el jardín.</span></div>
                <div class="mini-card"><strong>At the bus stop</strong><span>Un punto concreto donde alguien espera.</span></div>
                <div class="mini-card"><strong>At the concert</strong><span>Eventos y actividades organizadas.</span></div>
                <div class="mini-card"><strong>At 25 Baker Street</strong><span>Dirección con número: <em>at</em>. Solo la calle: <em>on</em>.</span></div>
                </div>

                <h2 id="transporte">In a car, on a bus: ¿qué preposición va con cada transporte?</h2>
                <p>La regla clásica: si puedes ponerte de pie y caminar dentro, normalmente <em>on</em>; si solo entras y te sientas, <em>in</em>. Bicis y motos van con <em>on</em> porque vas encima. Y para hablar del medio en general, <em>by</em>, sin artículo.</p>
                <table class="data-table">
                <thead><tr><th>in</th><th>on</th><th>by (medio, sin artículo)</th></tr></thead>
                <tbody>
                <tr><td>in a car, in a taxi, in a van</td><td>on a bus, on a train, on a plane, on a ship</td><td>by car, by bus, by train, by plane</td></tr>
                <tr><td>get in / get out of</td><td>get on / get off</td><td>a pie: <em>on foot</em></td></tr>
                </tbody>
                </table>
                <div class="lesson-box"><strong>By frente a in/on:</strong> <em>I go to work by bus</em>, pero en cuanto concretas el vehículo, cambias: <em>I go to work in my car</em>, <em>I was on the 8:15 train</em>. A pie es <em>on foot</em>; <em>by foot</em> se oye, pero <em>on foot</em> es la forma estándar.</div>

                <h2 id="excepciones">Excepciones que confunden: at night, on time, in the end</h2>
                <table class="data-table">
                <thead><tr><th>Pareja</th><th>Diferencia</th></tr></thead>
                <tbody>
                <tr><td>in the morning / at night</td><td>Las partes del día van con <em>in</em>, pero la noche con <em>at</em>. <em>In the night</em> existe para algo que pasa durante una noche: <em>I woke up twice in the night</em>.</td></tr>
                <tr><td>on time / in time</td><td><em>On time</em> = puntual: <em>The train left on time</em>. <em>In time</em> = a tiempo, con margen para algo: <em>We got there in time to see the start</em>.</td></tr>
                <tr><td>at the end / in the end</td><td><em>At the end of</em> = al final de algo concreto: <em>at the end of the film</em>. <em>In the end</em> = finalmente: <em>In the end, we stayed at home</em>.</td></tr>
                <tr><td>at the weekend / on the weekend</td><td>La primera es británica y la segunda americana. Las dos son correctas.</td></tr>
                <tr><td>arrive in / arrive at</td><td><em>Arrive in</em> con ciudades y países (<em>arrive in London</em>); <em>arrive at</em> con edificios y puntos (<em>arrive at the airport</em>). Lo que casi nunca oirás es <em>arrive to London</em>.</td></tr>
                <tr><td>in the corner / on the corner</td><td><em>In the corner</em> de una habitación; <em>on</em> (o <em>at</em>) <em>the corner</em> de una calle.</td></tr>
                </tbody>
                </table>
                <p>Ya que hablamos de <em>on time</em> e <em>in time</em>, practica también la palabra <a href="/audio/time.html">time</a>.</p>

                <h2 id="ejercicio">Ejercicio: ¿in, on o at?</h2>
                <p>Completa con <em>in</em>, <em>on</em>, <em>at</em> o nada. Pulsa cada frase para ver la solución.</p>
                <details class="exercise"><summary>1. My birthday is ___ June.</summary><p><strong>in</strong>. Mes sin día concreto: <em>in June</em>.</p></details>
                <details class="exercise"><summary>2. The meeting is ___ Monday ___ 10 a.m.</summary><p><strong>on</strong> y <strong>at</strong>. Día con <em>on</em>, hora exacta con <em>at</em>.</p></details>
                <details class="exercise"><summary>3. I can't sleep ___ night.</summary><p><strong>at</strong>. <em>In the morning</em>, <em>in the evening</em>... pero <em>at night</em>.</p></details>
                <details class="exercise"><summary>4. He was born ___ 12 March 1990.</summary><p><strong>on</strong>. En cuanto hay día concreto, manda <em>on</em>, aunque también aparezcan mes y año.</p></details>
                <details class="exercise"><summary>5. See you ___ the weekend!</summary><p><strong>at</strong> (inglés británico) u <strong>on</strong> (inglés americano). Las dos son correctas.</p></details>
                <details class="exercise"><summary>6. I'll call you ___ next Friday.</summary><p><strong>Sin preposición</strong>: <em>I'll call you next Friday</em>. Con <em>next</em>, <em>last</em>, <em>this</em> y <em>every</em> no se pone nada.</p></details>
                <details class="exercise"><summary>7. The keys are ___ the table.</summary><p><strong>on</strong>. Superficie.</p></details>
                <details class="exercise"><summary>8. I'll meet you ___ the bus stop.</summary><p><strong>at</strong>. Un punto concreto de encuentro.</p></details>
                <details class="exercise"><summary>9. She lives ___ a small town ___ the coast.</summary><p><strong>in</strong> y <strong>on</strong>. Dentro del pueblo; el pueblo, sobre la línea de la costa.</p></details>
                <details class="exercise"><summary>10. I was ___ the train when you called, and then I got ___ a taxi.</summary><p><strong>on</strong> e <strong>in</strong> (o <em>into</em>). Tren con <em>on</em>; taxi con <em>in</em>.</p></details>
                <details class="exercise"><summary>11. The train left exactly ___ time.</summary><p><strong>on</strong>. <em>On time</em> es puntual; <em>in time</em> sería “a tiempo para algo”.</p></details>
                <details class="exercise"><summary>12. ___ the end, we decided to stay at home.</summary><p><strong>In</strong>. <em>In the end</em> = al final, finalmente. <em>At the end</em> necesita un “de”: <em>at the end of the film</em>.</p></details>

                <h2 id="truco">Un truco mental que funciona</h2>
                <p>Si estás bloqueado, pregúntate qué imagen domina la frase: dentro de un espacio, sobre una superficie o en un punto. No resuelve todos los casos, pero te da una primera decisión mucho mejor que traducir “en”.</p>
                <div class="lesson-box">
                <strong>Detalle útil:</strong> si dudas entre <em>in</em> y <em>on</em>, <em>in</em> es muy frecuente y a veces te salvará, pero no conviertas eso en una regla universal.
                </div>
                <p>Un apunte de pronunciación: en una frase normal, <em>at</em> casi nunca suena <span class="ipa">/æt/</span>, sino débil, <span class="ipa">/ət/</span> (igual en EE. UU. y Reino Unido), y se pega a lo que viene detrás: <em>at eight</em> suena casi como una sola palabra. Lo explico en <a href="/articulos/ligar-palabras-ingles.html">cómo ligar palabras en inglés</a>.</p>
                <p>Para fijarlo, describe tu semana en voz alta: <em>I get up at seven, I work in an office, on Fridays I go out at night...</em> Frases sobre tu vida valen más que cualquier lista.</p>
        """,
    },
    {
        "slug": "preposiciones-to-for-by-from-with",
        "category": "Preposiciones",
        "title": "To, for, by, from y with: diferencias y usos sin traducir palabra por palabra",
        "seo_title": "To, for, by, from y with: diferencias y usos en inglés",
        "description": "Diferencia entre to y for, by o with, until o by: usos de to, for, by, from y with con tablas, errores típicos de españoles y ejercicio resuelto.",
        "lede": "Después de in, on y at, estas cinco preposiciones aparecen constantemente. Conviene aprenderlas por función, no por traducción aislada, porque “para” y “por” tienen varias salidas en inglés.",
        "reading": "9 minutos",
        "published": "2026-06-28",
        "toc": [
            ("resumen", "Tabla resumen"),
            ("to-o-for", "¿To o for?"),
            ("by-with", "¿By o with?"),
            ("until-by", "¿Until o by?"),
            ("from-with", "From y with"),
            ("ejercicio", "Ejercicio"),
        ],
        "related": [
            "preposiciones-in-on-at",
            "make-vs-do",
            "ligar-palabras-ingles",
        ],
        "quick_answer": "Usa <strong>to</strong> para destino, receptor y finalidad con verbo (<em>I came to learn</em>); <strong>for</strong> para beneficiario, duración y finalidad con sustantivo (<em>a gift for you</em>, <em>for two hours</em>); <strong>by</strong> para autor, medio y fecha límite (<em>by Friday</em>); <strong>from</strong> para origen; y <strong>with</strong> para compañía o herramienta.",
        "faq": [
            ("¿Cuál es la diferencia entre to y for?", "<em>To</em> marca destino, receptor y finalidad con verbo: <em>I came here to learn</em>. <em>For</em> marca beneficiario, duración y finalidad con sustantivo: <em>This is for you</em>, <em>for two weeks</em>, <em>I came for the job</em>."),
            ("¿Se dice “for + verbo” para expresar finalidad?", "No. Para decir para qué hace algo una persona se usa <em>to</em> + infinitivo: <em>I'm saving money to buy a car</em>. <em>For</em> + <em>-ing</em> solo se usa para la función de un objeto: <em>a machine for making coffee</em>."),
            ("¿Cuándo se usa by y cuándo with?", "<em>By</em> indica quién hace la acción, sobre todo en pasiva: <em>painted by Picasso</em>. <em>With</em> indica la herramienta que alguien usa: <em>painted with a small brush</em>."),
            ("¿Cuál es la diferencia entre until y by?", "<em>Until</em> se usa para algo que dura hasta un momento: <em>I'll wait until six</em>. <em>By</em> se usa para una fecha límite, algo que debe estar hecho como muy tarde entonces: <em>Send it by six</em>."),
            ("¿Se dice by car o in car?", "Para el medio de transporte en general se dice <em>by car</em>, sin artículo. Si concretas el coche, cambia la preposición: <em>in my car</em>, <em>in a taxi</em>."),
        ],
        "body": """
                <p>Las preposiciones son pequeñas, pero sostienen buena parte de la frase. El problema es que una misma preposición española puede convertirse en varias opciones inglesas según la función que cumpla: “para” puede ser <em>to</em> o <em>for</em>, “por” puede ser <em>by</em> o <em>for</em>, y “con” suele ser <em>with</em>, pero no siempre.</p>
                <p>Por eso es mejor aprender <strong>to</strong>, <strong>for</strong>, <strong>by</strong>, <strong>from</strong> y <strong>with</strong> con situaciones típicas. Empieza por la tabla y luego baja a las confusiones que más nos cuestan a los hispanohablantes.</p>

                <h2 id="resumen">Tabla resumen: usos de to, for, by, from y with</h2>
                <table class="data-table">
                <thead><tr><th>Preposición</th><th>Uso</th><th>Ejemplo</th></tr></thead>
                <tbody>
                <tr><td><strong>to</strong></td><td>destino, receptor</td><td>I'm going to Dublin. / Give it to me.</td></tr>
                <tr><td><strong>to</strong></td><td>finalidad con verbo</td><td>I came to learn. (Vine para aprender.)</td></tr>
                <tr><td><strong>for</strong></td><td>beneficiario, duración</td><td>This is for you. / for two hours</td></tr>
                <tr><td><strong>for</strong></td><td>finalidad con sustantivo; función de un objeto</td><td>I went out for a coffee. / a knife for cutting bread</td></tr>
                <tr><td><strong>by</strong></td><td>autor, medio, fecha límite, cercanía</td><td>written by Shakespeare / by bus / by Friday / by the river</td></tr>
                <tr><td><strong>from</strong></td><td>origen, punto de partida</td><td>I'm from Spain. / from Monday to Friday</td></tr>
                <tr><td><strong>with</strong></td><td>compañía, herramienta, característica</td><td>with my friends / with a knife / the girl with red hair</td></tr>
                </tbody>
                </table>

                <h2 id="to">To: dirección, receptor, límite y finalidad</h2>
                <p><em>To</em> suele apuntar hacia un destino, un receptor o el final de un rango. Y delante de un verbo expresa para qué haces algo.</p>
                <div class="example-grid">
                <div class="mini-card"><strong>Go to the store</strong><span>Dirección o destino físico.</span></div>
                <div class="mini-card"><strong>Give it to me</strong><span>El receptor de algo.</span></div>
                <div class="mini-card"><strong>From Monday to Friday</strong><span>El final de un rango de tiempo.</span></div>
                <div class="mini-card"><strong>I came to learn</strong><span>Finalidad: para qué hace algo una persona.</span></div>
                </div>
                <p>Escucha <a href="/audio/i-want-to-go-to-london.html">I want to go to London</a>: tiene dos <em>to</em> con funciones distintas. El primero acompaña al verbo (<em>want to go</em>) y el segundo marca el destino (<em>to London</em>). En una frase normal, <em>to</em> se reduce a <span class="ipa">/tə/</span> (igual en EE. UU. y Reino Unido), no <span class="ipa">/tuː/</span>.</p>
                <ul>
                <li><strong>Home, here y there no llevan to:</strong> <em>go home</em>, <em>come here</em>, <em>go there</em>. Lo oyes en <a href="/audio/tell-them-to-come-back-home.html">Tell them to come back home</a>: hay un <em>to</em> antes del verbo, pero ninguno antes de <em>home</em>.</li>
                <li><strong>Explain, say y describe necesitan to delante de la persona:</strong> <em>Can you explain it to me?</em>, no <em>explain me</em>. <em>Tell</em>, en cambio, va directo: <em>Tell me</em>.</li>
                <li><strong>Give, send y show admiten dos órdenes:</strong> <a href="/audio/give-me-that.html">Give me that</a> o <em>Give that to me</em>.</li>
                </ul>

                <h2 id="for">For: beneficiario, duración y propósito</h2>
                <p><em>For</em> aparece cuando algo es para alguien, durante un periodo o con un propósito expresado con un sustantivo.</p>
                <div class="example-grid">
                <div class="mini-card"><strong>I bought this for my son</strong><span>Beneficiario.</span></div>
                <div class="mini-card"><strong>For five years</strong><span>Duración en el tiempo: <em>I've lived here for five years</em>.</span></div>
                <div class="mini-card"><strong>For looking at the stars</strong><span>Propósito de un objeto o herramienta.</span></div>
                <div class="mini-card"><strong>I paid 20 euros for it</strong><span>Precio o intercambio.</span></div>
                </div>
                <p><em>For</em> también traduce muchos “por”: <em>Thanks for coming</em> (detrás de <em>thanks</em> y <em>sorry</em> va <em>for</em> + <em>-ing</em>), <em>I did it for you</em>, <em>famous for its beaches</em>.</p>

                <h2 id="to-o-for">¿To o for? La diferencia cuando en español dices “para”</h2>
                <p>Es la confusión número uno. La pista está en lo que viene detrás:</p>
                <ul>
                <li><strong>Para + verbo (intención de una persona):</strong> <em>to</em> + infinitivo. <em>I came here to learn English</em>. No <em>for learn</em>, ni <em>for to learn</em>, ni <em>for learning</em>.</li>
                <li><strong>Para + sustantivo o persona:</strong> <em>for</em>. <em>I came here for the job</em>, <em>This is for you</em>.</li>
                <li><strong>Para qué sirve un objeto:</strong> <em>for</em> + <em>-ing</em>, o <em>to</em> + infinitivo. <em>This app is for learning vocabulary</em> / <em>I use this app to learn vocabulary</em>.</li>
                <li><strong>Para alguien + verbo:</strong> <em>for</em> + persona + <em>to</em>. <em>It's hard for me to understand him</em>.</li>
                </ul>
                <table class="data-table">
                <thead><tr><th>En español</th><th>Correcto</th><th>Incorrecto</th></tr></thead>
                <tbody>
                <tr><td>Vine para aprender inglés</td><td>I came to learn English</td><td>I came for learn English</td></tr>
                <tr><td>Llamé para preguntar</td><td>I called to ask</td><td>I called for asking</td></tr>
                <tr><td>Salí a por pan</td><td>I went out for some bread</td><td>I went out for buy bread</td></tr>
                <tr><td>¿Para qué es esto?</td><td>What's this for?</td><td>For what is this?</td></tr>
                </tbody>
                </table>
                <div class="lesson-box"><strong>Atajo:</strong> si después de “para” viene un verbo y hablas de la intención de alguien, prueba primero con <em>to</em>. Si viene un sustantivo, con <em>for</em>.</div>

                <h2 id="by">By: autor, medio, cercanía y fecha límite</h2>
                <p><em>By</em> tiene varios usos frecuentes. La clave es no reducirlo solo a “por”.</p>
                <ul>
                <li><strong>By bus:</strong> método de transporte.</li>
                <li><strong>Written by him:</strong> autor o sujeto en una pasiva.</li>
                <li><strong>By the river:</strong> cerca o pegado a un lugar.</li>
                <li><strong>By Monday:</strong> antes de que termine el lunes, no necesariamente antes del lunes.</li>
                <li><strong>By + -ing:</strong> cómo consigues algo. <em>You can improve your listening by watching series</em> (viendo series).</li>
                <li><strong>By email, by card:</strong> medio de comunicación o de pago. Ojo: en efectivo es <em>in cash</em>.</li>
                </ul>
                <p>Con transporte, <em>by</em> va sin artículo ni posesivo. En cuanto concretas el vehículo, cambias de preposición: <em>by car</em> pero <em>in my car</em>; <em>by train</em> pero <em>on the 8:15 train</em>. A pie es <em>on foot</em>. Tienes todos los transportes en <a href="/articulos/preposiciones-in-on-at.html">in, on y at</a>.</p>
                <p>Expresiones fijas que conviene saber: <em>by mistake</em> (por error), <em>by chance</em> (por casualidad), <em>by heart</em> (de memoria), <em>by hand</em> (a mano), <em>step by step</em> (paso a paso), <em>by the way</em> (por cierto).</p>

                <h2 id="by-with">¿By o with? Quién lo hace frente a con qué se hace</h2>
                <p>En español decimos “por” para el autor y “con” para la herramienta, así que la lógica es la misma. El lío llega en las pasivas, donde pueden aparecer las dos cosas:</p>
                <table class="data-table">
                <thead><tr><th>By: quién (o qué) hace la acción</th><th>With: el instrumento que alguien usa</th></tr></thead>
                <tbody>
                <tr><td>The window was broken by the kids.</td><td>The window was broken with a stone.</td></tr>
                <tr><td>This letter was written by my grandmother.</td><td>It was written with a fountain pen.</td></tr>
                <tr><td>He was hit by a car.</td><td>He was hit with a stick.</td></tr>
                </tbody>
                </table>
                <p>Pregúntate: ¿es el agente o la herramienta? <em>She cut the cake with a knife</em> (herramienta); <em>The cake was made by my aunt</em> (agente). La excepción fija es <em>made by hand</em>, donde la mano funciona como método.</p>

                <h2 id="until-by">¿Until o by? Plazos y fechas límite</h2>
                <p>“Hasta el viernes” puede ser dos cosas muy distintas en inglés:</p>
                <ul>
                <li><strong>Until (o till):</strong> una situación que dura hasta ese momento. <em>I'll be in the office until 6</em>. <em>The shop is closed until Monday</em>.</li>
                <li><strong>By:</strong> algo que tiene que estar hecho, como muy tarde, en ese momento. <em>Please send it by Friday</em>.</li>
                </ul>
                <p>Prueba: si la acción es continua (esperar, quedarse, estar abierto), <em>until</em>. Si es puntual y hay que completarla (enviar, terminar, pagar), <em>by</em>. <em>Finish it until Friday</em> es un error muy común; lo correcto es <em>Finish it by Friday</em>. En negativa, <em>until</em> significa “no antes de”: <em>I won't know until Monday</em>.</p>
                <p>Para un rango, <em>from... to</em> o <em>from... until</em>: <em>I work from 9 to 5</em>. En EE. UU. también es muy común <em>Monday through Friday</em> (de lunes a viernes, ambos incluidos).</p>

                <h2 id="from-with">From y with</h2>
                <p><em>From</em> marca origen, punto de partida o causa. <em>With</em> marca compañía, herramienta o modo.</p>
                <div class="lesson-box">
                <p><strong>She is from Mexico.</strong> Origen.</p>
                <p><strong>We will walk from the station to the hotel.</strong> Punto de partida y llegada.</p>
                <p><strong>I attended the meeting with my manager.</strong> Compañía.</p>
                <p><strong>I ate my salad with a fork.</strong> Herramienta.</p>
                </div>
                <p>Practica el origen con <a href="/audio/i-am-from-spain-and-i-am-33.html">I am from Spain and I am 33</a>. <em>With</em> también describe rasgos (<em>the man with glasses</em>, el hombre de las gafas) y modo (<em>with a smile</em>). Pero “con” no siempre es <em>with</em>:</p>
                <div class="example-grid">
                <div class="mini-card"><strong>married to</strong><span>Casado con: <em>She's married to an Irishman</em>.</span></div>
                <div class="mini-card"><strong>dream about</strong><span>Soñar con: <em>I often dream about flying</em>.</span></div>
                <div class="mini-card"><strong>count on</strong><span>Contar con: <em>You can count on me</em>.</span></div>
                <div class="mini-card"><strong>agree with</strong><span>Estar de acuerdo con, sin <em>be</em>: <em>I agree with you</em>, no <em>I'm agree</em>.</span></div>
                </div>

                <h2 id="ejercicio">Ejercicio: elige la preposición</h2>
                <p>Completa con <em>to</em>, <em>for</em>, <em>by</em>, <em>from</em>, <em>with</em>, <em>until</em> o <em>in</em>. Pulsa cada frase para ver la solución.</p>
                <details class="exercise"><summary>1. I came to London ___ improve my English.</summary><p><strong>to</strong>. Finalidad con verbo: <em>to improve</em>. Nunca <em>for improve</em>.</p></details>
                <details class="exercise"><summary>2. This present is ___ you.</summary><p><strong>for</strong>. Beneficiario.</p></details>
                <details class="exercise"><summary>3. We've lived here ___ ten years.</summary><p><strong>for</strong>. Duración. (Con un punto de inicio sería <em>since</em>: <em>since 2016</em>.)</p></details>
                <details class="exercise"><summary>4. <em>Hamlet</em> was written ___ Shakespeare.</summary><p><strong>by</strong>. Autor en una pasiva.</p></details>
                <details class="exercise"><summary>5. She cut the bread ___ a knife.</summary><p><strong>with</strong>. Herramienta.</p></details>
                <details class="exercise"><summary>6. I usually go to work ___ bus, but today I went ___ my sister's car.</summary><p><strong>by</strong> e <strong>in</strong>. <em>By</em> + transporte sin artículo; con posesivo, <em>in my sister's car</em>.</p></details>
                <details class="exercise"><summary>7. Please send me the report ___ Friday at the latest.</summary><p><strong>by</strong>. Fecha límite para algo que hay que completar.</p></details>
                <details class="exercise"><summary>8. I'll wait here ___ you come back.</summary><p><strong>until</strong>. Acción continua (esperar) hasta ese momento.</p></details>
                <details class="exercise"><summary>9. Can you explain this ___ me?</summary><p><strong>to</strong>. <em>Explain something to someone</em>. <em>Explain me</em> es incorrecto.</p></details>
                <details class="exercise"><summary>10. My cousin is married ___ a guy ___ Dublin.</summary><p><strong>to</strong> y <strong>from</strong>. “Casado con” es <em>married to</em>; el origen, <em>from</em>.</p></details>

                <p>Cuando practiques en voz alta, recuerda que en una frase normal estas preposiciones casi nunca suenan como en el diccionario: <em>for</em> se reduce a <span class="ipa">/fə/</span> en Reino Unido y <span class="ipa">/fɚ/</span> en EE. UU., y <em>from</em> a <span class="ipa">/frəm/</span> en los dos. Si te cuesta oírlas, lee <a href="/articulos/ligar-palabras-ingles.html">cómo se ligan las palabras en inglés</a> y vuelve a escuchar los audios de arriba fijándote solo en ellas.</p>
        """,
    },
    {
        "slug": "actual-vs-actually",
        "category": "Falsos amigos",
        "title": "Actual vs actually: qué significa actually y por qué no es actualmente",
        "seo_title": "Actually significado en español: actual vs actually",
        "description": "Actually no significa actualmente, sino en realidad o de hecho. Diferencias con actual, currently y nowadays, otros falsos amigos y ejercicio resuelto.",
        "lede": "Actual y actually parecen transparentes desde el español, pero esa confianza es justo el problema. Son dos palabras útiles si las separas de actualmente.",
        "reading": "7 minutos",
        "published": "2026-06-28",
        "toc": [
            ("actual", "Actual"),
            ("actually", "Actually"),
            ("currently", "Currently y nowadays"),
            ("falsos-amigos", "Otros falsos amigos"),
            ("practica", "Ejercicio"),
        ],
        "related": [
            "sure-en-ingles",
            "i-mean-en-ingles",
            "fun-vs-funny",
            "make-vs-do",
        ],
        "quick_answer": "<strong>Actually</strong> significa <em>en realidad</em> o <em>de hecho</em>, no <em>actualmente</em>. Se usa para corregir, aclarar o contradecir con suavidad: <em>He’s actually Irish</em> (en realidad es irlandés). <em>Actual</em> significa <em>real</em> (<em>the actual cost</em>, el coste real). Para decir <em>actualmente</em>, usa <em>currently</em>, <em>at the moment</em> o <em>nowadays</em>.",
        "faq": [
            ("¿Actually significa actualmente?", "No. <em>Actually</em> significa “en realidad” o “de hecho”: <em>It’s actually quite easy</em> (en realidad es bastante fácil). Para “actualmente”, se usa <em>currently</em>, <em>at the moment</em> o <em>nowadays</em>."),
            ("¿Cómo se dice actualmente en inglés?", "Depende del matiz: <em>currently</em> para una situación presente (<em>I’m currently living in Dublin</em>), <em>at the moment</em> para “ahora mismo” y <em>nowadays</em> o <em>these days</em> para “hoy en día”, en contraste con el pasado."),
            ("¿Qué significa in actual fact?", "Significa “en realidad” o “de hecho”, igual que <em>actually</em>, pero con un tono algo más formal. Se usa sobre todo en inglés británico: <em>In actual fact, the plan was never approved</em>."),
            ("¿Cómo se pronuncia actually?", "Se pronuncia <span class=\"ipa\">/ˈæk.tʃu.ə.li/</span> en británico y en americano, y en el habla rápida se reduce a algo como <span class=\"ipa\">/ˈæk.tʃə.li/</span>. La T suena como la “ch” española, no como una T."),
            ("¿Qué significa eventually?", "<em>Eventually</em> significa “al final” o “finalmente”, tras un tiempo o un proceso: <em>We eventually found the hotel</em>. No equivale a “eventualmente”; para eso, según el caso, se usa <em>possibly</em> u <em>occasionally</em>."),
        ],
        "body": """
                <p>Un falso amigo no es peligroso porque sea difícil, sino porque parece fácil. <strong>Actual</strong> y <strong>actually</strong> se parecen demasiado a <em>actual</em> y <em>actualmente</em>, pero no significan eso: <em>actually</em> significa “en realidad” o “de hecho”, y <em>actual</em> significa “real”.</p>
                <p>Si alguna vez has dicho <em>Actually I live in Madrid</em> queriendo decir “actualmente vivo en Madrid”, no eres el único. La frase se entiende, pero lo que transmite es “en realidad vivo en Madrid”, como si corrigieras algo que alguien ha dicho.</p>
                <h2 id="actual">Actual significa real</h2>
                <p><em>Actual</em> es un adjetivo. Significa real, verdadero o definitivo, especialmente cuando lo comparas con una estimación, expectativa o apariencia.</p>
                <div class="example-grid">
                <div class="mini-card"><strong>The actual cost was higher</strong><span>El coste real fue más alto.</span></div>
                <div class="mini-card"><strong>The actual problem is different</strong><span>El problema real es diferente.</span></div>
                <div class="mini-card"><strong>This is the actual car from the film</strong><span>Este es el coche auténtico de la película.</span></div>
                <div class="mini-card"><strong>In actual fact</strong><span>En realidad. Algo formal y más británico.</span></div>
                </div>
                <p>Para el “actual” español usa <strong>current</strong> o <strong>present</strong>: <em>the current situation</em> (la situación actual), <em>the current president</em> (el presidente actual).</p>
                <p>Se pronuncia <span class="ipa">/ˈæk.tʃu.əl/</span> en británico y en americano. La T se une a la U y suena <span class="ipa">/tʃ/</span>, como nuestra “ch”. Es el mismo fenómeno que hace que la D de <em>gradual</em> o <em>individual</em> suene <span class="ipa">/dʒ/</span>; puedes practicarlo con el audio de <a href="/audio/education-individual-gradual-schedule-procedure-residual.html">education, individual, gradual, schedule, procedure y residual</a>.</p>
                <h2 id="actually">¿Qué significa actually? Usos con ejemplos</h2>
                <p><em>Actually</em> es un adverbio. Sirve para corregir, aclarar o introducir una idea que contrasta con lo que alguien esperaba.</p>
                <ul>
                <li><strong>Corrección:</strong> <em>He looks young, but he’s actually in his sixties.</em> → Parece joven, pero en realidad tiene sesenta y tantos.</li>
                <li><strong>Aclaración:</strong> <em>I thought it would be expensive, but it’s actually quite cheap.</em> → Pensaba que sería caro, pero la verdad es que es bastante barato.</li>
                <li><strong>Sorpresa:</strong> <em>Actually, I think I know the answer.</em> → Pues mira, creo que sé la respuesta.</li>
                <li><strong>Cambiar de opinión:</strong> <em>Actually, can I have tea instead?</em> → Bueno, mejor, ¿me pones un té?</li>
                <li><strong>Discrepar con suavidad:</strong> <em>Actually, the meeting is on Tuesday.</em> → Perdona, pero la reunión es el martes.</li>
                <li><strong>Énfasis:</strong> <em>Did you actually say that to him?</em> → ¿De verdad le dijiste eso?</li>
                </ul>
                <p>En inglés británico es muy típico al final de la frase, para matizar: <em>It’s quite good, actually</em> (pues está bastante bien, la verdad). En conversación también funciona a veces casi como muletilla, igual que <a href="/articulos/i-mean-en-ingles.html">I mean</a>.</p>
                <p>Un aviso: un <em>Actually...</em> seco para corregir a alguien puede sonar a sabelotodo, sobre todo si lo repites mucho. Para suavizarlo, es habitual añadir algo delante: <em>Sorry, I think it’s actually on Tuesday</em> (perdona, creo que en realidad es el martes).</p>
                <p>Se pronuncia <span class="ipa">/ˈæk.tʃu.ə.li/</span> en británico y en americano, aunque en el habla rápida se reduce a algo como <span class="ipa">/ˈæk.tʃə.li/</span>. Nada de “ak-tu-a-li”.</p>
                <h2 id="currently">Actually vs currently vs nowadays vs at the moment</h2>
                <p>Si quieres decir <em>actualmente</em>, la opción más directa es <strong>currently</strong>. Por ejemplo: <em>I currently live in Charlotte</em>. Pero hay más opciones según el matiz:</p>
                <table class="data-table">
                <thead><tr><th>Palabra</th><th>Significa</th><th>Ejemplo</th></tr></thead>
                <tbody>
                <tr><td>actually</td><td>en realidad, de hecho</td><td>Actually, I’m from Seville. (En realidad soy de Sevilla.)</td></tr>
                <tr><td>currently</td><td>actualmente (situación presente, a menudo temporal)</td><td>She’s currently working in Dublin. (Actualmente trabaja en Dublín.)</td></tr>
                <tr><td>at the moment</td><td>en este momento</td><td>He’s not here at the moment. (Ahora mismo no está.)</td></tr>
                <tr><td>nowadays / these days</td><td>hoy en día, en contraste con el pasado</td><td>Nowadays most people pay by card. (Hoy en día casi todo el mundo paga con tarjeta.)</td></tr>
                <tr><td>right now</td><td>ahora mismo</td><td>I can’t talk right now. (Ahora mismo no puedo hablar.)</td></tr>
                </tbody>
                </table>
                <div class="lesson-box"><strong>No traduzcas en automático:</strong> <em>actually</em> no significa <em>actualmente</em>. Casi siempre significa <em>en realidad</em> o <em>de hecho</em>.</div>
                <h2 id="falsos-amigos">Otros falsos amigos de la misma familia</h2>
                <p><em>Actually</em> no viaja solo. Estos primos cercanos confunden a los españoles por la misma razón: parecen transparentes.</p>
                <table class="data-table">
                <thead><tr><th>Inglés</th><th>Significa</th><th>No significa</th><th>Para eso, di</th></tr></thead>
                <tbody>
                <tr><td>eventually</td><td>al final, finalmente</td><td>eventualmente</td><td>possibly, occasionally</td></tr>
                <tr><td>actual</td><td>real</td><td>actual</td><td>current</td></tr>
                <tr><td>assist</td><td>ayudar (formal)</td><td>asistir a algo</td><td>attend</td></tr>
                <tr><td>attend</td><td>asistir a (clase, reunión)</td><td>atender a alguien</td><td>serve, help, look after</td></tr>
                <tr><td>realize</td><td>darse cuenta</td><td>realizar</td><td>carry out, do</td></tr>
                <tr><td>sensible</td><td>sensato</td><td>sensible</td><td>sensitive</td></tr>
                <tr><td>embarrassed</td><td>avergonzado</td><td>embarazada</td><td>pregnant</td></tr>
                <tr><td>carpet</td><td>moqueta, alfombra</td><td>carpeta</td><td>folder</td></tr>
                <tr><td>library</td><td>biblioteca</td><td>librería</td><td>bookshop (UK), bookstore (US)</td></tr>
                <tr><td>constipated</td><td>estreñido</td><td>constipado</td><td>have a cold</td></tr>
                </tbody>
                </table>
                <p>Dos matices para no pasarte de frenada: <em>attend to</em> sí puede significar “ocuparse de” o “atender”, en un registro algo formal (<em>attend to a customer</em>), y <em>realize</em> también aparece en <em>realize a dream</em> (hacer realidad un sueño). Pero en el día a día, <em>I realized</em> es “me di cuenta”. Y <em>surely</em> tampoco es exactamente “seguramente”: lo explicamos en <a href="/articulos/sure-en-ingles.html">sure en inglés</a>. Si te gustan estas trampas, mira también <a href="/articulos/fun-vs-funny.html">fun vs funny</a>, otra pareja que confunde mucho.</p>
                <h2 id="practica">Ejercicio: ¿actual, actually, currently o nowadays?</h2>
                <p>Antes de empezar, hazte esta pregunta cada vez que quieras usar una de estas palabras: ¿estoy hablando de algo real frente a algo supuesto, o estoy corrigiendo una expectativa? Si hablas de lo real, usa <em>actual</em>. Si corriges o aclaras, usa <em>actually</em>. Si hablas del presente, usa <em>currently</em>.</p>
                <details class="exercise"><summary>I thought he was English, but he’s ______ Irish.</summary><p><strong>actually</strong>. Corriges una suposición: en realidad es irlandés.</p></details>
                <details class="exercise"><summary>The ______ price was much lower than the estimate.</summary><p><strong>actual</strong>. El precio real frente al estimado.</p></details>
                <details class="exercise"><summary>She’s ______ working on a new project.</summary><p><strong>currently</strong>. Situación presente. También valdría <em>She’s working on a new project at the moment</em>.</p></details>
                <details class="exercise"><summary>______, most people book their holidays online.</summary><p><strong>Nowadays</strong> (o <em>These days</em>). Contraste con el pasado.</p></details>
                <details class="exercise"><summary>Traduce: Actualmente estoy buscando trabajo.</summary><p><em>I’m currently looking for a job</em> (o <em>At the moment I’m looking for a job</em>). Con <em>actually</em> dirías “en realidad estoy buscando trabajo”.</p></details>
                <details class="exercise"><summary>Traduce: Al final encontramos el hotel.</summary><p><em>We eventually found the hotel.</em> <em>Eventually</em> es “al final”, no “eventualmente”.</p></details>
                <details class="exercise"><summary>Traduce: Me da mucha vergüenza.</summary><p><em>I’m so embarrassed.</em> Nada de <em>pregnant</em>.</p></details>
                <details class="exercise"><summary>Traduce: ¿Asististe a la reunión?</summary><p><em>Did you attend the meeting?</em> (o <em>Did you go to the meeting?</em>). <em>Assist</em> es ayudar.</p></details>
                <details class="exercise"><summary>Traduce: Me di cuenta de que era tarde.</summary><p><em>I realized it was late.</em> En británico también se escribe <em>realised</em>.</p></details>
                <details class="exercise"><summary>Traduce: Es una decisión muy sensata.</summary><p><em>It’s a very sensible decision.</em> Si dijeras <em>sensitive</em>, hablarías de algo delicado o de alguien sensible.</p></details>
                <details class="exercise"><summary>Traduce: Voy a la biblioteca a devolver un libro.</summary><p><em>I’m going to the library to return a book.</em> Una librería sería <em>a bookshop</em> o <em>a bookstore</em>.</p></details>
                <p>Apunta los falsos amigos que más te cuesten y repasa una frase de cada uno antes de hablar o escribir en inglés. Con un poco de uso, <em>actually</em> dejará de sonarte a “actualmente”.</p>
        """,
    },
    {
        "slug": "ligar-palabras-ingles",
        "category": "Pronunciación",
        "title": "Gonna, wanna, gotta y más: cómo ligar palabras en inglés (connected speech)",
        "seo_title": "Gonna, wanna, gotta: significado y cómo ligar en inglés",
        "description": "Qué significan gonna, wanna, gotta, lemme, kinda o dunno, cuándo se pueden escribir y cómo ligar palabras en inglés hablado. Con tabla, audios y ejercicio.",
        "lede": "El inglés real no suena como palabras separadas en fila. Si no practicas las uniones, entenderás menos y sonarás más rígido.",
        "reading": "8 minutos",
        "published": "2026-06-28",
        "toc": [
            ("por-que", "Qué es"),
            ("formas", "Tabla de reducciones"),
            ("mecanismos", "Cómo se ligan"),
            ("escuchar", "Listening"),
            ("practicar", "Práctica y ejercicio"),
        ],
        "related": [
            "pronunciacion-ingles-para-espanoles",
            "how-are-you-respuestas-ingles",
            "como-se-pronuncia-the",
            "guia-pronunciacion-ingles-espanoles",
        ],
        "quick_answer": "<strong>Gonna</strong> significa <em>going to</em> (ir a), <strong>wanna</strong> es <em>want to</em> (querer) y <strong>gotta</strong> es <em>(have) got to</em> (tener que). Son formas reducidas del inglés hablado, lo que se llama <em>connected speech</em>: al hablar rápido, las palabras se ligan y se debilitan. Son normales en conversación, pero en un texto formal se escribe la forma completa.",
        "faq": [
            ("¿Qué significa gonna en inglés?", "<em>Gonna</em> es la forma hablada de <em>going to</em> cuando va seguido de un verbo y significa “ir a” hacer algo: <em>I'm gonna call her</em> (voy a llamarla). No se usa cuando <em>going to</em> indica un lugar: <em>I'm going to Madrid</em> no se reduce."),
            ("¿Qué significa gotta?", "<em>Gotta</em> es la forma reducida de <em>(have) got to</em> y significa “tener que”: <em>I gotta go</em> (me tengo que ir). Es informal y solo se usa en presente; para el pasado se dice <em>I had to go</em>."),
            ("¿Se pueden escribir gonna, wanna y gotta?", "Sí, pero solo en contextos informales: mensajes, redes sociales, letras de canciones o diálogos. En un email de trabajo, un examen oficial o un CV escribe la forma completa: <em>going to</em>, <em>want to</em>, <em>have to</em> o <em>have got to</em>."),
            ("¿Qué es el connected speech en inglés?", "Es la forma en que las palabras se unen, se debilitan o pierden sonidos al hablar con naturalidad: <em>pick it up</em> suena como una sola palabra, <em>to</em> se reduce a <span class=\"ipa\">/tə/</span> y <em>did you</em> se convierte en <em>didja</em>. Reconocerlo es clave para entender a los nativos."),
            ("¿Está mal decir gonna o wanna?", "No. Son formas normales del inglés hablado que usan hablantes nativos de todos los niveles. Lo que sí conviene es usarlas solo al hablar o en textos informales, y no forzarlas si todavía te salen artificiales."),
        ],
        "body": """
                <p>Para sonar más natural en inglés no basta con pronunciar cada palabra correctamente. También hay que aprender a ligar palabras como lo hace la gente cuando habla rápido: <em>going to</em> se convierte en <em>gonna</em>, <em>want to</em> en <em>wanna</em> y <em>pick it up</em> suena casi como una sola palabra. En español hacemos lo mismo, pero cuando escuchamos inglés tendemos a esperar palabras separadas.</p>
                <p>Practicar estas uniones mejora dos cosas a la vez: te entienden mejor y tú entiendes mejor a los nativos.</p>
                <h2 id="por-que">¿Qué es el connected speech y por qué cambia tanto?</h2>
                <p>Al conjunto de uniones, reducciones y sonidos que desaparecen al hablar se le llama <strong>connected speech</strong> (habla encadenada). Cuando dices una frase palabra por palabra, puedes ser correcto y aun así sonar poco natural. En conversación, muchas combinaciones se reducen porque la boca busca el camino más eficiente.</p>
                <p>No es algo exótico: en español decimos <em>pa’ casa</em> en vez de <em>para casa</em>, <em>vamo’ a ver</em>, y unimos <em>los otros</em> como si fuera <em>lo-so-tros</em>. El inglés lo hace todavía más, sobre todo con las palabras pequeñas.</p>
                <div class="lesson-box"><strong>Importante:</strong> muchas formas reducidas son normales al hablar, pero no siempre conviene escribirlas. Puedes decir algo parecido a <em>wanna</em>, pero en un email formal escribe <em>want to</em>.</div>
                <h2 id="formas">Tabla de reducciones: gonna, wanna, gotta y compañía</h2>
                <table class="data-table">
                <thead><tr><th>Forma hablada</th><th>Forma completa</th><th>Significado</th><th>Ejemplo</th><th>¿Se puede escribir?</th></tr></thead>
                <tbody>
                <tr><td><strong>gonna</strong></td><td>going to (+ verbo)</td><td>ir a (futuro, planes)</td><td><em>I'm gonna call her.</em></td><td>En chats, redes y diálogos informales. No en textos formales.</td></tr>
                <tr><td><strong>wanna</strong></td><td>want to / want a</td><td>querer (hacer algo)</td><td><em>I wanna go to London.</em></td><td>Igual que <em>gonna</em>: solo informal.</td></tr>
                <tr><td><strong>gotta</strong></td><td>(have) got to / got a</td><td>tener que</td><td><em>I gotta go.</em></td><td>Informal. En un texto neutro: <em>I've got to go</em> o <em>I have to go</em>.</td></tr>
                <tr><td><strong>hafta / hasta</strong></td><td>have to / has to</td><td>tener que</td><td><em>She hasta work.</em></td><td>Casi nunca se escribe: se oye.</td></tr>
                <tr><td><strong>lemme</strong></td><td>let me</td><td>déjame</td><td><em>Lemme see.</em></td><td>Solo en mensajes muy informales.</td></tr>
                <tr><td><strong>gimme</strong></td><td>give me</td><td>dame</td><td><em>Gimme that.</em></td><td>Solo muy informal.</td></tr>
                <tr><td><strong>kinda / sorta</strong></td><td>kind of / sort of</td><td>un poco, más o menos; tipo de</td><td><em>I'm kinda tired.</em></td><td>Informal.</td></tr>
                <tr><td><strong>outta</strong></td><td>out of</td><td>fuera de</td><td><em>Get outta here!</em></td><td>Informal, sobre todo en frases hechas.</td></tr>
                <tr><td><strong>shoulda / coulda / woulda</strong></td><td>should have / could have / would have</td><td>debería haber / podría haber / habría</td><td><em>You shoulda told me.</em></td><td>Informal. En texto neutro: <em>should've</em>. Nunca <em>should of</em>.</td></tr>
                <tr><td><strong>dunno</strong></td><td>(I) don't know</td><td>no sé</td><td><em>Dunno, maybe.</em></td><td>En chats.</td></tr>
                <tr><td><strong>didja</strong></td><td>did you</td><td>pregunta en pasado: ¿viste...?, ¿hiciste...?</td><td><em>Didja see that?</em></td><td>Casi nunca se escribe: se oye.</td></tr>
                </tbody>
                </table>
                <p>Tres matices que evitan errores muy típicos:</p>
                <ul>
                <li><strong><em>Gonna</em> solo sustituye a <em>going to</em> cuando va seguido de un verbo.</strong> <em>I'm gonna eat</em> es correcto; <em>I'm going to Madrid</em> nunca se convierte en <em>I'm gonna Madrid</em>.</li>
                <li><strong><em>Wanna</em> no vale para <em>wants to</em>.</strong> Se dice <em>I wanna go</em>, pero <em>he wants to go</em>, no <em>he wanna go</em>.</li>
                <li><strong><em>Has to</em> suena casi como el “hasta” español</strong>, <span class="ipa">/ˈhæstə/</span>, y <em>have to</em> se dice <span class="ipa">/ˈhæftə/</span>, con F. La V y la S se ensordecen por la T que viene detrás.</li>
                </ul>
                <p>Y para escucharlas en frases reales:</p>
                <div class="example-grid">
                <div class="mini-card"><strong>going to → gonna</strong><span><a href="/audio/going-to.html">Escuchar going to</a></span></div>
                <div class="mini-card"><strong>want to → wanna</strong><span><a href="/audio/i-want-to-go-to-london.html">Escuchar I want to go to London</a></span></div>
                <div class="mini-card"><strong>have got to → gotta</strong><span><a href="/audio/i-gotta-go.html">Escuchar I gotta go</a></span></div>
                <div class="mini-card"><strong>let me → lemme</strong><span><a href="/audio/let-me-see.html">Escuchar Let me see</a></span></div>
                <div class="mini-card"><strong>give me → gimme</strong><span><a href="/audio/give-me-that.html">Escuchar Give me that</a></span></div>
                <div class="mini-card"><strong>could have → could've</strong><span><a href="/audio/could-have-should-have-would-have.html">Escuchar could have, should have, would have</a></span></div>
                <div class="mini-card"><strong>out of, kind of, sort of</strong><span><a href="/audio/out-of-kind-of-sort-of.html">Escuchar out of, kind of, sort of</a></span></div>
                <div class="mini-card"><strong>did you → didja</strong><span><a href="/audio/did-you-see-that.html">Escuchar Did you see that?</a></span></div>
                </div>
                <h2 id="mecanismos">¿Cómo se ligan las palabras en inglés? Los 5 mecanismos</h2>
                <p>Las reducciones de la tabla no son caprichos: salen de unos pocos mecanismos que se repiten. Si los reconoces, entenderás también combinaciones que nadie te ha enseñado. Las transcripciones de esta sección valen para británico y americano salvo que se indique otra cosa.</p>
                <h3>1. Consonante final + vocal inicial</h3>
                <p>La consonante del final de una palabra se “pega” a la vocal de la siguiente. <em>Pick it up</em> se oye casi como <em>pi-ki-tup</em>, y <em>take it off</em> como <em>tei-ki-toff</em>. En inglés americano, además, la T entre vocales suele sonar como nuestra r de <em>pero</em>, así que <em>got it</em> se acerca a <em>gá-rit</em>. Practica con <a href="/audio/pick-it-up.html">pick it up</a> y <a href="/audio/take-it-off.html">take it off</a>.</p>
                <h3>2. Vocal + vocal: aparece una W o una Y</h3>
                <p>Cuando una palabra termina en vocal y la siguiente empieza por vocal, el inglés mete un puente suave: <em>go on</em> suena como <em>go-w-on</em>, <em>do it</em> como <em>do-w-it</em> y <em>I am</em> como <em>I-y-am</em>. Practícalo con <a href="/audio/i-am-spanish.html">I am Spanish</a>.</p>
                <h3>3. Formas débiles: las palabras pequeñas se encogen</h3>
                <p>Las palabras gramaticales casi nunca llevan su vocal completa dentro de la frase: <em>to</em> suena <span class="ipa">/tə/</span>, <em>of</em> <span class="ipa">/əv/</span> o incluso <span class="ipa">/ə/</span>, <em>and</em> <span class="ipa">/ən/</span> o <span class="ipa">/n/</span> (<em>fish ’n’ chips</em>), <em>can</em> <span class="ipa">/kən/</span>, <em>for</em> <span class="ipa">/fə/</span> (UK) · <span class="ipa">/fɚ/</span> (US) y <em>them</em> <span class="ipa">/ðəm/</span> o simplemente <em>’em</em> <span class="ipa">/əm/</span>. De ahí salen <em>kinda</em>, <em>outta</em> o <em>shoulda</em>. Practica con <a href="/audio/tell-them-to-come-back-home.html">Tell them to come back home</a>, donde <em>them</em> y <em>to</em> son justo ese tipo de palabras.</p>
                <h3>4. Sonidos que desaparecen</h3>
                <p>Una T o una D entre dos consonantes a menudo se pierde: <em>next week</em> suena como <em>nex week</em>, <em>last night</em> como <em>las night</em>, y <em>I don't know</em> puede quedar en <em>I dunno</em>. No es pereza: es la forma normal de hablar rápido.</p>
                <h3>5. Sonidos que se fusionan</h3>
                <p>Una D seguida de Y se convierte en el sonido de <em>John</em>: <em>did you</em> → <em>didja</em> <span class="ipa">/ˈdɪdʒə/</span>, <em>would you</em> → <em>wouldja</em>. Una T seguida de Y se convierte en el sonido de <em>church</em>: <em>got you</em> → <em>gotcha</em>, <em>don't you</em> → <em>don'tcha</em>. Practica con <a href="/audio/did-you-see-that.html">Did you see that?</a></p>
                <h2 id="escuchar">Esto también mejora tu listening</h2>
                <p>Si solo conoces la forma escrita, <em>I have got to go</em>, puede que no reconozcas <em>I gotta go</em>. No es que hablen mal: es que el inglés oral usa reducciones constantemente, en series, en canciones, en reuniones y en la cola del supermercado.</p>
                <p>Lo mismo ocurre con <em>out of</em>, <em>kind of</em> y <em>sort of</em>, que en conversación pueden sonar como <em>outta</em>, <em>kinda</em> y <em>sorta</em>. Cuanto antes entrenes el oído con estas formas, antes dejarás de perderte media frase cuando alguien habla a velocidad normal. Y no hace falta que tú las uses todas: con reconocerlas ya ganas mucho. Si quieres empezar a usar alguna, las más extendidas al hablar son <em>gonna</em>, <em>wanna</em> y <em>kinda</em>.</p>
                <h2 id="practicar">Cómo practicarlo</h2>
                <ol>
                <li>Di la frase primero despacio, palabra por palabra, y después a velocidad normal, ligando.</li>
                <li>Repite la frase completa, no solo la combinación aislada.</li>
                <li>Grábate y comprueba si sigues separando demasiado las palabras.</li>
                <li>Úsalo en frases que dirías de verdad: <em>I gotta go</em>, <em>lemme see</em>, <em>give me that</em>.</li>
                </ol>
                <p>Ahora ponte a prueba: ¿cómo sonarían estas frases en una conversación relajada?</p>
                <details class="exercise"><summary>1. <em>I'm going to call you later.</em></summary><p><em>I'm gonna call you later.</em> <em>Going to</em> va seguido de un verbo (<em>call</em>), así que se puede reducir.</p></details>
                <details class="exercise"><summary>2. <em>I'm going to the gym.</em></summary><p>No cambia. Aquí <em>going to</em> va seguido de un lugar, no de un verbo, así que no hay <em>gonna</em>.</p></details>
                <details class="exercise"><summary>3. <em>What do you want to do?</em></summary><p><em>What do you wanna do?</em> En habla muy rápida, incluso algo como <em>whaddaya wanna do?</em></p></details>
                <details class="exercise"><summary>4. <em>You should have told me.</em></summary><p><em>You shoulda told me</em> (o <em>should've</em>). Si lo escribes, nunca <em>should of</em>.</p></details>
                <details class="exercise"><summary>5. <em>Did you eat?</em></summary><p><em>Didja eat?</em> La D y la Y se fusionan en el sonido de <em>John</em>.</p></details>
                <details class="exercise"><summary>6. <em>Let me know.</em></summary><p><em>Lemme know.</em> Muy frecuente al final de mensajes y conversaciones.</p></details>
                <p>Sigue con la colección de <a href="/audios.html">audios para ligar palabras</a> y con cómo se reduce una palabra tan frecuente como <a href="/articulos/como-se-pronuncia-the.html">the</a>. Cinco minutos al día repitiendo frases enteras valen más que memorizar la tabla.</p>
        """,
    },
    {
        "slug": "sonido-th-ingles",
        "category": "Pronunciación",
        "title": "El sonido TH en inglés: cómo pronunciar la TH sorda y la sonora sin convertirlas en D, T o S",
        "seo_title": "Sonido TH en inglés: cómo pronunciar la TH sorda y sonora",
        "description": "Cómo pronunciar el sonido TH en inglés: TH sorda /θ/ (think, three) y sonora /ð/ (this, the), posición de la lengua, errores típicos y pares mínimos.",
        "lede": "El TH no es una D, ni una T, ni una S: es la lengua entre los dientes, con o sin vibración. Y si en tu español distingues casa de caza, ya tienes la mitad del trabajo hecho.",
        "reading": "8 minutos",
        "published": "2026-06-28",
        "toc": [
            ("por-que", "Por qué importa"),
            ("dos-sonidos", "TH sorda y sonora"),
            ("espanol", "Ya la tienes en español"),
            ("errores", "Errores típicos"),
            ("pares", "Pares mínimos"),
            ("lista", "The, this, that"),
            ("practica", "Práctica"),
        ],
        "related": [
            "como-se-pronuncia-the",
            "pronunciacion-ingles-para-espanoles",
            "palabras-ough-pronunciacion-ingles",
            "vocales-ingles-cortas-largas",
        ],
        "quick_answer": "El sonido TH en inglés se pronuncia con la punta de la lengua entre los dientes y dejando salir el aire. Hay dos: la <strong>TH sorda /θ/</strong>, sin vibración, de <em>think</em> o <em>three</em> (igual que la c de “cena” en casi toda España), y la <strong>TH sonora /ð/</strong>, con vibración, de <em>this</em>, <em>they</em> o <em>the</em>.",
        "faq": [
            ("¿Cómo se pronuncia la TH en inglés?", "Se pone la punta de la lengua entre los dientes, o justo detrás de los de arriba, y se deja salir el aire por encima. Si solo sale aire, es la TH sorda <span class=\"ipa\">/θ/</span> de <em>think</em>; si además vibran las cuerdas vocales, es la TH sonora <span class=\"ipa\">/ð/</span> de <em>this</em>."),
            ("¿Cuál es la diferencia entre la TH sorda y la TH sonora?", "La posición de la lengua es la misma; cambia la voz. La sorda <span class=\"ipa\">/θ/</span> (<em>think</em>, <em>three</em>, <em>thanks</em>) es solo aire. La sonora <span class=\"ipa\">/ð/</span> (<em>the</em>, <em>this</em>, <em>they</em>, <em>mother</em>) hace vibrar la garganta, como puedes comprobar tocándotela."),
            ("¿La TH inglesa es igual que la Z española?", "La TH sorda <span class=\"ipa\">/θ/</span> sí es prácticamente igual a la z o la c de <em>zapato</em> y <em>cena</em> tal como se pronuncian en la mayor parte de España. La TH sonora <span class=\"ipa\">/ð/</span> no: se parece más a la d suave de <em>nada</em>."),
            ("¿Cómo se pronuncia the en inglés?", "Con TH sonora: normalmente <span class=\"ipa\">/ðə/</span> antes de sonido consonante (<em>the book</em>) y <span class=\"ipa\">/ði/</span> antes de sonido vocal (<em>the apple</em>). No se pronuncia como una d española ni como “de”."),
            ("¿Por qué algunos nativos dicen fink en vez de think?", "Porque en algunos acentos, como muchos de Londres, la TH sorda se pronuncia como F (<em>fink</em>, o <em>free</em> por <em>three</em>). Es un rasgo de acento, no un error, pero para un estudiante es mejor aprender la TH estándar, que se entiende en todas partes."),
        ],
        "body": """
                <p>Para muchos hispanohablantes, el sonido TH en inglés es un pequeño misterio: <em>they</em>, <em>day</em>, <em>think</em> y <em>sink</em> acaban saliendo demasiado parecidas. El problema no suele ser el oído: es que intentamos producir el sonido con una posición de boca española.</p>
                <p>En inglés, el sonido <strong>TH</strong> se hace colocando la punta de la lengua entre los dientes o justo tocándolos. Esa pequeña diferencia física cambia por completo cómo te entiende un nativo. Y hay una sorpresa: si eres de la mayor parte de España, llevas toda la vida haciendo uno de los dos sonidos TH sin saberlo.</p>
                <h2 id="por-que">Por qué importa tanto</h2>
                <p>El TH aparece en palabras muy frecuentes: <em>the</em> (la palabra más común del inglés), <em>this</em>, <em>that</em>, <em>they</em>, <em>think</em>, <em>through</em>, <em>three</em>. Si lo conviertes siempre en D, T, S o Z, muchas frases siguen siendo comprensibles por contexto, pero tu pronunciación pierde claridad justo en las palabras que más repites. Y a veces cambia el significado: <em>three</em> (tres) frente a <em>tree</em> (árbol), o <em>thank</em> (agradecer) frente a <em>tank</em> (tanque).</p>
                <div class="lesson-box"><strong>Idea clave:</strong> no intentes arreglar el TH pensando en letras. Arregla la posición de la lengua. Primero coloca la lengua; luego añade aire y voz.</div>
                <h2 id="dos-sonidos">TH sorda y TH sonora: cómo se pronuncian /θ/ y /ð/</h2>
                <p>Los dos sonidos se hacen exactamente igual con la boca. Lo único que cambia es si vibran las cuerdas vocales:</p>
                <ol>
                <li>Apoya la punta de la lengua, relajada, entre los dientes de arriba y los de abajo, o justo detrás de los dientes de arriba. Sin morder.</li>
                <li>Deja salir el aire por encima de la lengua, rozando los dientes.</li>
                <li>Para la <strong>TH sorda</strong> <span class="ipa">/θ/</span>, solo aire. Para la <strong>TH sonora</strong> <span class="ipa">/ð/</span>, el mismo gesto, pero con voz, como un zumbido.</li>
                </ol>
                <div class="example-grid">
                <div class="mini-card"><strong>TH sonora /ð/</strong><span>Vibra la garganta. Aparece en <em>they</em>, <em>this</em>, <em>that</em>, <em>there</em>, <em>weather</em>.</span></div>
                <div class="mini-card"><strong>TH sorda /θ/</strong><span>No vibra la garganta. Aparece en <em>think</em>, <em>three</em>, <em>thanks</em>, <em>through</em>.</span></div>
                </div>
                <p>Una forma rápida de comprobarlo es tocarte la garganta. En <em>they</em> deberías notar vibración; en <em>think</em>, no.</p>
                <table class="data-table">
                <thead><tr><th>Palabra</th><th>IPA UK</th><th>IPA US</th><th>TH</th></tr></thead>
                <tbody>
                <tr><td>think</td><td><span class="ipa">/θɪŋk/</span></td><td><span class="ipa">/θɪŋk/</span></td><td>sorda</td></tr>
                <tr><td>three</td><td><span class="ipa">/θriː/</span></td><td><span class="ipa">/θriː/</span></td><td>sorda</td></tr>
                <tr><td>thanks</td><td><span class="ipa">/θæŋks/</span></td><td><span class="ipa">/θæŋks/</span></td><td>sorda</td></tr>
                <tr><td>Thursday</td><td><span class="ipa">/ˈθɜːzdeɪ/</span></td><td><span class="ipa">/ˈθɝːzdeɪ/</span></td><td>sorda</td></tr>
                <tr><td>birthday</td><td><span class="ipa">/ˈbɜːθdeɪ/</span></td><td><span class="ipa">/ˈbɝːθdeɪ/</span></td><td>sorda</td></tr>
                <tr><td>month</td><td><span class="ipa">/mʌnθ/</span></td><td><span class="ipa">/mʌnθ/</span></td><td>sorda</td></tr>
                <tr><td>this</td><td><span class="ipa">/ðɪs/</span></td><td><span class="ipa">/ðɪs/</span></td><td>sonora</td></tr>
                <tr><td>they</td><td><span class="ipa">/ðeɪ/</span></td><td><span class="ipa">/ðeɪ/</span></td><td>sonora</td></tr>
                <tr><td>those</td><td><span class="ipa">/ðəʊz/</span></td><td><span class="ipa">/ðoʊz/</span></td><td>sonora</td></tr>
                <tr><td>mother</td><td><span class="ipa">/ˈmʌðə/</span></td><td><span class="ipa">/ˈmʌðɚ/</span></td><td>sonora</td></tr>
                <tr><td>weather</td><td><span class="ipa">/ˈweðə/</span></td><td><span class="ipa">/ˈweðɚ/</span></td><td>sonora</td></tr>
                <tr><td>breathe</td><td><span class="ipa">/briːð/</span></td><td><span class="ipa">/briːð/</span></td><td>sonora</td></tr>
                </tbody>
                </table>
                <h2 id="espanol">¿Los españoles ya tenemos el sonido TH?</h2>
                <p>Sí, y es una ventaja enorme. Si en tu español distingues <em>casa</em> de <em>caza</em> (lo que se llama distinción, habitual en la mayor parte de España), la c de <em>cena</em> y la z de <em>zapato</em> son el mismo sonido <span class="ipa">/θ/</span> de <em>think</em>. También lo tienen quienes cecean. Haz la prueba: di <em>zinc</em> en español. Con una i un poco más relajada, acabas de decir <em>think</em> <span class="ipa">/θɪŋk/</span>.</p>
                <p>Si eres de Canarias o de una zona seseante de Andalucía, o hablas español de América, ese sonido no existe en tu español y lo normal es sustituirlo por S. Tendrás que aprenderlo desde cero, pero la posición es la misma que acabas de ver.</p>
                <p>¿Y la TH sonora <span class="ipa">/ð/</span>? También la tienes, aunque escondida: es la d suave que haces entre vocales en <em>nada</em>, <em>cada</em> o en la segunda d de <em>dedo</em>. La diferencia es que en español, al empezar a hablar o después de N o L, sale una d “dura”, con la lengua pegada a los dientes, y en inglés muchas frases empiezan justo así, desde el silencio: <em>They are here</em>, <em>This is it</em>. La <span class="ipa">/ð/</span> inglesa, además, suele hacerse un poco más adelante, con la lengua asomando entre los dientes y algo más de fricción.</p>
                <p>Truco: di <em>nada</em> despacio, quédate en la segunda d y alárgala con voz. Desde ahí, salta a <em>they</em>.</p>
                <h2 id="errores">Errores típicos de los españoles: T, D, S, F y Z</h2>
                <p>El primer error es hacer <em>they</em> como si fuera <em>day</em>. En <em>day</em>, la punta de la lengua toca el paladar justo detrás de los dientes de arriba; en <em>they</em>, la lengua va entre los dientes. El audio de <a href="/audio/sonido-th-paladar.html">TH frente a D</a> sirve justo para notar ese contraste. Los demás sustitutos habituales son estos:</p>
                <ul>
                <li><strong>T:</strong> <em>think</em> sale como <em>tink</em>, <em>three</em> como <em>tree</em> (árbol) y <em>thank</em> como <em>tank</em> (tanque).</li>
                <li><strong>D:</strong> <em>they</em> como <em>day</em> (día), <em>then</em> como <em>den</em> (guarida), <em>those</em> como <em>doze</em> (dormitar).</li>
                <li><strong>S:</strong> <em>think</em> como <em>sink</em> (fregadero; hundirse), <em>thick</em> como <em>sick</em> (enfermo), <em>mouth</em> como <em>mouse</em> (ratón). Es el error típico de las zonas seseantes y de los hispanohablantes de América.</li>
                <li><strong>F:</strong> <em>three</em> como <em>free</em>, <em>thought</em> como <em>fought</em>. Algunos acentos nativos, como muchos de Londres, hacen esto de forma natural, pero no es el modelo que conviene aprender.</li>
                <li><strong>Z española en la TH sonora:</strong> decir <em>this</em> con la z de <em>zapato</em>. La posición es buena, pero falta voz: en realidad estás diciendo <span class="ipa">/θɪs/</span>. Se entiende, aunque suena un poco seco.</li>
                </ul>
                <p>No hace falta exagerarlo hasta escupir aire. Basta con que la lengua asome o toque los dientes y el aire salga de forma controlada.</p>
                <h2 id="pares">Pares mínimos para practicar la TH</h2>
                <p>Un par mínimo son dos palabras que solo se diferencian en un sonido. Son el mejor entrenamiento: si las dos te suenan igual cuando las dices, todavía no has encontrado la posición.</p>
                <table class="data-table">
                <thead><tr><th>Con TH</th><th>Si fallas, dices...</th><th>Significado de lo que dices</th></tr></thead>
                <tbody>
                <tr><td>think <span class="ipa">/θɪŋk/</span></td><td>sink <span class="ipa">/sɪŋk/</span> o <em>tink</em></td><td>fregadero, hundirse; <em>tink</em> no existe</td></tr>
                <tr><td>three <span class="ipa">/θriː/</span></td><td>tree <span class="ipa">/triː/</span></td><td>árbol</td></tr>
                <tr><td>thank <span class="ipa">/θæŋk/</span></td><td>tank <span class="ipa">/tæŋk/</span></td><td>tanque, depósito</td></tr>
                <tr><td>thought <span class="ipa">/θɔːt/</span> (UK) · <span class="ipa">/θɑːt/</span> (US)</td><td>taught <span class="ipa">/tɔːt/</span> (UK) · <span class="ipa">/tɑːt/</span> (US)</td><td>enseñó, enseñado</td></tr>
                <tr><td>thick <span class="ipa">/θɪk/</span></td><td>sick <span class="ipa">/sɪk/</span></td><td>enfermo</td></tr>
                <tr><td>mouth <span class="ipa">/maʊθ/</span></td><td>mouse <span class="ipa">/maʊs/</span></td><td>ratón</td></tr>
                <tr><td>they <span class="ipa">/ðeɪ/</span></td><td>day <span class="ipa">/deɪ/</span></td><td>día</td></tr>
                <tr><td>then <span class="ipa">/ðen/</span></td><td>den <span class="ipa">/den/</span></td><td>guarida</td></tr>
                <tr><td>those <span class="ipa">/ðəʊz/</span> (UK) · <span class="ipa">/ðoʊz/</span> (US)</td><td>doze <span class="ipa">/dəʊz/</span> (UK) · <span class="ipa">/doʊz/</span> (US)</td><td>dormitar</td></tr>
                <tr><td>though <span class="ipa">/ðəʊ/</span> (UK) · <span class="ipa">/ðoʊ/</span> (US)</td><td>dough <span class="ipa">/dəʊ/</span> (UK) · <span class="ipa">/doʊ/</span> (US)</td><td>masa</td></tr>
                </tbody>
                </table>
                <p>Para el cuarteto <em>though</em>, <em>tough</em>, <em>thought</em> y <em>taught</em> tienes un audio específico: <a href="/audio/though-tough-thought-taught.html">though, tough, thought, taught</a>.</p>
                <h2 id="lista">The, this, that, they: ¿cuándo la TH es sonora?</h2>
                <p>No hay una regla perfecta, pero estas tendencias aciertan casi siempre:</p>
                <ul>
                <li><strong>Palabras gramaticales que empiezan por TH: sonora.</strong> <em>the</em>, <em>this</em> <span class="ipa">/ðɪs/</span>, <em>that</em> <span class="ipa">/ðæt/</span>, <em>these</em> <span class="ipa">/ðiːz/</span>, <em>those</em>, <em>they</em>, <em>them</em> <span class="ipa">/ðem/</span>, <em>their</em> y <em>there</em> <span class="ipa">/ðeə/</span> (UK) · <span class="ipa">/ðer/</span> (US), <em>then</em>, <em>than</em> <span class="ipa">/ðæn/</span>, <em>though</em>.</li>
                <li><strong>Palabras de contenido que empiezan por TH: sorda.</strong> <em>think</em>, <em>three</em>, <em>thing</em>, <em>thank</em>, <em>Thursday</em>, <em>theory</em>, <em>thirty</em>.</li>
                <li><strong>Entre vocales, en palabras comunes: suele ser sonora.</strong> <em>mother</em>, <em>brother</em>, <em>father</em>, <em>other</em>, <em>weather</em>, <em>together</em>. Excepciones frecuentes con sorda: <em>nothing</em> <span class="ipa">/ˈnʌθɪŋ/</span>, <em>author</em>, <em>method</em>.</li>
                <li><strong>Al final de palabra: normalmente sorda, pero sonora en los verbos en -the.</strong> <em>breath</em> <span class="ipa">/breθ/</span> (aliento) frente a <em>breathe</em> <span class="ipa">/briːð/</span> (respirar); <em>teeth</em> <span class="ipa">/tiːθ/</span> (dientes) frente a <em>teethe</em> <span class="ipa">/tiːð/</span> (echar los dientes).</li>
                <li><strong>Algunas TH suenan como T:</strong> <em>Thomas</em>, <em>Thailand</em>, <em>Thames</em> <span class="ipa">/temz/</span> y <em>thyme</em> (tomillo) <span class="ipa">/taɪm/</span>.</li>
                </ul>
                <p><em>With</em> admite las dos: <span class="ipa">/wɪð/</span> y <span class="ipa">/wɪθ/</span>. Y <em>the</em> tiene su propia regla: normalmente <span class="ipa">/ðə/</span> antes de sonido consonante (<em>the car</em>) y <span class="ipa">/ði/</span> antes de sonido vocal (<em>the apple</em>). La tienes explicada a fondo en <a href="/articulos/como-se-pronuncia-the.html">cómo se pronuncia THE en inglés</a>.</p>
                <h2 id="practica">Práctica rápida</h2>
                <ol>
                <li>Di <em>day</em> y <em>they</em> alternando, fijándote solo en dónde está la lengua.</li>
                <li>Practica una serie con TH sonora: <em>this, these, there, though, brother</em>.</li>
                <li>Practica una serie con TH sorda: <em>think, three, thanks, through, teeth</em>.</li>
                <li>Vuelve a una frase corta: <em>They think that this is good</em>.</li>
                <li>Prueba con números, donde más se nota: <em>thirty-three</em> lleva dos TH sordas, <span class="ipa">/ˌθɜːtiˈθriː/</span> (UK) · <span class="ipa">/ˌθɝːtiˈθriː/</span> (US). Escúchalo en <a href="/audio/i-am-from-spain-and-i-am-33.html">I am from Spain and I am 33</a>.</li>
                </ol>
                <p>Ahora tú: ¿TH sorda o sonora?</p>
                <details class="exercise"><summary>1. <em>thanks</em></summary><p>Sorda: <span class="ipa">/θæŋks/</span>. Es una palabra de contenido que empieza por TH.</p></details>
                <details class="exercise"><summary>2. <em>mother</em></summary><p>Sonora: <span class="ipa">/ˈmʌðə/</span> (UK) · <span class="ipa">/ˈmʌðɚ/</span> (US). TH entre vocales en una palabra común.</p></details>
                <details class="exercise"><summary>3. <em>those</em></summary><p>Sonora: es una palabra gramatical, de la familia de <em>this</em> y <em>that</em>.</p></details>
                <details class="exercise"><summary>4. <em>birthday</em></summary><p>Sorda: <span class="ipa">/ˈbɜːθdeɪ/</span> (UK) · <span class="ipa">/ˈbɝːθdeɪ/</span> (US).</p></details>
                <details class="exercise"><summary>5. <em>breath</em> y <em>breathe</em></summary><p><em>Breath</em> (sustantivo) lleva sorda, <span class="ipa">/breθ/</span>; <em>breathe</em> (verbo) lleva sonora, <span class="ipa">/briːð/</span>. Además, cambia la vocal.</p></details>
                <details class="exercise"><summary>6. <em>nothing</em></summary><p>Sorda, <span class="ipa">/ˈnʌθɪŋ/</span>, aunque esté entre vocales: viene de <em>thing</em>.</p></details>
                <p>Empieza por los audios de <a href="/audio/sonido-th-entre-dientes.html">TH entre dientes</a> y <a href="/audio/sonido-th-paladar.html">TH frente a D</a>, y después pasa a las <a href="/audio/though-through-tough-cough-enough-bough-thought-plough.html">palabras con TH y OUGH</a>. Con unos minutos al día, la lengua acaba yendo sola al sitio.</p>
        """,
    },
    {
        "slug": "vocales-ingles-cortas-largas",
        "category": "Pronunciación",
        "title": "Vocales en inglés para españoles: cortas, largas y la schwa (ship/sheep, book/moon, cat/cut)",
        "seo_title": "Vocales en inglés: cortas, largas y schwa para españoles",
        "description": "Pronunciación de las vocales en inglés para españoles: vocales cortas y largas, la schwa y pares como ship/sheep, full/fool o cat/cut, con IPA y audios.",
        "lede": "El inglés tiene cinco letras vocales, pero muchos más sonidos. Por eso leer con vocales españolas puede cambiar una palabra por otra, y no siempre por una palabra educada.",
        "reading": "9 minutos",
        "published": "2026-06-28",
        "toc": [
            ("problema", "El contraste"),
            ("tabla", "Tabla de vocales"),
            ("i-corta", "I corta y larga"),
            ("doble-o", "Doble O"),
            ("tres-aes", "Cat, cut, cart"),
            ("schwa", "La schwa"),
            ("practica", "Práctica"),
        ],
        "related": [
            "pronunciacion-ingles-para-espanoles",
            "alfabeto-fonetico-ingles",
            "guia-pronunciacion-ingles-espanoles",
            "palabras-ough-pronunciacion-ingles",
        ],
        "quick_answer": "El español tiene 5 vocales; el inglés, según el acento, una docena de vocales simples más varios diptongos. Para un español, lo clave es distinguir cortas y largas (<em>ship</em> /ʃɪp/ frente a <em>sheep</em> /ʃiːp/, <em>full</em> frente a <em>fool</em>), las tres “aes” de <em>cat</em>, <em>cut</em> y <em>cart</em>, y la <strong>schwa</strong> /ə/, la vocal débil más frecuente.",
        "faq": [
            ("¿Cuántas vocales tiene el inglés?", "Cinco letras vocales, pero muchos más sonidos. Depende del acento y de cómo se cuenten: en el inglés británico estándar se suelen contar 12 vocales simples y 8 diptongos. El español, en cambio, tiene 5 sonidos vocálicos."),
            ("¿Qué es la schwa en inglés?", "La schwa, <span class=\"ipa\">/ə/</span>, es una vocal neutra, corta y relajada que aparece en las sílabas sin acento, como la primera de <em>about</em> o la última de <em>banana</em>. Se considera la vocal más frecuente del inglés y es la que más cambia el ritmo de un español."),
            ("¿Qué diferencia hay entre vocales cortas y largas en inglés?", "No es solo la duración. Las largas, como la <span class=\"ipa\">/iː/</span> de <em>sheep</em>, son más tensas; las cortas, como la <span class=\"ipa\">/ɪ/</span> de <em>ship</em>, más relajadas y abiertas. En el alfabeto fonético, las largas llevan dos puntos: <span class=\"ipa\">ː</span>."),
            ("¿Cómo se pronuncia beach para que no suene mal?", "<em>Beach</em> se pronuncia <span class=\"ipa\">/biːtʃ/</span>, con una i larga y tensa, estirando un poco los labios. Si la i sale corta y relajada, <span class=\"ipa\">/bɪtʃ/</span>, se convierte en un insulto. Lo mismo ocurre con <em>sheet</em> <span class=\"ipa\">/ʃiːt/</span>, que con i corta es una palabrota."),
            ("¿Por qué love no se pronuncia con o?", "Porque en <em>love</em> la O representa el sonido <span class=\"ipa\">/ʌ/</span>, una a corta y relajada que no existe en español. Pasa lo mismo en <em>money</em>, <em>come</em>, <em>mother</em> o <em>son</em>. Por eso <em>love</em> rima con <em>glove</em>, pero no con <em>move</em>."),
        ],
        "body": """
                <p>En español, las vocales son bastante estables. La <em>a</em>, la <em>e</em>, la <em>i</em>, la <em>o</em> y la <em>u</em> casi siempre suenan como esperas. En inglés, la letra no manda tanto: manda la palabra. Y esas cinco letras vocales se reparten muchos más sonidos.</p>
                <p>Ese es uno de los motivos por los que un español puede decir una palabra con seguridad y aun así provocar confusión. La vocal equivocada no es un detalle estético; puede cambiar el significado. Esta guía repasa la pronunciación de las vocales en inglés que más problemas dan a los españoles, con su símbolo fonético, pares de palabras y audios. Cuando hay una sola transcripción, coincide en británico y americano.</p>
                <h2 id="problema">El problema no es tu acento, es el contraste</h2>
                <p>Si pronuncias <em>bit</em> con una i española demasiado limpia, el oyente puede acercarlo a <em>beat</em>. Si pronuncias <em>book</em> como una u larga española, se aleja del sonido natural. Y si lees <em>love</em> como se escribe, no sonará como una palabra inglesa reconocible.</p>
                <p>Un matiz importante: aunque se hable de vocales “cortas” y “largas”, la diferencia no es solo de duración. La vocal de <em>sheep</em> <span class="ipa">/ʃiːp/</span> es más tensa, con los labios estirados; la de <em>ship</em> <span class="ipa">/ʃɪp/</span> es más relajada y abierta, a medio camino hacia la e. En el alfabeto fonético, los dos puntos <span class="ipa">ː</span> marcan las largas. En inglés americano la duración pesa algo menos y la calidad del sonido, más.</p>
                <div class="lesson-box"><strong>Regla útil:</strong> no busques una vocal española perfecta para cada caso. Busca contrastes: <em>bit</em> no debe sonar como <em>beat</em>; <em>book</em> no debe sonar como <em>moon</em>.</div>
                <h2 id="tabla">Tabla de vocales en inglés para españoles</h2>
                <p>Estas son las vocales simples del inglés, con una pista para hacerlas desde el español. Si los símbolos te resultan nuevos, tienes una explicación sencilla en el <a href="/articulos/alfabeto-fonetico-ingles.html">alfabeto fonético inglés</a>.</p>
                <table class="data-table">
                <thead><tr><th>Sonido</th><th>Ejemplos</th><th>Cómo hacerlo</th><th>No confundir con</th></tr></thead>
                <tbody>
                <tr><td><span class="ipa">/iː/</span></td><td>sheep, leave, beach</td><td>i española larga y tensa, sonriendo</td><td><span class="ipa">/ɪ/</span></td></tr>
                <tr><td><span class="ipa">/ɪ/</span></td><td>ship, live, bit</td><td>i corta y relajada, cerca de la e</td><td><span class="ipa">/iː/</span></td></tr>
                <tr><td><span class="ipa">/e/</span></td><td>bed, men, said</td><td>parecida a nuestra e</td><td><span class="ipa">/æ/</span></td></tr>
                <tr><td><span class="ipa">/æ/</span></td><td>cat, bad, man</td><td>boca muy abierta, entre a y e</td><td><span class="ipa">/e/</span>, <span class="ipa">/ʌ/</span></td></tr>
                <tr><td><span class="ipa">/ʌ/</span></td><td>cut, love, up</td><td>a corta y relajada, boca poco abierta</td><td><span class="ipa">/æ/</span>, <span class="ipa">/ɑː/</span></td></tr>
                <tr><td><span class="ipa">/ɑː/</span></td><td>cart, father, calm</td><td>a larga y profunda</td><td><span class="ipa">/ʌ/</span></td></tr>
                <tr><td><span class="ipa">/ɒ/</span> (UK) · <span class="ipa">/ɑː/</span> (US)</td><td>lock, hot, stop</td><td>UK: o corta y abierta; US: a abierta</td><td><span class="ipa">/ɔː/</span></td></tr>
                <tr><td><span class="ipa">/ɔː/</span></td><td>door, floor, saw (UK)</td><td>o larga, labios redondeados</td><td><span class="ipa">/ɒ/</span></td></tr>
                <tr><td><span class="ipa">/ʊ/</span></td><td>book, full, look</td><td>u corta, labios poco redondeados</td><td><span class="ipa">/uː/</span></td></tr>
                <tr><td><span class="ipa">/uː/</span></td><td>moon, fool, Luke</td><td>u larga, labios redondeados</td><td><span class="ipa">/ʊ/</span></td></tr>
                <tr><td><span class="ipa">/ɜː/</span> (UK) · <span class="ipa">/ɝː/</span> (US)</td><td>bird, world, learn</td><td>vocal neutra larga; en EE. UU., con R</td><td><span class="ipa">/ɑː/</span></td></tr>
                <tr><td><span class="ipa">/ə/</span> (schwa)</td><td>about, banana, doctor</td><td>vocal débil, con la boca en reposo</td><td>cualquier vocal “entera”</td></tr>
                </tbody>
                </table>
                <p>A estas doce se suman los diptongos, como los de <em>day</em> <span class="ipa">/eɪ/</span>, <em>my</em> <span class="ipa">/aɪ/</span>, <em>now</em> <span class="ipa">/aʊ/</span> o <em>go</em> <span class="ipa">/əʊ/</span> (UK) · <span class="ipa">/oʊ/</span> (US).</p>
                <h2 id="i-corta">La I corta y la I larga: ship/sheep, live/leave</h2>
                <p>La <strong>I corta</strong> <span class="ipa">/ɪ/</span> de palabras como <em>bit</em>, <em>sit</em>, <em>win</em> o <em>lip</em> es uno de los sonidos más rentables para un hispanohablante. Se parece más a una vocal relajada entre nuestra i y nuestra e que a una i española pura. La <strong>I larga</strong> <span class="ipa">/iː/</span>, en cambio, sí se parece a nuestra i, pero más tensa y algo más larga. Una i demasiado española te acerca a la larga:</p>
                <table class="data-table">
                <thead><tr><th>I corta <span class="ipa">/ɪ/</span></th><th>I larga <span class="ipa">/iː/</span></th></tr></thead>
                <tbody>
                <tr><td>ship <span class="ipa">/ʃɪp/</span> (barco)</td><td>sheep <span class="ipa">/ʃiːp/</span> (oveja)</td></tr>
                <tr><td>live <span class="ipa">/lɪv/</span> (vivir)</td><td>leave <span class="ipa">/liːv/</span> (irse, dejar)</td></tr>
                <tr><td>sit <span class="ipa">/sɪt/</span> (sentarse)</td><td>seat <span class="ipa">/siːt/</span> (asiento)</td></tr>
                <tr><td>fill <span class="ipa">/fɪl/</span> (llenar)</td><td>feel <span class="ipa">/fiːl/</span> (sentir)</td></tr>
                <tr><td>chip <span class="ipa">/tʃɪp/</span> (chip; patata frita)</td><td>cheap <span class="ipa">/tʃiːp/</span> (barato)</td></tr>
                </tbody>
                </table>
                <p>Y luego están los pares que nadie quiere fallar en voz alta: <em>beach</em> <span class="ipa">/biːtʃ/</span> (playa) frente a <span class="ipa">/bɪtʃ/</span>, que es un insulto, y <em>sheet</em> <span class="ipa">/ʃiːt/</span> (hoja, sábana) frente a <span class="ipa">/ʃɪt/</span>, que es una palabrota. El subtítulo de <em>De FAK a Fluent</em> es, literalmente, “Consejos de un español que también confundió <em>beach</em> con otra cosa”. Si quieres hablar de la playa, alarga la i y estira un poco los labios. Y si un día te bloqueas, siempre te queda <em>the seaside</em>.</p>
                <p>Practica con <a href="/audio/bit-big-win-lip-clip.html">bit, big, win, lip, clip</a>, con el audio de <a href="/audio/hit.html">hit</a> y con <a href="/audio/live-leave-leaf.html">live, leave, leaf</a>.</p>
                <h2 id="doble-o">La doble O: book no suena como moon (full/fool, look/Luke)</h2>
                <p>La OO inglesa esconde dos vocales distintas: la <span class="ipa">/ʊ/</span> corta de <em>book</em> <span class="ipa">/bʊk/</span> y la <span class="ipa">/uː/</span> larga de <em>moon</em> <span class="ipa">/muːn/</span>. La corta se hace con los labios menos redondeados y la lengua más relajada. Si le pones una u española larga, <em>full</em> <span class="ipa">/fʊl/</span> (lleno) se convierte en <em>fool</em> <span class="ipa">/fuːl/</span> (tonto), y <em>look</em> <span class="ipa">/lʊk/</span> en <em>Luke</em> <span class="ipa">/luːk/</span>.</p>
                <div class="example-grid">
                <div class="mini-card"><strong>OO corta /ʊ/</strong><span><em>book, cook, look, foot, took, good</em>. Es rápida y no tan larga como nuestra u.</span></div>
                <div class="mini-card"><strong>OO larga /uː/</strong><span><em>moon, food, room, school, cool</em>. Aquí sí aparece una u más larga y marcada (<em>room</em> también se oye con la corta).</span></div>
                <div class="mini-card"><strong>O larga /ɔː/</strong><span><em>door, floor, score, shore</em>. No la mezcles con la doble O de <em>book</em>.</span></div>
                <div class="mini-card"><strong>OO inesperada /ʌ/</strong><span><em>blood</em> y <em>flood</em> suenan con la vocal de <em>cut</em>: <span class="ipa">/blʌd/</span>, <span class="ipa">/flʌd/</span>.</span></div>
                </div>
                <p>Escucha la versión correcta de <a href="/audio/book-cook-look-foot-hook-took-cookie-correcto.html">book, cook, look, foot, hook, took, cookie</a> y compárala con <a href="/audio/moon-food-room-school-tool-noodle-cool.html">moon, food, room, school, tool, noodle, cool</a>. Si quieres reírte un poco, también está la <a href="/audio/book-cook-look-foot-hook-took-cookie-lol.html">versión con el error típico</a>. Y para la O larga, <a href="/audio/door-floor-score-shore-roar-soar.html">door, floor, score, shore, roar, soar</a>.</p>
                <h2 id="tres-aes">Cat, cut y cart: tres “aes” que en español son una</h2>
                <p>Donde el español tiene una sola a, el inglés tiene tres sonidos que cambian el significado:</p>
                <ul>
                <li><strong><span class="ipa">/æ/</span></strong>, con la boca muy abierta, entre a y e: <em>cat</em> <span class="ipa">/kæt/</span> (gato), <em>bad</em>, <em>man</em>, <em>lack</em>.</li>
                <li><strong><span class="ipa">/ʌ/</span></strong>, una a corta y relajada, casi sin abrir: <em>cut</em> <span class="ipa">/kʌt/</span> (cortar), <em>love</em> <span class="ipa">/lʌv/</span>, <em>up</em>, <em>money</em>.</li>
                <li><strong><span class="ipa">/ɑː/</span></strong>, una a larga y profunda: <em>cart</em> <span class="ipa">/kɑːt/</span> (UK) · <span class="ipa">/kɑːrt/</span> (US) (carro), <em>father</em>, <em>heart</em>.</li>
                </ul>
                <p>La <span class="ipa">/ʌ/</span> es la más traicionera porque se escribe con U (<em>up</em>, <em>us</em>, <em>uncle</em>, <em>umbrella</em>) y también con O (<em>love</em>, <em>money</em>, <em>come</em>, <em>mother</em>). Por eso <em>love</em>, <em>clove</em> y <em>move</em> se escriben casi igual y tienen tres vocales distintas: <span class="ipa">/lʌv/</span>, <span class="ipa">/kləʊv/</span> (UK) · <span class="ipa">/kloʊv/</span> (US) y <span class="ipa">/muːv/</span>.</p>
                <p>Otro contraste que conviene vigilar es <em>bed</em> <span class="ipa">/bed/</span> frente a <em>bad</em> <span class="ipa">/bæd/</span>, o <em>men</em> frente a <em>man</em>: si la <span class="ipa">/æ/</span> te sale como una e española, el plural y el singular suenan igual.</p>
                <p>Practica con <a href="/audio/love-clove-move.html">love, clove, move</a>, <a href="/audio/microsoft-up-us-uncle-umbrella.html">Microsoft, up, us, uncle, umbrella</a> y <a href="/audio/lack-lock-look-luke.html">lack, lock, look, Luke</a>: cuatro palabras con cuatro vocales distintas, <span class="ipa">/læk/</span>, <span class="ipa">/lɒk/</span> (UK) · <span class="ipa">/lɑːk/</span> (US), <span class="ipa">/lʊk/</span> y <span class="ipa">/luːk/</span>.</p>
                <h2 id="schwa">La schwa /ə/: la vocal que nadie te enseña</h2>
                <p>La <strong>schwa</strong> <span class="ipa">/ə/</span> es una vocal neutra, corta y sin esfuerzo: la que sale si relajas la mandíbula y dices un “eh” muy breve sin mover nada. Se considera el sonido vocálico más frecuente del inglés porque aparece en muchísimas sílabas sin acento, se escriban con la letra que se escriban:</p>
                <ul>
                <li><em>about</em> <span class="ipa">/əˈbaʊt/</span>: la A inicial.</li>
                <li><em>today</em> <span class="ipa">/təˈdeɪ/</span>: la O.</li>
                <li><em>banana</em> <span class="ipa">/bəˈnɑːnə/</span> (UK) · <span class="ipa">/bəˈnænə/</span> (US): la primera y la última A.</li>
                <li><em>doctor</em> <span class="ipa">/ˈdɒktə/</span> (UK) · <span class="ipa">/ˈdɑːktɚ/</span> (US): la segunda O (en americano, con R).</li>
                <li><em>focus</em> <span class="ipa">/ˈfəʊkəs/</span> (UK) · <span class="ipa">/ˈfoʊkəs/</span> (US): la U. Practícala con <a href="/audio/focus.html">focus</a>.</li>
                </ul>
                <p>Los españoles tendemos a pronunciar cada vocal entera, tal como se escribe: <em>ba-na-na</em> con tres aes iguales. El resultado se entiende, pero suena muy español, porque el inglés necesita ese contraste entre sílabas fuertes y débiles. La schwa también es la clave de las formas débiles: <em>to</em> <span class="ipa">/tə/</span>, <em>of</em> <span class="ipa">/əv/</span>, <em>a</em> <span class="ipa">/ə/</span>. Lo tienes desarrollado en <a href="/articulos/ligar-palabras-ingles.html">cómo ligar palabras en inglés</a>.</p>
                <h3>Bonus: bird, bear, beer, beard</h3>
                <p>La vocal larga de <em>bird</em> <span class="ipa">/bɜːd/</span> (UK) · <span class="ipa">/bɝːd/</span> (US) es pariente de la schwa y no existe en español. Y con R detrás aparecen combinaciones que conviene separar bien: <em>bear</em> <span class="ipa">/beə/</span> (UK) · <span class="ipa">/ber/</span> (US), <em>beer</em> <span class="ipa">/bɪə/</span> (UK) · <span class="ipa">/bɪr/</span> (US) y <em>beard</em> <span class="ipa">/bɪəd/</span> (UK) · <span class="ipa">/bɪrd/</span> (US). Practica con <a href="/audio/bird-bear-beer-beard.html">bird, bear, beer, beard</a>: pedir una cerveza y acabar hablando de un oso es un clásico.</p>
                <h2 id="practica">Cómo practicar las vocales sin volverte loco</h2>
                <ol>
                <li>Elige un contraste por sesión: <em>ship</em> frente a <em>sheep</em>, o <em>book</em> frente a <em>moon</em>.</li>
                <li>Escucha antes de leer para que la ortografía no te arrastre.</li>
                <li>Repite en pares: corto, largo, corto, largo.</li>
                <li>Termina con frases completas para que la vocal sobreviva al ritmo real: <em>I live here, but I leave tomorrow</em>.</li>
                </ol>
                <p>Comprueba lo que has aprendido:</p>
                <details class="exercise"><summary>1. <em>I want to ___ in London</em> (vivir): ¿<em>live</em> o <em>leave</em>?</summary><p><em>Live</em>, con I corta: <span class="ipa">/lɪv/</span>. Con I larga, <em>leave</em> <span class="ipa">/liːv/</span>, dirías que quieres irte de Londres.</p></details>
                <details class="exercise"><summary>2. ¿Qué palabra tiene una vocal distinta: <em>book</em>, <em>look</em>, <em>food</em>, <em>foot</em>?</summary><p><em>Food</em>, con <span class="ipa">/uː/</span> larga. Las otras tres llevan <span class="ipa">/ʊ/</span> corta.</p></details>
                <details class="exercise"><summary>3. <em>The ___ is black</em> (el gato): ¿<em>cat</em>, <em>cut</em> o <em>cart</em>?</summary><p><em>Cat</em> <span class="ipa">/kæt/</span>, con la boca muy abierta. <em>Cut</em> <span class="ipa">/kʌt/</span> es cortar y <em>cart</em>, un carro.</p></details>
                <details class="exercise"><summary>4. ¿<em>Love</em> rima con <em>move</em> o con <em>glove</em>?</summary><p>Con <em>glove</em> (guante): las dos llevan <span class="ipa">/ʌ/</span>. <em>Move</em> lleva <span class="ipa">/uː/</span>.</p></details>
                <details class="exercise"><summary>5. ¿Cuántas schwas tiene <em>banana</em> en inglés británico?</summary><p>Dos, la primera y la última A: <span class="ipa">/bəˈnɑːnə/</span>. Solo la A del medio, la acentuada, suena entera.</p></details>
                <p>Para seguir, repasa las <a href="/articulos/palabras-ingles-mal-pronunciadas.html">palabras que los españoles pronuncian mal</a> y vuelve a estos audios cada pocos días: cada contraste que fijas se nota en cómo te entienden.</p>
        """,
    },
    {
        "slug": "letras-mudas-ingles",
        "category": "Pronunciación",
        "title": "Letras mudas en inglés: lista por letra con pronunciación y audios",
        "seo_title": "Letras mudas en inglés: lista por letra con IPA y audios",
        "description": "Letras mudas en inglés (silent letters) ordenadas por letra: B, K, L, W, G, H, T, P, D y U, con IPA, ejemplos y audios para dejar de pronunciarlas.",
        "lede": "En inglés no todo lo que se escribe se pronuncia. Memorizar unas pocas familias de letras mudas evita muchos errores muy visibles, desde walk hasta Wednesday.",
        "reading": "9 minutos",
        "published": "2026-06-28",
        "toc": [
            ("por-que", "Por qué existen"),
            ("tabla", "Lista con IPA"),
            ("b-muda", "B muda"),
            ("l-muda", "L muda"),
            ("h-muda", "H muda"),
            ("t-muda", "T muda"),
            ("practica", "Ejercicio"),
        ],
        "related": [
            "palabras-ough-pronunciacion-ingles",
            "palabras-ingles-mal-pronunciadas",
            "alfabeto-fonetico-ingles",
            "pronunciacion-ingles-para-espanoles",
        ],
        "quick_answer": "Las <strong>letras mudas en inglés</strong> (<em>silent letters</em>) se escriben pero no se pronuncian: la B de <em>comb</em>, la K de <em>know</em>, la L de <em>walk</em>, la W de <em>write</em> o la T de <em>listen</em>. No hay una regla única, pero casi todas siguen patrones como <em>-mb</em>, <em>kn-</em>, <em>wr-</em> o <em>-alk</em>.",
        "faq": [
            ("¿Hay alguna regla para saber si una letra es muda en inglés?", "No hay una regla universal, pero sí patrones fiables: <em>kn-</em> y <em>wr-</em> al principio de palabra (<em>know</em>, <em>write</em>), <em>-mb</em> al final (<em>comb</em>), <em>-alk</em> y <em>-ould</em> (<em>walk</em>, <em>would</em>) o <em>-stle</em> y <em>-sten</em> (<em>castle</em>, <em>listen</em>). Aun así hay excepciones, como <em>milk</em>, donde la L sí se pronuncia."),
            ("¿Se pronuncia la T de often?", "Las dos versiones son correctas: sin T (UK <span class=\"ipa\">/ˈɒf.ən/</span>, US <span class=\"ipa\">/ˈɑː.fən/</span>) y con T (UK <span class=\"ipa\">/ˈɒf.tən/</span>, US <span class=\"ipa\">/ˈɑːf.tən/</span>). La versión sin T es la más tradicional, pero con T también es muy habitual en Reino Unido y en Estados Unidos."),
            ("¿Por qué se dice an hour y no a hour?", "Porque la H de <em>hour</em> es muda y la palabra empieza por sonido vocálico. La elección entre <em>a</em> y <em>an</em> depende del sonido, no de la letra: <em>an hour</em> y <em>an honest man</em>, pero <em>a house</em> y <em>a university</em>, que empiezan con sonido consonante."),
            ("¿Cómo se pronuncia salmon en inglés?", "<em>Salmon</em> se pronuncia <span class=\"ipa\">/ˈsæm.ən/</span> en británico y en americano: la L es muda. La primera vocal es la A abierta de <em>cat</em>, y la segunda, una vocal débil."),
            ("¿La H de herb es muda?", "Depende del país. En inglés americano <em>herb</em> se pronuncia sin H, <span class=\"ipa\">/ɝːb/</span>, y en británico con H, <span class=\"ipa\">/hɜːb/</span>. Cada pronunciación es la normal en su variedad."),
        ],
        "body": """
                <p>Uno de los golpes de realidad del inglés es descubrir que hay letras escritas solo por tradición. Las ves, tu cerebro español intenta pronunciarlas y, de repente, una palabra tan común como <em>walk</em>, <em>know</em> o <em>listen</em> suena mucho menos natural.</p>
                <p>En español casi la única letra muda es la H (más la U de <em>queso</em> o <em>guerra</em>). En inglés hay muchas más, pero no hace falta aprender una lista infinita de excepciones: casi todas las <strong>letras mudas en inglés</strong> aparecen en grupos que se repiten. Aquí las tienes ordenadas por letra, con IPA y audios para practicar.</p>
                <h2 id="por-que">¿Por qué hay letras mudas en inglés?</h2>
                <p>La ortografía inglesa conserva capas antiguas de la lengua. Muchas palabras cambiaron su pronunciación con los siglos, pero mantuvieron su escritura. La K de <em>know</em> o la W de <em>write</em>, por ejemplo, se pronunciaban en el inglés medieval: el sonido desapareció y la letra se quedó.</p>
                <p>Otras letras se añadieron a propósito. En <em>debt</em> y <em>doubt</em>, la B se metió en la escritura para recordar el latín (<em>debitum</em>, <em>dubitare</em>), pero la pronunciación inglesa no cambió. Para un estudiante, la consecuencia es sencilla: si lees letra por letra, te equivocas.</p>
                <div class="lesson-box"><strong>Atajo práctico:</strong> aprende familias. Es más fácil recordar <em>walk, talk, half, calm</em> juntas que memorizar cada palabra como si no tuviera relación. Y cuando dudes, comprueba la pronunciación en el <a href="https://dictionary.cambridge.org/es/" target="_blank" rel="noopener noreferrer">diccionario de Cambridge</a>, que da la versión británica y la americana.</div>
                <h2 id="tabla">Lista de palabras con letras mudas en inglés (con IPA)</h2>
                <p>Las palabras más útiles, agrupadas por la letra que no se pronuncia (UK es el británico estándar; US, el americano). Si el alfabeto fonético te suena a jeroglífico, empieza por la <a href="/articulos/alfabeto-fonetico-ingles.html">guía del alfabeto fonético inglés</a>.</p>
                <table class="data-table">
                <thead><tr><th>Letra muda</th><th>Palabra</th><th>UK</th><th>US</th><th>Significado</th></tr></thead>
                <tbody>
                <tr><td>B</td><td><strong>bomb</strong></td><td><span class="ipa">/bɒm/</span></td><td><span class="ipa">/bɑːm/</span></td><td>bomba</td></tr>
                <tr><td>B</td><td><strong>comb</strong></td><td><span class="ipa">/kəʊm/</span></td><td><span class="ipa">/koʊm/</span></td><td>peine; peinar</td></tr>
                <tr><td>B</td><td><strong>tomb</strong></td><td><span class="ipa">/tuːm/</span></td><td><span class="ipa">/tuːm/</span></td><td>tumba</td></tr>
                <tr><td>B</td><td><strong>climb</strong></td><td><span class="ipa">/klaɪm/</span></td><td><span class="ipa">/klaɪm/</span></td><td>escalar, subir</td></tr>
                <tr><td>B</td><td><strong>doubt</strong></td><td><span class="ipa">/daʊt/</span></td><td><span class="ipa">/daʊt/</span></td><td>duda; dudar</td></tr>
                <tr><td>B</td><td><strong>debt</strong></td><td><span class="ipa">/det/</span></td><td><span class="ipa">/det/</span></td><td>deuda</td></tr>
                <tr><td>K</td><td><strong>know</strong></td><td><span class="ipa">/nəʊ/</span></td><td><span class="ipa">/noʊ/</span></td><td>saber, conocer</td></tr>
                <tr><td>K</td><td><strong>knife</strong></td><td><span class="ipa">/naɪf/</span></td><td><span class="ipa">/naɪf/</span></td><td>cuchillo</td></tr>
                <tr><td>K</td><td><strong>knee</strong></td><td><span class="ipa">/niː/</span></td><td><span class="ipa">/niː/</span></td><td>rodilla</td></tr>
                <tr><td>L</td><td><strong>walk</strong></td><td><span class="ipa">/wɔːk/</span></td><td><span class="ipa">/wɑːk/</span></td><td>caminar</td></tr>
                <tr><td>L</td><td><strong>talk</strong></td><td><span class="ipa">/tɔːk/</span></td><td><span class="ipa">/tɑːk/</span></td><td>hablar</td></tr>
                <tr><td>L</td><td><strong>half</strong></td><td><span class="ipa">/hɑːf/</span></td><td><span class="ipa">/hæf/</span></td><td>mitad</td></tr>
                <tr><td>L</td><td><strong>calm</strong></td><td><span class="ipa">/kɑːm/</span></td><td><span class="ipa">/kɑːm/</span></td><td>tranquilo</td></tr>
                <tr><td>L</td><td><strong>salmon</strong></td><td><span class="ipa">/ˈsæm.ən/</span></td><td><span class="ipa">/ˈsæm.ən/</span></td><td>salmón</td></tr>
                <tr><td>L</td><td><strong>would</strong></td><td><span class="ipa">/wʊd/</span></td><td><span class="ipa">/wʊd/</span></td><td>condicional</td></tr>
                <tr><td>L</td><td><strong>should</strong></td><td><span class="ipa">/ʃʊd/</span></td><td><span class="ipa">/ʃʊd/</span></td><td>debería</td></tr>
                <tr><td>L</td><td><strong>could</strong></td><td><span class="ipa">/kʊd/</span></td><td><span class="ipa">/kʊd/</span></td><td>podría</td></tr>
                <tr><td>L</td><td><strong>yolk</strong></td><td><span class="ipa">/jəʊk/</span></td><td><span class="ipa">/joʊk/</span></td><td>yema</td></tr>
                <tr><td>L</td><td><strong>palm</strong></td><td><span class="ipa">/pɑːm/</span></td><td><span class="ipa">/pɑːm/</span></td><td>palma</td></tr>
                <tr><td>L</td><td><strong>chalk</strong></td><td><span class="ipa">/tʃɔːk/</span></td><td><span class="ipa">/tʃɑːk/</span></td><td>tiza</td></tr>
                <tr><td>W</td><td><strong>write</strong></td><td><span class="ipa">/raɪt/</span></td><td><span class="ipa">/raɪt/</span></td><td>escribir</td></tr>
                <tr><td>W</td><td><strong>wrong</strong></td><td><span class="ipa">/rɒŋ/</span></td><td><span class="ipa">/rɑːŋ/</span></td><td>equivocado</td></tr>
                <tr><td>W</td><td><strong>answer</strong></td><td><span class="ipa">/ˈɑːn.sə/</span></td><td><span class="ipa">/ˈæn.sɚ/</span></td><td>respuesta</td></tr>
                <tr><td>W</td><td><strong>sword</strong></td><td><span class="ipa">/sɔːd/</span></td><td><span class="ipa">/sɔːrd/</span></td><td>espada</td></tr>
                <tr><td>G</td><td><strong>sign</strong></td><td><span class="ipa">/saɪn/</span></td><td><span class="ipa">/saɪn/</span></td><td>señal; firmar</td></tr>
                <tr><td>G</td><td><strong>foreign</strong></td><td><span class="ipa">/ˈfɒr.ən/</span></td><td><span class="ipa">/ˈfɔːr.ən/</span></td><td>extranjero</td></tr>
                <tr><td>G</td><td><strong>gnome</strong></td><td><span class="ipa">/nəʊm/</span></td><td><span class="ipa">/noʊm/</span></td><td>gnomo</td></tr>
                <tr><td>H</td><td><strong>hour</strong></td><td><span class="ipa">/aʊə/</span></td><td><span class="ipa">/aʊr/</span></td><td>hora</td></tr>
                <tr><td>H</td><td><strong>honest</strong></td><td><span class="ipa">/ˈɒn.ɪst/</span></td><td><span class="ipa">/ˈɑː.nɪst/</span></td><td>honesto</td></tr>
                <tr><td>H</td><td><strong>honour / honor</strong></td><td><span class="ipa">/ˈɒn.ə/</span></td><td><span class="ipa">/ˈɑː.nɚ/</span></td><td>honor</td></tr>
                <tr><td>T</td><td><strong>listen</strong></td><td><span class="ipa">/ˈlɪs.ən/</span></td><td><span class="ipa">/ˈlɪs.ən/</span></td><td>escuchar</td></tr>
                <tr><td>T</td><td><strong>castle</strong></td><td><span class="ipa">/ˈkɑː.səl/</span></td><td><span class="ipa">/ˈkæs.əl/</span></td><td>castillo</td></tr>
                <tr><td>T</td><td><strong>often</strong></td><td><span class="ipa">/ˈɒf.ən/ o /ˈɒf.tən/</span></td><td><span class="ipa">/ˈɑː.fən/ o /ˈɑːf.tən/</span></td><td>a menudo</td></tr>
                <tr><td>T</td><td><strong>Christmas</strong></td><td><span class="ipa">/ˈkrɪs.məs/</span></td><td><span class="ipa">/ˈkrɪs.məs/</span></td><td>Navidad</td></tr>
                <tr><td>P</td><td><strong>psychology</strong></td><td><span class="ipa">/saɪˈkɒl.ə.dʒi/</span></td><td><span class="ipa">/saɪˈkɑː.lə.dʒi/</span></td><td>psicología</td></tr>
                <tr><td>P</td><td><strong>receipt</strong></td><td><span class="ipa">/rɪˈsiːt/</span></td><td><span class="ipa">/rɪˈsiːt/</span></td><td>recibo, ticket</td></tr>
                <tr><td>D</td><td><strong>Wednesday</strong></td><td><span class="ipa">/ˈwenz.deɪ/</span></td><td><span class="ipa">/ˈwenz.deɪ/</span></td><td>miércoles</td></tr>
                <tr><td>D</td><td><strong>handsome</strong></td><td><span class="ipa">/ˈhæn.səm/</span></td><td><span class="ipa">/ˈhæn.səm/</span></td><td>guapo</td></tr>
                <tr><td>U</td><td><strong>guess</strong></td><td><span class="ipa">/ɡes/</span></td><td><span class="ipa">/ɡes/</span></td><td>adivinar, suponer</td></tr>
                <tr><td>U</td><td><strong>guitar</strong></td><td><span class="ipa">/ɡɪˈtɑː/</span></td><td><span class="ipa">/ɡɪˈtɑːr/</span></td><td>guitarra</td></tr>
                <tr><td>U</td><td><strong>build</strong></td><td><span class="ipa">/bɪld/</span></td><td><span class="ipa">/bɪld/</span></td><td>construir</td></tr>
                </tbody>
                </table>
                <h2 id="b-muda">B muda: bomb, comb, climb, doubt y debt</h2>
                <p>La B suele ser muda en dos posiciones. La primera es al final de palabra, detrás de M: <strong>-mb</strong>. En <em>bomb</em>, <em>tomb</em>, <em>comb</em>, <em>climb</em>, <em>thumb</em> (pulgar) o <em>lamb</em> (cordero), la B final no se pronuncia. Si la marcas, la palabra suena artificial y cuesta reconocerla.</p>
                <p>La segunda es delante de T: <em>doubt</em>, <em>debt</em> y <em>subtle</em> (sutil). Curiosidad: la B de <em>bomb</em> vuelve a sonar en <em>bombard</em>, porque ya no está al final. Practica con <a href="/audio/bomb-tomb-comb.html">bomb, tomb y comb</a>: las tres terminan en sonido <span class="ipa">/m/</span>, sin rastro de B.</p>
                <h2 id="k-muda">K muda: know, knife, knee</h2>
                <p>Regla muy fiable: si una palabra empieza por <strong>kn-</strong>, la K no se pronuncia. <em>Know</em>, <em>knife</em>, <em>knee</em>, <em>knock</em> (llamar a la puerta), <em>knight</em> (caballero) y <em>knowledge</em> (conocimiento) empiezan con sonido <span class="ipa">/n/</span>. Por eso <em>know</em> suena igual que <em>no</em>, y <em>knight</em> igual que <em>night</em>.</p>
                <h2 id="l-muda">L muda: walk, talk, would, should</h2>
                <p>En palabras como <em>walk</em>, <em>talk</em>, <em>half</em>, <em>calm</em>, <em>salmon</em>, <em>would</em>, <em>should</em>, <em>could</em>, <em>yolk</em>, <em>palm</em> y <em>chalk</em>, la L no se pronuncia como esperaríamos desde el español.</p>
                <p>El error típico es intentar meter una L clara porque la vemos escrita. En <em>walk</em> y <em>talk</em>, esa L desaparece y lo que importa es la vocal. En <em>would</em>, <em>should</em> y <em>could</em>, también: riman con <em>good</em>. Los patrones que conviene vigilar son <strong>-alk</strong>, <strong>-alm</strong>, <strong>-alf</strong>, <strong>-ould</strong> y <strong>-olk</strong>.</p>
                <p>Cuidado con generalizar: en <em>milk</em>, <em>film</em>, <em>cold</em> o <em>help</em> la L sí suena. Y en Estados Unidos algunos hablantes pronuncian una L ligera en <em>calm</em> o <em>palm</em>; las dos versiones se entienden.</p>
                <p>Practica con el audio de <a href="/audio/walk-talk-half-calm-salmon-would-should-yolk-palm-chalk-walkie-talkie.html">walk, talk, half, calm, salmon, would, should, yolk, palm, chalk y walkie-talkie</a>, y oye <em>could</em>, <em>should</em> y <em>would</em> dentro de una expresión en <a href="/audio/could-have-should-have-would-have.html">could have, should have, would have</a>.</p>
                <h2 id="w-muda">W muda: write, wrong, answer, sword</h2>
                <p>Igual que con <em>kn-</em>, cuando una palabra empieza por <strong>wr-</strong> la W no suena: <em>write</em>, <em>wrong</em>, <em>wrist</em> (muñeca), <em>wrap</em> (envolver). <em>Write</em> y <em>right</em> se pronuncian igual. Fuera de ese patrón, también es muda en <em>answer</em>, <em>sword</em> y <em>two</em>, y en <em>who</em>, <em>whose</em> y <em>whole</em>, que empiezan con sonido <span class="ipa">/h/</span>.</p>
                <h2 id="g-muda">G muda: sign, foreign, gnome</h2>
                <p>La G suele callarse en el grupo <strong>gn</strong>, tanto al principio (<em>gnome</em>) como al final: <em>sign</em>, <em>design</em>, <em>foreign</em>, <em>reign</em> (reinado), <em>champagne</em>. Lo curioso es que en otras palabras de la misma familia la G reaparece: <em>sign</em> no la pronuncia, pero <em>signature</em> y <em>signal</em>, sí.</p>
                <p>Y si te preguntas por la GH de <em>light</em>, <em>night</em> o <em>though</em>, tiene su propio caos: lo explicamos en <a href="/articulos/palabras-ough-pronunciacion-ingles.html">las palabras con -ough</a>.</p>
                <h2 id="h-muda">H muda: hour, honest, honour</h2>
                <p>Este grupo es pequeño, pero se nota mucho porque afecta al artículo. En <em>hour</em>, <em>honest</em>, <em>honour</em> (<em>honor</em> en EE. UU.) y <em>heir</em> (heredero), la H no suena y la palabra empieza por vocal. Por eso se dice <em>an hour</em> y <em>an honest person</em>, igual que <em>an apple</em>.</p>
                <div class="lesson-box"><strong>Ojo, españoles:</strong> nuestro problema con la H suele ser el contrario. La mayoría de las H inglesas sí suenan, como una aspiración suave, mucho más ligera que nuestra J. Practícalo con <a href="/audio/hello-hard.html">hello y hard</a>.</div>
                <h2 id="t-muda">T muda: listen, castle, often y Christmas</h2>
                <p>La T suele desaparecer en los grupos <strong>-sten</strong> y <strong>-stle</strong>: <em>listen</em>, <em>fasten</em> (abrocharse), <em>castle</em>, <em>whistle</em> (silbar). También en <em>Christmas</em> y en <em>mortgage</em> (hipoteca).</p>
                <p><em>Often</em> es un caso especial: existen las dos pronunciaciones, sin T y con T (las tienes en la tabla). Las dos son correctas y se oyen a ambos lados del Atlántico, así que elige una y no te agobies.</p>
                <p>Practica <em>listen</em> con la serie <a href="/audio/light-love-listen-like-late-learn-laugh.html">light, love, listen, like, late, learn y laugh</a>.</p>
                <h2 id="otras">P, D y U mudas: psychology, Wednesday, guess</h2>
                <p><strong>P muda.</strong> Al principio de palabra, el grupo <strong>ps-</strong> suena <span class="ipa">/s/</span>: <em>psychology</em>, <em>psychologist</em>. También es muda en <em>receipt</em> (el ticket de compra) y en <em>cupboard</em> (armario), que muchos españoles leen “cup-board” cuando en realidad suena <span class="ipa">/ˈkʌb.əd/</span> en británico y <span class="ipa">/ˈkʌb.ɚd/</span> en americano.</p>
                <p><strong>D muda.</strong> <em>Wednesday</em> tiene dos sílabas, no tres: nada de “wed-nes-dei”. En <em>handsome</em> la D tampoco suena.</p>
                <p><strong>U muda.</strong> Detrás de G, la U muchas veces solo sirve para que la G suene dura, como en <em>guerra</em>: <em>guess</em>, <em>guest</em>, <em>guitar</em>, <em>guide</em>. En <em>build</em>, <em>building</em> y <em>biscuit</em>, la U tampoco suena.</p>
                <div class="lesson-box"><strong>Bonus:</strong> la N de <em>autumn</em> y <em>column</em> y la C de <em>muscle</em> y <em>scissors</em> tampoco suenan.</div>
                <h2 id="practica">Ejercicio: ¿qué letra no se pronuncia?</h2>
                <p>Primero, la rutina que funciona:</p>
                <ol>
                <li>Lee la palabra, pero tacha mentalmente la letra muda.</li>
                <li>Escucha el audio sin mirar la pantalla.</li>
                <li>Repite la serie completa varias veces, sin añadir la letra escrita.</li>
                <li>Usa una frase corta: <em>I would walk there</em>, <em>talk to me</em>, <em>comb your hair</em>, <em>I know the answer</em>.</li>
                </ol>
                <p>Ahora ponte a prueba. Di cada palabra en voz alta antes de abrir la respuesta.</p>
                <details class="exercise"><summary>thumb</summary><p>La <strong>B</strong>: <span class="ipa">/θʌm/</span> (UK y US). Patrón <em>-mb</em>, como <em>comb</em>.</p></details>
                <details class="exercise"><summary>knock</summary><p>La <strong>K</strong>: UK <span class="ipa">/nɒk/</span>, US <span class="ipa">/nɑːk/</span>. Patrón <em>kn-</em>.</p></details>
                <details class="exercise"><summary>folk</summary><p>La <strong>L</strong>: UK <span class="ipa">/fəʊk/</span>, US <span class="ipa">/foʊk/</span>. Patrón <em>-olk</em>, como <em>yolk</em>.</p></details>
                <details class="exercise"><summary>design</summary><p>La <strong>G</strong>: <span class="ipa">/dɪˈzaɪn/</span> (UK y US). Patrón <em>-gn</em>.</p></details>
                <details class="exercise"><summary>cupboard</summary><p>La <strong>P</strong>: UK <span class="ipa">/ˈkʌb.əd/</span>, US <span class="ipa">/ˈkʌb.ɚd/</span>.</p></details>
                <details class="exercise"><summary>milk (trampa)</summary><p><strong>Ninguna.</strong> Aquí la L sí suena: <span class="ipa">/mɪlk/</span> (UK y US).</p></details>
                <details class="exercise"><summary>¿A hour o an hour?</summary><p><strong>An hour</strong>, porque la H es muda y la palabra empieza por sonido vocálico.</p></details>
                <p>Las letras mudas no se aprenden de una sentada: se fijan escuchando. Si una palabra te traiciona, apúntala con su IPA y repítela en una frase hasta que te salga sola. Para seguir, repasa las <a href="/articulos/palabras-ingles-mal-pronunciadas.html">palabras en inglés que los españoles pronuncian mal</a>.</p>
        """,
    },
    {
        "slug": "como-decir-de-nada-en-ingles",
        "category": "Conversación",
        "title": "Cómo decir de nada en inglés: you’re welcome, no problem, no worries y más",
        "seo_title": "De nada en inglés: formal, coloquial y británico",
        "description": "Cómo decir de nada en inglés según el contexto: you’re welcome, no problem, no worries, not at all, my pleasure... Tabla con registro, país y matiz.",
        "lede": "You’re welcome es correcto, pero no es la única respuesta. En inglés real eliges según cercanía, contexto, nivel de formalidad y hasta país.",
        "reading": "7 minutos",
        "published": "2026-06-28",
        "toc": [
            ("basicas", "Formas básicas"),
            ("tabla", "Tabla completa"),
            ("matices", "Matices"),
            ("formal", "Contextos formales"),
            ("coloquial", "Coloquial y británico"),
            ("practica", "Práctica"),
        ],
        "related": [
            "how-are-you-respuestas-ingles",
            "sure-en-ingles",
            "i-mean-en-ingles",
        ],
        "quick_answer": "<strong>De nada en inglés</strong> se dice <em>you’re welcome</em>, la forma neutra que vale en cualquier contexto. En el día a día también son muy naturales <em>no problem</em>, <em>no worries</em> y <em>anytime</em>; en contextos formales, <em>my pleasure</em> o <em>happy to help</em>; y en inglés británico se oye mucho <em>not at all</em>.",
        "faq": [
            ("¿Cómo se dice de nada en inglés británico?", "En Reino Unido son muy comunes <em>not at all</em>, <em>no worries</em>, <em>no problem</em> y <em>you’re welcome</em>. <em>Cheers</em> también se oye mucho, pero significa sobre todo “gracias”. En Irlanda es muy típico <em>no bother</em>."),
            ("¿Es de mala educación decir no problem?", "Para la mayoría de hablantes no: es una respuesta amable y muy común. Algunas personas, a menudo mayores, la ven menos cortés que <em>you’re welcome</em> en contextos de servicio, así que con clientes o desconocidos <em>you’re welcome</em> o <em>my pleasure</em> son la opción más segura."),
            ("¿Qué diferencia hay entre you’re welcome y welcome?", "<em>You’re welcome</em> significa “de nada”. <em>Welcome</em> solo significa “bienvenido”, como en <em>Welcome to Madrid</em>. Responder <em>Welcome!</em> a un <em>thank you</em> es un error típico de hispanohablantes."),
            ("¿Qué significa my pleasure?", "Significa “es un placer” o “un placer”, y se usa como un “de nada” cálido y profesional. Es muy habitual en hostelería y atención al cliente."),
            ("¿Not at all significa de nada?", "Sí, como respuesta a <em>thank you</em> equivale a “no hay de qué”, y es especialmente común en inglés británico. En otros contextos significa “en absoluto”: <em>I’m not at all tired</em> (no estoy nada cansado)."),
        ],
        "body": """
                <p>Cuando alguien dice <em>thank you</em>, muchos españoles contestan automáticamente <em>you’re welcome</em>. Es correcto, pero puede sonar demasiado de manual si lo usas para todo.</p>
                <p>En inglés hay varias formas naturales de decir <strong>de nada</strong>. La diferencia no está solo en la traducción, sino en la actitud que transmites y en dónde estás: no responde igual un camarero en Nueva York que una compañera de trabajo en Dublín.</p>
                <h2 id="basicas">¿Cómo se dice de nada en inglés? Las formas básicas</h2>
                <div class="example-grid">
                <div class="mini-card"><strong>You’re welcome</strong><span>Correcto y neutro. Útil cuando quieres sonar claro y educado.</span></div>
                <div class="mini-card"><strong>No problem</strong><span>Muy común en situaciones cotidianas. Transmite que no ha supuesto molestia.</span></div>
                <div class="mini-card"><strong>No worries</strong><span>Natural e informal. Equivale a “no te preocupes”.</span></div>
                <div class="mini-card"><strong>Anytime</strong><span>Suena disponible: “cuando quieras”. Muy útil si ayudarías de nuevo.</span></div>
                </div>
                <p>Con estas cuatro ya puedes responder bien en casi cualquier situación. Pero hay más, y cada una tiene su matiz.</p>
                <h2 id="tabla">Tabla: formas de decir de nada en inglés según registro y país</h2>
                <p>La columna de países indica dónde se oye más cada expresión, no dónde es obligatoria: todas se entienden en cualquier país de habla inglesa.</p>
                <table class="data-table">
                <thead><tr><th>Expresión</th><th>Registro</th><th>Dónde es habitual</th><th>Matiz</th></tr></thead>
                <tbody>
                <tr><td>You’re welcome</td><td>Neutro</td><td>En todas partes; muy típica en EE. UU.</td><td>La respuesta estándar. Con <em>very</em> suena más cálida.</td></tr>
                <tr><td>No problem</td><td>Informal / neutro</td><td>En todas partes</td><td>“Sin problema”: no te ha costado nada.</td></tr>
                <tr><td>No worries</td><td>Informal</td><td>Australia, Reino Unido, Irlanda; cada vez más en EE. UU.</td><td>Relajada: “no te preocupes”.</td></tr>
                <tr><td>Not at all</td><td>Neutro / formal</td><td>Más británica</td><td>“No hay de qué”, educada y discreta.</td></tr>
                <tr><td>Don’t mention it</td><td>Neutro</td><td>En todas partes</td><td>“Ni lo menciones”; algo tradicional.</td></tr>
                <tr><td>My pleasure</td><td>Formal</td><td>Hostelería, atención al cliente</td><td>“Es un placer”; cálida y profesional.</td></tr>
                <tr><td>Anytime</td><td>Informal</td><td>En todas partes</td><td>“Cuando quieras”: lo volverías a hacer.</td></tr>
                <tr><td>Happy to help</td><td>Neutro / profesional</td><td>Emails, trabajo, atención al cliente</td><td>Útil y amable.</td></tr>
                <tr><td>It was nothing</td><td>Informal</td><td>En todas partes</td><td>“No fue nada”; le quitas importancia.</td></tr>
                <tr><td>Sure</td><td>Muy informal</td><td>Sobre todo EE. UU.</td><td>“Claro”, casi un encogimiento de hombros.</td></tr>
                <tr><td>You bet</td><td>Muy informal</td><td>EE. UU.</td><td>Entusiasta: “¡no hay de qué!”.</td></tr>
                <tr><td>No prob / No probs</td><td>Muy informal</td><td><em>No prob</em>, más en EE. UU.; <em>no probs</em>, en Reino Unido y Australia</td><td>Versión acortada de <em>no problem</em>.</td></tr>
                <tr><td>No bother</td><td>Informal</td><td>Irlanda y Escocia</td><td>“Ninguna molestia”.</td></tr>
                <tr><td>Cheers</td><td>Informal</td><td>Reino Unido, Irlanda, Australia</td><td>Ojo: sobre todo significa “gracias” (y “adiós”).</td></tr>
                </tbody>
                </table>
                <h2 id="matices">Matices que cambian la impresión</h2>
                <p><em>No problem</em> y <em>no worries</em> minimizan el favor. Son buenas opciones cuando alguien te agradece algo pequeño: sujetar una puerta, enviar un enlace o responder una duda rápida.</p>
                <p><em>Anytime</em> va un paso más allá: no solo dices que no pasa nada, sino que estás dispuesto a repetirlo. Por eso funciona muy bien con amigos, compañeros de trabajo y situaciones amables.</p>
                <h3>El debate de no problem</h3>
                <p>Hay quien considera <em>no problem</em> menos educado que <em>you’re welcome</em>, sobre todo algunas personas mayores y en contextos de servicio. Su argumento es que da a entender que ayudar podría haber sido un problema. Para la mayoría de hablantes, y en especial los más jóvenes, es una respuesta amable y normal. Si atiendes a clientes o no conoces a la persona, <em>you’re welcome</em> o <em>my pleasure</em> no fallan.</p>
                <h3>Cuando you’re welcome es irónico</h3>
                <p>Si haces algo por alguien y no te da las gracias, puedes soltar un <em>You’re welcome!</em> con retintín, como nuestro “¡de nada, eh!”. El tono lo es todo.</p>
                <div class="lesson-box"><strong>Error típico:</strong> responder solo <em>Welcome</em>. Sin el <em>you’re</em>, significa “bienvenido”, no “de nada”.</div>
                <h2 id="formal">De nada en inglés formal: trabajo, clientes y emails</h2>
                <p><em>My pleasure</em> significa algo parecido a “un placer”. Es más cálido y profesional, especialmente en atención al cliente. <em>You’re very welcome</em> funciona cuando la otra persona te ha dado las gracias con mucha intensidad y quieres responder al mismo nivel.</p>
                <p><em>Happy to help</em> también es excelente en emails y trabajo: suena útil, amable y natural. Algunas fórmulas para correo:</p>
                <ul>
                <li><em>You’re very welcome. Let me know if you need anything else.</em> → De nada. Avísame si necesitas algo más.</li>
                <li><em>Happy to help!</em> → ¡Encantado de ayudar!</li>
                <li><em>Glad I could help.</em> → Me alegro de haber podido ayudar.</li>
                <li><em>Not at all, it was a pleasure.</em> → No hay de qué, ha sido un placer.</li>
                </ul>
                <p>En un email no hace falta responder a cada <em>thanks</em>: si la conversación ya está cerrada, a veces lo más natural es no contestar.</p>
                <h2 id="coloquial">De nada en inglés coloquial y británico</h2>
                <p>En Reino Unido, Irlanda y Australia oirás mucho <em>no worries</em>, y en Gran Bretaña también <em>not at all</em>, que es educado sin ser rígido. En Irlanda, <em>no bother</em> o <em>no bother at all</em> es de lo más normal. En algunas zonas de Inglaterra incluso se responde <em>you’re alright</em>, que ahí viene a ser “nada, tranquilo”.</p>
                <p>¿Y <em>cheers</em>? En el inglés británico informal es, sobre todo, una forma de dar las gracias (y también de despedirse o brindar). No es exactamente “de nada”, pero aparece constantemente en el intercambio: <em>Cheers, mate.</em> / <em>No worries.</em> Si alguien te da las gracias con un <em>cheers</em>, basta con un <em>no worries</em> o una sonrisa.</p>
                <p>En Estados Unidos, el registro coloquial va por otro lado: <em>sure</em>, <em>you bet</em>, <em>you got it</em> o <em>no prob</em>. Si te interesa todo lo que puede significar <em>sure</em> según el tono, lo tienes en <a href="/articulos/sure-en-ingles.html">sure en inglés</a>.</p>
                <h2 id="practica">Qué responder en cada situación</h2>
                <ol>
                <li>Favor pequeño entre amigos: <em>No problem</em> o <em>No worries</em>.</li>
                <li>Quieres mostrar disponibilidad: <em>Anytime</em>.</li>
                <li>Cliente o situación profesional: <em>My pleasure</em> o <em>Happy to help</em>.</li>
                <li>Agradecimiento muy sincero: <em>You’re very welcome</em>.</li>
                <li>Estás en Londres o en Dublín y quieres sonar local: <em>Not at all</em>, <em>No worries</em> o <em>No bother</em>.</li>
                </ol>
                <p>Ponte a prueba: ¿qué responderías tú?</p>
                <details class="exercise"><summary>Un cliente del hotel te da las gracias por recomendarle un restaurante.</summary><p><em>My pleasure</em> o <em>You’re very welcome</em>. En hostelería, <em>my pleasure</em> es muy habitual.</p></details>
                <details class="exercise"><summary>Un compañero te da las gracias por pasarle un archivo.</summary><p><em>No problem</em>, <em>No worries</em> o <em>Sure</em>. Favor pequeño, respuesta ligera.</p></details>
                <details class="exercise"><summary>Tu amiga te agradece que la llevaras al aeropuerto a las cinco de la mañana.</summary><p><em>Anytime!</em> o <em>Don’t mention it</em>. Dejas claro que lo harías otra vez.</p></details>
                <details class="exercise"><summary>Te dicen “Thanks!” y respondes “Welcome!”. ¿Está bien?</summary><p>No: <em>welcome</em> solo significa “bienvenido”. Di <em>You’re welcome</em>.</p></details>
                <div class="lesson-box"><strong>Evita traducir literalmente:</strong> no necesitas buscar una versión exacta de “de nada”. Elige la respuesta que encaje con la relación y el tono.</div>
                <p>Escoge dos o tres y úsalas esta semana. Igual que con <a href="/articulos/how-are-you-respuestas-ingles.html">las respuestas a How are you</a>, el objetivo no es la frase perfecta, sino tener varias opciones naturales a mano. Y para entrenar el oído con más expresiones de conversación, tienes los <a href="/audios.html">audios gratuitos de práctica</a>.</p>
        """,
    },
    {
        "slug": "sure-en-ingles",
        "category": "Conversación",
        "title": "Sure en inglés: significado, usos y expresiones (make sure, not sure, for sure)",
        "seo_title": "Sure significado en español: usos, ejemplos y pronunciación",
        "description": "Qué significa sure en español: seguro, claro, de nada... Y también make sure, not sure, sure thing y for sure, con ejemplos y cómo se pronuncia.",
        "lede": "Sure parece una palabra pequeña, pero cambia mucho según el contexto y la entonación. Ahí está la parte importante.",
        "reading": "7 minutos",
        "published": "2026-06-28",
        "toc": [
            ("significados", "Significados"),
            ("make-sure", "Make sure"),
            ("not-sure", "Not sure"),
            ("sure-thing", "Sure thing y for sure"),
            ("tono", "El tono"),
            ("pronunciacion", "Pronunciación"),
            ("ejemplos", "Ejercicio"),
        ],
        "related": [
            "como-decir-de-nada-en-ingles",
            "i-mean-en-ingles",
            "actual-vs-actually",
            "how-are-you-respuestas-ingles",
        ],
        "quick_answer": "<strong>Sure</strong> significa <em>seguro</em> como adjetivo (<em>I’m sure</em>, estoy seguro), pero en conversación suele ser un <em>sí, claro</em> informal (<em>Can you help me? Sure!</em>). También forma expresiones muy comunes: <em>make sure</em> (asegurarse), <em>not sure</em> (no estar seguro), <em>sure thing</em> (claro que sí) y <em>for sure</em> (seguro, sin duda).",
        "faq": [
            ("¿Qué significa make sure?", "<em>Make sure</em> significa “asegurarse (de que)”. Por ejemplo, <em>Make sure you lock the door</em> es “asegúrate de cerrar con llave”. Después de <em>make sure</em> se suele usar presente, aunque hables del futuro."),
            ("¿Qué significa sure thing?", "Es una respuesta coloquial, sobre todo americana, que significa “claro que sí” o “hecho”. Se usa para aceptar una petición (<em>Can you call me later? Sure thing</em>) y también como respuesta informal a <em>thanks</em>."),
            ("¿Qué diferencia hay entre sure y of course?", "Las dos pueden significar “claro”, pero <em>sure</em> es más relajado y <em>of course</em> más enfático, como “¡por supuesto!”. Respondiendo a una pregunta de información, <em>of course</em> a veces puede sonar a “es obvio”, así que <em>sure</em> suele ser más neutro."),
            ("¿Surely significa seguramente?", "No exactamente. <em>Surely</em> expresa que algo te parece evidente o que te sorprende lo contrario: <em>Surely you’re joking</em> (no lo dirás en serio). Para “seguramente” con el sentido de “probablemente”, se usa <em>probably</em>."),
            ("¿Cómo se pronuncia sure en inglés?", "Empieza por el sonido <span class=\"ipa\">/ʃ/</span> de <em>she</em>, no por S. En inglés americano es <span class=\"ipa\">/ʃʊr/</span> o <span class=\"ipa\">/ʃɝː/</span>, y en británico <span class=\"ipa\">/ʃɔː/</span> o <span class=\"ipa\">/ʃʊə/</span>."),
        ],
        "body": """
                <p><em>Sure</em> es una de esas palabras que escuchas constantemente en inglés hablado. El problema es que no tiene una única traducción estable. Puede significar “seguro”, “sí”, “claro”, “de nada” o incluso sonar sarcástico.</p>
                <p>La clave no es memorizar una lista de equivalencias, sino entender qué función cumple en cada frase. Aquí tienes el <strong>significado de sure en español</strong> según el contexto, las expresiones que más se usan (<em>make sure</em>, <em>not sure</em>, <em>sure thing</em>, <em>for sure</em>) y cómo se pronuncia.</p>
                <h2 id="significados">¿Qué significa sure? Los usos más comunes</h2>
                <div class="example-grid">
                <div class="mini-card"><strong>Certeza</strong><span><em>I’m sure it is</em>: estoy seguro de que sí.</span></div>
                <div class="mini-card"><strong>Sí informal</strong><span><em>Do you want coffee? Sure</em>: sí, claro.</span></div>
                <div class="mini-card"><strong>De nada</strong><span><em>Thanks! Sure, no problem</em>: de nada, no pasa nada.</span></div>
                <div class="mini-card"><strong>Énfasis</strong><span><em>It sure is cold</em>: desde luego hace frío.</span></div>
                </div>
                <table class="data-table">
                <thead><tr><th>Uso</th><th>Ejemplo</th><th>Traducción</th></tr></thead>
                <tbody>
                <tr><td>Certeza</td><td>I’m sure she’ll come.</td><td>Estoy seguro de que vendrá.</td></tr>
                <tr><td>Confirmar</td><td>Are you sure?</td><td>¿Estás seguro?</td></tr>
                <tr><td>Sí informal</td><td>Can I sit here? Sure.</td><td>¿Me puedo sentar aquí? Claro.</td></tr>
                <tr><td>Respuesta a <em>thanks</em></td><td>Thanks! Sure.</td><td>¡Gracias! De nada.</td></tr>
                <tr><td>Conceder</td><td>Sure, it’s expensive, but it’s worth it.</td><td>Vale, es caro, pero merece la pena.</td></tr>
                <tr><td>Énfasis (informal)</td><td>It sure is cold today.</td><td>Desde luego, hoy hace frío.</td></tr>
                <tr><td>Recordar algo</td><td>Be sure to call me.</td><td>No te olvides de llamarme.</td></tr>
                </tbody>
                </table>
                <p>Fíjate en las estructuras: <em>be sure of/about something</em> (estar seguro de algo), <em>be sure (that)...</em> (estar seguro de que...) y <em>be sure to</em> + verbo (no olvidarse de hacer algo). El uso enfático (<em>It sure is</em>, <em>I sure hope so</em>) es sobre todo americano y coloquial. Y como respuesta a <em>thanks</em>, <em>sure</em> es otra forma relajada de <a href="/articulos/como-decir-de-nada-en-ingles.html">decir de nada en inglés</a>.</p>
                <h2 id="make-sure">¿Qué significa make sure?</h2>
                <p><em>Make sure</em> significa <strong>asegurarse (de que)</strong> o comprobar. Es de las expresiones más útiles del inglés cotidiano:</p>
                <ul>
                <li><em>Make sure you lock the door.</em> → Asegúrate de cerrar con llave.</li>
                <li><em>I called to make sure everything was OK.</em> → Llamé para asegurarme de que todo iba bien.</li>
                <li><em>Make sure to bring your passport.</em> → No te olvides de traer el pasaporte.</li>
                </ul>
                <p>Detalle gramatical: después de <em>make sure</em> se suele usar presente aunque hables del futuro. Se dice <em>Make sure you arrive on time</em>, no <em>make sure you will arrive</em>. En textos formales verás <em>ensure</em> (garantizar, asegurar): <em>Please ensure that all doors are closed</em>. Y no lo confundas con <em>assure</em>, que es asegurarle algo a alguien: <em>I assure you it’s true</em>.</p>
                <h2 id="not-sure">Not sure, I’m not sure y not so sure</h2>
                <ul>
                <li><em>I’m not sure.</em> → No estoy seguro / No lo sé. Más suave que un <em>I don’t know</em> seco.</li>
                <li><em>Not sure.</em> → Lo mismo, más informal.</li>
                <li><em>I’m not sure if it’s open.</em> → No sé si está abierto. (También con <em>whether</em>.)</li>
                <li><em>I’m not so sure.</em> → Yo no lo tengo tan claro. Sirve para discrepar con educación.</li>
                <li><em>I’m not sure about that.</em> → No lo veo claro.</li>
                </ul>
                <h2 id="sure-thing">Sure thing, for sure y otras expresiones con sure</h2>
                <ul>
                <li><strong>Sure thing:</strong> “claro que sí”, “hecho”. Muy coloquial, sobre todo en EE. UU.; vale para aceptar algo o para responder a un <em>thanks</em>. <em>Can you send me the file? Sure thing.</em> Ojo: <em>a sure thing</em> es “algo seguro”, una apuesta sin riesgo.</li>
                <li><strong>For sure:</strong> “seguro”, “sin duda”. <em>She’ll be there for sure</em> (seguro que estará). En negativa, <em>I don’t know for sure</em> (no lo sé con certeza). Sola, <em>For sure!</em> es un “¡claro!” entusiasta.</li>
                <li><strong>That’s for sure:</strong> “eso seguro”, “eso está claro”.</li>
                <li><strong>Sure enough:</strong> “efectivamente”, “como era de esperar”. <em>He said it would rain and, sure enough, it did.</em></li>
                <li><strong>Surely:</strong> cuidado, no es exactamente “seguramente”. Expresa que algo te parece obvio o que te sorprendería lo contrario: <em>Surely you don’t believe that!</em> (¡no me digas que te lo crees!). Para “seguramente” en el sentido de “probablemente”, usa <em>probably</em>.</li>
                </ul>
                <h2 id="tono">El tono decide mucho</h2>
                <p>Un <em>sure!</em> alegre puede sonar amistoso y dispuesto. Un <em>sure</em> plano, bajo o lento puede sonar como aceptación sin ganas. Y con el tono adecuado, también puede transmitir sarcasmo: <em>Sure, I’d love to work all weekend</em>. Lo mismo pasa con <em>Oh, sure...</em>, que muchas veces significa “sí, hombre, claro”.</p>
                <p>Por eso conviene escuchar la palabra dentro de frases reales. El significado literal te da una parte; la entonación te da la otra.</p>
                <h2 id="pronunciacion">¿Cómo se pronuncia sure?</h2>
                <p>Lo primero: <em>sure</em> empieza por el sonido <span class="ipa">/ʃ/</span>, el de <em>she</em> o <em>shoe</em>, no por una S. Es uno de los pocos casos, junto con <em>sugar</em>, en que una S inicial suena así, y decir “sur” es el error típico.</p>
                <ul>
                <li><strong>Inglés americano (US):</strong> <span class="ipa">/ʃʊr/</span>, aunque muchos hablantes dicen <span class="ipa">/ʃɝː/</span>, parecido a “sher”.</li>
                <li><strong>Inglés británico (UK):</strong> <span class="ipa">/ʃɔː/</span>, hoy muy habitual, o <span class="ipa">/ʃʊə/</span>, más tradicional.</li>
                </ul>
                <p>Con la pronunciación británica <span class="ipa">/ʃɔː/</span>, <em>sure</em> suena igual que <em>shore</em> (orilla). Puedes practicar <em>shore</em> con el audio de <a href="/audio/door-floor-score-shore-roar-soar.html">door, floor, score, shore, roar y soar</a>.</p>
                <h2 id="errores">Errores típicos con sure</h2>
                <p>El primer error es traducir <em>sure</em> siempre como “seguro”. En muchas conversaciones solo equivale a un “sí” relajado. El segundo es usarlo en contextos demasiado formales donde quedaría mejor una respuesta completa, como <em>certainly</em> u <em>of course</em>.</p>
                <p>El tercero es el contrario: usar <em>sure</em> para todo lo que en español es “seguro”. Nuestra palabra tiene varios equivalentes:</p>
                <table class="data-table">
                <thead><tr><th>En español</th><th>En inglés</th><th>Ejemplo</th></tr></thead>
                <tbody>
                <tr><td>Seguro (sin dudas)</td><td>sure</td><td>I’m sure. (Estoy seguro.)</td></tr>
                <tr><td>Seguro (sin peligro)</td><td>safe</td><td>This area is safe. (Esta zona es segura.)</td></tr>
                <tr><td>Seguro (protegido)</td><td>secure</td><td>a secure password (una contraseña segura)</td></tr>
                <tr><td>Seguro (póliza)</td><td>insurance</td><td>car insurance (el seguro del coche)</td></tr>
                </tbody>
                </table>
                <div class="lesson-box"><strong>Regla práctica:</strong> si alguien te ofrece algo informalmente, <em>sure</em> puede servir. Si estás escribiendo un email formal, normalmente conviene una frase más explícita.</div>
                <h2 id="ejemplos">Ejemplos y ejercicio rápido</h2>
                <ol>
                <li><em>Are you sure?</em> → ¿Estás seguro?</li>
                <li><em>Sure, no problem.</em> → Claro, sin problema / de nada.</li>
                <li><em>It sure looks expensive.</em> → Desde luego parece caro.</li>
                <li><em>Sure...</em> con tono seco → Sí, pero no muy convencido.</li>
                </ol>
                <p>Ahora tú: ¿cómo lo dirías en inglés?</p>
                <details class="exercise"><summary>Asegúrate de que tienes las llaves.</summary><p><em>Make sure you have the keys.</em> Presente después de <em>make sure</em>.</p></details>
                <details class="exercise"><summary>No sé si viene.</summary><p><em>I’m not sure if he’s coming</em> (o <em>whether</em>). Más natural que <em>I don’t know if</em> cuando dudas.</p></details>
                <details class="exercise"><summary>—¿Me ayudas con esto? —¡Claro!</summary><p><em>Sure!</em> o <em>Sure thing!</em> Respuesta informal y dispuesta.</p></details>
                <details class="exercise"><summary>Esta calle no es segura de noche.</summary><p><em>This street isn’t safe at night.</em> Aquí “seguro” es <em>safe</em>, no <em>sure</em>.</p></details>
                <p>Empieza por los dos usos que más vas a oír, el “sí, claro” y <em>make sure</em>, y presta atención al tono cada vez que alguien te diga <em>sure</em>. Si te interesan otras palabras pequeñas que cambian según el contexto, sigue con <a href="/articulos/i-mean-en-ingles.html">I mean en inglés</a>.</p>
        """,
    },
    {
        "slug": "i-mean-en-ingles",
        "category": "Conversación",
        "title": "I mean en inglés: significado y cómo usar esta muletilla sin sonar raro",
        "seo_title": "I mean significado en español: usos y ejemplos reales",
        "description": "Qué significa I mean en español (o sea, es decir, a ver) y cómo usarlo para aclarar, corregirte o suavizar. Incluye like, you know y kind of.",
        "lede": "I mean no siempre se traduce palabra por palabra. En conversación sirve para aclarar, corregirte, enfatizar, ganar tiempo o suavizar lo que vas a decir.",
        "reading": "6 minutos",
        "published": "2026-06-28",
        "toc": [
            ("significa", "Qué significa"),
            ("usos", "Cinco usos"),
            ("what-i-mean", "Expresiones con mean"),
            ("muletillas", "Muletillas parecidas"),
            ("cuidado", "Cuándo evitarlo"),
            ("practica", "Práctica"),
        ],
        "related": [
            "sure-en-ingles",
            "actual-vs-actually",
            "ligar-palabras-ingles",
            "how-are-you-respuestas-ingles",
        ],
        "quick_answer": "<strong>I mean</strong> significa literalmente <em>quiero decir</em>, pero en conversación funciona como <em>o sea</em>, <em>es decir</em> o <em>a ver</em>. Se usa para aclarar lo que acabas de decir, corregirte, suavizar una opinión o dar énfasis. Es una muletilla muy común en inglés hablado; en textos formales, mejor <em>in other words</em> o <em>that is</em>.",
        "faq": [
            ("¿Qué significa I mean it?", "<em>I mean it</em> significa “lo digo en serio”. No es una muletilla: se usa para insistir en que hablas con sinceridad, como en <em>Thank you so much. I mean it</em>."),
            ("¿Es de mala educación decir I mean?", "No. Es una muletilla normal en el inglés hablado y la usan hablantes de todas las edades. El problema es abusar de ella, porque distrae, y usarla en textos formales, donde es mejor <em>in other words</em> o <em>that is</em>."),
            ("¿Qué diferencia hay entre I mean e I meant?", "<em>I mean</em> aclara o corrige en el momento: <em>See you Tuesday. I mean, Thursday</em>. <em>I meant</em> se refiere a lo que querías decir antes: <em>Sorry, I meant Thursday</em> (perdona, quería decir jueves)."),
            ("¿Cómo se dice o sea en inglés?", "Depende de la función. Para aclarar, <em>I mean</em> o <em>in other words</em>; para sacar una conclusión, <em>so</em>; y como relleno informal, muchos hablantes usan <em>like</em>, que se parece a nuestro “en plan”."),
            ("¿Qué significa you know what I mean?", "Significa “¿me entiendes?” o “¿sabes lo que te digo?”. Se usa para buscar la complicidad de quien escucha y, en el habla rápida, a menudo se acorta a <em>know what I mean?</em>"),
        ],
        "body": """
                <p><em>I mean</em> aparece muchísimo en inglés hablado. La traducción más directa sería “quiero decir”, pero en la vida real funciona como una herramienta de conversación, no solo como una frase traducible.</p>
                <p>Los nativos la usan para corregirse, matizar, pensar en voz alta o preparar una frase delicada. Si entiendes qué hace en cada caso, la reconocerás en series y conversaciones, y podrás usarla sin que suene forzada.</p>
                <h2 id="significa">¿Qué significa I mean en español?</h2>
                <p>Literalmente, <em>I mean</em> significa “quiero decir”. Pero según el contexto puede equivaler a “o sea”, “es decir”, “a ver”, “bueno”, “la verdad es que” o incluso una pausa mientras piensas.</p>
                <table class="data-table">
                <thead><tr><th>En inglés</th><th>Traducción natural</th></tr></thead>
                <tbody>
                <tr><td>It’s far. I mean, it’s a two-hour drive.</td><td>Está lejos. O sea, son dos horas en coche.</td></tr>
                <tr><td>We need more people. I mean, two more at least.</td><td>Necesitamos más gente. Es decir, dos más como mínimo.</td></tr>
                <tr><td>I mean, it’s not a bad idea.</td><td>A ver, no es mala idea.</td></tr>
                <tr><td>I mean, come on!</td><td>¡Pero bueno, hombre!</td></tr>
                </tbody>
                </table>
                <div class="lesson-box"><strong>Idea útil:</strong> no intentes poner <em>I mean</em> en cada frase. Úsalo cuando realmente estés aclarando, corrigiendo o suavizando algo.</div>
                <p>Un apunte de pronunciación: <em>mean</em> lleva una I larga, <span class="ipa">/miːn/</span> (igual en británico y americano). Si la acortas demasiado, se acerca a <span class="ipa">/mɪn/</span>. Lo explicamos en <a href="/articulos/vocales-ingles-cortas-largas.html">vocales cortas y largas en inglés</a>.</p>
                <h2 id="usos">¿Para qué se usa I mean? Cinco usos con ejemplos</h2>
                <h3>1. Aclarar o ampliar</h3>
                <p><em>The movie was okay. I mean, it wasn’t great.</em> → La peli estuvo bien. O sea, tampoco fue para tanto.</p>
                <h3>2. Corregirte sobre la marcha</h3>
                <p><em>See you on Tuesday. I mean, Thursday!</em> → Nos vemos el martes. ¡Digo, el jueves! Donde en español decimos “digo”, en inglés sale <em>I mean</em>.</p>
                <h3>3. Suavizar una opinión</h3>
                <p><em>I mean, maybe we could try another approach.</em> → A ver, quizá podríamos probar de otra forma. Delante de una crítica o una sugerencia, <em>I mean</em> rebaja el tono.</p>
                <h3>4. Enfatizar o justificar</h3>
                <p><em>I mean, it was really cold.</em> → Es que hacía muchísimo frío. <em>I mean, who does that?</em> → O sea, ¿quién hace eso?</p>
                <h3>5. Ganar tiempo</h3>
                <p><em>I don’t know... I mean... it’s complicated.</em> → No sé... a ver... es complicado. Otra opción muy natural para pensar es <a href="/audio/let-me-see.html">Let me see</a> (“a ver, déjame pensar”).</p>
                <h2 id="what-i-mean">What I mean is, I meant, I mean it: expresiones con mean</h2>
                <table class="data-table">
                <thead><tr><th>Expresión</th><th>Significado</th><th>Ejemplo</th></tr></thead>
                <tbody>
                <tr><td>What I mean is...</td><td>Lo que quiero decir es...</td><td>What I mean is, we need more time.</td></tr>
                <tr><td>I meant...</td><td>Quería decir...</td><td>Sorry, I meant Tuesday, not Thursday.</td></tr>
                <tr><td>(You) know what I mean?</td><td>¿Me entiendes? / ¿Sabes lo que te digo?</td><td>It’s just weird, you know what I mean?</td></tr>
                <tr><td>I see what you mean.</td><td>Entiendo lo que dices.</td><td>I see what you mean, but I disagree.</td></tr>
                <tr><td>What do you mean?</td><td>¿Qué quieres decir? / ¿Cómo que...?</td><td>What do you mean you’re leaving?</td></tr>
                <tr><td>I mean it.</td><td>Lo digo en serio.</td><td>Thank you. I mean it.</td></tr>
                <tr><td>I didn’t mean to.</td><td>No quería / Fue sin querer.</td><td>Sorry, I didn’t mean to wake you.</td></tr>
                </tbody>
                </table>
                <p>No confundas <em>I mean it</em> (lo digo en serio) con la muletilla <em>I mean</em>: ese <em>it</em> lo cambia todo.</p>
                <h2 id="muletillas">I mean, like, you know, kind of: muletillas parecidas</h2>
                <p><em>I mean</em> forma parte de una familia de palabras que dan ritmo a la conversación. Se parecen, pero no son intercambiables:</p>
                <table class="data-table">
                <thead><tr><th>Muletilla</th><th>Para qué sirve</th><th>En español, más o menos</th></tr></thead>
                <tbody>
                <tr><td>I mean</td><td>Aclarar, corregir, suavizar</td><td>o sea, a ver, digo</td></tr>
                <tr><td>like</td><td>Rellenar, aproximar o citar lo que alguien dijo: <em>She was like, “No way!”</em></td><td>en plan, como</td></tr>
                <tr><td>you know</td><td>Buscar complicidad</td><td>¿sabes?, ya sabes</td></tr>
                <tr><td>kind of / sort of</td><td>Suavizar, “más o menos”</td><td>un poco, como que, medio</td></tr>
                <tr><td>basically</td><td>Resumir (a veces sin resumir nada)</td><td>básicamente, total</td></tr>
                <tr><td>actually</td><td>Corregir o contrastar</td><td>en realidad, la verdad es que</td></tr>
                <tr><td>well</td><td>Empezar a responder, ganar un segundo</td><td>bueno, pues</td></tr>
                </tbody>
                </table>
                <p>En el habla rápida, <em>kind of</em> y <em>sort of</em> suelen sonar como <em>kinda</em> y <em>sorta</em>; practícalos con el audio de <a href="/audio/out-of-kind-of-sort-of.html">out of, kind of, sort of</a>. Y si <em>actually</em> te suena a “actualmente”, lee <a href="/articulos/actual-vs-actually.html">actual vs actually</a>: es uno de los falsos amigos más traicioneros.</p>
                <h2 id="cuidado">¿Cuándo evitar I mean? Cómo no abusar de la muletilla</h2>
                <p><em>I mean</em> pertenece sobre todo al inglés hablado. En un email formal, un documento o una presentación escrita, normalmente puedes sustituirlo por frases más limpias: <em>in other words</em>, <em>that is</em>, <em>to clarify</em> o directamente una explicación mejor construida.</p>
                <p>En conversación, el problema no es usarlo, sino abusar. Algunas pistas:</p>
                <ul>
                <li><strong>Una vez por idea, como mucho.</strong> Tres <em>I mean</em> en una frase distraen más que ayudan.</li>
                <li><strong>No empieces todas las respuestas con él.</strong> Puede sonar a que te estás justificando todo el rato.</li>
                <li><strong>Prueba con una pausa.</strong> Un silencio corto suena más seguro que encadenar muletillas.</li>
                <li><strong>Grábate.</strong> Habla un minuto sobre tu día y cuenta cuántas veces dices <em>I mean</em>, <em>like</em> o <em>you know</em>.</li>
                <li><strong>En entrevistas y presentaciones,</strong> cámbialo por estructuras más claras: <em>What I mean is...</em> o <em>Let me put it another way</em>.</li>
                </ul>
                <h2 id="practica">Práctica rápida</h2>
                <ol>
                <li>Úsalo para corregirte: <em>I liked it. I mean, I liked the first half</em>.</li>
                <li>Úsalo para suavizar: <em>I mean, we could wait until tomorrow</em>.</li>
                <li>Evita repetirlo tres veces por frase. Una muletilla ayuda; abusar de ella distrae.</li>
                </ol>
                <p>¿Qué función tiene <em>I mean</em> en cada frase?</p>
                <details class="exercise"><summary>“It’s a nice flat. I mean, it’s small, but it’s nice.”</summary><p><strong>Suavizar y matizar:</strong> reconoces un defecto sin quitarle valor al piso.</p></details>
                <details class="exercise"><summary>“Let’s meet at six. I mean, seven.”</summary><p><strong>Corregirte:</strong> equivale a nuestro “digo”.</p></details>
                <details class="exercise"><summary>“I mean, he ate the whole cake. Who does that?”</summary><p><strong>Enfatizar:</strong> subraya lo exagerado de la situación.</p></details>
                <details class="exercise"><summary>“Well... I mean... I’m not sure.”</summary><p><strong>Ganar tiempo:</strong> piensas mientras hablas.</p></details>
                <p>La próxima vez que veas una serie en inglés, fíjate en cuándo aparece <em>I mean</em> y qué está haciendo en la frase. Cuando reconozcas sus funciones, usarlo te saldrá solo, y con moderación.</p>
        """,
    },
    {
        "slug": "fun-vs-funny",
        "category": "Vocabulario",
        "title": "Fun vs funny: la diferencia entre divertido, gracioso y raro",
        "seo_title": "Fun vs funny: diferencia en inglés, ejemplos y ejercicio",
        "description": "Fun o funny: diferencia entre fun (divertido) y funny (gracioso o raro), have fun vs make fun of, more fun vs funnier y ejercicio con soluciones.",
        "lede": "Fun y funny no son intercambiables. Una fiesta puede ser fun; un chiste puede ser funny; y un olor extraño también puede ser funny, aunque no tenga ninguna gracia.",
        "reading": "7 minutos",
        "published": "2026-06-28",
        "toc": [
            ("fun", "Fun"),
            ("funny", "Funny"),
            ("comparacion", "Comparación"),
            ("have-fun", "Have fun y very fun"),
            ("ejercicio", "Ejercicio"),
            ("practica", "Práctica"),
        ],
        "related": [
            "sufijos-ish-wise",
            "make-vs-do",
            "actual-vs-actually",
        ],
        "quick_answer": "<strong>Fun</strong> significa divertido o entretenido, algo con lo que disfrutas (<em>The party was fun</em>). <strong>Funny</strong> significa gracioso, que te hace reír (<em>The film was really funny</em>), y también raro (<em>This milk tastes funny</em>). Una persona <em>fun</em> es buena compañía; una persona <em>funny</em> te hace reír.",
        "faq": [
            ("¿Cuál es la diferencia entre fun y funny?", "<em>Fun</em> se usa para algo que disfrutas, aunque no te haga reír: <em>Skiing is fun</em>. <em>Funny</em> se usa para algo que te hace reír (<em>a funny joke</em>) o que resulta raro (<em>a funny smell</em>)."),
            ("¿Se dice very fun o so much fun?", "La opción más segura es <em>so much fun</em>, <em>a lot of fun</em> o <em>really fun</em>. <em>Very fun</em> se oye cada vez más en inglés informal, sobre todo americano, pero algunos hablantes lo consideran incorrecto."),
            ("¿Cuál es el comparativo de fun?", "El comparativo estándar es <em>more fun</em> y el superlativo <em>the most fun</em>: <em>This game is more fun</em>. <em>Funner</em> y <em>funnest</em> existen en el habla informal, pero se consideran poco correctos."),
            ("¿Qué significa make fun of?", "<em>Make fun of someone</em> significa burlarse de alguien: <em>Don't make fun of her accent</em>. No tiene nada que ver con <em>have fun</em>, que significa pasarlo bien."),
            ("¿Funny puede significar raro?", "Sí. Además de gracioso, <em>funny</em> significa raro o extraño en frases como <em>That's funny</em> (qué raro), <em>It smells funny</em> (huele raro) o <em>I feel funny</em> (me encuentro raro)."),
        ],
        "body": """
                <p>En español usamos “divertido” para muchas cosas: una fiesta, una persona, un plan, un juego o una película. En inglés, esa comodidad nos puede llevar a mezclar <em>fun</em> y <em>funny</em>, y a decir que una boda fue <em>very funny</em> cuando lo que queríamos decir es que nos lo pasamos genial.</p>
                <p>La diferencia es sencilla si separas dos ideas: disfrute y risa. Y luego añades una tercera que pilla a mucha gente por sorpresa: <em>funny</em> también puede significar raro.</p>

                <h2 id="fun">¿Qué significa fun? Diversión o experiencia agradable</h2>
                <p><em>Fun</em> se usa cuando algo es entretenido, disfrutable o lo pasaste bien. No tiene por qué hacerte reír. Una excursión, una fiesta, una clase o un juego pueden ser <em>fun</em>.</p>
                <div class="example-grid">
                <div class="mini-card"><strong>We had fun</strong><span>Nos lo pasamos bien.</span></div>
                <div class="mini-card"><strong>That was a fun game</strong><span>Fue un juego divertido.</span></div>
                <div class="mini-card"><strong>Have fun!</strong><span>¡Pásalo bien! Despedida típica antes de un plan.</span></div>
                <div class="mini-card"><strong>Just for fun</strong><span>Por diversión, por gusto: <em>I play the guitar just for fun</em>.</span></div>
                </div>
                <p>La clave gramatical: <em>fun</em> es, ante todo, un <strong>sustantivo incontable</strong> que significa “diversión”. Por eso se dice <em>a lot of fun</em>, <em>so much fun</em> o <em>great fun</em>, y nunca <em>a fun</em> o <em>funs</em> como sustantivo. Además funciona como <strong>adjetivo</strong>, delante de un sustantivo (<em>a fun day</em>, <em>a fun teacher</em>) o detrás de <em>be</em> (<em>The trip was fun</em>).</p>
                <p>Se pronuncia <span class="ipa">/fʌn/</span> en EE. UU. y en Reino Unido, con la misma vocal corta de <em>up</em> o <em>us</em> que oyes en <a href="/audio/microsoft-up-us-uncle-umbrella.html">Microsoft, up, us, uncle, umbrella</a>. <em>Funny</em> es <span class="ipa">/ˈfʌni/</span>, también igual en los dos.</p>

                <h2 id="funny">¿Qué significa funny? Gracioso… o raro</h2>
                <p><em>Funny</em> suele significar gracioso: algo o alguien te hace reír. Un cómico puede ser <em>funny</em>, un vídeo puede ser <em>funny</em>, un comentario puede ser <em>funny</em>.</p>
                <p>Pero también puede significar raro, extraño o curioso. Si alguien dice <em>that smells funny</em>, probablemente no quiere decir que el olor cuente chistes.</p>
                <ul>
                <li><em>That's funny, I thought I'd locked the door.</em> → Qué raro, creía que había cerrado con llave.</li>
                <li><em>This milk tastes funny.</em> → Esta leche sabe rara.</li>
                <li><em>I've got a funny feeling about this.</em> → Esto me da mala espina.</li>
                <li><em>I feel a bit funny.</em> → Me encuentro un poco raro, algo indispuesto.</li>
                </ul>
                <p>Como la palabra tiene dos caras, en inglés británico existe la pregunta <em>Funny ha-ha or funny peculiar?</em> (¿gracioso de risa o gracioso de raro?). Y ojo con el tono: <em>Very funny.</em>, dicho seco y sin sonreír, es irónico, como nuestro “qué gracioso” cuando alguien te ha gastado una broma pesada.</p>

                <h2 id="comparacion">Fun vs funny: tabla comparativa</h2>
                <table class="data-table">
                <thead><tr><th></th><th>Fun</th><th>Funny</th></tr></thead>
                <tbody>
                <tr><td>Significado</td><td>Divertido, entretenido; diversión</td><td>Gracioso; también raro</td></tr>
                <tr><td>¿Te hace reír?</td><td>No necesariamente</td><td>Sí, en su sentido principal</td></tr>
                <tr><td>Tipo de palabra</td><td>Sustantivo incontable y adjetivo</td><td>Solo adjetivo</td></tr>
                <tr><td>Para intensificar</td><td>so much fun, a lot of fun, really fun</td><td>very funny, really funny</td></tr>
                <tr><td>Comparativo</td><td>more fun, the most fun</td><td>funnier, the funniest</td></tr>
                <tr><td>Aplicado a una persona</td><td>She's fun: es buena compañía</td><td>She's funny: te hace reír</td></tr>
                </tbody>
                </table>
                <div class="lesson-box">
                <strong>Atajo:</strong> si quieres decir que disfrutaste una experiencia, piensa en <em>fun</em>. Si quieres decir que algo te hizo reír, piensa en <em>funny</em>. Si algo te parece extraño, <em>funny</em> también puede servir.
                </div>
                <ol>
                <li><em>The party was fun</em> → La fiesta fue divertida.</li>
                <li><em>The comedian was funny</em> → El cómico era gracioso.</li>
                <li><em>It's funny that he didn't call</em> → Es raro/curioso que no llamara.</li>
                <li><em>She is fun</em> → Es divertida como persona, da gusto estar con ella.</li>
                <li><em>She is funny</em> → Hace gracia, te hace reír.</li>
                </ol>

                <h2 id="have-fun">Have fun, make fun of, so much fun y very funny</h2>
                <h3>Have fun frente a make fun of</h3>
                <p><em>Have fun</em> es pasarlo bien: <em>We had so much fun in Galway</em>. <em>Make fun of</em> es burlarse de alguien: <em>The other kids made fun of his accent</em>. Comparten la palabra <em>fun</em>, pero confundirlas puede dar situaciones incómodas. (Tienes más expresiones con <em>make</em> en <a href="/articulos/make-vs-do.html">make vs do</a>.)</p>
                <h3>So much fun, very funny y el polémico very fun</h3>
                <p>Como <em>fun</em> es sobre todo un sustantivo, lo tradicional es intensificarlo como tal: <em>so much fun</em>, <em>a lot of fun</em>. <em>Funny</em> es un adjetivo normal y va con <em>very</em>: <em>very funny</em>. ¿Y <em>very fun</em>? Se oye cada vez más, sobre todo en inglés americano informal, pero algunos hablantes todavía lo consideran incorrecto. Si quieres ir a lo seguro, di <em>really fun</em> o <em>so much fun</em>.</p>
                <h3>More fun y funnier</h3>
                <p>El comparativo estándar de <em>fun</em> es <em>more fun</em> (<em>Going with friends is more fun</em>). <em>Funner</em> y <em>funnest</em> aparecen en el habla informal, pero muchos los consideran incorrectos: no los uses en un examen. <em>Funny</em> hace <em>funnier</em> y <em>the funniest</em> sin problema.</p>
                <h3>Errores típicos</h3>
                <ul>
                <li><em>The wedding was very funny</em> → si te lo pasaste bien, <em>The wedding was so much fun</em>. Con <em>funny</em> parecería que la boda fue cómica.</li>
                <li><em>I had a lot of funny</em> → <em>I had a lot of fun</em>.</li>
                <li><em>I enjoyed a lot</em> → <em>enjoy</em> necesita complemento: <em>I enjoyed it a lot</em> o <em>I enjoyed myself</em>.</li>
                </ul>
                <p>Y si quieres variar, <em>I had a great time</em> (me lo pasé genial) o, más informal, <em>I had a blast</em>.</p>

                <h2 id="ejercicio">Ejercicio: ¿fun o funny?</h2>
                <p>Completa con <em>fun</em>, <em>funny</em> o una de sus formas. Pulsa cada frase para ver la solución.</p>
                <details class="exercise"><summary>1. We had a lot of ___ at the wedding.</summary><p><strong>fun</strong>. <em>Have fun</em>: lo pasasteis bien. <em>A lot of funny</em> no existe.</p></details>
                <details class="exercise"><summary>2. That joke wasn't ___ at all.</summary><p><strong>funny</strong>. Un chiste hace (o no hace) reír.</p></details>
                <details class="exercise"><summary>3. Surfing is really ___. You should try it.</summary><p><strong>fun</strong>. Es una actividad que se disfruta, no algo que dé risa.</p></details>
                <details class="exercise"><summary>4. This milk smells ___. I think it's gone bad.</summary><p><strong>funny</strong>. Aquí significa raro.</p></details>
                <details class="exercise"><summary>5. Stop making ___ of your brother!</summary><p><strong>fun</strong>. <em>Make fun of</em> = burlarse de.</p></details>
                <details class="exercise"><summary>6. My uncle is so ___. He always makes us laugh.</summary><p><strong>funny</strong>. Te hace reír.</p></details>
                <details class="exercise"><summary>7. Have ___ in Ibiza!</summary><p><strong>fun</strong>. <em>Have fun!</em> = ¡Pásalo bien!</p></details>
                <details class="exercise"><summary>8. It's ___, I was just thinking about you when you called.</summary><p><strong>funny</strong>. Curioso, qué casualidad.</p></details>
                <details class="exercise"><summary>9. Playing with friends is more ___ than playing alone.</summary><p><strong>fun</strong>. El comparativo estándar de <em>fun</em> es <em>more fun</em>.</p></details>
                <details class="exercise"><summary>10. This is the ___ film I've ever seen.</summary><p><strong>funniest</strong>. Superlativo de <em>funny</em>: la película más graciosa.</p></details>

                <h2 id="practica">Práctica rápida</h2>
                <p>Antes de elegir, pregúntate: ¿hablo de pasarlo bien, de reírme o de algo extraño? Esa pregunta resuelve la mayoría de casos.</p>
                <p>Para fijarlo, cuenta en voz alta tu último fin de semana: algo que fue <em>fun</em>, alguien que fue <em>funny</em> y algo que te pareció <em>funny</em> en el sentido de raro. Y ya que hablamos de risa, practica el verbo <em>laugh</em> (<span class="ipa">/lɑːf/</span> en Reino Unido, <span class="ipa">/læf/</span> en EE. UU.) con el audio <a href="/audio/light-love-listen-like-late-learn-laugh.html">light, love, listen, like, late, learn, laugh</a>: la <em>gh</em> suena como una <em>f</em>. Y si te gustan estos matices de vocabulario, sigue con <a href="/articulos/sufijos-ish-wise.html">los sufijos -ish y -wise</a>.</p>
        """,
    },
    {
        "slug": "some-vs-any",
        "category": "Gramática real",
        "title": "Some vs any: diferencias, excepciones y cuándo usar cada uno",
        "seo_title": "Some vs any: diferencias, reglas y excepciones en inglés",
        "description": "Some y any: diferencias, excepciones (ofertas, “cualquier”), somebody, anything, nobody y una tabla con much, many, a lot of y a few. Con ejercicio.",
        "lede": "La regla del workbook ayuda, pero se queda corta. Some y any dependen de si esperas un sí, si niegas algo o si quieres decir “cualquier”.",
        "reading": "8 minutos",
        "published": "2026-06-28",
        "toc": [
            ("regla", "La regla"),
            ("preguntas", "Preguntas"),
            ("negaciones", "Negaciones"),
            ("afirmaciones", "Afirmaciones"),
            ("compuestos", "Somebody, anything..."),
            ("cantidades", "Much, many, a few"),
            ("ejercicio", "Ejercicio"),
        ],
        "related": [
            "make-vs-do",
            "preposiciones-to-for-by-from-with",
            "fun-vs-funny",
        ],
        "quick_answer": "<strong>Some</strong> se usa normalmente en frases afirmativas y en ofrecimientos o peticiones (<em>Would you like some tea?</em>). <strong>Any</strong> se usa en negaciones y preguntas abiertas (<em>I don't have any money</em>, <em>Any questions?</em>) y en afirmativas con el sentido de “cualquier” (<em>Take any seat</em>). Los dos van con plurales e incontables.",
        "faq": [
            ("¿Cuál es la diferencia entre some y any?", "<em>Some</em> indica una cantidad indefinida que existe o que esperas: <em>I have some money</em>. <em>Any</em> se usa cuando niegas, cuando preguntas sin saber la respuesta o cuando quieres decir “cualquier”: <em>I don't have any money</em>, <em>Any idea?</em>"),
            ("¿Se puede usar some en preguntas?", "Sí, en ofrecimientos y peticiones o cuando esperas que la respuesta sea sí: <em>Would you like some cake?</em>, <em>Can I have some water?</em> En preguntas abiertas, lo normal es <em>any</em>."),
            ("¿Se puede usar any en frases afirmativas?", "Sí, cuando significa “cualquier”: <em>You can come at any time</em>, <em>Any bus goes to the station</em>. También después de <em>if</em> y de palabras como <em>hardly</em> o <em>without</em>."),
            ("¿Cuándo se usa much, many o a lot of?", "<em>Many</em> va con contables y <em>much</em> con incontables, sobre todo en negativas y preguntas: <em>How many?</em>, <em>not much time</em>. En afirmativas suena más natural <em>a lot of</em>, que vale para los dos tipos."),
            ("¿Se dice somebody o anybody?", "<em>Somebody</em> en afirmativas y ofrecimientos (<em>Somebody called</em>); <em>anybody</em> en negativas y preguntas abiertas (<em>Is anybody there?</em>, <em>I didn't see anybody</em>). Al principio de una frase negativa se usa <em>nobody</em>: <em>Nobody came</em>."),
        ],
        "body": """
                <p>La explicación típica dice: <em>some</em> en afirmaciones y <em>any</em> en preguntas y negaciones. No está mal como punto de partida, pero falla justo en frases muy comunes, como <em>Would you like some coffee?</em> o <em>Call me any time</em>.</p>
                <p>La versión útil para hablar es esta: <strong>some</strong> suele aparecer cuando hay una cantidad indefinida pero esperada; <strong>any</strong> aparece cuando no sabes si existe, cuando niegas, o cuando quieres decir “cualquier”. Vamos por partes: las diferencias entre some y any, sus compuestos (<em>somebody</em>, <em>anything</em>, <em>nobody</em>...) y una tabla con <em>much</em>, <em>many</em>, <em>a lot of</em>, <em>a few</em> y <em>a little</em>.</p>

                <h2 id="regla">La regla básica de some y any</h2>
                <div class="example-grid">
                <div class="mini-card"><strong>Some</strong><span><em>There are some books on the floor</em>. Hay algunos libros en el suelo.</span></div>
                <div class="mini-card"><strong>Any</strong><span><em>I don't have any questions</em>. No tengo ninguna pregunta.</span></div>
                </div>
                <table class="data-table">
                <thead><tr><th>Tipo de frase</th><th>Lo normal</th><th>Ejemplo</th></tr></thead>
                <tbody>
                <tr><td>Afirmativa</td><td>some</td><td>I've got some friends in Cork.</td></tr>
                <tr><td>Negativa</td><td>any</td><td>I haven't got any money.</td></tr>
                <tr><td>Pregunta abierta</td><td>any</td><td>Is there any milk?</td></tr>
                <tr><td>Oferta o petición</td><td>some</td><td>Would you like some tea?</td></tr>
                <tr><td>Afirmativa con sentido de “cualquier”</td><td>any</td><td>Take any seat.</td></tr>
                </tbody>
                </table>
                <p>Los dos van con <strong>plurales</strong> (<em>some books</em>, <em>any questions</em>) y con <strong>incontables</strong> (<em>some water</em>, <em>any information</em>). Con un contable en singular, lo normal es <em>a/an</em>: <em>I need a pen</em>, no <em>I need some pen</em>. Y muchas veces el español ni los traduce: <em>Is there any milk?</em> es simplemente “¿Hay leche?”.</p>
                <p>Hasta aquí, fácil. El problema llega con preguntas y afirmaciones donde la regla de instituto no explica el matiz.</p>

                <h2 id="preguntas">Preguntas: some si esperas que exista o que acepten</h2>
                <p>Usa <em>some</em> en preguntas cuando sabes que lo que pides existe o cuando estás ofreciendo algo que esperas que la otra persona acepte.</p>
                <ol>
                <li><em>Can I have some water?</em> → Sabes que hay agua y estás pidiendo de forma educada.</li>
                <li><em>Do you want some water?</em> → Tienes el agua a mano y esperas que pueda aceptar.</li>
                <li><em>Do you have any questions?</em> → No sabes si hay preguntas; por eso encaja <em>any</em>.</li>
                <li><em>Did you buy some bread?</em> → Esperas que sí, quizá porque se lo pediste. Con <em>any</em> sería una pregunta neutra.</li>
                </ol>
                <div class="lesson-box"><strong>Truco:</strong> si en tu cabeza la respuesta esperada es “sí”, <em>some</em>. Si de verdad no lo sabes, <em>any</em>.</div>

                <h2 id="negaciones">Negaciones: any es lo normal</h2>
                <p>En inglés no se usa la doble negación como en español. Decimos “no sé nada”, pero en inglés no digas <em>I don't know nothing</em>. La forma natural es <em>I don't know anything</em>. (La doble negación aparece en canciones y en algunos dialectos, pero no en inglés estándar.)</p>
                <p>Hay tres formas de negar la misma idea:</p>
                <ul>
                <li><em>I don't have any time.</em> → La más neutra.</li>
                <li><em>I have no time.</em> → Más tajante. <em>No</em> va con el verbo en afirmativa.</li>
                <li><em>None.</em> → Pronombre, solo o con <em>of</em>: <em>How much time do you have? — None.</em> / <em>None of my friends came.</em></li>
                </ul>
                <p>También verás <em>any</em> con palabras que ya tienen sentido negativo o limitante: <em>without any difficulty</em>, <em>barely any food</em>, <em>hardly any time</em>. Y después de <em>if</em>: <em>If you have any problems, call me</em>.</p>

                <h2 id="afirmaciones">Afirmaciones: some es alguno; any es cualquier</h2>
                <p>En afirmaciones, <em>some</em> suele significar “algún/algunos”: <em>There are some books</em>. En cambio, <em>any</em> puede significar “cualquier”: <em>Pick any card</em>, <em>Take any bus</em>, <em>Call me at any time</em>.</p>
                <p>Con este sentido, <em>any</em> va muy bien con contables en singular (<em>Any child knows that</em>, cualquier niño lo sabe) y se pronuncia con fuerza: <span class="ipa">/ˈeni/</span>, igual en EE. UU. y Reino Unido.</p>
                <p><em>Some</em> también tiene un uso especial con singular: “algún... no sé cuál”. <em>Some guy called for you</em> (te llamó un tipo, no sé quién). Es informal y a veces suena despectivo: <em>Some idiot scratched my car</em>.</p>
                <p>Y el acento cambia el significado: <em>some</em> átono suena <span class="ipa">/səm/</span> y significa “un poco de, unos”: <em>I bought some bread</em>. Acentuado suena <span class="ipa">/sʌm/</span> (EE. UU. y Reino Unido) y significa “algunos, no todos”: <em>SOME people love it, others hate it</em>. Esa vocal fuerte es la de <em>up</em> o <em>us</em>; escúchala en <a href="/audio/microsoft-up-us-uncle-umbrella.html">Microsoft, up, us, uncle, umbrella</a>.</p>
                <div class="lesson-box">
                <strong>Prueba mental:</strong> si en español puedes decir “cualquier”, probablemente necesitas <em>any</em>. Si quieres decir “algún” o “unos cuantos”, probablemente necesitas <em>some</em>.
                </div>

                <h2 id="compuestos">Somebody, anything, nobody: los compuestos</h2>
                <p>Las mismas reglas valen para los compuestos con <em>-body</em>/<em>-one</em> (personas), <em>-thing</em> (cosas) y <em>-where</em> (lugares):</p>
                <table class="data-table">
                <thead><tr><th></th><th>Personas</th><th>Cosas</th><th>Lugares</th></tr></thead>
                <tbody>
                <tr><td><strong>some-</strong></td><td>somebody, someone (alguien)</td><td>something (algo)</td><td>somewhere (en algún sitio)</td></tr>
                <tr><td><strong>any-</strong></td><td>anybody, anyone (alguien, nadie, cualquiera)</td><td>anything (algo, nada, cualquier cosa)</td><td>anywhere (en algún sitio, en ningún sitio, donde sea)</td></tr>
                <tr><td><strong>no-</strong></td><td>nobody, no one (nadie)</td><td>nothing (nada)</td><td>nowhere (en ningún sitio)</td></tr>
                <tr><td><strong>every-</strong></td><td>everybody, everyone (todos)</td><td>everything (todo)</td><td>everywhere (en todas partes)</td></tr>
                </tbody>
                </table>
                <ul>
                <li><strong>-body y -one significan lo mismo:</strong> <em>somebody</em> y <em>someone</em> son intercambiables; <em>-body</em> suena algo más coloquial.</li>
                <li><strong>Una sola negación:</strong> <em>I didn't see anybody</em> o <em>I saw nobody</em>, pero no <em>I didn't see nobody</em>.</li>
                <li><strong>Al principio de la frase, no-:</strong> <em>Nobody came</em>, nunca <em>Anybody didn't come</em>.</li>
                <li><strong>Verbo en singular:</strong> <em>Everybody is here</em>, <em>Nobody knows</em>. Pero el pronombre suele ser <em>they</em>: <em>Someone left their umbrella</em>.</li>
                <li><strong>Las mismas excepciones:</strong> <em>Would you like something to drink?</em> (oferta) y <em>Sit anywhere</em> (siéntate donde quieras).</li>
                </ul>

                <h2 id="cantidades">Some, any, much, many, a lot of, a few, a little: tabla resumen</h2>
                <p>Some y any forman parte de una familia de cuantificadores. Lo primero es mirar si el sustantivo es contable (<em>books</em>, <em>people</em>) o incontable (<em>water</em>, <em>money</em>, <em>time</em>).</p>
                <table class="data-table">
                <thead><tr><th>Cuantificador</th><th>Contables</th><th>Incontables</th><th>Uso típico</th><th>Ejemplo</th></tr></thead>
                <tbody>
                <tr><td>some</td><td>sí</td><td>sí</td><td>afirmativas, ofertas</td><td>some friends, some help</td></tr>
                <tr><td>any</td><td>sí</td><td>sí</td><td>negativas, preguntas, “cualquier”</td><td>any ideas?, not any money</td></tr>
                <tr><td>no / none</td><td>sí</td><td>sí</td><td>negación con verbo afirmativo</td><td>no idea, none of them</td></tr>
                <tr><td>many</td><td>sí</td><td>no</td><td>sobre todo negativas y preguntas</td><td>How many people?</td></tr>
                <tr><td>much</td><td>no</td><td>sí</td><td>sobre todo negativas y preguntas</td><td>I don't have much time.</td></tr>
                <tr><td>a lot of / lots of</td><td>sí</td><td>sí</td><td>sobre todo afirmativas</td><td>a lot of people, lots of time</td></tr>
                <tr><td>a few</td><td>sí</td><td>no</td><td>unos cuantos (positivo)</td><td>a few days</td></tr>
                <tr><td>a little</td><td>no</td><td>sí</td><td>un poco (positivo)</td><td>a little sugar</td></tr>
                <tr><td>few / little</td><td>few</td><td>little</td><td>pocos, poco (negativo)</td><td>few people know, little time</td></tr>
                </tbody>
                </table>
                <ul>
                <li><strong>Much y many en afirmativas suenan formales.</strong> <em>I have much time</em> es raro; lo natural es <em>I have a lot of time</em>. Con <em>too</em>, <em>so</em> y <em>as</em> sí son normales: <em>too much noise</em>, <em>so many people</em>.</li>
                <li><strong>A few frente a few.</strong> <em>I have a few friends here</em> (tengo algunos, estoy bien) frente a <em>I have few friends here</em> (tengo pocos, me siento algo solo). En conversación, <em>few</em> y <em>little</em> sin <em>a</em> suenan algo formales; se suele decir <em>not many</em> o <em>not much</em>.</li>
                <li><strong>Incontables traicioneros:</strong> <em>information</em>, <em>advice</em>, <em>news</em>, <em>furniture</em>, <em>luggage</em> y <em>homework</em> son incontables: <em>some advice</em>, <em>a lot of information</em>, nunca <em>an advice</em> o <em>informations</em>. Para contarlos, <em>a piece of advice</em>. (Lo mismo pasa con <em>fun</em>, como explico en <a href="/articulos/fun-vs-funny.html">fun vs funny</a>, y <em>homework</em> además va con <em>do</em>: lo tienes en <a href="/articulos/make-vs-do.html">make vs do</a>.)</li>
                </ul>

                <h2 id="ejercicio">Ejercicio: some, any, much, a few o compuestos</h2>
                <p>Elige la opción correcta para cada hueco. Pulsa cada frase para ver la solución.</p>
                <details class="exercise"><summary>1. Would you like ___ coffee?</summary><p><strong>some</strong>. Es un ofrecimiento y esperas un sí.</p></details>
                <details class="exercise"><summary>2. There isn't ___ milk in the fridge.</summary><p><strong>any</strong>. Negación. También valdría <em>There's no milk</em>.</p></details>
                <details class="exercise"><summary>3. Do you have ___ questions?</summary><p><strong>any</strong>. Pregunta abierta: no sabes si hay preguntas.</p></details>
                <details class="exercise"><summary>4. Can you give me ___ advice?</summary><p><strong>some</strong>. Petición. Y <em>advice</em> es incontable: nunca <em>an advice</em>.</p></details>
                <details class="exercise"><summary>5. You can call me at ___ time.</summary><p><strong>any</strong>. Significa “cualquier”: llámame cuando quieras.</p></details>
                <details class="exercise"><summary>6. I didn't see ___ at the party that I knew.</summary><p><strong>anybody</strong> o <strong>anyone</strong>. Con el verbo en negativa, <em>any-</em>. <em>I didn't see nobody</em> es incorrecto.</p></details>
                <details class="exercise"><summary>7. ___ called you this morning, but they didn't leave a message.</summary><p><strong>Somebody</strong> o <strong>Someone</strong>. Afirmativa, persona indeterminada. Fíjate en <em>they</em> para referirse a ella.</p></details>
                <details class="exercise"><summary>8. I've got ___ friends in Dublin, so I won't be alone.</summary><p><strong>a few</strong>. Unos cuantos, con idea positiva. <em>Few friends</em> sonaría a “pocos amigos”.</p></details>
                <details class="exercise"><summary>9. Hurry up, we haven't got ___ time.</summary><p><strong>much</strong>. <em>Time</em> es incontable y la frase es negativa.</p></details>
                <details class="exercise"><summary>10. I don't know ___ about cars.</summary><p><strong>anything</strong>. Una sola negación: <em>I don't know anything</em> o <em>I know nothing</em>.</p></details>

                <p>Para fijarlo, abre la nevera (de verdad o en tu cabeza) y descríbela en voz alta: <em>There's some milk, there isn't any cheese, there are a few eggs...</em> Parece un ejercicio tonto, pero te obliga a decidir en tiempo real, que es justo lo que pasa en una conversación.</p>
        """,
    },
    {
        "slug": "sufijos-ish-wise",
        "category": "Vocabulario",
        "title": "Sufijos -ish y -wise en inglés: significado, ejemplos y cuándo usarlos",
        "seo_title": "Sufijos -ish y -wise en inglés: significado y ejemplos",
        "description": "Qué significa el sufijo -ish en inglés (sevenish, tallish, “ish”) y cómo usar -wise (clockwise, money-wise), con ejemplos y notas de registro.",
        "lede": "-ish y -wise condensan mucha información en pocas letras. Son muy útiles en conversación, pero conviene saber qué significan exactamente y cuándo suenan demasiado informales.",
        "reading": "7 minutos",
        "published": "2026-06-28",
        "toc": [
            ("ish", "-ish"),
            ("gentilicios", "Spanish, British..."),
            ("wise", "-wise"),
            ("like-y", "-ish, -like, -y"),
            ("formalidad", "Formalidad"),
            ("ejemplos", "Práctica"),
        ],
        "related": [
            "fun-vs-funny",
            "i-mean-en-ingles",
            "actual-vs-actually",
            "some-vs-any",
        ],
        "quick_answer": "El sufijo <strong>-ish</strong> significa “más o menos” o “tirando a” (<em>sevenish</em>, sobre las siete; <em>tallish</em>, más bien alto) y también forma gentilicios (<em>Spanish</em>, <em>British</em>). <strong>-wise</strong> indica manera o dirección (<em>clockwise</em>, <em>likewise</em>) y, en registro informal, “en cuanto a” (<em>money-wise</em>, en cuanto al dinero).",
        "faq": [
            ("¿Qué significa -ish en inglés?", "<em>-ish</em> indica aproximación: “más o menos”, “tirando a”. <em>Greenish</em> es verdoso, <em>tallish</em> es más bien alto y <em>sevenish</em> es sobre las siete. En gentilicios como <em>Spanish</em> o <em>Irish</em> no indica aproximación, sino origen."),
            ("¿Qué significa “ish” sola?", "Usada como palabra suelta, <em>ish</em> significa “más o menos”: <em>Are you ready? — Ish.</em> Es muy coloquial y se asocia sobre todo al inglés británico, aunque se entiende en todas partes."),
            ("¿Qué significa -wise en inglés?", "Tiene dos usos: manera o dirección, en palabras clásicas como <em>clockwise</em>, <em>likewise</em> u <em>otherwise</em>; y “en cuanto a”, en formaciones modernas e informales como <em>money-wise</em> o <em>work-wise</em>."),
            ("¿Se puede usar -wise en inglés formal?", "Las palabras clásicas (<em>clockwise</em>, <em>likewise</em>, <em>otherwise</em>) sí. Las formaciones del tipo <em>money-wise</em> son informales y algunas guías de estilo las desaconsejan; en un texto formal es mejor <em>financially</em> o <em>in terms of money</em>."),
            ("¿Cuál es la diferencia entre childish y childlike?", "<em>Childish</em> es negativo: infantil, inmaduro (<em>Don't be childish</em>). <em>Childlike</em> es positivo o neutro: con la inocencia o la curiosidad de un niño (<em>a childlike sense of wonder</em>)."),
        ],
        "body": """
                <p>El inglés tiene una economía de lenguaje muy potente. A veces puedes añadir unas pocas letras a una palabra y crear un matiz que en español necesitaría una frase completa.</p>
                <p>Dos sufijos muy útiles para eso son <strong>-ish</strong> y <strong>-wise</strong>. Los dos vienen del inglés antiguo, pero tienen usos modernos muy coloquiales que oirás constantemente en series, en el trabajo y en cualquier conversación con nativos.</p>

                <h2 id="ish">¿Qué significa -ish en inglés? Aproximado, tirando a, más o menos</h2>
                <p><em>-ish</em> se añade a adjetivos, cualidades o cantidades para indicar aproximación. No dice “exactamente esto”, sino “algo parecido a esto”.</p>
                <div class="example-grid">
                <div class="mini-card"><strong>greenish</strong><span>Verdoso, tirando a verde.</span></div>
                <div class="mini-card"><strong>tallish</strong><span>Más bien alto, tirando a alto.</span></div>
                <div class="mini-card"><strong>fourish</strong><span>Sobre las cuatro, más o menos a las cuatro.</span></div>
                <div class="mini-card"><strong>Spanish-ish</strong><span>Algo parecido a español, pero no del todo.</span></div>
                </div>
                <ul>
                <li><strong>Colores:</strong> <em>reddish</em> (rojizo), <em>yellowish</em> (amarillento), <em>bluish</em> (azulado; también <em>blueish</em>).</li>
                <li><strong>Tamaño, edad o forma:</strong> <em>smallish</em> (tirando a pequeño), <em>youngish</em> (bastante joven), <em>longish</em> (algo largo).</li>
                <li><strong>Horas, números y edades:</strong> <em>Let's meet at sevenish</em> (sobre las siete), <em>He's fortyish</em> (tiene unos cuarenta).</li>
                </ul>
                <p>Ortografía: en palabras cortas que terminan en consonante + vocal + consonante se duplica la última (<em>red → reddish</em>, <em>big → biggish</em>), y la <em>-e</em> final suele caer (<em>white → whitish</em>). El sufijo se pronuncia <span class="ipa">/ɪʃ/</span> en EE. UU. y Reino Unido, con la <em>i</em> corta que oyes en <a href="/audio/bit-big-win-lip-clip.html">bit, big, win, lip, clip</a>.</p>

                <h2 id="ish-sola">“Ish” sola: la respuesta para “más o menos”</h2>
                <p>En el inglés hablado de hoy, <em>ish</em> funciona también como palabra suelta, al final de una frase o como respuesta. Es muy coloquial y se asocia sobre todo al inglés británico, aunque se entiende en todas partes.</p>
                <ul>
                <li><em>Are you ready? — Ish.</em> → ¿Estás listo? —Más o menos.</li>
                <li><em>I'll be there at eight. Ish.</em> → Llegaré a las ocho. Bueno, más o menos.</li>
                <li><em>The kitchen is clean... ish.</em> → La cocina está limpia... por así decirlo.</li>
                </ul>
                <p>Es como una versión corta de <em>kind of</em> o <em>sort of</em>, que en el habla rápida suelen reducirse a algo parecido a “kinda” y “sorta”. Practícalas con el audio <a href="/audio/out-of-kind-of-sort-of.html">out of, kind of, sort of</a>, y si te interesan estas muletillas, mira también <a href="/articulos/i-mean-en-ingles.html">cómo usar I mean</a>.</p>

                <h2 id="gentilicios">-ish en nacionalidades: Spanish, British, Irish</h2>
                <p>Hay otro <em>-ish</em> que no tiene nada de aproximado: el que forma gentilicios e idiomas. <em>Spanish</em>, <em>English</em>, <em>British</em>, <em>Irish</em>, <em>Scottish</em>, <em>Polish</em>, <em>Turkish</em>, <em>Danish</em>, <em>Swedish</em>. Aquí significa simplemente “de”: <em>Spanish</em> es español a secas. Por eso el <em>Spanish-ish</em> de arriba tiene gracia: es un <em>-ish</em> de aproximación pegado a un gentilicio que ya lleva <em>-ish</em>.</p>
                <ul>
                <li>Van siempre con mayúscula. Ojo: <em>Polish</em> es polaco, pero <em>polish</em>, con minúscula, es sacar brillo, y se pronuncian distinto.</li>
                <li>Son adjetivos: <em>I'm Spanish</em>, no <em>I'm a Spanish</em>. Como sustantivo, <em>a Spaniard</em> (algo formal) o <em>a Spanish person</em>. Escúchalo en <a href="/audio/i-am-spanish.html">I am Spanish</a>.</li>
                <li>Para el grupo: <em>the Spanish</em>, <em>the British</em>, <em>the Irish</em>.</li>
                </ul>
                <p>Practica varios seguidos con <a href="/audio/american-british-australian-irish-spanish.html">American, British, Australian, Irish, Spanish</a>. <em>Spanish</em> se pronuncia <span class="ipa">/ˈspænɪʃ/</span> en EE. UU. y en Reino Unido.</p>

                <h2 id="wise">¿Qué significa -wise? En cuanto a, respecto a</h2>
                <p><em>-wise</em> tiene dos usos muy distintos, y conviene separarlos porque no tienen el mismo registro.</p>
                <h3>1. Manera o dirección: uso clásico y neutro</h3>
                <p>Es el uso antiguo, “a la manera de” o “en la dirección de”. Estas palabras son correctas en cualquier registro, incluido el formal:</p>
                <table class="data-table">
                <thead><tr><th>Palabra</th><th>Significado</th><th>Ejemplo</th></tr></thead>
                <tbody>
                <tr><td>clockwise</td><td>en el sentido de las agujas del reloj</td><td>Turn it clockwise.</td></tr>
                <tr><td>anticlockwise (UK) / counterclockwise (US)</td><td>en sentido contrario</td><td>Turn the key anticlockwise.</td></tr>
                <tr><td>likewise</td><td>igualmente, lo mismo digo</td><td>Nice to meet you. — Likewise.</td></tr>
                <tr><td>otherwise</td><td>si no, de lo contrario; por lo demás</td><td>Hurry up, otherwise we'll miss the train.</td></tr>
                <tr><td>lengthwise</td><td>a lo largo</td><td>Cut the carrot lengthwise.</td></tr>
                </tbody>
                </table>
                <h3>2. “En cuanto a”: uso moderno e informal</h3>
                <p>El uso que más vas a oír en conversación es el moderno: se pega <em>-wise</em> a casi cualquier sustantivo para decir “en cuanto a” o “en términos de”.</p>
                <ol>
                <li><em>Moneywise, this project is risky</em> → En cuanto al dinero, este proyecto es arriesgado.</li>
                <li><em>Career-wise, it was a good move</em> → En términos profesionales, fue una buena decisión.</li>
                <li><em>Weather-wise, we were really lucky</em> → Con el tiempo tuvimos mucha suerte.</li>
                <li><em>How are things work-wise?</em> → ¿Qué tal en el trabajo?</li>
                </ol>
                <p>Se escribe junto (<em>moneywise</em>) o con guion (<em>money-wise</em>); con combinaciones poco habituales, el guion es lo más frecuente. Y no lo confundas con el adjetivo <em>wise</em> (sabio): <em>streetwise</em> sí significa “espabilado, que sabe moverse”, pero <em>money-wise</em> no es “sabio con el dinero”, sino “en cuanto al dinero”.</p>

                <h2 id="like-y">-ish, -like y -y: ¿cuál es la diferencia?</h2>
                <table class="data-table">
                <thead><tr><th>Sufijo</th><th>Idea</th><th>Ejemplos</th></tr></thead>
                <tbody>
                <tr><td>-ish (aproximación)</td><td>más o menos, tirando a</td><td>greenish, tallish, sevenish</td></tr>
                <tr><td>-ish (con sustantivos)</td><td>con cualidades de, a veces negativo</td><td>childish (infantil), foolish (tonto), selfish (egoísta)</td></tr>
                <tr><td>-like</td><td>parecido a, neutro o positivo</td><td>childlike (inocente), lifelike (realista), businesslike (profesional)</td></tr>
                <tr><td>-y</td><td>que tiene o que recuerda a</td><td>sunny, salty, lemony (con sabor a limón)</td></tr>
                </tbody>
                </table>
                <p>La pareja clave es <strong>childish</strong> frente a <strong>childlike</strong>: <em>Don't be childish</em> es una crítica; <em>She has a childlike curiosity</em> (tiene una curiosidad de niña) es un elogio. Y una curiosidad: <em>funny</em> se formó justo así, <em>fun</em> + <em>-y</em> (lo explico en <a href="/articulos/fun-vs-funny.html">fun vs funny</a>).</p>

                <h2 id="formalidad">Ojo con la formalidad</h2>
                <p>Estos sufijos son muy prácticos y naturales en conversación, pero no siempre encajan en escritura formal. En un informe serio, quizá prefieras una frase completa: <em>from a financial perspective</em> en lugar de <em>moneywise</em>.</p>
                <p>Con el <em>-wise</em> moderno hay además un problema de imagen: algunas guías de estilo y bastantes hablantes lo ven como jerga de oficina, sobre todo cuando se abusa de él. Una vez en una conversación, perfecto; tres veces en el mismo correo, mejor no.</p>
                <table class="data-table">
                <thead><tr><th>Informal</th><th>Más neutro o formal</th></tr></thead>
                <tbody>
                <tr><td>at sevenish</td><td>at around seven, at approximately seven o'clock</td></tr>
                <tr><td>Ish.</td><td>More or less. / Sort of.</td></tr>
                <tr><td>money-wise</td><td>financially, in terms of money</td></tr>
                <tr><td>work-wise</td><td>as far as work is concerned</td></tr>
                </tbody>
                </table>
                <div class="lesson-box">
                <strong>Regla práctica:</strong> úsalos para sonar ágil en conversación. En documentos formales, comprueba si una alternativa más completa suena mejor.
                </div>

                <h2 id="ejemplos">Mini práctica</h2>
                <p>¿Cómo lo dirías en inglés? Piensa tu respuesta y pulsa para comprobarla.</p>
                <details class="exercise"><summary>1. Llegaré sobre las ocho.</summary><p><em>I'll be there at eightish.</em> Más neutro: <em>at around eight</em>.</p></details>
                <details class="exercise"><summary>2. Es más bien bajito.</summary><p><em>He's shortish.</em> También <em>He's quite short</em>.</p></details>
                <details class="exercise"><summary>3. ¿Está terminado? —Más o menos.</summary><p><em>Is it finished? — Ish.</em> Muy coloquial.</p></details>
                <details class="exercise"><summary>4. En cuanto al tiempo, el viaje fue perfecto.</summary><p><em>Weather-wise, the trip was perfect.</em></p></details>
                <details class="exercise"><summary>5. Gira la tapa en el sentido de las agujas del reloj.</summary><p><em>Turn the lid clockwise.</em> Al revés: <em>anticlockwise</em> (Reino Unido) o <em>counterclockwise</em> (EE. UU.).</p></details>
                <details class="exercise"><summary>6. Encantado de conocerte. —Igualmente.</summary><p><em>Nice to meet you. — Likewise.</em></p></details>
                <details class="exercise"><summary>7. No seas infantil.</summary><p><em>Don't be childish.</em> <em>Childlike</em> sería un elogio, no una crítica.</p></details>
                <details class="exercise"><summary>8. Soy español.</summary><p><em>I'm Spanish.</em> Sin artículo: <em>I'm a Spanish</em> es incorrecto.</p></details>

                <p>Después, prueba a crear tres frases propias: una con una hora aproximada usando <em>-ish</em>, otra con un color aproximado y otra con <em>-wise</em> para hablar de dinero, carrera o tiempo.</p>
        """,
    },
    {
        "slug": "libros-para-aprender-ingles",
        "category": "Recursos",
        "title": "Libros para aprender inglés: cuál elegir según tu nivel y tu objetivo",
        "seo_title": "Libros para aprender inglés: los mejores por nivel",
        "description": "Los mejores libros para aprender inglés por nivel y objetivo: gramática, vocabulario, pronunciación y lectura, y para quién es (y no) cada uno.",
        "lede": "No existe el mejor libro de inglés para todo el mundo, pero sí el mejor para tu nivel y para lo que te falla. Aquí tienes pocos libros, bien elegidos y explicados con honestidad.",
        "reading": "12 minutos",
        "published": "2026-10-11",
        "from_book": False,
        "toc": [
            ("como-elegir", "Cómo elegir"),
            ("gramatica", "Gramática"),
            ("pronunciacion", "Pronunciación"),
            ("leer", "Aprender leyendo"),
            ("comparativa", "Tabla comparativa"),
            ("por-nivel", "Libros por nivel"),
            ("estudiar-solo", "Estudiar solo"),
        ],
        "related": [
            "guia-pronunciacion-ingles-espanoles",
            "alfabeto-fonetico-ingles",
            "prompts-aprender-ingles-ia",
            "vocales-ingles-cortas-largas",
        ],
        "quick_answer": "El mejor libro para aprender inglés depende de tu nivel y de lo que te falla: para gramática, <strong>English Grammar in Use</strong> de Raymond Murphy (o <em>Essential Grammar in Use</em> si empiezas); para vocabulario, <strong>English Vocabulary in Use</strong>; para pronunciación, <strong>English Pronunciation in Use</strong> o <strong>Ship or Sheep?</strong>; y para aprender leyendo, lecturas graduadas por nivel.",
        "faq": [
            ("¿Cuál es el mejor libro para aprender inglés por tu cuenta?", "Para gramática, <em>English Grammar in Use</em> de Raymond Murphy (Cambridge), en su versión con soluciones, es la opción más segura si tienes nivel intermedio; si empiezas, <em>Essential Grammar in Use</em>. Para estudiar solo, elige siempre libros con solucionario y, si trabajan pronunciación, con audio."),
            ("¿Se puede aprender inglés solo con libros?", "Solo con libros, no del todo. Un libro te da estructura, gramática y vocabulario, pero la comprensión auditiva y la soltura al hablar exigen escuchar y hablar. Lo ideal es combinar un libro con audio, series, podcasts y conversación real."),
            ("¿Qué libro de inglés es mejor para empezar desde cero?", "Para un adulto que empieza desde cero: <em>Essential Grammar in Use</em> (Raymond Murphy) para la gramática, <em>English Vocabulary in Use Elementary</em> para el vocabulario y lecturas graduadas de nivel inicial con audio. Si vas a estudiar sin profesor, cómpralos en versión con soluciones."),
            ("¿Qué libro sirve para mejorar la pronunciación en inglés?", "<em>English Pronunciation in Use</em> (Cambridge), con volúmenes de nivel elemental, intermedio y avanzado, y <em>Ship or Sheep?</em> de Ann Baker para practicar pares de sonidos. Cualquiera de ellos solo funciona si usas el audio y repites en voz alta."),
            ("¿Qué libros leer en inglés para practicar?", "Empieza por lecturas graduadas por nivel, como Penguin Readers, Oxford Bookworms o Cambridge English Readers, a ser posible con audio. Cuando se te queden cortas, pasa a novelas juveniles escritas para nativos, como <em>Wonder</em> de R. J. Palacio o <em>Holes</em> de Louis Sachar."),
        ],
        "body": """
                <p>Si has buscado “libros para aprender inglés”, ya sabes lo que pasa: listas de veinte títulos, todos “imprescindibles”, y ninguna pista sobre cuál es para ti. La verdad es que no existe el mejor libro de inglés en abstracto. Existe el mejor libro para tu nivel, para lo que te falla y para la forma en que vas a estudiar.</p>
                <p>Esta guía va al revés que la mayoría: primero te ayuda a elegir y después te propone pocos libros, agrupados por necesidad, con un “para quién es” y un “para quién no” honesto en cada uno.</p>

                <h2 id="como-elegir">¿Cómo elegir un libro para aprender inglés?</h2>
                <p>Antes de comprar nada, responde a tres preguntas. Te ahorrarán la frustración de abandonar un libro en la página 30.</p>
                <h3>1. ¿Cuál es tu nivel real?</h3>
                <p>No el que pone tu CV, sino el que tienes hoy. Un libro demasiado fácil aburre; uno demasiado difícil desmoraliza. Si no lo tienes claro, haz un test de nivel online gratuito y, si dudas entre dos niveles, empieza por el más bajo: consolidar siempre rinde más que pelearse con cada frase. Fíjate en los niveles del Marco Común Europeo (A1, A2, B1, B2, C1, C2), porque muchas editoriales los usan para clasificar sus libros.</p>
                <h3>2. ¿Qué te falla de verdad?</h3>
                <p>No es lo mismo dudar con el <em>present perfect</em> que entenderlo todo por escrito y quedarte en blanco en una llamada. Para lo primero, un libro de gramática. Para lo segundo, uno de pronunciación y escucha, con audio. Muchos españoles llevamos años comprando libros de gramática cuando lo que nos frena es el oído y la boca.</p>
                <h3>3. ¿Vas a estudiar solo o con profesor?</h3>
                <p>Si estudias por tu cuenta, necesitas tres cosas: explicaciones claras, ejercicios con solucionario y, si el libro trabaja sonidos, audio. Varios de los libros de esta lista se venden en versión <em>with answers</em> (con soluciones) y <em>without answers</em> (pensada para usar en clase). Si estudias solo, la versión con soluciones no es opcional.</p>
                <div class="lesson-box"><strong>Regla práctica:</strong> un libro por objetivo y de uno en uno. Un libro terminado vale más que cinco empezados.</div>

                <h2 id="gramatica">Los mejores libros de gramática inglesa</h2>
                <p>Si buscas un libro de gramática inglesa para estudiar por tu cuenta, la familia <em>Grammar in Use</em> de Cambridge University Press es la referencia. En los libros de Murphy, cada unidad ocupa dos páginas, con la explicación a la izquierda y los ejercicios a la derecha, así que puedes hacer una unidad en una sentada y saber exactamente dónde te has quedado.</p>
                <h3>Essential Grammar in Use – Raymond Murphy (Cambridge)</h3>
                <p>Es el hermano pequeño del famoso “Murphy”: gramática básica explicada con frases cortas y ejercicios inmediatos. Está escrito en un inglés sencillo, así que puedes seguirlo aunque tu nivel sea bajo.</p>
                <ul>
                <li><strong>Para quién es:</strong> principiantes (A1-A2) o quien tiene una base desordenada y quiere reconstruirla desde los cimientos.</li>
                <li><strong>Para quién no:</strong> si ya manejas los tiempos verbales básicos, se te quedará corto enseguida.</li>
                </ul>
                <h3>English Grammar in Use – Raymond Murphy (Cambridge)</h3>
                <p>El clásico de los clásicos. En España mucha gente lo llama simplemente “el Murphy”. Cubre la gramática de nivel intermedio: tiempos verbales, condicionales, pasiva, estilo indirecto, preposiciones, phrasal verbs y mucho más.</p>
                <ul>
                <li><strong>Para quién es:</strong> nivel intermedio (B1-B2, orientativamente) y cualquiera que estudie solo y quiera un manual al que volver durante años. Úsalo como consulta: buscas la unidad de tu duda, la haces y sigues.</li>
                <li><strong>Para quién no:</strong> si tu gramática ya es aceptable y lo que quieres es hablar con más soltura. Hacer más fichas no te va a dar oído ni pronunciación.</li>
                </ul>
                <h3>Advanced Grammar in Use – Martin Hewings (Cambridge)</h3>
                <p>La continuación para niveles altos, de otro autor pero con la misma filosofía. Entra en matices, estructuras más formales y usos menos frecuentes que el Murphy intermedio no toca.</p>
                <ul>
                <li><strong>Para quién es:</strong> nivel C1 o quien prepara exámenes de nivel avanzado.</li>
                <li><strong>Para quién no:</strong> si todavía dudas con el <em>present perfect</em> o los condicionales. Vuelve antes al Murphy intermedio.</li>
                </ul>
                <h3>Practical English Usage – Michael Swan (Oxford)</h3>
                <p>No es un curso, es un libro de consulta: entradas breves sobre puntos concretos (la diferencia entre dos palabras parecidas, una estructura que te suena rara, una regla con excepciones) que se resuelven con precisión. Está pensado tanto para estudiantes avanzados como para profesores.</p>
                <ul>
                <li><strong>Para quién es:</strong> nivel B2 en adelante, gente curiosa que quiere entender el porqué de las cosas y quien escribe en inglés en el trabajo.</li>
                <li><strong>Para quién no:</strong> para aprender gramática desde cero o para seguir un orden. No tiene sentido leerlo de principio a fin.</li>
                </ul>

                <h2 id="vocabulario">Libros de vocabulario: English Vocabulary in Use</h2>
                <p>La serie <em>English Vocabulary in Use</em> (Cambridge), con la mayoría de sus volúmenes firmados por Michael McCarthy y Felicity O’Dell, organiza el vocabulario por temas: el trabajo, los viajes, los sentimientos, el dinero... Hay un volumen por nivel: <em>Elementary</em>, <em>Pre-intermediate and Intermediate</em>, <em>Upper-intermediate</em> y <em>Advanced</em>. Dentro de la misma familia “in Use” también hay libros específicos de phrasal verbs, idioms y collocations.</p>
                <ul>
                <li><strong>Para quién es:</strong> quien entiende la gramática pero se queda sin palabras, o usa siempre las mismas. Funciona muy bien para estudiar solo.</li>
                <li><strong>Para quién no:</strong> si esperas aprender vocabulario solo rellenando huecos. Las palabras se quedan cuando las vuelves a ver y las usas en frases tuyas: el libro es el punto de partida, no la meta.</li>
                </ul>

                <h2 id="pronunciacion">Libros de pronunciación en inglés</h2>
                <p>Aquí está el hueco de casi todos los españoles. Y una advertencia: un libro de pronunciación sin audio es como un libro de natación sin piscina. Antes de comprarlo, comprueba que la edición que eliges incluye el audio, ya sea descargable, en CD o dentro de la versión digital.</p>
                <h3>English Pronunciation in Use (Cambridge)</h3>
                <p>Tres volúmenes, cada uno de un autor: <em>Elementary</em> (Jonathan Marks), <em>Intermediate</em> (Mark Hancock) y <em>Advanced</em> (Martin Hewings). Trabajan sonidos sueltos, pero también el acento de las palabras, el ritmo y la entonación, que es justo lo que más se nota cuando hablas. Verás símbolos fonéticos, así que te vendrá bien saber leer el <a href="/articulos/alfabeto-fonetico-ingles.html">alfabeto fonético inglés</a>.</p>
                <ul>
                <li><strong>Para quién es:</strong> quien estudia solo y quiere un recorrido ordenado y completo por la pronunciación. El <em>Intermediate</em> es el que encaja con más gente.</li>
                <li><strong>Para quién no:</strong> si no vas a escuchar y repetir en voz alta. Leído en silencio, no sirve de mucho.</li>
                </ul>
                <h3>Ship or Sheep? – Ann Baker (Cambridge)</h3>
                <p>Un clásico basado en pares mínimos: palabras que solo se diferencian en un sonido, como <em>ship</em> (barco) y <em>sheep</em> (oveja). Es exactamente el tipo de contraste que a un hispanohablante le cuesta oír y producir. Su hermano pequeño, <em>Tree or Three?</em>, de la misma autora, está pensado para niveles iniciales.</p>
                <ul>
                <li><strong>Para quién es:</strong> nivel intermedio que quiere atacar sonidos concretos (vocales cortas y largas, consonantes que no tenemos) con práctica muy repetitiva.</li>
                <li><strong>Para quién no:</strong> si lo que buscas es conversación; su fuerte son los sonidos.</li>
                </ul>
                <p>Puedes probar la idea ahora mismo con nuestros audios: <a href="/audio/live-leave-leaf.html">live, leave y leaf</a> es el mismo contraste que <em>ship</em> y <em>sheep</em>, y <a href="/audio/bit-big-win-lip-clip.html">bit, big, win, lip y clip</a> entrena la vocal corta que más nos cuesta.</p>

                <h2 id="metodo">Libros sobre método y conversación real</h2>
                <h3>Fluent Forever – Gabriel Wyner</h3>
                <p>No es un libro de inglés, sino un libro sobre cómo aprender idiomas. Wyner propone empezar por la pronunciación, aprender las palabras con imágenes en lugar de con traducciones y repasar con tarjetas de repetición espaciada (por ejemplo, con Anki). Si nunca has tenido un sistema de estudio, te da uno.</p>
                <ul>
                <li><strong>Para quién es:</strong> autodidactas metódicos de cualquier nivel que quieren organizar su estudio. Si lo lees en inglés, un B2 te permitirá disfrutarlo.</li>
                <li><strong>Para quién no:</strong> si buscas ejercicios de inglés o explicaciones gramaticales, porque no los vas a encontrar. Y si odias las flashcards, la mitad del método no es para ti.</li>
                </ul>
                <h3>De FAK a Fluent – Javier Sanz</h3>
                <div class="lesson-box"><strong>Transparencia:</strong> es el libro de este sitio. Lo incluimos porque cubre un hueco concreto: pronunciación y conversación real para españoles con base, con audios. No es para principiantes absolutos.</div>
                <p>Lo escribió un español que ha vivido y trabajado en inglés en Irlanda, Reino Unido y Estados Unidos, y se centra en lo que los manuales suelen dejar fuera: pronunciación, comprensión auditiva, expresiones naturales y matices culturales. Tiene más de 28.000 palabras y cerca de 100 ejemplos de audio, y en esta web tienes <a href="/audios.html">60 audios gratis</a> para probar el enfoque antes de decidir. Tampoco promete milagros: en la portada pone, literalmente, “No vas a aprender inglés en 30 días”.</p>
                <ul>
                <li><strong>Para quién es:</strong> españoles con base (nivel intermedio) que entienden más de lo que hablan, a los que no siempre entienden o que se pierden cuando los nativos hablan rápido.</li>
                <li><strong>Para quién no:</strong> principiantes absolutos o quien busca un manual de gramática con ejercicios. Para eso, el Murphy.</li>
                </ul>

                <h2 id="leer">Libros para aprender inglés leyendo</h2>
                <p>Leer es la forma más cómoda de ganar vocabulario y de ver la gramática funcionando, pero solo si el texto es de tu nivel. Para eso existen las lecturas graduadas (<em>graded readers</em>): novelas, clásicos adaptados e historias originales escritas con un vocabulario y una gramática limitados según el nivel.</p>
                <ul>
                <li><strong>Penguin Readers:</strong> serie graduada por niveles, con muchos clásicos adaptados y títulos conocidos.</li>
                <li><strong>Oxford Bookworms:</strong> la colección graduada de Oxford University Press, desde los niveles iniciales hasta los avanzados.</li>
                <li><strong>Cambridge English Readers:</strong> la colección graduada de Cambridge, con historias originales escritas directamente para estudiantes.</li>
                </ul>
                <p>Cada colección usa su propia escala de niveles, y muchos títulos indican también su equivalencia con el Marco Común Europeo. Además, muchos incluyen audio, lo que te permite leer y escuchar a la vez: es de lo mejor que puedes hacer por tu oído.</p>
                <div class="lesson-box"><strong>Cómo acertar con el nivel:</strong> lee la primera página. Si necesitas el diccionario en cada línea, baja un nivel. Si la lees casi entera sin parar y te enteras de la historia, ese es tu libro. La lectura que funciona es la que disfrutas, no la que sufres.</div>
                <p>Cuando las lecturas graduadas se te queden cortas, salta a novelas juveniles escritas para nativos, como <em>Wonder</em> (R. J. Palacio) o <em>Holes</em> (Louis Sachar): lenguaje real, frases asequibles y tramas que enganchan.</p>

                <h2 id="comparativa">¿Cuál es el mejor libro para aprender inglés? Tabla comparativa</h2>
                <table class="data-table">
                <thead><tr><th>Libro</th><th>Nivel (orientativo)</th><th>Para qué sirve</th><th>¿Con audio?</th></tr></thead>
                <tbody>
                <tr><td>Essential Grammar in Use</td><td>A1-B1</td><td>Gramática básica para estudiar solo</td><td>No es su enfoque</td></tr>
                <tr><td>English Grammar in Use</td><td>B1-B2</td><td>Gramática intermedia y consulta durante años</td><td>No es su enfoque</td></tr>
                <tr><td>Advanced Grammar in Use</td><td>C1-C2</td><td>Gramática avanzada y matices</td><td>No es su enfoque</td></tr>
                <tr><td>Practical English Usage</td><td>B2-C2</td><td>Resolver dudas concretas de uso</td><td>No es su enfoque</td></tr>
                <tr><td>English Vocabulary in Use</td><td>De básico a avanzado (un volumen por nivel)</td><td>Vocabulario organizado por temas</td><td>No es su enfoque</td></tr>
                <tr><td>English Pronunciation in Use</td><td>De básico a avanzado (tres volúmenes)</td><td>Sonidos, acento, ritmo y entonación</td><td>Sí, imprescindible</td></tr>
                <tr><td>Ship or Sheep?</td><td>Intermedio</td><td>Pares mínimos y sonidos difíciles</td><td>Sí</td></tr>
                <tr><td>Fluent Forever</td><td>Cualquiera</td><td>Método de estudio y memoria</td><td>No (es un libro de método)</td></tr>
                <tr><td>Lecturas graduadas</td><td>De A1 a C1</td><td>Aprender leyendo, vocabulario en contexto</td><td>Muchos títulos, sí</td></tr>
                <tr><td>De FAK a Fluent</td><td>Con base (intermedio)</td><td>Pronunciación, listening y conversación real para españoles</td><td>Sí: cerca de 100 ejemplos</td></tr>
                </tbody>
                </table>
                <p>Si solo vas a comprar uno, la pregunta clave es la segunda del principio: ¿qué te falla de verdad? Gramática, Murphy. Vocabulario, <em>Vocabulary in Use</em>. Que no te entiendan o no entender a los nativos, un libro con audio.</p>

                <h2 id="por-nivel">Libros por nivel (A1-C1)</h2>
                <p>Si prefieres ir directo a tu nivel, esta es la combinación que funciona: un libro de base, uno para tu punto débil y lectura.</p>
                <h3>A1-A2: desde cero</h3>
                <ul>
                <li><strong>Gramática:</strong> Essential Grammar in Use.</li>
                <li><strong>Vocabulario:</strong> English Vocabulary in Use Elementary.</li>
                <li><strong>Pronunciación:</strong> English Pronunciation in Use Elementary o Tree or Three?</li>
                <li><strong>Lectura:</strong> lecturas graduadas de los primeros niveles, con audio.</li>
                </ul>
                <h3>B1: “lo entiendo todo escrito, pero...”</h3>
                <ul>
                <li><strong>Gramática:</strong> English Grammar in Use, empezando por tus dudas.</li>
                <li><strong>Vocabulario:</strong> English Vocabulary in Use Pre-intermediate and Intermediate.</li>
                <li><strong>Pronunciación:</strong> English Pronunciation in Use Intermediate o Ship or Sheep?</li>
                <li><strong>Lectura:</strong> lecturas graduadas de nivel intermedio.</li>
                </ul>
                <h3>B2: de saber inglés a usarlo</h3>
                <ul>
                <li><strong>Gramática:</strong> termina el Murphy intermedio y consulta Practical English Usage para las dudas finas.</li>
                <li><strong>Vocabulario:</strong> English Vocabulary in Use Upper-intermediate.</li>
                <li><strong>Pronunciación y conversación:</strong> English Pronunciation in Use Intermediate y De FAK a Fluent.</li>
                <li><strong>Lectura:</strong> los últimos niveles de las lecturas graduadas y novelas juveniles.</li>
                </ul>
                <h3>C1: los matices</h3>
                <ul>
                <li><strong>Gramática:</strong> Advanced Grammar in Use y Practical English Usage.</li>
                <li><strong>Vocabulario:</strong> English Vocabulary in Use Advanced.</li>
                <li><strong>Pronunciación:</strong> English Pronunciation in Use Advanced.</li>
                <li><strong>Lectura:</strong> libros originales sin adaptar, de lo que te guste.</li>
                </ul>
                <p>Si preparas un examen oficial de B1, B2 o C1, existen series pensadas para eso, como <em>Destination</em> (Malcolm Mann y Steve Taylore-Knowles, Macmillan), que combinan gramática y vocabulario por nivel. Úsalas junto al material específico del examen.</p>

                <h2 id="estudiar-solo">Cómo sacarle partido a un libro de inglés si estudias solo</h2>
                <p>Comprar el libro es la parte fácil. Estas son las costumbres que separan el libro que te cambia el inglés del que acaba de posavasos:</p>
                <ol>
                <li><strong>Empieza por tus errores, no por la página 1.</strong> En un libro de gramática, ve directo a las unidades de lo que fallas. El orden del índice está pensado para una clase, no para ti.</li>
                <li><strong>Escribe las respuestas fuera del libro.</strong> En un cuaderno o en una hoja. Así puedes repetir los ejercicios una semana después y comprobar si lo has aprendido o solo lo habías entendido.</li>
                <li><strong>Corrige en el momento y apunta el porqué.</strong> Un error sin explicación vuelve.</li>
                <li><strong>Di los ejemplos en voz alta.</strong> También en el libro de gramática. Leer en silencio entrena los ojos; tú necesitas entrenar la boca.</li>
                <li><strong>Convierte cada unidad en tres frases tuyas.</strong> Sobre tu trabajo, tu familia o tus planes. Lo personal se recuerda.</li>
                <li><strong>Poco y a menudo.</strong> Veinte minutos al día rinden más que tres horas el domingo.</li>
                <li><strong>Con audio, grábate y compara.</strong> Diez segundos tuyos frente al original. Duele un poco. Funciona.</li>
                <li><strong>Usa la IA como profesor de guardia.</strong> Si una explicación no te entra, pide a un asistente que te la explique con otros ejemplos o que te prepare más ejercicios. Tienes ideas en <a href="/articulos/prompts-aprender-ingles-ia.html">prompts para aprender inglés con IA</a>.</li>
                </ol>
                <p>Y combina siempre el libro con inglés real: series, podcasts, conversaciones. El libro te da la estructura; el oído y la soltura salen de escuchar y hablar. Si no sabes por dónde empezar con la pronunciación, la <a href="/articulos/guia-pronunciacion-ingles-espanoles.html">guía gratis de pronunciación para españoles</a> y las <a href="/articulos/vocales-ingles-cortas-largas.html">vocales que más nos confunden</a> son un buen primer paso.</p>
        """,
    },
    {
        "slug": "prompts-aprender-ingles-ia",
        "category": "Recursos",
        "title": "Prompts para aprender inglés con ChatGPT, Claude o Gemini: 12 listos para copiar",
        "seo_title": "Prompts para aprender inglés con ChatGPT, Claude o Gemini",
        "description": "Prompts para aprender inglés con ChatGPT, Gemini, Claude o Copilot: 12 listos para copiar, cómo practicar speaking por voz y un plan semanal.",
        "lede": "Conversación, entrevistas, role-plays, emails, pronunciación y gramática: instrucciones concretas para que la IA te corrija de verdad, y lo que conviene saber de sus límites.",
        "reading": "10 minutos",
        "published": "2026-10-11",
        "from_book": False,
        "toc": [
            ("como-practicar", "Texto y voz"),
            ("limites", "Límites de la IA"),
            ("prompts", "12 prompts"),
            ("speaking", "Practicar speaking"),
            ("plan-semanal", "Plan semanal"),
        ],
        "related": [
            "libros-para-aprender-ingles",
            "alfabeto-fonetico-ingles",
            "guia-pronunciacion-ingles-espanoles",
            "how-are-you-respuestas-ingles",
        ],
        "quick_answer": "Para aprender inglés con ChatGPT, Gemini, Claude o Copilot, usa un <strong>prompt</strong> que fije su papel (compañero, entrevistador, profesor), tu nivel y cómo quieres que te corrija; por ejemplo: <em>Have a conversation with me and correct my most important mistake after each message.</em> Para practicar speaking, usa el modo de voz, pero toma su feedback de pronunciación como orientativo.",
        "faq": [
            ("¿Es gratis practicar inglés con ChatGPT?", "Se puede empezar gratis: ChatGPT, Gemini, Claude y Copilot tienen versiones gratuitas con las que funcionan estos prompts. Eso sí, los límites de uso y las funciones de voz de cada versión cambian con frecuencia, así que consulta las condiciones actuales en la web oficial de cada herramienta."),
            ("¿Puede ChatGPT corregir mi pronunciación?", "Solo de forma aproximada. En modo texto no te oye, así que no puede evaluarla; en modo voz puede darte pistas, pero a veces no detecta errores o señala otros que no existen. Para la pronunciación, compárate con audios reales y con la transcripción IPA de un diccionario."),
            ("¿Qué IA es mejor para aprender inglés: ChatGPT, Gemini, Claude o Copilot?", "Para practicar con prompts como estos, cualquiera de ellas sirve; la diferencia pesa menos que la calidad del prompt y la constancia. Prueba dos durante una semana y quédate con la que te resulte más cómoda, sobre todo en modo voz."),
            ("¿Cuánto tiempo al día debo practicar inglés con IA?", "Bastan 10-20 minutos diarios si los dedicas a hablar o escribir tú, no a leer respuestas largas. Es mejor poco cada día que una sesión larga a la semana."),
            ("¿Puedo fiarme de las correcciones de la IA?", "Normalmente son útiles, pero no infalibles: la IA puede explicar mal una regla o dar una IPA incorrecta con total seguridad. Si algo te sorprende, pídele que lo justifique y compruébalo en un diccionario fiable."),
        ],
        "body": """
                <p>Practicar inglés con ChatGPT, Gemini, Claude o Copilot puede ser la forma más cómoda de hablar inglés cada día: sin horarios, sin vergüenza y sin nadie mirando. Pero la diferencia entre una práctica útil y una charla de cortesía con un asistente que a todo te responde “Great job!” está en el prompt, las instrucciones que le das al principio.</p>
                <p>Aquí tienes cómo usar la IA para practicar (por texto y por voz), lo que no hace bien, 12 prompts para aprender inglés listos para copiar y un plan semanal. Los prompts están en inglés a propósito: así la IA te responde en inglés desde la primera línea. Solo tienes que cambiar lo que va entre corchetes.</p>
                <h2 id="como-practicar">¿Cómo practicar inglés con ChatGPT y otras IA?</h2>
                <p>Tienes dos formas de practicar, y conviene combinarlas:</p>
                <div class="example-grid">
                    <div class="mini-card"><strong>Modo texto</strong><span>Ideal para gramática, vocabulario, emails y correcciones detalladas. Tienes tiempo para pensar y la corrección queda por escrito para repasarla.</span></div>
                    <div class="mini-card"><strong>Modo voz</strong><span>La mayoría de asistentes ofrecen algún modo de conversación por voz, sobre todo en sus apps para el móvil. Es lo más parecido a hablar con alguien: entrenas listening, fluidez y reacción.</span></div>
                </div>
                <p>Un truco para el modo voz: escribe primero el prompt en el chat y, si tu app lo permite, pasa a voz en esa misma conversación. Así la IA sigue tus instrucciones mientras habláis. Las funciones de cada herramienta cambian a menudo; si no encuentras una opción, consulta la ayuda oficial de tu app.</p>
                <div class="lesson-box"><strong>Regla de oro:</strong> pide respuestas cortas. Si la IA suelta párrafos de diez líneas, tú hablas poco, y lo que te hace mejorar es hablar tú.</div>
                <h2 id="limites">¿Qué no hace bien la IA cuando practicas inglés?</h2>
                <ul>
                    <li><strong>En modo texto no te oye.</strong> Solo lee lo que escribes. Si usas el dictado del móvil, recibe la transcripción, y el reconocimiento de voz suele “arreglar” lo que dijiste: tus errores de pronunciación desaparecen antes de llegar a la IA.</li>
                    <li><strong>En modo voz, su opinión sobre tu pronunciación es aproximada.</strong> Puede pasar por alto errores claros o señalar otros que no existen. Tómalo como orientación, no como diagnóstico. Una pista útil: si entiende una palabra distinta de la que dijiste, probablemente ese sonido necesita trabajo (o había ruido).</li>
                    <li><strong>Se equivoca con total seguridad.</strong> A veces explica mal una regla, se inventa un matiz o da una transcripción IPA incorrecta. Comprueba lo importante en un diccionario como el <a href="https://dictionary.cambridge.org/es/" target="_blank" rel="noopener noreferrer">Diccionario Cambridge</a>.</li>
                    <li><strong>Tiende a ser demasiado amable.</strong> Si no le pides expresamente que te corrija, muchas veces no lo hará. Por eso todos los prompts de abajo lo piden.</li>
                    <li><strong>Privacidad.</strong> No compartas datos personales: ni tu nombre completo, ni tu dirección, ni información de tu empresa o de clientes. Si pegas un email o tu CV, quita antes nombres y cifras, y revisa la configuración de privacidad e historial de tu cuenta.</li>
                </ul>
                <p>Para la pronunciación, combina la IA con modelos de audio fijos: los <a href="/audios.html">audios de pronunciación</a> de esta web y el <a href="/articulos/alfabeto-fonetico-ingles.html">alfabeto fonético inglés</a> te dan una referencia que no cambia de una respuesta a otra.</p>
                <h2 id="prompts">12 prompts para aprender inglés con IA (listos para copiar)</h2>
                <p>Funcionan en ChatGPT, Gemini, Claude, Copilot y cualquier asistente parecido. Copia el texto completo, rellena los corchetes y envíalo como primer mensaje de una conversación nueva.</p>
                <div class="lesson-box"><strong>1. Compañero de conversación:</strong> Para charlar a diario con correcciones breves. Si quieres una versión más completa, con botón de copiar, usa <a href="/prompt.html">nuestro prompt para practicar inglés con IA</a>.<br><br>I'm a Spanish speaker from Spain and I want to practise my English. Have a natural conversation with me about [topic]. Ask me one question at a time and keep your replies short (2-4 sentences). After each of my messages, correct my most important mistake and suggest a more natural way to say it. Adjust your English to my level.</div>
                <div class="lesson-box"><strong>2. Entrevista de trabajo:</strong> Para preparar una entrevista en inglés. Usa un puesto real, pero no tu nombre ni datos de empresas concretas.<br><br>Act as a hiring manager interviewing me for a [job title] position at [type of company]. Ask me one typical interview question at a time, starting with 'Tell me about yourself', and wait for my answer. After each answer, give me short feedback in Spanish on grammar, vocabulary and how convincing I sound, and then show me an improved version in English. At the end, tell me the three things I should improve before a real interview.</div>
                <div class="lesson-box"><strong>3. Role-play: restaurante, aeropuerto, médico:</strong> Para ensayar situaciones reales sin presión. Funciona especialmente bien en modo voz.<br><br>Let's do a role-play. You are [a waiter in a London restaurant / a check-in agent at an airport / a doctor] and I am [the customer / the passenger / the patient]. Stay in character and speak like a real person would, using common everyday expressions. Don't interrupt the scene to correct me. When I write 'END', give me a list of my mistakes and of the phrases that sounded unnatural, with a better alternative for each one.</div>
                <div class="lesson-box"><strong>4. Corrección de errores explicada en español:</strong> Para entender tus errores, no solo verlos corregidos.<br><br>I'm going to write sentences in English. For each one: 1) write the corrected version, 2) explain every mistake in Spanish, briefly and simply, 3) tell me if it's a typical mistake for Spanish speakers and why (for example, a literal translation from Spanish). If a sentence is already correct, say so and suggest a more natural alternative if there is one.</div>
                <div class="lesson-box"><strong>5. Revisión de emails:</strong> Para mensajes de trabajo. Quita antes nombres, cifras y cualquier dato confidencial.<br><br>Here is an email I wrote in English: [paste your email]. It's for [a client / my manager / a colleague] and the tone should be [formal / friendly but professional]. Correct it and make it sound natural to a native speaker without changing my meaning. Then show the main changes in a table with three columns: my version, improved version and why (explained in Spanish).</div>
                <div class="lesson-box"><strong>6. Vocabulario de un tema:</strong> Para aprender las palabras que de verdad vas a usar. Comprueba la IPA en un diccionario: aquí la IA a veces falla.<br><br>Give me the 15 most useful words and expressions to talk about [topic, e.g. my job in marketing / renting a flat / football]. For each one, include the IPA pronunciation (British and American if they differ), the Spanish translation and a natural example sentence. Warn me about any false friends for Spanish speakers. Then quiz me on them, one at a time.</div>
                <div class="lesson-box"><strong>7. Guion para listening y shadowing:</strong> Para tener material a tu medida. Escúchalo con la lectura en voz alta de tu app, si la tiene, y repite detrás imitando el ritmo.<br><br>Write a natural dialogue of about 150 words between two friends [planning a weekend trip], at [B1 / B2] level. Use contractions and everyday expressions such as 'gonna' or 'kind of' where they sound natural. Then rewrite it marking the stressed words in CAPITALS and joining with hyphens the words that are usually linked in fast speech (for example, 'pick-it-up').</div>
                <div class="lesson-box"><strong>8. Phrasal verbs:</strong> Para que los phrasal verbs te salgan al hablar, no solo al leerlos.<br><br>Quiz me on common phrasal verbs used in everyday conversation (with get, take, put, come, go and look). Give me one sentence in Spanish at a time and I'll translate it into English using a phrasal verb. Tell me if my answer is correct and natural, and give me a better option if there is one. Keep score and make it harder every five questions.</div>
                <div class="lesson-box"><strong>9. Pares mínimos de pronunciación con IPA:</strong> Para entrenar los sonidos que más confundimos. En modo texto la IA no te oye: di cada palabra en voz alta y compárala con audios reales.<br><br>Create a pronunciation drill with minimal pairs for sounds that Spanish speakers often confuse: /ɪ/ vs /iː/ (ship, sheep), /æ/ vs /ʌ/ (cap, cup), /b/ vs /v/ (berry, very) and /d/ vs /ð/ (day, they). For each pair, give the IPA and a short sentence with each word. Then test me: write sentences with a gap and two options, and I'll choose the word that fits.</div>
                <div class="lesson-box"><strong>10. Test de nivel:</strong> Para hacerte una idea de tu nivel. Es una estimación orientativa, no un certificado oficial.<br><br>Give me a quick English level test with 15 questions that get progressively harder (grammar, vocabulary and reading comprehension). Ask one question at a time and don't tell me the answers until the end. Then estimate my level on the CEFR scale (A1-C2), explain in Spanish what I did well and what I should study next, and suggest a four-week study plan.</div>
                <div class="lesson-box"><strong>11. Profesor de gramática para hispanohablantes:</strong> Para entender la gramática desde el español. Contrasta después con artículos como <a href="/articulos/make-vs-do.html">make vs do</a> o <a href="/articulos/some-vs-any.html">some vs any</a>.<br><br>Act as an English teacher who speaks Spanish and knows the typical mistakes of learners from Spain. Explain [the present perfect / make vs do / some vs any] in Spanish, comparing it with Spanish grammar when that helps. Use simple language, give five examples with their translation, point out where the Spanish logic does NOT work in English, and finish with five sentences for me to complete.</div>
                <div class="lesson-box"><strong>12. Rutina diaria de 10 minutos:</strong> Para crear el hábito. Vuelve siempre a la misma conversación: según la herramienta y tu configuración, la IA puede no recordar chats anteriores.<br><br>Be my 10-minute daily English coach. Every time I write 'START', give me: 1) one useful everyday expression with an example, 2) three questions for me to answer in full sentences, and 3) corrections of my answers plus a mini challenge for the next day. Keep track of the expressions you teach me in this chat and include one of them for review every day.</div>
                <p>Para sacar partido al guion del prompt 7, repasa antes cómo se unen las palabras en <a href="/articulos/ligar-palabras-ingles.html">gonna, wanna, gotta y compañía</a> y escucha un ejemplo real como <a href="/audio/pick-it-up.html">pick it up</a>. Para el prompt 9, compara con <a href="/audio/bit-big-win-lip-clip.html">bit, big, win, lip y clip</a> y con <a href="/audio/sonido-th-paladar.html">day frente a they</a>.</p>
                <h2 id="speaking">¿Cómo practicar inglés hablado con ChatGPT?</h2>
                <p>Para practicar speaking en inglés con ChatGPT (o con cualquier otra IA con modo de voz), sigue esta secuencia:</p>
                <ol>
                    <li>Escribe el prompt 1 o el 3 y añade al final: <em>Speak slowly and keep your answers short.</em></li>
                    <li>Cambia a modo voz en la misma conversación.</li>
                    <li>Habla 10 minutos sin miedo a equivocarte. Si te bloqueas, pregunta <em>How do you say [palabra] in English?</em> y sigue.</li>
                    <li>Al terminar, vuelve al texto y pide: <em>Summarise my three most important mistakes from this conversation and give me five sentences to practise them.</em></li>
                    <li>Di esas cinco frases en voz alta varias veces y grábate una vez para comparar.</li>
                </ol>
                <div class="lesson-box"><strong>Si te da vergüenza hablar:</strong> empieza por respuestas cortas a saludos reales, como <a href="/audio/hows-it-going.html">How's it going?</a> y <a href="/audio/pretty-good.html">Pretty good</a>. La IA no se cansa de repetir la misma conversación diez veces, y eso es justo lo que necesitas al principio.</div>
                <h2 id="plan-semanal">Plan semanal: unos 20 minutos al día</h2>
                <p>Un ejemplo para combinar los prompts sin repetir siempre lo mismo:</p>
                <table class="data-table">
                    <thead>
                        <tr><th>Día</th><th>Prompt</th><th>Objetivo</th></tr>
                    </thead>
                    <tbody>
                        <tr><td>Lunes</td><td>1. Conversación (voz)</td><td>Fluidez y confianza</td></tr>
                        <tr><td>Martes</td><td>6. Vocabulario + 8. Phrasal verbs</td><td>Vocabulario útil</td></tr>
                        <tr><td>Miércoles</td><td>3. Role-play (voz)</td><td>Situaciones reales</td></tr>
                        <tr><td>Jueves</td><td>11. Gramática + 4. Corrección</td><td>Precisión</td></tr>
                        <tr><td>Viernes</td><td>5. Email o texto propio</td><td>Escritura</td></tr>
                        <tr><td>Sábado</td><td>7. Shadowing + 9. Pares mínimos</td><td>Listening y pronunciación</td></tr>
                        <tr><td>Domingo</td><td>12. Rutina de 10 minutos o descanso</td><td>Repaso</td></tr>
                    </tbody>
                </table>
                <p>Cada cuatro semanas, repite el test de nivel (prompt 10) para ver la evolución, sabiendo que es solo una estimación. Y recuerda que la IA es un gimnasio, no el partido: sirve para llegar a las conversaciones con personas reales con más soltura, no para sustituirlas. Si además te gusta aprender leyendo, tienes ideas en <a href="/articulos/libros-para-aprender-ingles.html">libros para aprender inglés</a>.</p>
        """,
    },
]


ARTICLE_BY_SLUG = {article["slug"]: article for article in ARTICLES}

ARTICLE_CLUSTERS = [
    {
        "key": "pronunciacion",
        "title": "Pronunciación clara",
        "description": "Sonidos, letras mudas y palabras que un hispanohablante suele leer con reglas españolas.",
        "categories": {"Pronunciación"},
    },
    {
        "key": "conversacion",
        "title": "Conversación natural",
        "description": "Respuestas, muletillas y expresiones que aparecen en conversaciones reales.",
        "categories": {"Conversación"},
    },
    {
        "key": "gramatica-real",
        "title": "Gramática real",
        "description": "Reglas útiles explicadas desde el uso diario, no desde frases artificiales de workbook.",
        "categories": {"Gramática real"},
    },
    {
        "key": "preposiciones",
        "title": "Preposiciones",
        "description": "Guías para dejar de traducir palabra por palabra y elegir la preposición por contexto.",
        "categories": {"Preposiciones"},
    },
    {
        "key": "recursos",
        "title": "Recursos para estudiar",
        "description": "Libros, prompts de IA y métodos para practicar inglés por tu cuenta con cabeza.",
        "categories": {"Recursos"},
    },
    {
        "key": "vocabulario",
        "title": "Vocabulario y falsos amigos",
        "description": "Palabras que parecen fáciles, pero cambian mucho por matiz, uso o traducción falsa.",
        "categories": {"Falsos amigos", "Vocabulario"},
    },
]


def article_cluster(article: dict) -> dict:
    for cluster in ARTICLE_CLUSTERS:
        if article["category"] in cluster["categories"]:
            return cluster
    return ARTICLE_CLUSTERS[-1]


def render_related(slug: str) -> str:
    article = ARTICLE_BY_SLUG[slug]
    items = []
    for related_slug in article["related"]:
        related = ARTICLE_BY_SLUG[related_slug]
        items.append(
            f'                        <li><a href="/articulos/{related_slug}.html">{esc(related["title"])}</a></li>'
        )
    return "\n".join(items)


def render_toc(article: dict) -> str:
    entries = list(article["toc"])
    if article.get("faq"):
        entries.append(("preguntas-frecuentes", "Preguntas frecuentes"))
    items = "\n".join(
        f'                        <li><a href="#{esc(anchor)}">{esc(label)}</a></li>'
        for anchor, label in entries
    )
    return f"""<div class="toc">
                    <p><strong>En esta guía</strong></p>
                    <ol>
{items}
                    </ol>
                </div>"""


def render_article_download(article: dict) -> str:
    pdf_path = article.get("download_pdf")
    if not pdf_path:
        return ""
    return f"""
                <div class="download-card">
                    <div>
                        <p class="eyebrow">PDF gratis</p>
                        <h2>Descarga la guía para compartir o imprimir.</h2>
                        <p>La versión PDF resume los 25 tips, incluye enlaces a los audios y un QR para abrir la guía online.</p>
                    </div>
                    <a class="button secondary" href="{esc(pdf_path)}" download>Descargar PDF</a>
                </div>
"""


def article_dates(article: dict) -> tuple[str, str]:
    published = article.get("published", FIRST_PUBLISHED)
    return published, article.get("updated", TODAY)


def render_article(article: dict) -> str:
    slug = article["slug"]
    path = f"/articulos/{slug}.html"
    canonical = f"{BASE_URL}{path}"
    published, updated = article_dates(article)
    body_html = wrap_tables(
        f"{render_quick_answer(article.get('quick_answer'))}{render_article_download(article)}"
        f"{article['body'].rstrip()}\n{render_faq(article.get('faq'))}"
    )
    trail = [("Inicio", "/"), ("Artículos", "/articulos.html"), (article["title"], path)]
    graph = [
        {
            "@type": "Article",
            "@id": f"{canonical}#article",
            "headline": article["title"],
            "description": article["description"],
            "image": {"@type": "ImageObject", "url": OG_IMAGE, "width": 1200, "height": 630},
            "author": schema_author(),
            "publisher": schema_publisher(),
            "datePublished": published,
            "dateModified": updated,
            "mainEntityOfPage": {"@type": "WebPage", "@id": canonical},
            "isPartOf": {"@id": WEBSITE_ID},
            "articleSection": article["category"],
            "inLanguage": "es",
            "isAccessibleForFree": True,
        },
        schema_breadcrumbs(trail),
    ]
    if article.get("faq"):
        graph.append(schema_faq(article["faq"]))
    schema = {"@context": "https://schema.org", "@graph": graph}
    if article.get("from_book", True):
        origin = f"Adaptado de ideas del libro <strong>{BOOK_TITLE}</strong>. "
    else:
        origin = ""
    if published == updated:
        dates = f'Publicado el <time datetime="{published}">{human_date(published)}</time>'
    else:
        dates = (
            f'Actualizado el <time datetime="{updated}">{human_date(updated)}</time> '
            f'(publicado el {human_date(published)})'
        )
    return f"""<!DOCTYPE html>
<html lang="es">
{page_head(title=article["seo_title"], description=article["description"], canonical=canonical, og_type="article", schema=schema, published=published, modified=updated)}
<body>
    {site_header("articulos")}

    <main>
        <section class="hero">
            <div class="hero-inner">
                <div>
                    {render_breadcrumbs(trail)}
                    <p class="eyebrow">{esc(article["category"])}</p>
                    <h1>{esc(article["title"])}</h1>
                    <p class="lede">{esc(article["lede"])}</p>
                </div>
                {cover_img("hero-cover", eager=True)}
            </div>
        </section>

        <div class="page-shell article-layout">
            <article class="article-body">
                <p class="article-meta byline">Por <a href="/contacto.html" rel="author">{AUTHOR}</a>, autor de <em>{BOOK_TITLE}</em>. {dates}. {origin}Lectura: {esc(article["reading"])}.</p>
{body_html}

                <div class="related">
                    <h2>También te interesa</h2>
                    <ul>
{render_related(slug)}
                        <li><a href="/audios.html">Escuchar audios del libro</a></li>
                    </ul>
                </div>
            </article>

            <aside class="sidebar" aria-label="Recursos relacionados">
                {render_toc(article)}
                <div class="panel">
                    {cover_img("")}
                    <p>{"El libro desarrolla este tema con más ejemplos, audios y contexto para hispanohablantes." if article.get("from_book", True) else "De FAK a Fluent: pronunciación y conversación real para hispanohablantes, con audios gratis."}</p>
                    <a class="button primary" href="{AMAZON_URL}" target="_blank" rel="noopener noreferrer">Comprar el libro</a>
                </div>
            </aside>
        </div>
    </main>

    {site_footer()}
</body>
</html>"""


def render_article_hub() -> str:
    nav_links = "\n".join(
        f'                    <a href="#{cluster["key"]}">{esc(cluster["title"])}</a>'
        for cluster in ARTICLE_CLUSTERS
        if any(article_cluster(article)["key"] == cluster["key"] for article in ARTICLES)
    )
    sections = []
    for cluster in ARTICLE_CLUSTERS:
        group = [article for article in ARTICLES if article_cluster(article)["key"] == cluster["key"]]
        if not group:
            continue
        cards = []
        for article in group:
            cards.append(
                f"""                    <a class="article-card" href="/articulos/{article["slug"]}.html">
                        <span>{esc(article["category"])}</span>
                        <h3>{esc(article["title"])}</h3>
                        <p>{esc(article["lede"])}</p>
                    </a>"""
            )
        sections.append(
            f"""            <section id="{cluster["key"]}" class="article-section">
                <div class="section-heading">
                    <p class="eyebrow">Cluster</p>
                    <h2>{esc(cluster["title"])}</h2>
                    <p>{esc(cluster["description"])}</p>
                </div>
                <div class="hub-grid">
{chr(10).join(cards)}
                </div>
            </section>"""
        )
    description = (
        f"{len(ARTICLES)} guías de inglés para hispanohablantes: pronunciación, conversación real, "
        "gramática, falsos amigos y recursos, con audios y ejemplos."
    )
    trail = [("Inicio", "/"), ("Artículos", "/articulos.html")]
    schema = {
        "@context": "https://schema.org",
        "@graph": [
            {
                "@type": "CollectionPage",
                "@id": f"{BASE_URL}/articulos.html",
                "name": "Artículos para aprender inglés",
                "description": description,
                "url": f"{BASE_URL}/articulos.html",
                "inLanguage": "es",
                "isPartOf": {"@id": WEBSITE_ID},
                "mainEntity": {
                    "@type": "ItemList",
                    "itemListElement": [
                        {
                            "@type": "ListItem",
                            "position": index + 1,
                            "name": article["title"],
                            "url": f"{BASE_URL}/articulos/{article['slug']}.html",
                        }
                        for index, article in enumerate(ARTICLES)
                    ],
                },
            },
            schema_breadcrumbs(trail),
        ],
    }
    return f"""<!DOCTYPE html>
<html lang="es">
{page_head(title="Artículos para aprender inglés | De FAK a Fluent", description=description, canonical=f"{BASE_URL}/articulos.html", og_type="website", schema=schema)}
<body>
    {site_header("articulos")}

    <main>
        <section class="hero">
            <div class="hero-inner">
                <div>
                    {render_breadcrumbs(trail)}
                    <p class="eyebrow">Guías prácticas para hispanohablantes</p>
                    <h1>Inglés real explicado desde los errores que más cometemos en español.</h1>
                    <p class="lede">Estos artículos convierten ideas clave del libro en guías prácticas, enlazadas con audios y ejemplos para practicar pronunciación, conversación, gramática y vocabulario útil.</p>
                    <div class="button-row">
                        <a class="button primary" href="{AMAZON_URL}" target="_blank" rel="noopener noreferrer">Comprar el libro</a>
                        <a class="button secondary" href="/audios.html">Escuchar audios</a>
                    </div>
                </div>
                {cover_img("hero-cover", eager=True)}
            </div>
        </section>

        <section class="page-shell" aria-label="Artículos">
            <div class="cluster-nav" aria-label="Clusters de artículos">
{nav_links}
            </div>
{chr(10).join(sections)}
        </section>
    </main>

    {site_footer()}
</body>
</html>"""


def audio_files() -> list[str]:
    return sorted(path.name for path in (ROOT / "audios").glob("*.mp3"))


AUDIO_DATA_FILE = ROOT / "tools" / "audio_pronunciation.json"
AUDIO_DATA: dict = json.loads(AUDIO_DATA_FILE.read_text(encoding="utf-8")) if AUDIO_DATA_FILE.exists() else {}


def audio_entry(filename: str) -> dict:
    """Hand-written pronunciation notes (IPA, meaning, examples) for one recording."""
    return AUDIO_DATA.get(filename, {})


AUDIO_DISPLAY_OVERRIDES = {
    "doing.well.yourself.mp3": "Doing well, yourself?",
    "either.American_either.British.mp3": "Either: American vs. British",
    "hanging.mp3": "Hanging in there",
    "lack_lock_look_luke.mp3": "Lack, lock, look, Luke",
    "mountain_button_cotton_manhattan.mp3": "Mountain, button, cotton, Manhattan",
    "sonido.'th'.Entre.Dientes.mp3": "TH entre dientes",
    "sonido.'th'.Paladar.mp3": "TH frente a D: lengua en paladar",
}


AUDIO_SEO_LABEL_OVERRIDES = {
    "American_British_Australian_Irish_Spanish.mp3": "Acentos: American, British...",
    "Book_cook_look_foot_hook_took_cookie.(LOL).mp3": "Book/cook/look: error común",
    "Book_cook_look_foot_hook_took_cookie.(correcto).mp3": "Book/cook/look: correcto",
    "Could.have_should.have_would.have.mp3": "Could've, should've, would've",
    "Education_individual_gradual_schedule_procedure_residual.mp3": "Sonido J: education, schedule...",
    "Light_love_listen_like_late_learn_laugh.mp3": "L inicial: light, love, listen...",
    "Moon_food_room_school_tool_noodle_cool.mp3": "OO larga: moon, food, school...",
    "Out.of_kind.of_sort.of.mp3": "Outta, kinda, sorta",
    "Skill_goal_ball_full_world_call_feel_school.mp3": "L final: skill, goal, ball...",
    "Though_Through_Tough_Cough_Enough_Bough_Thought_Plough.mp3": "OUGH: though, through, tough...",
    "Walk_talk_half_calm_salmon_would_should_yolk_palm_chalk_walkie-talkie.mp3": "L muda: walk, talk, would...",
    "bit_big_win_lip_clip.mp3": "I corta: bit, big, win...",
    "door_floor_score_shore_roar_soar.mp3": "O larga: door, floor, score...",
    "texts_guests_desks_costs.mp3": "S final: texts, guests, desks...",
}


def audio_display_name(filename: str) -> str:
    if filename in AUDIO_DISPLAY_OVERRIDES:
        return AUDIO_DISPLAY_OVERRIDES[filename]
    stem = Path(filename).stem
    text = stem.replace("_", ", ").replace(".", " ")
    text = text.replace("(correcto)", "(correcto)").replace("(LOL)", "(LOL)")
    text = re.sub(r"\s+", " ", text).strip()
    return text[:1].upper() + text[1:]


def audio_seo_label(filename: str) -> str:
    if filename in AUDIO_SEO_LABEL_OVERRIDES:
        return AUDIO_SEO_LABEL_OVERRIDES[filename]
    name = audio_display_name(filename)
    if len(name) <= 42:
        return name
    return name[:39].rstrip(" ,") + "..."


def audio_seo_title(filename: str) -> str:
    if audio_entry(filename).get("seo_title"):
        return audio_entry(filename)["seo_title"]
    return f"{audio_seo_label(filename)} | Audio inglés"


def audio_category(filename: str) -> str:
    low = filename.lower()
    if any(key in low for key in ["going.to", "did.you", "want.to", "gotta", "let.me", "give.me", "could.have", "out.of", "tell.them", "take.it.off", "pick.it.up"]):
        return "Ligar palabras"
    if any(key in low for key in ["how", "what", "doing", "pretty", "hanging", "very.good"]):
        return "Conversación"
    if any(key in low for key in ["ough", "omb", "ove", "book_cook", "live_leave", "either"]):
        return "Palabras difíciles"
    if any(key in low for key in ["american_british", "spanish"]):
        return "Acentos"
    return "Pronunciación"


def audio_description(filename: str) -> str:
    if audio_entry(filename).get("description"):
        return audio_entry(filename)["description"]
    name = audio_seo_label(filename)
    category = audio_category(filename)
    if category == "Ligar palabras":
        return f"Practica cómo se liga en inglés hablado: {name}. Mini-transcript y práctica rápida para hispanohablantes."
    if category == "Conversación":
        return f"Practica una expresión real en inglés: {name}. Audio con mini-transcript y notas para hispanohablantes."
    if category == "Palabras difíciles":
        return f"Compara la pronunciación de {name}. Audio con mini-transcript, errores típicos y práctica rápida."
    return f"Practica pronunciación en inglés: {name}. Audio con mini-transcript, errores típicos y notas para españoles."


def audio_mini_transcript(filename: str) -> str:
    text = audio_display_name(filename)
    text = re.sub(r"\s+\((correcto|LOL)\)$", "", text)
    return text


def audio_focus_note(filename: str) -> str:
    if audio_entry(filename).get("focus"):
        return audio_entry(filename)["focus"]
    low = filename.lower()
    category = audio_category(filename)
    if "sonido.'th'.entre" in low:
        return "Trabaja la posición de la lengua para que el TH no se convierta en una D, T, S o Z española."
    if "sonido.'th'.paladar" in low:
        return "Compara la D de day, con la lengua en el paladar, frente al TH de they, donde la lengua se acerca a los dientes."
    if "though" in low:
        return "Compara palabras con grafía parecida pero sonidos distintos; aquí la ortografía no es una guía fiable."
    if any(key in low for key in ["bit_big", "hit"]):
        return "Practica la I corta inglesa, más relajada que una i española y distinta de la vocal larga de palabras como seat."
    if any(key in low for key in ["book_cook", "moon_food", "door_floor", "lack_lock", "love_clove", "live_leave"]):
        return "Entrena contrastes de vocales que para un español parecen pequeñas variaciones, pero para un nativo cambian la palabra."
    if any(key in low for key in ["walk_talk", "bomb_tomb"]):
        return "Ignora la letra muda y memoriza el bloque sonoro completo en lugar de leer letra por letra."
    if any(key in low for key in ["hello_hard", "how", "hanging"]):
        return "Mantén una H inicial suave, como echar vaho, sin convertirla en una jota española."
    if "texts_guests" in low:
        return "Añade la S final sin crear una sílaba extra; la palabra debe seguir sonando compacta."
    if "stop" in low:
        return "Empieza directamente con la S inicial, sin añadir una e española antes de la palabra."
    if "very.good" in low:
        return "Diferencia la V labiodental de la B española juntando dientes superiores y labio inferior."
    if any(key in low for key in ["jump_john", "education_individual"]):
        return "Practica el sonido J inglés y cómo algunas combinaciones con D se suavizan hacia un sonido parecido."
    if "yellow_young" in low:
        return "Haz que la Y inicial funcione como una i breve antes de la vocal siguiente."
    if "red_car" in low:
        return "Lleva la lengua hacia atrás para la R inglesa, sin vibrarla como una R fuerte española."
    if "american_british" in low or "either" in low:
        return "Escucha cómo cambia una pronunciación válida según el acento; no hay una única versión correcta."
    if category == "Ligar palabras":
        return "Practica la unión entre palabras para que la frase fluya como inglés hablado, no como palabras aisladas."
    if category == "Conversación":
        return "Trabaja entonación y ritmo conversacional para que la frase suene como una respuesta real, no recitada."
    return "Concéntrate en claridad, acento de palabra y en no dejar que la ortografía española decida el sonido."


def audio_mistake_note(filename: str) -> str:
    if audio_entry(filename).get("mistake"):
        return audio_entry(filename)["mistake"]
    low = filename.lower()
    category = audio_category(filename)
    if "sonido.'th'.entre" in low:
        return "El error más común es esconder la lengua y decir una D o T española. Si la lengua no participa, el sonido no sale."
    if "sonido.'th'.paladar" in low:
        return "El error típico es usar la D de day cuando quieres decir they, this o that. La diferencia está en mover la lengua del paladar hacia los dientes."
    if "though" in low:
        return "El error típico es hacer rimar todas las palabras con OUGH. Though, through, tough y thought no comparten una pronunciación única."
    if any(key in low for key in ["bit_big", "hit"]):
        return "Si usas una i española demasiado limpia, puedes acercarte a otra palabra inglesa y cambiar el significado."
    if any(key in low for key in ["book_cook", "moon_food"]):
        return "No pronuncies todas las dobles O como una u larga. Book y moon no tienen la misma vocal."
    if "love_clove" in low:
        return "No leas love y move como si fueran de la misma familia fonética solo porque terminan igual."
    if any(key in low for key in ["walk_talk", "bomb_tomb"]):
        return "La trampa es pronunciar la letra escrita. En estas palabras, verla no significa decirla."
    if category == "Ligar palabras":
        return "Si separas demasiado cada palabra, la frase puede ser correcta pero sonar poco natural y difícil de reconocer en listening."
    if category == "Conversación":
        return "Evita una entonación plana. En saludos y respuestas cortas, el tono transmite casi tanto como las palabras."
    return "El error más frecuente es practicar la palabra aislada y perder el sonido cuando aparece dentro de una frase real."


def audio_practice_steps(filename: str) -> list[str]:
    low = filename.lower()
    category = audio_category(filename)
    if "sonido.'th'.entre" in low:
        return [
            "Coloca la lengua entre los dientes antes de reproducir el audio.",
            "Escucha una vez sin repetir y nota si hay vibración de garganta.",
            "Repite despacio exagerando la lengua, luego reduce la exageración.",
            "Termina con una frase corta usando el mismo sonido.",
        ]
    if "sonido.'th'.paladar" in low:
        return [
            "Di day con la lengua tocando el paladar, justo detrás de los dientes.",
            "Escucha el contraste con they y fíjate en cómo cambia la posición de la lengua.",
            "Alterna day y they sin dejar que los dos sonidos se mezclen.",
            "Termina con una frase corta como they do it, manteniendo el TH separado de la D.",
        ]
    if any(key in low for key in ["bit_big", "book_cook", "moon_food", "door_floor", "lack_lock", "love_clove", "live_leave"]):
        return [
            "Escucha el contraste completo sin leer la lista.",
            "Repite en pares, alternando el sonido difícil con el sonido que sueles confundir.",
            "Grábate una vez y comprueba si las palabras siguen siendo distinguibles.",
            "Cierra leyendo una frase corta donde aparezca una de las palabras.",
        ]
    if any(key in low for key in ["walk_talk", "bomb_tomb"]):
        return [
            "Tacha mentalmente la letra muda antes de decir la palabra.",
            "Repite la serie completa sin añadir sonidos escritos.",
            "Haz una pausa breve y vuelve a repetirla a velocidad normal.",
            "Usa dos palabras en una frase propia para fijarlas.",
        ]
    if category == "Ligar palabras":
        return [
            "Escucha la frase completa y marca dónde se unen las palabras.",
            "Repite primero despacio, manteniendo la unión principal.",
            "Sube la velocidad sin separar artificialmente cada palabra.",
            "Di una frase parecida que usarías en una conversación real.",
        ]
    if category == "Conversación":
        return [
            "Escucha el audio fijándote en la entonación final.",
            "Repite como respuesta natural, no como palabra de vocabulario.",
            "Cambia el tono una vez: más amable, más cansado o más informal.",
            "Úsalo en un mini diálogo de dos líneas.",
        ]
    return [
        "Escucha el audio completo antes de leer la palabra.",
        "Repite dos veces imitando ritmo y acento.",
        "Aísla el sonido que más cuesta durante una repetición.",
        "Vuelve a la palabra o frase completa para cerrar la práctica.",
    ]


def render_audio_notes(filename: str) -> str:
    steps = "\n".join(f"                        <li>{esc(step)}</li>" for step in audio_practice_steps(filename))
    return f"""                <section class="practice-panel" aria-label="Notas de práctica">
                    <div class="practice-block">
                        <h2>Mini-transcript</h2>
                        <p class="transcript-line">{esc(audio_mini_transcript(filename))}</p>
                    </div>
                    <div class="practice-block">
                        <h2>Qué trabajar</h2>
                        <p>{esc(audio_focus_note(filename))}</p>
                    </div>
                    <div class="practice-block">
                        <h2>Error típico</h2>
                        <p>{esc(audio_mistake_note(filename))}</p>
                    </div>
                    <div class="practice-block">
                        <h2>Práctica rápida</h2>
                        <ol>
{steps}
                        </ol>
                    </div>
                </section>"""


def render_audio_pronunciation(filename: str) -> str:
    items = audio_entry(filename).get("items") or []
    if not items:
        return ""
    rows = "\n".join(
        f"""                        <tr>
                            <th scope="row" lang="en">{esc(item["en"])}</th>
                            <td><span class="ipa">{esc(item["us"])}</span></td>
                            <td><span class="ipa">{esc(item["uk"])}</span></td>
                            <td>{esc(item["es"])}</td>
                        </tr>"""
        for item in items
    )
    tips = "\n".join(
        f"""                    <li><strong lang="en">{esc(item["en"])}</strong>: {esc(item["pista"])}<br><em lang="en">{esc(item["ejemplo"])}</em> — {esc(item["ejemplo_es"])}</li>"""
        for item in items
    )
    return f"""                <h2 id="pronunciacion">Pronunciación (IPA) y significado</h2>
                <div class="table-wrap"><table class="data-table ipa-table">
                    <thead>
                        <tr><th scope="col">Inglés</th><th scope="col">EE. UU.</th><th scope="col">Reino Unido</th><th scope="col">Significado</th></tr>
                    </thead>
                    <tbody>
{rows}
                    </tbody>
                </table></div>
                <p class="table-note">¿No te suenan los símbolos? Tienes la tabla completa en el <a href="/articulos/alfabeto-fonetico-ingles.html">alfabeto fonético inglés para españoles</a>.</p>
                <h2 id="como-decirlo">Cómo decirlo bien</h2>
                <ul class="tip-list">
{tips}
                </ul>
"""


def related_articles_for_audio(filename: str) -> list[str]:
    category = audio_category(filename)
    low = filename.lower()
    if "sonido.'th'" in low:
        picks = ["sonido-th-ingles", "como-se-pronuncia-the", "pronunciacion-ingles-para-espanoles"]
    elif "33" in low:
        picks = ["sonido-th-ingles", "como-se-pronuncia-the", "palabras-ingles-mal-pronunciadas"]
    elif any(key in low for key in ["bit_big", "hit", "book_cook", "moon_food", "door_floor", "lack_lock", "love_clove", "live_leave", "bird_bear", "microsoft"]):
        picks = ["vocales-ingles-cortas-largas", "alfabeto-fonetico-ingles", "palabras-ingles-mal-pronunciadas"]
    elif any(key in low for key in ["walk_talk", "bomb_tomb", "light_love"]):
        picks = ["letras-mudas-ingles", "palabras-ingles-mal-pronunciadas", "pronunciacion-ingles-para-espanoles"]
    elif "texts_guests" in low:
        picks = ["pronunciacion-ed-ingles", "pronunciacion-ingles-para-espanoles", "ligar-palabras-ingles"]
    elif any(key in low for key in ["mcdonald", "focus", "fak_fuck", "stop", "spanish", "spain", "either", "education"]):
        picks = ["palabras-ingles-mal-pronunciadas", "pronunciacion-ingles-para-espanoles", "alfabeto-fonetico-ingles"]
    elif category == "Ligar palabras":
        picks = ["ligar-palabras-ingles", "i-mean-en-ingles", "pronunciacion-ingles-para-espanoles"]
    elif category == "Conversación":
        picks = ["how-are-you-respuestas-ingles", "como-decir-de-nada-en-ingles", "sure-en-ingles"]
    elif "ough" in low:
        picks = ["palabras-ough-pronunciacion-ingles", "sonido-th-ingles", "pronunciacion-ingles-para-espanoles"]
    elif category == "Palabras difíciles":
        picks = ["pronunciacion-ingles-para-espanoles", "vocales-ingles-cortas-largas", "palabras-ough-pronunciacion-ingles"]
    else:
        picks = ["pronunciacion-ingles-para-espanoles", "alfabeto-fonetico-ingles", "vocales-ingles-cortas-largas"]
    fallback = ["pronunciacion-ingles-para-espanoles", "vocales-ingles-cortas-largas", "ligar-palabras-ingles"]
    chosen = [slug for slug in picks if slug in ARTICLE_BY_SLUG]
    for slug in fallback:
        if len(chosen) >= 3:
            break
        if slug not in chosen:
            chosen.append(slug)
    return chosen


def render_audio_page(filename: str) -> str:
    slug = audio_slug(filename)
    path = f"/audio/{slug}.html"
    entry = audio_entry(filename)
    name = audio_display_name(filename)
    heading = entry.get("h1") or name
    canonical = f"{BASE_URL}{path}"
    src = f"/audios/{quote(filename)}"
    description = audio_description(filename)
    lede = entry.get("intro") or description
    category = audio_category(filename)
    dynamic_stem = quote(Path(filename).stem)
    related = "\n".join(
        f'                        <li><a href="/articulos/{slug}.html">{esc(ARTICLE_BY_SLUG[slug]["title"])}</a></li>'
        for slug in related_articles_for_audio(filename)
    )
    trail = [("Inicio", "/"), ("Audios", "/audios.html"), (name, path)]
    audio_object = {
        "@type": "AudioObject",
        "@id": f"{canonical}#audio",
        "name": name,
        "description": description,
        "contentUrl": f"{BASE_URL}/audios/{quote(filename)}",
        "encodingFormat": "audio/mpeg",
        "inLanguage": "en",
        "transcript": audio_mini_transcript(filename),
        "author": schema_author(),
        "isAccessibleForFree": True,
    }
    graph = [
        {
            "@type": "WebPage",
            "@id": canonical,
            "name": heading,
            "description": description,
            "url": canonical,
            "inLanguage": "es",
            "isPartOf": {"@id": WEBSITE_ID},
            "dateModified": TODAY,
            "mainEntity": {"@id": f"{canonical}#audio"},
        },
        audio_object,
        schema_breadcrumbs(trail),
    ]
    if entry.get("faq"):
        graph.append(schema_faq(entry["faq"]))
    schema = {"@context": "https://schema.org", "@graph": graph}
    faq_html = render_faq([(question, esc(answer)) for question, answer in entry.get("faq", [])])
    return f"""<!DOCTYPE html>
<html lang="es">
{page_head(title=audio_seo_title(filename), description=description, canonical=canonical, og_type="website", schema=schema)}
<body>
    {site_header("audios")}

    <main>
        <section class="hero compact-hero">
            <div class="hero-inner">
                <div>
                    {render_breadcrumbs(trail)}
                    <p class="eyebrow">{esc(category)}</p>
                    <h1>{esc(heading)}</h1>
                    <p class="lede">{esc(lede)}</p>
                    <div class="button-row">
                        <a class="button secondary" href="/audios.html">Ver todos los audios</a>
                        <a class="button primary" href="{AMAZON_URL}" target="_blank" rel="noopener noreferrer">Comprar el libro</a>
                    </div>
                </div>
                {cover_img("hero-cover", eager=True)}
            </div>
        </section>

        <div class="page-shell article-layout">
            <article class="article-body">
                <div class="audio-player-box">
                    <audio controls preload="metadata" src="{src}">
                        Tu navegador no soporta el elemento de audio.
                    </audio>
                </div>
                <p>Repite el audio varias veces en voz alta. La primera escucha debería centrarse en reconocer los sonidos; las siguientes, en imitar ritmo, acento y unión entre palabras.</p>
{render_audio_pronunciation(filename)}
{render_audio_notes(filename)}
                <div class="lesson-box">
                    <strong>Consejo de práctica:</strong> reproduce el audio, pausa, repite la frase completa y vuelve a escuchar. Si una palabra se te resiste, no la practiques sola durante demasiado tiempo: vuelve pronto a la frase completa.
                </div>
{faq_html}
                <p>También puedes abrir este audio en el <a href="/pronunciacion.html?word={dynamic_stem}">reproductor original con enlace compatible con QR</a>.</p>

                <div class="related">
                    <h2>Guías relacionadas</h2>
                    <ul>
{related}
                    </ul>
                </div>
            </article>

            <aside class="sidebar" aria-label="Recursos relacionados">
                <div class="panel">
                    {cover_img("")}
                    <p>Estos audios acompañan el método del libro para mejorar pronunciación y comprensión auditiva.</p>
                    <a class="button primary" href="{AMAZON_URL}" target="_blank" rel="noopener noreferrer">Comprar el libro</a>
                </div>
            </aside>
        </div>
    </main>

    {site_footer()}
</body>
</html>"""


def render_audio_hub(files: list[str]) -> str:
    category_order = ["Pronunciación", "Palabras difíciles", "Ligar palabras", "Conversación", "Acentos"]
    sections = []
    for category in category_order:
        group = [filename for filename in files if audio_category(filename) == category]
        if not group:
            continue
        cards = []
        for filename in group:
            slug = audio_slug(filename)
            name = audio_display_name(filename)
            items = audio_entry(filename).get("items") or []
            hint = f'<span class="ipa">{esc(items[0]["us"])}</span> · ' if items else ""
            cards.append(
                f"""                    <a class="audio-card" href="/audio/{slug}.html">
                        <span>{esc(category)}</span>
                        <strong>{esc(name)}</strong>
                        <small>{hint}Escuchar audio</small>
                    </a>"""
            )
        section_id = slugify(category)
        sections.append(
            f"""            <section id="{section_id}" class="audio-section">
                <h2>{esc(category)}</h2>
                <div class="audio-grid">
{chr(10).join(cards)}
                </div>
            </section>"""
        )
    item_list = [
        {
            "@type": "ListItem",
            "position": index + 1,
            "name": audio_display_name(filename),
            "url": f"{BASE_URL}/audio/{audio_slug(filename)}.html",
        }
        for index, filename in enumerate(files)
    ]
    description = (
        f"{len(files)} audios gratis de pronunciación en inglés para hispanohablantes, con transcripción fonética (IPA), "
        "significado y errores típicos de los españoles."
    )
    trail = [("Inicio", "/"), ("Audios", "/audios.html")]
    schema = {
        "@context": "https://schema.org",
        "@graph": [
            {
                "@type": "CollectionPage",
                "@id": f"{BASE_URL}/audios.html",
                "name": "Audios de pronunciación en inglés de De FAK a Fluent",
                "description": description,
                "url": f"{BASE_URL}/audios.html",
                "inLanguage": "es",
                "isPartOf": {"@id": WEBSITE_ID},
                "mainEntity": {"@type": "ItemList", "itemListElement": item_list},
            },
            schema_breadcrumbs(trail),
        ],
    }
    return f"""<!DOCTYPE html>
<html lang="es">
{page_head(title="Audios de pronunciación en inglés gratis | De FAK a Fluent", description=description, canonical=f"{BASE_URL}/audios.html", og_type="website", schema=schema)}
<body>
    {site_header("audios")}

    <main>
        <section class="hero">
            <div class="hero-inner">
                <div>
                    {render_breadcrumbs(trail)}
                    <p class="eyebrow">Biblioteca de audios</p>
                    <h1>Audios de pronunciación y conversación en inglés.</h1>
                    <p class="lede">{len(files)} audios gratis del libro, cada uno con su página: transcripción fonética (IPA) en inglés americano y británico, significado, el error típico de un español y una práctica rápida.</p>
                    <div class="button-row">
                        <a class="button primary" href="{AMAZON_URL}" target="_blank" rel="noopener noreferrer">Comprar el libro</a>
                        <a class="button secondary" href="/articulos/alfabeto-fonetico-ingles.html">Entender los símbolos IPA</a>
                    </div>
                </div>
                {cover_img("hero-cover", eager=True)}
            </div>
        </section>

        <div class="page-shell audio-list-page">
{chr(10).join(sections)}
        </div>
    </main>

    {site_footer()}
</body>
</html>"""


def sitemap_paths(files: list[str]) -> list[tuple[str, str, str, str]]:
    urls: list[tuple[str, str, str, str]] = [
        ("/", "1.00", "weekly", TODAY),
        ("/audios.html", "0.90", "weekly", TODAY),
        ("/articulos.html", "0.90", "weekly", TODAY),
        ("/contacto.html", "0.50", "yearly", TODAY),
        ("/prompt.html", "0.55", "yearly", TODAY),
    ]
    urls.extend(
        (f"/articulos/{article['slug']}.html", "0.85", "monthly", article_dates(article)[1]) for article in ARTICLES
    )
    urls.extend(
        (article["download_pdf"], "0.55", "monthly", FIRST_PUBLISHED) for article in ARTICLES if article.get("download_pdf")
    )
    urls.extend((f"/audio/{audio_slug(filename)}.html", "0.65", "monthly", TODAY) for filename in files)
    return urls


def render_sitemap(files: list[str]) -> str:
    entries = []
    for path, priority, changefreq, lastmod in sitemap_paths(files):
        loc = f"{BASE_URL}{path}"
        entries.append(
            f"""<url>
  <loc>{xml_escape(loc)}</loc>
  <lastmod>{lastmod}T00:00:00+00:00</lastmod>
  <changefreq>{changefreq}</changefreq>
  <priority>{priority}</priority>
</url>"""
        )
    return f"""<?xml version="1.0" encoding="UTF-8"?>
<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">
{chr(10).join(entries)}
</urlset>"""


def render_llms_txt(files: list[str]) -> str:
    """Plain-text map of the site for AI assistants (https://llmstxt.org)."""
    lines = [
        f"# {BOOK_TITLE}",
        "",
        f"> {BOOK_TITLE} es un libro de inglés para hispanohablantes escrito por {AUTHOR} (noviembre de 2024). "
        "Este sitio, librodeingles.com, es su complemento gratuito: guías en español sobre pronunciación inglesa, "
        "inglés de conversación real, gramática útil y falsos amigos, y una biblioteca de audios con "
        "transcripción fonética (IPA) pensada para los errores típicos de los españoles.",
        "",
        "Datos clave:",
        f"- Autor: {AUTHOR}, español que ha vivido y trabajado en inglés en Irlanda, Reino Unido y Estados Unidos. Perfil: {AUTHOR_URL}",
        "- Público: hispanohablantes con base de inglés que quieren pronunciar con más claridad y entender conversaciones reales. No es un curso para principiantes absolutos ni promete fluidez en 30 días.",
        "- Contenido del libro: más de 28.000 palabras y cerca de 100 ejemplos de audio; pronunciación, comprensión auditiva, expresiones naturales y matices culturales.",
        "- Ediciones: tapa blanda (ISBN 979-8-9918812-0-3, la más vendida) y tapa dura (ISBN 979-8-9918812-1-0).",
        f"- Compra: {AMAZON_URL}",
        f"- Guía gratuita en PDF: {BASE_URL}{PRONUNCIATION_GUIDE_PDF}",
        "",
    ]
    for cluster in ARTICLE_CLUSTERS:
        group = [article for article in ARTICLES if article_cluster(article)["key"] == cluster["key"]]
        if not group:
            continue
        lines.append(f"## {cluster['title']}")
        lines.append("")
        for article in group:
            lines.append(f"- [{article['title']}]({BASE_URL}/articulos/{article['slug']}.html): {article['description']}")
        lines.append("")
    lines.append("## Audios de pronunciación (con IPA)")
    lines.append("")
    for filename in files:
        lines.append(f"- [{audio_entry(filename).get('h1') or audio_display_name(filename)}]({BASE_URL}/audio/{audio_slug(filename)}.html)")
    lines += [
        "",
        "## Optional",
        "",
        f"- [Sobre el autor]({AUTHOR_URL})",
        f"- [Prompt para practicar inglés con IA]({BASE_URL}/prompt.html)",
        f"- [Mapa del sitio XML]({BASE_URL}/sitemap.xml)",
    ]
    return "\n".join(lines)


def render_not_found() -> str:
    schema = {"@context": "https://schema.org", "@type": "WebPage", "name": "Página no encontrada", "inLanguage": "es"}
    popular = [
        "guia-pronunciacion-ingles-espanoles",
        "pronunciacion-ingles-para-espanoles",
        "how-are-you-respuestas-ingles",
        "preposiciones-in-on-at",
        "make-vs-do",
        "sonido-th-ingles",
    ]
    links = "\n".join(
        f'                        <li><a href="/articulos/{slug}.html">{esc(ARTICLE_BY_SLUG[slug]["title"])}</a></li>'
        for slug in popular
        if slug in ARTICLE_BY_SLUG
    )
    return f"""<!DOCTYPE html>
<html lang="es">
{page_head(title="Página no encontrada | De FAK a Fluent", description="Esta página no existe. Encuentra guías de inglés y audios de pronunciación para hispanohablantes.", canonical=None, og_type="website", schema=schema, robots="noindex, follow")}
<body>
    {site_header("")}

    <main>
        <section class="hero compact-hero">
            <div class="hero-inner">
                <div>
                    <p class="eyebrow">Error 404</p>
                    <h1>Esta página no existe (o se ha mudado).</h1>
                    <p class="lede">Puede que el enlace esté mal escrito. Aquí tienes lo más útil del sitio para seguir practicando.</p>
                    <div class="button-row">
                        <a class="button primary" href="/">Ir al inicio</a>
                        <a class="button secondary" href="/audios.html">Audios de pronunciación</a>
                        <a class="button secondary" href="/articulos.html">Todos los artículos</a>
                    </div>
                </div>
                {cover_img("hero-cover", eager=True)}
            </div>
        </section>

        <div class="page-shell">
            <article class="article-body">
                <h2>Guías más leídas</h2>
                <ul>
{links}
                </ul>
            </article>
        </div>
    </main>

    {site_footer()}
</body>
</html>"""


def main() -> None:
    files = audio_files()
    audio_dir = ROOT / "audio"
    if audio_dir.exists():
        for path in audio_dir.glob("*.html"):
            path.unlink()
    write("articulos.html", render_article_hub())
    for article in ARTICLES:
        write(f"articulos/{article['slug']}.html", render_article(article))
    write("audios.html", render_audio_hub(files))
    for filename in files:
        write(f"audio/{audio_slug(filename)}.html", render_audio_page(filename))
    write("sitemap.xml", render_sitemap(files))
    write("llms.txt", render_llms_txt(files))
    write("404.html", render_not_found())
    write(f"{INDEXNOW_KEY}.txt", INDEXNOW_KEY)


if __name__ == "__main__":
    main()
