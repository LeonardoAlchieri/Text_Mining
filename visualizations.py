import matplotlib.pyplot as plt
import pandas as pd
from yaml import safe_load

def main():
    print("\n\t\t VISULIZATION EVALUATIONS\t\t\n")
    print('[INFO] Loading configuration')
    with open("./config.yml", 'r') as file:
        config_var = safe_load(file)["main"]

    print("[INFO] Loading evaluation averages and errors.")
    with open(config_var["output_folder"]+"/avgs.csv", 'r') as file:
        avgs = pd.read_csv(file, index_col = 0)
    with open(config_var["output_folder"]+"/ses.csv", 'r') as file:
        ses = pd.read_csv(file, index_col = 0)
    print("[INFO] Dropping Rouge L (summary level).")
    print("[COMMENT] This is done since the results are inconclusive and may be skewed (see report).")
    avgs = avgs.drop(index = 'Rouge_L_summary_level', axis = 0)
    ses = ses.drop(index = 'Rouge_L_summary_level', axis = 0)
    print("[INFO] Making errorplot.")
    FONTSIZE = 13
    plt.figure(figsize=(20, 15))
    plt.subplot(153)
    for i, col in enumerate(avgs):
        plt.errorbar(x=avgs.index,
                     y=avgs[col],
                     yerr=ses[col],
                     label=col,
                     elinewidth=40,
                     linestyle='none',
                     markersize=10,
                     marker='.',
                     color=config_var["color_vis"][i],
                     ecolor=config_var["color_vis"][i]+"BF")

    plt.legend(loc='best')
    # plt.ylim((0,max(avgs.max(axis=1))))
    plt.tick_params(labelsize=FONTSIZE)
    plt.margins(x=0.5)
    plt.grid(True)
    locs, labels = plt.xticks()
    plt.setp(labels, rotation=40)
    # Non posso mettere il titolo, perché mi viene tagliato
    plt.title("Evaluations on "+config_var["name"], pad=10, fontsize=17)
    plt.savefig(config_var['vis_folder']+"/error_plot.pdf")
    plt.close()
    print("[INFO] Program completed.")



if __name__ == "__main__":
    main()
