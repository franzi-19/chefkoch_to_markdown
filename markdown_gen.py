from chefkoch_to_markdown.scrape import get_recipe_data
from argparse import ArgumentParser, FileType
import re

def get_title(url):
    return get_recipe_data(url).name

def get_markdown_of_unknown_side(url, id):
    return f"""
# Unkown
### #{id}
## Informationen
* Entspricht bei Multiplikator 1: 0 Portionen
...Metadaten(Zubereitungszeit etc.)...

## Zubereitung
### Gericht
...Zutaten...

...Zubereitung...

## Kommentare

## Schlagwörter
...Tags...

## Quelle
<{url}>
    """.strip() + "\n"


def get_markdown(url, id): # returns converted recipe in markdown
    data = get_recipe_data(url)

    ingredients = "\n".join(f"* {re.sub(r' ', '', amount)} {what}" for amount, what in data.ingredients)
    interesting_meta = [(key, val) for key, val in data.meta.items() if key[0].isupper()]
    meta = "\n".join(f"* {key}: {val}" for (key,val) in interesting_meta)
    tags = "\n".join(f"* {tag}" for tag in data.tags)

    return f"""
# {data.name}
### #{id}
## Informationen
* Entspricht bei Multiplikator 1: {data.servings} Portionen
{meta}

## Zubereitung
### Gericht
{ingredients}

{data.preparation}

## Kommentare

## Schlagwörter
{tags}

## Quelle
<{url}>
    """.strip() + "\n"

def main():
    parser = ArgumentParser(description="Generate markdown from a URL")
    parser.add_argument("URL", help="The target URL")
    parser.add_argument("FILE", help="The markdown file", type=FileType(mode="w"))

    args = parser.parse_args()
    markdown, _ = get_markdown(args.URL)
    args.FILE.write(markdown)

if __name__ == '__main__':
    main()
