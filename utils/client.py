import os
from datetime import datetime

from utils.codesmell_detection import CodeSmell
from utils.files_handler import write_files
from utils.pybind11.check_api import MyPybind
from utils.python_c.check_api import Utils


def find_api(path,frame_name, file_name):
    c_files_path = os.path.join("c_files", frame_name)
    py_files_path = os.path.join("py_files", frame_name)
    print(path)
    print(c_files_path)
    print(py_files_path)
    if not os.path.exists(c_files_path):
        os.makedirs(c_files_path)
    if not os.path.exists(py_files_path):
        os.makedirs(py_files_path)
    write_files(path,frame_name,file_name)
    pybind11_file_path = os.path.join('pybind11',frame_name, file_name)
    if not os.path.exists(pybind11_file_path):
        os.makedirs(pybind11_file_path)
    pybind = MyPybind(frame_name, file_name,front_flag=True)
    pybind.get_module()
    if len(pybind.modules) == 0:
        print("the module is null")
    pybind.check_import()
    pybind.get_c_py_class()
    pybind.get_c_py_function()
    pybind.data_augmentation()
    #python/c api
    pybindc_file_path = os.path.join('python_c',frame_name, file_name)
    if not os.path.exists(pybindc_file_path):
        os.makedirs(pybindc_file_path)
    u = Utils(frame_name, file_name,front_flag=True)
    u.getPyMethodDef()
    u.getPyModuleDef()

def detect_smells(frame_name, file_name):
    start_time = datetime.datetime.now()
    print("start_time:", start_time)
    dest_path = os.path.join("detection_results", frame_name, file_name)
    if not os.path.exists(dest_path):
        os.makedirs(dest_path)
    codesmell = CodeSmell(frame_name, file_name)
    codesmell.detect_unused_module()
    codesmell.detect_long_lambda_function_for_inter_language_binding()
    codesmell.detect_large_inter_language_binding_class()
    codesmell.detect_unused_entity()
    codesmell.detect_excessive_interLanguage_communication()
    codesmell.lack_of_rigorous_error_check()
    codesmell.detect_lack_of_static_declaration()
    codesmell.detect_not_using_relative_path()
    end_time = datetime.datetime.now()
    print("end_time:", end_time)
    print("all runtime:", end_time.timestamp() - start_time.timestamp())