# %%time
from annoy import AnnoyIndex
from scipy.spatial import KDTree
import os
import pickle

# %%time
def build(N, D):
    dataset = [None] * N
    for i in range(N):
        dataset[i] = [((i % 9997 - d) + (i * d - d)) % 9999 for d in range(D)]
        dataset[i] = tuple(dataset[i])
    return dataset

with open("input.txt",'r') as fp:
    method_of_search,vector=fp.readlines()
    vector=[int(i) for i in vector.split(" ")]
    method_of_search=method_of_search.strip()

PATH_Annoy='annoy.ann'
PATH_KDT="KDT.ann"

ann=AnnoyIndex(3,"euclidean")

res=[]
if method_of_search == 'annoy':
    if os.path.exists(PATH_Annoy):
        ann.load(PATH_Annoy)
        # print("load annoy")
    else:
        DATASET = build(100000, 3)
        # print("build annoy")
        for i,v in enumerate(DATASET):
            ann.add_item(i,list(v))
        ann.build(n_trees=5,n_jobs=-1)
        ann.save(PATH_Annoy)
    res=ann.get_nns_by_vector(vector,1)
else: #elif "kdtree" in method_of_search.lower():
    if os.path.exists(PATH_KDT):
        # print("load kdtree")
        kdtree=pickle.load(open(PATH_KDT,'rb'))
    else:
        # print("build kdtree")
        DATASET = build(100000, 3)
        kdtree=KDTree(DATASET)
        pickle.dump(kdtree,open(PATH_KDT,'wb'))
    res=kdtree.query([vector],k=1)[1]

with open("output.txt",'w') as fp:
    for i in res:
        fp.write(str(i))
