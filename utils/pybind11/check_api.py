import os

import pandas as pd
from lxml import etree

from utils.configuration import XML_Line_Shifting
from utils.files_handler import parse_file_to_ast
from utils.srcml_parse import SrcML_Parser
from utils.version_management import DFLs_version, Frame_names


class MyPybind:
    def __init__(self, frame_name, frame_version,front_flag=False):
        self.frame_name = frame_name
        self.frame_version = frame_version
        self.front_flag=front_flag
        self.srcml_parser = SrcML_Parser()
        self.used_module = set()
        self.modules = []
        self.parser = etree.HTMLParser(huge_tree=True, encoding="utf-8")
        self.QUERY_MODULE_NAME = "//macro[name=\'PYBIND11_MODULE\']/argument_list/argument[1]"

        self.QUERY_C_PY_FUNCTION = "//expr_stmt/expr/call[name[name[1]=\'m\' and name[2]=\'def\']]/child::argument_list"
        self.QUERY_C_PY_CLASS_1 = "//expr_stmt/expr/call[name/name[last()]=\'class_\']"
        self.QUERY_C_PY_CLASS_2 = "//decl_stmt/decl[type/name/name[last()]=\'class_\']"
        self.QUERY_CALL = "//expr_stmt/expr"

    def get_module(self):
        module_list = []
        self.srcml_parser.read_c_files(self.frame_name, self.frame_version,front_flag=True)
        for path in self.srcml_parser.c_files:
            archive = self.srcml_parser.parse_c_files(path)
            list = etree.XML(archive.srcML().encode(), self.parser).xpath(self.QUERY_MODULE_NAME)
            for item in list:
                sub_module_list = [path, item.text, item.sourceline - XML_Line_Shifting]
                module_list.append(sub_module_list)
        self.modules = module_list
        if self.front_flag:
            pd.DataFrame(module_list, columns=['module_path', 'module_name', 'lineno']).to_csv(
                os.path.join('pybind11',self.frame_name, self.frame_version, "module.csv"), index=False)
        else:
            pd.DataFrame(module_list, columns=['module_path', 'module_name', 'lineno']).to_csv(
            os.path.join(self.frame_name, self.frame_version, "module.csv"), index=False)

    def get_c_py_function(self):
        c_py_fun_list = []
        for item in self.modules:
            path = item[0]
            module_name = item[1]
            archive = self.srcml_parser.parse_c_files(path)
            nodes = etree.XML(archive.srcML().encode(), self.parser).xpath(self.QUERY_C_PY_FUNCTION)

            get_fun(nodes, path, module_name, c_py_fun_list)
            for ele in c_py_fun_list:
                print(ele)
        if self.front_flag:
            pd.DataFrame(c_py_fun_list,
                         columns=['c_path', 'module_name', 'py_fun_name', 'c_fun_name', 'lineno', 'lambda_len']).to_csv(
                os.path.join('pybind11',self.frame_name, self.frame_version, "c_py_fun_table.csv"), index=False, encoding='utf-8')
        else:
            pd.DataFrame(c_py_fun_list,columns=['c_path', 'module_name', 'py_fun_name', 'c_fun_name', 'lineno', 'lambda_len']).to_csv(os.path.join(self.frame_name ,self.frame_version, "c_py_fun_table.csv"), index=False, encoding='utf-8')

    def check_import(self):
        c_py_files = []
        py_paths = []
        py_files_path = os.path.join("..", "py_files", self.frame_name,self.frame_version + "_py_files.csv")
        if os.path.exists(py_files_path):
            py_paths = pd.read_csv(py_files_path, header=None).values.flatten()
        else:
            print("the path of file is not exist")

        for py_path in py_paths:
            myast = parse_file_to_ast(py_path)
            if isinstance(myast, bool) and not myast:
                continue
            for defitem in myast.imports:
                for module in self.modules:
                    if module[-2].isupper():
                        continue
                    if module[-2] == 'python':
                        continue

                    if defitem[0] == module[-2]:
                        self.used_module.add(defitem[0])
                        sub_c_py_files = [defitem[0], defitem[1], module[0], module[-1], py_path, defitem[-1]]
                        c_py_files.append(sub_c_py_files)
                        break
        if self.front_flag:
            pd.DataFrame(c_py_files,
                         columns=['module_name', 'module_asname', 'c_file_path', 'c_lineno', 'python_file_path',
                                  'py_lineno']).to_csv(
                os.path.join('pybind11',self.frame_name, self.frame_version, "c_py_call_table.csv"), index=False)

        else:
            pd.DataFrame(c_py_files, columns=['module_name', 'module_asname', 'c_file_path', 'c_lineno', 'python_file_path','py_lineno']).to_csv(os.path.join(self.frame_name ,self.frame_version, "c_py_call_table.csv"), index=False)

    def get_c_py_class(self):
        c_py_class_list = []
        for item in self.modules:
            path = item[0]
            module_name = item[1]
            archive = self.srcml_parser.parse_c_files(path)
            nodes1 = etree.XML(archive.srcML().encode(), self.parser).xpath(self.QUERY_C_PY_CLASS_1)
            nodes2 = etree.XML(archive.srcML().encode(), self.parser).xpath(self.QUERY_C_PY_CLASS_2)
            get_class(nodes1, nodes2, path, module_name, c_py_class_list)
        if self.front_flag:
            pd.DataFrame(c_py_class_list,
                         columns=['c_path', 'lineno', 'module_name', 'c_class_name', 'py_class_name']).to_csv(
                os.path.join('pybind11',self.frame_name, self.frame_version, "c_py_class_table.csv"), index=False,
                encoding='utf-8')
        else:
            pd.DataFrame(c_py_class_list,columns=['c_path', 'lineno', 'module_name', 'c_class_name', 'py_class_name']).to_csv(os.path.join(self.frame_name ,self.frame_version ,"c_py_class_table.csv"), index=False, encoding='utf-8')

    # def get_c_py_enum(self):
    #
    #     for item in self.modules:
    #         path = item[0]
    #         module_name = item[1]
    #         archive = self.srcml_parser.parse_c_files(path)
    #         nodes=etree.XML(archive.srcML().encode(), self.parser).xpath(self.QUERY_C_PY_ENUM)

    def data_augmentation(self):
        call_list = []
        visited_path = set()
        for item in self.modules:
            path = item[0]
            module_name = item[1]
            module_lineno = item[-1]
            visited_path.add(path)
            archive = self.srcml_parser.parse_c_files(path)
            expr = etree.XML(archive.srcML().encode(), self.parser).xpath(self.QUERY_CALL)
            get_call(module_name, expr, call_list)

        self.srcml_parser.read_c_files(self.frame_name,self.frame_version)
        c_py_class_list = []
        c_py_fun_list = []
        visited_call_list_id = set()
        for i in call_list:
            print(i)
        print("-----------------------------------------------------------")
        print(len(call_list))
        self.snowball_search(call_list, visited_path, visited_call_list_id, c_py_class_list, c_py_fun_list)
        if self.front_flag:
            pd.DataFrame(c_py_fun_list).to_csv(os.path.join('pybind11',self.frame_name, self.frame_version, "c_py_fun_table.csv"),
                                               mode='a', index=False, header=False, encoding='utf-8')
            pd.DataFrame(c_py_class_list).to_csv(
                os.path.join('pybind11',self.frame_name, self.frame_version, "c_py_class_table.csv"), mode='a', index=False,
                header=False, encoding='utf-8')

        else:
            pd.DataFrame(c_py_fun_list).to_csv(os.path.join(self.frame_name ,self.frame_version, "c_py_fun_table.csv"), mode='a', index=False, header=False, encoding='utf-8')
            pd.DataFrame(c_py_class_list).to_csv(os.path.join(self.frame_name ,self.frame_version, "c_py_class_table.csv"), mode='a', index=False, header=False, encoding='utf-8')

    def snowball_search(self, call_list, visited_path, visited_call_list_id, c_py_class_list, c_py_fun_list):
        for c_path in self.srcml_parser.c_files:
            if c_path.endswith('.h') or c_path in visited_path:
                continue
            for index in range(len(call_list)):

                archive = self.srcml_parser.parse_c_files(c_path)
                call_name = call_list[index][0]
                module_name = call_list[index][1]
                e = etree.XML(archive.srcML().encode(), self.parser)
                res_list = e.xpath(
                    "//function[type/name=\'void\' and name[1]=\'{}\']/block/block_content".format(call_name))
                if len(res_list) == 0:
                    continue
                iter_call_nodes = e.xpath(
                    "//function[type/name=\'void\' and name[1]=\'{}\']/block/block_content/expr_stmt/expr".format(
                        call_name))
                get_call(module_name, iter_call_nodes, call_list)

                class_nodes1 = e.xpath(
                    "//function[type/name=\'void\' and name[1]=\'{}\']/block/block_content/expr_stmt/expr/call[name/name[last()]=\'class_\']".format(
                        call_name))
                class_nodes2 = e.xpath(
                    "//function[type/name=\'void\' and name[1]=\'{}\']/block/block_content/decl_stmt/decl[type/name/name[last()]=\'class_\']".format(
                        call_name))
                fun_nodes = e.xpath(
                    "//function[type/name=\'void\' and name[1]=\'{}\']/block/block_content/expr_stmt/expr/call[name[name[1]=\'m\' and name[2]=\'def\']]/child::argument_list".format(
                        call_name))

                get_class(class_nodes1, class_nodes2, c_path, module_name, c_py_class_list)

                get_fun(fun_nodes, c_path, module_name, c_py_fun_list)
                visited_call_list_id.add(index)

        if len(call_list) != len(visited_call_list_id):
            print("len_call_list:", len(call_list))
            print("len_visited_call_list_id:", len(visited_call_list_id))
            new_call_list = []
            for call_index in range(len(call_list)):
                if call_index not in visited_call_list_id:
                    new_call_list.append(call_list[call_index])

        return


def get_fun(nodes, path, module_name, c_py_fun_list):
    for node in nodes:
        c_py_sub_list = []
        flag_lambda = False
        arg_num = 0
        parent_node = node
        c_py_sub_list.append(path)
        c_py_sub_list.append(module_name)

        for childnode in node.iter():
            # print(childnode.tag)

            if childnode.tag == 'argument' and childnode.getparent() is parent_node:
                arg_num += 1
            if arg_num > 2:
                break
            if not flag_lambda and childnode.tag == "literal" and childnode.attrib.get('type') == "string":
                c_py_sub_list.append(childnode.text[1:-1])
            if not flag_lambda and childnode.tag == "name":
                c_name = childnode.text

            if not flag_lambda and childnode.tag == "lambda":
                flag_lambda = True
                len_lambda = 0
                c_py_sub_list.append("lambda expression")
                continue
            if childnode.tag == 'comment':
                continue
            if flag_lambda and childnode.text is not None:
                if childnode.text.strip() in ('(', '{', '['):
                    len_lambda = len_lambda + 1

                len_lambda = len_lambda + len(childnode.text.strip()) - childnode.text.count(' ')
        if flag_lambda:
            c_py_sub_list.append(node.sourceline - XML_Line_Shifting)
            c_py_sub_list.append(int(len_lambda))
        else:
            c_py_sub_list.append(c_name)
            c_py_sub_list.append(node.sourceline - XML_Line_Shifting)
            c_py_sub_list.append(None)

        c_py_fun_list.append(c_py_sub_list)


def get_class(nodes1, nodes2, path, module_name, c_py_class_list):
    for node in nodes1:
        c_class1 = node.find('name/argument_list/argument/expr/name')

        if c_class1 is None or c_class1.text is None:
            c_class1 = node.find('name/argument_list/argument/expr/name/name[last()]')

        py_class1 = node.find('argument_list/argument[2]/expr/literal')
        if py_class1 is None or c_class1 is None:
            continue
        c_py_sub_class = [path, c_class1.sourceline - XML_Line_Shifting, module_name, c_class1.text,
                          py_class1.text[1:-1]]
        c_py_class_list.append(c_py_sub_class)
    for node in nodes2:
        c_class2 = node.find('type/name/argument_list/argument/expr/name')
        if c_class2 is None or c_class2.text is None:
            c_class2 = node.find('type/name/argument_list/argument/expr/name/name[last()]')

        py_class2 = node.find('argument_list/argument[2]/expr/literal')
        if py_class2 is None or c_class2 is None:
            continue
        c_py_sub_class = [path, c_class2.sourceline - XML_Line_Shifting, module_name, c_class2.text,
                          py_class2.text[1:-1]]
        c_py_class_list.append(c_py_sub_class)


def get_enum():
    pass


def get_call(module_name, expr, call_list):
    for nodes in expr:
        dest = []
        for node in nodes.iter():
            dest.append(node)
            if node.tag == 'name' and dest[1].tag == 'call':
                param = dest[1].xpath("argument_list[argument/expr/name=\'m\']")
                if len(dest) == 3 and len(param) != 0:
                    argnum = 0
                    for subnode in param[0].iter():
                        if subnode.tag == 'argument':
                            argnum = argnum + 1
                    if argnum > 1:
                        break
                    name = node.text
                    if name is None:
                        name = node.find('name[last()]')
                        name = name.text
                    if name == 'class_' or name == 'enum_':
                        break
                    sub_call_list = [name, module_name]
                    call_list.append(sub_call_list)
                else:
                    break


if __name__ == '__main__':

    # frame_names = ['tensorflow-master','pytorch-master']
    for i in range(len(DFLs_version)):
        if i<=2:
            continue
        for path in DFLs_version[i]:
            file_name = path[path.rfind("\\") + 1:]
            file_path = os.path.join(Frame_names[i], file_name)
            if not os.path.exists(file_path):
                os.makedirs(file_path)
            pybind = MyPybind(Frame_names[i], file_name)
            pybind.get_module()
            if len(pybind.modules) == 0:
                print("the module is null")
            pybind.check_import()
            pybind.get_c_py_class()
            pybind.get_c_py_function()
            pybind.data_augmentation()

