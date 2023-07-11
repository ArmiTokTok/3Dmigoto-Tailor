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


def get_first_real_index_from_trianglelist_indices(element_name_test, input_trianglelist_indices, max_vertex_count):

    # 从input_trianglelist_indices中选出VertexCount最大的
    # 按顺序找第一个含有此element真实数据的索引
    print("按顺序找第一个含有此element真实数据的索引")
    print(input_trianglelist_indices)
    find_ib_index = ""
    for ib_index in input_trianglelist_indices:
        extract_vb_file = vertex_config[element_name_test.decode()]["extract_vb_file"]
        filter_vb_filenames = get_filter_filenames(ib_index + "-" + extract_vb_file, ".txt")
        if len(filter_vb_filenames) == 0:
            continue
        trianglelist_file_name = filter_vb_filenames[0]
        # print(trianglelist_file_name)

        file_vertex_count = get_attribute_from_txtfile(trianglelist_file_name, "vertex count")
        # print("file_vertex_count")
        # print(file_vertex_count)
        if file_vertex_count != max_vertex_count:
            continue

        vb_file = open(WorkFolder + trianglelist_file_name, "rb")
        vb_file_lines = vb_file.readlines()
        # 读取第一个VertexDataChunk,并去除相同值

        meet_first_vertex_data = False
        element_name_vertex_data_dict = {}
        data_time_dict = {}
        # 要顺便统计每个Data出现的频率
        for line in vb_file_lines:
            if line.startswith(extract_vb_file.encode()):
                meet_first_vertex_data = True

            if meet_first_vertex_data and line == b"\r\n":
                break

            if meet_first_vertex_data:
                line_vertex_data = VertexData(line)
                element_name_vertex_data_dict[line_vertex_data.element_name] = line_vertex_data.data
                if data_time_dict.get(line_vertex_data.data) is None:
                    data_time_dict[line_vertex_data.data] = 1
                else:
                    data_time_dict[line_vertex_data.data] = data_time_dict.get(line_vertex_data.data) + 1
        print("oooooooooo")
        print(element_name_vertex_data_dict)
        print(data_time_dict)

        real_element_list = []
        for element_name in element_name_vertex_data_dict:
            data = element_name_vertex_data_dict.get(element_name)
            if data_time_dict.get(data) == 1:
                real_element_list.append(element_name)

            if data_time_dict.get(data) == 2 and element_name.startswith(b"TEXCOORD"):
                real_element_list.append(element_name)

        # print(real_element_list)

        if element_name_test in real_element_list:
            # print("find real value")
            find_ib_index = ib_index
            break
    return find_ib_index


def get_pointlist_and_trianglelist_info_location(info_location):
    print(split_str)
    print("Execute: {get_pointlist_and_trianglelist_info_location}")
    print("The elements need to read is: " + str(info_location.keys()))
    pointlist_info_location = {}
    trianglelist_info_location = {}

    element_names = list(info_location.keys())
    # 这里应该使用生成的info_location的，而不是直接读取的

    for element_name in element_names:
        if vertex_config[element_name.decode()]["extract_tech"] == "pointlist":
            pointlist_info_location[element_name] = vertex_config[element_name.decode()]["extract_vb_file"]

        if vertex_config[element_name.decode()]["extract_tech"] == "trianglelist":
            trianglelist_info_location[element_name] = vertex_config[element_name.decode()]["extract_vb_file"]

    # Convenient for us to observe the processing result
    print("pointlist_info_location: ")
    print(pointlist_info_location)
    print("trianglelist_info_location: ")
    print(trianglelist_info_location)
    print(split_str)

    return pointlist_info_location, trianglelist_info_location


def merge_pointlist_trianglelist_files(pointlist_indices, input_trianglelist_indices, info_location, max_vertex_count):
    # -------------------------------------读取区域-----------------------------------------------------------
    print("Start to merge pointlist and trianglelist files: ")
    # (1) split the info_location based on config file element's extract_tech.
    pointlist_info_location, trianglelist_info_location = get_pointlist_and_trianglelist_info_location(info_location)
    # 这里根据pointlist_indices索引和pointlist_info_location，得到对应vb的hash值。
    unique_pointlist_vb_list = list(set(list(pointlist_info_location.values())))
    unique_trianglelist_vb_list = list(set(list(trianglelist_info_location.values())))
    pointlist_vb_slot_hash_dict = {}
    trianglelist_vb_slot_hash_dict = {}
    print("pointlist_vb_slot hash:")
    for pointlist_vb_slot in unique_pointlist_vb_list:
        prefix = pointlist_indices[0] + "-" + pointlist_vb_slot
        filenames = get_filter_filenames(prefix, ".txt")
        if len(filenames) == 0:
            continue
        pointlist_vb_file = filenames[0]
        vb_slot_hash = pointlist_vb_file[len(prefix + "="):len(prefix + "=") + 8]
        print(pointlist_vb_slot + " :" + vb_slot_hash)
        pointlist_vb_slot_hash_dict[pointlist_vb_slot] = vb_slot_hash
    print("trianglelist_vb_slot hash:")

    for trianglelist_vb_slot in unique_trianglelist_vb_list:

        filenames = []
        for index in input_trianglelist_indices:
            prefix = index + "-" + trianglelist_vb_slot
            filenames = get_filter_filenames(prefix, ".txt")
            if len(filenames) == 0:
                continue
            else:
                break

        print(filenames)

        trianglelist_vb_file = filenames[0]
        vb_slot_hash = trianglelist_vb_file[len(prefix + "="):len(prefix + "=") + 8]
        print(trianglelist_vb_slot + " :" + vb_slot_hash)
        trianglelist_vb_slot_hash_dict[trianglelist_vb_slot] = vb_slot_hash

    pointlist_category_vb_dict = {}
    # 计算得到每个vb0,vb1对应的category
    for element_name in pointlist_info_location.keys():
        category = vertex_config[element_name.decode()]["category"]
        extract_vb_file = vertex_config[element_name.decode()]["extract_vb_file"]
        pointlist_category_vb_dict[extract_vb_file] = category
    print(pointlist_category_vb_dict)
    trianglelist_category_vb_dict = {}
    for element_name in trianglelist_info_location.keys():
        category = vertex_config[element_name.decode()]["category"]
        extract_vb_file = vertex_config[element_name.decode()]["extract_vb_file"]
        trianglelist_category_vb_dict[extract_vb_file] = category
    print(trianglelist_category_vb_dict)

    print(pointlist_vb_slot_hash_dict)
    print(trianglelist_vb_slot_hash_dict)
    # 随后将这些值保存到配置文件
    for vb_slot, vb_hash in pointlist_vb_slot_hash_dict.items():
        category = pointlist_category_vb_dict.get(vb_slot)
        print(category)
        tmp_config.set("category_hash", category, vb_hash)
        tmp_config.set("category_slot", category, vb_slot)
        tmp_config.write(open(config_folder + "/tmp.ini", "w"))

    for vb_slot, vb_hash in trianglelist_vb_slot_hash_dict.items():
        category = trianglelist_category_vb_dict.get(vb_slot)
        print(category)
        tmp_config.set("category_hash", category, vb_hash)
        tmp_config.set("category_slot", category, vb_slot)
        tmp_config.write(open(config_folder + "/tmp.ini", "w"))

    # 将修改后的配置信息写回 .ini 文件


    # (2) Read pointlist element vertexdata list dict.
    print(split_str)
    pointlist_vertex_count = 0
    pointlist_element_vertex_data_list_dict = {}
    if len(pointlist_info_location) != 0:
        pointlist_element_list = []
        for element_name in list(pointlist_info_location.keys()):
            pointlist_element_list.append(element_name.decode())
        pointlist_vertex_count, pointlist_element_vertex_data_list_dict = read_element_vertex_data_list_dict(pointlist_indices[0], pointlist_element_list)
    print("len(pointlist_element_vertex_data_list_dict.get(BLENDINDICES)) :")
    print(len(pointlist_element_vertex_data_list_dict.get("BLENDINDICES")))

    # (3) Read trianglelist element vertexdata list dict.
    # 根据element_name,在给出的trianglelist_indices中找到第一个含有真实对应element数据的index
    print("Read trianglelist element vertexdata list dict.")
    trianglelist_vertex_count = 0
    trianglelist_element_vertex_data_list_dict = {}
    if len(trianglelist_info_location) != 0:
        element_real_index_dict = {}
        for element_name in list(trianglelist_info_location.keys()):
            index = get_first_real_index_from_trianglelist_indices(element_name, input_trianglelist_indices, max_vertex_count)
            element_real_index_dict[element_name] = index
        print(element_real_index_dict)

        for element_name in element_real_index_dict:
            index = element_real_index_dict.get(element_name)
            vertex_data_list = get_vertex_data_list(index, element_name.decode())
            trianglelist_element_vertex_data_list_dict[element_name.decode()] = vertex_data_list
            trianglelist_vertex_count = len(vertex_data_list)

    # print(trianglelist_element_vertex_data_list_dict)
    # print("len(trianglelist_element_vertex_data_list_dict.get(TEXCOORD)) :")
    # print(len(trianglelist_element_vertex_data_list_dict.get("TEXCOORD")))

    # Calculate final vertex count depends on pointlist
    vb0_vertex_count = trianglelist_vertex_count
    if len(trianglelist_info_location) == 0:
        vb0_vertex_count = pointlist_vertex_count

    # -------------------------------------生成区域-----------------------------------------------------------
    # (4) Get header_info_str
    # 对于9684c4091fc9e35a缺失BLENDWEIGTHS的情况，生成header_info使用的element_list需要添加BLENDWEIGHTS
    header_info_input_element_list = list(info_location.keys())
    if root_vs == "9684c4091fc9e35a" and auto_completion_blendweights:
        header_info_input_element_list.append(b"BLENDWEIGHTS")

    header_info_str = get_header_info_str(vb0_vertex_count, header_info_input_element_list)
    # print(split_str)
    # print("Header info str: ")
    # print(header_info_str)

    # 这里我们需要把最终使用的element_list列表写到tmp.ini里,然后在Split的时候来读取
    tmp_element_list_str = ""
    for element in header_info_input_element_list:
        tmp_element_list_str = tmp_element_list_str + element.decode() + ","
    tmp_element_list_str = tmp_element_list_str[0:-1]
    tmp_config.set("Ini", "tmp_element_list", tmp_element_list_str)
    tmp_config.write(open(config_folder + "/tmp.ini", "w"))

    # (5) Merge pointlist and trianglelist together.
    # print(trianglelist_element_vertex_data_list_dict)
    pointlist_element_vertex_data_list_dict.update(trianglelist_element_vertex_data_list_dict)

    # 对于9684c4091fc9e35a缺失BLENDWEIGTHS的情况，需要额外添加一个默认的vertex_data_dict来装载默认的BLENDWEIGHTS值。
    if root_vs == "9684c4091fc9e35a" and auto_completion_blendweights:
        # 1.构建VertexData
        # 2.构建符合vertex_count的长度的列表，并装入字典
        blendweight_list = []
        for i in range(vb0_vertex_count):
            vertex_data = VertexData(b"vb0[" + str(i).encode() +b"]+666 BLENDWEIGHTS: 1, 0, 0, 0\r\n")
            blendweight_list.append(vertex_data)
        blendweight_dict = {"BLENDWEIGHTS": blendweight_list}
        pointlist_element_vertex_data_list_dict.update(blendweight_dict)

    merged_element_vertex_data_list_dict = pointlist_element_vertex_data_list_dict

    print(split_str)
    print(len(merged_element_vertex_data_list_dict.get("BLENDINDICES")))


    # Order by info_location.keys()
    print(info_location.keys())
    ordered_element_vertex_data_list_dict = {}
    for element_name in info_location.keys():
        values = merged_element_vertex_data_list_dict.get(element_name.decode())
        ordered_element_vertex_data_list_dict[element_name.decode()] = values

    merged_element_vertex_data_list_dict = ordered_element_vertex_data_list_dict
    print(merged_element_vertex_data_list_dict.keys())

    # (6) 获取唯一的ib的index
    ib_file_bytes, ib_file_first_index_list = get_unique_ib_bytes_by_indices(input_trianglelist_indices)
    unique_trianglelist_ib_indices_list = []
    # 遍历ib_file_bytes，读取每一个trianglelist索引的ib文件进行对比，满足就把第一个满足的索引添加到列表
    for ib_file_byte in ib_file_bytes:
        for ib_index in input_trianglelist_indices:
            trianglelist_ib_file = open(WorkFolder + get_filter_filenames(ib_index + "-ib", ".txt")[0], "rb")
            trianglelist_ib_file_byte = trianglelist_ib_file.read()
            trianglelist_ib_file.close()
            if trianglelist_ib_file_byte == ib_file_byte:
                unique_trianglelist_ib_indices_list.append(ib_index)
                break

    print("ib_file_first_index_list: ")
    print(ib_file_first_index_list)

    # 这里需要将ib_file_first_inex_list写到tmp.ini中
    match_first_index_str = ""
    for first_index in ib_file_first_index_list:
        match_first_index_str = match_first_index_str + first_index.decode() + ","
    match_first_index_str = match_first_index_str[0:-1]
    tmp_config.set("Ini", "match_first_index", match_first_index_str)
    tmp_config.write(open(config_folder + "/tmp.ini", "w"))

    print("unique_trianglelist_ib_indices_list: ")
    print(unique_trianglelist_ib_indices_list)

    part_names = []
    for order_number in range(len(unique_trianglelist_ib_indices_list)):
        part_names.append(part_name + "_part" + str(order_number))

        trianglelist_ib_index = unique_trianglelist_ib_indices_list[order_number]
        print(split_str)
        print(vb0_vertex_count)
        print(split_str)
        model_file_data = ModelFileData(trianglelist_ib_index, order_number, merged_element_vertex_data_list_dict,
                                        header_info_str, vb0_vertex_count)

        model_file_data.calculate_vertex_data_str()

        model_file_data.save_to_file()
        print(str(trianglelist_ib_index) + " process over")

    # 记录part_names到tmp.ini方便后续使用
    part_names_str = ""
    for name in part_names:
        part_names_str = part_names_str + name + ","
    part_names_str = part_names_str[0:-1]
    tmp_config.set("Ini", "part_names", part_names_str)
    tmp_config.write(open(config_folder + "/tmp.ini", "w"))


def read_element_vertex_data_list_dict(ib_index, read_element_list, convert_normal=False):
    vertex_count = 0
    element_vertex_data_list_dict = {}
    # {"POSITION":[xxx,xxx]}
    for element_name in read_element_list:
        vertex_data_list = get_vertex_data_list(ib_index, element_name, convert_normal=convert_normal)
        element_vertex_data_list_dict[element_name] = vertex_data_list

        vertex_count = len(vertex_data_list)
    # print(element_vertex_data_list_dict.get("POSITION")[0].element_name)
    return vertex_count, element_vertex_data_list_dict


def merge_ue4():
    ib_indices = get_indices_by_draw_ib()
    print(ib_indices)
    for order_number in range(len(ib_indices)):
        # (1) read VertexData object list for every element_name.
        ib_index = ib_indices[order_number]

        # 因为后面的方法接收的都是bytes类型的element，所以这里要做转换
        bytes_element_list = []
        for element in element_list:
            bytes_element_list.append(element.encode())

        # 这里的element_list用原始的
        vertex_count, element_vertex_data_list_dict = read_element_vertex_data_list_dict(ib_index, element_list, convert_normal=True)

        # (2) get header_info_str.
        # 这里要用bytes的
        header_info_str = get_header_info_str(vertex_count, bytes_element_list)

        # Initial a model_file_data.
        model_file_data = ModelFileData(ib_index, order_number, element_vertex_data_list_dict, header_info_str, vertex_count)

        # calculate vertex_data_str.
        model_file_data.calculate_vertex_data_str()
        # save to file
        model_file_data.save_to_file()
        print(str(ib_index) + " process over.")
        
        
def merge_unity():
    # Decide weather to create a new {OutputFolder}.
    if DeleteOutputFolder:
        if os.path.exists(OutputFolder):
            shutil.rmtree(OutputFolder)

    # Make sure the {OutputFolder} exists.
    if not os.path.exists(OutputFolder):
        os.mkdir(OutputFolder)

    # (3) Calculate vertex_limit_vb.
    vertex_limit_raise_index = trianglelist_indices[0]
    # Get vb0 filename, normally it always use vb0 to store POSITION info,so we use vb0 by default.
    first_draw_vb_filename = get_filter_filenames(vertex_limit_raise_index+"-vb0=", ".txt")[0]
    index_vb_prefix = vertex_limit_raise_index + "-vb0="
    vertex_limit_vb = first_draw_vb_filename[len(index_vb_prefix):len(index_vb_prefix) + 8]
    # Save to tmp.ini for future split script use.
    tmp_config.set("Ini", "vertex_limit_vb", vertex_limit_vb)
    tmp_config.write(open(config_folder + "/tmp.ini", "w"))
    print("Calculated VertexLimitRaise hash value: " + vertex_limit_vb)
    print(split_str)

    # (4) move trianglelist related files.
    move_related_files(trianglelist_indices, OutputFolder, move_dds=True)

    # (5) Start to merge vb0 files.
    merge_pointlist_trianglelist_files(pointlist_indices, trianglelist_indices, info_location, max_vertex_count)


if __name__ == "__main__":
    if Engine == "UE4":
        merge_ue4()
    
    if Engine == "Unity":
        merge_unity()