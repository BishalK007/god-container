from utils import utils
from InquirerPy import inquirer

def handle_waypipe(data1, devcontainer_path):
    # Ask user for waypipe configuration
    answer = inquirer.select(
        "Do you want waypipe?",
        choices=["Yes", "No"]
    ).execute()
    print(f"Selected: {answer}")
    if answer == "Yes":
        print("Waypipe will be added to the configuration.")
    return utils.merge_jsonc_data(
            data1,
            utils.load_jsonc(f"{devcontainer_path}/templates/waypipe.jsonc")
        )