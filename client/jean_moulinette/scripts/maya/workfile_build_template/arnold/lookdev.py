from ayon_core.pipeline import registered_host
from ayon_core.pipeline.create import CreateContext
from ayon_maya.api.workfile_template_builder import MayaTemplateBuilder
from ayon_maya.api.lib import get_container_transforms, get_node_parent
from maya import cmds

def run_after_build(placeholder):
    """
    placeholder - ayon_core.pipeline.workfile.workfile_template_builder.PlaceholderItem
    Parameter received from runscript allowing access to ayon context including 
    builder, loaders, etc.
    """
    
    print("Building lookdev workfile")
    host = registered_host()
    containers = list(host.get_containers())
    create_context = CreateContext(host)
    builder = MayaTemplateBuilder(host)

    product_types = ["look", "lookanim" , "proxygpu", "actorbase" ]
    variant="Main"
    for product_type in product_types:
        instance = create_context.create(
            creator_identifier="io.openpype.creators.maya.{}".format(product_type),
            variant=variant
        )

        # Move loaded containers into the created instances
        instance_set_name = f"{product_type}{variant}"

        for container in containers:
            container_transforms = get_container_transforms(container, root=True)
            root_group = get_node_parent(container_transforms)
            cmds.sets(root_group, addElement=instance_set_name)

    # Finally clean up all placeholders in the scene 
    placeholders = builder.get_placeholders()
    for placeholder in placeholders:

        placeholder_node = placeholder.scene_identifier
        members = cmds.sets(placeholder_node, query=True)
        if members:
            cmds.delete(members)       # Delete any members
        cmds.delete(placeholder_node)  # Cleanup self
