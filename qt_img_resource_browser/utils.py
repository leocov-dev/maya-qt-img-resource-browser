"""
utilities module for generic UI actions
"""
import os
import platform
import pymel.core as pm


def make_shelf_icon(name, icon_path, command_str, source_type="python", annotation=None):
    """
    make an icon on the current shelf
    Args:
        name (str): the string name for this shelf item
        icon_path (str): the path to the image to use for the shelf item
        command_str (str): the command to run when pressing this shelf item
        source_type (str): the type of command, mel or python
        annotation (str): the tool-tip annotation to display on hovering over this shelf item

    Returns:
        pm.uitypes.ShelfButton: returns the button just created
    """
    icon_path = os.path.normpath(icon_path)

    # Maya requires all paths to be forward slash for internal use
    if platform.system().startswith("Win"):
        icon_path = icon_path.replace("\\", "/")

    try:
        current_shelf = pm.uitypes.ShelfLayout(pm.mel.eval('tabLayout -q -st $gShelfTopLevel;'))

        for item in [x for x in current_shelf.getChildren() if isinstance(x, pm.uitypes.ShelfButton)]:
            if name == item.getLabel():
                item.delete()

        # you must set the active parent before creating shelf buttons or they will be parented under maya's main window
        pm.setParent(current_shelf)

        shelf_button = pm.shelfButton(label=name)
        shelf_button.setSourceType(source_type)
        shelf_button.setCommand(command_str)
        shelf_button.setImage(icon_path)
        if annotation:
            shelf_button.setAnnotation(annotation)

        return shelf_button

    except Exception as e:
        pm.warning("Something went wrong making the shelf item: {}\n Exception Msg: {}".format(name, e.message))
