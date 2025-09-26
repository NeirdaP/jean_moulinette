import os
import ayon_api
from ayon_core.pipeline.context_tools import get_current_context


def main():
    # Create folders
    texture_folder_relative_path = "/publish/image/imageTexture"
    current_folder_path = get_current_folder_full_path()
    texture_folder_path = f"{current_folder_path}{texture_folder_relative_path}"
    os.makedirs(texture_folder_path, exist_ok=True)

    # Open created folder in filesystem
    os.startfile(texture_folder_path)


def get_folder_from_context(context):
    project_name = context["project_name"]
    folder_path = context["folder_path"]
    folder = ayon_api.get_folder_by_path(project_name, folder_path)

    return folder


def get_current_folder_full_path():
    context = get_current_context()
    current_project_name = context["project_name"]
    current_folder = get_folder_from_context(context)
    current_folder_path = current_folder["path"]
    current_project_root_path = get_project_root_path(current_project_name)
    current_folder_full_path = f"{current_project_root_path}{current_folder_path}"

    return current_folder_full_path


def get_project_root_path(project_name):
    con = ayon_api.get_server_api_connection()
    project = con.get_project(project_name)

    roots = project["config"]["roots"]

    work_root = roots["work"]
    root_path = work_root["windows"]
    full_path = os.path.join(root_path, project_name)

    return full_path
