import os
from vendor.Qt import QtCore


class QtImgResourceBrowser(object):
    """
    a class to read the resources and build a data structure for them
    this data structure is used by the UI to display the image resources and their information
    """

    def __init__(self):
        self.data_dict = {}

    @staticmethod
    def generator_find_images(valid_ext_list=None):
        """
        search the resource path for any resources
        :param valid_ext_list:
        :return:
        """
        if not valid_ext_list:
            valid_ext_list = [".png", ".svg"]

        it = QtCore.QDirIterator(":", QtCore.QDirIterator.Subdirectories)
        while it.hasNext():
            next_item = it.next()
            if any(next_item.endswith(ext) for ext in valid_ext_list):
                yield next_item

    def build_img_dict(self, valid_ext_list=None):
        """
        build the data dict
        :return:
        """

        for img_path in self.generator_find_images(valid_ext_list):
            img = os.path.basename(img_path)
            img_name, img_ext = os.path.splitext(img)

            data_item = {"img_path": img_path,
                         "img_name": img_name,
                         "img_ext": img_ext}

            self.data_dict[img_name] = data_item

    def dict_as_sorted_list(self, by_path=False, by_name=False):
        """
        return the data dict as a sorted list
        :return:
        """
        if not any([by_path, by_name]):
            raise ValueError("You must supply ONE argument")

        if all([by_path, by_name]):
            raise ValueError("You many supply ONLY ONE argument")

        sort_key = None
        if by_path:
            sort_key = "img_path"
        if by_name:
            sort_key = "img_name"

        if not sort_key:
            raise RuntimeError("How did we even get here!")

        return sorted(self.data_dict.items(), key=lambda (x, y): y[sort_key])
