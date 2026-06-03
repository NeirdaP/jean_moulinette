import maya.cmds as cmds
from ayon_core.pipeline import context_tools
from ayon_core.pipeline import registered_host
from ayon_core.pipeline.create import CreateContext

from ayon_maya.api.workfile_template_builder import MayaTemplateBuilder, PLACEHOLDER_SET

def get_all_instances():
    instances = []
    object_sets = cmds.ls(type="objectSet")
    for object_set in object_sets:
        if not cmds.attributeQuery("productType", node=object_set, exists=True):
            continue
        instances.append(object_set)
    return instances


def get_instances_of_type(instance_type):
    instances = get_all_instances()
    instances_of_type = []
    for instance in instances:
        if cmds.getAttr(f"{instance}.productType") != instance_type:
            continue

        instances_of_type.append(instance)
    return instances_of_type


def get_placeholder_locators():
    placeholder_locators = []
    for locator in cmds.ls(type="locator"):
        locator_parents = cmds.listRelatives(locator, parent=True)
        if not locator_parents:
            continue
        for locator_parent in locator_parents:
            print(locator_parent)
            if cmds.attributeQuery("loader", node=locator_parent, exists=True):
                placeholder_locators.append(locator_parent)
    return placeholder_locators


def run_after_build(placeholder):
    host = registered_host()
    create_context = CreateContext(host)
    context = context_tools.get_current_context()
    builder = MayaTemplateBuilder(host)
    default_variant = "Main"


    # Create review instance
    if not cmds.objExists(f"review{default_variant}"):
        print("Creating review instance")
        creator_identifier = "io.openpype.creators.maya.review"
        create_context.create(
            creator_identifier=creator_identifier,
            variant=default_variant
        )

    # Activate all animation instances
    print("Activating all animation instances")
    object_sets = cmds.ls(type="objectSet")
    for object_set in object_sets:
        if not cmds.attributeQuery("productType", node=object_set, exists=True) or cmds.getAttr(
                f"{object_set}.productType") != "animation":
            continue

        cmds.setAttr(f"{object_set}.active", True)
        print(f"Successfully activated {object_set}")


    # Add shot camera to review instance
    default_cameras = ["perspShape", "topShape", "frontShape", "sideShape"]

    cameras = cmds.ls(type="camera")
    cameras = [camera for camera in cameras if camera not in default_cameras]
    if cameras:
        print(f"Adding camera {cameras[0]} instance")
        instance_set_name = f"review{default_variant}"
        cmds.sets([cameras[0]], add=instance_set_name)

    else:
        print("No camera found, skipping camera parenting to preview instance")


    # Activate camera instances
    camera_instances = get_instances_of_type("camera")
    for camera_instance in camera_instances:
        cmds.setAttr(f"{camera_instance}.active", True)

    # Change context of existing instances for the layout context
    current_task_name = context["task_name"]

    for instance in get_all_instances():

        if cmds.attributeQuery("task", node=instance, exists=True):
            cmds.setAttr(f"{instance}.task", current_task_name, type="string")
        else:
            print(f"instance node {instance} does not have any attribute named task, skipping context switch")


    # Clean up the mayaScene placeholder after build so as not to 
    # corrupt the scene if we pull from casting for updates
    placeholders = builder.get_placeholders()
    for placeholder in placeholders:
        placeholder_node = placeholder.scene_identifier

        # Only remove the mayascene placeholder
        if not cmds.objExists(placeholder_node) or ("mayaScene" not in placeholder_node):
            continue
        
        members = cmds.sets(placeholder_node, query=True)
        if members:
            print(f"Removing placeholder members {members} of placeholder {placeholder}")
            cmds.delete(members)       # Delete any members
        print(f"Removing placeholder {placeholder}")
        cmds.delete(placeholder_node)  # Cleanup self

    # Remove placeholder locators
    #locators = get_placeholder_locators()
    #for locator in locators:
    #    if "mayaScene" in locator:
    #        cmds.delete(locator)