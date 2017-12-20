from vendor.Qt import QtCore, QtWidgets, QtGui

try:
    from PySide2 import QtCore, QtWidgets, QtGui
except:
    pass

def progress_bar(msg, num_items, cancelable=False, size=None, font=None, center=True, parent=None):
    """
    a progress bar macro to make a quick progress bar window
    :param msg:
    :param num_items:
    :param cancelable:
    :param size:
    :param font:
    :param center:
    :param parent:
    :return:
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
    progress.forceShow()
    if center:
        center_widget(progress)

    return progress


def center_widget(widget):
    """
    move the given widget to the center of the screen with the mouse pointer currently inside it
    :param widget:
    :return:
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
