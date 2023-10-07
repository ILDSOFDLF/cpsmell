import os.path

import pandas as pd

from utils.version_management import DFLs_version, Frame_names

code_smell_results_files = ['large_class.csv',
                            'excessive_interLanguage_communication.csv',
                            'long_lambda_function.csv',
                            'not_using_relative_path.csv',
                            'lack_of_rigorous_error_check.csv',
                            'unused_entity.csv',
                            'unused_module.csv',
                            'lack_of_static_declaration.csv']


def print_delete_smells(smell_file1, smell_file2, start_id, first_frame=None, end_frame=None):
    smell_list1 = smell_file1[:, start_id].flatten()
    smell_list2 = smell_file2[:, start_id].flatten()
    if first_frame is not None:
        path_list1 = []
        path_list2 = []
        for smell_path in smell_list1:
            new_smell_path = smell_path[smell_path.find(first_frame) + len(first_frame) + 1:]
            path_list1.append(new_smell_path)
        for smell_path in smell_list2:
            new_smell_path = smell_path[smell_path.find(end_frame) + len(end_frame) + 1:]
            path_list2.append(new_smell_path)
        smell_list1 = path_list1
        smell_list2 = path_list2
    delete_smells = []
    for index in range(len(smell_list1)):
        smell_name = smell_list1[index]
        if smell_name not in smell_list2:
            delete_smells.append(smell_file1[index])
    for item in delete_smells:
        print(item)


if __name__ == '__main__':
    for i in range(len(DFLs_version)):

        print("==========================", Frame_names[i], "============================")
        first_frame = DFLs_version[i][0][DFLs_version[i][0].rfind("\\") + 1:]
        end_frame = DFLs_version[i][-1][DFLs_version[i][-1].rfind("\\") + 1:]
        for smell_file_name in code_smell_results_files:
            print("--------------", smell_file_name, "-----------------")
            first_path = os.path.join("detection_results", Frame_names[i], first_frame, smell_file_name)
            end_path = os.path.join("detection_results", Frame_names[i], end_frame, smell_file_name)

            smell_file1 = pd.read_csv(first_path).values
            smell_file2 = pd.read_csv(end_path).values
            if smell_file_name == 'large_class.csv':
                print_delete_smells(smell_file1, smell_file2, 1)
            elif smell_file_name == 'excessive_interLanguage_communication.csv':
                print_delete_smells(smell_file1, smell_file2, 0, first_frame, end_frame)
            elif smell_file_name == 'long_lambda_function.csv':
                print_delete_smells(smell_file1, smell_file2, 2)
            elif smell_file_name == 'not_using_relative_path.csv':
                print_delete_smells(smell_file1, smell_file2, 0, first_frame, end_frame)
            elif smell_file_name == 'lack_of_rigorous_error_check.csv':
                print_delete_smells(smell_file1, smell_file2, 0, first_frame, end_frame)
            elif smell_file_name == 'unused_entity.csv':
                print_delete_smells(smell_file1, smell_file2, 2)
            elif smell_file_name == 'unused_module.csv':
                print_delete_smells(smell_file1, smell_file2, 1)
            elif smell_file_name == 'lack_of_static_declaration.csv':
                print_delete_smells(smell_file1, smell_file2, 1)
