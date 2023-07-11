"""
    This program is free software: you can redistribute it and/or modify
    it under the terms of the GNU General Public License as published by
    the Free Software Foundation, either version 3 of the License, or
    (at your option) any later version.

    This program is distributed in the hope that it will be useful,
    but WITHOUT ANY WARRANTY; without even the implied warranty of
    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
    GNU General Public License for more details.

    You should have received a copy of the GNU General Public License
    along with this program.  If not, see <https://www.gnu.org/licenses/>.
"""
import configparser
import os
import shutil
import glob
import struct

split_str = "----------------------------------------------------------------------------------------------------------"
global_config = configparser.ConfigParser()
global_config.read("Configs/global_config.ini", "utf-8")
config_folder = global_config["Global"]["config_folder"]

preset_config = configparser.ConfigParser()
preset_config.read(config_folder + "/preset.ini", "utf-8")

tmp_config = configparser.ConfigParser()
tmp_config.read(config_folder + '/tmp.ini', 'utf-8')

vertex_attr_ini = preset_config["Merge"]["vertex_attr_ini"]
vertex_config = configparser.ConfigParser()
vertex_config.read(config_folder + "/" + vertex_attr_ini, "utf-8")

# -----------------------------------------------------------
# --General--
Engine = preset_config["General"]["Engine"]
DeleteOutputFolder = preset_config["General"].getboolean("DeleteOutputFolder")
FrameAnalyseFolder = preset_config["General"]["FrameAnalyseFolder"]
LoaderFolder = preset_config["General"]["LoaderFolder"]
OutputFolder = preset_config["General"]["OutputFolder"]
mod_name = preset_config["General"]["mod_name"]
Author = preset_config["General"]["Author"]

# --Merge--
root_vs = preset_config["Merge"]["root_vs"]
draw_ib = preset_config["Merge"]["draw_ib"]
part_name = preset_config["Merge"]["part_name"]
auto_element_list = preset_config["Merge"].getboolean("auto_element_list")
auto_completion_blendweights = preset_config["Merge"].getboolean("auto_completion_blendweights")

# --Split--
repair_tangent = preset_config["Split"]["repair_tangent"]

# combine a WorkFolder
WorkFolder = LoaderFolder + FrameAnalyseFolder + "/"
element_list = preset_config["Merge"]["element_list"].split(",")


# --Basic Functions--
def get_filter_filenames(in_str, end_str,target_folder=WorkFolder):
    filtered_filenames = []
    filenames = os.listdir(target_folder)
    for filename in filenames:
        if in_str in filename and filename.endswith(end_str):
            filtered_filenames.append(filename)
    return filtered_filenames


def get_attribute_from_txtfile(filename, attribute):
    """
    不要使用这个方法来获取步长
    """
    file = open(WorkFolder + filename, "rb")
    filesize = os.path.getsize(WorkFolder + filename)

    attribute_name = str(attribute + ": ").encode()
    attribute_value = None
    count = 0
    while file.tell() <= filesize:
        line = file.readline()
        # Because topology only appear in the first 5 line,so if count > 5 ,we can stop looking for it.
        count = count + 1
        if count > 5:
            break
        if line.startswith(attribute.encode()):
            attribute_value = line[line.find(attribute_name) + attribute_name.__len__():line.find(b"\r\n")]

    # Safely close the file.
    file.close()

    # return value we get.
    return attribute_value
