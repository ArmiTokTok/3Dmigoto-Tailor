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
from TailorUtil import *

part_names = tmp_config["Ini"]["part_names"].split(",")
# mod_name = preset_config["General"]["mod_name"]

# calculate the stride,here must use tmp_element_list from tmp.ini
tmp_element_list = tmp_config["Ini"]["tmp_element_list"].split(",")

# 因为下面这两个dict只有分割和生成配置文件时会用到，所以不放在Tailor_Util中
# Calculate every replace_vb_slot's element_list,used in config file generate step and Split step.
category_element_list = {}
# format: {'vb0': ['POSITION'],'vb1':['NORMAL','TANGENT'],...}
for element_name in tmp_element_list:
    # You need to put it back to the slot which slot it been extract from,so here we use [extract_vb_file]
    category = vertex_config[element_name]["category"]
    slot_element_list = category_element_list.get(category)
    if slot_element_list is None:
        category_element_list[category] = [element_name]
    else:
        slot_element_list.append(element_name)
        category_element_list[category] = slot_element_list

# 根据vb_slot_element_list 获取一个步长字典，例如: {"vb0":40,"vb1":12,"vb2":24}
category_stride_dict = {}
categories = list(category_element_list.keys())
for categpory in categories:
    slot_elements = category_element_list.get(categpory)
    slot_stride = 0
    for slot_element in slot_elements:
        slot_stride_single = vertex_config[slot_element].getint("byte_width")
        slot_stride = slot_stride + slot_stride_single
    category_stride_dict[categpory] = slot_stride

# 获取所有的vb槽位
category_list = list(category_element_list.keys())


category_hash_dict = dict(tmp_config.items("category_hash"))
category_slot_dict = dict(tmp_config.items("category_slot"))

resource_ib_partnames = []
for part_name in part_names:
    name = "Resource_" + mod_name + "_" + part_name
    resource_ib_partnames.append(name)


def get_vb_override_str():
    vb_override_str = ""
    # 自动拼接vb部分的TextureOverride
    for category in category_list:
        vb_hash = category_hash_dict.get(category)
        vb_slot = category_slot_dict.get(category)
        vb_override_str = vb_override_str + "[TextureOverride_" + mod_name + "_" + category + "]" + "\n"

        vb_override_str = vb_override_str + "hash = " + vb_hash + "\n"

        # 这里要提前生成Resource的名称才行
        vb_override_str = vb_override_str + vb_slot + " = " + "Resource_VB_" + category + "\n"

        # 如果是vb2,还需要控制draw call的数量
        # 这里我们需要两个变量来控制VertexLimitRaise特性，一个是开关用于是否生成，一个是需要skip并重新draw的槽位。
        if category == "position":
            vb_override_str = vb_override_str + "handling = skip\n"
            draw_numbers = tmp_config["Ini"]["draw_numbers"]
            vb_override_str = vb_override_str + "draw = " + draw_numbers + ",0\n"

        vb_override_str = vb_override_str + "\n"

        # 添加VertexLimitRaise支持
    vertex_limit_vb = tmp_config["Ini"]["vertex_limit_vb"]
    vb_override_str = vb_override_str + "[TextureOverride_" + mod_name +"_VertexLimitRaise]" + "\n"
    vb_override_str = vb_override_str + "hash = " + vertex_limit_vb + "\n" + "\n"

    return vb_override_str


def get_ib_override_str():
    ib_override_str = ""
    # 首先把原本的IndexBuffer Skip掉
    ib_override_str = ib_override_str + "[TextureOverride_" + mod_name + "_IB]" + "\n"
    ib_override_str = ib_override_str + "hash = " + draw_ib + "\n"
    ib_override_str = ib_override_str + "handling = skip\n\n"
    match_first_index = tmp_config["Ini"]["match_first_index"].split(",")

    # 然后补齐要添加的资源


    for i in range(len(part_names)):
        part_name = part_names[i]
        first_index = match_first_index[i]
        ib_override_str = ib_override_str + "[TextureOverride_" + mod_name + "_" + part_name + "]\n"
        ib_override_str = ib_override_str + "hash = " + draw_ib + "\n"
        ib_override_str = ib_override_str + "match_first_index = " + first_index + "\n"
        ib_override_str = ib_override_str + "ib = " + resource_ib_partnames[i] + "\n"
        # output_str = output_str + texcoord_slot + " = " + resource_texcoord_name + "\n"
        ib_override_str = ib_override_str + "drawindexed = auto\n\n"

    return ib_override_str


def get_texture_resource_str():
    # Auto generate the ps slot we possibly will use.
    # But we still need to modify them to make it work.
    texture_resource_str = ""
    texture_resource_str = texture_resource_str + ";[Resource_diffuse1]\n"
    texture_resource_str = texture_resource_str + ";filename = diffuse1.dds\n" + "\n"

    texture_resource_str = texture_resource_str + ";[Resource_light1]\n"
    texture_resource_str = texture_resource_str + ";filename = light1.dds\n" + "\n"
    return texture_resource_str


def get_vb_resource_str():
    vb_resource_str = ""
    # 循环生成对应的VertexBuffer Resource文件
    for category in category_list:
        vb_resource_str = vb_resource_str + "[Resource_VB_" + category + "]\n"
        vb_resource_str = vb_resource_str + "type = Buffer\n"
        vb_slot_stride = category_stride_dict.get(category)
        vb_resource_str = vb_resource_str + "stride = " + str(vb_slot_stride) + "\n"
        vb_resource_str = vb_resource_str + "filename = " + mod_name + "_" + category + ".buf\n\n"

    return vb_resource_str


def get_ib_resource_str():
    ib_resource_str = ""
    # 循环生成对应的IndexBuffer Resource文件
    for i in range(len(part_names)):
        part_name = part_names[i]
        resource_name = resource_ib_partnames[i]
        ib_resource_str = ib_resource_str + "[" + resource_name + "]\n"
        ib_resource_str = ib_resource_str + "type = Buffer\n"
        ib_resource_str = ib_resource_str + "format = " + preset_config["Merge"]["ib_format"] + "\n"
        # compatible with GIMI script.
        if i == 0:
            ib_resource_str = ib_resource_str + "filename = " + part_name + ".ib\n\n"
        else:
            ib_resource_str = ib_resource_str + "filename = " + part_name + "_new.ib\n\n"

    return ib_resource_str


def get_end_str():
    end_str = ""
    end_str = end_str + "; .ini generated by 3Dmigoto-Tailor script.\n"
    end_str = end_str + "; Github: https://github.com/airdest/3Dmigoto-Tailor\n"
    end_str = end_str + "; Discord: https://discord.gg/U8cRdUYZrR\n"
    end_str = end_str + "; Author of this mod: " + Author + "\n"
    return end_str


def move_modfiles():
    final_output_folder = OutputFolder + mod_name + "/"
    # Make sure the final mod folder exists.
    if not os.path.exists(final_output_folder):
        os.mkdir(final_output_folder)
    print("move mod files to final output mod folder.")
    mod_file_list = []
    part_names = tmp_config["Ini"]["part_names"].split(",")
    for num in range(len(part_names)):
        if num == 0:
            mod_file_list.append(part_names[num] + ".ib")
        else:
            mod_file_list.append(part_names[num] + "_new.ib")
    mod_file_list.append(mod_name + ".ini")

    for vb_slot in category_list:
        mod_file_list.append(mod_name + "_" + vb_slot + ".buf")

    for file_path in mod_file_list:
        original_file_path = OutputFolder + file_path
        dest_file_path = final_output_folder + file_path
        if os.path.exists(original_file_path):
            shutil.copy2(original_file_path, dest_file_path)


def collect_ib(filename, offset):
    ib = bytearray()
    with open(filename, "rb") as f:
        data = f.read()
        data = bytearray(data)
        i = 0
        while i < len(data):
            # Here you must notice!
            # GIMI use R32 will need 1H,but we use R16 will nead H
            ib += struct.pack('H', struct.unpack('H', data[i:i + 2])[0] + offset)
            i += 2
    return ib


def collect_vb_v2(vb_file_name, collect_stride, ignore_tangent=True):
    print(split_str)
    print("Start to collect vb info from: " + vb_file_name)
    print("Collect_stride: " + str(collect_stride))
    print(category_element_list)
    print(category_stride_dict)

    position_width = vertex_config["POSITION"].getint("byte_width")
    normal_width = vertex_config["NORMAL"].getint("byte_width")
    print("Prepare position_width: " + str(position_width))
    print("Prepare normal_width: " + str(normal_width))

    # 这里定义一个dict{vb0:bytearray(),vb1:bytearray()}类型，来依次装载每个vb中的数据
    # 其中vb0需要特殊处理TANGENT部分
    collect_vb_slot_bytearray_dict = {}
    with open(vb_file_name, "rb") as f:
        data = bytearray(f.read())
        i = 0
        while i < len(data):
            # print(vb_slot_stride_dict)  {'vb0': 40, 'vb1': 20, 'vb2': 32}

            # 遍历vb_slot_stride_dict，依次处理
            for vb_stride_slot in category_stride_dict:
                vb_stride = category_stride_dict.get(vb_stride_slot)

                vb_slot_bytearray = bytearray()
                # vb0一般装的是POSITION数据，所以需要特殊处理
                if vb_stride_slot == "vb0":
                    if ignore_tangent:
                        # POSITION and NORMAL
                        vb_slot_bytearray += data[i:i + position_width + normal_width]

                        # TANGENT recalculate use normal value,here we use silent's method.
                        vb_slot_bytearray += data[i + position_width:i + position_width + normal_width] + bytearray(
                            struct.pack("f", 1))
                    else:
                        print("在处理vb0时,vb_stride必须为40,实际值: " + str(vb_stride))
                        vb_slot_bytearray += data[i:i + vb_stride]
                else:
                    # 这里必须考虑到9684c4091fc9e35a的情况，所以我们需要在这里不读取BLENDWEIGHTS信息，不读取BLENDWEIGHTS必须满足自动补全的情况
                    blendweights_extract_vb_file = vertex_config["BLENDWEIGHTS"]["extract_vb_file"]
                    if root_vs == "9684c4091fc9e35a" and vb_stride_slot == blendweights_extract_vb_file and auto_completion_blendweights:
                        print("读取时，并不读取BLENDWEIGHTS部分")
                        stride_blendweights = vertex_config["BLENDWEIGHTS"].getint("byte_width")
                        vb_slot_bytearray += data[i:i + vb_stride - stride_blendweights]
                    else:
                        # print("在处理不为vb0时,vb_stride,实际值: " + str(vb_stride))
                        vb_slot_bytearray += data[i:i + vb_stride]

                # print("collecting vb_slot:")
                # print(vb_stride_slot)
                #
                # print("collected vb_slot_bytearray: ")
                # print(len(vb_slot_bytearray))

                # 追加到收集的vb信息中
                original_vb_slot_bytearray = collect_vb_slot_bytearray_dict.get(vb_stride_slot)
                if original_vb_slot_bytearray is None:
                    original_vb_slot_bytearray = bytearray()
                collect_vb_slot_bytearray_dict[vb_stride_slot] = original_vb_slot_bytearray + vb_slot_bytearray

                # 更新步长
                i += vb_stride
    return collect_vb_slot_bytearray_dict


def generate_config_file():
    # 输出便于调试
    print(category_element_list)
    print(category_list)
    # 创建一个空白字符串
    output_str = ""

    output_str = output_str + get_vb_override_str()
    output_str = output_str + get_ib_override_str()
    output_str = output_str + get_texture_resource_str()
    output_str = output_str + get_vb_resource_str()
    output_str = output_str + get_ib_resource_str()
    # 添加结尾的作者信息
    output_str = output_str + get_end_str()

    # 写出到最终配置文件
    output_file = open(OutputFolder + mod_name + ".ini", "w")
    output_file.write(output_str)
    output_file.close()

    # Move to the final folder
    move_modfiles_flag = preset_config["General"].getboolean("move_modfiles_flag")
    if move_modfiles_flag:
        move_modfiles()


if __name__ == "__main__":
    # 首先计算步长
    stride = 0
    for element in tmp_element_list:
        stride = stride + int(vertex_config[element].getint("byte_width"))

    # collect vb
    offset = 0

    # 这里定义一个总体的vb_slot_bytearray_dict
    vb0_slot_bytearray_dict = {}

    # vb filename
    for part_name in part_names:
        vb_filename = OutputFolder + part_name + ".vb"

        ignore_tangent = False

        if repair_tangent == "simple":
            ignore_tangent = True

        # 这里获取了vb0:bytearray() 这样的字典
        vb_slot_bytearray_dict = collect_vb_v2(vb_filename, stride, ignore_tangent=ignore_tangent)

        print(split_str)
        for categpory in vb_slot_bytearray_dict:
            vb_byte_array = vb_slot_bytearray_dict.get(categpory)

            # 获取总的vb_byte_array:
            vb0_byte_array = vb0_slot_bytearray_dict.get(categpory)
            # 如果为空就初始化一下
            if vb0_byte_array is None:
                vb0_byte_array = bytearray()

            vb0_byte_array = vb0_byte_array + vb_byte_array
            vb0_slot_bytearray_dict[categpory] = vb0_byte_array

        # fix_vb_filename = get_filter_filenames(SplitFolder)
        # calculate nearest TANGENT
        if repair_tangent == "nearest":
            # TODO 如何计算TANGENT信息？这始终是一个值得探讨的问题。甚至我觉得这个能单独写一个项目来计算了，所以暂时先不考虑，凑合一下够用了。
            pass
            # position_buf = calculate_tangent_nearest(position_buf, vb_filename)

        # collect ib
        ib_filename = OutputFolder + part_name + ".ib"
        print("ib_filename: " + ib_filename)
        ib_buf = collect_ib(ib_filename, offset)
        with open(OutputFolder + part_name + "_new.ib", "wb") as ib_buf_file:
            ib_buf_file.write(ib_buf)

        # After collect ib, set offset for the next time's collect
        print(offset)
        offset = len(vb0_slot_bytearray_dict.get("position")) // 40

    # write vb buf to file.
    for categpory in vb0_slot_bytearray_dict:
        vb0_byte_array = vb0_slot_bytearray_dict.get(categpory)

        with open(OutputFolder + mod_name + "_" + categpory + ".buf", "wb") as byte_array_file:
            byte_array_file.write(vb0_byte_array)

    # set the draw number used in VertexLimitRaise
    """
    Where draw xxx,0 comes from?
    It is calculated by the byte length of POSITION file subdivide with POSITION file's stride
    so we could get a vertex number,this is the final number used in [TextureOverrideVertexLimitRaise]
    
    when you import any -ib.txt and -vb0.txt into blender,blender will add vertex number for you.
    for example if your import vertex number is 18000,then import it into blender and nothing,and just export it
    to .ib and .vb file,and the vertex number will increase to 21000 or higher,so recalculate this when split it
    into .BLEND file is important,and if you calculate it in Merge script ,it will not work well since the vertex
    number is been modified in blender process.
    """
    draw_numbers = len(vb0_slot_bytearray_dict.get("position")) // 40
    tmp_config.set("Ini", "draw_numbers", str(draw_numbers))
    tmp_config.write(open(config_folder + "/tmp.ini", "w"))

    print(split_str)
    print("Start to generate final .ini file.")
    generate_config_file()

    print("----------------------------------------------------------\r\nAll process done！")

