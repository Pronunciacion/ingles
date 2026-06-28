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
TODAY = "2026-06-28"
BOOK_TITLE = "De FAK a Fluent"
AUTHOR = "Javier Sanz"


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


def page_head(
    *,
    title: str,
    description: str,
    canonical: str,
    og_type: str,
    schema: dict,
) -> str:
    return f"""<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>{esc(title)}</title>
    <meta name="description" content="{esc(description)}">
    <link rel="canonical" href="{esc(canonical)}">
    <link rel="icon" type="image/png" sizes="32x32" href="/images/flag_ukus_32px.png">
    <link rel="icon" type="image/png" sizes="64x64" href="/images/flag_ukus_64px.png">
    <link rel="apple-touch-icon" sizes="64x64" href="/images/flag_ukus_64px.png">
    <meta property="og:title" content="{esc(title)}">
    <meta property="og:description" content="{esc(description)}">
    <meta property="og:image" content="{BASE_URL}/images/book-cover-600.png">
    <meta property="og:url" content="{esc(canonical)}">
    <meta property="og:type" content="{esc(og_type)}">
    <meta name="twitter:card" content="summary_large_image">
    <link rel="stylesheet" href="/styles.css">
    <script type="application/ld+json">
    {json_ld(schema)}
    </script>
    <script defer data-domain="librodeingles.com" src="https://plausible.io/js/script.manual.outbound-links.js"></script>
</head>"""


def site_header(active: str) -> str:
    items = [
        ("/", "Inicio", "inicio"),
        ("/audios.html", "Audios", "audios"),
        ("/articulos.html", "Artículos", "articulos"),
        ("/contacto.html", "Contacto", "contacto"),
    ]
    links = "\n".join(
        f'                <a href="{href}"{" aria-current=\"page\"" if key == active else ""}>{label}</a>'
        for href, label, key in items
    )
    return f"""<header class="site-header">
        <div class="nav-shell">
            <a class="brand" href="/">
                <img src="/images/flag_ukus_64px.png" alt="">
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
            <p>© Todos los derechos reservados</p>
            <a href="/contacto.html">Contacto</a>
        </div>
    </footer>"""


ARTICLES: list[dict] = [
    {
        "slug": "pronunciacion-ingles-para-espanoles",
        "category": "Pronunciación",
        "title": "Pronunciación en inglés para españoles: los errores que más bloquean",
        "seo_title": "Pronunciación en inglés para españoles | De FAK a Fluent",
        "description": "Errores de pronunciación en inglés frecuentes en españoles: vocales, H, TH y acento. Aprende qué practicar primero para que te entiendan.",
        "lede": "Si tu gramática es suficiente pero no te entienden, el problema casi nunca es una regla más: es sonido, ritmo y confianza al imitar.",
        "reading": "5 minutos",
        "toc": [
            ("por-que", "Por qué cuesta"),
            ("sonidos", "Sonidos clave"),
            ("acento", "Acento"),
            ("practica", "Práctica"),
        ],
        "related": [
            "palabras-ough-pronunciacion-ingles",
            "ligar-palabras-ingles",
            "how-are-you-respuestas-ingles",
        ],
        "body": """
                <p>La pronunciación es el filtro de entrada de una conversación. Puedes cometer errores de gramática y aun así comunicarte, pero si una palabra clave suena como otra palabra, o como algo que no existe en inglés, el interlocutor no tiene suficiente información para ayudarte.</p>
                <p>Para un español, el reto no es sonar perfecto ni borrar su acento. El objetivo útil es que las palabras importantes sean reconocibles para un hablante nativo. Eso se consigue priorizando los sonidos que más diferencia producen.</p>

                <h2 id="por-que">Por qué nos cuesta tanto</h2>
                <p>En español tenemos cinco vocales muy estables. En inglés, esas mismas letras pueden producir muchos más sonidos. Por eso dos palabras que a un español le parecen casi idénticas pueden sonar completamente distintas para un nativo.</p>
                <div class="lesson-box">
                    <strong>Regla práctica:</strong> no practiques palabras aisladas solo leyendo. Escucha, repite y compárate con el audio. El ojo manda demasiado cuando la ortografía inglesa no coincide con el sonido.
                </div>

                <h2 id="sonidos">Los sonidos que conviene atacar primero</h2>
                <div class="example-grid">
                    <div class="mini-card"><strong>La H inicial</strong><span>No es la jota española. Es más suave, como echar vaho en una ventana.</span></div>
                    <div class="mini-card"><strong>La I corta</strong><span>En palabras como <em>sit</em>, <em>bit</em> o <em>win</em>, se acerca más a una e española que a una i limpia.</span></div>
                    <div class="mini-card"><strong>La O corta</strong><span>Palabras comunes como <em>love</em> o <em>money</em> no se leen como una o española.</span></div>
                    <div class="mini-card"><strong>TH</strong><span>Puede sonar con vibración, como en <em>they</em>, o sin vibración, como en <em>think</em>.</span></div>
                </div>

                <h2 id="acento">Tu acento importa, pero no por postureo</h2>
                <p>En España muchas personas sienten vergüenza al pronunciar bien, como si imitar un acento inglés o americano fuera exagerado. Esa barrera social es cara: en una entrevista, llamada o reunión, una pronunciación clara transmite seguridad y reduce fricción.</p>
                <p>La meta no es parecer de Londres, Boston o Dublín. La meta es que tu interlocutor no tenga que descifrarte. Puedes conservar parte de tu acento español y, a la vez, trabajar los sonidos que desbloquean la comprensión.</p>

                <h2 id="practica">Cómo practicar sin perderte</h2>
                <ol>
                    <li>Elige un sonido, no veinte. Por ejemplo, la H inicial durante una semana.</li>
                    <li>Escucha pares de palabras donde el error cambie el significado.</li>
                    <li>Repite en voz alta, grabándote si puedes.</li>
                    <li>Practica dentro de frases completas para añadir ritmo natural.</li>
                </ol>
                <p>Empieza con los audios de <a href="/audio/hello-hard.html">hello y hard</a>, <a href="/audio/bit-big-win-lip-clip.html">bit, big, win, lip y clip</a>, y la colección de <a href="/audios.html">audios de pronunciación</a>.</p>
        """,
    },
    {
        "slug": "palabras-ough-pronunciacion-ingles",
        "category": "Pronunciación",
        "title": "Cómo pronunciar palabras con OUGH: though, through, tough y más",
        "seo_title": "OUGH en inglés: pronunciación de though, through y tough",
        "description": "Aprende cómo pronunciar palabras con OUGH en inglés: though, through, tough, cough, enough, bough, thought y plough.",
        "lede": "La ortografía inglesa no siempre avisa. OUGH puede sonar de formas muy distintas, así que estas palabras se aprenden mejor por familias y con audio.",
        "reading": "4 minutos",
        "toc": [
            ("lista", "Lista rápida"),
            ("errores", "Error típico"),
            ("metodo", "Método"),
            ("contexto", "Contexto"),
        ],
        "related": [
            "pronunciacion-ingles-para-espanoles",
            "actual-vs-actually",
            "ligar-palabras-ingles",
        ],
        "body": """
                <p>Si buscas una prueba rápida de que el inglés no se pronuncia como se escribe, mira la combinación <strong>ough</strong>. La misma secuencia aparece en palabras muy comunes, pero no mantiene un sonido único.</p>
                <p>La solución no es frustrarse ni buscar una regla perfecta. La solución práctica es agrupar, escuchar y memorizar las palabras de más uso.</p>

                <h2 id="lista">Lista rápida de palabras con OUGH</h2>
                <div class="example-grid">
                    <div class="mini-card"><strong>Though</strong><span>Aunque, sin embargo. En redes también verás <em>tho</em>.</span></div>
                    <div class="mini-card"><strong>Through</strong><span>A través de. En usos informales aparece como <em>thru</em>.</span></div>
                    <div class="mini-card"><strong>Tough</strong><span>Difícil, duro o resistente.</span></div>
                    <div class="mini-card"><strong>Cough</strong><span>Tos. Aparece en expresiones como <em>cough drops</em>.</span></div>
                    <div class="mini-card"><strong>Enough</strong><span>Suficiente. Muy frecuente en conversación.</span></div>
                    <div class="mini-card"><strong>Thought</strong><span>Pensamiento o pasado de <em>think</em>.</span></div>
                </div>

                <h2 id="errores">El error típico: hacerlas rimar</h2>
                <p>La tentación para un hispanohablante es leer todas estas palabras con un patrón estable. El problema es que <em>though</em>, <em>through</em>, <em>tough</em> y <em>thought</em> no funcionan como una familia fonética limpia.</p>
                <p>Por eso conviene practicar cada palabra dentro de una frase corta. No quieres recordar solo una transcripción aproximada; quieres que la boca la encuentre cuando estés hablando.</p>

                <h2 id="metodo">Método de práctica</h2>
                <ol>
                    <li>Escucha la lista completa sin leer, para que el sonido llegue antes que la ortografía.</li>
                    <li>Repite palabra por palabra, exagerando el sonido difícil.</li>
                    <li>Añade una frase mínima: <em>That was tough</em>, <em>I have enough</em>, <em>go through it</em>.</li>
                    <li>Vuelve al audio y comprueba si ya distingues los cambios.</li>
                </ol>
                <div class="lesson-box">
                    <strong>Practica ahora:</strong> escucha el audio de <a href="/audio/though-through-tough-cough-enough-bough-thought-plough.html">though, through, tough, cough, enough, bough, thought y plough</a>.
                </div>

                <h2 id="contexto">Por qué hay tantas excepciones</h2>
                <p>El inglés ha absorbido palabras y sonidos de muchos orígenes. Esa historia explica parte del caos: la ortografía conserva capas antiguas, mientras que la pronunciación cambió de manera desigual. Para aprenderlo, la memoria auditiva suele ser más fiable que la intuición visual.</p>
                <p>La buena noticia es que no necesitas dominar todas las excepciones a la vez. Empieza por las palabras que aparecen en conversaciones, vídeos, trabajo y viajes.</p>
        """,
    },
    {
        "slug": "how-are-you-respuestas-ingles",
        "category": "Conversación",
        "title": "Qué responder a How are you sin sonar como un workbook",
        "seo_title": "Qué responder a How are you en inglés | De FAK a Fluent",
        "description": "Respuestas naturales a How are you en inglés: I am good, doing well, pretty good, hanging in there y cuándo usar cada una.",
        "lede": "La respuesta correcta depende de contexto, país y relación. No necesitas una frase perfecta; necesitas varias respuestas naturales.",
        "reading": "5 minutos",
        "toc": [
            ("respuestas", "Respuestas"),
            ("pais", "Por país"),
            ("preguntas", "Preguntas"),
            ("plantillas", "Plantillas"),
        ],
        "related": [
            "pronunciacion-ingles-para-espanoles",
            "ligar-palabras-ingles",
            "make-vs-do",
        ],
        "body": """
                <p>Muchos españoles aprendieron una única respuesta para <em>How are you?</em>: <em>I am fine, thank you, and you?</em>. La frase existe y es correcta, pero en conversaciones reales puede sonar demasiado formal, automática o poco natural.</p>
                <p>En inglés, igual que en español, preguntar qué tal estás no siempre busca una respuesta profunda. A veces es un saludo, a veces abre una conversación y a veces solo mantiene la cortesía.</p>

                <h2 id="respuestas">Respuestas naturales a How are you</h2>
                <div class="example-grid">
                    <div class="mini-card"><strong>I am good</strong><span>Muy común en Estados Unidos para una respuesta breve y positiva.</span></div>
                    <div class="mini-card"><strong>Doing well</strong><span>Suena natural porque responde a la idea completa de <em>How are you doing?</em>.</span></div>
                    <div class="mini-card"><strong>Pretty good</strong><span>Informal, útil con compañeros o gente que ves a menudo.</span></div>
                    <div class="mini-card"><strong>Hanging in there</strong><span>Honesta y conversacional: no estás mal, pero tampoco celebrando la vida.</span></div>
                </div>

                <h2 id="pais">Diferencias por país</h2>
                <p>En Irlanda es habitual escuchar respuestas como <em>I am grand</em> o <em>not too bad</em>. En Estados Unidos se oyen mucho <em>I am good</em> y <em>doing well</em>. En Reino Unido puede aparecer más la respuesta formal, pero también respuestas cortas como <em>I am alright</em> o <em>very well</em>.</p>
                <p>No hace falta copiar un país entero. Lo útil es reconocer las variantes para no bloquearte cuando no escuches la fórmula del libro de texto.</p>

                <h2 id="preguntas">Otras formas de preguntar qué tal</h2>
                <ul>
                    <li><strong>How's it going?</strong> Informal, común con gente conocida.</li>
                    <li><strong>How've you been?</strong> Para alguien a quien no ves desde hace tiempo.</li>
                    <li><strong>What's up?</strong> Muy informal. Mejor con amigos o gente joven.</li>
                    <li><strong>How's your day going?</strong> Buena opción a mitad del día.</li>
                    <li><strong>How's everything?</strong> Invita a una respuesta un poco más amplia.</li>
                </ul>

                <h2 id="plantillas">Plantillas seguras</h2>
                <p>Si no sabes qué decir, usa respuestas cortas con una repregunta. Son naturales y no te obligan a improvisar demasiado.</p>
                <div class="lesson-box">
                    <p><strong>Contexto formal:</strong> I am doing well, thank you. And yourself?</p>
                    <p><strong>Contexto informal:</strong> Pretty good. How about you?</p>
                    <p><strong>Hace tiempo que no os veis:</strong> I've been good, thanks. What about you?</p>
                </div>
                <p>Practica la pronunciación con <a href="/audio/hows-it-going.html">How is it going?</a>, <a href="/audio/howve-you-been.html">How have you been?</a> y <a href="/audio/pretty-good.html">Pretty good</a>.</p>
        """,
    },
    {
        "slug": "make-vs-do",
        "category": "Gramática real",
        "title": "Make vs do: cuándo usar cada verbo si los dos significan hacer",
        "seo_title": "Make vs do: diferencia en inglés | De FAK a Fluent",
        "description": "Make vs do explicado para hispanohablantes: cuándo usar make, cuándo usar do y expresiones comunes que debes aprender juntas.",
        "lede": "En español decimos hacer para casi todo. En inglés, make y do dividen ese territorio, y la diferencia se aprende mejor con patrones.",
        "reading": "5 minutos",
        "toc": [
            ("do", "Usar do"),
            ("make", "Usar make"),
            ("matiz", "Make it"),
            ("aprender", "Aprender bloques"),
        ],
        "related": [
            "actual-vs-actually",
            "preposiciones-in-on-at",
            "how-are-you-respuestas-ingles",
        ],
        "body": """
                <p><strong>Make</strong> y <strong>do</strong> se traducen muchas veces como hacer, pero no son intercambiables. Si intentas traducir palabra por palabra desde español, tarde o temprano dirás una combinación que suena rara.</p>
                <p>La regla mental más útil es esta: <strong>do</strong> se asocia con realizar una acción o completar una tarea; <strong>make</strong> se asocia con crear, producir, causar o lograr algo.</p>

                <h2 id="do">Cuándo usar do</h2>
                <p>Usa <em>do</em> cuando el foco está en la actividad, el proceso o la tarea. No estás fabricando un objeto nuevo; estás llevando a cabo algo.</p>
                <div class="example-grid">
                    <div class="mini-card"><strong>do the dishes</strong><span>Fregar o lavar los platos.</span></div>
                    <div class="mini-card"><strong>do your homework</strong><span>Hacer los deberes.</span></div>
                    <div class="mini-card"><strong>do me a favor</strong><span>Hacerme un favor.</span></div>
                    <div class="mini-card"><strong>do research</strong><span>Investigar, llevar a cabo investigación.</span></div>
                </div>

                <h2 id="make">Cuándo usar make</h2>
                <p>Usa <em>make</em> cuando hay creación, resultado, efecto o consecución. A veces el resultado es físico, como comida; otras veces es abstracto, como una decisión o una diferencia.</p>
                <div class="example-grid">
                    <div class="mini-card"><strong>make a decision</strong><span>Tomar una decisión.</span></div>
                    <div class="mini-card"><strong>make money</strong><span>Ganar dinero.</span></div>
                    <div class="mini-card"><strong>make a mistake</strong><span>Cometer un error.</span></div>
                    <div class="mini-card"><strong>make progress</strong><span>Progresar.</span></div>
                </div>

                <h2 id="matiz">El matiz de make it</h2>
                <p><em>Make it</em> añade una idea de conseguir algo que no era automático. Puede hablar de llegar a tiempo, lograr entrar en un lugar, asistir a un evento o triunfar en un entorno competitivo.</p>
                <div class="lesson-box">
                    <p><strong>I made it to the airport on time.</strong> Llegué al aeropuerto a tiempo, probablemente con cierta dificultad.</p>
                    <p><strong>He made it in Hollywood.</strong> Logró triunfar en Hollywood.</p>
                    <p><strong>I could not make it to the party.</strong> No pude ir a la fiesta.</p>
                </div>

                <h2 id="aprender">Cómo aprenderlos sin memorizar listas infinitas</h2>
                <p>No intentes aprender make y do como una regla matemática. Aprende bloques frecuentes: <em>make sure</em>, <em>make sense</em>, <em>do your best</em>, <em>do nothing</em>. Cuando memorizas la combinación completa, la frase sale más rápido y con menos traducción mental.</p>
                <p>Luego añade tus propias frases. Por ejemplo: <em>I need to make time to practice English</em> o <em>I will do my best in the interview</em>. Si la frase conecta con tu vida, se queda.</p>
        """,
    },
    {
        "slug": "preposiciones-in-on-at",
        "category": "Preposiciones",
        "title": "In, on, at en inglés: usos y ejemplos para hispanohablantes",
        "seo_title": "In, on, at en inglés: cuándo usar cada preposición",
        "description": "Aprende cuándo usar in, on y at en inglés con lugares, fechas, horas, transporte y ejemplos pensados para hispanohablantes.",
        "lede": "In, on y at son difíciles porque las tres pueden traducirse como en. La salida es dejar de traducir y pensar en espacio, superficie o punto concreto.",
        "reading": "5 minutos",
        "toc": [
            ("in", "Cuándo usar in"),
            ("on", "Cuándo usar on"),
            ("at", "Cuándo usar at"),
            ("truco", "Truco mental"),
        ],
        "related": [
            "preposiciones-to-for-by-from-with",
            "actual-vs-actually",
            "make-vs-do",
        ],
        "body": """
                <p>Para un hispanohablante, <strong>in</strong>, <strong>on</strong> y <strong>at</strong> tienen una trampa: en muchos casos las tres se traducen como <em>en</em>. Si dependes de la traducción, cada frase parece una apuesta.</p>
                <p>La forma práctica de mejorar es asociar cada preposición con una imagen mental. <em>In</em> suele apuntar a estar dentro de algo o en un marco amplio. <em>On</em> suele apuntar a superficie, día o línea. <em>At</em> suele apuntar a un punto concreto.</p>

                <h2 id="in">Cuándo usar in</h2>
                <p>Usa <em>in</em> para espacios cerrados, lugares grandes y periodos de tiempo amplios.</p>
                <div class="example-grid">
                    <div class="mini-card"><strong>I'm in the kitchen</strong><span>Estoy en la cocina. Hay idea de interior.</span></div>
                    <div class="mini-card"><strong>She lives in Spain</strong><span>Países, ciudades y zonas grandes usan <em>in</em>.</span></div>
                    <div class="mini-card"><strong>In August</strong><span>Meses, años y estaciones: <em>in August</em>, <em>in 2025</em>, <em>in summer</em>.</span></div>
                    <div class="mini-card"><strong>In my car</strong><span>En transportes sin pasillo por el que caminar.</span></div>
                </div>

                <h2 id="on">Cuándo usar on</h2>
                <p>Usa <em>on</em> para superficies, días concretos, fechas, calles y transportes con pasillo.</p>
                <div class="example-grid">
                    <div class="mini-card"><strong>The book is on the table</strong><span>El libro está sobre la mesa.</span></div>
                    <div class="mini-card"><strong>On Monday</strong><span>Días y fechas específicas van con <em>on</em>.</span></div>
                    <div class="mini-card"><strong>On Main Street</strong><span>Calles y avenidas suelen usar <em>on</em>.</span></div>
                    <div class="mini-card"><strong>On the plane</strong><span>Avión, tren o autobús si puedes caminar dentro.</span></div>
                </div>

                <h2 id="at">Cuándo usar at</h2>
                <p>Usa <em>at</em> para puntos concretos: una hora, una localización específica o un evento.</p>
                <div class="example-grid">
                    <div class="mini-card"><strong>At 3 p.m.</strong><span>Las horas específicas van con <em>at</em>.</span></div>
                    <div class="mini-card"><strong>At home</strong><span>Casa como punto de referencia, aunque estés en el jardín.</span></div>
                    <div class="mini-card"><strong>At the bus stop</strong><span>Un punto concreto donde alguien espera.</span></div>
                    <div class="mini-card"><strong>At the concert</strong><span>Eventos y actividades organizadas.</span></div>
                </div>

                <h2 id="truco">Un truco mental que funciona</h2>
                <p>Si estás bloqueado, pregúntate qué imagen domina la frase: dentro de un espacio, sobre una superficie o en un punto. No resuelve todos los casos, pero te da una primera decisión mucho mejor que traducir <em>en</em>.</p>
                <div class="lesson-box">
                    <strong>Detalle útil:</strong> si dudas entre <em>in</em> y <em>on</em>, <em>in</em> es muy frecuente y a veces te salvará, pero no conviertas eso en una regla universal.
                </div>
        """,
    },
    {
        "slug": "preposiciones-to-for-by-from-with",
        "category": "Preposiciones",
        "title": "To, for, by, from y with: preposiciones inglesas sin traducir palabra por palabra",
        "seo_title": "To, for, by, from y with en inglés | De FAK a Fluent",
        "description": "Guía rápida de to, for, by, from y with en inglés: dirección, propósito, beneficiario, método, origen y compañía.",
        "lede": "Después de in, on y at, estas cinco preposiciones aparecen constantemente. Conviene aprenderlas por función, no por traducción aislada.",
        "reading": "5 minutos",
        "toc": [
            ("to", "To"),
            ("for", "For"),
            ("by", "By"),
            ("from-with", "From y with"),
        ],
        "related": [
            "preposiciones-in-on-at",
            "make-vs-do",
            "actual-vs-actually",
        ],
        "body": """
                <p>Las preposiciones son pequeñas, pero sostienen buena parte de la frase. El problema es que una misma preposición española puede convertirse en varias opciones inglesas según la función que cumpla.</p>
                <p>Por eso es mejor aprender <strong>to</strong>, <strong>for</strong>, <strong>by</strong>, <strong>from</strong> y <strong>with</strong> con situaciones típicas.</p>

                <h2 id="to">To: dirección, receptor y límite</h2>
                <p><em>To</em> suele apuntar hacia un destino, un receptor o el final de un rango.</p>
                <div class="example-grid">
                    <div class="mini-card"><strong>Go to the store</strong><span>Dirección o destino físico.</span></div>
                    <div class="mini-card"><strong>Give it to me</strong><span>El receptor de algo.</span></div>
                    <div class="mini-card"><strong>From Monday to Friday</strong><span>El final de un rango de tiempo.</span></div>
                </div>

                <h2 id="for">For: beneficiario, duración y propósito</h2>
                <p><em>For</em> aparece cuando algo es para alguien, durante un periodo o con un propósito.</p>
                <div class="example-grid">
                    <div class="mini-card"><strong>I bought this for my son</strong><span>Beneficiario.</span></div>
                    <div class="mini-card"><strong>For five years</strong><span>Duración en el tiempo.</span></div>
                    <div class="mini-card"><strong>For looking at the stars</strong><span>Propósito de un objeto o herramienta.</span></div>
                </div>

                <h2 id="by">By: método, autor, cercanía y fecha límite</h2>
                <p><em>By</em> tiene varios usos frecuentes. La clave es no reducirlo solo a <em>por</em>.</p>
                <ul>
                    <li><strong>By bus:</strong> método de transporte.</li>
                    <li><strong>Written by him:</strong> autor o sujeto en una pasiva.</li>
                    <li><strong>By the river:</strong> cerca o pegado a un lugar.</li>
                    <li><strong>By Monday:</strong> antes de que termine el lunes, no necesariamente antes del lunes.</li>
                </ul>

                <h2 id="from-with">From y with</h2>
                <p><em>From</em> marca origen, punto de partida o causa. <em>With</em> marca compañía, herramienta o modo.</p>
                <div class="lesson-box">
                    <p><strong>She is from Mexico.</strong> Origen.</p>
                    <p><strong>We will walk from the station to the hotel.</strong> Punto de partida y llegada.</p>
                    <p><strong>I attended the meeting with my manager.</strong> Compañía.</p>
                    <p><strong>I ate my salad with a fork.</strong> Herramienta.</p>
                </div>
        """,
    },
    {
        "slug": "actual-vs-actually",
        "category": "Falsos amigos",
        "title": "Actual vs actually: el falso amigo que cambia tus frases en inglés",
        "seo_title": "Actual vs actually: significado y ejemplos en inglés",
        "description": "Actual no significa actual y actually no significa actualmente. Aprende la diferencia con ejemplos claros para hispanohablantes.",
        "lede": "Actual y actually parecen transparentes desde español, pero esa confianza es justo el problema. Son dos palabras útiles si las separas de actualmente.",
        "reading": "4 minutos",
        "toc": [
            ("actual", "Actual"),
            ("actually", "Actually"),
            ("currently", "Currently"),
            ("practica", "Práctica"),
        ],
        "related": [
            "make-vs-do",
            "preposiciones-in-on-at",
            "how-are-you-respuestas-ingles",
        ],
        "body": """
                <p>Un falso amigo no es peligroso porque sea difícil, sino porque parece fácil. <strong>Actual</strong> y <strong>actually</strong> se parecen demasiado a <em>actual</em> y <em>actualmente</em>, pero no significan eso.</p>

                <h2 id="actual">Actual significa real</h2>
                <p><em>Actual</em> es un adjetivo. Significa real, verdadero o definitivo, especialmente cuando lo comparas con una estimación, expectativa o apariencia.</p>
                <div class="example-grid">
                    <div class="mini-card"><strong>The actual cost was higher</strong><span>El coste real fue más alto.</span></div>
                    <div class="mini-card"><strong>The actual problem is different</strong><span>El problema real es diferente.</span></div>
                </div>

                <h2 id="actually">Actually significa en realidad o de hecho</h2>
                <p><em>Actually</em> es un adverbio. Sirve para corregir, aclarar o introducir una idea que contrasta con lo que alguien esperaba.</p>
                <ul>
                    <li><strong>Corrección:</strong> He looks young, but he is actually in his sixties.</li>
                    <li><strong>Aclaración:</strong> I thought it would be expensive, but it is actually quite cheap.</li>
                    <li><strong>Sorpresa:</strong> Actually, I think I know the answer.</li>
                </ul>

                <h2 id="currently">Para actualmente, usa currently</h2>
                <p>Si quieres decir <em>actualmente</em>, la opción más directa es <strong>currently</strong>. Por ejemplo: <em>I currently live in Charlotte</em>.</p>
                <div class="lesson-box">
                    <strong>No traduzcas en automático:</strong> <em>actually</em> no significa <em>actualmente</em>. Casi siempre significa <em>en realidad</em> o <em>de hecho</em>.
                </div>

                <h2 id="practica">Cómo practicarlo</h2>
                <p>Hazte esta pregunta cada vez que quieras usar una de estas palabras: ¿estoy hablando de algo real frente a algo supuesto, o estoy corrigiendo una expectativa? Si hablas de lo real, usa <em>actual</em>. Si corriges o aclaras, usa <em>actually</em>. Si hablas del presente, usa <em>currently</em>.</p>
        """,
    },
    {
        "slug": "ligar-palabras-ingles",
        "category": "Pronunciación",
        "title": "Cómo ligar palabras en inglés: gonna, wanna, gotta, lemme y más",
        "seo_title": "Cómo ligar palabras en inglés | Gonna, wanna y gotta",
        "description": "Aprende cómo se ligan palabras en inglés hablado: going to, want to, have got to, let me, give me, could have y más.",
        "lede": "El inglés real no suena como palabras separadas en fila. Si no practicas las uniones, entenderás menos y sonarás más rígido.",
        "reading": "6 minutos",
        "toc": [
            ("por-que", "Por qué ligar"),
            ("formas", "Formas comunes"),
            ("escuchar", "Escuchar mejor"),
            ("practicar", "Práctica"),
        ],
        "related": [
            "pronunciacion-ingles-para-espanoles",
            "how-are-you-respuestas-ingles",
            "palabras-ough-pronunciacion-ingles",
        ],
        "body": """
                <p>Para sonar más natural en inglés no basta con pronunciar cada palabra correctamente. También hay que aprender cómo se unen cuando la gente habla rápido. En español hacemos lo mismo, pero cuando escuchamos inglés tendemos a esperar palabras separadas.</p>
                <p>Practicar estas uniones mejora dos cosas a la vez: te entienden mejor y tú entiendes mejor a los nativos.</p>

                <h2 id="por-que">Por qué ligar palabras cambia tanto</h2>
                <p>Cuando dices una frase palabra por palabra, puedes ser correcto y aun así sonar poco natural. En conversación, muchas combinaciones se reducen porque la boca busca el camino más eficiente.</p>
                <div class="lesson-box">
                    <strong>Importante:</strong> muchas formas reducidas son normales al hablar, pero no siempre conviene escribirlas. Puedes decir algo parecido a <em>wanna</em>, pero en un email formal escribe <em>want to</em>.
                </div>

                <h2 id="formas">Formas comunes que debes reconocer</h2>
                <div class="example-grid">
                    <div class="mini-card"><strong>going to → gonna</strong><span><a href="/audio/going-to.html">Escuchar going to</a></span></div>
                    <div class="mini-card"><strong>want to → wanna</strong><span><a href="/audio/i-want-to-go-to-london.html">Escuchar want to</a></span></div>
                    <div class="mini-card"><strong>have got to → gotta</strong><span><a href="/audio/i-gotta-go.html">Escuchar gotta</a></span></div>
                    <div class="mini-card"><strong>let me → lemme</strong><span><a href="/audio/let-me-see.html">Escuchar let me</a></span></div>
                    <div class="mini-card"><strong>give me → gimme</strong><span><a href="/audio/give-me-that.html">Escuchar give me</a></span></div>
                    <div class="mini-card"><strong>could have → could've</strong><span><a href="/audio/could-have-should-have-would-have.html">Escuchar could have</a></span></div>
                </div>

                <h2 id="escuchar">Esto también mejora tu listening</h2>
                <p>Si solo conoces la forma escrita, <em>I have got to go</em>, puede que no reconozcas <em>I gotta go</em>. No es que hablen mal: es que el inglés oral usa reducciones constantemente.</p>
                <p>Lo mismo ocurre con <em>out of</em>, <em>kind of</em> y <em>sort of</em>, que en conversación pueden sonar como <em>outta</em>, <em>kinda</em> y <em>sorta</em>.</p>

                <h2 id="practicar">Cómo practicarlo</h2>
                <ol>
                    <li>Escucha primero la versión lenta y después la versión conversacional.</li>
                    <li>Repite la frase completa, no solo la combinación aislada.</li>
                    <li>Grábate y comprueba si sigues separando demasiado las palabras.</li>
                    <li>Úsalo en frases que dirías de verdad: <em>I gotta go</em>, <em>lemme see</em>, <em>give me that</em>.</li>
                </ol>
                <p>Empieza por la colección de <a href="/audios.html#ligar-palabras">audios para ligar palabras</a>.</p>
        """,
    },
    {
        "slug": "sonido-th-ingles",
        "category": "Pronunciación",
        "title": "El sonido TH en inglés: cómo pronunciarlo sin convertirlo en D, T o Z",
        "seo_title": "Sonido TH en inglés para españoles | Pronunciación y ejemplos",
        "description": "Aprende cómo pronunciar el sonido TH en inglés con ejemplos como they, this, think y through. Guía para hispanohablantes con audios.",
        "lede": "El TH no es una D española, ni una T, ni una Z. La diferencia está en la posición de la lengua y en si el sonido vibra o no.",
        "reading": "5 minutos",
        "toc": [
            ("por-que", "Por qué importa"),
            ("dos-sonidos", "Dos TH"),
            ("errores", "Errores típicos"),
            ("practica", "Práctica"),
        ],
        "related": [
            "pronunciacion-ingles-para-espanoles",
            "palabras-ough-pronunciacion-ingles",
            "vocales-ingles-cortas-largas",
        ],
        "body": """
                <p>Para muchos hispanohablantes, <em>they</em>, <em>day</em>, <em>think</em> y <em>sink</em> acaban saliendo demasiado parecidas. El problema no suele ser el oído: es que intentamos producir el sonido con una posición de boca española.</p>
                <p>En inglés, el sonido <strong>TH</strong> se hace colocando la punta de la lengua entre los dientes o justo tocándolos. Esa pequeña diferencia física cambia por completo cómo te entiende un nativo.</p>

                <h2 id="por-que">Por qué importa tanto</h2>
                <p>El TH aparece en palabras muy frecuentes: <em>the</em>, <em>this</em>, <em>that</em>, <em>they</em>, <em>think</em>, <em>through</em>, <em>three</em>. Si lo conviertes siempre en D, T, S o Z, muchas frases siguen siendo comprensibles por contexto, pero tu pronunciación pierde claridad en justo las palabras que más repites.</p>
                <div class="lesson-box">
                    <strong>Idea clave:</strong> no intentes arreglar el TH pensando en letras. Arregla la posición de la lengua. Primero coloca la lengua; luego añade aire y voz.
                </div>

                <h2 id="dos-sonidos">Los dos sonidos TH</h2>
                <div class="example-grid">
                    <div class="mini-card"><strong>TH con voz</strong><span>Vibra la garganta. Aparece en <em>they</em>, <em>this</em>, <em>that</em>, <em>there</em>, <em>weather</em>.</span></div>
                    <div class="mini-card"><strong>TH sin voz</strong><span>No vibra la garganta. Aparece en <em>think</em>, <em>three</em>, <em>thanks</em>, <em>through</em>.</span></div>
                </div>
                <p>Una forma rápida de comprobarlo es tocarte la garganta. En <em>they</em> deberías notar vibración; en <em>think</em>, no.</p>

                <h2 id="errores">Errores típicos de los españoles</h2>
                <p>El primer error es hacer <em>they</em> como si fuera <em>day</em>. En <em>day</em>, la lengua está en el paladar; en <em>they</em>, la lengua va entre los dientes. El segundo error es sustituir <em>think</em> por un sonido parecido a nuestra Z o S. Puede funcionar a medias, pero no es el sonido inglés.</p>
                <p>No hace falta exagerarlo hasta escupir aire. Basta con que la lengua asome o toque los dientes y el aire salga de forma controlada.</p>

                <h2 id="practica">Práctica rápida</h2>
                <ol>
                    <li>Di <em>day</em> y <em>they</em> alternando, fijándote solo en dónde está la lengua.</li>
                    <li>Practica una serie con TH sonoro: <em>this, these, there, though, brother</em>.</li>
                    <li>Practica una serie con TH sordo: <em>think, three, thanks, through, teeth</em>.</li>
                    <li>Vuelve a una frase corta: <em>They think that this is good</em>.</li>
                </ol>
                <p>Empieza por los audios de <a href="/audio/sonido-th-entre-dientes.html">TH entre dientes</a>, <a href="/audio/sonido-th-paladar.html">TH frente a D</a> y <a href="/audio/though-through-tough-cough-enough-bough-thought-plough.html">palabras con TH y OUGH</a>.</p>
        """,
    },
    {
        "slug": "vocales-ingles-cortas-largas",
        "category": "Pronunciación",
        "title": "Vocales en inglés que confunden a los españoles: bit, book, love y moon",
        "seo_title": "Vocales en inglés para españoles | Bit, book, love y moon",
        "description": "Guía de vocales inglesas difíciles para hispanohablantes: I corta, doble O, love, book, moon y pares que cambian el significado.",
        "lede": "El inglés tiene cinco letras vocales, pero muchos más sonidos. Por eso leer con vocales españolas puede cambiar una palabra por otra.",
        "reading": "6 minutos",
        "toc": [
            ("problema", "El problema"),
            ("i-corta", "I corta"),
            ("doble-o", "Doble O"),
            ("practica", "Práctica"),
        ],
        "related": [
            "pronunciacion-ingles-para-espanoles",
            "sonido-th-ingles",
            "palabras-ough-pronunciacion-ingles",
        ],
        "body": """
                <p>En español, las vocales son bastante estables. La <em>a</em>, la <em>e</em>, la <em>i</em>, la <em>o</em> y la <em>u</em> casi siempre suenan como esperas. En inglés, la letra no manda tanto: manda la palabra.</p>
                <p>Ese es uno de los motivos por los que un español puede decir una palabra con seguridad y aun así provocar confusión. La vocal equivocada no es un detalle estético; puede cambiar el significado.</p>

                <h2 id="problema">El problema no es tu acento, es el contraste</h2>
                <p>Si pronuncias <em>bit</em> con una i española demasiado limpia, el oyente puede acercarlo a <em>beat</em>. Si pronuncias <em>book</em> como una u larga española, se aleja del sonido natural. Y si lees <em>love</em> como se escribe, no sonará como una palabra inglesa reconocible.</p>
                <div class="lesson-box">
                    <strong>Regla útil:</strong> no busques una vocal española perfecta para cada caso. Busca contrastes: <em>bit</em> no debe sonar como <em>beat</em>; <em>book</em> no debe sonar como <em>moon</em>.
                </div>

                <h2 id="i-corta">La I corta: bit, big, win, lip, clip</h2>
                <p>La <strong>I corta</strong> de palabras como <em>bit</em>, <em>sit</em>, <em>win</em> o <em>lip</em> es uno de los sonidos más rentables para un hispanohablante. Se parece más a una vocal relajada entre nuestra i y nuestra e que a una i española pura.</p>
                <p>La trampa es que una i demasiado española puede acercarte a otra palabra: <em>sit</em> puede sonar como <em>seat</em>, <em>fit</em> como <em>feet</em>, y <em>dip</em> como <em>deep</em>.</p>

                <h2 id="doble-o">La doble O: book no suena como moon</h2>
                <div class="example-grid">
                    <div class="mini-card"><strong>OO corta</strong><span><em>book, cook, look, foot, took</em>. Es rápida y no tan larga como nuestra u.</span></div>
                    <div class="mini-card"><strong>OO larga</strong><span><em>moon, food, room, school, cool</em>. Aquí sí aparece una u más larga y marcada.</span></div>
                    <div class="mini-card"><strong>O larga</strong><span><em>door, floor, score, shore</em>. No la mezcles con la doble O de <em>book</em>.</span></div>
                    <div class="mini-card"><strong>O inesperada</strong><span><em>love</em> no se pronuncia como una o española. Compárala con <em>move</em>.</span></div>
                </div>

                <h2 id="practica">Cómo practicar las vocales sin volverte loco</h2>
                <ol>
                    <li>Elige un contraste por sesión: <em>bit</em> frente a <em>beat</em>, o <em>book</em> frente a <em>moon</em>.</li>
                    <li>Escucha antes de leer para que la ortografía no te arrastre.</li>
                    <li>Repite en pares: corto, largo, corto, largo.</li>
                    <li>Termina con frases completas para que la vocal sobreviva al ritmo real.</li>
                </ol>
                <p>Practica con <a href="/audio/bit-big-win-lip-clip.html">bit, big, win, lip y clip</a>, <a href="/audio/book-cook-look-foot-hook-took-cookie-correcto.html">book, cook, look, foot, hook, took y cookie</a>, <a href="/audio/moon-food-room-school-tool-noodle-cool.html">moon, food, room, school, tool, noodle y cool</a>, y <a href="/audio/love-clove-move.html">love, clove y move</a>.</p>
        """,
    },
    {
        "slug": "letras-mudas-ingles",
        "category": "Pronunciación",
        "title": "Letras mudas en inglés: walk, talk, would, should, bomb y comb",
        "seo_title": "Letras mudas en inglés | Walk, talk, would, bomb y comb",
        "description": "Aprende letras mudas frecuentes en inglés para españoles: L muda en walk, talk, would y should, y B muda en bomb, tomb y comb.",
        "lede": "En inglés no todo lo que se escribe se pronuncia. Memorizar unas pocas familias evita muchos errores muy visibles.",
        "reading": "5 minutos",
        "toc": [
            ("por-que", "Por qué pasa"),
            ("l-muda", "L muda"),
            ("b-muda", "B muda"),
            ("practica", "Práctica"),
        ],
        "related": [
            "pronunciacion-ingles-para-espanoles",
            "vocales-ingles-cortas-largas",
            "palabras-ough-pronunciacion-ingles",
        ],
        "body": """
                <p>Uno de los golpes de realidad del inglés es descubrir que hay letras escritas solo por tradición. Las ves, tu cerebro español intenta pronunciarlas y, de repente, una palabra común suena mucho menos natural.</p>
                <p>No hace falta aprender una lista infinita de excepciones. Conviene empezar por grupos frecuentes que aparecen en conversaciones normales y en textos básicos.</p>

                <h2 id="por-que">Por qué hay letras mudas</h2>
                <p>La ortografía inglesa conserva capas antiguas de la lengua. Muchas palabras cambiaron su pronunciación, pero mantuvieron parte de su escritura. Para un estudiante, la consecuencia es sencilla: si lees letra por letra, te equivocas.</p>
                <div class="lesson-box">
                    <strong>Atajo práctico:</strong> aprende familias. Es más fácil recordar <em>walk, talk, half, calm</em> juntas que memorizar cada palabra como si no tuviera relación.
                </div>

                <h2 id="l-muda">La L muda: walk, talk, would, should</h2>
                <p>En palabras como <em>walk</em>, <em>talk</em>, <em>half</em>, <em>calm</em>, <em>salmon</em>, <em>would</em>, <em>should</em>, <em>yolk</em>, <em>palm</em> y <em>chalk</em>, la L no se pronuncia como esperaríamos desde el español.</p>
                <p>El error típico es intentar meter una L clara porque la vemos escrita. En <em>walk</em> y <em>talk</em>, esa L desaparece. En <em>would</em> y <em>should</em>, también.</p>

                <h2 id="b-muda">La B muda: bomb, tomb y comb</h2>
                <p>Otra familia útil es la de palabras terminadas en <strong>-mb</strong>. En <em>bomb</em>, <em>tomb</em> y <em>comb</em>, la B final no se pronuncia. Si la marcas demasiado, la palabra suena artificial y difícil de reconocer.</p>
                <div class="example-grid">
                    <div class="mini-card"><strong>Walk / talk</strong><span>No busques una L española. Concéntrate en la vocal y el cierre final.</span></div>
                    <div class="mini-card"><strong>Would / should</strong><span>La L escrita no te ayuda. Aprende el bloque completo de sonido.</span></div>
                    <div class="mini-card"><strong>Bomb / comb</strong><span>La B final está escrita, pero no sale por la boca.</span></div>
                    <div class="mini-card"><strong>Salmon / yolk</strong><span>Palabras muy comunes donde leer todas las letras te traiciona.</span></div>
                </div>

                <h2 id="practica">Práctica rápida</h2>
                <ol>
                    <li>Lee la palabra, pero tacha mentalmente la letra muda.</li>
                    <li>Escucha el audio sin mirar la pantalla.</li>
                    <li>Repite la serie completa varias veces, sin añadir la letra escrita.</li>
                    <li>Usa una frase corta: <em>I would walk there</em>, <em>talk to me</em>, <em>comb your hair</em>.</li>
                </ol>
                <p>Empieza con <a href="/audio/walk-talk-half-calm-salmon-would-should-yolk-palm-chalk-walkie-talkie.html">walk, talk, half, calm, salmon, would, should, yolk, palm y chalk</a> y <a href="/audio/bomb-tomb-comb.html">bomb, tomb y comb</a>.</p>
        """,
    },
    {
        "slug": "como-decir-de-nada-en-ingles",
        "category": "Conversación",
        "title": "Cómo decir de nada en inglés: you’re welcome, no problem, anytime y más",
        "seo_title": "Cómo decir de nada en inglés | You’re welcome, no problem y más",
        "description": "Formas naturales de decir de nada en inglés: you’re welcome, no problem, no worries, anytime, you got it, my pleasure y happy to help.",
        "lede": "You’re welcome es correcto, pero no es la única respuesta. En inglés real eliges según cercanía, contexto y nivel de formalidad.",
        "reading": "5 minutos",
        "toc": [
            ("basicas", "Formas básicas"),
            ("matices", "Matices"),
            ("formal", "Contextos formales"),
            ("practica", "Práctica"),
        ],
        "related": [
            "how-are-you-respuestas-ingles",
            "sure-en-ingles",
            "i-mean-en-ingles",
        ],
        "body": """
                <p>Cuando alguien dice <em>thank you</em>, muchos españoles contestan automáticamente <em>you’re welcome</em>. Es correcto, pero puede sonar demasiado de manual si lo usas para todo.</p>
                <p>En inglés hay varias respuestas naturales para decir <strong>de nada</strong>. La diferencia no está solo en la traducción, sino en la actitud que transmites.</p>

                <h2 id="basicas">Formas básicas para el día a día</h2>
                <div class="example-grid">
                    <div class="mini-card"><strong>You’re welcome</strong><span>Correcto y neutro. Útil cuando quieres sonar claro y educado.</span></div>
                    <div class="mini-card"><strong>No problem</strong><span>Muy común en situaciones cotidianas. Transmite que no ha supuesto molestia.</span></div>
                    <div class="mini-card"><strong>No worries</strong><span>Natural e informal. Equivale a “no te preocupes”.</span></div>
                    <div class="mini-card"><strong>Anytime</strong><span>Suena disponible: “cuando quieras”. Muy útil si ayudarías de nuevo.</span></div>
                </div>

                <h2 id="matices">Matices que cambian la impresión</h2>
                <p><em>No problem</em> y <em>no worries</em> minimizan el favor. Son buenas opciones cuando alguien te agradece algo pequeño: sujetar una puerta, enviar un enlace o responder una duda rápida.</p>
                <p><em>Anytime</em> va un paso más allá: no solo dices que no pasa nada, sino que estás dispuesto a repetirlo. Por eso funciona muy bien con amigos, compañeros de trabajo y situaciones amables.</p>

                <h2 id="formal">Cuando quieres sonar más formal o atento</h2>
                <p><em>My pleasure</em> significa algo parecido a “un placer”. Es más cálido y profesional, especialmente en atención al cliente. <em>You are very welcome</em> funciona cuando la otra persona te ha dado las gracias con mucha intensidad y quieres responder al mismo nivel.</p>
                <p><em>Happy to help</em> también es excelente en emails y trabajo: suena útil, amable y natural.</p>

                <h2 id="practica">Qué responder en cada situación</h2>
                <ol>
                    <li>Favor pequeño entre amigos: <em>No problem</em> o <em>No worries</em>.</li>
                    <li>Quieres mostrar disponibilidad: <em>Anytime</em>.</li>
                    <li>Cliente o situación profesional: <em>My pleasure</em> o <em>Happy to help</em>.</li>
                    <li>Agradecimiento muy sincero: <em>You’re very welcome</em>.</li>
                </ol>
                <div class="lesson-box">
                    <strong>Evita traducir literalmente:</strong> no necesitas buscar una versión exacta de “de nada”. Elige la respuesta que encaje con la relación y el tono.
                </div>
        """,
    },
    {
        "slug": "sure-en-ingles",
        "category": "Conversación",
        "title": "Sure en inglés: sí, claro, de nada o sarcasmo según el tono",
        "seo_title": "Sure en inglés | Significados, usos y ejemplos",
        "description": "Qué significa sure en inglés y cómo usarlo: certeza, sí informal, de nada, énfasis y sarcasmo. Ejemplos para hispanohablantes.",
        "lede": "Sure parece una palabra pequeña, pero cambia mucho según el contexto y la entonación. Ahí está la parte importante.",
        "reading": "4 minutos",
        "toc": [
            ("significados", "Significados"),
            ("tono", "El tono"),
            ("errores", "Errores"),
            ("ejemplos", "Ejemplos"),
        ],
        "related": [
            "como-decir-de-nada-en-ingles",
            "how-are-you-respuestas-ingles",
            "i-mean-en-ingles",
        ],
        "body": """
                <p><em>Sure</em> es una de esas palabras que escuchas constantemente en inglés hablado. El problema es que no tiene una única traducción estable. Puede significar “seguro”, “sí”, “claro”, “de nada” o incluso sonar sarcástico.</p>
                <p>La clave no es memorizar una lista de equivalencias, sino entender qué función cumple en cada frase.</p>

                <h2 id="significados">Los usos más comunes de sure</h2>
                <div class="example-grid">
                    <div class="mini-card"><strong>Certeza</strong><span><em>I’m sure it is</em>: estoy seguro de que sí.</span></div>
                    <div class="mini-card"><strong>Sí informal</strong><span><em>Do you want coffee? Sure</em>: sí, claro.</span></div>
                    <div class="mini-card"><strong>De nada</strong><span><em>Thanks! Sure, no problem</em>: de nada, no pasa nada.</span></div>
                    <div class="mini-card"><strong>Énfasis</strong><span><em>It sure is cold</em>: desde luego hace frío.</span></div>
                </div>

                <h2 id="tono">El tono decide mucho</h2>
                <p>Un <em>sure!</em> alegre puede sonar amistoso y dispuesto. Un <em>sure</em> plano, bajo o lento puede sonar como aceptación sin ganas. Y con el tono adecuado, también puede transmitir sarcasmo: <em>Sure, I’d love to work all weekend</em>.</p>
                <p>Por eso conviene escuchar la palabra dentro de frases reales. El significado literal te da una parte; la entonación te da la otra.</p>

                <h2 id="errores">Errores típicos</h2>
                <p>El primer error es traducir <em>sure</em> siempre como “seguro”. En muchas conversaciones solo equivale a un “sí” relajado. El segundo es usarlo en contextos demasiado formales donde quedaría mejor una respuesta completa, como <em>certainly</em> o <em>of course</em>.</p>
                <div class="lesson-box">
                    <strong>Regla práctica:</strong> si alguien te ofrece algo informalmente, <em>sure</em> puede servir. Si estás escribiendo un email formal, normalmente conviene una frase más explícita.
                </div>

                <h2 id="ejemplos">Ejemplos rápidos</h2>
                <ol>
                    <li><em>Are you sure?</em> → ¿Estás seguro?</li>
                    <li><em>Sure, no problem.</em> → Claro, sin problema / de nada.</li>
                    <li><em>It sure looks expensive.</em> → Desde luego parece caro.</li>
                    <li><em>Sure...</em> con tono seco → Sí, pero no muy convencido.</li>
                </ol>
        """,
    },
    {
        "slug": "i-mean-en-ingles",
        "category": "Conversación",
        "title": "I mean en inglés: cómo usar esta muletilla sin sonar raro",
        "seo_title": "I mean en inglés | Significado, usos y ejemplos",
        "description": "Qué significa I mean en inglés y cómo se usa para aclarar, enfatizar, ganar tiempo o suavizar una frase en conversación.",
        "lede": "I mean no siempre se traduce palabra por palabra. En conversación sirve para aclarar, enfatizar, ganar tiempo o suavizar lo que vas a decir.",
        "reading": "4 minutos",
        "toc": [
            ("significa", "Qué significa"),
            ("usos", "Usos"),
            ("cuidado", "Cuándo evitarlo"),
            ("practica", "Práctica"),
        ],
        "related": [
            "sure-en-ingles",
            "how-are-you-respuestas-ingles",
            "ligar-palabras-ingles",
        ],
        "body": """
                <p><em>I mean</em> aparece muchísimo en inglés hablado. La traducción más directa sería “quiero decir”, pero en la vida real funciona como una herramienta de conversación, no solo como una frase traducible.</p>
                <p>Los nativos la usan para corregirse, matizar, pensar en voz alta o preparar una frase delicada.</p>

                <h2 id="significa">Qué significa I mean</h2>
                <p>Literalmente, <em>I mean</em> significa “quiero decir”. Pero según el contexto puede equivaler a “o sea”, “es decir”, “a ver”, “la verdad es que” o incluso una pausa mientras piensas.</p>
                <div class="lesson-box">
                    <strong>Idea útil:</strong> no intentes poner <em>I mean</em> en cada frase. Úsalo cuando realmente estés aclarando, corrigiendo o suavizando algo.
                </div>

                <h2 id="usos">Usos comunes</h2>
                <div class="example-grid">
                    <div class="mini-card"><strong>Aclarar</strong><span><em>The movie was okay. I mean, it wasn’t great</em>.</span></div>
                    <div class="mini-card"><strong>Enfatizar</strong><span><em>I mean, it was really cold</em>.</span></div>
                    <div class="mini-card"><strong>Ganar tiempo</strong><span><em>I don’t know... I mean... it’s complicated</em>.</span></div>
                    <div class="mini-card"><strong>Suavizar</strong><span><em>I mean, maybe we could try another approach</em>.</span></div>
                </div>

                <h2 id="cuidado">Cuándo evitarlo</h2>
                <p><em>I mean</em> pertenece sobre todo al inglés hablado. En un email formal, un documento o una presentación escrita, normalmente puedes sustituirlo por frases más limpias: <em>in other words</em>, <em>to clarify</em> o directamente una explicación mejor construida.</p>
                <p>También existe <em>I mean it</em>, que significa “lo digo en serio”. No lo confundas con la muletilla conversacional.</p>

                <h2 id="practica">Práctica rápida</h2>
                <ol>
                    <li>Úsalo para corregirte: <em>I liked it. I mean, I liked the first half</em>.</li>
                    <li>Úsalo para suavizar: <em>I mean, we could wait until tomorrow</em>.</li>
                    <li>Evita repetirlo tres veces por frase. Una muletilla ayuda; abusar de ella distrae.</li>
                </ol>
        """,
    },
    {
        "slug": "fun-vs-funny",
        "category": "Vocabulario",
        "title": "Fun vs funny: la diferencia entre divertido, gracioso y raro",
        "seo_title": "Fun vs funny en inglés | Diferencia y ejemplos",
        "description": "Diferencia entre fun y funny en inglés: cuándo fun significa diversión o divertido, y cuándo funny significa gracioso o raro.",
        "lede": "Fun y funny no son intercambiables. Una fiesta puede ser fun; un chiste puede ser funny; una situación extraña también puede ser funny.",
        "reading": "4 minutos",
        "toc": [
            ("fun", "Fun"),
            ("funny", "Funny"),
            ("comparacion", "Comparación"),
            ("practica", "Práctica"),
        ],
        "related": [
            "actual-vs-actually",
            "sufijos-ish-wise",
            "how-are-you-respuestas-ingles",
        ],
        "body": """
                <p>En español usamos “divertido” para muchas cosas: una fiesta, una persona, un plan, un juego o una película. En inglés, esa comodidad nos puede llevar a mezclar <em>fun</em> y <em>funny</em>.</p>
                <p>La diferencia es sencilla si separas dos ideas: disfrute y risa.</p>

                <h2 id="fun">Fun: diversión o experiencia agradable</h2>
                <p><em>Fun</em> se usa cuando algo es entretenido, disfrutable o lo pasaste bien. No tiene por qué hacerte reír. Una excursión, una fiesta, una clase o un juego pueden ser <em>fun</em>.</p>
                <div class="example-grid">
                    <div class="mini-card"><strong>We had fun</strong><span>Nos lo pasamos bien.</span></div>
                    <div class="mini-card"><strong>That was a fun game</strong><span>Fue un juego divertido.</span></div>
                </div>

                <h2 id="funny">Funny: gracioso, o raro según contexto</h2>
                <p><em>Funny</em> suele significar gracioso: algo o alguien te hace reír. Un cómico puede ser <em>funny</em>, un vídeo puede ser <em>funny</em>, un comentario puede ser <em>funny</em>.</p>
                <p>Pero también puede significar raro, extraño o curioso. Si alguien dice <em>that smells funny</em>, probablemente no quiere decir que el olor cuente chistes.</p>

                <h2 id="comparacion">Comparación rápida</h2>
                <div class="lesson-box">
                    <strong>Atajo:</strong> si quieres decir que disfrutaste una experiencia, piensa en <em>fun</em>. Si quieres decir que algo te hizo reír, piensa en <em>funny</em>. Si algo te parece extraño, <em>funny</em> también puede servir.
                </div>
                <ol>
                    <li><em>The party was fun</em> → La fiesta fue divertida.</li>
                    <li><em>The comedian was funny</em> → El cómico era gracioso.</li>
                    <li><em>It’s funny that he didn’t call</em> → Es raro/curioso que no llamara.</li>
                    <li><em>She is fun</em> → Es divertida como persona, da gusto estar con ella.</li>
                    <li><em>She is funny</em> → Hace gracia, te hace reír.</li>
                </ol>

                <h2 id="practica">Práctica rápida</h2>
                <p>Antes de elegir, pregúntate: ¿hablo de pasarlo bien, de reírme o de algo extraño? Esa pregunta resuelve la mayoría de casos.</p>
        """,
    },
    {
        "slug": "some-vs-any",
        "category": "Gramática real",
        "title": "Some vs any: cuándo usar cada uno en preguntas, negaciones y afirmaciones",
        "seo_title": "Some vs any en inglés | Explicación con ejemplos",
        "description": "Aprende la diferencia entre some y any en inglés: preguntas, ofertas, negaciones, afirmaciones y el uso de any como cualquier.",
        "lede": "La regla del workbook ayuda, pero se queda corta. Some y any dependen de si esperas un sí, si niegas algo o si quieres decir cualquier.",
        "reading": "6 minutos",
        "toc": [
            ("regla", "La regla"),
            ("preguntas", "Preguntas"),
            ("negaciones", "Negaciones"),
            ("afirmaciones", "Afirmaciones"),
        ],
        "related": [
            "make-vs-do",
            "preposiciones-to-for-by-from-with",
            "sufijos-ish-wise",
        ],
        "body": """
                <p>La explicación típica dice: <em>some</em> en afirmaciones y <em>any</em> en preguntas y negaciones. No está mal como punto de partida, pero falla justo en frases muy comunes.</p>
                <p>La versión útil para hablar es esta: <strong>some</strong> suele aparecer cuando hay una cantidad indefinida pero esperada; <strong>any</strong> aparece cuando no sabes si existe, cuando niegas, o cuando quieres decir “cualquier”.</p>

                <h2 id="regla">La regla básica</h2>
                <div class="example-grid">
                    <div class="mini-card"><strong>Some</strong><span><em>There are some books on the floor</em>. Hay algunos libros en el suelo.</span></div>
                    <div class="mini-card"><strong>Any</strong><span><em>I don’t have any questions</em>. No tengo ninguna pregunta.</span></div>
                </div>
                <p>Hasta aquí, fácil. El problema llega con preguntas y afirmaciones donde la regla de instituto no explica el matiz.</p>

                <h2 id="preguntas">Preguntas: some si esperas que exista o que acepten</h2>
                <p>Usa <em>some</em> en preguntas cuando sabes que lo que pides existe o cuando estás ofreciendo algo que esperas que la otra persona acepte.</p>
                <ol>
                    <li><em>Can I have some water?</em> → Sabes que hay agua y estás pidiendo de forma educada.</li>
                    <li><em>Do you want some water?</em> → Tienes el agua a mano y esperas que pueda aceptar.</li>
                    <li><em>Do you have any questions?</em> → No sabes si hay preguntas; por eso encaja <em>any</em>.</li>
                </ol>

                <h2 id="negaciones">Negaciones: any es lo normal</h2>
                <p>En inglés no se usa la doble negación como en español. Decimos “no sé nada”, pero en inglés no digas <em>I don’t know nothing</em>. La forma natural es <em>I don’t know anything</em>.</p>
                <p>También verás <em>any</em> con palabras que ya tienen sentido negativo o limitante: <em>without any difficulty</em>, <em>barely any food</em>, <em>hardly any time</em>.</p>

                <h2 id="afirmaciones">Afirmaciones: some es alguno; any es cualquier</h2>
                <p>En afirmaciones, <em>some</em> suele significar “algún/algunos”: <em>There are some books</em>. En cambio, <em>any</em> puede significar “cualquier”: <em>Pick any card</em>, <em>Take any bus</em>, <em>Call me at any time</em>.</p>
                <div class="lesson-box">
                    <strong>Prueba mental:</strong> si en español puedes decir “cualquier”, probablemente necesitas <em>any</em>. Si quieres decir “algún” o “unos cuantos”, probablemente necesitas <em>some</em>.
                </div>
        """,
    },
    {
        "slug": "sufijos-ish-wise",
        "category": "Vocabulario",
        "title": "Sufijos -ish y -wise: cómo sonar más natural en inglés hablado",
        "seo_title": "Sufijos -ish y -wise en inglés | Significado y ejemplos",
        "description": "Aprende a usar los sufijos -ish y -wise en inglés: greenish, tallish, fourish, moneywise, clockwise y cuándo evitarlos.",
        "lede": "-ish y -wise condensan mucha información en pocas letras. Son útiles en conversación, pero conviene saber cuándo suenan informales.",
        "reading": "4 minutos",
        "toc": [
            ("ish", "-ish"),
            ("wise", "-wise"),
            ("formalidad", "Formalidad"),
            ("ejemplos", "Ejemplos"),
        ],
        "related": [
            "actual-vs-actually",
            "fun-vs-funny",
            "some-vs-any",
        ],
        "body": """
                <p>El inglés tiene una economía de lenguaje muy potente. A veces puedes añadir unas pocas letras a una palabra y crear un matiz que en español necesitaría una frase completa.</p>
                <p>Dos sufijos muy útiles para eso son <strong>-ish</strong> y <strong>-wise</strong>.</p>

                <h2 id="ish">-ish: aproximado, tirando a, más o menos</h2>
                <p><em>-ish</em> se añade a adjetivos, cualidades o cantidades para indicar aproximación. No dice “exactamente esto”, sino “algo parecido a esto”.</p>
                <div class="example-grid">
                    <div class="mini-card"><strong>greenish</strong><span>Verdoso, tirando a verde.</span></div>
                    <div class="mini-card"><strong>tallish</strong><span>Más bien alto, tirando a alto.</span></div>
                    <div class="mini-card"><strong>fourish</strong><span>Sobre las cuatro, más o menos a las cuatro.</span></div>
                    <div class="mini-card"><strong>Spanish-ish</strong><span>Algo parecido a español, pero no del todo.</span></div>
                </div>

                <h2 id="wise">-wise: en cuanto a, respecto a</h2>
                <p><em>-wise</em> se usa para hablar “en términos de” algo. Por ejemplo, <em>moneywise</em> significa “en cuanto al dinero”. También aparece en palabras de dirección como <em>clockwise</em> y <em>counterclockwise</em>.</p>
                <ol>
                    <li><em>Moneywise, this project is risky</em> → En cuanto al dinero, este proyecto es arriesgado.</li>
                    <li><em>Career-wise, it was a good move</em> → En términos profesionales, fue una buena decisión.</li>
                    <li><em>Turn it clockwise</em> → Gíralo en el sentido de las agujas del reloj.</li>
                </ol>

                <h2 id="formalidad">Ojo con la formalidad</h2>
                <p>Estos sufijos son muy prácticos y naturales en conversación, pero no siempre encajan en escritura formal. En un informe serio, quizá prefieras una frase completa: <em>from a financial perspective</em> en lugar de <em>moneywise</em>.</p>
                <div class="lesson-box">
                    <strong>Regla práctica:</strong> úsalos para sonar ágil en conversación. En documentos formales, comprueba si una alternativa más completa suena mejor.
                </div>

                <h2 id="ejemplos">Mini práctica</h2>
                <p>Prueba a crear tres frases propias: una con una hora aproximada usando <em>-ish</em>, otra con un color aproximado y otra con <em>-wise</em> para hablar de dinero, carrera o tiempo.</p>
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
    items = "\n".join(
        f'                        <li><a href="#{esc(anchor)}">{esc(label)}</a></li>'
        for anchor, label in article["toc"]
    )
    return f"""<div class="toc">
                    <p><strong>En esta guía</strong></p>
                    <ol>
{items}
                    </ol>
                </div>"""


def render_article(article: dict) -> str:
    slug = article["slug"]
    canonical = f"{BASE_URL}/articulos/{slug}.html"
    schema = {
        "@context": "https://schema.org",
        "@type": "Article",
        "headline": article["title"],
        "description": article["description"],
        "image": f"{BASE_URL}/images/book-cover-600.png",
        "author": {"@type": "Person", "name": AUTHOR},
        "publisher": {"@type": "Organization", "name": BOOK_TITLE},
        "datePublished": TODAY,
        "dateModified": TODAY,
        "mainEntityOfPage": canonical,
        "inLanguage": "es",
    }
    return f"""<!DOCTYPE html>
<html lang="es">
{page_head(title=article["seo_title"], description=article["description"], canonical=canonical, og_type="article", schema=schema)}
<body>
    {site_header("articulos")}

    <main>
        <section class="hero">
            <div class="hero-inner">
                <div>
                    <p class="eyebrow">{esc(article["category"])}</p>
                    <h1>{esc(article["title"])}</h1>
                    <p class="lede">{esc(article["lede"])}</p>
                </div>
                <img class="hero-cover" src="/images/book-cover-600.png" alt="Portada de {BOOK_TITLE}">
            </div>
        </section>

        <div class="page-shell article-layout">
            <article class="article-body">
                <p class="article-meta">Adaptado de ideas del libro <strong>{BOOK_TITLE}</strong>. Lectura: {esc(article["reading"])}.</p>
{article["body"].rstrip()}

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
                    <img src="/images/book-cover-300.png" alt="Portada de {BOOK_TITLE}">
                    <p>El libro desarrolla este tema con más ejemplos, audios y contexto para hispanohablantes.</p>
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
    schema = {
        "@context": "https://schema.org",
        "@type": "CollectionPage",
        "name": "Artículos para aprender inglés",
        "description": "Guías de inglés para hispanohablantes basadas en De FAK a Fluent.",
        "url": f"{BASE_URL}/articulos.html",
        "inLanguage": "es",
        "isPartOf": {"@type": "WebSite", "name": BOOK_TITLE, "url": f"{BASE_URL}/"},
    }
    return f"""<!DOCTYPE html>
<html lang="es">
{page_head(title="Artículos para aprender inglés | De FAK a Fluent", description="Guías de inglés para hispanohablantes basadas en De FAK a Fluent: pronunciación, conversación real, gramática y palabras difíciles.", canonical=f"{BASE_URL}/articulos.html", og_type="website", schema=schema)}
<body>
    {site_header("articulos")}

    <main>
        <section class="hero">
            <div class="hero-inner">
                <div>
                    <p class="eyebrow">Guías prácticas para hispanohablantes</p>
                    <h1>Inglés real explicado desde los errores que más cometemos en español.</h1>
                    <p class="lede">Estos artículos convierten ideas clave del libro en guías rápidas, enlazadas con audios y ejemplos para practicar pronunciación, conversación, gramática y vocabulario útil.</p>
                    <div class="button-row">
                        <a class="button primary" href="{AMAZON_URL}" target="_blank" rel="noopener noreferrer">Comprar el libro</a>
                        <a class="button secondary" href="/audios.html">Escuchar audios</a>
                    </div>
                </div>
                <img class="hero-cover" src="/images/book-cover-600.png" alt="Portada de {BOOK_TITLE}">
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


AUDIO_DISPLAY_OVERRIDES = {
    "doing.well.yourself.mp3": "Doing well, yourself?",
    "either.American_either.British.mp3": "Either: American vs. British",
    "hanging.mp3": "Hanging in there",
    "lack_lock_look_luke.mp3": "Lack, lock, look, Luke",
    "mountain_button_cotton_manhattan.mp3": "Mountain, button, cotton, Manhattan",
}


def audio_display_name(filename: str) -> str:
    if filename in AUDIO_DISPLAY_OVERRIDES:
        return AUDIO_DISPLAY_OVERRIDES[filename]
    stem = Path(filename).stem
    text = stem.replace("_", ", ").replace(".", " ")
    text = text.replace("(correcto)", "(correcto)").replace("(LOL)", "(LOL)")
    text = re.sub(r"\s+", " ", text).strip()
    return text[:1].upper() + text[1:]


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
    name = audio_display_name(filename)
    category = audio_category(filename)
    if category == "Ligar palabras":
        return f"Escucha y practica cómo se liga en inglés hablado: {name}. Audio del libro De FAK a Fluent."
    if category == "Conversación":
        return f"Escucha la pronunciación natural de {name}, una expresión frecuente en conversaciones reales en inglés."
    if category == "Palabras difíciles":
        return f"Compara la pronunciación de {name} y entrena el oído para palabras inglesas que se escriben de forma engañosa."
    return f"Escucha el audio de pronunciación de {name}, creado para hispanohablantes que quieren sonar más claros en inglés."


def audio_mini_transcript(filename: str) -> str:
    text = audio_display_name(filename)
    text = re.sub(r"\s+\((correcto|LOL)\)$", "", text)
    return text


def audio_focus_note(filename: str) -> str:
    low = filename.lower()
    category = audio_category(filename)
    if "sonido.'th'.entre" in low or "sonido.'th'.paladar" in low:
        return "Trabaja la posición de la lengua para que el TH no se convierta en una D, T, S o Z española."
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
    low = filename.lower()
    category = audio_category(filename)
    if "sonido.'th'" in low:
        return "El error más común es esconder la lengua y decir una D o T española. Si la lengua no participa, el sonido no sale."
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
    if "sonido.'th'" in low:
        return [
            "Coloca la lengua entre los dientes antes de reproducir el audio.",
            "Escucha una vez sin repetir y nota si hay vibración de garganta.",
            "Repite despacio exagerando la lengua, luego reduce la exageración.",
            "Termina con una frase corta usando el mismo sonido.",
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


def related_articles_for_audio(filename: str) -> list[str]:
    category = audio_category(filename)
    low = filename.lower()
    if "sonido.'th'" in low:
        return ["sonido-th-ingles", "pronunciacion-ingles-para-espanoles", "palabras-ough-pronunciacion-ingles"]
    if any(key in low for key in ["bit_big", "hit", "book_cook", "moon_food", "door_floor", "lack_lock", "love_clove", "live_leave"]):
        return ["vocales-ingles-cortas-largas", "pronunciacion-ingles-para-espanoles", "palabras-ough-pronunciacion-ingles"]
    if any(key in low for key in ["walk_talk", "bomb_tomb"]):
        return ["letras-mudas-ingles", "pronunciacion-ingles-para-espanoles", "palabras-ough-pronunciacion-ingles"]
    if category == "Ligar palabras":
        return ["ligar-palabras-ingles", "i-mean-en-ingles", "pronunciacion-ingles-para-espanoles"]
    if category == "Conversación":
        return ["how-are-you-respuestas-ingles", "como-decir-de-nada-en-ingles", "sure-en-ingles"]
    if "ough" in low:
        return ["palabras-ough-pronunciacion-ingles", "sonido-th-ingles", "pronunciacion-ingles-para-espanoles"]
    if category == "Palabras difíciles":
        return ["pronunciacion-ingles-para-espanoles", "vocales-ingles-cortas-largas", "palabras-ough-pronunciacion-ingles"]
    return ["pronunciacion-ingles-para-espanoles", "vocales-ingles-cortas-largas", "ligar-palabras-ingles"]


def render_audio_page(filename: str) -> str:
    slug = audio_slug(filename)
    name = audio_display_name(filename)
    canonical = f"{BASE_URL}/audio/{slug}.html"
    src = f"/audios/{quote(filename)}"
    description = audio_description(filename)
    category = audio_category(filename)
    dynamic_stem = quote(Path(filename).stem)
    related = "\n".join(
        f'                        <li><a href="/articulos/{slug}.html">{esc(ARTICLE_BY_SLUG[slug]["title"])}</a></li>'
        for slug in related_articles_for_audio(filename)
    )
    schema = {
        "@context": "https://schema.org",
        "@type": "WebPage",
        "name": f"{name} | Audio de inglés",
        "description": description,
        "url": canonical,
        "inLanguage": "es",
        "mainEntity": {
            "@type": "AudioObject",
            "name": name,
            "description": description,
            "contentUrl": f"{BASE_URL}/audios/{quote(filename)}",
            "encodingFormat": "audio/mpeg",
            "inLanguage": "en",
        },
    }
    return f"""<!DOCTYPE html>
<html lang="es">
{page_head(title=f"{name} | Audio de pronunciación en inglés", description=description, canonical=canonical, og_type="website", schema=schema)}
<body>
    {site_header("audios")}

    <main>
        <section class="hero compact-hero">
            <div class="hero-inner">
                <div>
                    <p class="eyebrow">{esc(category)}</p>
                    <h1>{esc(name)}</h1>
                    <p class="lede">{esc(description)}</p>
                    <div class="button-row">
                        <a class="button secondary" href="/audios.html">Ver todos los audios</a>
                        <a class="button primary" href="{AMAZON_URL}" target="_blank" rel="noopener noreferrer">Comprar el libro</a>
                    </div>
                </div>
                <img class="hero-cover" src="/images/book-cover-600.png" alt="Portada de {BOOK_TITLE}">
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
                <div class="lesson-box">
                    <strong>Consejo de práctica:</strong> reproduce el audio, pausa, repite la frase completa y vuelve a escuchar. Si una palabra se te resiste, no la practiques sola durante demasiado tiempo: vuelve pronto a la frase completa.
                </div>
{render_audio_notes(filename)}
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
                    <img src="/images/book-cover-300.png" alt="Portada de {BOOK_TITLE}">
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
            cards.append(
                f"""                    <a class="audio-card" href="/audio/{slug}.html">
                        <span>{esc(category)}</span>
                        <strong>{esc(name)}</strong>
                        <small>Escuchar audio</small>
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
    schema = {
        "@context": "https://schema.org",
        "@type": "CollectionPage",
        "name": "Audios de inglés de De FAK a Fluent",
        "description": "Biblioteca de audios de pronunciación y conversación para hispanohablantes.",
        "url": f"{BASE_URL}/audios.html",
        "inLanguage": "es",
        "mainEntity": {"@type": "ItemList", "itemListElement": item_list},
    }
    return f"""<!DOCTYPE html>
<html lang="es">
{page_head(title="Audios de inglés | De FAK a Fluent", description="Escucha audios de pronunciación, conversación y palabras difíciles del libro De FAK a Fluent.", canonical=f"{BASE_URL}/audios.html", og_type="website", schema=schema)}
<body>
    {site_header("audios")}

    <main>
        <section class="hero">
            <div class="hero-inner">
                <div>
                    <p class="eyebrow">Biblioteca de audios</p>
                    <h1>Audios de pronunciación y conversación en inglés.</h1>
                    <p class="lede">Cada audio tiene su propia página para que puedas practicar, compartirlo y volver a él fácilmente desde el móvil.</p>
                    <div class="button-row">
                        <a class="button primary" href="{AMAZON_URL}" target="_blank" rel="noopener noreferrer">Comprar el libro</a>
                        <a class="button secondary" href="/articulos.html">Leer artículos</a>
                    </div>
                </div>
                <img class="hero-cover" src="/images/book-cover-600.png" alt="Portada de {BOOK_TITLE}">
            </div>
        </section>

        <div class="page-shell audio-list-page">
{chr(10).join(sections)}
        </div>
    </main>

    {site_footer()}
</body>
</html>"""


def render_sitemap(files: list[str]) -> str:
    urls: list[tuple[str, str, str]] = [
        ("/", "1.00", "daily"),
        ("/audios.html", "0.90", "weekly"),
        ("/articulos.html", "0.90", "weekly"),
        ("/contacto.html", "0.50", "yearly"),
        ("/prompt.html", "0.55", "yearly"),
    ]
    urls.extend((f"/articulos/{article['slug']}.html", "0.85", "monthly") for article in ARTICLES)
    urls.extend((f"/audio/{audio_slug(filename)}.html", "0.65", "monthly") for filename in files)
    entries = []
    for path, priority, changefreq in urls:
        loc = f"{BASE_URL}{path}"
        entries.append(
            f"""<url>
  <loc>{xml_escape(loc)}</loc>
  <lastmod>{TODAY}T00:00:00+00:00</lastmod>
  <changefreq>{changefreq}</changefreq>
  <priority>{priority}</priority>
</url>"""
        )
    return f"""<?xml version="1.0" encoding="UTF-8"?>
<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">
{chr(10).join(entries)}
</urlset>"""


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


if __name__ == "__main__":
    main()
