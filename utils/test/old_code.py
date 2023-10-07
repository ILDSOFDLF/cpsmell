

'''
import os
import re

import numpy
import pandas as pd


def get_PYBIND11_MODULE(self, files_path):
    py_method_list = []
    c_method_list = []
    module_list = []
    pybind_flag = 0  # 1表示进入了PYBIND11_MODULE中
    lambda_flag = 0  # 1表示这是个lambda表达式
    code_cancel = 0  # 1表示这是/*...*/注释的代码
    str_flag = 0  # 0表示没有进入m.def中
    not_match = 0
    has_check = 0  # 0表示没有进行过lambda表达式检测
    arr = []  # 用于存放'{','}','(',')'类型，调用括号匹配算法判断某个PYBIND11_MODULE或函数绑定是否结束
    str = ""
    for path in files_path:
        with open(path, 'r') as f:
            for line in f.readlines():
                line = line.strip()  # 删除前后空格
                if line.isspace() or line.startswith('#') or line.startswith("//"):  # 如果字符串为空白字符，如'\n',空格等或者字符串为注释
                    continue
                if line.startswith("/*") and str_flag == 0:
                    code_cancel = 1
                if code_cancel == 1:
                    if line.endswith("*/"):
                        code_cancel = 0
                    continue

                if pybind_flag == 0:
                    arr_name = re.findall("PYBIND11_MODULE\((.*),", line)

                    if arr_name:
                        sub_module_list = []
                        arr = []
                        sub_module_list.append(path)
                        sub_module_list.append(arr_name[0])
                        module_list.append(sub_module_list)
                        if line.endswith("}"):
                            continue
                        arr.append("{")
                        pybind_flag = 1  # 1表示找到了pybind
                    continue
                if pybind_flag == 1:
                    if line.startswith("m.def") or not_match == 1:
                        str_flag = 1
                        if not_match == 1:
                            s = re.split(",", str + line)[0]
                        else:
                            s = re.split(",", line)[0]
                        py_method_name = re.findall("m.def\(\"(.*)\"", s)
                        if len(py_method_name) == 0:
                            not_match = 1  # 进来匹配了，但是没匹配上
                            check_lambda(line, arr, lambda_flag)
                            str = str + line
                            continue
                        if not_match == 1:
                            not_match = 0

                        sub_py_list = []
                        str = str + line
                        sub_py_list.append(path)
                        sub_py_list.append(py_method_name[0])
                        py_method_list.append(sub_py_list)

                        lambda_flag = check_lambda(line, arr, lambda_flag)
                        has_check = 1  # 表示已经检查了是否存在lambda表达式
                    if str_flag == 0:
                        if line.endswith("}"):
                            arr = []
                            pybind_flag = 0

                    if str_flag == 1:
                        if len(arr) > 1:
                            if has_check == 1:
                                has_check = 0
                                continue
                            lambda_flag = check_lambda(line, arr, lambda_flag)
                            str = str + line
                        if len(arr) <= 1:  # 表示m.def();结束
                            sub_c_list = []
                            sub_c_list.append(path)
                            if lambda_flag == 0:
                                c_method_name = str.split(",")[1].strip()
                                # print(c_method_name+"@@@")

                                if c_method_name.endswith(";"):
                                    c_method_name = re.findall("(.*)\);", c_method_name)[0]

                                elif c_method_name.endswith(","):
                                    c_method_name = re.findall("(.*),", c_method_name)[0]

                                sub_c_list.append(c_method_name)

                            else:
                                sub_c_list.append("lambda表达式")
                            c_method_list.append(sub_c_list)

                            str = ""
                            lambda_flag = 0
                            str_flag = 0
                            if len(arr) == 0:
                                pybind_flag = 0

    pd.DataFrame(c_method_list).to_csv(self.frame_name + "/c_method.csv", header=False, index=False)
    pd.DataFrame(py_method_list).to_csv(self.frame_name + "/py_method.csv", header=False, index=False)
    pd.DataFrame(module_list).to_csv(self.frame_name + "/module.csv", header=False, index=False)


def find_import(self, files_path, module_name):
    c_py_files = []
    for path in files_path:
        with open(path, 'r') as f:
            for line in f.readlines():
                line = line.strip()  # 删除前后空格
                if line.isspace() or line.startswith('#'):
                    continue
                match1 = re.findall("import(.*)as", line)
                match2 = re.findall("import(.*)", line)
                sub_c_py_files = []
                if match1:
                    for module in module_name:
                        if match1[0].strip() == module[-1]:
                            print(module[-1])
                            sub_c_py_files.append(module[-1])
                            sub_c_py_files.append(module[0])
                            sub_c_py_files.append(path)
                            c_py_files.append(sub_c_py_files)
                            break
                elif match2:
                    list = match2[0].split(",")
                    for item in list:
                        for module in module_name:
                            if item.strip() == module[-1]:
                                print(module[-1])
                                sub_c_py_files.append(module[-1])
                                sub_c_py_files.append(module[0])
                                sub_c_py_files.append(path)
                                c_py_files.append(sub_c_py_files)
                                break

    pd.DataFrame(c_py_files, columns=['module_name', 'c_file_path', 'python_file_path']).to_csv(
        self.frame_name + "/c_py_call_table", index=False)


def check_lambda(line,arr,flag):
    symbols = {'}':'{',')': '('}
    symbols_L,symbols_R=symbols.values(),symbols.keys()

    #flag=0#1表示确定有lambda表达式
    for ch in line:
        if ch=="[":
            flag=1
            continue

        if ch in symbols_L:
            arr.append(ch)
        elif ch in symbols_R:
            if arr and arr[-1]==symbols[ch]:
                arr.pop()
            else:
                print("code is error")
    return flag


def read_module(frame_name):
    path = frame_name + "/module.csv"
    if os.path.exists(path):
        module_name = pd.read_csv(path,header=None).values
    else:
        print("the path of file is not exist")
    return module_name


py_files_list=[]
c_files_list=[]
def scan_files(path):

    postfixs = (".c", ".cpp", ".cc", ".h", ".py")


    for dirpaths, dirnames, fs in os.walk(path):
        for f in fs:
            for postfix in postfixs:
                if f.endswith(postfix):
                    if postfix == ".py":
                        py_files_list.append(os.path.join(dirpaths, f))
                    else:
                        c_files_list.append(os.path.join(dirpaths, f))


def read_c_files(frame_name):
    path="../"+"c_files/"+frame_name+"_c_files.csv" #因为一般是check_api调用的，所以相对路径是相对于check_api的相对路径
    if os.path.exists(path):
        c_files = pd.read_csv(path,header=None).values.flatten()  # values提取数据（不会插入表头和序号列）为numpy二维列表，flatten()将二维转化成一维,要指定header=None，不然会默认将第一行作为表头
    else:
        print("the path of file is not exist")
    return c_files


def getPyMethodDef(self, files_path):
    method_list = []
    method_list_flag = 0
    str_flag = 1  # 0表示没有拿到需要的字符串
    c_method_list = []
    py_method_list = []
    str = ""
    for path in files_path:
        with open(path, 'r') as f:
            for line in f.readlines():
                line = line.strip()  # 删除前后空格
                if line.isspace() or line.startswith('#') or line.startswith("//"):  # 如果字符串为空白字符，如'\n',空格等或者字符串为注释
                    continue
                if method_list_flag == 0:
                    arr_name = re.findall("(static)?\s*PyMethodDef\s+(.*)\[", line)

                    if arr_name:
                        arr_name = numpy.array(arr_name)[:, 1]
                        method_list.append(arr_name)
                        method_list_flag = 1  # 1表示找到了method数组
                    continue
                if method_list_flag == 1 and (line.startswith("{\"") or str_flag == 0):
                    if line.endswith("},"):
                        if str_flag == 0:
                            str_flag = 1
                            line = str + line
                            str = ""
                        sub_py_list = []
                        sub_c_list = []
                        py_method_name = re.findall("\{\"(.*)\",", line)[0]
                        sub_py_list.append(path)
                        sub_py_list.append(py_method_name)
                        c_method_name = line.split(",")[1].strip()
                        if c_method_name.startswith("castPyCFunctionWithKeywords"):
                            c_method_name = re.findall("castPyCFunctionWithKeywords\((.*)\)", c_method_name)[0]
                        sub_c_list.append(path)
                        sub_c_list.append(c_method_name)

                        py_method_list.append(sub_py_list)
                        c_method_list.append(sub_c_list)
                    else:
                        str_flag = 0
                        str += line
                    continue
                if method_list_flag == 1:
                    if line.endswith(";"):
                        method_list_flag = 0

    # pd.DataFrame(c_method_list).to_csv("torch/c_method.csv")
    # pd.DataFrame(py_method_list).to_csv("torch/py_method.csv")
    pd.DataFrame(c_method_list).to_csv(self.frame_name + "/c_method.csv", header=False, index=False)
    pd.DataFrame(py_method_list).to_csv(self.frame_name + "/py_method.csv", header=False, index=False)

    return method_list


    def parse_module(self,frame_name, xpath):
        parser = etree.HTMLParser(huge_tree=True, encoding="utf-8")
        SrcML_Parser.read_c_files(frame_name)

        for path in self.c_files:
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

            list = etree.XML(archive.srcML().encode(), parser).xpath(xpath)
            for item in list:
                sub_module_list = []
                sub_module_list.append(path)
                sub_module_list.append(item)
                self.module_list.append(sub_module_list)

        print(len(self.module_list))


    def parse_c_py_function(self,frame_name):
        parser = etree.HTMLParser(huge_tree=True, encoding="utf-8")
        SrcML_Parser.read_c_files(frame_name)

        for path in self.c_files:
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

def detect_unused_component(frame_name):
    modules = MyPybind(frame_name).read_module()
    modules = np.array(modules)[:, 1:2].flatten()
    unused_module_path = os.path.join(frame_name, "codesmell", "unused_module.csv")
    if os.path.exists(unused_module_path):
        unused_module = pd.read_csv(unused_module_path).values
        unused_module = np.array(unused_module)[:, 1:2].flatten()
    else:
        print(unused_module_path, " is not exist")
    class_tables = pd.read_csv(os.path.join(frame_name, "c_py_class_table.csv")).values
    fun_tables = pd.read_csv(os.path.join(frame_name, "c_py_fun_table.csv")).values
    call_tables = pd.read_csv(os.path.join(frame_name, "c_py_call_table.csv")).values
    unused_class = []
    unused_fun = []
    for module in modules:
        class_table = []
        fun_table = []
        for item in class_tables:
            if item[2] == module:
                class_table.append(item)
        for item in fun_tables:
            if item[1] == module:
                fun_table.append(item)
        if module in unused_module:
            if len(class_table) > 0:
                unused_class.append(class_table)
            if len(fun_table) > 0:
                unused_fun.append(fun_table)
            continue
        if len(class_table) > 0:
            class_names = np.array(class_table)[:, -1:].flatten()
            class_names = class_names.tolist()
        if len(fun_table) > 0:
            fun_names = np.array(fun_table)[:, 2:3].flatten()
            fun_names = fun_names.tolist()
        visited_class = set()
        visited_fun = set()
        visited_path = set()
        for call_item in call_tables:
            if module == call_item[0] and call_item[-2] not in visited_path:
                call_path = call_item[-2]
                visited_path.add(call_path)
                file_name = call_path[call_path.rfind("\\") + 1:]
                if isinstance(call_item[1], str):
                    myast = astChecker.MyAst(call_item[1])
                else:
                    myast = astChecker.MyAst(module)
                myast.fileName = file_name
                try:
                    astContent = parse_file(call_path)
                except Exception as e:
                    print(call_path)
                    print(e)
                    continue

                myast.visit(astContent)
                print(type(class_table))
                for import_item in myast.imports:
                    print(import_item[0])
                    if len(class_table) > 0 and import_item[0] in class_names:
                        visited_class.add(class_names.index(import_item[0]))
                    if len(fun_table) > 0 and import_item[0] in fun_names:
                        visited_fun.add(fun_names.index(import_item[0]))

                for com_item in myast.component:
                    com = com_item[0]
                    if len(class_table) > 0 and com in class_names:
                        visited_class.add(class_names.index(com))
                    if len(fun_table) > 0 and com in fun_names:
                        visited_fun.add(fun_names.index(com))
        for index in range(len(class_table)):
            if index not in visited_class:
                unused_class.append(class_table[index])
        for index in range(len(fun_table)):
            if index not in visited_fun:
                unused_fun.append(fun_table[index])

    for item in unused_class:
        print("unused_class:", item)
    for item in unused_fun:
        print("unused_fun:", item)

def detect_excessive_interLanguage_communication(frame_name):
    modules = MyPybind(frame_name).read_module()
    modules = np.array(modules)[:, 1:2].flatten()
    class_tables = pd.read_csv(os.path.join(frame_name, "c_py_class_table.csv")).values
    fun_tables = pd.read_csv(os.path.join(frame_name, "c_py_fun_table.csv")).values
    call_tables = pd.read_csv(os.path.join(frame_name, "c_py_call_table.csv")).values
    excessive_communication_files = []
    for module in modules:
        class_table = []
        fun_table = []

        for item in class_tables:
            if item[2] == module:
                class_table.append(item)
        for item in fun_tables:
            if item[1] == module:
                fun_table.append(item)
        class_names = None
        fun_names = None
        if len(class_table) > 0:
            class_names = np.array(class_table)[:, -1:].flatten()
            class_names = class_names.tolist()
        if len(fun_table) > 0:
            fun_names = np.array(fun_table)[:, 2:3].flatten()
            fun_names = fun_names.tolist()
        visited_path = set()
        for call_item in call_tables:
            if module == call_item[0] and call_item[-2] not in visited_path:
                excessive_communication_class_id = set()
                excessive_communication_fun_id = set()
                sum_calls = 0
                call_path = call_item[-2]
                visited_path.add(call_path)
                file_name = call_path[call_path.rfind("\\") + 1:]
                if isinstance(call_item[1], str):
                    myast = astChecker.MyAst(call_item[1])
                else:
                    myast = astChecker.MyAst()
                myast.fileName = file_name
                try:
                    astContent = parse_file(call_path)
                except Exception as e:
                    print(call_path)
                    print(e)
                    continue
                myast.visit(astContent)
                call_class_count = None
                call_fun_count = None
                if len(class_table) > 0:
                    call_class_count = np.zeros(len(class_names))
                if len(fun_table) > 0:
                    call_fun_count = np.zeros(len(fun_names))
                class_asnames = dict()
                fun_asnames = dict()
                for item in myast.imports:
                    name = item[0]
                    asname = item[1]
                    if isinstance(asname, str):
                        if class_names is not None and name in class_names:
                            class_asnames[asname] = name
                        if fun_names is not None and name in fun_names:
                            fun_asnames[asname] = name
                get_excessive_communication_component(myast, myast.component, class_table, class_names, fun_table,
                                                      fun_names, excessive_communication_class_id,
                                                      excessive_communication_fun_id, call_class_count, call_fun_count,
                                                      class_asnames, fun_asnames, sum_calls)

                get_excessive_communication_component(myast, myast.call_names, class_table, class_names, fun_table,
                                                      fun_names, excessive_communication_class_id,
                                                      excessive_communication_fun_id, call_class_count, call_fun_count,
                                                      class_asnames, fun_asnames, sum_calls)

                if sum_calls > Max_Call_Sum_Count:
                    excessive_communication_files.append([call_path, "all calls is excessive"])
                for class_id in excessive_communication_class_id:
                    py_class_name = class_table[class_id][-1]
                    c_class_name = class_table[class_id][-2]
                    c_path = class_table[class_id][0]
                    excessive_communication_files.append([call_path, py_class_name, c_class_name, c_path])
                for fun_id in excessive_communication_fun_id:
                    py_fun_name = fun_table[fun_id][2]
                    c_fun_name = fun_table[fun_id][3]
                    c_path = fun_table[fun_id][0]
                    excessive_communication_files.append([call_path, py_fun_name, c_fun_name, c_path])
    for ans in excessive_communication_files:
        print("7777777777777777777777777777777777777777777777777777777777")
        print(ans)



                for com_item in myast.component:
                com = com_item[0]
                if com in IGNORE_KEYWORDS:
                    continue
                sum_calls += classify_ECC(com, self.class_names, class_id,call_class_count, class_asnames,Max_Call_Class_Count)
                sum_calls += classify_ECC(com, self.pybind_fun_names,pybind_fun_id, call_pybind_fun_count,pybind_fun_asnames, Max_Call_Fun_Count)
                sum_calls += classify_ECC(com, self.pyc_fun_names, pyc_fun_id,call_pyc_fun_count, pyc_fun_asnames,Max_Call_Fun_Count)
            for call_item in myast.call_names:
                com = call_item[0]
                sum_calls += classify_ECC(com, self.class_names, class_id,call_class_count, class_asnames,Max_Call_Class_Count)
                sum_calls += classify_ECC(com, self.pybind_fun_names,pybind_fun_id, call_pybind_fun_count,pybind_fun_asnames, Max_Call_Fun_Count)
                sum_calls += classify_ECC(com, self.pyc_fun_names, pyc_fun_id,call_pyc_fun_count, pyc_fun_asnames,Max_Call_Fun_Count)

            if sum_calls > Max_Call_Sum_Count:
                excessive_communication_files.append([call_path, "all calls is excessive", None, None])
            for c_id in class_id:
                py_class_name = self.class_tables[c_id][-1]
                c_class_name = self.class_tables[c_id][-2]
                c_path = self.class_tables[c_id][0]
                excessive_communication_files.append([call_path, py_class_name, c_class_name, c_path])
            for fun_id in pybind_fun_id:
                py_fun_name = self.pybind_fun_tables[fun_id][2]
                c_fun_name = self.pybind_fun_tables[fun_id][3]
                c_path = self.pybind_fun_tables[fun_id][0]
                excessive_communication_files.append([call_path, py_fun_name, c_fun_name, c_path])
            for fun_id in pyc_fun_id:
                py_fun_name = self.pyc_fun_tables[fun_id][0]
                c_fun_name = self.pyc_fun_tables[fun_id][1]
                c_path = self.pyc_fun_tables[fun_id][-1]
                excessive_communication_files.append([call_path, py_fun_name, c_fun_name, c_path])

        for ans in excessive_communication_files:
            print("7777777777777777777777777777777777777777777777777777777777")
            print(ans)
        pd.DataFrame(excessive_communication_files,
                     columns=['call_path', 'py_component', 'c_component', 'c_path']).to_csv(
            os.path.join("detection_results", self.frame_name, self.frame_version,
                         "excessive_interLanguage_communication.csv"),
            index=False)

def classify_ECC(com, cf_names, cf_id, call_cf_count, cf_asnames, threshold):
    call_count = 0
    if len(cf_names) > 0 and (com in cf_names or com in cf_asnames.keys()):

        call_count += 1
        if com in cf_names:
            id = cf_names.index(com)
        else:
            id = cf_names.index(cf_asnames.get(com))

        call_cf_count[id] += 1
        if call_cf_count[id] > threshold:
            cf_id.add(id)
    return call_count

        for path in self.ctypes_paths:
            with open(path) as f:
                lines = f.readlines()
                comment_flag = False
                for index in range(len(lines)):
                    line = lines[index].strip()
                    # if line.startswith("r\"\"\"") or line.startswith("\"\"\""):
                    #     comment_flag = True
                    # if comment_flag:
                    #     if line.endswith("\"\"\""):
                    #         comment_flag = False
                    #     continue
                    if line.startswith("#"):
                        continue
                    match_str_list = ["cdll", "CDLL", ".LoadLibrary", "windll", "WinDLL"]
                    # match_res = re.findall("\'/[a-zA-Z]|\"/[a-zA-Z]|[A-Z]:\\\\", line)
                    for match_str in match_str_list:
                        pattern = "{}\((.*)".format(match_str)
                        match_res = re.findall(pattern, line)
                        if len(match_res) > 0 and (match_res[0][0] == '\'' or match_res[0][0] == '\"'):
                            if len(match_res[0]) > 1 and ('/' not in match_res[0] or match_res[0][1] == '/'):
                                print(match_res[0])
                                code_smells.append([path, index + 1])
'''