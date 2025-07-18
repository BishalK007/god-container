import requests
from bs4 import BeautifulSoup
import commentjson
from InquirerPy import inquirer
from utils import utils


def scrape_devconainer_features():
    # https://containers.dev/features
    url = "https://containers.dev/features"
    response = requests.get(url)
    html = response.text
    # print(f"Scraped :::::: \n {html}\n\n\n\n")
    soup = BeautifulSoup(html, "html.parser")
    table = soup.find("table", id="collectionTable")
    rows = table.find_all("tr")[1:]  # Skip header row

    data = []
    for row in rows:
        cols = row.find_all("td")
        if len(cols) < 4:
            continue  # skip empty or malformed rows
        name_tag = cols[0].find("a")
        name = name_tag.text.strip() if name_tag else cols[0].text.strip()
        link = name_tag["href"] if name_tag else ""
        maintainer = cols[1].text.strip()
        reference = cols[2].find("code").text.strip() if cols[2].find("code") else cols[2].text.strip()
        version = cols[3].find("code").text.strip() if cols[3].find("code") else cols[3].text.strip()
        data.append({
            "name": name,
            "link": link,
            "maintainer": maintainer,
            "reference": reference,
            "version": version
        })

    return data
    
def make_json(selected, data):
    features = {}
    for item in data:
        label = f"{item['name']} ({item['version']})"
        if label in selected:
            features[item['reference']] = {} 
    result = {"features": features}
    print(commentjson.dumps(result, indent=2))
    return result

def search_add_feature(data):
    
    # data: list of dicts with 'name' key (and others)
    choices = [f"{item['name']} ({item['version']})" for item in data]
    selected = inquirer.fuzzy(
        message="Select features:",
        choices=choices,
        multiselect=True,
        instruction="\n[Use <tab> to select, type to search\n Up/Down to navigate, <enter> to confirm]",
    ).execute()

    return selected

    


def handle_add_feature(data1):
    data = scrape_devconainer_features()
    selected = search_add_feature(data)

    json_data = make_json(selected, data)

    return utils.merge_jsonc_data(
            data1,
            json_data
        )
