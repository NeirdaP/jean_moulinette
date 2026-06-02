from maya import cmds
from ayon_core.pipeline import registered_host
from ayon_core.pipeline.create import CreateContext
from ayon_maya.api.workfile_template_builder import MayaTemplateBuilder


def run_after_build(placeholder):
    """
    placeholder - ayon_core.pipeline.workfile.workfile_template_builder.PlaceholderItem
    Parameter received from runscript allowing access to ayon context including 
    builder, loaders, etc.
    """
    
    print("Building rigging workfile")
    host = registered_host()
    create_context = CreateContext(host)
    builder = MayaTemplateBuilder(host)

    # create empty rig instance
    product_type = "rig"
    variant = "Main"

    cmds.select(clear=True)
    instance = create_context.create(
        creator_identifier=f"io.openpype.creators.maya.{product_type}",
        variant=variant
    )

    # add "rig_root_grp" transform to newly created instance
    cmds.sets("rig_root_grp",  addElement=f"{product_type}{variant}")

    # Finally clean up all placeholders in the scene 
    placeholders = builder.get_placeholders()
    for placeholder in placeholders:

        placeholder_node = placeholder.scene_identifier
        members = cmds.sets(placeholder_node, query=True)
        if members:
            cmds.delete(members)       # Delete any members
        cmds.delete(placeholder_node)  # Cleanup self
