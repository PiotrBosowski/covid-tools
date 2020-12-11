import os
import re

def restart_numeration(path, dry_run=True, starting_index=1):
    pattern = r"model-([\d]*)(-.*)?"
    matcher = re.compile(pattern)
    item_names = [item for item in os.listdir(path)]
    item_names = sorted(item_names, key=lambda c: int(matcher.match(c).group(1)))
    for index, name in enumerate(item_names):
        match = matcher.match(name)
        if match:
            new_name = f"model-{index+starting_index}"
            print(f"Renaming {name} -> {new_name}")
            if not dry_run and name != new_name:
                os.rename(os.path.join(path, name), os.path.join(path, new_name))
    if dry_run:
        print("Run this command with dry_run=False to apply the changes.")

def restart_numeration_tree(path, dry_run=True):
    folders = [folder for folder in os.listdir(path) if os.path.isdir(path)]
    for folder in folders:
        restart_numeration(os.path.join(path, folder), dry_run)




restart_numeration_tree('/home/peter/covid/models')