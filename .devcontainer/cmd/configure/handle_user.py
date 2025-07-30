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

    # Save configuration to .conf file
    save_config_file(data1, devcontainer_path)
    
    return data1

def save_config_file(data1, devcontainer_path):
    """Save important configuration values to .conf file for later use"""
    
    # Extract important values from the devcontainer configuration
    config_data = {
        'REMOTE_USER': data1.get('remoteUser', 'vscode'),
        'CONTAINER_NAME': data1.get('name', 'devcontainer'),
        'IMAGE': data1.get('image', ''),
        'USER_ID': '',
        'GROUP_ID': ''
    }
    
    # Extract user ID and group ID from runArgs if present
    run_args = data1.get('runArgs', [])
    for arg in run_args:
        if arg.startswith('--user='):
            user_info = arg.replace('--user=', '')
            if ':' in user_info:
                config_data['USER_ID'], config_data['GROUP_ID'] = user_info.split(':')
            else:
                config_data['USER_ID'] = user_info
    
    # Create .conf file content
    conf_content = f"""# Devcontainer Configuration
# Generated automatically - do not edit manually

# User Configuration
REMOTE_USER={config_data['REMOTE_USER']}
USER_ID={config_data['USER_ID']}
GROUP_ID={config_data['GROUP_ID']}

# Container Configuration  
CONTAINER_NAME={config_data['CONTAINER_NAME']}
IMAGE={config_data['IMAGE']}

# Usage Examples:
# docker exec -it $(docker ps -q --filter "label=devcontainer.local_folder") bash
# docker exec -it --user {config_data['REMOTE_USER']} $(docker ps -q --filter "name=vsc-") bash
"""
    
    # Save to .devcontainer/.conf
    conf_path = os.path.join(devcontainer_path, '.conf')
    with open(conf_path, 'w') as f:
        f.write(conf_content)
    
    print(f"Configuration saved to {conf_path}")
    return conf_path