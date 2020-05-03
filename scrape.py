import requests
import bs4
from dataclasses import dataclass, field
import re
import sys

@dataclass
class RecipeData:
    name: str = ""
    meta: dict = field(default_factory=dict)
    servings: int = 0
    ingredients: list = field(default_factory=list)
    preparation: str = ""
    tags: set = field(default_factory=set)

def consolidate_text(text):
    return re.sub(r" +", " ", text)

def get_recipe_data(url) -> RecipeData:
    r = requests.get(url)
    content = r.text
    soup = bs4.BeautifulSoup(content, features="html.parser")
    recipe = RecipeData()
    recipe.name = soup.h1.text
    for meta_el in soup.select(".ds-recipe-meta span"):
        if meta_el.has_attr("class"):
            name = meta_el["class"][0]
            if name.startswith("recipe-"):
                name = name[len("recipe-"):]
            val = re.search(r"[\w\s\.]+", meta_el.text).group(0).strip()
        else:
            (name, val) = map(str.strip, re.search(r"[\w\s\.\-/]+", meta_el.text).group(0).strip().split("ca."))
        recipe.meta[name] = val

    recipe.servings = int(soup.select_one("div.recipe-servings input")["value"])

    for ingredient_row in soup.select("table.ingredients tr"):
        res = ingredient_row.select("td span")
        if len(res) == 1:
            # Got an ingredient without amount, insert an empty string for the amount
            t = "", consolidate_text(res[0].text.strip())
        elif len(res) == 2:
            # Got and ingredient with amount
            amount, what = res
            t = tuple(map(lambda e: consolidate_text(e.text.strip()), (amount,what)))
        else:
            print("Probably got multiple sections in ingredients; this might result in a wrong list of ingredients!", file=sys.stderr)
            continue
        recipe.ingredients.append(t)


    prep_heading = soup.find("h2", text="Zubereitung")
    recipe.preparation = prep_heading.find_next_sibling("div").text.strip()

    recipe.tags.update(t.text.strip() for t in soup.select(".ds-tag"))

    return recipe
