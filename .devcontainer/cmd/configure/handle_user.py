from utils import utils
from InquirerPy import inquirer
import pwd
import grp
import os

def handle_user(data1, devcontainer_path):
    user_json = utils.load_jsonc(f"{devcontainer_path}/templates/user.jsonc")
    
    # Ask user for user configuration
    answer = inquirer.select(
        message="Do you want default remote user as vscode",
        choices=[
            "Yes", 
            "No"
        ]
    ).execute()
    print(f"Selected: {answer}")
    if answer == "Yes":
        print("Default remote user vscode will be used.")
    elif answer == "No":
        print("Please provide a custom remote user name.")
        user_name = inquirer.text(message="Remote user name:").execute()
        print(f"Custom remote user name: {user_name}")
        user_json['remoteUser'] = user_name
        data1 = utils.merge_jsonc_data(data1, user_json)
    
    # Get all users and groups with their UIDs and GIDs
    user_objs = [u for u in pwd.getpwall()]
    group_objs = [g for g in grp.getgrall()]

    users = [f"{u.pw_name} (UID: {u.pw_uid})" for u in user_objs]
    groups = [f"{g.gr_name} (GID: {g.gr_gid})" for g in group_objs]

    uid = None
    gid = None

    # Ask user if they want to set a custom UID
    answer = inquirer.select(
        message="Do you want to set custom uid?",
        choices=["No (DEFAULT UID: 1000)", "Yes"]
    ).execute()
    print(f"Selected: {answer}")
    if answer == "Yes":
        uid_choice = inquirer.select(
            message="Select a user for UID or choose Custom:",
            choices=["Custom"] + users
        ).execute()
        print(f"Selected: {uid_choice}")
        if uid_choice == "Custom":
            uid = inquirer.text(message="Enter custom UID:").execute()
            print(f"Custom uid: {uid}")
        else:
            username = uid_choice.split(" (UID:")[0]
            user_info = pwd.getpwnam(username)
            uid = str(user_info.pw_uid)
            print(f"Custom uid: {uid}")

    # Ask user if they want to set a custom GID
    answer = inquirer.select(
        message="Do you want to set custom gid?",
        choices=["No (DEFAULT GID: 1000)", "Yes"],
    ).execute()
    print(f"Selected: {answer}")
    if answer == "Yes":
        gid_choice = inquirer.fuzzy(
            message="Select a group for GID or choose Custom:",
            choices=["Custom"] + groups,
            instruction="\n[Use <enter> to select/confirm, type to search\n Up/Down to navigate]",
        ).execute()
        print(f"Selected: {gid_choice}")
        if gid_choice == "Custom":
            gid = inquirer.text(message="Enter custom GID:").execute()
            print(f"Custom gid: {gid}")
        else:
            groupname = gid_choice.split(" (GID:")[0]
            group_info = grp.getgrnam(groupname)
            gid = str(group_info.gr_gid)
            print(f"Custom gid: {gid}")

    if uid is not None or gid is not None:
        # Only modify runArgs if user chose custom values
        # Use defaults if not set
        uid_val = uid if uid is not None else "1000"
        gid_val = gid if gid is not None else "1000"
        user_json['runArgs'] = [f"--user={uid_val}:{gid_val}"]
        print(f"Set custom runArgs: {user_json['runArgs']}")
    else:
        # User selected defaults for both UID and GID
        # The template already has the correct default values, so no need to modify
        print("Using default UID/GID from template (1000:1000)")
    
    # Always merge the user_json (which contains remoteUser and runArgs)
    data1 = utils.merge_jsonc_data(data1, user_json)
    
    return data1