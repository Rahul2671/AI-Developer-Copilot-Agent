import os
import json


PROJECT_DIR = "data/projects"


os.makedirs(
    PROJECT_DIR,
    exist_ok=True
)


def save_project(
    project_id,
    data
):

    path = f"{PROJECT_DIR}/{project_id}.json"


    with open(path,"w") as f:
        json.dump(
            data,
            f,
            indent=4
        )


    return path



def get_project(
    project_id
):

    path = f"{PROJECT_DIR}/{project_id}.json"


    if not os.path.exists(path):
        return None


    with open(path,"r") as f:
        return json.load(f)