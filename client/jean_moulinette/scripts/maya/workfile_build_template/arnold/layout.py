import ayon_api
from maya import cmds

from ayon_core.pipeline import registered_host
from ayon_core.pipeline.create import CreateContext
from ayon_maya.api.workfile_template_builder import MayaTemplateBuilder
from ayon_core.pipeline.load import (
    get_representation_contexts,
    load_with_repre_context,
)

def get_instances_of_type(instance_type):
    instances = []
    object_sets = cmds.ls(type="objectSet")
    for object_set in object_sets:
        if not cmds.attributeQuery("productType", node=object_set, exists=True) or cmds.getAttr(
                f"{object_set}.productType") != instance_type:
            continue

        instances.append(object_set)
    return instances


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


def run_after_build(placeholder, plugin):
    host = registered_host()
    create_context = CreateContext(host)
    builder = MayaTemplateBuilder(host)

    default_variant = "Main"
    placeholder_data = placeholder.data


    # ANIMATIC LOAD

    if not placeholder_data.get("run_once"):
        print("Loading animatic for the image plane")

        # Load the animatic product for this context into an image plane
        containers = list(host.get_containers())

        # Get the image plane loader
        builder = placeholder.builder
        loader_name = "ImagePlaneLoader"
        loader = builder.get_loaders_by_name()[loader_name]

        # Get the representation that we want to load
        # This is the current context/shot's plate exr representation
        current_folder_id = builder.current_folder_entity["id"]
        product_ids = [product.get("id") for product in list(ayon_api.get_products(
                                                                        builder.project_name,
                                                                        folder_ids=[current_folder_id],
                                                                        product_types=["plate"],
                                                                        fields={"id", "name"}))]

        # Get the last version of the product
        version_ids = set(
            version["id"]
            for version in ayon_api.get_last_versions(
                builder.project_name, product_ids, fields={"id"}
            ).values()
        )

        # Get the frames representations of the plate
        representations = ayon_api.get_representations(
                                        builder.project_name,
                                        representation_names=["frames"],
                                        version_ids=version_ids,
                                    )
        repre_load_contexts = get_representation_contexts(builder.project_name, representations) or {}

        # Formulate options for loading the animatic frames
        # 1001 - clipIn represents how much to offset the imported frames
        # seek_camera allows the builder to import frames onto first non default camera found in the scene
        options = {
            "seek_camera": True,
            "fit_to_resolution_gate": True,
            "offset": 1
        }

        print("Image plane load options:")
        print(options)

        for repre_context in repre_load_contexts.values():
            load_with_repre_context(loader, repre_context, options=options)

        print("Done loading animatic into image plane")


        # Update run_once of placeholder so as to not repeat this logic on rebuilds
        print("Updating placeholder data so as not to rerun")
        placeholder_data_copy = dict(placeholder_data)
        placeholder_data_copy["run_once"] = True
        plugin.update_placeholder(placeholder, placeholder_data_copy)



    # CREATE PRODUCT INSTANCES

    product_types_to_variants = {
        "mayaScene" : "Layout", 
        "camera" : "Main",
        "review" : "Main"
    }

    for product_type, variant in product_types_to_variants.items():
        if cmds.objExists(f"{product_type}{variant}"):      # Don't unnecessarily re-create product instances
            continue
        cmds.select(clear=True)
        instance = create_context.create(
            creator_identifier="io.openpype.creators.maya.{}".format(product_type.lower()),
            variant=variant
        )

    # Add  everything in the scene to the maya scene instance
    cmds.sets("ASSETS",  addElement="mayaSceneLayout")


    # ACTIVATIONS AND PARENTING

    # Disable all animation instances
    animation_instances = get_instances_of_type("animation")
    for animation_instance in animation_instances:
        cmds.setAttr(f"{animation_instance}.active", False)
        print(f"Successfully disabled {animation_instance}")

    # Parent animation instance in mayaScene instance
    maya_scene_instance = None
    maya_scene_instances = get_instances_of_type("mayaScene")
    if maya_scene_instances:
        maya_scene_instance = maya_scene_instances[0]

    if maya_scene_instance:
        cmds.sets(animation_instances, add=maya_scene_instance)
    else:
        print("WARNING: mayaScene instance not found, skipping parenting animation instances")

    # Parent mayaScene instances to avalon container
    avalon_containers = "AVALON_CONTAINERS"
    print("Parenting AVALON_CONTAINERS to mayaScene instance")

    if cmds.objExists(avalon_containers):
        if maya_scene_instance:
            cmds.sets([avalon_containers], add=maya_scene_instance)
        else:
            print("Warning: no maya scene instance found, skipping parenting to mayaScene instance")
    else:
        print("Warning: no AVALON_CONTAINERS found, skipping parenting to mayaScene instance")


    # Parent shot camera in camera instance

    default_cameras = ["perspShape", "topShape", "frontShape", "sideShape"]

    cameras = cmds.ls(type="camera")
    cameras = [camera for camera in cameras if camera not in default_cameras]
    shot_camera = None
    if cameras:
        shot_camera = cameras[0]
    if len(cameras) > 1:
        print(f"WARNING: multiple cameras found for this shot: {cameras}, using {shot_camera}")

    if shot_camera:
        cmds.sets([shot_camera], add=f"camera{default_variant}")
        print(f"Successfully parented {shot_camera} to camera instance")
    else:
        print("WARNING: No shot camera found")

    # Parent camera instance to mayaScene instance
    if maya_scene_instance:
        cmds.sets([f"camera{default_variant}"], add=maya_scene_instance)
    else:
        print("WARNING: No mayaScene instance found, skipping parenting camera instance")


    # Disable camera instance
    cmds.setAttr("camera{}.active".format(default_variant), False)


    # Parent camera to review instance
    if shot_camera:
        cmds.sets([shot_camera], add=f"review{default_variant}")