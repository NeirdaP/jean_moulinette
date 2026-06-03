from maya import cmds
from ayon_core.pipeline import registered_host
from ayon_core.pipeline.create import CreateContext


def run_after_build(placeholder):
    """
    placeholder - ayon_core.pipeline.workfile.workfile_template_builder.PlaceholderItem
    Parameter received from runscript allowing access to ayon context including 
    builder, loaders, etc.
    """

    print("Building modeling workfile")
    host = registered_host()
    create_context = CreateContext(host)

    # create model instance/selection set
    instance = create_context.create(
        creator_identifier="io.openpype.creators.maya.model",
        variant='Main'
    )


    # Remove the script placeholder from the scene after building
    from maya import cmds

    placeholder_node = placeholder.scene_identifier
    members = cmds.sets(placeholder_node, query=True)
    if members:
        cmds.delete(members)       # Delete any members
    cmds.delete(placeholder_node)  # Cleanup self
