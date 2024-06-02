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
            all_count = 0
            for result_file_name in code_smell_results_files:
                smell_results_paths = os.path.join("detection_results", Frame_names[i], frame_version, result_file_name)
                with open(smell_results_paths) as f:
                    smell_count = len(f.readlines()) - 1
                    if result_file_name == 'unused_entity.csv':
                        smell_count = smell_count - 1
                    all_count += smell_count
                    results_line.append(smell_count)
            avg_count = all_count/8
            results_line.append(avg_count)
            results.append(results_line)
        pd.DataFrame(results, columns=['LILBC', 'EILC', 'LLF', 'NURP', 'LREC', 'UNE', 'UEM', 'LSD', 'AVG']). \
            to_csv(os.path.join("version_evolution_results", Frame_names[i] + ".csv"), index=False)


def drawing():
    x_labels = [1, 2, 3, 4, 5, 6, 7, 8, 9, 10]
    results_names=['(a) TensorFlow','(b) PyTorch','(e) MindSpore','(d) PaddlePaddle','(c) Chainer']
    marker_styles = ['o', '^', 's', 'D', 'v', '<', '>', '*']
    for index,frame_name in enumerate(Frame_names):
        path=os.path.join("version_evolution_results",frame_name+'.csv')
        smell_data=pd.read_csv(path).values
        plt.figure(figsize=(10, 8))
        legend_handles = []
        for i in range(9):
            y_labels=[smell_data[j][i] for j in range(10)]
            line_color = plt.plot(x_labels,y_labels,label=smell_alias[i],linewidth=2)[0].get_color()

            for x, y in zip(x_labels, y_labels):
                plt.scatter(x, y, s=120, color=line_color, marker=marker_styles[i])
            legend_handles.append(plt.Line2D([0], [0], color=line_color, linestyle='-', marker=marker_styles[i], markersize=20, label=smell_alias[i]))

        # add title and label
        # plt.title(results_names[index], fontsize=14)
        plt.ylabel('Number', fontsize=25)


        ax = plt.gca()
        ax.tick_params(axis='x', labelsize=30)
        ax.tick_params(axis='y', labelsize=30)
        plt.text(1, -0.15, 'Versions', ha='right', fontsize=25, transform=ax.transAxes)


        ax.spines['top'].set_visible(False)
        ax.spines['right'].set_visible(False)
        if index==2:
            ax.set_yticks(np.arange(0, 19, 2))
        plt.suptitle(results_names[index], fontsize=30, y=0.05)

        plt.subplots_adjust(bottom=0.15)
        plt.savefig(os.path.join('version_evolution_results',results_names[index]+'.png'),dpi=300)
        plt.show()

    fig_legend, ax_legend = plt.subplots(figsize=(6, 4))
    ax_legend.legend(handles=legend_handles, loc='center', ncol=2, fontsize=30)
    ax_legend.axis('off')  # 关闭坐标轴
    plt.savefig(os.path.join('version_evolution_results', 'legend.png'), dpi=300)
    plt.show()


if __name__ == '__main__':
    analyse()
    # drawing()