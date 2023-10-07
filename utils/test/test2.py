import re

from utils.files_handler import read_c_files

import numpy as np
from typing import List,Dict,Optional

class People:
    name="jack"
    age=29


class Music:
    musicname="my_dream"


def get_PYBIND11_MODULE(path):
    py_method_list = []
    c_method_list = []
    module_list = []
    pybind_flag = 0
    lambda_flag = 0
    code_cancel = 0
    str_flag = 0
    not_match = 0
    has_check = 0
    arr = []
    str = ""
    with open(path, 'r') as f:
        for line in f.readlines():
            line = line.strip()  # 删除前后空格
            if line.isspace() or line.startswith('#') or line.startswith("//"):  # 如果字符串为空白字符，如'\n',空格等或者字符串为注释
                continue
            if line.startswith("/*") and str_flag==0:
                code_cancel = 1
            if code_cancel == 1:
                if line.endswith("*/"):
                    code_cancel = 0
                continue

            if pybind_flag == 0:
                arr_name = re.findall("PYBIND11_MODULE\((.*),", line)

                if arr_name:
                    arr = []

                    module_list.append(arr_name[0])
                    if line.endswith("}"):
                        continue
                    arr.append("{")
                    pybind_flag = 1  # 1表示找到了pybind
                continue
            if pybind_flag == 1:
                if line.startswith("m.def") or not_match == 1:
                    str_flag = 1
                    if not_match == 1:
                        s=re.split(",",str + line)[0]
                    else:
                        s = re.split(",", line)[0]
                    py_method_name = re.findall("m.def\(\"(.*)\"", s)
                    if len(py_method_name) == 0:
                        not_match = 1  # 进来匹配了，但是没匹配上
                        check_lambda(line, arr,lambda_flag)
                        str = str + line
                        continue
                    if not_match == 1:
                        not_match = 0

                    sub_py_list = []
                    str = str + line
                    sub_py_list.append(path)
                    sub_py_list.append(py_method_name[0])
                    print(sub_py_list[1])
                    py_method_list.append(sub_py_list)

                    lambda_flag=check_lambda(line, arr,lambda_flag)
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
                        lambda_flag=check_lambda(line, arr,lambda_flag)
                        str = str + line
                    if len(arr)<=1:
                        sub_c_list = []
                        sub_c_list.append(path)
                        if lambda_flag == 0:
                            c_method_name = str.split(",")[1].strip()
                            if c_method_name.endswith(";"):
                                c_method_name = re.findall("(.*)\);", c_method_name)[0]

                            elif c_method_name.endswith(","):
                                c_method_name = re.findall("(.*),", c_method_name)[0]

                            sub_c_list.append(c_method_name)

                        else:
                            sub_c_list.append("lambda表达式")
                        print(sub_c_list[1])
                        c_method_list.append(sub_c_list)
                        str = ""
                        lambda_flag = 0
                        str_flag = 0
                        if len(arr) == 0:
                            pybind_flag = 0



    for i in c_method_list:
        print(i)
    print("-------------python_method---------------")
    for j in py_method_list:
        print(j)

    print("------------module-------------------")
    print(*module_list)


def check_lambda(line, arr,flag):
    symbols = {'}': '{', ')': '('}
    symbols_L, symbols_R = symbols.values(), symbols.keys()


    # flag=0#1表示确定有lambda表达式
    for ch in line:
        if ch == "[":
            flag = 1
            continue

        if ch in symbols_L:
            arr.append(ch)
        elif ch in symbols_R:
            if arr and arr[-1] == symbols[ch]:
                arr.pop()
            else:
                print("code is error")
    return flag


if __name__ == '__main__':
    c_files = "/Users/charles/PycharmProjects/DeepLearning-framework/tensorflow-master/tensorflow/python/tfe_wrapper.cc"
    get_PYBIND11_MODULE(c_files)
