"""Module to scrape Wikipedia's 'vital articles' and store them in JSON files."""


from bs4 import BeautifulSoup
import json
import requests
from typing import Dict, List, Optional


STORAGE_LINK = "cache/vital_articles"

CATEGORIES = [
    "People",
    "History",
    "Geography",
    "Arts",
    "Philosophy and religion",
    "Everyday life",
    "Society and social sciences",
    "Biological and health sciences",
    "Physical sciences",
    "Technology",
    "Mathematics"
]

LEVEL_1_VITAL_ARTICLE_URLS = [f"{STORAGE_LINK}/lvl1_vital_articles.json"]
LEVEL_2_VITAL_ARTICLE_URLS = [f"{STORAGE_LINK}/lvl2_vital_articles.json"]
LEVEL_3_VITAL_ARTICLE_URLS = [f"{STORAGE_LINK}/lvl3_vital_articles.json"]
LEVEL_4_VITAL_ARTICLE_URLS = [
    f"{STORAGE_LINK}/lvl4_vital_articles/people.json",
    f"{STORAGE_LINK}/lvl4_vital_articles/history.json",
    f"{STORAGE_LINK}/lvl4_vital_articles/geography.json",
    f"{STORAGE_LINK}/lvl4_vital_articles/arts.json",
    f"{STORAGE_LINK}/lvl4_vital_articles/philosophy_and_religion.json",
    f"{STORAGE_LINK}/lvl4_vital_articles/everyday_life.json",
    f"{STORAGE_LINK}/lvl4_vital_articles/society_and_social_sciences.json",
    f"{STORAGE_LINK}/lvl4_vital_articles/biological_and_health_sciences.json",
    f"{STORAGE_LINK}/lvl4_vital_articles/physical_sciences.json",
    f"{STORAGE_LINK}/lvl4_vital_articles/technology.json",
    f"{STORAGE_LINK}/lvl4_vital_articles/mathematics.json"
]
LEVEL_5_VITAL_ARTICLE_URLS = [
    f"{STORAGE_LINK}/lvl5_vital_articles/people/writers_and_journalists.json",
    f"{STORAGE_LINK}/lvl5_vital_articles/people/artists_musicians_and_composers.json",
    f"{STORAGE_LINK}/lvl5_vital_articles/people/entertainers_directors_producers_and_screenwriters.json",
    f"{STORAGE_LINK}/lvl5_vital_articles/people/philosophers_historians_and_social_scientists.json",
    f"{STORAGE_LINK}/lvl5_vital_articles/people/religious_figures.json",
    f"{STORAGE_LINK}/lvl5_vital_articles/people/politicians_and_leaders.json",
    f"{STORAGE_LINK}/lvl5_vital_articles/people/military_personnel_revolutionaries_and_activists.json",
    f"{STORAGE_LINK}/lvl5_vital_articles/people/scientists_inventors_and_mathematicians.json",
    f"{STORAGE_LINK}/lvl5_vital_articles/people/sports_figures.json",
    f"{STORAGE_LINK}/lvl5_vital_articles/people/miscellaneous.json",
    f"{STORAGE_LINK}/lvl5_vital_articles/history/history.json",
    f"{STORAGE_LINK}/lvl5_vital_articles/geography/physical_geography.json",
    f"{STORAGE_LINK}/lvl5_vital_articles/geography/countries_and_subdivisions.json",
    f"{STORAGE_LINK}/lvl5_vital_articles/geography/cities.json",
    f"{STORAGE_LINK}/lvl5_vital_articles/arts/arts.json",
    f"{STORAGE_LINK}/lvl5_vital_articles/philosophy_and_religion/philosophy_and_religion.json",
    f"{STORAGE_LINK}/lvl5_vital_articles/everyday_life/everyday_life.json",
    f"{STORAGE_LINK}/lvl5_vital_articles/everyday_life/sports_games_and_recreation.json",
    f"{STORAGE_LINK}/lvl5_vital_articles/society_and_social_sciences/social_studies.json",
    f"{STORAGE_LINK}/lvl5_vital_articles/society_and_social_sciences/politics_and_economics.json",
    f"{STORAGE_LINK}/lvl5_vital_articles/society_and_social_sciences/culture.json",
    f"{STORAGE_LINK}/lvl5_vital_articles/biological_and_health_sciences/biology_biochemistry_anatomy_and_physiology.json",
    f"{STORAGE_LINK}/lvl5_vital_articles/biological_and_health_sciences/animals.json",
    f"{STORAGE_LINK}/lvl5_vital_articles/biological_and_health_sciences/plants_fungi_and_other_organisms.json",
    f"{STORAGE_LINK}/lvl5_vital_articles/biological_and_health_sciences/health_medicine_and_disease.json",
    f"{STORAGE_LINK}/lvl5_vital_articles/physical_sciences/basics_and_measurement.json",
    f"{STORAGE_LINK}/lvl5_vital_articles/physical_sciences/astronomy.json",
    f"{STORAGE_LINK}/lvl5_vital_articles/physical_sciences/chemistry.json",
    f"{STORAGE_LINK}/lvl5_vital_articles/physical_sciences/earth_science.json",
    f"{STORAGE_LINK}/lvl5_vital_articles/physical_sciences/physics.json",
    f"{STORAGE_LINK}/lvl5_vital_articles/technology/technology.json",
    f"{STORAGE_LINK}/lvl5_vital_articles/mathematics/mathematics.json",
]


def parse_upper_level_list(url: str, default_level: int) -> Dict[str, int]:
    """Parse a Level 4 subsection of articles.
    
    Parameters
    ----------
    url: str
        The URL pointing to the Wikipedia page listing a given
        subcategory of Level 4 articles.
    
    Returns
    -------
    Dict[str, int]
        A dictionary containing the title of the article, which points
        to the integer value of its level. Level 4 articles and beyond
        will also store articles of lower level as they appear.
    """

    articles: Dict[str, int] = {}
    soup = BeautifulSoup(  # get soup
        requests.get(url).text, 'html.parser'
    ).find(
        'div', attrs={"id": "mw-content-text"}
    ).find(
        'div', attrs={"class": "mw-parser-output"}
    )
    for table in soup.find_all('table') + soup.find_all('div', attrs={'class': 'div-col'}) + soup.find_all('ol', recursive=False):
        if table.has_attr('class') and ("mw-collapsible" in table['class'] or "navbox-subgroup" in table['class']): continue  # avoid getting footer table
        for li in table.find_all('li'):
            title: Optional[str] = None
            level: int = default_level
            for a_tag in li.find_all('a'):
                if not a_tag.has_attr('title'): continue
                if a_tag.has_attr('class') and "image" in a_tag['class']: continue  # skip article-rank icons
                if a_tag.has_attr('href') and "#" in a_tag['href']: continue  # skip section tags
                if "Wikipedia:Vital articles" in a_tag['title']:  # article has a different level
                    level = int(a_tag.text[-1])
                    continue
                if title: break
                if "Wikipedia:" in a_tag['title']: break  # bad link
                title = a_tag['title']
            if not title: continue
            articles[title] = level
    return articles


def parse_level_four_articles() -> Dict[str, Dict[str, int]]:
    """Parse all level four vital articles, returning each subcategory and its corresponding items."""

    lvl4_articles = {
        "People": "https://en.wikipedia.org/wiki/Wikipedia:Vital_articles/Level/4/People",
        "History": "https://en.wikipedia.org/wiki/Wikipedia:Vital_articles/Level/4/History",
        "Geography": "https://en.wikipedia.org/wiki/Wikipedia:Vital_articles/Level/4/Geography",
        "Arts": "https://en.wikipedia.org/wiki/Wikipedia:Vital_articles/Level/4/Arts",
        "Philosophy and religion": "https://en.wikipedia.org/wiki/Wikipedia:Vital_articles/Level/4/Philosophy_and_religion",
        "Everyday life": "https://en.wikipedia.org/wiki/Wikipedia:Vital_articles/Level/4/Everyday_life",
        "Society and social sciences": "https://en.wikipedia.org/wiki/Wikipedia:Vital_articles/Level/4/Society_and_social_sciences",
        "Biological and health sciences": "https://en.wikipedia.org/wiki/Wikipedia:Vital_articles/Level/4/Biology_and_health_sciences",
        "Physical sciences": "https://en.wikipedia.org/wiki/Wikipedia:Vital_articles/Level/4/Physical_sciences",
        "Technology": "https://en.wikipedia.org/wiki/Wikipedia:Vital_articles/Level/4/Technology",
        "Mathematics": "https://en.wikipedia.org/wiki/Wikipedia:Vital_articles/Level/4/Mathematics"
    }

    all_articles: Dict[str, Dict[str, int]] = {}

    for group, url in lvl4_articles.items():
        print(f"Parsing {group}...")
        articles = parse_upper_level_list(url, 4)
        all_articles[group] = articles

    return all_articles


def parse_level_five_articles() -> Dict[str, Dict[str, Dict[str, int]]]:
    """Parse all level five vital articles, returning each subcategory's subcategory, and its corresponding items."""

    lvl5_articles = {
        "People": {
            "Writers and journalists": "https://en.wikipedia.org/wiki/Wikipedia:Vital_articles/Level/5/People/Writers_and_journalists",
            "Artists, musicians, and composers": "https://en.wikipedia.org/wiki/Wikipedia:Vital_articles/Level/5/People/Artists,_musicians,_and_composers",
            "Entertainers, directors, producers, and screenwriters": "https://en.wikipedia.org/wiki/Wikipedia:Vital_articles/Level/5/People/Entertainers,_directors,_producers,_and_screenwriters",
            "Philosophers, historians, and social scientists": "https://en.wikipedia.org/wiki/Wikipedia:Vital_articles/Level/5/People/Philosophers,_historians,_political_and_social_scientists",
            "Religious figures": "https://en.wikipedia.org/wiki/Wikipedia:Vital_articles/Level/5/People/Religious_figures",
            "Politicians and leaders": "https://en.wikipedia.org/wiki/Wikipedia:Vital_articles/Level/5/People/Politicians_and_leaders",
            "Military personnel, revolutionaries, and activists": "https://en.wikipedia.org/wiki/Wikipedia:Vital_articles/Level/5/People/Military_personnel,_revolutionaries,_and_activists",
            "Scientists, inventors, and mathematicians": "https://en.wikipedia.org/wiki/Wikipedia:Vital_articles/Level/5/People/Scientists,_inventors,_and_mathematicians",
            "Sports figures": "https://en.wikipedia.org/wiki/Wikipedia:Vital_articles/Level/5/People/Sports_figures",
            "Miscellaneous": "https://en.wikipedia.org/wiki/Wikipedia:Vital_articles/Level/5/People/Miscellaneous"
        },
        "History": {
            "History": "https://en.wikipedia.org/wiki/Wikipedia:Vital_articles/Level/5/History"
        },
        "Geography": {
            "Physical geography": "https://en.wikipedia.org/wiki/Wikipedia:Vital_articles/Level/5/Geography/Physical",
            "Countries and subdivisions": "https://en.wikipedia.org/wiki/Wikipedia:Vital_articles/Level/5/Geography/Countries",
            "Cities": "https://en.wikipedia.org/wiki/Wikipedia:Vital_articles/Level/5/Geography/Cities"
        },
        "Arts": {
            "Arts": "https://en.wikipedia.org/wiki/Wikipedia:Vital_articles/Level/5/Arts"
        },
        "Philosophy and religion": {
            "Philosophy and religion": "https://en.wikipedia.org/wiki/Wikipedia:Vital_articles/Level/5/Philosophy_and_religion"
        },
        "Everyday life": {
            "Everyday life": "https://en.wikipedia.org/wiki/Wikipedia:Vital_articles/Level/5/Everyday_life",
            "Sports, games and recreation": "https://en.wikipedia.org/wiki/Wikipedia:Vital_articles/Level/5/Everyday_life/Sports,_games_and_recreation"
        },
        "Society and social sciences": {
            "Social studies": "https://en.wikipedia.org/wiki/Wikipedia:Vital_articles/Level/5/Society_and_social_sciences/Social_studies",
            "Politics and economics": "https://en.wikipedia.org/wiki/Wikipedia:Vital_articles/Level/5/Society_and_social_sciences/Politics_and_economics",
            "Culture": "https://en.wikipedia.org/wiki/Wikipedia:Vital_articles/Level/5/Society_and_social_sciences/Culture"
        },
        "Biological and health sciences": {
            "Biology, biochemistry, anatomy, and physiology": "https://en.wikipedia.org/wiki/Wikipedia:Vital_articles/Level/5/Biological_and_health_sciences/Biology",
            "Animals": "https://en.wikipedia.org/wiki/Wikipedia:Vital_articles/Level/5/Biological_and_health_sciences/Animals",
            "Plants, fungi, and other organisms": "https://en.wikipedia.org/wiki/Wikipedia:Vital_articles/Level/5/Biological_and_health_sciences/Plants",
            "Health, medicine, and disease": "https://en.wikipedia.org/wiki/Wikipedia:Vital_articles/Level/5/Biological_and_health_sciences/Health"
        },
        "Physical sciences": {
            "Basics and measurement": "https://en.wikipedia.org/wiki/Wikipedia:Vital_articles/Level/5/Physical_sciences/Basics_and_measurement",
            "Astronomy": "https://en.wikipedia.org/wiki/Wikipedia:Vital_articles/Level/5/Physical_sciences/Astronomy",
            "Chemistry": "https://en.wikipedia.org/wiki/Wikipedia:Vital_articles/Level/5/Physical_sciences/Chemistry",
            "Earth science": "https://en.wikipedia.org/wiki/Wikipedia:Vital_articles/Level/5/Physical_sciences/Earth_science",
            "Physics": "https://en.wikipedia.org/wiki/Wikipedia:Vital_articles/Level/5/Physical_sciences/Physics"
        },
        "Technology": {
            "Technology": "https://en.wikipedia.org/wiki/Wikipedia:Vital_articles/Level/5/Technology"
        },
        "Mathematics": {
            "Mathematics": "https://en.wikipedia.org/wiki/Wikipedia:Vital_articles/Level/5/Mathematics"
        }
    }

    all_articles: Dict[str, Dict[str, Dict[str, int]]] = {}

    for group, subgroups in lvl5_articles.items():
        group_article: Dict[str, Dict[str, int]] = {}
        for subgroup, url in subgroups.items():
            print(f"Parsing {group}/{subgroup}...")
            articles: Dict[str, int] = parse_upper_level_list(url, 5)
            group_article[subgroup] = articles
        all_articles[group] = group_article

    return all_articles


def combine_all_articles():
    """Combine all *_vital_articles.json files into one file."""

    FILENAME = f"{STORAGE_LINK}/vital_articles.json"

    filenames = LEVEL_1_VITAL_ARTICLE_URLS \
              + LEVEL_2_VITAL_ARTICLE_URLS \
              + LEVEL_3_VITAL_ARTICLE_URLS \
              + LEVEL_4_VITAL_ARTICLE_URLS \
              + LEVEL_5_VITAL_ARTICLE_URLS

    articles = {}
    # Read all
    for filename in filenames:
        print(f"Reading {filename}...")
        raw_articles = {}
        with open(f"{STORAGE_LINK}/{filename}", "r") as infile:
            raw_articles = json.load(infile)
        for title, level in raw_articles.items():
            if title in articles.keys(): continue
            articles[title] = level
    # Write
    with open(FILENAME, "w+") as outfile:
        json.dump(articles, outfile, indent=4)


def get_vital_articles_at_level(level: int) -> Optional[List[str]]:
    """Retrieve a list of vital articles at a given level."""
    if level > 5 or level < 1:
        return None
    
    urls_to_parse = []
    if level == 1:  # yes, this is "naive fizz-buzz"-level code, but vital article levels likely wont grow past 5
        urls_to_parse = LEVEL_1_VITAL_ARTICLE_URLS
    elif level == 2:
        urls_to_parse = LEVEL_2_VITAL_ARTICLE_URLS
    elif level == 3:
        urls_to_parse = LEVEL_3_VITAL_ARTICLE_URLS
    elif level == 4:
        urls_to_parse = LEVEL_4_VITAL_ARTICLE_URLS
    else:
        urls_to_parse = LEVEL_5_VITAL_ARTICLE_URLS

    article_names = []
    for url in urls_to_parse:
        with open(url, "r") as infile:
            article_names.extend(json.load(infile).keys())
    
    return article_names


def get_vital_articles_by_category(category: str) -> Optional[List[str]]:
    """Given the name of a vital article category, return all level <=5 article titles."""

    if category not in CATEGORIES: return None

    urls = [url for url in LEVEL_5_VITAL_ARTICLE_URLS if category.lower().replace(' ', '_') in url]
    article_titles = []
    for url in urls:
        with open(url, "r") as infile:
            article_titles.extend(json.load(infile).keys())

    return article_titles


if __name__=='__main__':

    lvl4_articles = parse_level_four_articles()

    for group, articles in lvl4_articles.items():
        filename = f"{STORAGE_LINK}/lvl4_vital_articles/{group.lower().replace(' ', '_')}.json"
        with open(filename, "w+") as outfile:
            json.dump(articles, outfile, indent=4)


    lvl5_articles = parse_level_five_articles()

    for group, subgroups in lvl5_articles.items():
        for subgroup, articles in subgroups.items():
            filename = f"{STORAGE_LINK}/lvl5_vital_articles/{group.lower().replace(' ', '_')}/{subgroup.lower().replace(',', '').replace(' ', '_')}.json"
            with open(filename, "w+") as outfile:
                json.dump(articles, outfile, indent=4)

    combine_all_articles()
