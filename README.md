# Maya Qt Image Resource Browser

## WIP
This project is still in progress

## Description

This python tool for Maya will let you browse all the image resources Maya has already loaded from QResource bundles.

These internal resources make it easy to add images to buttons and other UI elements without authoring anything.

There is the added benefit of having your application look native to Maya and use images users are already familiar with.

This is an example of using a built in Maya icon as a QPixmap in your code:

    px_open = QtGui.QPixmap(":/fileOpen.png")
    
## Installation and Use
* Place the entire directory qt_img_resource_browser in your Maya scripts directory or a directory that Maya can load Python scripts from.
* Restart Maya.
* Launch the window with this python command:


    xxxxxxxxx
    
## Screenshot