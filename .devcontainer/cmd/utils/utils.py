import commentjson
from deepmerge import always_merger

'''
    ************** Util functions **************
'''
def load_jsonc(path):
    with open(path, 'r') as f:
        return commentjson.load(f)

def merge_jsonc_data(data1, data2):
    data1_cpy = data1.copy()
    data2_cpy = data2.copy()
    merged = always_merger.merge(data1_cpy, data2_cpy)

    # Special handling for postCreateCommand
    if "postCreateCommand" in data1 and "postCreateCommand" in data2:
        cmd1 = data1["postCreateCommand"].strip()
        cmd2 = data2["postCreateCommand"].strip()
        print(f"postCreateCommand1: {cmd1}")
        print(f"postCreateCommand2: {cmd2}")
        # Concatenate with ' && ' if both are non-empty
        if cmd1 and cmd2:
            merged["postCreateCommand"] = f"{cmd1} && {cmd2}"
        else:
            merged["postCreateCommand"] = cmd1 or cmd2
    return merged

def save_jsonc(path, data):
    with open(path, 'w') as f:
        commentjson.dump(data, f, indent=4)