from sklearn.cluster import DBSCAN
import numpy as np

# blobs, labels = make_blobs(n_samples=50, n_features=10)
# distance_matrix = pairwise_distances(blobs)
# distance_matrix = pd.read_csv('../data/matrix_cost_260221.csv', header=None)
# distance_matrix = [[0, 12, 1000, 5, 8], [12, 0, 14, 1000, 18], [1000, 14, 0, 6, 19], [5, 1000, 6, 0, 2], [8, 18, 19, 2, 0]]


def cluster(distance_matrix, Eps, Min_samples):
    cluster_list = []
    distance_matrix = np.array(distance_matrix)

    # remove depot, just cluster customers
    distance_matrix_1 = distance_matrix[1:, 1:]
    # The current implementation uses ball trees and kd-trees to determine the neighborhood of points, which avoids calculating the full distance matrix. The possibility to use custom metrics is retained; for details, see NearestNeighbors.
    # Can use metric='precomputed' if it is the Cost_Matrix, not Lat-long
    clustering = DBSCAN(eps=Eps, min_samples=Min_samples, metric='precomputed')

    # This is new Solution, the Upgrade of DBSCAN, but the function error if input metric is pre-computed; and available just in Python3
    # For more information, read https://hdbscan.readthedocs.io/en/latest/basic_hdbscan.html
    # clustering = hdbscan.HDBSCAN(algorithm='best', alpha=1.0, approx_min_span_tree=True, gen_min_span_tree=False, leaf_size=40, metric='euclidean', min_cluster_size=5, min_samples=3, p=None)

    clustering.fit(distance_matrix_1)

    # print(clustering.labels_)
    labels = clustering.labels_
    n_clusters_ = len(set(labels)) - (1 if -1 in labels else 0)
    # n_noise = list(labels).count(-1)

    noise_list = []
    for idx_noise in range(len(labels)):
        if labels[idx_noise] == -1:
            noise_list.append(idx_noise+1)

    # Return each Cluster and index of points in that Cluster
    for i in range(0, n_clusters_):
        tmp = []
        for node in range(0, len(clustering.labels_)):
            if clustering.labels_[node] == i:
                tmp.append(node+1)
        tmp.insert(0, 0)
        array = []
        for x in tmp:
            for y in tmp:
                array.append(distance_matrix[x, y])
        array = np.array(array)
        # print(array)
        dimen = len(tmp)
        # print(dimen)
        matrix_new = array.reshape(dimen, dimen)

        cluster_list.append([tmp, matrix_new])
    return cluster_list, noise_list

# How to use Cluster function:
# c = cluster(distance_matrix, 300, 2)
# for matrix in c:
#     print(matrix)
