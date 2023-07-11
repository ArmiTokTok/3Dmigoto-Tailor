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
from BasicConfig import *


class VertexData:
    vb_file_number = b"vb0"  # vb0
    index = None
    aligned_byte_offset = None
    element_name = None
    data = None

    def __init__(self, line_bytes=b""):
        if line_bytes != b"":
            line_str = str(line_bytes.decode())
            # vb_file_number = line_str.split("[")[0]
            # because we vb_merge into one file, so it always be vb0
            vb_file_number = "vb0"
            self.vb_file_number = vb_file_number.encode()

            tmp_left_index = line_str.find("[")
            tmp_right_index = line_str.find("]")
            index = line_str[tmp_left_index + 1:tmp_right_index]
            self.index = index.encode()

            tmp_left_index = line_str.find("]+")
            aligned_byte_offset = line_str[tmp_left_index + 2:tmp_left_index + 2 + 3]
            self.aligned_byte_offset = aligned_byte_offset.encode()

            tmp_right_index = line_str.find(": ")
            element_name = line_str[tmp_left_index + 2 + 3 + 1:tmp_right_index]
            self.element_name = element_name.encode()

            tmp_left_index = line_str.find(": ")
            tmp_right_index = line_str.find("\r\n")
            data = line_str[tmp_left_index + 2:tmp_right_index]
            self.data = data.encode()

    def __str__(self):
        return self.vb_file_number + b"[" + self.index + b"]+" + self.aligned_byte_offset.decode().zfill(3).encode() + b" " + self.element_name + b": " + self.data + b"\n"


class ModelFileData:
    ib_index = None
    order_number = None
    original_ib_filename = ""

    target_ib_filename = ""
    target_vb0_filename = ""

    element_vertex_data_list_dict = {}

    header_info_str = ""

    vertex_data_str = ""

    vertex_count = 0

    def __init__(self, index, order_number, element_vertex_data_list_dict, header_info_str, vertex_count):
        self.ib_index = index
        self.order_number = order_number
        self.element_vertex_data_list_dict = element_vertex_data_list_dict
        self.header_info_str = header_info_str
        self.vertex_count = vertex_count

        self.original_ib_filename = get_filter_filenames(self.ib_index + "-ib", ".txt")[0]

        self.target_ib_filename = draw_ib + "-" + part_name + "_part" + str(self.order_number) + "-ib.txt"
        self.target_vb0_filename = draw_ib + "-" + part_name + "_part" + str(self.order_number) + "-vb0.txt"

    def calculate_vertex_data_str(self):
        print("------------------------------")
        print("calculate_vertex_data_str:")
        print("ib_index: " + str(self.ib_index))
        self.vertex_data_str = self.vertex_data_str + "\nvertex-data:\n\n"
        for index_number in range(self.vertex_count):
            vertex_data_chunk_str = ""
            align_byte_offset = 0
            for calc_element_name in self.element_vertex_data_list_dict:
                # print(calc_element_name)
                vertex_data_list = self.element_vertex_data_list_dict.get(calc_element_name)
                # print(vertex_data_list)
                vertex_data = vertex_data_list[index_number]
                # print(vertex_data.aligned_byte_offset)
                # Reset some values
                vertex_data.aligned_byte_offset = str(align_byte_offset).encode()
                vertex_data.calc_element_name = calc_element_name.encode()

                vertex_data_chunk_str = vertex_data_chunk_str + vertex_data.__str__().decode()
                align_byte_offset = align_byte_offset + vertex_config[calc_element_name].getint("byte_width")
            # print(vertex_data_chunk_str)

            self.vertex_data_str = self.vertex_data_str + vertex_data_chunk_str + "\n"
        # print(self.vertex_data_str)

    def save_to_file(self):
        # (1) copy ib file to target folder.
        if not os.path.exists(OutputFolder):
            os.mkdir(OutputFolder)

        shutil.copy2(WorkFolder + self.original_ib_filename, OutputFolder + self.target_ib_filename)

        # (2) write vb0 str to file.
        vb0_output_str = self.header_info_str + self.vertex_data_str
        with open(OutputFolder + self.target_vb0_filename,"w") as vb0_file:
            vb0_file.write(vb0_output_str)


# ------------------------------------------------------------------------------------------------------------------
def read_pointlit_and_trianglelist_indices():
    dump_files = os.listdir(WorkFolder)
    indices = []
    for filename in dump_files:
        if "-vb0" in filename and filename.endswith(".txt"):
            index = filename.split("-vb0")[0]
            indices.append(index)
    # -----------------------------------------------------
    pointlist_indices_dict = {}
    trianglelist_indices_dict = {}
    root_vs_pointlist_indices_dict = {}
    # format: {index:vertex count,index2,vertex count2,...}
    trianglelist_vertex_count = b"0"

    # -----------------------------------------------------
    for index in range(len(indices)):
        # get all vb0 file's indices.
        vb0_filename = get_filter_filenames( indices[index] + "-vb0", ".txt")[0]

        # If pointlist exists,add it to dict.
        topology_vb = get_attribute_from_txtfile(vb0_filename, "topology")
        if topology_vb == b"pointlist":
            vertex_count = get_attribute_from_txtfile(vb0_filename, "vertex count")
            pointlist_indices_dict[indices[index]] = vertex_count
            if root_vs in vb0_filename:
                root_vs_pointlist_indices_dict[indices[index]] = vertex_count

        # If there is no -ib file,we skip,because we need to read vertex_count from trianglelist.
        ib_filenames = get_filter_filenames(indices[index] + "-ib", ".txt")
        if len(ib_filenames) == 0:
            continue
        ib_filename = get_filter_filenames(indices[index] + "-ib", ".txt")[0]

        # add trianglist tech and get largest vertex_count
        topology_ib = get_attribute_from_txtfile(ib_filename, "topology")
        if topology_ib == b"trianglelist":
            # Filter,ib filename must include input_ib_hash.
            if draw_ib in ib_filename:
                vertex_count = get_attribute_from_txtfile(vb0_filename, "vertex count")
                # print(indices[index])
                trianglelist_indices_dict[(indices[index])] = vertex_count

                # In every game, if a IB have more than one vertex_count, only the largest is true.
                vertex_count_int = int.from_bytes(vertex_count, "big")
                trianglelist_vertex_count_int = int.from_bytes(trianglelist_vertex_count, "big")
                """
                We need the largest one.
                for example if there is:
                INFO:root:{'000051': b'18389', '000052': b'10284', '000053': b'18389', '000062': b'10284'}
                The 18389 is the entire mesh,and 10284 is just a part mesh of 18389,so we use the largest one.
                """
                if vertex_count_int >= trianglelist_vertex_count_int:
                    trianglelist_vertex_count = vertex_count


    print(split_str)
    print("[Pointlist vb index count] Amount:" + str(len(pointlist_indices_dict)))
    print(pointlist_indices_dict)
    print("[ROOT_VS Pointlist vb index count] Amount:" + str(len(root_vs_pointlist_indices_dict)))
    print(root_vs_pointlist_indices_dict)
    print("[Trianglelist vb index count] Amount:" + str(len(trianglelist_indices_dict)))
    print(trianglelist_indices_dict)
    print(split_str)

    # We only need to return the real pointlist which has root_vs
    pointlist_indices = []
    trianglelist_indices = []
    for pointlist_index in root_vs_pointlist_indices_dict:
        if root_vs_pointlist_indices_dict.get(pointlist_index) == trianglelist_vertex_count:
            pointlist_indices.append(pointlist_index)

    for trianglelist_index in trianglelist_indices_dict:
        trianglelist_indices.append(trianglelist_index)

    print("Pointlist vb indices: " + str(pointlist_indices))
    print("Trianglelist vb indices: " + str(trianglelist_indices))
    print(split_str)
    return pointlist_indices, trianglelist_indices, trianglelist_vertex_count


# (1) Read all pointlit and trianglelist indices by match vertex count.
pointlist_indices, trianglelist_indices, max_vertex_count = read_pointlit_and_trianglelist_indices()

use_pointlist = True
if len(pointlist_indices) == 0:
    use_pointlist = False


def get_info_location_from_pointlist_files(index):

    # Automatically get element_list and location info from pointlist files.
    # (1) get vb files by index
    pointlist_vb_file_list = get_filter_filenames(index + "-vb", ".txt")

    print("pointlist_vb_file_list: ")
    print(pointlist_vb_file_list)

    # (2) get location info ,include vb slot and stride and real element list
    vb_vertex_data_chunk = {}
    # get vb stride to finally check again to make sure we got the correct element list
    vb_stride = {}
    for pointlist_vb_file in pointlist_vb_file_list:
        # Get the stride of this pointlist vb file.
        stride = get_attribute_from_txtfile(pointlist_vb_file, "stride")

        # Get the vb file's slot number.
        vb_number = pointlist_vb_file[pointlist_vb_file.find("-vb"):pointlist_vb_file.find("=")][1:].encode()
        # print(vb_number)
        # add to vb_stride {}
        vb_stride[vb_number.decode()] = int(stride.decode())

        # the first line's vertex_data_chunk
        vertex_data_chunk = []

        # Open the vb file.
        vb_file = open(WorkFolder + pointlist_vb_file, 'rb')
        # For temporarily record the last line.
        line_before_tmp = b"\r\n"

        vb_file_size = os.path.getsize(vb_file.name)
        while vb_file.tell() <= vb_file_size:
            # Read a line
            line = vb_file.readline()

            # Process vertexdata
            if line.startswith(vb_number):
                line_before_tmp = line

                vertex_data = VertexData(line)

                # add to vb file's element list

                vertex_data_chunk.append(vertex_data)

            # Process when meet the \r\n.
            if (line.startswith(b"\r\n") or vb_file.tell() == vb_file_size) and line_before_tmp.startswith(vb_number):
                # If we got \r\n,it means this vertex_data_chunk as ended
                # Because we only need to read first line to get the real element name,
                # so we quit from here.
                vb_vertex_data_chunk[vb_number] = vertex_data_chunk
                break

        vb_file.close()

    # Remove duplicated element name by real vertex-data value.
    vb_element_list = {}
    for vb_number in vb_vertex_data_chunk:
        vertex_data_chunk = vb_vertex_data_chunk.get(vb_number)
        # 这里我们计算文件中出现相同的值的次数，如果重复了，则次数不为1，则说明值是假的
        # 但是这里有一个特例，就是BLENDWEIGHTS和BLENDINDICES是可以相同的，所以要特殊处理
        unique_data_times = {}
        for vertex_data in vertex_data_chunk:
            data = vertex_data.data
            if data not in list(unique_data_times.keys()):
                unique_data_times[data] = 1
            else:
                unique_data_times[data] = unique_data_times[data] + 1
        print(unique_data_times)
        real_element_list = []

        for vertex_data in vertex_data_chunk:
            element_name = vertex_data.element_name
            data = vertex_data.data
            # 默认是要添加的
            add_to_real_element_list = True
            # 如果次数不为1，则默认先不添加，在后面再判断一手
            if unique_data_times.get(data) != 1:
                add_to_real_element_list = False
            # 上面说到的BLENDWEIGTHS和BLENDINDICES可以相同，所以这里要进行特殊情况处理
            if element_name in [b"BLENDWEIGHTS", b"BLENDINDICES"] and vb_number != "vb0":
                # 假如当前处理的文件不是vb0，那么就允许存在BLENDWEIGHTS和BLENDINDICES相同的情况
                # 因为不管是Unity还是UE4,vb0一般只装POSITION、NORMAL、TANGENT‘
                print("特殊情况：" + str(vb_number) + "中的BLENDWEIGHTS和BLENDINDICES值相同，允许将" + element_name.decode() + "添加到real_element_list。")
                add_to_real_element_list = True

            if add_to_real_element_list:
                real_element_list.append(element_name.decode())

        vb_element_list[vb_number] = real_element_list
    print(split_str)
    print("real_element_list: ")
    print(vb_element_list)

    # finally we check if the stride is correct with config file value.
    for vb in vb_element_list:
        real_element_list = vb_element_list.get(vb)
        stride = vb_stride.get(vb.decode())

        config_stride = 0
        for element_name in real_element_list:
            byte_width = vertex_config[element_name].getint("byte_width")
            config_stride = config_stride + byte_width

        if stride != config_stride:
            print(str(vb) + " file's stride config is not correct:")
            print("The stride read from pointlist file is :" + str(stride))
            print("But the stride read from vertex_config is :" + str(config_stride))
            # raise ArithmeticError

    # convert format to get info_location format.
    info_location = {}
    for vb in vb_element_list:
        real_element_list = vb_element_list.get(vb)
        for element_name in real_element_list:
            info_location[element_name.encode()] = vb.decode()
    return info_location


# (2) Read location info from pointlist file or from config.
# Automatically get element list and which vb file it's extracted from by read config file.
info_location = {}
if auto_element_list:
    # Auto read element list and location info from pointlist file.
    if len(pointlist_indices) != 0:
        info_location = get_info_location_from_pointlist_files(pointlist_indices[0])
else:
    # Read from preset.ini
    for element in element_list:
        info_location[element.encode()] = vertex_config[element]["extract_vb_file"]
print("Auto read info_location from pointlist file: " + str(auto_element_list))
print("info_location: " + str(info_location))
print(split_str)

# --Class--


def get_indices_by_draw_ib():
    filenames = os.listdir(WorkFolder)
    ib_indices = []
    for filename in filenames:
        if draw_ib in filename and filename.endswith(".txt"):
            index = filename[0:6]
            ib_indices.append(index)
    return ib_indices


def get_vertex_data_list(index, element_name, convert_normal=False):
    """
    TODO:
     Here we just remove the last value to avoid the import into blender problem,
     but we need to add this value when import it back to game,that is another question.

    TODO:
     Here we read from file line by line ,but it's too slow.
     Need to read into a bytearray and process later.
    """
    extract_vb_file = vertex_config[element_name]["extract_vb_file"]

    extract_semantic_name = vertex_config[element_name]["extract_semantic_name"]
    semantic_index = vertex_config[element_name].getint("semantic_index")
    if semantic_index == 0:
        semantic_index = ""
    else:
        semantic_index = str(semantic_index)
    semantic_name = str(extract_semantic_name + semantic_index).encode()

    prefix = index + "-" + extract_vb_file
    print(prefix)
    vb_filename = get_filter_filenames(prefix, ".txt")[0]

    # tmp vertex_data_chunk
    vertex_data_list = []

    # Get the vb file's slot number.
    vb_number = extract_vb_file.encode()

    # For temporarily record the last line.
    line_before_tmp = b"\r\n"

    # Open the vb file.
    vb_file = open(WorkFolder + vb_filename, 'rb')
    vb_file_lines = vb_file.readlines()
    vb_file.close()

    vertex_data_tmp = ""

    for line_index in range(len(vb_file_lines)):
        line = vb_file_lines[line_index]
        # Process vertexdata
        if line.startswith(vb_number):
            line_before_tmp = line
            # only add element_name
            vertex_data = VertexData(line)

            if convert_normal and element_name == "NORMAL":
                """
                In UE4 we got a Normal are 4D problem when import into blender use DarkStarSword's script.
                so here we try to remove the last one,because it seems all value is 1
                seems like it is not useful in blender.
                """
                # remove the last value in normal to solve Normal are 4D problem.
                data = vertex_data.data.decode()
                normals = data.split(",")
                new_data = normals[0] + "," + normals[1] + "," + normals[2]
                new_data = new_data.encode()
                vertex_data.data = new_data
                # print(data)

            if vertex_data.element_name == semantic_name:
                vertex_data.element_name = element_name.encode()

                vertex_data_tmp = vertex_data

        # Process when meet the \r\n.
        if (line.startswith(b"\r\n") or line_index == len(vb_file_lines) -1) and line_before_tmp.startswith(vb_number):
            line_before_tmp = b"\r\n"

            # If we got \r\n,it means this vertex_data_chunk as ended
            vertex_data_list.append(vertex_data_tmp)

    return vertex_data_list


def get_header_info_str(vertex_count, output_element_list):
    # we just generate str here.

    header_str = ""

    stride = 0
    for output_element_name in output_element_list:
        byte_width = vertex_config[output_element_name.decode()].getint("byte_width")
        stride += byte_width

    header_str = header_str + "stride: " + str(stride) + "\n"
    header_str = header_str + "first vertex: 0\n"
    header_str = header_str + "vertex count: " + str(vertex_count) + "\n"
    header_str = header_str + "topology: trianglelist\n"

    aligned_byte_offset = 0
    for order_number in range(len(output_element_list)):
        output_element_name = str(output_element_list[order_number].decode())
        header_str = header_str + "element[" + str(order_number) + "]:\n"

        if output_element_name.startswith("TEXCOORD") and output_element_name != "TEXCOORD":
            header_str = header_str + "  " + "SemanticName: " + "TEXCOORD" + "\n"
        else:
            header_str = header_str + "  " + "SemanticName: " + output_element_name + "\n"

        output_semantic_index = vertex_config[output_element_name]["output_semantic_index"]
        header_str = header_str + "  " + "SemanticIndex: " + output_semantic_index + "\n"


        format = vertex_config[output_element_name]["format"]
        header_str = header_str + "  " + "Format: " + format + "\n"

        header_str = header_str + "  " + "InputSlot: " + "0" + "\n"

        header_str = header_str + "  " + "AlignedByteOffset: " + str(aligned_byte_offset) + "\n"

        header_str = header_str + "  " + "InputSlotClass: " + "per-vertex" + "\n"

        header_str = header_str + "  " + "InstanceDataStepRate: " + "0" + "\n"

        byte_width = vertex_config[output_element_name].getint("byte_width")
        aligned_byte_offset += byte_width

    return header_str


def move_related_files(indices, output_folder, move_dds=False, move_vscb=False, move_pscb=False):
    """
    :param indices:  the file indix you want to move
    :param move_dds: weather move dds file.
    :param only_pst7: weather only move ps-t7 dds file.
    :param move_vscb:
    :param move_pscb:
    :return:
    """

    if move_dds:
        # Start to move .dds files.
        filenames = get_filter_filenames( "ps-t", ".dds")

        for filename in filenames:
            if os.path.exists(WorkFolder + filename):
                for index in indices:
                    if filename.__contains__(index):
                        shutil.copy2(WorkFolder + filename, output_folder + filename)

    if move_vscb:
        # Start to move VS-CB files.
        filenames = get_filter_filenames( "vs-cb", "")

        for filename in filenames:
            if os.path.exists(filename):
                # Must have the vb index you sepcified.
                for index in indices:
                    if filename.__contains__(index):
                        shutil.copy2(WorkFolder + filename, output_folder + filename)

    if move_pscb:
        # Start to move PS-CB files.
        filenames = glob.glob('*ps-cb*')
        filenames = get_filter_filenames( "ps-cb", "")

        for filename in filenames:
            if os.path.exists(filename):
                # Must have the vb index you sepcified.
                for index in indices:
                    if filename.__contains__(index):

                        shutil.copy2(WorkFolder + filename, output_folder + filename)


def get_first_index_in_ibfile(filename):
    ib_file = open(WorkFolder + filename, "rb")
    ib_file_size = os.path.getsize(WorkFolder + filename)
    get_topology = None
    get_first_index = None
    count = 0
    while ib_file.tell() <= ib_file_size:
        line = ib_file.readline()
        # Because topology only appear in the first 5 line,so if count > 5 ,we can stop looking for it.
        count = count + 1
        if count > 5:
            break
        if line.startswith(b"first index: "):
            get_first_index = line[line.find(b"first index: ") + b"first index: ".__len__():line.find(b"\r\n")]

    # Safely close the file.
    ib_file.close()

    return get_first_index


def get_unique_ib_bytes_by_indices(indices):
    ib_filenames = []
    for index in range(len(indices)):
        indexnumber = indices[index]
        ib_filename = sorted(get_filter_filenames( str(indexnumber) + "-ib", ".txt"))[0]
        ib_filenames.append(ib_filename)

    ib_file_bytes = []
    ib_file_first_index_list = []
    for ib_filename in ib_filenames:
        first_index = get_first_index_in_ibfile(ib_filename)

        with open(WorkFolder + ib_filename, "rb") as ib_file:
            bytes = ib_file.read()
            if bytes not in ib_file_bytes:
                ib_file_bytes.append(bytes)

                # also need [first index] info to generate the .ini file.
                if first_index not in ib_file_first_index_list:
                    ib_file_first_index_list.append(first_index)

    # 这里必须得重新排序
    original_dict = {}
    for num in range(len(ib_file_first_index_list)):
        first_index = ib_file_first_index_list[num]
        ib_bytes = ib_file_bytes[num]
        original_dict[first_index] = ib_bytes

    order_first_index_list = sorted(original_dict.keys())
    ordered_dict = {}
    for first_index in order_first_index_list:
        ib_bytes = original_dict.get(first_index)
        ordered_dict[first_index] = ib_bytes

    ib_file_first_index_list = list(ordered_dict.keys())
    ib_file_bytes = list(ordered_dict.values())

    return ib_file_bytes, ib_file_first_index_list



