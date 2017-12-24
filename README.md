# Maya Qt Image Resource Browser

## Description

This Python tool for Maya will let you browse all the image resources Maya has already loaded from QResource bundles.

These internal resources make it easy to add images to buttons and other UI elements without authoring anything.

There is the added benefit of having your application look native to Maya and use images users are already familiar with.

This is an example of using a built in Maya icon as a QPixmap in your code:

    px_open = QtGui.QPixmap(":/fileOpen.png")
    
## Installation and Use
I've tested this tool with Maya 2016 and Maya 2018. It uses the Qt.py shim to enable compatibility with PySide or PySide2.

1. Place the entire directory qt_img_resource_browser in your Maya scripts directory or a directory that Maya can load Python scripts from.
2. Restart Maya.
3. Launch the window with this python command:


    # Python
    import qt_img_resource_browser.interface as interface
    interface.load()
    
By Default some paths are excluded from the list. You can edit the ``config.json`` file to modify these exclusions.
    
## Screenshot
![Window Screenshot](https://github.com/leocov-dev/maya-qt-img-resource-browser/tree/master/qt_img_resource_browser/screenshots/capture_01.png)

## Known Issues

For some reason on Maya 2018 the QProgressDialog is not rendering as expected.