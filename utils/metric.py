import os.path

import numpy as np
import pandas as pd

from utils.configuration import IGNORE_KEYWORDS
from utils.files_handler import read_py_files, parse_file_to_ast
from utils.smell_verification import code_smell_results_files
from utils.version_management import Frame_names, test_DFLs_version

smell_alias = ['LILBC', 'EILC', 'LLFFILB', 'NURP', 'LOREC', 'UE', 'UM', 'LOSD']


def get_smell_distribution():
    results_list1 = []
    results_list2 = []
    results_list3 = []
    cpy_files_list=pd.read_csv('inter_language_files.csv').values
    cpy_Nfile={}
    cpy_Ncodeline={}
    for cpy_item in cpy_files_list:
        cpy_Nfile[cpy_item[0]]=cpy_item[1]
        cpy_Ncodeline[cpy_item[0]]=cpy_item[2]
    for i in range(len(test_DFLs_version)):
        results_list1.append(['==================' + Frame_names[i] + '=================='])
        results_list2.append(['==================' + Frame_names[i] + '=================='])
        results_list3.append(['==================' + Frame_names[i] + '=================='])
        for path in test_DFLs_version[i]:
            frame_version = path[path.rfind("\\") + 1:]
            inter_Nfile=cpy_Nfile[frame_version]
            inter_Ncodelines=cpy_Ncodeline[frame_version]
            results_list1.append(['---------------' + frame_version + '---------------'])
            results_list2.append(['---------------' + frame_version + '---------------'])
            results_list3.append(['---------------' + frame_version + '---------------'])
            print("=============", frame_version, "=================")
            print("the number of files：", inter_Nfile)
            print("the number of code lines:", inter_Ncodelines)
            all_smell_files = set()
            all_Nsmell=0

            for k, results_file_name in enumerate(code_smell_results_files):
                results_file_path = os.path.join("detection_results", Frame_names[i], frame_version, results_file_name)
                results_file = pd.read_csv(results_file_path).values
                src_smell_files = results_file[:, 0].flatten()
                dest_smell_files = set()
                Nsmell=len(src_smell_files)
                if k==5:
                    Nsmell=Nsmell-1
                all_Nsmell+=Nsmell
                if k == 1:
                    dest_smell_files = get_EILC_code_files(Frame_names[i], frame_version)

                    for EILC_path in dest_smell_files:
                        if EILC_path not in all_smell_files:
                            all_smell_files.add(EILC_path)

                else:
                    for index, x in enumerate(src_smell_files):
                        if x=='path':
                            continue
                        if x not in src_smell_files[:index]:
                            dest_smell_files.add(x)
                        if x not in all_smell_files:
                            all_smell_files.add(x)

                smell_file_count=len(dest_smell_files)
                smell_file_proportion = smell_file_count / inter_Nfile
                smell_file_proportion = round(smell_file_proportion, 4)
                smell_code_lines_density = Nsmell*1000 / inter_Ncodelines
                smell_code_lines_density = round(smell_code_lines_density, 6)
                smell_density_each_file=round(Nsmell/inter_Nfile,4)
                results_list1.append(['the number of {} smell files:{}\tthe proportion of {} smell files:{}'
                                     .format(smell_alias[k], smell_file_count, smell_alias[k], smell_file_proportion)])
                results_list2.append(['the number of {} smell:{}\tthe density of {} KLOC:{}'
                                     .format(smell_alias[k], Nsmell, smell_alias[k], smell_code_lines_density)])
                results_list3.append(['Number of {} smell for each cross-language file:{}'.format(smell_alias[k],smell_density_each_file)])

            all_smell_file_proportion = len(all_smell_files) / inter_Nfile
            all_smell_file_proportion = round(all_smell_file_proportion, 4)
            all_smell_code_lines_density = all_Nsmell*1000 / inter_Ncodelines
            all_smell_code_lines_density = round(all_smell_code_lines_density, 6)
            all_smell_density_each_file=round(all_Nsmell/inter_Nfile,4)
            results_list1.append(['the number of all smell files:{}\tthe proportion of all smell files:{}'
                                 .format(len(all_smell_files),all_smell_file_proportion)])
            results_list2.append(['the number of all smell:{}\tthe density of all smell KLOC:{}'
                                 .format(all_Nsmell, all_smell_code_lines_density)])
            results_list3.append(['the number of all smell:{}\tthe smell density of files:{}'
                                 .format(all_Nsmell, all_smell_density_each_file)])
            results_list1.append([])
            results_list2.append([])
            results_list3.append([])
    pd.DataFrame(results_list1).to_csv("file_smell_proportion.csv", header=False, index=False)
    pd.DataFrame(results_list2).to_csv("KLOC_smell_density.csv", header=False, index=False)
    pd.DataFrame(results_list3).to_csv("file_smell_density.csv", header=False, index=False)


def get_EILC_code_files(frame_name, frame_version):
    visited_paths = []
    EILC_result_path = os.path.join("detection_results", frame_name, frame_version,
                                    "excessive_interLanguage_communication.csv")
    pybind_fun_path = os.path.join("pybind11", frame_name, frame_version, "c_py_fun_table.csv")
    pybind_class_path = os.path.join("pybind11", frame_name, frame_version, "c_py_class_table.csv")
    pyc_fun_path = os.path.join("python_c", frame_name, frame_version, "c_py_fun_table.csv")

    pybind_fun_tables = pd.read_csv(pybind_fun_path).values
    class_tables = pd.read_csv(pybind_class_path).values
    pyc_fun_tables = pd.read_csv(pyc_fun_path).values
    EILC_result = pd.read_csv(EILC_result_path).values
    class_names = []
    pybind_fun_names = []
    pyc_fun_names = []
    if len(class_tables) > 0:
        class_names = np.array(class_tables)[:, -1].flatten().tolist()
    if len(pybind_fun_tables) > 0:
        pybind_fun_names = np.array(pybind_fun_tables)[:, 2].flatten().tolist()
    if len(pyc_fun_tables) > 0:
        pyc_fun_names = np.array(pyc_fun_tables)[:, 0].flatten().tolist()

    for item in EILC_result:
        if item[0] not in visited_paths:
            visited_paths.append(item[0])
        myast = parse_file_to_ast(item[0])
        if isinstance(myast, bool) and not myast:
            continue
        class_asnames = dict()
        pybind_fun_asnames = dict()
        pyc_fun_asnames = dict()
        for import_item in myast.imports:
            name = import_item[0]
            asname = import_item[1]
            if name in IGNORE_KEYWORDS:
                continue
            if isinstance(asname, str):
                if len(class_names) > 0 and name in class_names:
                    class_asnames[asname] = name
                if len(pybind_fun_names) > 0 and name in pybind_fun_names:
                    pybind_fun_asnames[asname] = name
                if len(pyc_fun_names) > 0 and name in pyc_fun_names:
                    pyc_fun_asnames[asname] = name
            for com_item in myast.component:
                com = com_item[0]
                if com in IGNORE_KEYWORDS:
                    continue
                classify_metric_EILC(com, class_names, class_tables, visited_paths, class_asnames, 0)
                classify_metric_EILC(com, pybind_fun_names, pybind_fun_tables, visited_paths, pybind_fun_asnames, 0)
                classify_metric_EILC(com, pyc_fun_names, pyc_fun_tables, visited_paths, pyc_fun_asnames, -1)

            for call_item in myast.call_names:
                com = call_item[0]
                classify_metric_EILC(com, class_names, class_tables, visited_paths, class_asnames, 0)
                classify_metric_EILC(com, pybind_fun_names, pybind_fun_tables, visited_paths, pybind_fun_asnames, 0)
                classify_metric_EILC(com, pyc_fun_names, pyc_fun_tables, visited_paths, pyc_fun_asnames, -1)

    return visited_paths


def classify_metric_EILC(com, cf_names, cf_tables, visited_paths, cf_asnames, path_index):
    if len(cf_names) > 0 and (com in cf_names or com in cf_asnames.keys()):
        if com in cf_names:
            com_id = cf_names.index(com)
        else:
            com_id = cf_names.index(cf_asnames.get(com))
        cf_path = cf_tables[com_id][path_index]
        if cf_path not in visited_paths:
            visited_paths.append(cf_path)


def get_fixed_smells_ratio(frame_name, first_version, end_version, all_fixed_snell_results):
    all_fixed_snell_results.append(["=================" + frame_name + "================="])
    for smell_name in code_smell_results_files:
        all_fixed_snell_results.append(['---------------------' + smell_name + '---------------------'])
        first_version_smell_path = os.path.join(first_version, smell_name)
        end_version_smell_path = os.path.join(end_version, smell_name)
        if smell_name == 'large_class.csv':
            fixed_smell__ratio(all_fixed_snell_results, first_version_smell_path, end_version_smell_path, 1)
        elif smell_name == 'excessive_interLanguage_communication.csv':
            fixed_smell__ratio(all_fixed_snell_results, first_version_smell_path, end_version_smell_path, 0, True)
        elif smell_name == 'long_lambda_function.csv':
            fixed_smell__ratio(all_fixed_snell_results, first_version_smell_path, end_version_smell_path, 2)
        elif smell_name == 'not_using_relative_path.csv':
            fixed_smell__ratio(all_fixed_snell_results, first_version_smell_path, end_version_smell_path, 0, True)
        elif smell_name == 'lack_of_rigorous_error_check.csv':
            fixed_smell__ratio(all_fixed_snell_results, first_version_smell_path, end_version_smell_path, 0, True)
        elif smell_name == 'unused_entity.csv':
            fixed_smell__ratio(all_fixed_snell_results, first_version_smell_path, end_version_smell_path, 2)
        elif smell_name == 'unused_module.csv':
            fixed_smell__ratio(all_fixed_snell_results, first_version_smell_path, end_version_smell_path, 1)
        elif smell_name == 'lack_of_static_declaration.csv':
            fixed_smell__ratio(all_fixed_snell_results, first_version_smell_path, end_version_smell_path, 1)
    all_fixed_snell_results.append(['================================================'])


def fixed_smell__ratio(fixed_result, first_path, end_path, pos, isPath=False):
    first_result_file = pd.read_csv(first_path).values
    end_result_file = pd.read_csv(end_path).values
    first_content = set(first_result_file[:, pos])
    end_content = set(end_result_file[:, pos])
    first_temp = set()
    end_temp = set()
    if isPath:
        for first_item in first_content:
            first_temp.add(os.path.basename(first_item))
        for end_item in end_content:
            end_temp.add(os.path.basename(end_item))
        first_content = first_temp
        end_content = end_temp
    src_count = len(first_content)
    end_count = 0
    fixed_count = 0
    for item in first_content:
        if item not in end_content:
            fixed_count += 1
        else:
            end_count += 1
    fixed_result.append(["Original number of smells :%d" % src_count])
    fixed_result.append(["End number of of smells :%d" % end_count])
    if src_count == 0:
        fixed_result.append(["Fixed number of smells :0"])
    else:
        fixed_result.append(["Fixed number of smells %f" % round((fixed_count / src_count), 4)])
    return fixed_result


def get_number_of_smell():
    results = []
    for i in range(len(test_DFLs_version)):
        results.append(["===================" + Frame_names[i] + "====================="])
        for path in test_DFLs_version[i]:
            smell_sum = 0
            frame_version = path[path.rfind("\\") + 1:]
            results.append(["------------------------" + frame_version + "---------------------"])
            for result_file_name in code_smell_results_files:
                smell_results_paths = os.path.join("detection_results", Frame_names[i], frame_version, result_file_name)
                with open(smell_results_paths) as f:
                    smell_count = len(f.readlines()) - 1
                    if result_file_name=='unused_entity.csv':
                        smell_count=smell_count-1
                    smell_sum += smell_count
                    results.append([result_file_name + "————%d" % smell_count])
            results.append(["the number of all smell:%d" % smell_sum])
    pd.DataFrame(results).to_csv("number_of_smell.csv", header=False, index=False)


if __name__ == '__main__':
    get_smell_distribution()
    get_number_of_smell()
    all_fixed_smell_results = []
    for i in range(len(test_DFLs_version)):
        first_path = test_DFLs_version[i][0]
        end_path = test_DFLs_version[i][-1]
        frame_name = Frame_names[i]
        first_frame_version = first_path[first_path.rfind("\\") + 1:]
        end_frame_version = end_path[end_path.rfind("\\") + 1:]
        first_smells_path = os.path.join("detection_results", frame_name, first_frame_version)
        end_smells_path = os.path.join("detection_results", frame_name, end_frame_version)
        get_fixed_smells_ratio(frame_name, first_smells_path, end_smells_path, all_fixed_smell_results)
    pd.DataFrame(all_fixed_smell_results).to_csv("fixed_smell_results.csv", header=False, index=False)
