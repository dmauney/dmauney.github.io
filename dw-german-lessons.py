from urllib.request import Request, urlopen
from urllib.parse import urlparse, unquote
from html import escape
import xml.etree.ElementTree as ET


SITEMAP_URL = "https://learngerman.dw.com/de/lesson-sitemap.xml"
OUTPUT_FILE = "dw-lesson-sitemap-transcripts.html"


def get_sitemap():
    request = Request(
        SITEMAP_URL,
        headers={"User-Agent": "Mozilla/5.0"}
    )

    with urlopen(request, timeout=30) as response:
        return response.read()


def get_lesson_urls(xml_data):
    root = ET.fromstring(xml_data)

    namespace = {
        "sm": "http://www.sitemaps.org/schemas/sitemap/0.9"
    }

    urls = []

    for location in root.findall("sm:url/sm:loc", namespace):
        if location.text:
            url = location.text.strip().rstrip("/")

            if not url.endswith("/lm"):
                url += "/lm"

            urls.append(url)

    return urls


def get_title(url):
    """
    Convert:

    https://learngerman.dw.com/de/1-zugspitze/l-17389149/lm

    to:

    1 zugspitze
    """

    path = unquote(urlparse(url).path)

    if "/de/" in path:
        path = path.split("/de/", 1)[1]

    if "/l-" in path:
        path = path.split("/l-", 1)[0]

    return path.replace("-", " ")


def create_html(urls):
    links = []

    for url in urls:
        title = get_title(url)

        links.append(
            f'<li><a href="{escape(url, quote=True)}">'
            f'{escape(title)}</a></li>'
        )

    return f"""<!DOCTYPE html>
<html lang="de">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">

<title>DW German Lesson Transcripts</title>

<style>
body {{
    font-family: Arial, sans-serif;
    max-width: 1100px;
    margin: 30px auto;
    padding: 0 20px;
    line-height: 1.5;
}}

li {{
    margin: 7px 0;
}}

a {{
    color: #0645ad;
}}
</style>

</head>

<body>

<h1>DW German Lesson Transcripts</h1>

<p>{len(urls)} transcript links</p>

<ul>

{chr(10).join(links)}

</ul>

</body>
</html>
"""


def main():
    print(f"Reading sitemap: {SITEMAP_URL}")

    xml_data = get_sitemap()

    urls = get_lesson_urls(xml_data)

    print(f"Found {len(urls)} lessons.")

    html = create_html(urls)

    with open(OUTPUT_FILE, "w", encoding="utf-8") as f:
        f.write(html)

    print(f"Created: {OUTPUT_FILE}")


if __name__ == "__main__":
    main()