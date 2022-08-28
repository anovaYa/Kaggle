#https://github.com/miracl1e6/clustering/blob/b1f48adde2719702568808ebdd0f4f659423a78b/utils.py
#!/usr/bin/env python
# coding: utf-8

# # Video Game Sales
# data from more than 16,500 games.

# ## Importing Libraries

# In[3]:


import numpy as np
import pandas as pd
import seaborn as sns

import matplotlib.pyplot as plt
get_ipython().run_line_magic('matplotlib', 'inline')

import warnings 
warnings.filterwarnings('ignore')

RAND = 10


# ## Loading Data

# In[68]:


videoGameData = pd.read_csv('../input/vgsales.csv', parse_dates=['Year'])


# In[69]:


videoGameData.head()


# ### About Dataset
# This dataset contains a list of video games with sales greater than 100,000 copies. It was generated by a scrape of vgchartz.com.
# 
# Fields include
# 
# * Rank - Ranking of overall sales
# 
# * Name - The games name
# 
# * Platform - Platform of the games release (i.e. PC,PS4, etc.)
# 
# * Year - Year of the game's release
# 
# * Genre - Genre of the game
# 
# * Publisher - Publisher of the game
# 
# * NA_Sales - Sales in North America (in millions)
# 
# * EU_Sales - Sales in Europe (in millions)
# 
# * JP_Sales - Sales in Japan (in millions)
# 
# * Other_Sales - Sales in the rest of the world (in millions)
# 
# * Global_Sales - Total worldwide sales.
# 
# The script to scrape the data is available at https://github.com/GregorUT/vgchartzScrape.

# In[70]:


videoGameData.info()


# In[71]:


videoGameData.describe()


# In[72]:


videoGameData.describe(include='object')


# In[73]:


fig, ax = plt.subplots(2, 2, figsize=(15, 8))
sns.boxplot(videoGameData['NA_Sales'][videoGameData['NA_Sales']<10], palette='PRGn', ax = ax[0, 0])
sns.distplot(videoGameData['NA_Sales'][videoGameData['NA_Sales']<10], ax = ax[1, 0])
sns.boxplot(videoGameData['Global_Sales'][videoGameData['Global_Sales']<10], palette='PRGn', ax = ax[0, 1])
sns.distplot(videoGameData['Global_Sales'][videoGameData['Global_Sales']<10], ax = ax[1, 1])


# ## Data Preprocessing

# In[74]:


videoGameData.isnull().sum()


# In[75]:


videoGameData.dropna(inplace=True)


# In[76]:


videoGameData['Year'] = videoGameData['Year'].dt.to_period('Y')


# In[77]:


videoGameData = videoGameData.drop(videoGameData['Global_Sales'].idxmax())


# ### Categorical Data

# In[79]:


videoGameData['Genre'] = videoGameData['Genre'].astype('category')
videoGameData['Platform'] = videoGameData['Platform'].astype('category')
videoGameData['Publisher'] = videoGameData['Publisher'].astype('category')


# #### Add categorical columns 

# In[80]:


platformCatDict = dict( enumerate(videoGameData['Platform'].cat.categories ) )
genreCatDict = dict( enumerate(videoGameData['Genre'].cat.categories ) )


# In[81]:


# videoGameData['Genre_cat'] = videoGameData['Genre'].cat.codes.astype('int')
videoGameData['Platform_cat'] = videoGameData['Platform'].cat.codes.astype('int')
videoGameData['Publisher_cat'] = videoGameData['Publisher'].cat.codes.astype('int')


# #### Name id

# In[82]:


videoGameData['Name_id'] = videoGameData['Name'].astype('category')
nameIDDict = dict( enumerate(videoGameData['Name_id'].cat.categories ) )
videoGameData['Name_id'] = videoGameData['Name_id'].cat.codes.astype('int')
videoGameData.head()


# ## Data Exploration and Analysis

# In[83]:


videoGameData['Year'].value_counts()[:20].plot(kind='bar')
plt.xlabel('Year')
plt.ylabel('Count')


# In[84]:


plt.figure(figsize=(15, 5))
sns.countplot(videoGameData['Genre'])
plt.ylabel('Count')
plt.xlabel('Genre')


# In[85]:


plt.figure(figsize=(15, 5))
sns.countplot(videoGameData['Platform'])
plt.ylabel('Count')
plt.xlabel('Platform')


# In[86]:


plt.figure(figsize=(15, 5))
videoGameData.groupby(by=['Year'])['Global_Sales'].sum().plot(kind='bar')
plt.ylabel('Global sales')


# In[87]:


plt.figure(figsize=(15, 5))
videoGameData.groupby(by=['Platform'])['Global_Sales'].sum().plot(kind='bar')
plt.ylabel('Global sales')


# In[88]:


plt.figure(figsize=(15, 5))
videoGameData.groupby(by=['Genre'])['Global_Sales'].sum().plot(kind='bar')
plt.ylabel('Global sales')


# In[89]:


videoGameData['Publisher'].value_counts()[:25].plot(kind='bar')


# In[90]:


salesPerYear = videoGameData.loc[:, ['Year', 'NA_Sales', 'EU_Sales', 'JP_Sales', 'Other_Sales']].groupby(by =  'Year'  ).sum()
salesPerYear.plot(figsize=(15, 7))
plt.ylabel('Total Sales')


# ## Correlation Heatmap

# In[91]:


plt.figure(figsize=(15,10))
heatmap = sns.heatmap(videoGameData.corr(), cmap = "Blues", annot=True, linewidth=3)
heatmap.set_title('Correlation Heatmap', fontdict={'fontsize':12}, pad=12)


# ## Modeling

# In[92]:


dataLabels = pd.get_dummies(videoGameData, columns=['Genre'])
dataLabels['Year'] = dataLabels['Year'].astype('int')
dataLabels = dataLabels.drop(columns=['Name', 'Publisher', 'Platform'], axis=1)


# In[93]:


dataLabels.info()


# ### PCA (Principal Component Analysis)

# In[94]:


from sklearn.preprocessing import StandardScaler
from sklearn.decomposition import PCA

X_scaled = StandardScaler().fit_transform(dataLabels)

pca = PCA().fit(X_scaled)

plt.figure(figsize=(12, 5))
x = np.arange(1, len(pca.explained_variance_ratio_)+1, 1)
plt.plot(x, np.cumsum(pca.explained_variance_ratio_), marker='o', linestyle='--', color='b')
plt.axhline(y=0.9, color='r', linestyle='-')
plt.text(0.6, 0.85, '90% cut-off threshold', color = 'red', fontsize=12)
plt.grid(axis='x')

plt.xlabel('number of components')
plt.ylabel('cumulative explained variance');


# In[95]:


import plotly.express as px
pca = PCA(n_components=13).fit(X_scaled)

components = pca.fit_transform(X_scaled)
total_var = pca.explained_variance_ratio_.sum() * 100
n_components = len(pca.explained_variance_ratio_)

labels = {str(i): f"PC {i+1}" for i in range(n_components)}
labels['color'] = 'Median Price'
labels = {
    str(i): f"PC {i+1} ({var:.1f}%)"
    for i, var in enumerate(pca.explained_variance_ratio_ * 100)
}

fig = px.scatter_matrix(
    components,
    dimensions=range(n_components),
    labels=labels,
    title=f'Total Explained Variance: {total_var:.2f}%',
)
fig.update_traces(marker_size=1, diagonal_visible=False)

fig.update_layout(
    font=dict(size=5, color='black'),
    autosize=False,
    width=1000,
    height=1000,
)


# In[112]:


X_scaled = StandardScaler().fit_transform(dataLabels)

pca = PCA(n_components=0.9, random_state=RAND)
X_embedding_pca = pca.fit_transform(X_scaled)

pca_3 = PCA(n_components=13, random_state=RAND)
X_embedding_pca_3 = pca_3.fit_transform(X_scaled)

fig = px.scatter_3d(
    X_embedding_pca, x=3, y=7, z=12,
    labels={'color': 'species'}
)
fig.update_traces(marker_size=2)


# ### KMeans

# In[97]:


from sklearn.cluster import SpectralClustering, KMeans, AgglomerativeClustering
from sklearn.metrics import silhouette_score
from utils import plotting_object, plotting_kde_num, plot_clustering, plotting_num, plot_size, silhouette_plot
params_cluster = {
    'KMeans': {
        'random_state': RAND,
    },
    'SpectralClustering': {
        'random_state': RAND,
        'affinity': 'nearest_neighbors',
        'n_neighbors': 25,
        'n_jobs': -1
    },
    'AgglomerativeClustering': {
    }
}
dict_clusters_km = plot_clustering(data=dataLabels,
                                   data_scale=X_scaled,
                                   embedding=X_embedding_pca,
                                   kwargs=params_cluster['KMeans'],
                                   model=KMeans,
                                   type_train='embedding')


# In[98]:


videoGameData['Genre_cat'] = videoGameData['Genre'].cat.codes.astype('int')
videoGameData['Platform_cat'] = videoGameData['Platform'].cat.codes.astype('int')
videoGameData['Year'] = videoGameData['Year'].astype('int')
num_cols = [
    'Year',
    'NA_Sales',
    'EU_Sales',
    'JP_Sales',
    'Global_Sales',
    'Publisher_cat',
    'Genre_cat',
    'Platform_cat'
]


# In[107]:


plotting_kde_num(videoGameData, dict_clusters_km[6], num_cols)
plotting_num(videoGameData, dict_clusters_km[6], num_cols)


# In[110]:


fig = px.scatter_3d(
    X_embedding_pca, x=3, y=7, z=12,
    labels={'color': 'species'},
    color=dict_clusters_km[6]
)
fig.update_traces(marker_size=2)


# In[111]:


sns.scatterplot(X_embedding_pca[:,7], X_embedding_pca[:,12], c=dict_clusters_km[6])


# ## t-statistic

# In[114]:


videoGameDataClus = videoGameData.copy()


# In[115]:


videoGameDataClus['cluster'] = dict_clusters_km[6]


# In[117]:


clusterSdt = []
for i in set(dict_clusters_km[6]):
    clusterSdt.append(videoGameDataClus[videoGameDataClus['cluster'] == i]['Global_Sales'].std())
print('std:')
for c, n in enumerate(clusterSdt):
    print(f'cluster {c} - {n}')


# In[120]:


plt.figure(figsize=(20, 20))
sns.boxplot(x='cluster', y='Global_Sales', data=videoGameDataClus)


# In[139]:


fig, ax = plt.subplots(3, 2, figsize=(25, 20))
for i, ax in zip(set(dict_clusters_km[6]), ax.ravel()):
    plt.title(i)
    sns.countplot(videoGameDataClus[videoGameDataClus['cluster'] == i]['Genre'], ax = ax).set(title=f'cluster = {i}')

