import os
import pathlib
import importlib
import ayon_api

from . import addon
from .version import __version__

def execute_script(project, script_name, dcc=None):
    # From the given name, seek out the matching script file and execute it
    script_path = get_scripts(project, dcc).get(script_name)
    if not script_path:
        print("Given script name was not found in the registry of scripts, verify name and jean_moulinette addon")
        return

    spec = importlib.util.spec_from_file_location(script_name, script_path)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)


def get_scripts(project, dcc=None):
    # Return all the registered scripts, optionally only for certain DCC
    from . import scripts
    script_names_to_path = {}

    def filter_scripts_from_root(script_names_to_path, root):
        all_files = root.rglob("*")

        for path in all_files:
            basename,ext = os.path.splitext(os.path.basename(path))
            if (ext!=".py") or (basename == "__init__") or (basename in script_names_to_path):        # Only consider non init python files that haven't already been added
                continue
            script_names_to_path[basename] = path
        return script_names_to_path

    # Start by collecting paths from addon scripts dir
    script_names_to_path = filter_scripts_from_root(script_names_to_path, pathlib.Path(os.path.dirname(scripts.__file__)))

    # Add any modules found in scripts hot directory defined in addon settings
    scripts_hot_dir = ayon_api.get_addon_project_settings(
        addon.ADDON_NAME, 
        __version__, 
        project).get("scripts_hot_directory")
    
    if os.path.exists(scripts_hot_dir) and os.path.isdir(scripts_hot_dir):
        script_names_to_path = filter_scripts_from_root(script_names_to_path, pathlib.Path(scripts_hot_dir))

    return script_names_to_path