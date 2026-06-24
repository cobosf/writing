import os
import re
from pathlib import Path
from datetime import datetime

ARTICLES_DIR = "articles"
TEMPLATE_FILE = "templates/article.html"
OUTPUT_DIR = "generated"

os.makedirs(OUTPUT_DIR, exist_ok=True)

with open(TEMPLATE_FILE, "r", encoding="utf-8") as f:
    template = f.read()

for md_file in Path(ARTICLES_DIR).glob("*.md"):

    with open(md_file, "r", encoding="utf-8") as f:
        text = f.read()

    # Frontmatter
    frontmatter_match = re.match(
        r"---\n(.*?)\n---\n(.*)",
        text,
        re.S
    )

    if not frontmatter_match:
        continue

    frontmatter = frontmatter_match.group(1)
    content = frontmatter_match.group(2)

    metadata = {}

    for line in frontmatter.splitlines():
        if ":" in line:
            key, value = line.split(":", 1)
            metadata[key.strip()] = value.strip()

    # Reading time
    words = len(content.split())
    reading_time = max(2, round(words / 200))

    # Format date
    formatted_date = metadata.get("date", "")

    try:
        formatted_date = datetime.strptime(
            formatted_date,
            "%Y-%m-%d"
        ).strftime("%B %Y")
    except:
        pass

    # Markdown -> HTML

    html_content = content

    # Italics (*text*)
    html_content = re.sub(
        r"\*(.*?)\*",
        r"<em>\1</em>",
        html_content
    )

    # Blockquotes (> text)
    html_content = re.sub(
        r"^> (.+)$",
        r"<blockquote>\1</blockquote>",
        html_content,
        flags=re.MULTILINE
    )

    # H2
    html_content = re.sub(
        r"^## (.+)$",
        r"<h2>\1</h2>",
        html_content,
        flags=re.MULTILINE
    )

    # Horizontal rule
    html_content = html_content.replace(
        "\n---\n",
        "<hr>"
    )

    # Paragraphs
    paragraphs = []

    for block in html_content.split("\n\n"):

        block = block.strip()

        if not block:
            continue

        if block.startswith("<h2>"):
            paragraphs.append(block)

        elif block.startswith("<blockquote>"):
            paragraphs.append(block)

        elif block.startswith("<hr>"):
            paragraphs.append(block)

        else:
            paragraphs.append(f"<p>{block}</p>")

    html_content = "\n".join(paragraphs)

    # Apply template

    page = template

    page = page.replace(
        "{{title}}",
        metadata.get("title", "")
    )

    page = page.replace(
        "{{description}}",
        metadata.get("description", "")
    )

    page = page.replace(
        "{{date}}",
        formatted_date
    )

    page = page.replace(
        "{{readingTime}}",
        str(reading_time)
    )

    page = page.replace(
        "{{content}}",
        html_content
    )

    slug = md_file.stem

    output_file = f"{OUTPUT_DIR}/{slug}.html"

    with open(output_file, "w", encoding="utf-8") as f:
        f.write(page)

    print(f"Generated: {output_file}")