import os
import ayon_api
from ayon_maya.api import workfile_template_builder
from ayon_core.pipeline.workfile import path_resolving, utils
from ayon_core.pipeline.context_tools import get_current_context

def main():
    print ("Initializing workfile...")

    # Only run initialize if no other workfile is available on disk 
    # may later allow init of previously saved scenes
    context = get_current_context()
    project = ayon_api.get_project(context.get("project_name"))
    folder = ayon_api.get_folder_by_path(context.get("project_name"), context.get("folder_path"))
    task = ayon_api.get_task_by_name(context.get("project_name"), folder.get("id"), context.get("task_name"))
    workdir = path_resolving.get_workdir(project, folder, task, "maya")
    prior_workfiles = [workfile for workfile in os.listdir(workdir) if workfile.endswith(".ma")]

    if prior_workfiles:
        print("Skipping scene initialization for {} because workfile(s) already exist".format(context.get("folder_path")))
        return

    try:
        workfile_template_builder.build_workfile_template()
        utils.save_next_version(description="First workfile automatic build and save by jean moulinette")
    except Exception as e:
        print("Hit exception during scene build: {}".format(e))

        
main()