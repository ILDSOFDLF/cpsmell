import datetime
import os

import numpy as np
import pandas as pd

from utils import astChecker
from utils.customast import parse_file

# s1="adsajdINDAKSJ"
# s2="NIDAIAJDOA"
# print(s1.isupper())
# print(s2.isupper())
# #
# print("callgrind_bindings" in "callgrind_bindings")
# myast = astChecker.MyAst()
# list1=[[1,42,12,23],[321,42,55,122]]
# list2=np.array(list1)[:,2].flatten()
# print(list2)
# astContent = parse_file("calibrator.py")
#
# myast.visit(astContent)
start_time = datetime.datetime.now()
print(start_time.timestamp())
# path = "F:\\python_workplace\\check_utils\\utils\\pybind11\\Paddle-develop\\c_py_call_table.csv"
# used_module=[]
# if os.path.exists(path):
#     used_module = pd.read_csv(path).values
# else:
#     print("the path of file is not exist")
# used_module=np.array(used_module)[:,:1].flatten()
# used_module=np.unique(used_module)
# for i in used_module:
#     print(i)

# with open("BUILD",'r') as f:
#     for line in f.readlines():
#         line=line.strip()
#         print(line)
#         if "cost_analyzer_wrapper.cc" in line:
#             print("==================================")
#             print(line)