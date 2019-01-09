import pandas as pd
import numpy as np
import matplotlib
matplotlib.use('TkAgg')
import matplotlib.pyplot as plt

path = "records_larger.csv"

df = pd.read_csv(path)

node_groups = df.nodes.unique().tolist()
tie_groups = df.tie.unique().tolist()
influence_groups = df.influence.unique().tolist()
mean_groups = df.mean_.unique().tolist()
sd_groups = df.sd_.unique().tolist()
#make sure axis directions make sense
node_groups.sort(reverse=False)
tie_groups.sort(reverse=True)
influence_groups.sort(reverse=False)
mean_groups.sort(reverse=False)
sd_groups.sort(reverse=True)

_5D_data_store = np.zeros((len(node_groups), len(mean_groups), len(sd_groups), len(tie_groups), len(influence_groups)))

node_index =0
for nodes in node_groups:
    mean_index =0
    for mean in mean_groups:
        sd_index =0
        for sd in sd_groups:
            tie_index =0
            for tie in tie_groups:
                influence_index =0
                for influence in influence_groups:
                    df_select = df[
                                    (df["nodes"]==nodes) &
                                    (df["mean_"]==mean) &
                                    (df["sd_"]==sd) &
                                    (df["tie"]==tie) &
                                    (df["influence"]==influence)
                                    ]
                    mean_tie = df_select["10"].mean()
                    _5D_data_store[node_index][mean_index][sd_index][tie_index][influence_index] = mean_tie
                    influence_index += 1
                tie_index += 1
            sd_index += 1
        mean_index += 1
    node_index += 1

def plot_all():
    nrows = len(sd_groups)
    ncols = len(mean_groups)
    x_index_max = len(influence_groups)-1
    y_index_max = len(tie_groups)-1
    x_min = min(influence_groups)
    x_max = max(influence_groups)
    y_min = min(tie_groups)
    y_max = max(tie_groups)
    print((nrows, ncols))

    first_subplot = True
    node_index =0
    for nodes in node_groups:
        sd_index =0
        for sd in sd_groups:
            mean_index =0
            for mean in mean_groups:
                print("mean:{0}, sd{1}, index:{2}, mean_i:{3} sd_i:{4}".format(mean, sd, sd_index*ncols+mean_index+1, mean_index, sd_index))
                tie_influence_array = _5D_data_store[node_index][mean_index][sd_index]
                plt.subplot(nrows, ncols, sd_index*ncols+mean_index+1)
                plt.imshow(tie_influence_array, vmin=0, vmax=1.3, cmap='Greys_r')
                plt.axis("off")
                mean_index += 1
            sd_index += 1
        node_index += 1
        #Save
        path = "results/"+ str(nodes) + "plots.png"
        plt.savefig(path)
        plt.show()
        first_subplot = True

def single_plot():
    x_index_max = len(influence_groups)-1
    y_index_max = len(tie_groups)-1
    x_min = min(influence_groups)
    x_max = max(influence_groups)
    y_min = min(tie_groups)
    y_max = max(tie_groups)

    tie_influence_array = _5D_data_store[0][0][6]
    plt.imshow(tie_influence_array, vmin=0, vmax=1.3, cmap='Greys_r')
    plt.xticks([0, x_index_max], [x_min, x_max])
    plt.yticks([0, y_index_max], [y_max, y_min])
    plt.xlabel("Influence")
    plt.ylabel("Tie annoyance")

    path = "results/singlePlot.png"
    plt.savefig(path)
    plt.show()

def line_plot():
    df_select = df[
                    (df["nodes"]==500) &
                    (df["mean_"]==1) &
                    (df["sd_"]==1) &
                    (df["tie"]==0.8) &
                    (df["influence"]==0.5)
                    ]
    df_select = df_select.mean()
    time_series = df_select[["1", "2", "3", "4", "5", "6", "7", "8", "9", "10"]].values.tolist()
    print(time_series)
    a = [1, 1, 1, 1]
    for t in time_series:
        a.append(t)

    print(a)
    plt.plot(range(16)[1:-1], a, "k.-")
    plt.xlabel("Day")
    plt.ylabel("Proportion of population wearing ties")
    plt.show()

line_plot()
single_plot()
plot_all()

'''
plot layout:

^   ^
|   |
|   t
|   i
|   e
|   |
|    --influence----->
S   ^
D   |
|   t
|   i
|   e
|   |
|    --influence----->
|
|
------------------MEAN--CONNECTIONS------------>
'''
