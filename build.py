#!/usr/bin/env python3
"""
Генератор маркетингового сайта Medistory.

Три языка, две страницы на каждый: посадочная и поддержка (её адрес
обязателен для App Store Connect). Тексты лежат здесь же, в CONTENT, —
править их можно, не заглядывая в разметку.

    python3 build.py          # собрать в docs/
    python3 -m http.server -d docs 8000    # посмотреть локально

Публикация: docs/ раздаётся GitHub Pages из отдельного
репозитория (как medistory-legal) или в любой статический хостинг.
"""

import html
import shutil
import sys
from pathlib import Path

ROOT = Path(__file__).parent
DIST = ROOT / "docs"   # Pages раздаёт из корня или из docs/, другую папку не умеет

# Цвета и типографика повторяют приложение и страницу политики:
# человек, пришедший из App Store, должен узнать то же самое место.
CSS = """
:root {
  --bg:#F7F5F1; --card:#FFFFFF; --deep:#0F3D3E; --active:#287D77;
  --lavender:#8F82D8; --text:#1B2B2A; --muted:#6B7A78; --line:#E8E5E1;
  --mint:#E8F3F1;
}
@media (prefers-color-scheme: dark) {
  :root { --bg:#0A0F10; --card:#141C1C; --deep:#E6ECE8; --active:#53ABA2;
          --lavender:#A89CE6; --text:#F2F4F2; --muted:#B9C1BE; --line:#232A28;
          --mint:#143734; }
}
* { box-sizing:border-box; }
body { margin:0; padding:0; background:var(--bg); color:var(--text);
  font:17px/1.6 -apple-system,BlinkMacSystemFont,"Segoe UI",Roboto,sans-serif;
  -webkit-font-smoothing:antialiased; }
main { max-width:760px; margin:0 auto; padding:0 20px 80px; }
h1 { font-family:ui-serif,Georgia,serif; font-weight:600; font-size:clamp(34px,7vw,52px);
  line-height:1.1; margin:0 0 12px; color:var(--deep); }
h2 { font-family:ui-serif,Georgia,serif; font-weight:600; font-size:clamp(24px,4vw,32px);
  margin:56px 0 6px; color:var(--deep); }
h3 { font-size:18px; margin:0 0 4px; }
p { margin:0 0 14px; }
.lede { font-size:clamp(18px,2.4vw,21px); color:var(--muted); margin-bottom:28px; }
.hero { text-align:center; padding:56px 0 8px; position:relative; }
.hero img.icon { width:104px; height:104px; border-radius:24px; box-shadow:0 8px 30px rgba(0,0,0,.10); }
.branch { position:absolute; width:190px; opacity:.5; pointer-events:none;
  top:-10px; right:-40px; transform:rotate(-42deg); }
@media (max-width:700px) { .branch { width:130px; right:-30px; } }
.cards { display:grid; gap:14px; grid-template-columns:repeat(auto-fit,minmax(230px,1fr)); }
.card { background:var(--card); border:1px solid var(--line); border-radius:18px; padding:20px 22px; }
.card p { color:var(--muted); margin:0; font-size:16px; }
.steps { counter-reset:s; padding:0; margin:18px 0 0; list-style:none; }
.steps li { counter-increment:s; position:relative; padding:0 0 0 46px; margin:0 0 18px; }
.steps li::before { content:counter(s); position:absolute; left:0; top:-2px;
  width:30px; height:30px; border-radius:50%; background:var(--mint); color:var(--active);
  display:grid; place-items:center; font-weight:600; font-size:15px; }
.note { background:var(--mint); border-radius:18px; padding:22px 24px; margin-top:18px; }
.note p:last-child { margin-bottom:0; }
.faq { margin-top:18px; }
.faq details { border-bottom:1px solid var(--line); padding:14px 0; }
.faq summary { cursor:pointer; font-weight:500; list-style:none; }
.faq summary::-webkit-details-marker { display:none; }
.faq summary::after { content:"+"; float:right; color:var(--muted); }
.faq details[open] summary::after { content:"–"; }
.faq p { margin:10px 0 0; color:var(--muted); }
nav.langs { display:flex; gap:8px; justify-content:center; padding:22px 0 0; flex-wrap:wrap; }
nav.langs a { text-decoration:none; color:var(--active); border:1px solid var(--line);
  border-radius:999px; padding:6px 14px; font-size:14px; background:var(--card); }
nav.langs a[aria-current] { background:var(--mint); border-color:transparent; }
.cta { display:inline-block; margin-top:8px; background:var(--deep); color:#fff;
  text-decoration:none; border-radius:16px; padding:15px 30px; font-weight:600; font-size:17px; }
@media (prefers-color-scheme: dark) { .cta { color:#0A0F10; } }
.cta.secondary { background:transparent; color:var(--active); border:1px solid var(--line); }
footer { margin-top:64px; padding-top:24px; border-top:1px solid var(--line);
  color:var(--muted); font-size:14px; }
footer a { color:var(--active); }
"""

EMAIL = "krispo.dev@gmail.com"
PRIVACY_URL = "https://krispo95.github.io/medistory-legal/"
APPSTORE_URL = ("https://apps.apple.com/app/apple-store/id6797866671"
                "?pt=129030541&ct=site_hero&mt=8")  # без страны: Apple сам выберет витрину

CONTENT = {
    "ru": {
        "lang": "ru",
        "label": "Русский",
        "title": "Medistory — помогаем ничего не забыть рассказать врачу",
        "meta": "Приложение для подготовки к приёму: собирает вашу медицинскую историю "
                "и превращает её в одностраничное резюме для врача. Всё хранится на телефоне.",
        "tagline": "Ваша история здоровья",
        "lede": "На приёме десять минут, а рассказать нужно многое. Medistory задаёт короткие "
                "вопросы заранее и собирает одностраничное резюме, которое можно показать "
                "врачу с телефона или распечатать.",
        "cta": "Загрузить в App Store",
        "cta_note": "iPhone. Данные остаются на телефоне",
        "what_title": "Что делает",
        "what": [
            ("Помнит за вас", "Диагнозы, лекарства, аллергии, операции и семейная история — "
                              "один раз заполнили, дальше только дополняете."),
            ("Спрашивает по делу", "Перед приёмом — короткие вопросы именно о вашей жалобе: "
                                   "когда началось, что усиливает, что уже принимали."),
            ("Говорит на языке врача", "Резюме на русском, испанском или английском. "
                                       "Диагнозы и лекарства подставляются официальными названиями."),
        ],
        "how_title": "Как это работает",
        "how": [
            ("Заполняете профиль", "Восемь коротких блоков, около трёх минут. Любой можно пропустить. "
                                   "Вес, рост и лекарства подставятся из приложения «Здоровье»."),
            ("Говорите, к какому врачу идёте", "И описываете, что беспокоит, — своими словами."),
            ("Отвечаете на вопросы", "Обычно их пять–десять, все с готовыми вариантами. "
                                     "«Не знаю» — нормальный ответ на любой."),
            ("Показываете резюме", "Одна страница: жалоба, хронология, важное для этого приёма "
                                   "и краткий анамнез. PDF, текст или экран телефона."),
        ],
        "privacy_title": "Данные остаются у вас",
        "privacy": [
            "Медицинская история хранится только на вашем телефоне. Ни аккаунтов, ни серверов: "
            "мы физически не можем её прочитать, восстановить или кому-то передать.",
            "Уточняющие вопросы подбирает модель Apple, встроенная в iOS, а свободный текст "
            "переводится тоже на устройстве. Ваши слова не уходят в интернет.",
        ],
        "privacy_link": "Читать политику конфиденциальности целиком",
        "sources_title": "Откуда названия",
        "sources": "Диагнозы — из МКБ-11 ВОЗ (30 тысяч кодов с официальными переводами на три языка) "
                   "и МКБ-10. Лекарства — из классификации ATC ВОЗ. Поэтому «щитовидка» находится "
                   "как «Гипотиреоз», а испанский врач видит «Hipotiroidismo» — это один и тот же код.",
        "faq_title": "Вопросы",
        "faq": [
            ("Это ставит диагноз?", "Нет. Приложение не диагностирует, не оценивает срочность и не "
                                    "советует лечение. Оно помогает вам структурировать то, что вы "
                                    "хотите рассказать врачу, и не заменяет медицинскую помощь."),
            ("Нужен интернет?", "Нет. Справочники лежат внутри приложения, вопросы и перевод "
                                "работают на самом телефоне."),
            ("Что бесплатно?", "Всё, кроме перевода резюме на другой язык: профиль, интервью, "
                               "резюме и PDF на вашем языке — без оплаты."),
            ("Что с данными, если удалить приложение?", "Они удалятся вместе с ним — копии у нас нет. "
                                                       "Перед этим можно сохранить резервный файл и перенести историю на другой телефон."),
            ("Работает без Apple Health?", "Да. Health только избавляет от ручного ввода веса, роста "
                                           "и лекарств, и подключать его необязательно."),
        ],
        "footer_privacy": "Политика конфиденциальности",
        "footer_support": "Поддержка",
        "support_title": "Поддержка",
        "support_lede": "Напишите — отвечаем обычно в течение пары дней.",
        "support_blocks": [
            ("Как связаться", f"Почта: <a href=\"mailto:{EMAIL}\">{EMAIL}</a>. "
                              "Опишите, что произошло и на каком экране, — этого хватит, "
                              "чтобы разобраться. Скриншот приложите, если он есть."),
            ("Данные не подтянулись из Здоровья",
             "Лекарства Apple отдаёт по одному: в системном окне нужно отметить конкретные "
             "препараты. Открыть его заново можно в «Настройки → Apple Здоровье». "
             "Чтение списка лекарств работает начиная с iOS 26."),
            ("Пропали записи",
             "История хранится только на телефоне, поэтому восстановить её у нас нельзя. "
             "Если вы делали резервную копию, откройте «Настройки → Восстановить из копии»."),
            ("Перенести историю на новый телефон",
             "На старом: «Настройки → Сохранить копию». На новом: «Восстановить из копии»."),
        ],
        "back": "На главную",
    },
    "en": {
        "lang": "en",
        "label": "English",
        "title": "Medistory — never forget what you meant to tell the doctor",
        "meta": "An app that collects your medical history and turns it into a one-page "
                "summary for your doctor. Everything stays on your phone.",
        "tagline": "Your health story",
        "lede": "An appointment lasts ten minutes, and there is a lot to say. Medistory asks "
                "short questions beforehand and builds a one-page summary you can show on "
                "your phone or print.",
        "cta": "Download on the App Store",
        "cta_note": "iPhone. Your data stays on the phone",
        "what_title": "What it does",
        "what": [
            ("Remembers for you", "Conditions, medications, allergies, surgeries and family history — "
                                  "fill it in once, then just keep it up to date."),
            ("Asks what matters", "Before the visit: short questions about your actual complaint — "
                                  "when it started, what makes it worse, what you already took."),
            ("Speaks the doctor's language", "A summary in English, Spanish or Russian, with official "
                                             "names for diagnoses and medications."),
        ],
        "how_title": "How it works",
        "how": [
            ("Fill in your profile", "Eight short blocks, about three minutes; any of them can be "
                                     "skipped. Weight, height and medications can come from Apple Health."),
            ("Say which doctor you're seeing", "And describe what's bothering you, in your own words."),
            ("Answer a few questions", "Usually five to ten, all with ready-made options. "
                                       "\"I don't know\" is a valid answer to any of them."),
            ("Show the summary", "One page: the complaint, its history, what matters for this visit "
                                 "and a short medical background. PDF, text, or straight off the screen."),
        ],
        "privacy_title": "Your data stays with you",
        "privacy": [
            "Your medical history is stored only on your phone. No accounts, no servers: we "
            "physically cannot read it, restore it or hand it to anyone.",
            "Follow-up questions come from Apple's model built into iOS, and free text is translated "
            "on the device too. Your words never go online.",
        ],
        "privacy_link": "Read the full privacy policy",
        "sources_title": "Where the names come from",
        "sources": "Diagnoses come from WHO ICD-11 (30,000 codes with official translations into three "
                   "languages) and ICD-10. Medications come from the WHO ATC classification. That's why "
                   "\"thyroid\" finds \"Hypothyroidism\", and a Spanish doctor sees \"Hipotiroidismo\" — "
                   "the very same code.",
        "faq_title": "Questions",
        "faq": [
            ("Does it diagnose?", "No. The app does not diagnose, does not triage and does not advise "
                                  "treatment. It helps you structure what you want to tell a doctor and "
                                  "does not replace medical care."),
            ("Do I need an internet connection?", "No. The catalogues ship inside the app; questions and "
                                                  "translation run on the phone itself."),
            ("What's free?", "Everything except translating the summary into another language: the profile, "
                             "the interview, the summary and the PDF in your own language cost nothing."),
            ("What happens to my data if I delete the app?", "It goes with it — we hold no copy. Before that "
                                                             "you can save a backup file and move your history to another phone."),
            ("Does it work without Apple Health?", "Yes. Health only saves you typing in weight, height and "
                                                   "medications; connecting it is optional."),
        ],
        "footer_privacy": "Privacy Policy",
        "footer_support": "Support",
        "support_title": "Support",
        "support_lede": "Drop us a line — we usually reply within a couple of days.",
        "support_blocks": [
            ("How to reach us", f"Email: <a href=\"mailto:{EMAIL}\">{EMAIL}</a>. Tell us what happened "
                                "and on which screen — that's usually enough. Attach a screenshot if you have one."),
            ("Health data didn't come through",
             "Apple shares medications one by one: you have to tick the specific ones in the system sheet. "
             "You can open it again in Settings → Apple Health. Reading the medications list works from iOS 26 onwards."),
            ("My records disappeared",
             "The history lives only on your phone, so we cannot restore it. If you made a backup, "
             "open Settings → Restore from backup."),
            ("Moving to a new phone",
             "On the old one: Settings → Save a backup. On the new one: Restore from backup."),
        ],
        "back": "Back to the main page",
    },
    "es": {
        "lang": "es",
        "label": "Español",
        "title": "Medistory — no olvide nada de lo que quiere contarle al médico",
        "meta": "Una app que reúne su historial médico y lo convierte en un resumen de una "
                "página para el médico. Todo se queda en su teléfono.",
        "tagline": "Su historia de salud",
        "lede": "La consulta dura diez minutos y hay mucho que contar. Medistory hace preguntas "
                "breves antes y prepara un resumen de una página que puede enseñar desde el "
                "móvil o imprimir.",
        "cta": "Descárgalo en el App Store",
        "cta_note": "iPhone. Sus datos no salen del teléfono",
        "what_title": "Qué hace",
        "what": [
            ("Recuerda por usted", "Enfermedades, medicación, alergias, cirugías y antecedentes "
                                   "familiares: se rellena una vez y luego solo se completa."),
            ("Pregunta lo que importa", "Antes de la consulta: preguntas breves sobre su molestia — "
                                        "cuándo empezó, qué la empeora, qué ha tomado ya."),
            ("Habla el idioma del médico", "Un resumen en español, inglés o ruso, con los nombres "
                                           "oficiales de diagnósticos y medicamentos."),
        ],
        "how_title": "Cómo funciona",
        "how": [
            ("Rellena su perfil", "Ocho bloques cortos, unos tres minutos; cualquiera se puede omitir. "
                                  "El peso, la estatura y los medicamentos pueden venir de Salud."),
            ("Dice a qué médico va", "Y describe qué le preocupa, con sus propias palabras."),
            ("Responde unas preguntas", "Suelen ser entre cinco y diez, todas con opciones preparadas. "
                                        "«No lo sé» es una respuesta válida en cualquiera."),
            ("Enseña el resumen", "Una página: el motivo, su cronología, lo importante para esta consulta "
                                  "y un breve historial. PDF, texto o directamente la pantalla."),
        ],
        "privacy_title": "Sus datos se quedan con usted",
        "privacy": [
            "El historial se guarda solo en su teléfono. Sin cuentas ni servidores: no podemos "
            "leerlo, recuperarlo ni entregárselo a nadie.",
            "Las preguntas de seguimiento las genera el modelo de Apple integrado en iOS, y el texto "
            "libre también se traduce en el dispositivo. Sus palabras no salen a internet.",
        ],
        "privacy_link": "Leer la política de privacidad completa",
        "sources_title": "De dónde salen los nombres",
        "sources": "Los diagnósticos vienen de la CIE-11 de la OMS (30 000 códigos con traducciones "
                   "oficiales a tres idiomas) y de la CIE-10. Los medicamentos, de la clasificación ATC "
                   "de la OMS. Por eso «tiroides» encuentra «Hipotiroidismo» y un médico ruso ve "
                   "«Гипотиреоз»: es el mismo código.",
        "faq_title": "Preguntas",
        "faq": [
            ("¿Diagnostica?", "No. La app no diagnostica, no clasifica la urgencia y no recomienda "
                              "tratamientos. Ayuda a ordenar lo que quiere contarle al médico y no "
                              "sustituye la atención médica."),
            ("¿Hace falta internet?", "No. Los catálogos van dentro de la app; las preguntas y la "
                                      "traducción funcionan en el propio teléfono."),
            ("¿Qué es gratis?", "Todo salvo traducir el resumen a otro idioma: el perfil, la entrevista, "
                                "el resumen y el PDF en su idioma no cuestan nada."),
            ("¿Qué pasa con mis datos si borro la app?", "Se van con ella: no guardamos ninguna copia. "
                                                         "Antes puede guardar un archivo de respaldo y llevar el historial a otro teléfono."),
            ("¿Funciona sin Salud de Apple?", "Sí. Salud solo evita teclear el peso, la estatura y los "
                                              "medicamentos; conectarlo es opcional."),
        ],
        "footer_privacy": "Política de privacidad",
        "footer_support": "Soporte",
        "support_title": "Soporte",
        "support_lede": "Escríbanos: solemos responder en un par de días.",
        "support_blocks": [
            ("Cómo contactarnos", f"Correo: <a href=\"mailto:{EMAIL}\">{EMAIL}</a>. Cuéntenos qué pasó "
                                  "y en qué pantalla; con eso suele bastar. Adjunte una captura si la tiene."),
            ("Los datos de Salud no llegaron",
             "Apple comparte los medicamentos de uno en uno: hay que marcarlos en la ventana del sistema. "
             "Puede abrirla de nuevo en Ajustes → Salud de Apple. La lectura de la lista funciona a partir de iOS 26."),
            ("Han desaparecido mis registros",
             "El historial vive solo en su teléfono, así que no podemos recuperarlo. Si hizo una copia, "
             "abra Ajustes → Restaurar desde una copia."),
            ("Pasar el historial a otro teléfono",
             "En el antiguo: Ajustes → Guardar una copia. En el nuevo: Restaurar desde una copia."),
        ],
        "back": "Volver al inicio",
    },
}

ORDER = ["ru", "en", "es"]


def path_to(target: str, page: str = "index", *, current: str = "ru") -> str:
    """Ссылки относительные: сайт может лежать в подпапке домена
    (github.io/medistory-site/), и абсолютные пути там ведут в никуда.

    Русская версия лежит в корне, остальные — в подпапках по коду языка.
    """
    if target == current:
        return f"{page}.html"
    up = "" if current == "ru" else "../"
    down = "" if target == "ru" else f"{target}/"
    return f"{up}{down}{page}.html"


def lang_nav(current: str, page: str) -> str:
    links = []
    for code in ORDER:
        mark = ' aria-current="page"' if code == current else ""
        href = path_to(code, page, current=current)
        links.append(f'<a href="{href}"{mark}>{CONTENT[code]["label"]}</a>')
    return '<nav class="langs">' + "".join(links) + "</nav>"


def shell(c: dict, page: str, body: str, title: str) -> str:
    assets = "assets" if c["lang"] == "ru" else "../assets"
    return f"""<!doctype html>
<html lang="{c['lang']}">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>{html.escape(title)}</title>
<meta name="description" content="{html.escape(c['meta'])}">
<meta property="og:title" content="{html.escape(title)}">
<meta property="og:description" content="{html.escape(c['meta'])}">
<meta property="og:image" content="{assets}/icon.png">
<link rel="icon" href="{assets}/icon.png">
<style>{CSS}</style>
</head>
<body>
<main>
{body}
<footer>
  <p>© 2026 Medistory ·
     <a href="{PRIVACY_URL}">{html.escape(c['footer_privacy'])}</a> ·
     <a href="{path_to(c['lang'], 'support', current=c['lang'])}">{html.escape(c['footer_support'])}</a> ·
     <a href="mailto:{EMAIL}">{EMAIL}</a></p>
</footer>
{lang_nav(c['lang'], page)}
</main>
</body>
</html>
"""


def landing(c: dict) -> str:
    assets = "assets" if c["lang"] == "ru" else "../assets"
    # The store URL carries query parameters, so & has to be escaped here.
    cta_href = html.escape(APPSTORE_URL or f"mailto:{EMAIL}", quote=True)

    cards = "".join(
        f'<div class="card"><h3>{html.escape(t)}</h3><p>{html.escape(d)}</p></div>'
        for t, d in c["what"]
    )
    steps = "".join(
        f'<li><h3>{html.escape(t)}</h3><p style="color:var(--muted);margin:0">{html.escape(d)}</p></li>'
        for t, d in c["how"]
    )
    privacy = "".join(f"<p>{html.escape(p)}</p>" for p in c["privacy"])
    faq = "".join(
        f"<details><summary>{html.escape(q)}</summary><p>{html.escape(a)}</p></details>"
        for q, a in c["faq"]
    )

    body = f"""
<div class="hero">
  <img class="branch" src="{assets}/branch.png" alt="">
  <img class="icon" src="{assets}/icon.png" alt="Medistory">
  <h1>Medistory</h1>
  <p class="lede" style="margin-bottom:18px">{html.escape(c['tagline'])}</p>
  <p class="lede">{html.escape(c['lede'])}</p>
  <a class="cta" href="{cta_href}">{html.escape(c['cta'])}</a>
  <p style="color:var(--muted);font-size:14px;margin-top:10px">{html.escape(c['cta_note'])}</p>
</div>

<h2>{html.escape(c['what_title'])}</h2>
<div class="cards">{cards}</div>

<h2>{html.escape(c['how_title'])}</h2>
<ol class="steps">{steps}</ol>

<h2>{html.escape(c['privacy_title'])}</h2>
<div class="note">{privacy}
  <p style="margin-top:14px"><a href="{PRIVACY_URL}">{html.escape(c['privacy_link'])} →</a></p>
</div>

<h2>{html.escape(c['sources_title'])}</h2>
<p style="color:var(--muted)">{html.escape(c['sources'])}</p>

<h2>{html.escape(c['faq_title'])}</h2>
<div class="faq">{faq}</div>
"""
    return shell(c, "index", body, c["title"])


def support(c: dict) -> str:
    blocks = "".join(
        f'<div class="card" style="margin-bottom:14px"><h3>{html.escape(t)}</h3>'
        f'<p>{d}</p></div>'
        for t, d in c["support_blocks"]
    )
    body = f"""
<div class="hero" style="padding-bottom:0">
  <h1>{html.escape(c['support_title'])}</h1>
  <p class="lede">{html.escape(c['support_lede'])}</p>
</div>
{blocks}
<div class="card"><h3>{html.escape(c['privacy_title'])}</h3>
  <p><a href="{PRIVACY_URL}">{html.escape(c['privacy_link'])} →</a></p></div>
<p style="margin-top:28px"><a href="{path_to(c['lang'], current=c['lang'])}">← {html.escape(c['back'])}</a></p>
"""
    return shell(c, "support", body, f"Medistory — {c['support_title']}")


def build() -> None:
    if DIST.exists():
        shutil.rmtree(DIST)
    DIST.mkdir(parents=True)
    shutil.copytree(ROOT / "assets", DIST / "assets")

    written = []
    for code in ORDER:
        c = CONTENT[code]
        folder = DIST if code == "ru" else DIST / code
        folder.mkdir(exist_ok=True)
        (folder / "index.html").write_text(landing(c), encoding="utf-8")
        (folder / "support.html").write_text(support(c), encoding="utf-8")
        written += [f"{code}: index.html", f"{code}: support.html"]

    # GitHub Pages не должен трогать вывод Jekyll'ом
    (DIST / ".nojekyll").write_text("", encoding="utf-8")

    print("Собрано в", DIST)
    for w in written:
        print("  ", w)


if __name__ == "__main__":
    build()
    sys.exit(0)
