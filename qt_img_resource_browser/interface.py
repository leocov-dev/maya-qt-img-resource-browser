"""
Create a window that shows a list of any image resources that
are available to Qt

Examples:
    load the window with the following command

    interface.load()
"""
import os
import logging
import webbrowser
from functools import partial
from maya.app.general.mayaMixin import MayaQWidgetBaseMixin
from .vendor.Qt import QtCore, QtWidgets, QtGui
from app import QtImgResourceData
from utils import make_shelf_icon


log = logging.getLogger(__name__)
log.setLevel(logging.CRITICAL)


icon_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), "icons")


class QtImgResourceBrowserInterface(MayaQWidgetBaseMixin, QtWidgets.QMainWindow):
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
        self.setWindowIcon(QtGui.QPixmap(os.path.join(icon_path, "lc.png"), parent=self))
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

        # main menu
        self.menu_bar = self.menuBar()

        # utils menu
        self.utils_menu = QtWidgets.QMenu("Utils", self.menu_bar)
        self.menu_bar.addMenu(self.utils_menu)

        self.add_shelf_icon = QtWidgets.QAction("Add Shelf Icon",
                                                self.utils_menu,
                                                triggered=self.add_shelf_icon)
        self.utils_menu.addAction(self.add_shelf_icon)

        # help menu
        self.help_menu = QtWidgets.QMenu("Help", self.menu_bar)
        self.menu_bar.addMenu(self.help_menu)

        self.open_repo_page = QtWidgets.QAction("About",
                                                self.help_menu,
                                                triggered=self.get_about)
        self.help_menu.addAction(self.open_repo_page)

        self.open_issue_page = QtWidgets.QAction("Get Help",
                                                 self.help_menu,
                                                 triggered=self.get_help)
        self.help_menu.addAction(self.open_issue_page)

        # main widget and layout
        self.container = QtWidgets.QWidget(parent=self)
        self.setCentralWidget(self.container)
        self.layout = QtWidgets.QVBoxLayout(self)
        self.layout.setContentsMargins(5, 5, 5, 5)
        self.container.setLayout(self.layout)

        # UI items
        # ------------------------------------------

        # stack
        self.stack = QtWidgets.QStackedLayout(self)
        self.stack.setStackingMode(QtWidgets.QStackedLayout.StackAll)

        # progress bar
        self.progress_container = QtWidgets.QWidget(parent=self)
        self.progress_container.setAttribute(QtCore.Qt.WA_TransparentForMouseEvents)
        self.progress_container.setFixedSize(QtCore.QSize(self.width(), self.width()))
        self.stack.addWidget(self.progress_container)

        progress_layout = QtWidgets.QVBoxLayout(self)
        progress_layout.setContentsMargins(5, 0, 5, 0)
        progress_layout.setSpacing(8)

        progress_spacer = QtWidgets.QSpacerItem(50, 20)
        progress_layout.addItem(progress_spacer)

        self.progress_container.setLayout(progress_layout)
        self.progress = QtWidgets.QProgressBar(self)
        self.progress.setFixedHeight(35)
        self.progress.setFont(self.btn_font)
        progress_layout.addWidget(self.progress)

        progress_label = QtWidgets.QLabel("Updating - Please Wait", parent=self)
        progress_label.setFont(self.bold_font)
        progress_label.setAlignment(QtCore.Qt.AlignCenter)
        progress_label.setFixedHeight(64)
        progress_label.setStyleSheet("""
                                     background-color: qlineargradient(x1: 0,
                                                                       y1: 0,
                                                                       x2: 1,
                                                                       y2: 0,
                                                                       stop: 0.01 rgb(0, 0, 0, 0),
                                                                       stop: 0.2 rgb({0}, {0}, {0}, 255),
                                                                       stop: 0.8  rgb({0}, {0}, {0}, 255),
                                                                       stop: 0.99 rgb(0, 0, 0, 0) );
                                     """.format(42))
        progress_layout.addWidget(progress_label)

        progress_layout.addStretch()

        # scroll area
        self.scroll = ResourceBrowserList(self.data_list, parent=self)
        self.scroll.return_count.connect(self.set_custom_title)
        self.scroll.start_progress.connect(self.init_progress)
        self.scroll.update_progress.connect(self.update_progress)
        self.scroll.end_progress.connect(self.end_progress)
        self.stack.addWidget(self.scroll)

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
        self.le_filter.textChanged.connect(self.update_filtering)
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

    @staticmethod
    def add_shelf_icon():
        """
        add a shelf icon to the current shelf to open the tool window
        """
        make_shelf_icon("QtImgResourceBrowserInterface",
                        os.path.join(icon_path, "qt_img_resource_browser.png"),
                        "import qt_img_resource_browser.interface as interface\ninterface.load()",
                        annotation="Open the Qt Image Resource Browser")

    @staticmethod
    def get_about():
        """
        open the projects github page
        """
        webbrowser.open("https://github.com/leocov-dev/maya-qt-img-resource-browser#maya-qt-image-resource-browser", new=2)

    @staticmethod
    def get_help():
        """
        open the projects github page
        """
        webbrowser.open("https://github.com/leocov-dev/maya-qt-img-resource-browser/issues", new=2)

    def init_progress(self, max_value):
        """
        show and start the progress bar

        Args:
            max_value (int): the maximum value for the progress bar
        """
        self.progress_container.show()
        self.progress.setMaximum(max_value)

    def update_progress(self, value):
        """
        update the progress bar's value

        Args:
            value (int): the current value for the progress bar
        """
        self.progress.setValue(value)

    def end_progress(self):
        """
        reset and hide the progress bar
        """
        self.progress.reset()
        self.progress_container.hide()

    def update_filtering(self):
        """
        update the list's filtering
        """
        self.scroll.filter_widgets(self.le_filter.text())

    def set_custom_title(self, num):
        """
        set a window title with the number of items in the list
        Args:
            num (int): number of items in the list
        """
        self.setWindowTitle("Qt Image Resource Browser - {}".format(num))

    def closeEvent(self, event):
        """
        when closing the window, also explicitly close the scroll area so that its own closeEvent will trigger
        """
        # Save window's geometry
        self.win_settings.setValue("windowGeometry", self.saveGeometry())

        # clean up the scroll area and all its children
        self.scroll.close()

        event.accept()

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

            QtCore.QTimer.singleShot(50, _win.scroll.initialize_widget_list)


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

    copy_text = QtCore.Signal(str)

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
        self.px_image = QtGui.QPixmap(self.img_path, parent=self)

        # image's natural size
        self.img_size = self.px_image.size()

        px_preview = self.px_image
        # scale to fit in widget
        if self.px_image.height() > self.max_height:
            px_preview = self.px_image.scaledToHeight(self.max_height, QtCore.Qt.SmoothTransformation)
        if self.px_image.width() > self.max_height:
            px_preview = self.px_image.scaledToWidth(self.max_height, QtCore.Qt.SmoothTransformation)

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
        self.ly_ops.setContentsMargins(0, 8, 5, 15)
        self.layout.addLayout(self.ly_ops)

        # informational text
        self.ly_info = QtWidgets.QHBoxLayout(self)
        self.ly_info.setContentsMargins(0, 0, 0, 0)
        self.ly_ops.addLayout(self.ly_info)

        # name label
        name_font = QtGui.QFont()
        name_font.setPointSize(8)
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
        self.lbl_size = QtWidgets.QLabel("w: {} h: {}".format(self.img_size.width(), self.img_size.height()),
                                         parent=self)
        self.ly_info.addWidget(self.lbl_size)

        # layout clip path string
        self.ly_clip = QtWidgets.QHBoxLayout(self)
        self.ly_clip.setContentsMargins(0, 0, 0, 0)
        self.ly_ops.addLayout(self.ly_clip)

        # clip-able path text
        self.le_string = QtWidgets.QLineEdit('"{}"'.format(self.img_path), parent=self)
        self.le_string.setFixedHeight(25)
        self.le_string.setReadOnly(True)
        self.ly_clip.addWidget(self.le_string)

        # copy to clipboard
        px_copy = QtGui.QPixmap(":/skinWeightCopy.png", parent=self)
        self.btn_clip = QtWidgets.QPushButton(parent=self)
        self.btn_clip.setFixedSize(QtCore.QSize(23, 23))
        self.btn_clip.setIcon(px_copy)
        self.btn_clip.setIconSize(QtCore.QSize(20, 20))
        self.btn_clip.clicked.connect(self.emit_path)
        self.ly_clip.addWidget(self.btn_clip)

        # save icon
        px_save = QtGui.QPixmap(":/fileSave.png", parent=self)
        self.btn_save = QtWidgets.QPushButton(parent=self)
        self.btn_save.setFixedSize(QtCore.QSize(23, 23))
        self.btn_save.setIcon(px_save)
        self.btn_save.setIconSize(QtCore.QSize(20, 20))
        self.btn_save.clicked.connect(self.save_image)
        self.ly_clip.addWidget(self.btn_save)

    def emit_path(self):
        """
        emit path string
        """
        self.copy_text.emit(self.le_string.text())

    def save_image(self):
        """
        save the image
        """
        save_path, __ = QtWidgets.QFileDialog.getSaveFileName(parent=self,
                                                              caption="Save Image Resource - {}".format(self.img_name),
                                                              filter="Images (*.png)")
        if save_path:
            self.px_image.save(save_path, quality=100)


class ResourceBrowserList(QtWidgets.QScrollArea):
    """
    a scroll area containing a list of qt image resources
    Args:
        data_list (list): a list of image resource tuples, a name and a dictionary of data
        parent (QtWidgets.QWidget): the parent for this object, it is not required but should always have one
    """

    clipboard = QtWidgets.QApplication.clipboard()

    return_count = QtCore.Signal(int)
    start_progress = QtCore.Signal(int)
    update_progress = QtCore.Signal(int)
    end_progress = QtCore.Signal()

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

    def copy_to_clipboard(self, string):
        """
        copy the string to the system clipboard
        Args:
            string: a string
        """
        self.clipboard.setText(string)

    def filter_widgets(self, filter_string):
        """
        filter the list of displayed widgets who's names contain the given ``filter_string``.

        Args:
            filter_string (str): search image names for this string
        """
        # might seem easier to hide and show widgets based on the filter, but show() is very, very slow

        new_filtered_list = []
        for item in self.widget_list:
            if filter_string and filter_string.lower() not in item.img_name.lower():
                continue
            new_filtered_list.append(item)

        if new_filtered_list == self.filtered_widget_list:
            return

        # update the filtered list
        self.filtered_widget_list = new_filtered_list

        num = len(self.filtered_widget_list)
        if num > 200:
            self.start_progress.emit(num)

        # remove all items from scroll
        for i in reversed(range(self.layout.count())):
            self.layout.removeItem(self.layout.itemAt(i))

        # add filtered items to layout
        for i, item in enumerate(self.filtered_widget_list):
            self.layout.addWidget(item)
            self.update_progress.emit(i)

        # emit the number of items to update the window title bar
        self.return_count.emit(len(self.filtered_widget_list))

        self.update_container_size()

        self.end_progress.emit()

    def add_resource_item(self, img_path, img_name, img_ext, addl_sizes):
        """
        add a new resource item to the scroll area
        Args:
            img_path (str): the full path to the image
            img_name (str): the name of the image only
            img_ext (str): the file extension for this image
            addl_sizes (list[str]): a list of additional size suffixes

        Returns:
            ResourceBrowserItem: the item just added
        """
        item_widget = ResourceBrowserItem(img_path, img_name, img_ext, addl_sizes, parent=self)
        item_widget.copy_text.connect(self.copy_to_clipboard)
        self.widget_list.append(item_widget)

        return item_widget

    def initialize_widget_list(self):
        """
        initialize the entire widget list
        """
        if not self.data_list:
            return

        self.start_progress.emit(len(self.data_list))

        for i, list_item in enumerate(self.data_list):
            name, data = list_item
            img_path = data["img_path"]
            img_name = data["img_name"]
            img_ext = data["img_ext"]
            addl_sizes = data["addl_sizes"]
            self.add_resource_item(img_path, img_name, img_ext, addl_sizes)
            self.update_progress.emit(i)

        self.end_progress.emit()

        self.filter_widgets("")

    def update_container_size(self):

        num_widgets = len(self.filtered_widget_list)

        new_height = num_widgets * ResourceBrowserItem.max_height
        new_height += (num_widgets - 1) * self.layout.spacing()
        self.container.setFixedHeight(new_height)

        parent_width = self.parent().width()
        # parent_margins = self.parent().centralWidget().layout.contentsMargins()
        scroll_bar_width = 26
        self.container.setFixedWidth(parent_width - scroll_bar_width)

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

        event.accept()


def load():
    """
    entry point for the UI, launch an instance of the tool with this method
    """
    QtImgResourceBrowserInterface.show_window()
