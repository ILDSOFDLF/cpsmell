import datetime
import math
import os
import re

import numpy as np
import pandas as pd
from lxml import etree

from utils.configuration import Lambda_MAX_Char, XML_Line_Shifting, Max_Function_Num, Max_Call_Sum_Count, \
    IGNORE_KEYWORDS
from utils.files_handler import read_py_files, parse_file_to_ast
from utils.srcml_parse import SrcML_Parser
from utils.version_management import Frame_names, DFLs_version

build_file_dict = {'tensorflow': 'F:\\DLFs_dataset\\tensorflow\\'}


class CodeSmell:
    def __init__(self, frame_name, frame_version):
        self.frame_name = frame_name
        self.frame_version = frame_version
        self.srcml_parser = SrcML_Parser()
        self.parser = etree.HTMLParser(huge_tree=True, encoding="utf-8")
        self.module = []
        self.class_tables = []
        self.pybind_fun_tables = []
        self.pyc_fun_tables = []
        try:
            self.module = pd.read_csv(
                os.path.join("pybind11", self.frame_name, self.frame_version, "module.csv")).values
            self.class_tables = pd.read_csv(
                os.path.join("pybind11", self.frame_name, self.frame_version, "c_py_class_table.csv")).values
            self.pybind_fun_tables = pd.read_csv(
                os.path.join("pybind11", self.frame_name, self.frame_version, "c_py_fun_table.csv")).values
            self.pyc_fun_tables = pd.read_csv(
                os.path.join("python_c", self.frame_name, self.frame_version, "c_py_fun_table.csv")).values
        except FileNotFoundError as e:
            print("the file is null")

        self.py_paths = read_py_files(self.frame_name, self.frame_version)
        self.class_names = []
        self.pybind_fun_names = []
        self.pyc_fun_names = []
        self.call_paths = set()
        self.call_code_lines = 0
        self.ctypes_paths=set()
        if len(self.class_tables) > 0:
            self.class_names = self.class_tables[:, -1].flatten().tolist()
        if len(self.pybind_fun_tables) > 0:
            self.pybind_fun_names = self.pybind_fun_tables[:, 2].flatten().tolist()
        if len(self.pyc_fun_tables) > 0:
            self.pyc_fun_names = self.pyc_fun_tables[:, 0].flatten().tolist()

    def detect_unused_module(self):
        module = self.module
        unused_module = []
        if len(module) != 0:
            used_module = []
            path = os.path.join("pybind11", self.frame_name, self.frame_version, "c_py_call_table.csv")
            if os.path.exists(path):
                used_module = pd.read_csv(path).values
                used_module = used_module[:, :1].flatten()
                used_module = np.unique(used_module)
            else:
                print("the path of file is not exist---->", path)

            for item in module:
                module_name = item[1]
                if module_name == 'python':
                    continue
                if module_name not in used_module and not module_name.isupper():  # not judge macro
                    unused_module.append(item)

            if self.frame_name in build_file_dict:
                build_path = build_file_dict[self.frame_name] + self.frame_version
                build_lines = []
                new_module_table = []
                module_files = np.array(unused_module)[:, 0:1].flatten()
                memory = set()
                for dirpaths, dirnames, fs in os.walk(build_path):
                    for f in fs:
                        if len(build_path) + 1 < len(dirpaths) and dirpaths[len(build_path) + 1] == '.':
                            continue
                        if f == 'BUILD':
                            with open(os.path.join(dirpaths, f)) as b:
                                for line in b.readlines():
                                    build_lines.append(line)

                                    index = 0
                                    for match_str in module_files:
                                        if index in memory:
                                            index = index + 1
                                            continue
                                        match_str = match_str[match_str.rfind("\\") + 1:]
                                        if match_str in line:
                                            new_line = build_lines[-3] + build_lines[-2]
                                            new_module = re.findall("\"(.*)\",", new_line)
                                            if new_module:
                                                new_module = new_module[0]
                                            else:
                                                print("match fail")
                                                break

                                            if new_module != unused_module[index][1]:
                                                sub_module_table = [new_module, index]
                                                new_module_table.append(sub_module_table)
                                            memory.add(index)
                                            break
                                        index = index + 1
                                    if len(memory) == len(module_files):
                                        break
                        if len(memory) == len(module_files):
                            break
                    if len(memory) == len(module_files):
                        break

                if len(new_module_table) > 0:
                    for t in new_module_table:
                        print("new module name")
                        print(t)
                        print("old module")
                        print(unused_module[t[1]])

                    for py_path in self.py_paths:
                        myast = parse_file_to_ast(py_path)
                        if isinstance(myast, bool) and not myast:
                            continue
                        for defitem in myast.imports:
                            i = 0
                            for m in new_module_table:

                                if defitem[0] == m[0]:
                                    unused_module.pop(m[1])
                                    new_module_table.pop(i)
                                    break
                                i = i + 1
                            if len(new_module_table) == 0:
                                break
                        if len(new_module_table) == 0:
                            break

            # enhancing validate
            if len(unused_module) > 0:
                unused_module_names = np.array(unused_module)[:, 1].flatten()
                visited = set()
                for py_path in self.py_paths:
                    myast = parse_file_to_ast(py_path)
                    if isinstance(myast, bool) and not myast:
                        continue
                    id = 0
                    for un_name in unused_module_names:
                        if id in visited:
                            id = id + 1
                            continue
                        for con in myast.constant:
                            if un_name in con[0]:
                                visited.add(id)
                                break
                        id = id + 1
                print(len(unused_module))
                temp = []
                for num in range(len(unused_module)):
                    if num not in visited:
                        temp.append(unused_module[num])
                    else:
                        print("delete module", unused_module[num])
                unused_module = temp
        else:
            print('need run check_module')

        pd.DataFrame(unused_module, columns=['path', 'unused_module_name',
                                             'lineno']).to_csv(os.path.join("detection_results", self.frame_name,
                                                                            self.frame_version, "unused_module.csv"),
                                                               index=False)

    def detect_long_lambda_function_for_inter_language_binding(self):
        long_lambda_table = []
        for item in self.pybind_fun_tables:
            if item[-1] is not None and item[-1] > Lambda_MAX_Char:
                long_lambda_table.append(item)

        pd.DataFrame(long_lambda_table, columns=['c_path', 'module_name', 'py_fun_name', 'c_fun_name', 'lineno',
                                                 'lambda_len']).to_csv(
            os.path.join("detection_results", self.frame_name, self.frame_version, "long_lambda_function.csv"),
            index=False)

    def detect_large_inter_language_binding_class(self):
        code_smell_list = []
        for item in self.class_tables:
            path = item[0]
            class_name = item[-2]
            lineno = item[1]
            archive = self.srcml_parser.parse_c_files(path)
            e = etree.XML(archive.srcML().encode(), self.parser)
            nodes = e.xpath(
                "//expr_stmt/expr[call/name/name[last()]=\'class_\']|//decl_stmt/decl[type/name/name[last()]=\'class_\']")
            for node in nodes:
                if node.sourceline - XML_Line_Shifting != lineno:
                    continue
                alias_list = node.find('name')
                extra = 0
                indir_nodes = []
                if alias_list is not None and alias_list.text is not None:
                    alias_name = alias_list.text
                    indir_nodes = e.xpath("//expr_stmt/expr[call/name/name=\'{}\']".format(alias_name))
                    first_nodes = e.xpath(
                        "//expr_stmt/expr/call[name[name[1]=\'{}\' and name[2][contains(text(),\"def\")]]]".format(
                            alias_name))

                    if len(first_nodes) != 0:
                        for first_node in first_nodes:
                            first_name = first_node.find('argument_list/argument[1]/expr/literal')
                            if first_name is not None:
                                first_name = first_name.text[1:-1]
                                if first_name.startswith('__') and first_name.endswith('__'):
                                    continue
                                else:
                                    extra = extra + 1
                index = 0
                while True:
                    if len(indir_nodes) != 0:
                        node = indir_nodes.pop(0)

                    fun_names = node.xpath(
                        "descendant::call[name[contains(text(),\"def\")]]/argument_list/argument[1]/expr/literal")
                    while index < len(fun_names):
                        fun_name = fun_names[index].text[1:-1]
                        if fun_name.startswith("__") and fun_name.endswith("__"):
                            fun_names.pop(index)
                            continue
                        index = index + 1
                    if len(indir_nodes) == 0:
                        break
                if len(fun_names) + extra > Max_Function_Num:
                    code_smell_list.append([path, class_name, lineno])
                break

        pd.DataFrame(code_smell_list, columns=['path', 'class_name', 'lineno']).to_csv(
            os.path.join("detection_results", self.frame_name, self.frame_version, "large_class.csv"), index=False)

    def detect_unused_entity(self):
        unused_module_path = os.path.join("detection_results", self.frame_name, self.frame_version, "unused_module.csv")
        if os.path.exists(unused_module_path):
            unused_module = pd.read_csv(unused_module_path).values
            unused_module = unused_module[:, 1].flatten()
        else:
            print(unused_module_path, " is not exist")

        visited_class_names = set()
        visited_pybind_fun_names = set()
        visited_pyc_fun_names = set()
        unused_class = []
        unused_fun = []
        for py_path in self.py_paths:
            myast = parse_file_to_ast(py_path)
            if isinstance(myast, bool) and not myast:
                continue
            imports_flag = visited_calls(myast.imports, self.class_names, self.pybind_fun_names, self.pyc_fun_names,
                                         visited_class_names, visited_pybind_fun_names, visited_pyc_fun_names)
            com_flag = visited_calls(myast.component, self.class_names, self.pybind_fun_names, self.pyc_fun_names,
                                     visited_class_names, visited_pybind_fun_names, visited_pyc_fun_names)
            call_flag = visited_calls(myast.call_names, self.class_names, self.pybind_fun_names, self.pyc_fun_names,
                                      visited_class_names, visited_pybind_fun_names, visited_pyc_fun_names)

            if imports_flag or com_flag or call_flag:
                self.call_paths.add(py_path)

        for index in range(len(self.class_tables)):
            module = self.class_tables[index][2]
            c_path = self.class_tables[index][0]
            c_class_name = self.class_tables[index][-2]
            py_class_name = self.class_tables[index][-1]
            lineno = self.class_tables[index][1]
            if module in unused_module:
                continue
            if py_class_name not in visited_class_names:
                unused_class.append([c_path, c_class_name, py_class_name, lineno])

        for index in range(len(self.pybind_fun_tables)):
            module = self.pybind_fun_tables[index][1]
            c_path = self.pybind_fun_tables[index][0]
            c_fun_name = self.pybind_fun_tables[index][-3]
            py_fun_name = self.pybind_fun_tables[index][2]
            lineno = self.pybind_fun_tables[index][-2]
            if module in unused_module:
                continue
            if py_fun_name not in visited_pybind_fun_names:
                if py_fun_name.startswith("__") and py_fun_name.endswith("__"):
                    continue
                unused_fun.append([c_path, c_fun_name, py_fun_name, lineno])
        for index in range(len(self.pyc_fun_tables)):
            py_fun_name = self.pyc_fun_tables[index][0]
            if py_fun_name not in visited_pyc_fun_names:
                c_path = self.pyc_fun_tables[index][-1]
                c_fun_name = self.pyc_fun_tables[index][1]
                lineno = self.pyc_fun_tables[index][2]
                if py_fun_name.startswith("__") and py_fun_name.endswith("__"):
                    continue
                unused_fun.append([c_path, c_fun_name, py_fun_name, lineno])
        for item in unused_class:
            print("unused_class:", item)
        for item in unused_fun:
            print("unused_fun:", item)
        pd.DataFrame(unused_class, columns=['path', 'c_class_name', 'py_class_name', 'lineno']).to_csv(
            os.path.join("detection_results", self.frame_name, self.frame_version, "unused_entity.csv"), index=False)
        pd.DataFrame(unused_fun, columns=['path', 'c_fun_name', 'py_fun_name', 'lineno']).to_csv(
            os.path.join("detection_results", self.frame_name, self.frame_version, "unused_entity.csv"), mode='a',
            index=False)

    def detect_excessive_interLanguage_communication(self):
        if len(self.call_paths) == 0:
            print("you need detect unused entity first")

        excessive_communication_files = []
        for call_path in self.call_paths:
            class_id = set()
            pybind_fun_id = set()
            pyc_fun_id = set()
            communication_files = set()
            myast = parse_file_to_ast(call_path)
            if isinstance(myast, bool) and not myast:
                continue

            class_asnames = dict()
            pybind_fun_asnames = dict()
            pyc_fun_asnames = dict()
            for item in myast.imports:
                name = item[0]
                asname = item[1]
                if name in IGNORE_KEYWORDS:
                    continue
                if isinstance(asname, str):
                    if len(self.class_names) > 0 and name in self.class_names:
                        class_asnames[asname] = name
                    if len(self.pybind_fun_names) > 0 and name in self.pybind_fun_names:
                        pybind_fun_asnames[asname] = name
                    if len(self.pyc_fun_names) > 0 and name in self.pyc_fun_names:
                        pyc_fun_asnames[asname] = name

            for com_item in myast.component:
                com = com_item[0]
                if com in IGNORE_KEYWORDS:
                    continue
                classify_ECC(com, self.class_names, class_id, class_asnames)
                classify_ECC(com, self.pybind_fun_names, pybind_fun_id, pybind_fun_asnames)
                classify_ECC(com, self.pyc_fun_names, pyc_fun_id, pyc_fun_asnames)
            for call_item in myast.call_names:
                com = call_item[0]
                classify_ECC(com, self.class_names, class_id, class_asnames)
                classify_ECC(com, self.pybind_fun_names, pybind_fun_id, pybind_fun_asnames)
                classify_ECC(com, self.pyc_fun_names, pyc_fun_id, pyc_fun_asnames)

            for c_id in class_id:
                print(self.class_names[c_id])
                communication_files.add(self.class_tables[c_id][0])
            for fun_id in pybind_fun_id:
                print(self.pybind_fun_names[fun_id])
                communication_files.add(self.pybind_fun_tables[fun_id][0])
            for fun_id in pyc_fun_id:
                print(self.pyc_fun_names[fun_id])
                communication_files.add(self.pyc_fun_tables[fun_id][-1])
            print("------------------------:%d" % len(communication_files))
            if len(communication_files) >= Max_Call_Sum_Count:
                excessive_communication_files.append([call_path, len(communication_files)])
                print(excessive_communication_files[-1])

        for ans in excessive_communication_files:
            print(ans)
        pd.DataFrame(excessive_communication_files,
                     columns=['call_path', 'number_of_communication_files']).to_csv(
            os.path.join("detection_results", self.frame_name, self.frame_version,
                         "excessive_interLanguage_communication.csv"), index=False)

    def lack_of_rigorous_error_check(self):
        c_path = os.path.join("c_files", self.frame_name, self.frame_version + "_c_files.csv")
        c_files = pd.read_csv(c_path, header=None).values.flatten()
        code_smell_list = []
        for path in c_files:
            archive = self.srcml_parser.parse_c_files(path)
            e = etree.XML(archive.srcML().encode(), self.parser)
            add_object_nodes = e.xpath("//expr[call/name=\'PyModule_AddObject\']")
            for node in add_object_nodes:
                if node.getparent() == 'condition':
                    continue
                if node.find('operator') is not None:
                    continue
                try_list = e.xpath("//try//expr[call/name=\'PyModule_AddObject\']")
                flag_try = False
                if try_list is not None:
                    for t in try_list:
                        if t == node:
                            flag_try = True
                            print("try.............")
                            break
                # print(flag_try)
                if not flag_try:
                    code_smell_list.append([path, node.sourceline - XML_Line_Shifting])

        pd.DataFrame(code_smell_list, columns=['path', 'lineno']).to_csv(
            os.path.join("detection_results", self.frame_name, self.frame_version, "lack_of_rigorous_error_check.csv"),
            index=False)

    def detect_lack_of_static_declaration(self):
        csv_path = os.path.join("python_c", self.frame_name, self.frame_version, "c_py_fun_table.csv")
        c_py_fun = pd.read_csv(csv_path).values
        path_num = len(c_py_fun)
        c_path = os.path.join("c_files", self.frame_name, self.frame_version + "_c_files.csv")
        c_files = pd.read_csv(c_path, header=None).values.flatten()
        code_smell_list = []
        for i in range(path_num):
            path = c_py_fun[i][-1]
            fun_name = c_py_fun[i][1]
            archive = self.srcml_parser.parse_c_files(path)
            e = etree.XML(archive.srcML().encode(), self.parser)
            nodes = e.xpath("//function[name=\'{}\']".format(fun_name))
            if len(nodes) != 0:
                st_node = nodes[0].find("type/specifier")
                if st_node is not None and st_node.text == 'static':
                    continue
                else:
                    code_smell_list.append([path, fun_name, nodes[0].sourceline - XML_Line_Shifting])
            else:
                print(path)
                print(fun_name)
                # print("======================================")

        # enhanced detection using pattern matching
        index = 0
        while index < len(code_smell_list):
            item = code_smell_list[index]
            with open(item[0]) as f:
                content = f.readlines()
                line_sum = len(content)
                line = content[item[-1] - 1].strip()
                if line.startswith("static"):
                    code_smell_list.pop(index)
                    continue
            index = index + 1

        pd.DataFrame(code_smell_list, columns=['path', 'fun_name', 'lineno']).to_csv(
            os.path.join("detection_results", self.frame_name, self.frame_version, "lack_of_static_declaration.csv"),
            index=False)

    def detect_not_using_relative_path(self):
        code_smells = []
        for path in self.py_paths:
            myast = parse_file_to_ast(path)
            if isinstance(myast, bool) and not myast:
                continue
            for item in myast.imports:
                import_name = item[0]
                if import_name == "ctypes":
                    self.ctypes_paths.add(path)
        for path in self.ctypes_paths:
            myast = parse_file_to_ast(path)
            with open(path) as f:
                lines = f.readlines()
                for cdll_info in myast.load_cdll:
                    lineno = cdll_info[1]
                    line = lines[lineno - 1].strip()
                    pattern = "{}\((.*)".format(cdll_info[0])
                    match_res = re.findall(pattern, line)
                    if len(match_res) > 0 and (match_res[0][0] == '\'' or match_res[0][0] == '\"'):
                        if len(match_res[0]) > 1 and ('/' not in match_res[0] or match_res[0][1] == '/'):
                            print(match_res[0])
                            code_smells.append([path, lineno])
        for i in code_smells:
            print(i)
        pd.DataFrame(code_smells, columns=['path', 'lineno']).to_csv(
            os.path.join("detection_results", self.frame_name, self.frame_version, "not_using_relative_path.csv"),
            index=False)

    def detect_hard_code_DLL(self):
        sys_list = ['WINDOWS', 'MACOS', 'system', 'platform']
        code_smells = []
        for path in self.ctypes_paths:
            myast = parse_file_to_ast(path)
            with open(path) as f:
                lines = f.readlines()
                hard_code = True
                for cdll_info in myast.load_cdll:
                    print(cdll_info)
                    if cdll_info[-1] != 0:
                        if_line = lines[cdll_info[-1] - 1].strip()
                        for sys in sys_list:
                            if sys in if_line:
                                hard_code = False
                    lineno = cdll_info[1]
                    line = lines[lineno - 1].strip()
                    pattern = "{}\((.*)".format(cdll_info[0])
                    match_res = re.findall(pattern, line)
                    if len(match_res) > 0 and (match_res[0][0] == '\'' or match_res[0][0] == '\"'):
                        if hard_code and len(match_res[0]) > 1:
                            print(match_res[0])
                            code_smells.append([path, lineno])

    def about_inter_language_files(self):
        # must be last run!
        cpy_files=set()
        cpy_code_lines=0
        module_calls_list=pd.read_csv(os.path.join("pybind11", self.frame_name, self.frame_version,'c_py_call_table.csv')).values
        module_calls_paths=module_calls_list[:,-2].flatten()
        get_inter_language_path(module_calls_paths,cpy_files)
        get_inter_language_path(self.call_paths,cpy_files)
        get_inter_language_path(self.ctypes_paths,cpy_files)
        get_inter_language_path(self.class_tables[:,0].flatten(),cpy_files)
        get_inter_language_path(self.pybind_fun_tables[:,0].flatten(),cpy_files)
        get_inter_language_path(self.pyc_fun_tables[:,-1].flatten(),cpy_files)
        for path in cpy_files:
            with open(path, encoding="utf-8") as f:
                cpy_code_lines += len(f.readlines())
        return len(cpy_files),cpy_code_lines


def get_inter_language_path(src_path,dest_path):
    for path in src_path:
        dest_path.add(path)


def classify_ECC(com, cf_names, cf_id, cf_asnames):
    if len(cf_names) > 0 and (com in cf_names or com in cf_asnames.keys()):
        if com in cf_names:
            id = cf_names.index(com)
        else:
            id = cf_names.index(cf_asnames.get(com))
        cf_id.add(id)


def visited_calls(items, class_names, pybind_fun_names, pyc_fun_names, visited_class_names, visited_pybind_fun_names,
                  visited_pyc_fun_names):
    find_call = False
    for item in items:
        component = item[0]
        add_class = add_calls_component(component, class_names, visited_class_names)
        add_pybind_fun = add_calls_component(component, pybind_fun_names, visited_pybind_fun_names)
        add_pyc_fun = add_calls_component(component, pyc_fun_names, visited_pyc_fun_names)
        if component in IGNORE_KEYWORDS:
            continue
        find_call = add_class or add_pybind_fun or add_pyc_fun

    return find_call


def add_calls_component(component, names, visited_names):
    if component in names:
        visited_names.add(component)
        return True
    return False


if __name__ == '__main__':
    start_time = datetime.datetime.now()
    print("start_time:", start_time)
    calls_list = []
    for i in range(len(DFLs_version)):
        for path in DFLs_version[i]:
            file_name = path[path.rfind("\\") + 1:]

            dest_path = os.path.join("detection_results", Frame_names[i], file_name)
            if not os.path.exists(dest_path):
                os.makedirs(dest_path)
            codesmell = CodeSmell(Frame_names[i], file_name)

            # codesmell.detect_unused_module()
            # codesmell.detect_long_lambda_function_for_inter_language_binding()
            # codesmell.detect_large_inter_language_binding_class()
            # codesmell.detect_unused_entity()
            # codesmell.detect_excessive_interLanguage_communication()
            # codesmell.lack_of_rigorous_error_check()
            codesmell.detect_lack_of_static_declaration()
            # codesmell.detect_not_using_relative_path()
            # must run detect_unused_module ,detect_unused_entity, detect_not_using_relative_path first
            # cpy_file_count,cpy_code_lines=codesmell.about_inter_language_files()
            # calls_list.append([file_name, cpy_file_count, cpy_code_lines])
    if len(calls_list) > 0:
        pd.DataFrame(calls_list, columns=['DFL', 'NumFilesCPy', 'NumCodeLinesCPy']) \
            .to_csv('inter_language_files.csv', index=False)
    end_time = datetime.datetime.now()
    print("end_time:", end_time)
    print("all runtime:", end_time.timestamp() - start_time.timestamp())
