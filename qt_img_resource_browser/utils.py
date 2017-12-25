"""
utilities module for generic UI actions
"""
from vendor.Qt import QtCore, QtWidgets, QtGui


def make_shelf_icon(icon_path, command_str):
    """
    make an icon on the current shelf
    Args:
        icon_path:
        command_str:
    """
    pass


def progress_bar(msg, num_items, cancelable=False, size=None, font=None, center=True, parent=None):
    """
    a progress bar macro to make a quick progress bar window

    Args:
        msg (str): the string to display above the progress bar
        num_items (int): the total number of items we are counting
        cancelable (bool): if True, will show a button and allow the progress bar to be canceled
        size (QtCore.QSize): set a custom size for the window
        font (QtGui.QFont): set a custom font for the message text
        center (bool): if True, the window will center on the monitor the mouse pointer is currently on
        parent (QtWidgets.QWidget): you can specify a parent, but it is not required for this kind of window
    """
    if not size:
        size = QtCore.QSize(400, 100)

    if not font:
        font = QtGui.QFont()
        font.setBold(True)
        font.setPointSize(16)

    progress = QtWidgets.QProgressDialog(msg, "Cancel", 0, num_items, parent)
    progress.setWindowFlags(QtCore.Qt.WindowStaysOnTopHint | QtCore.Qt.CustomizeWindowHint)
    if not cancelable:
        progress.setCancelButton(None)
    progress.setFont(font)
    progress.setFixedSize(size)
    progress.setMinimumDuration(1000)
    if center:
        center_widget(progress)

    return progress


def center_widget(widget):
    """
    move the given widget to the center of the screen with the mouse pointer currently inside it

    Args:
        widget (QtWidgets.QWidget): the widget we want to center
    """
    # get the dimensions of the widget
    offset_rect = widget.rect()

    # get a point offset from the corner of the widget to the center of the widget
    offset_point = QtCore.QPoint(offset_rect.width()/2, offset_rect.height()/2)

    # get the location of the mouse
    mouse_point = QtWidgets.QApplication.desktop().cursor().pos()

    # get the center point of the screen the mouse is currently in, offset it by the center point of the widget
    widget_new_position = QtWidgets.QApplication.desktop().availableGeometry(mouse_point).center() - offset_point

    # move the widget to the new position
    widget.move(widget_new_position)
