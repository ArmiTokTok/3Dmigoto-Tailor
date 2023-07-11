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
import os
import glob
import shutil
import datetime


if __name__ == "__main__":
    # 此脚本用于TextureOverride和ShaderOverride的规范化命名生成。
    # 首先确定mod文件输出位置
    output_folder = "D:/Desktop/HSRLoader/Mods"

    # 然后确定输出的mod文件名称，这里名称示例为 前缀主要名称_版本号.ini
    # 版本号以v1开始，数字依次增加
    mod_name = "pela"
    version = "v1"
    mod_file_name = mod_name + "_" + version + ".ini"

    # 然后确定最终写入的mod文件的完整路径
    output_filename = output_folder + "/" + mod_file_name

     # 一个变量用于装载最终文本内容
    mod_content = ""

    # 首先给出要Override的IB或VB的字典
    # 格式为 hash值  : [部位名称,handling方式]
    # 例如 "1a1525c8":["裙子","skip"]
    texture_override_dict = {"ca2e71f9":["喇叭裤腿","skip"],
                             "4f9efac1":["棉袄主体","skip"],
                             "75ad6d51":["棉袄下边","skip"],
                             "8e956759":["棉袄绒毛","skip"],
                             "148c3943":["眼罩","skip"],
                             "73eaf816":["棉袄下边的毛","skip"]

                             
                             
                             
                             }
    # 其次要给出Override的VertexShader或者PixelShader，一般都是VertexShader
    # 这里要给出需要check的 层次类型名称，处理方式： handling checktextureoverride  处理值：如果是handling 则可以设置为skip
    # 如果处理方式是checktextureoverride 则处理值可以设置为vb0,ib,cb等等等等，具体参考代码逻辑
    # shader_override_dict = {"b42jdx42x2a25f123":["模型层","handling","skip"]}
    # 记住，如果是checktextureoverride先check vb1 再check ib
    shader_override_dict = {
        # 下面这些是通用的
        
        "2a65eed103b94ebe":["棉袄下边的毛","checktextureoverride",["vb1","ib"]]
         ,"99bdb7bafd41f0ab":["通用_主体模型阴影修正","checktextureoverride",["vb1","ib"]]
         ,"e8425f64cfb887cd":["通用_ROOTVS修正","checktextureoverride",["vb0","vb2"]]
         ,"2030c989673a6153":["通用_灰色层修正","checktextureoverride",["vb1","ib"]]
         }
    
    # 处理TextureOverride
    for override_hash in texture_override_dict:
        attribute = texture_override_dict.get(override_hash)
        object_name = attribute[0]
        handling = attribute[1]

        if handling == "skip":
            texture_override_sect = ""
            texture_override_sect = texture_override_sect + "[TextureOverride_" + mod_name + "_" + object_name + "]\n"
            texture_override_sect = texture_override_sect + "hash = " + override_hash + "\n"
            texture_override_sect = texture_override_sect + "handling = skip\n"
            texture_override_sect = texture_override_sect + "\n"
            mod_content = mod_content + texture_override_sect
    # 处理ShaderOverride
    for override_hash in shader_override_dict:
        attribute = shader_override_dict.get(override_hash)
        object_name = attribute[0]
        handling = attribute[1]
        shader_override_sect = ""
        shader_override_sect = shader_override_sect + "[ShaderOverride_" + mod_name + "_" + object_name + "]\n"
        shader_override_sect = shader_override_sect + "hash = " + override_hash + "\n"

        if handling == "checktextureoverride":
            checks = attribute[2]
            shader_override_sect = shader_override_sect + "if $costume_mods\n"
            for check in checks:
                shader_override_sect = shader_override_sect + "  checktextureoverride = " + check +"\n"
            shader_override_sect = shader_override_sect + "endif\n"

        if handling == "handling":
            check = attribute[2]
            if check == "skip":
                shader_override_sect = shader_override_sect + "handling = skip\n"
        shader_override_sect = shader_override_sect + "\n"

        mod_content = mod_content + shader_override_sect
    
    # 添加作者信息
    author = "Nicomico"
    makedate = datetime.datetime.now().strftime('%Y-%m-%d')
    signature = "Made by "
    contactinfo = "Github:  "
    mod_content = mod_content + ";" + "Author: "+ author +".\n"
    mod_content = mod_content + ";" + "Manufacture date: " + makedate + ".\n"
    mod_content = mod_content + ";" + signature + ".\n"
    mod_content = mod_content + ";" + contactinfo + "\n"
    
    output_file = open(output_filename, "w+")
    output_file.write(mod_content)
    output_file.close()

    
