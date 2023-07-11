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
if __name__ == "__main__":
    """
    Based on ps-t*,quickly move the files.
    """

if __name__ == "__main__":
    # Set work dir, here is your FrameAnalysis dump dir.
    FrameAnalyseFolder = "FrameAnalysis-2023-04-08-150127"
    os.chdir("C:/Users/Administrator/Desktop/Loader/" + FrameAnalyseFolder + "/")
    if not os.path.exists('output'):
        os.mkdir('output')

    filenames = glob.glob('*ps-t*.dds')
    for filename in filenames:
        if os.path.exists(filename):
            print("Moving ： " + filename + " ....")
            shutil.copy2(filename, 'output/' + filename)

    filenames = glob.glob('*ps-t0*.dds')
    for filename in filenames:
        if os.path.exists(filename):
            print("Moving ： " + filename + " ....")
            shutil.copy2(filename, 'output/' + filename)

    filenames = glob.glob('*ps-t9*.dds')
    for filename in filenames:
        if os.path.exists(filename):
            print("Moving ： " + filename + " ....")
            shutil.copy2(filename, 'output/' + filename)

    # Here is the ib you want to import into blender.
    # "1edd6d83":"part2","4d6916bb":"part4"
    ib_hashs = {"9fd57cc6":"body"}

