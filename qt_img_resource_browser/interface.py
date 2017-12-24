"""
Create a window that shows a list of any image resources that
are available to Qt

Examples:
    load the window with the following command

    interface.load()
"""
import os
import logging
from functools import partial
from maya.app.general.mayaMixin import MayaQWidgetBaseMixin
from vendor.Qt import QtCore, QtWidgets, QtGui
from app import QtImgResourceData
from utils import progress_bar


log = logging.getLogger(__name__)
log.setLevel(logging.CRITICAL)


icon_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), "icons")


class QtImgResourceBrowserInterface(MayaQWidgetBaseMixin, QtWidgets.QWidget):
    """
    Qt UI class to display the tool window
    Args:
        parent (QtWidgets.QWidget): the parent for this window, since we are subclassing MayaQWidgetBaseMixin this
            is not required
    """

    def __init__(self, parent=None):
        super(QtImgResourceBrowserInterface, self).__init__(parent=parent)

        # setup window
        self.setMinimumHeight(400)
        self.setFixedWidth(500)
        self.setWindowTitle("Qt Image Resource Browser")
        self.setAttribute(QtCore.Qt.WA_DeleteOnClose)

        # ini file to store window settings
        self.win_settings = QtCore.QSettings("leocov", "QtImgResourceBrowserInterface")

        # instance vars
        self.app = QtImgResourceData()
        self.app.build_img_dict()
        self.data_list = self.app.dict_as_sorted_list(by_path=True)

        # fonts
        self.bold_font = QtGui.QFont()
        self.bold_font.setBold(True)
        self.bold_font.setPointSize(10)

        self.btn_font = QtGui.QFont()
        self.btn_font.setBold(True)
        self.btn_font.setPointSize(9)

        # UI items
        self.layout = QtWidgets.QVBoxLayout(self)
        self.setContentsMargins(5, 5, 5, 5)
        self.setLayout(self.layout)
        self.scroll = ResourceBrowserList(self.data_list, parent=self)

        # A filtering bar
        filter_bar_height = 28

        self.lyt_filter = QtWidgets.QHBoxLayout(self)
        self.lyt_filter.setContentsMargins(0, 0, 0, 0)
        self.layout.addLayout(self.lyt_filter)

        self.lbl_filter = QtWidgets.QLabel("Search:", parent=self)
        self.lbl_filter.setFont(self.bold_font)
        self.lyt_filter.addWidget(self.lbl_filter)

        self.le_filter = QtWidgets.QLineEdit(parent=self)
        self.le_filter.setFixedHeight(filter_bar_height)
        self.le_filter.editingFinished.connect(partial(self.scroll.filter_widgets, self.le_filter.text()))
        self.lyt_filter.addWidget(self.le_filter)

        self.btn_filter_clear = QtWidgets.QPushButton("Clear", self)
        self.btn_filter_clear.setFixedSize(QtCore.QSize(80, filter_bar_height))
        self.btn_filter_clear.setFont(self.btn_font)
        self.btn_filter_clear.clicked.connect(partial(self.le_filter.setText, ""))
        self.btn_filter_clear.clicked.connect(partial(self.scroll.filter_widgets, ""))
        self.lyt_filter.addWidget(self.btn_filter_clear)

        # add scroll to layout
        self.layout.addWidget(self.scroll)

        # Restore window's previous geometry
        self.restoreGeometry(self.win_settings.value("windowGeometry"))

    def closeEvent(self, event):
        """
        when closing the window, also explicitly close the scroll area so that its own closeEvent will trigger
        """
        # Save window's geometry
        self.win_settings.setValue("windowGeometry", self.saveGeometry())

        # clean up the scroll area and all its children
        self.scroll.close()

    @staticmethod
    def show_window():
        """
        Static method for creating the UI window and closing an existing instance
        """
        global _win
        try:
            _win.close()
        except:
            pass
        finally:
            _win = QtImgResourceBrowserInterface()
            _win.setWindowFlags(QtCore.Qt.Window)
            _win.show()


class ResourceBrowserItem(QtWidgets.QWidget):
    """
    a single image resource item widget
    Args:
        img_path (str): the full path to the image
        img_name (str): the name of the image only
        img_ext (str): the file extension for this image
        addl_sizes (list[str]): a list of suffixes for alternate image sizes
        parent (QtWidgets.QWidget): The parent for this item, not required but should always have one

    Class Attributes:
        max_height (int): the maximum height for this class of widget
    """

    max_height = 64

    def __init__(self, img_path, img_name, img_ext, addl_sizes, parent=None):
        super(ResourceBrowserItem, self).__init__(parent=parent)

        # instance vars
        self.img_path = img_path
        self.img_name = img_name
        self.img_ext = img_ext
        self.addl_sizes = addl_sizes

        # self style
        self.setAttribute(QtCore.Qt.WA_DeleteOnClose)
        self.setFixedHeight(self.max_height)
        self.setSizePolicy(QtWidgets.QSizePolicy.MinimumExpanding, QtWidgets.QSizePolicy.MinimumExpanding)
        self.setAttribute(QtCore.Qt.WA_StyledBackground, True)
        self.setObjectName("BrowserItem")
        self.setStyleSheet("""
                           #BrowserItem{
                              background-color: rgb(64, 64, 64);
                           }
                           """)

        # main layout
        self.layout = QtWidgets.QHBoxLayout(self)
        self.layout.setContentsMargins(0, 0, 0, 0)
        self.setLayout(self.layout)

        # checker/solid label
        px_checker = QtGui.QPixmap(os.path.join(icon_path, "checker.png"), parent=self)

        # preview pixmap
        px_preview = QtGui.QPixmap(self.img_path, parent=self)

        # image's natural size
        self.img_size = px_preview.size()

        # scale to fit in widget
        if px_preview.height() > self.max_height:
            px_preview = px_preview.scaledToHeight(self.max_height, QtCore.Qt.SmoothTransformation)
        if px_preview.width() > self.max_height:
            px_preview = px_preview.scaledToWidth(self.max_height, QtCore.Qt.SmoothTransformation)

        # combine pixmaps with a painter
        painter = QtGui.QPainter()
        painter.begin(px_checker)
        painter.drawPixmap((px_checker.width()-px_preview.width())/2,
                           (px_checker.height()-px_preview.height())/2,
                           px_preview)
        painter.end()

        self.lbl_combined = QtWidgets.QLabel(parent=self)
        self.lbl_combined.setPixmap(px_checker)

        self.layout.addWidget(self.lbl_combined)

        # ops layout
        self.ly_ops = QtWidgets.QVBoxLayout(self)
        self.ly_ops.setContentsMargins(0, 5, 5, 5)
        self.layout.addLayout(self.ly_ops)

        # informational text
        self.ly_info = QtWidgets.QHBoxLayout(self)
        self.ly_info.setContentsMargins(0, 0, 0, 0)
        self.ly_ops.addLayout(self.ly_info)

        # name label
        name_font = QtGui.QFont()
        name_font.setPointSize(7)
        name_font.setBold(True)
        self.lbl_name = QtWidgets.QLabel(self.img_name, parent=self)
        self.lbl_name.setFont(name_font)
        self.ly_info.addWidget(self.lbl_name)

        # stretch
        self.ly_info.insertStretch(1)

        # ext label
        self.lbl_ext = QtWidgets.QLabel("ext: {}  |".format(self.img_ext), parent=self)
        self.ly_info.addWidget(self.lbl_ext)

        # size label
        self.lbl_size = QtWidgets.QLabel("w: {} h: {} ".format(self.img_size.width(), self.img_size.height()),
                                         parent=self)
        self.ly_info.addWidget(self.lbl_size)

        # layout clip path string
        self.ly_clip = QtWidgets.QHBoxLayout(self)
        self.ly_clip.setContentsMargins(0, 0, 0, 0)
        self.ly_ops.addLayout(self.ly_clip)

        # clip-able path text
        self.le_string = QtWidgets.QLineEdit(self.img_path, parent=self)
        self.le_string.setReadOnly(True)
        self.ly_clip.addWidget(self.le_string)

        # additional sizes dropdown
        # todo: is this useful? or should these alt sizes be used only for dpi changes?
        # if len(self.addl_sizes) > 1:
        #     self.cb_size = QtWidgets.QComboBox(parent=self)
        #     self.cb_size.setFixedWidth(80)
        #     self.cb_size.addItems(sorted(self.addl_sizes))
        #     self.ly_clip.addWidget(self.cb_size)


class ResourceBrowserList(QtWidgets.QScrollArea):
    """
    a scroll area containing a list of qt image resources
    Args:
        data_list (list): a list of image resource tuples, a name and a dictionary of data
        parent (QtWidgets.QWidget): the parent for this object, it is not required but should always have one
    """

    def __init__(self, data_list, parent=None):
        super(ResourceBrowserList, self).__init__(parent=parent)

        # instance vars
        self.data_list = data_list
        self.widget_list = []
        self.filtered_widget_list = []

        # scroll area policies
        self.setSizePolicy(QtWidgets.QSizePolicy.MinimumExpanding, QtWidgets.QSizePolicy.MinimumExpanding)
        self.setVerticalScrollBarPolicy(QtCore.Qt.ScrollBarAlwaysOn)
        self.setHorizontalScrollBarPolicy(QtCore.Qt.ScrollBarAlwaysOff)
        self.setMinimumSize(QtCore.QSize(300, 300))

        # container widget to hold things in the scroll area
        self.container = QtWidgets.QWidget(parent=self)
        self.container.setSizePolicy(QtWidgets.QSizePolicy.MinimumExpanding, QtWidgets.QSizePolicy.MinimumExpanding)
        self.container.setAttribute(QtCore.Qt.WA_StyledBackground, True)
        self.container.setObjectName("Container")
        self.container.setStyleSheet("""
                                     #Container{
                                        background-color: rgb(54, 54, 54);
                                     }
                                     """)

        # layout for child widgets
        self.layout = QtWidgets.QVBoxLayout(self)
        self.layout.setContentsMargins(0, 0, 0, 0)
        self.layout.setSpacing(5)
        self.container.setLayout(self.layout)

        # add the container to the scroll
        self.setWidget(self.container)

        # initialize the widgets
        self.initialize_widget_list()

    def filter_widgets(self, filter_string):
        """
        filter the list of displayed widgets who's names contain the given ``filter_string``.

        Args:
            filter_string (str): search image names for this string
        """

        self.filtered_widget_list = []

        for item in self.widget_list:
            if filter_string and filter_string.lower() not in item.img_name.lower():
                item.hide()
                continue

            self.filtered_widget_list.append(item)
            item.show()

        self.update_container_size()

    def add_resource_item(self, img_path, img_name, img_ext, addl_sizes):
        """
        add a new resource item to the scroll area
        Args:
            img_path (str): the full path to the image
            img_name (str): the name of the image only
            img_ext (str): the file extension for this image
            addl_sizes (list[str]): a list of additional size suffixes
        """
        item_widget = ResourceBrowserItem(img_path, img_name, img_ext, addl_sizes, parent=self)
        self.layout.addWidget(item_widget)
        self.widget_list.append(item_widget)

    def initialize_widget_list(self):
        """
        initialize the entire widget list
        """
        if not self.data_list:
            return

        num = len(self.data_list)

        log.debug("initializing num: {}".format(num))

        progress = progress_bar("Loading Images", num)

        for i, list_item in enumerate(self.data_list):
            name, data = list_item
            img_path = data["img_path"]
            img_name = data["img_name"]
            img_ext = data["img_ext"]
            addl_sizes = data["addl_sizes"]
            self.add_resource_item(img_path, img_name, img_ext, addl_sizes)
            progress.setValue(i)

        progress.reset()

        self.filter_widgets("")

    def update_container_size(self):

        num_widgets = len(self.filtered_widget_list)

        new_height = num_widgets * ResourceBrowserItem.max_height
        new_height += (num_widgets - 1) * self.layout.spacing()
        self.container.setFixedHeight(new_height)

        parent_width = self.parent().width()
        parent_margins = self.parent().layout.contentsMargins()
        scroll_bar_width = 26
        self.container.setFixedWidth(parent_width - parent_margins.right() - parent_margins.left() - scroll_bar_width)

        log.debug("Update Size")

    def closeEvent(self, event):
        """
        close all child widgets explicitly on closing this widget
        Args:
            event: the event object
        """
        # clean up any child widgets
        for item in self.widget_list:
            try:
                item.close()
            except:
                pass


def load():
    """
    entry point for the UI, launch an instance of the tool with this method
    """
    QtImgResourceBrowserInterface.show_window()
