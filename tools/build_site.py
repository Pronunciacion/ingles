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
                    <li><strong>How is it going?</strong> Informal, común con gente conocida.</li>
                    <li><strong>How have you been?</strong> Para alguien a quien no ves desde hace tiempo.</li>
                    <li><strong>What is up?</strong> Muy informal. Mejor con amigos o gente joven.</li>
                    <li><strong>How is your day going?</strong> Buena opción a mitad del día.</li>
                    <li><strong>How is everything?</strong> Invita a una respuesta un poco más amplia.</li>
                </ul>

                <h2 id="plantillas">Plantillas seguras</h2>
                <p>Si no sabes qué decir, usa respuestas cortas con una repregunta. Son naturales y no te obligan a improvisar demasiado.</p>
                <div class="lesson-box">
                    <p><strong>Contexto formal:</strong> I am doing well, thank you. And yourself?</p>
                    <p><strong>Contexto informal:</strong> Pretty good. How about you?</p>
                    <p><strong>Hace tiempo que no os veis:</strong> It has been good, thanks. What about you?</p>
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

                <h2 id="to">To: dirección, receptor e intención</h2>
                <p><em>To</em> suele apuntar hacia un destino: físico, personal o mental.</p>
                <div class="example-grid">
                    <div class="mini-card"><strong>Go to the store</strong><span>Dirección o destino físico.</span></div>
                    <div class="mini-card"><strong>Give it to me</strong><span>El receptor de algo.</span></div>
                    <div class="mini-card"><strong>To become a doctor</strong><span>Intención u objetivo.</span></div>
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
]


ARTICLE_BY_SLUG = {article["slug"]: article for article in ARTICLES}


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
    cards = []
    for article in ARTICLES:
        cards.append(
            f"""                <a class="article-card" href="/articulos/{article["slug"]}.html">
                    <span>{esc(article["category"])}</span>
                    <h2>{esc(article["title"])}</h2>
                    <p>{esc(article["lede"])}</p>
                </a>"""
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
            <div class="hub-grid">
{chr(10).join(cards)}
            </div>
        </section>
    </main>

    {site_footer()}
</body>
</html>"""


def audio_files() -> list[str]:
    return sorted(path.name for path in (ROOT / "audios").glob("*.mp3"))


def audio_display_name(filename: str) -> str:
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


def related_articles_for_audio(filename: str) -> list[str]:
    category = audio_category(filename)
    low = filename.lower()
    if category == "Ligar palabras":
        return ["ligar-palabras-ingles", "pronunciacion-ingles-para-espanoles"]
    if category == "Conversación":
        return ["how-are-you-respuestas-ingles", "ligar-palabras-ingles"]
    if "ough" in low:
        return ["palabras-ough-pronunciacion-ingles", "pronunciacion-ingles-para-espanoles"]
    if category == "Palabras difíciles":
        return ["pronunciacion-ingles-para-espanoles", "palabras-ough-pronunciacion-ingles"]
    return ["pronunciacion-ingles-para-espanoles", "ligar-palabras-ingles"]


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
