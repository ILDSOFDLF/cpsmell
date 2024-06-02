import re

from utils.files_handler import parse_file_to_ast

py_paths=["F:\\DLFs_dataset\\pytorch\pytorch-2.0.1\\torch\\__init__.py",
          "F:\\DLFs_dataset\\pytorch\pytorch-2.0.1\\torch\\_inductor\\codecache.py",
          "F:\\DLFs_dataset\\pytorch\\pytorch-2.0.1\\torch\\cuda\\__init__.py",
          "F:\\DLFs_dataset\\tensorflow\\tensorflow-2.12.0\\tensorflow\\tools\\test\\gpu_info_lib.py"]
# sys_list=['WINDOWS','MACOS','system','platform']
# ctypes_paths = set()
# code_smells = []
# for path in py_paths:
#     myast = parse_file_to_ast(path)
#     if isinstance(myast, bool) and not myast:
#         continue
#     for item in myast.imports:
#         import_name = item[0]
#         if import_name == "ctypes":
#             ctypes_paths.add(path)
# for path in ctypes_paths:
#     myast=parse_file_to_ast(path)
#     with open(path) as f:
#         lines = f.readlines()
#         hard_code=True
#         for cdll_info in myast.load_cdll:
#             print(cdll_info)
#             if cdll_info[-1] != 0:
#                 if_line=lines[cdll_info[-1]-1].strip()
#                 for sys in sys_list:
#                     if sys in if_line:
#                         hard_code=False
#             lineno=cdll_info[1]
#             line=lines[lineno-1].strip()
#             pattern1 = "{}\(\"(.*)\"".format(cdll_info[0])
#             pattern2 = "{}\(\'(.*)\'".format(cdll_info[0])
#             match_res1 = re.findall(pattern1, line)
#             match_res2 = re.findall(pattern2, line)
#             if hard_code and (len(match_res1) > 0 or len(match_res2) > 0):
#                 code_smells.append([lineno, path])
#
# def test1():
#     for path in py_paths:
#         myast = parse_file_to_ast(path)
#         with open(path) as f:
#             lines = f.readlines()
#             for cdll_info in myast.load_cdll:
#                 lineno = cdll_info[1]
#                 line = lines[lineno - 1].strip()
#                 pattern = "{}\((.*)".format(cdll_info[0])
#                 match_res = re.findall(pattern, line)
#                 if len(match_res) > 0 and (match_res[0][0] == '\'' or match_res[0][0] == '\"'):
#                     if len(match_res[0]) > 1 and ('/' not in match_res[0] or match_res[0][1] == '/'):
#                         print(match_res[0])
#                         code_smells.append([path, lineno])
#     for i in code_smells:
#         print("------------------------")
#         print(i)
if __name__ == '__main__':
    test1()
        # for index in range(len(lines)):
        #     line = lines[index].strip()
        #     # if line.startswith("r\"\"\"") or line.startswith("\"\"\""):
        #     #     comment_flag = True
        #     # if comment_flag:
        #     #     if line.endswith("\"\"\""):
        #     #         comment_flag = False
        #     #     continue
        #     if line.startswith("#"):
        #         continue
        #     match_str_list = ["cdll", "CDLL", "LoadLibrary", "windll", "WinDLL"]
        #     # match_res = re.findall("\'/[a-zA-Z]|\"/[a-zA-Z]|[A-Z]:\\\\", line)
        #
        #     for match_str in match_str_list:
        #         pattern1 = "{}\(\"(.*)\"".format(match_str)
        #         pattern2 = "{}\(\'(.*)\'".format(match_str)
        #         match_res1 = re.findall(pattern1,line)
        #         match_res2 = re.findall(pattern2, line)
        #         if len(match_res1)>0 and '\\' not in match_res1[0] and '/' not in match_res1[0]:
        #             code_smells.append([index+1,path])
        #         if len(match_res2)>0 and '\\' not in match_res2[0] and '/' not in match_res2[0]:
        #             code_smells.append([index+1,path])



#
# for i in code_smells:
#     print(i)