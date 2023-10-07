import os

import pandas as pd
from lxml import etree
from pylibsrcml import srcml


class SrcML_Parser:
    def __init__(self):
        self.c_files=[]

    def read_c_files(self,frame_name,frame_version,front_flag=False):
        if front_flag:
            c_path = os.path.join("c_files", frame_name,frame_version+ "_c_files.csv")
        else:
            c_path = os.path.join("..\\" + "c_files", frame_name, frame_version + "_c_files.csv")


        if os.path.exists(c_path):
            self.c_files = pd.read_csv(c_path, header=None).values.flatten()
        else:
            print("the path of file is not exist--->",c_path)

    def parse_c_files(self,path):
        # Create a new srcml archive structure
        archive = srcml.srcml_archive()
        # Open a srcml archive for output
        archive.write_open_memory()
        unit = srcml.srcml_unit(archive)
        with open(path, "r", encoding='utf-8') as f:
            buffer = str(f.read())

            unit.set_language(archive.check_extension(path))
            # print(unit.get_language())
            unit.parse_memory(buffer)

            # Translate to srcml and append to the archive
            archive.write_unit(unit)
        # Close archive
        archive.close()
        # print(type(archive.srcML()))

        return archive











