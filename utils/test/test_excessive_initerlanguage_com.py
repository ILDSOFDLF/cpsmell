import pandas as pd

from utils.configuration import IGNORE_KEYWORDS
from utils.files_handler import parse_file_to_ast

def test1():
    test_path="F:\\DLFs_dataset\\paddle\\Paddle-2.4.2\\python\\paddle\\fluid\\tests\\unittests\\test_uniform_random_bf16_op.py"
    myast = parse_file_to_ast(test_path)
    class_path="F:\\python_workplace\\check_utils\\utils\\pybind11\\Paddle\\Paddle-2.4.2\\c_py_class_table.csv"
    pybind_fun_path="F:\\python_workplace\\check_utils\\utils\\pybind11\\Paddle\\Paddle-2.4.2\\c_py_fun_table.csv"
    pyc_fun_path="F:\\python_workplace\\check_utils\\utils\\python_c\\Paddle\\Paddle-2.4.2\\c_py_fun_table.csv"
    class_tables=pd.read_csv(class_path).values
    class_names=class_tables[:,-1:].flatten()
    pybind_fun_tables=pd.read_csv(pybind_fun_path).values
    pybind_fun_names=pybind_fun_tables[:,2:3].flatten()
    pyc_fun_tables=pd.read_csv(pyc_fun_path).values
    pyc_fun_names=pyc_fun_tables[:,0:1].flatten()
    class_asnames = dict()
    pybind_fun_asnames = dict()
    pyc_fun_asnames = dict()
    class_id=set()
    pybind_fun_id=set()
    pyc_fun_id=set()
    communication_files=set()
    for item in myast.imports:
        name = item[0]
        asname = item[1]
        if name in IGNORE_KEYWORDS:
            continue
        if isinstance(asname, str):
            if len(class_names) > 0 and name in class_names:
                class_asnames[asname] = name
            if len(pybind_fun_names) > 0 and name in pybind_fun_names:
                pybind_fun_asnames[asname] = name
            if len(pyc_fun_names) > 0 and name in pyc_fun_names:
                pyc_fun_asnames[asname] = name
    sum_calls=0
    for com_item in myast.component:
        com = com_item[0]
        if com in IGNORE_KEYWORDS:
            continue
        sum_calls += classify_excessive_communication_component(com, class_names, class_asnames,class_id)
        sum_calls += classify_excessive_communication_component(com, pybind_fun_names,pybind_fun_asnames,pybind_fun_id)
        sum_calls += classify_excessive_communication_component(com, pyc_fun_names, pyc_fun_asnames,pyc_fun_id)
    for call_item in myast.call_names:
        com = call_item[0]
        sum_calls += classify_excessive_communication_component(com, class_names, class_asnames,class_id)
        sum_calls += classify_excessive_communication_component(com, pybind_fun_names,pybind_fun_asnames,pybind_fun_id)
        sum_calls += classify_excessive_communication_component(com, pyc_fun_names, pyc_fun_asnames,pyc_fun_id)
    print(sum_calls)
    for c_id in class_id:
        print(class_names[c_id])
        communication_files.add(class_tables[c_id][0])
    for fun_id in pybind_fun_id:
        print(pybind_fun_names[fun_id])
        communication_files.add(pybind_fun_tables[fun_id][0])
    for fun_id in pyc_fun_id:
        print(pyc_fun_names[fun_id])
        communication_files.add(pyc_fun_tables[fun_id][-1])
    # if sum_calls>20:
    #     print("all calls is excessive")
    for item in communication_files:
        print(item)

def classify_excessive_communication_component(com, cf_names, cf_asnames,cf_id):
    call_count=0
    if len(cf_names) > 0 and (com in cf_names or com in cf_asnames.keys()):
        print("-------------"+com+"-----------------")
        call_count += 1
        if com in cf_names:
            id = cf_names.index(com)
        else:
            id = cf_names.index(cf_asnames.get(com))
        cf_id.add(id)

    return call_count

if __name__ == '__main__':
    test1()