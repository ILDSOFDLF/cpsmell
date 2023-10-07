import os

import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
from utils.metric import smell_alias
from utils.smell_verification import code_smell_results_files
from utils.version_management import DFLs_version, Frame_names


def analyse():
    for i in range(len(DFLs_version)):
        results = []
        for path in DFLs_version[i]:
            frame_version = path[path.rfind("\\") + 1:]
            results_line = []
            for result_file_name in code_smell_results_files:

                smell_results_paths = os.path.join("detection_results", Frame_names[i], frame_version, result_file_name)
                with open(smell_results_paths) as f:
                    smell_count = len(f.readlines()) - 1
                    if result_file_name == 'unused_entity.csv':
                        smell_count = smell_count - 1
                    results_line.append(smell_count)
            results.append(results_line)
        pd.DataFrame(results, columns=['LILBC', 'EILC', 'LLFFILB', 'NURP', 'LOREC', 'UE', 'UM', 'LOSD']). \
            to_csv(os.path.join("version_evolution_results", Frame_names[i] + ".csv"), index=False)


def drawing():
    x_labels = [1, 2, 3, 4, 5, 6, 7, 8, 9, 10]
    results_names=['TensorFlow','PyTorch','Mindspore','Paddle','Chainer']
    for index,frame_name in enumerate(Frame_names):
        path=os.path.join("version_evolution_results",frame_name+'.csv')
        smell_data=pd.read_csv(path).values
        plt.figure(figsize=(10, 6))
        for i in range(8):
            y_labels=[smell_data[j][i] for j in range(10)]
            plt.plot(x_labels,y_labels,label=smell_alias[i])
        # add title and label
        plt.title(results_names[index])
        plt.xlabel('Version')
        plt.ylabel('Number')

        ax = plt.gca()
        ax.spines['top'].set_visible(False)
        ax.spines['right'].set_visible(False)
        if index==2:
            ax.set_yticks(np.arange(0, 19, 2))
        plt.legend()
        plt.savefig(os.path.join('version_evolution_results',results_names[index]+'.pdf'),dpi=300)
        plt.show()


if __name__ == '__main__':
    drawing()