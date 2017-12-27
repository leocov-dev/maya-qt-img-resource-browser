"""
This is the worker module for finding all the image resources and
building a data representation
"""
import os
import re
import json
import logging
from collections import defaultdict
from .vendor.Qt import QtCore


log = logging.getLogger(__name__)
log.setLevel(logging.CRITICAL)


class QtImgResourceData(object):
    """
    a class to read the resources and build a data structure for them
    this data structure is used by the UI to display the image resources and their information

    the data dictionary is not built on instantiation, you must call ``build_img_dict()`` first

    because the dictionary is not sorted you may want to call the convenience funtion
    ``dict_as_sorted_list()``

    Attributes:
        data_dict (dict): this dictionary holds the information about the image resources

    Class Attributes:
        config_json (str): string path to the configuration json file

    Examples:
        data = QtImgResourceData()
        data.build_img_dict()
        data_list =
    """

    config_json = os.path.join(os.path.dirname(os.path.abspath(__file__)), "config.json")

    def __init__(self):
        self.data_dict = defaultdict(lambda: {"img_path": "",
                                              "img_name": "",
                                              "img_ext": "",
                                              "addl_sizes": []})

        self.config = {"path_exclusions": [],
                       "valid_ext": [
                            ".png",
                            ".svg"]}
        if os.path.exists(self.config_json):
            with open(self.config_json) as config_data:
                self.config = json.load(config_data)
        else:
            log.critical("Could not load the config.json file!")

    def _generator_find_images(self, valid_ext_list=None):
        """
        Iterate over the ":" path, in Qt this is the loaded resources path
        when an item is found that matches the ``valid_ext_list`` it is yielded

        Notes:
            You don't call this directly, use ``build_img_dict``

        Args:
            valid_ext_list (list[str]): a list of valid extension strings, must start with a "." as in ".png".
            this is an optional argument, if no list is provided, the default list is loaded from the configuration file

        Yields:
            str: the next found path string
        """
        if not valid_ext_list:
            valid_ext_list = self.config["valid_ext"]

        if not isinstance(valid_ext_list, list):
            raise ValueError("You must provide a list of valid extensions")

        if not all(x.startswith(".") for x in valid_ext_list):
            raise ValueError("all extensions in valid_ext_list must start with a '.' ")

        it = QtCore.QDirIterator(":", QtCore.QDirIterator.Subdirectories)
        while it.hasNext():
            next_item = it.next()

            if any(next_item.startswith(x) for x in self.config["path_exclusions"]):
                continue

            if any(next_item.endswith(ext) for ext in valid_ext_list):
                yield next_item

    def build_img_dict(self, valid_ext_list=None):
        """
        build the data dict and update the instance variable ``data_dict``
        groups images that have the same name except a number suffix, preceded by an underscore or a dash,
        such as _123 or -45.

        Args:
            valid_ext_list (list[str]): a list of valid extension strings provided to the generator,
            must start with a "." as in ".png".
            this is an optional argument, if no list is provided, the default list is [".png", ".svg"]
        """

        for img_path in self._generator_find_images(valid_ext_list):
            img = os.path.basename(img_path)
            img_name, img_ext = os.path.splitext(img)

            img_sizes = []

            # match ending in -000 or _000
            search_string, __ = os.path.splitext(img_path)
            match_list = re.split("([_-]\d+$)", search_string)
            if len(match_list) > 1:
                img_path = "{}{}".format(match_list[0], img_ext)
                img_name, img_ext = os.path.splitext(os.path.basename(img_path))
                self.data_dict[img_name]["addl_sizes"].append(match_list[1])
                self.data_dict[img_name]["img_path"] = img_path
                self.data_dict[img_name]["img_name"] = img_name
                self.data_dict[img_name]["img_ext"] = img_ext
                img_sizes.append(match_list[1])
            else:
                self.data_dict[img_name]["addl_sizes"].append("")  # if no number suffix, add empty string
                self.data_dict[img_name]["img_path"] = img_path
                self.data_dict[img_name]["img_name"] = img_name
                self.data_dict[img_name]["img_ext"] = img_ext

        log.debug("dict len: {}".format(len(self.data_dict)))
        for key, value in self.data_dict.items():
            log.debug("{}: {}\n"
                      "    {}\n"
                      "    {}\n"
                      "    {}".format(key, value["img_name"], value["img_ext"], value["img_path"], value["addl_sizes"]))

    def dict_as_sorted_list(self, by_path=False, by_name=False):
        """
        format the data as a list sorted by the full path or by the file name

        Notes:
            you must specify only ONE argument

        Args:
            by_path (bool): sort the list by the full path
            by_name (bool) sort the list by the file name

        Returns:
            list: a list sorted by full path or file name
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

        return sorted(self.data_dict.items(), key=lambda (x, y): y[sort_key].lower())
