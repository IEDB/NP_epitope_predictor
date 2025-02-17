import os
import matplotlib.pyplot as plt
import matplotlib.cm as cm
import pandas as pd
import numpy as np

plt.rcParams.update({'font.size': "14"}) #bigger text fro phd

###########################
#Dataset choice
###########################

data_storage = os.path.join('benchmark_data')

data_to_use = {
'FP_CT_R3_MN':'RF',
# 'FP_CT_R3_MR':'Dummy RF',
# 'FP_CT_R3_MN_NN':'NN',
# 'FP_CT_R3_MN_KNN':'KNN',
}

###########################
#Open Sim Clf
###########################

sim_dict = {}
for file in os.listdir(os.path.join(data_storage,'sim_clf')):
	df = pd.read_csv(os.path.join(os.path.join(data_storage,'sim_clf'), file))
	sim_dict[file.strip('.csv')] = df

cell_types = {'b_cell':'B cell','t_cell':'T cell'}

#get some colors for the plot
colors = {}
c_choice = cm.rainbow(np.linspace(0, 1, len(data_to_use)))
for index, data_name in enumerate(data_to_use):
    colors[data_name] = c_choice[index]

fig1, axs1 = plt.subplots(4,2,figsize = (8.27,11.69))
# fig2, axs2 = plt.subplots(4,2,figsize = (8.27,11.69))
axis = axs1.reshape(-1)
# axis2 = axs2.reshape(-1)

base_range = np.around(np.geomspace(1, 2048, num=12)).astype(int) #the reange for all clf even though they might not go that far

#locate all benchmark files and store cluster/cell type
for folder in os.listdir(data_storage):
    if folder in data_to_use:
        folder_path = os.path.join(data_storage, folder)
        for sub_folder in os.listdir(folder_path):
            if sub_folder in cell_types: 
                cell_type = sub_folder
                sub_folder_path = os.path.join(data_storage, folder, sub_folder)
                for benchmark_file in os.listdir(sub_folder_path):
                    cluster = int(benchmark_file.replace('.csv',''))

                    # print(folder)
                    # print(sub_folder)
                    # print(benchmark_file)
                    # print(cell_type)
                    # print(cluster)
                    benchmark_file_path = os.path.join(data_storage, folder, sub_folder, benchmark_file)
                    df = pd.read_csv(benchmark_file_path, index_col=0)

                    # print(df['mean'])
                    # exit()

                    label_ml = "{0} ({1})".format(data_to_use[folder], cell_types[cell_type])
                    label_sim = "{0} ({1})".format('Similarity Classifier', cell_types[cell_type])
                    #plot

                    if cell_type == 'b_cell':

                        color = 'blue'
                        # axis = axis1
                    if cell_type == 't_cell':
                        color = "orange"
                        # axis = axis2

                    # color = colors[folder]


                    df['mean'].plot(yerr = df['err'], ax = axis[cluster], label=label_ml, color = color)

                    #axis properties    
                    axis[cluster].set_xscale('log', basex=2)
                    axis[cluster].set_xticks(base_range)
                    axis[cluster].set_xticklabels(base_range, rotation=90)
                    
                    axis[cluster].set_xlabel("Features (chi2)")
                    axis[cluster].set_ylabel("ROC-AUC") 
                    
                    # axis[index].axhline(y=sim_data_storage_b[index], ls = "--", color = "blue", label = 'Sim (B cell)')
                    
                    sim_df = sim_dict[cell_type]
                    sim_df = sim_df.set_index('Cluster')
                    # print(sim_df)
                    y = sim_df.loc[cluster,'AUC']
                    
                    print(y)

                    # y = sim_dict[cell_type]
                    axis[cluster].axhline(y=y, ls = "--", color = color, label = label_sim)
                    
                    axis[cluster].set_title("Cluster {0}".format(cluster))

                    axis[cluster].set_ylim(0.4,1)

                    # axis[cluster].legend(loc = 'lower right', bbox_to_anchor=(1, 0))

# axis1[3].set_visible(False)
# axis2[3].set_visible(False)

axis[3].legend(*axis[2].get_legend_handles_labels(), loc='center', title="Legend")
axis[3].axis('off')

# axis2[3].legend(*axis2[2].get_legend_handles_labels(), loc='center')
# axis2[3].axis('off')

# axis1[2].legend(loc=(2, 0.5))
# axis2[2].legend(loc=(2, 0.5))

fig1.tight_layout()
# fig2.tight_layout()
fig1.savefig('AUC_vs_Features_RF_vs_Sim.pdf', bbox_inches = "tight")
# fig2.savefig('AUC_vs_Features_CLFs_t_cell.pdf', bbox_inches = "tight")
exit()

#############################
#Get max AUC score for each query
#############################

main_df = pd.DataFrame()
# main_df.set_index(['cell_type','cluster','data'], inplace=True)

#locate all benchmark files and store cluster/cell type
idx = 0
for folder in os.listdir(data_storage):
    if folder in data_to_use:
        folder_path = os.path.join(data_storage, folder)
        for sub_folder in os.listdir(folder_path):
            if sub_folder in cell_types: 
                cell_type = sub_folder
                sub_folder_path = os.path.join(data_storage, folder, sub_folder)
                for benchmark_file in os.listdir(sub_folder_path):
                    cluster = int(benchmark_file.replace('.csv',''))

                    print(folder)
                    print(sub_folder)
                    print(benchmark_file)
                    print(cell_type)
                    print(cluster)
                    benchmark_file_path = os.path.join(data_storage, folder, sub_folder, benchmark_file)
                    df = pd.read_csv(benchmark_file_path, index_col=0)

                    max_mean = df['mean'].max()
                    max_err = df.loc[df['mean'].idxmax(),'err']

                    main_df.loc[idx, 'max_mean'] = max_mean
                    main_df.loc[idx, 'max_err'] = max_err
                    main_df.loc[idx, 'cell_type'] = cell_types[cell_type]
                    main_df.loc[idx, 'cluster'] = cluster
                    main_df.loc[idx, 'data'] = data_to_use[folder] 

                    idx += 1


#mean for all cluster and cell_type

fig, ax = plt.subplots(1,1,figsize = (11,6))

mean_per_data = main_df.groupby('data').apply(lambda group: group['max_mean'].mean())

mean_per_data.plot.bar(ax = ax)

for p in ax.patches:
    ax.annotate(str(round(p.get_height(),2)), (p.get_x() * 1.005, p.get_height() * 1.005))

ax.set_ylabel('Mean AUC for all clusters and cell types')
ax.set_xlabel('Non Chiral (NC); Chiral (C), Radius (R)')
ax.set_ylim(0.45,1.05)

plt.savefig('Different_CLF_vs_AUC.png', bbox_inches = "tight")
# fig.tight_layout()
# plt.show()

#per cell type
# fig, axs = plt.subplots(1,2,figsize = (15,15))

# for idx, (index, cell_group) in enumerate(main_df.groupby('cell_type')):

# 	mean_per_data = cell_group.groupby('data').apply(lambda group: group['max_mean'].mean())

# 	ax = axs[idx]
# 	mean_per_data.plot.bar(ax = ax)

# 	for p in ax.patches:
# 	    ax.annotate(str(round(p.get_height(),2)), (p.get_x() * 1.005, p.get_height() * 1.005))

# plt.tight_layout()
# plt.show()