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
import math

import PySimpleGUI as sg
import os
import configparser


def combine_mods():
    # TODO combine multiple mods to a single one and use a variable toggle key to switch between them.

    pass


if __name__ == "__main__":
    """
    A neat and simple mod GUI for Shader Hacker.
    
    Files->Open:    Choose a Mods folder.
    Help->About:    Show author info.
    
    Reference:
    https://www.pysimplegui.org/en/latest/
    https://www.pysimplegui.org/en/latest/#menus
    https://www.pysimplegui.org/en/latest/#image-element
    https://www.pysimplegui.org/en/latest/call%20reference/
    
    """
    # TODO 添加合并相同皮肤mod并按指定快捷键切换选项
    # Define a menu

    menu_def = [
        ['Files', ['Open']]
    ]

    headings = ["Mod name", "Enable", "收藏"]
    table_def = sg.Table(
        values=[],
        headings=headings,
        auto_size_columns=True,
        display_row_numbers=True,
        justification='center',
        key="-ModTable-",
        enable_events=True,
        expand_x=True,
        # expand_y=True,
        # TODO 右键弹出列表
        right_click_menu=[[], ['Enable mod', 'Disable mod']],
        num_rows=12
    )

    # Define the main layout of program
    test_filename = "C:/Program Files/Honkai Impact 3/Games/Mods/Mods大全/爱莉希雅_春好桃夭_SFW/preview.png"
    layout = [
        [sg.Menu(menu_def)],
        [table_def],
        [sg.Image(
            filename="",
            enable_events=True,
            key="PreviewImage",
            size=(200, 200),
            subsample=4
        )]
    ]

    # Create the Window
    window = sg.Window('Shader Freedom Mod Manager V0.1', layout, size=(600, math.floor(671*0.6)),resizable=True)

    # Event Loop to process "events" and get the "values" of the inputs
    while True:
        event, values = window.read()
        if event == sg.WIN_CLOSED or event == 'Cancel':  # if user closes window or clicks cancel
            break

        if event == "Open":
            # choose a Mods folder to read mods
            ModsFolder = sg.popup_get_folder('Choose your 3Dmigoto Mods folder', keep_on_top=True)
            # os.listdir to get all mod folders
            mod_folder_list = []
            mod_files = os.listdir(ModsFolder)
            print(mod_files)
            for filename in mod_files:
                if os.path.isdir(ModsFolder + "/" + filename):
                    enable = "off"
                    if filename.startswith("DISABLED"):
                        enable = "on"

                    mod_folder_list.append([filename, enable])

            # use mod_file_list to update Listbox
            window["-ModTable-"].update(values=mod_folder_list)

            print(ModsFolder)
            pass

        print('You entered ', values[0])

    window.close()
