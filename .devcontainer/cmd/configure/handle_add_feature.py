import requests
from bs4 import BeautifulSoup
import commentjson
from InquirerPy import inquirer
from InquirerPy.base.control import Choice
from InquirerPy.separator import Separator
from utils import utils
import time
from typing import List, Dict, Any


def get_fallback_features() -> List[Dict[str, str]]:
    """
    Fallback list of popular devcontainer features when network request fails.
    
    Returns:
        List of dictionaries containing feature information
    """
    return [
        {
            "name": "Node.js (via nvm)",
            "link": "",
            "maintainer": "devcontainers",
            "reference": "ghcr.io/devcontainers/features/node:1",
            "version": "1"
        },
        {
            "name": "Python",
            "link": "",
            "maintainer": "devcontainers", 
            "reference": "ghcr.io/devcontainers/features/python:1",
            "version": "1"
        },
        {
            "name": "Docker (Docker-in-Docker)",
            "link": "",
            "maintainer": "devcontainers",
            "reference": "ghcr.io/devcontainers/features/docker-in-docker:2",
            "version": "2"
        },
        {
            "name": "Git (from source)",
            "link": "",
            "maintainer": "devcontainers",
            "reference": "ghcr.io/devcontainers/features/git:1",
            "version": "1"
        },
        {
            "name": "GitHub CLI",
            "link": "",
            "maintainer": "devcontainers",
            "reference": "ghcr.io/devcontainers/features/github-cli:1",
            "version": "1"
        },
        {
            "name": "Go",
            "link": "",
            "maintainer": "devcontainers",
            "reference": "ghcr.io/devcontainers/features/go:1",
            "version": "1"
        },
        {
            "name": "Rust",
            "link": "",
            "maintainer": "devcontainers",
            "reference": "ghcr.io/devcontainers/features/rust:1",
            "version": "1"
        },
        {
            "name": "Java (via SDKMAN!)",
            "link": "",
            "maintainer": "devcontainers",
            "reference": "ghcr.io/devcontainers/features/java:1",
            "version": "1"
        }
    ]


def scrape_devconainer_features() -> List[Dict[str, str]]:
    """
    Scrape devcontainer features from containers.dev with robust error handling.
    
    Attempts to fetch features from the official website with timeout and retry logic.
    Falls back to a curated list of popular features if the network request fails.
    
    Returns:
        List of dictionaries containing feature information
    """
    url = "https://containers.dev/features"
    max_retries = 2
    timeout = 10
    
    for attempt in range(max_retries):
        try:
            print(f"🔍 Fetching devcontainer features (attempt {attempt + 1}/{max_retries})...")
            
            response = requests.get(url, timeout=timeout)
            response.raise_for_status()  # Raise an exception for bad status codes
            
            html = response.text
            soup = BeautifulSoup(html, "html.parser")
            table = soup.find("table", id="collectionTable")
            
            if not table:
                print("⚠️  Could not find features table on the website")
                if attempt == max_retries - 1:
                    break
                continue
            
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
            
            if data:
                print(f"✅ Successfully fetched {len(data)} features from containers.dev")
                return data
            else:
                print("⚠️  No features found on the website")
                
        except requests.exceptions.Timeout:
            print(f"⏰ Request timed out (attempt {attempt + 1}/{max_retries})")
        except requests.exceptions.ConnectionError as e:
            print(f"🌐 Connection error (attempt {attempt + 1}/{max_retries}): {str(e)}")
        except requests.exceptions.RequestException as e:
            print(f"❌ Request failed (attempt {attempt + 1}/{max_retries}): {str(e)}")
        except Exception as e:
            print(f"❌ Unexpected error (attempt {attempt + 1}/{max_retries}): {str(e)}")
        
        if attempt < max_retries - 1:
            print("⏳ Retrying in 2 seconds...")
            time.sleep(2)
    
    # If all attempts failed, use fallback features
    print("🔄 Using fallback list of popular devcontainer features...")
    return get_fallback_features()
    
def make_json(selected: List[str], data: List[Dict[str, str]]) -> Dict[str, Any]:
    """
    Convert selected features into devcontainer.json format.
    
    Args:
        selected: List of selected feature labels
        data: List of feature dictionaries
        
    Returns:
        Dictionary in devcontainer.json features format
    """
    features = {}
    for item in data:
        label = f"{item['name']} ({item['version']})"
        if label in selected:
            features[item['reference']] = {} 
    
    result = {"features": features}
    if features:
        print(f"📦 Selected {len(features)} features:")
        print(commentjson.dumps(result, indent=2))
    else:
        print("📦 No features selected")
    
    return result


def search_add_feature(data: List[Dict[str, str]]) -> List[str]:
    """
    Interactive feature selection with skip option.
    
    Args:
        data: List of feature dictionaries
        
    Returns:
        List of selected feature labels
    """
    if not data:
        print("⚠️  No features available for selection")
        return []
    
    # First ask if they want to add features at all
    add_features = inquirer.confirm(
        message="Would you like to add devcontainer features? (Y/n)",
        default=True
    ).execute()
    
    if not add_features:
        print("⏭️  Skipping feature installation")
        return []
    
    # Prepare feature choices for fuzzy search (without separators)
    feature_choices = [f"{item['name']} ({item['version']})" for item in data]
    
    print(f"\n📦 Found {len(feature_choices)} available features")
    print("💡 Features provide additional tools and runtime environments for your devcontainer")
    
    selected = inquirer.fuzzy(
        message="Select devcontainer features to add (type to search):",
        choices=feature_choices,
        multiselect=True,
        instruction="\n[Use <tab> to select, type to search, Up/Down to navigate, <enter> to confirm]",
        border=True,
        validate=lambda result: len(result) >= 0,  # Allow empty selection
        invalid_message="Invalid selection"
    ).execute()
    
    if not selected:
        print("📦 No features selected")
    else:
        print(f"📦 Selected {len(selected)} features")
    
    return selected


def handle_add_feature(data1: Dict[str, Any]) -> Dict[str, Any]:
    """
    Handle the complete devcontainer feature addition workflow.
    
    Args:
        data1: Existing devcontainer configuration
        
    Returns:
        Updated devcontainer configuration with features
    """
    try:
        data = scrape_devconainer_features()
        selected = search_add_feature(data)
        
        if not selected:
            print("📦 No features will be added to the devcontainer")
            return data1
        
        json_data = make_json(selected, data)
        
        return utils.merge_jsonc_data(data1, json_data)
        
    except Exception as e:
        print(f"❌ Error during feature selection: {str(e)}")
        print("📦 Continuing without adding features...")
        return data1
