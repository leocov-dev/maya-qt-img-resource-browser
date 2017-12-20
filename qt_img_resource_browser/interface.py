from maya.app.general.mayaMixin import MayaQWidgetBaseMixin
from vendor.Qt import QtCore, QtWidgets, QtGui
from app import QtImgResourceBrowser
from utils import progress_bar

try:
    from PySide2 import QtCore, QtWidgets, QtGui
except:
    pass


class QtImgResourceBrowserInterface(MayaQWidgetBaseMixin, QtWidgets.QWidget):
    """
    Qt UI class to display the tool window
    """

    def __init__(self, parent=None):
        super(QtImgResourceBrowserInterface, self).__init__(parent=parent)

        # setup window
        self.setMinimumHeight(400)
        self.setFixedWidth(500)
        self.setWindowTitle("Qt Image Resource Browser")

        # instance vars
        self.app = QtImgResourceBrowser()
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

        # A filtering bar
        filter_bar_height = 28

        self.lyt_filter = QtWidgets.QHBoxLayout(self)
        self.lyt_filter.setContentsMargins(0, 0, 0, 0)
        self.layout.addLayout(self.lyt_filter)

        self.lbl_filter = QtWidgets.QLabel("Filter:", parent=self)
        self.lbl_filter.setFont(self.bold_font)
        self.lyt_filter.addWidget(self.lbl_filter)

        self.le_filter = QtWidgets.QLineEdit(parent=self)
        self.le_filter.setFixedHeight(filter_bar_height)
        self.lyt_filter.addWidget(self.le_filter)

        self.btn_filter_clear = QtWidgets.QPushButton("Clear", self)
        self.btn_filter_clear.setFixedSize(QtCore.QSize(80, filter_bar_height))
        self.btn_filter_clear.setFont(self.btn_font)
        self.lyt_filter.addWidget(self.btn_filter_clear)

        # a scrolling list of items
        self.scroll = ResourceBrowserList(self.data_list, parent=self)
        self.layout.addWidget(self.scroll)

        self.scroll.populate_list()

    def closeEvent(self, event):
        """
        what to do on closing the ui
        :param event:
        :return:
        """
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
    """

    def __init__(self, img_path, img_name, img_ext, parent=None):
        super(ResourceBrowserItem, self).__init__(parent=parent)

        self.max_height = 64
        self.img_path = img_path
        self.img_name = img_name
        self.img_ext = img_ext

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

        # preview pixmap
        self.img_preview = QtGui.QPixmap(self.img_path, parent=self)
        self.img_size = self.img_preview.size()

        # scale to fit in widget
        if self.img_preview.height() > self.max_height:
            self.img_preview = self.img_preview.scaledToHeight(self.max_height, QtCore.Qt.SmoothTransformation)
        elif self.img_preview.width() > self.max_height:
            self.img_preview = self.img_preview.scaledToWidth(self.max_height, QtCore.Qt.SmoothTransformation)

        # preview widget
        self.lbl_preview = QtWidgets.QLabel(parent=self)
        self.lbl_preview.setFixedSize(QtCore.QSize(self.max_height, self.max_height))
        self.lbl_preview.setPixmap(self.img_preview)
        self.lbl_preview.setAlignment(QtCore.Qt.AlignCenter)
        self.layout.addWidget(self.lbl_preview)

        # informational text
        self.ly_info = QtWidgets.QVBoxLayout(self)
        self.ly_info.setContentsMargins(0, 0, 0, 0)
        self.layout.addLayout(self.ly_info)

        self.lbl_name = QtWidgets.QLabel(self.img_name, parent=self)
        self.layout.addWidget(self.lbl_name)


class ResourceBrowserList(QtWidgets.QScrollArea):
    """
    a scroll area containing a list of qt image resources
    """

    def __init__(self, data_list, parent=None):
        """
        :param data_list:
            a list of image resource tuples, a name and a dictionary of data
        :param parent:
        """
        super(ResourceBrowserList, self).__init__(parent=parent)

        # instance vars
        self.data_list = data_list
        self.widget_list = []

        # scroll area policies
        self.setSizePolicy(QtWidgets.QSizePolicy.MinimumExpanding, QtWidgets.QSizePolicy.MinimumExpanding)
        self.setVerticalScrollBarPolicy(QtCore.Qt.ScrollBarAlwaysOn)
        self.setHorizontalScrollBarPolicy(QtCore.Qt.ScrollBarAlwaysOff)
        self.setMinimumHeight(175)

        # container widget to hold things in the scroll area
        self.container = QtWidgets.QWidget(parent=self)
        self.setWidgetResizable(True)
        self.container.setSizePolicy(QtWidgets.QSizePolicy.MinimumExpanding, QtWidgets.QSizePolicy.MinimumExpanding)
        self.container.setAttribute(QtCore.Qt.WA_StyledBackground, True)
        self.container.setObjectName("Container")
        self.container.setStyleSheet("""
                                     #Container{
                                        background-color: rgb(64, 128, 64);
                                     }
                                     """)

        # layout for child widgets
        self.layout = QtWidgets.QVBoxLayout(self)
        self.layout.setContentsMargins(0, 0, 0, 0)
        self.container.setLayout(self.layout)

        # add the container to the scroll
        self.setWidget(self.container)

    def add_resource_item(self, img_path, img_name, img_ext):
        """
        add a new resource item to the scroll area
        :param img_path:
        :param img_name:
        :param img_ext:
        :return:
        """
        item_widget = ResourceBrowserItem(img_path, img_name, img_ext, parent=self)
        self.layout.addWidget(item_widget)
        self.widget_list.append(item_widget)

    def populate_list(self):
        """
        populate the entire list
        :return:
        """
        if not self.data_list:
            return

        # populate list
        num = len(self.data_list)
        progress = progress_bar("Loading Images", num)

        for i, list_item in enumerate(self.data_list):
            name, data = list_item
            progress.setValue(i)
            img_path = data["img_path"]
            img_name = data["img_name"]
            img_ext = data["img_ext"]
            self.add_resource_item(img_path, img_name, img_ext)
        # add a spacer
        self.layout.addStretch()

        progress.setValue(num)

    def closeEvent(self, event):
        """
        what to do on closing this widget
        :param event:
        :return:
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
    :return:
    """
    QtImgResourceBrowserInterface.show_window()
