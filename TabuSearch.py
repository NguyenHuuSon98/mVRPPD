import random
import time
import numpy as np


# TabuSearch for each router
class TSP:

    @staticmethod
    def find_way(matrix, time_to_run, go_back=False):
        # init
        TSP.tabu_size = len(matrix) ** 2
        deadline = time.time() + time_to_run
        n = len(matrix)
        permutation = [0] + random.sample(range(1, n), n - 1)
        best = permutation
        tabu_list = [permutation]
        cost_best = TSP.calculate_route(best, n, matrix, go_back)
        cout = 0
        loop_number = 10000

        while time.time() < deadline:
            neighbours = list(TSP.get_neighbours(permutation))
            best_neighbour = neighbours[0]
            for perm in neighbours:
                if perm not in tabu_list and TSP.calculate_route(perm, n, matrix, go_back) < TSP.calculate_route(best_neighbour, n, matrix, go_back):
                    best_neighbour = perm
            # update to tabu_list
            permutation = best_neighbour
            tabu_list.append(best_neighbour)
            if TSP.calculate_route(best, n, matrix, go_back) > TSP.calculate_route(best_neighbour, n, matrix, go_back):
                best = best_neighbour

            if len(tabu_list) == TSP.tabu_size:
                tabu_list.__delitem__(0)

            # check len(loop)
            cost_check = TSP.calculate_route(best_neighbour, n, matrix, go_back)
            if cost_best > cost_check:
                cout = 0
                cost_best = cost_check
            else:
                cout += 1

            # init new permutation after loop_number time if solution isn't better
            if cout == loop_number:
                cout = 0
                permutation = [0] + random.sample(range(1, n), n - 1)
                tabu_list = [permutation]

        return np.array(best), TSP.calculate_route(best, n, matrix, go_back)

    # Using tabu to search new neighbours
    @staticmethod
    def get_neighbours(permutation):
        for i in range(1, len(permutation) - 1):
            result = []
            j = 0
            while j < len(permutation):
                if i == j:
                    result += [permutation[j + 1], permutation[j]]
                    j += 2

                if j < len(permutation):
                    result.append(permutation[j])
                j += 1
            yield result

    # calculate total cost in router
    @staticmethod
    def calculate_route(permutation, n, matrix, go_back):
        result = 0
        for i in range(1, n):
            result += matrix[permutation[i - 1]][permutation[i]]

        # if you want the vehicle back to depot, remove the hash sign in next line

        # if value go_back = true then vehicle back to depot
        if go_back:
            result += matrix[permutation[n - 1]][0]

        return result

