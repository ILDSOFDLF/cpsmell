import os
import re

import numpy
import pandas as pd
from lxml import etree

from utils.configuration import XML_Line_Shifting
from utils.srcml_parse import SrcML_Parser
from utils.version_management import DFLs_version, Frame_names


class Utils:
    def __init__(self, frame_name,frame_version,front_flag=False):
        self.frame_name = frame_name
        self.frame_version=frame_version
        self.front_flag=front_flag
        self.srcml_parser = SrcML_Parser()
        self.parser = etree.HTMLParser(huge_tree=True, encoding="utf-8")
        self.QUERY_METHODS_TABLE = "//decl_stmt/decl[type/name=\'PyMethodDef\']|//decl_stmt/decl[type/name/name[last()]=\'PyMethodDef\']"
        self.QUERY_MODULE="//decl_stmt/decl[type//name[last()]=\'PyModuleDef\']"

    def getPyMethodDef(self):
        py_c_fun_list = []
        self.srcml_parser.read_c_files(self.frame_name,self.frame_version,front_flag=True)
        for path in self.srcml_parser.c_files:
            archive = self.srcml_parser.parse_c_files(path)
            pymethoddefs = etree.XML(archive.srcML().encode(), self.parser).xpath(self.QUERY_METHODS_TABLE)
            for node in pymethoddefs:
                methods_table = node.find("name")
                if methods_table.text is None:
                    methods_table = node.find("name/name")
                print(methods_table.text)

                blocks = node.findall("init/expr/block/expr/block")
                if len(blocks) == 0:
                    py_fun = node.find("init/expr/block/expr[1]/literal")
                    if py_fun is None or py_fun.text is None:
                        continue
                    c_fun = node.find("init/expr/block/expr[2]/name[last()]")
                    if c_fun is None or c_fun.text is None:
                        name_list = block.findall("init/expr/block/expr[2]//name")
                        if len(name_list) > 0:
                            c_fun = name_list[-1]
                        else:
                            continue
                    if c_fun is None:
                        continue
                    print(py_fun.text)
                    print(c_fun.text)
                    sub_py_c_fun_list = [py_fun.text[1:-1], c_fun.text, py_fun.sourceline - XML_Line_Shifting, methods_table.text, path]

                    py_c_fun_list.append(sub_py_c_fun_list)
                else:
                    for block in blocks:

                        py_fun = block.find("expr[1]/literal")
                        if py_fun is None or py_fun.text is None:
                            continue
                        c_fun = block.find("expr[2]/name[last()]")

                        if c_fun is None or c_fun.text is None:
                            print("-------------------------------------")
                            name_list = block.findall("expr[2]//name")
                            if len(name_list) > 0:
                                c_fun = name_list[-1]
                            else:
                                continue
                        if c_fun is None:
                            continue
                        print(py_fun.text)
                        print(c_fun.text)
                        sub_py_c_fun_list = [py_fun.text[1:-1], c_fun.text, py_fun.sourceline - XML_Line_Shifting, methods_table.text,
                                             path]

                        py_c_fun_list.append(sub_py_c_fun_list)
        if self.front_flag:
            pd.DataFrame(py_c_fun_list, columns=['py_fun_name', 'c_fun_name', 'lineno', 'methods_table', 'path']).to_csv(
            os.path.join('python_c',self.frame_name,self.frame_version ,"c_py_fun_table.csv"), index=False)
        else:
            pd.DataFrame(py_c_fun_list, columns=['py_fun_name', 'c_fun_name', 'lineno', 'methods_table', 'path']).to_csv(
            os.path.join(self.frame_name,self.frame_version ,"c_py_fun_table.csv"), index=False)

    def getPyModuleDef(self):
        self.srcml_parser.read_c_files(self.frame_name,self.frame_version,front_flag=True)
        module=[]
        for path in self.srcml_parser.c_files:
            archive = self.srcml_parser.parse_c_files(path)
            pymoduledefs = etree.XML(archive.srcML().encode(), self.parser).xpath(self.QUERY_MODULE)
            for node in pymoduledefs:
                sub_module=[]
                module_name = node.find("init/expr/block/expr[2]/literal")
                sub_module.append(module_name.text[1:-1])
                print(module_name.text[1:-1])
                methods_table = node.find("init/expr/block/expr[5]/name")
                if methods_table is not None and methods_table.text != "NULL":
                    sub_module.append(methods_table.text)
                    print(methods_table.text)
                else:
                    sub_module.append(None)
                    print("asdsadsa")
                sub_module.append(node.sourceline-XML_Line_Shifting)
                sub_module.append(path)
                module.append(sub_module)
        if self.front_flag:
            pd.DataFrame(module, columns=['module_name', 'methods_table', 'lineno', 'path']).to_csv(
                os.path.join('python_c',self.frame_name, self.frame_version, "module.csv"), index=False)
        else:
            pd.DataFrame(module, columns=['module_name', 'methods_table', 'lineno', 'path']).to_csv(
            os.path.join(self.frame_name,self.frame_version,"module.csv"), index=False)


if __name__ == '__main__':
    for i in range(len(DFLs_version)):
        for path in DFLs_version[i]:
            file_name = path[path.rfind("\\") + 1:]
            file_path = os.path.join(Frame_names[i], file_name)
            if not os.path.exists(file_path):
                os.makedirs(file_path)
            u = Utils(Frame_names[i],file_name)
            u.getPyMethodDef()
            u.getPyModuleDef()



