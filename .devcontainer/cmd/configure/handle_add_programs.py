import requests
from InquirerPy import inquirer
from utils import utils


def search_debian_packages(query):
    """Search for Debian packages using the packages.debian.org API"""
    try:
        # Use Debian package search API
        url = "https://packages.debian.org/search"
        params = {
            'keywords': query,
            'searchon': 'names',
            'suite': 'bookworm',
            'section': 'all'
        }
        
        response = requests.get(url, params=params, timeout=10)
        packages = []
        
        if response.status_code == 200:
            # Parse the HTML response to extract package names
            from bs4 import BeautifulSoup
            soup = BeautifulSoup(response.text, 'html.parser')
            
            # Find all h3 elements containing package names
            package_headers = soup.find_all('h3')
            
            for header in package_headers:
                # Extract package name from h3 text
                if header.text.startswith('Package '):
                    package_name = header.text.replace('Package ', '').strip()
                    
                    # Find the description in the next ul > li element
                    description = ""
                    next_ul = header.find_next_sibling('ul')
                    if next_ul:
                        first_li = next_ul.find('li')
                        if first_li:
                            # Extract description text after the suite info
                            text_parts = first_li.get_text().split(': ')
                            if len(text_parts) > 1:
                                description = text_parts[-1].strip()[:100]
                                if len(text_parts[-1]) > 100:
                                    description += "..."
                    
                    if package_name and description:
                        packages.append({
                            'name': package_name,
                            'description': description
                        })
        
        return packages[:30]  # Limit to 30 results for performance
    except Exception as e:
        print(f"Error searching packages: {e}")
        return []


def lazy_search_packages():
    """Implement lazy search with user interaction - starts empty, everything from network"""
    all_programs = []  # Start with empty list - everything comes from network
    
    while True:
        # Show current available programs count
        program_count = len(all_programs)
        choices = [
            "--- Search for packages ---",
            "--- Finish and select programs ---",
            "--- Skip program installation ---"
        ]
        
        if program_count > 0:
            choices.insert(-1, f"--- View found packages ({program_count} available) ---")
        
        action = inquirer.select(
            message="Choose an action:",
            choices=choices
        ).execute()
        
        if action == "--- Search for packages ---":
            search_query = inquirer.text(
                message="Enter search term (e.g., 'firefox', 'editor', 'media'):"
            ).execute()
            
            if search_query and len(search_query.strip()) >= 2:
                print(f"Searching for '{search_query}'...")
                search_results = search_debian_packages(search_query.strip())
                
                if search_results:
                    # Add new programs to the list (avoid duplicates)
                    existing_names = {prog['name'] for prog in all_programs}
                    new_programs = [prog for prog in search_results if prog['name'] not in existing_names]
                    all_programs.extend(new_programs)
                    print(f"Found {len(new_programs)} new packages. Total available: {len(all_programs)}")
                else:
                    print("No packages found for that search term")
            else:
                print("Search term too short. Please enter at least 2 characters.")
                
        elif action.startswith("--- View found packages"):
            # Show a preview of found packages
            if all_programs:
                print(f"\nFound packages ({len(all_programs)}):")
                for i, prog in enumerate(all_programs[:10]):  # Show first 10
                    print(f"  {i+1}. {prog['name']} - {prog['description']}")
                if len(all_programs) > 10:
                    print(f"  ... and {len(all_programs) - 10} more")
            
        elif action == "--- Finish and select programs ---":
            if len(all_programs) == 0:
                print("No packages found yet. Please search for packages first.")
                continue
            break
        
        elif action == "--- Skip program installation ---":
            print("Skipping program installation. No additional packages will be installed.")
            return []  # Return empty list to skip program installation
    
    return all_programs





def search_and_select_programs():
    """Interactive search and selection of programs with lazy search"""
    
    # First, let user search for packages
    all_programs = lazy_search_packages()
    
    # If user chose to skip, return empty list
    if not all_programs:
        return []
    
    # Now let them select from all available programs
    choices = [f"{prog['name']} - {prog['description']}" for prog in all_programs]
    
    selected = inquirer.fuzzy(
        message="Select programs to install:",
        choices=choices,
        multiselect=True,
        instruction="\n[Use <tab> to select, type to search, <enter> to confirm]"
    ).execute()
    
    # Extract program names from selections
    program_names = []
    for selection in selected:
        # Extract program name (before the first " - ")
        if " - " in selection:
            program_name = selection.split(" - ")[0]
            program_names.append(program_name)
    
    return program_names


def handle_add_programs(data1):
    """Handle adding programs to the devcontainer configuration"""
    
    print("Select programs to install in your devcontainer...")
    selected_programs = search_and_select_programs()
    
    if not selected_programs:
        print("No programs selected. Skipping package installation.")
        return data1
    
    print(f"\nSelected programs: {', '.join(selected_programs)}")
    
    # Create the install command
    install_command = f"sudo apt-get install -y {' '.join(selected_programs)}"
    
    # Create the configuration to merge
    program_config = {
        "postCreateCommand": install_command
    }
    
    print(f"Will add command: {install_command}")
    
    # Merge with existing configuration
    return utils.merge_jsonc_data(data1, program_config)