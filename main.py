# import sys
import numpy as np
import time
import csv

# calculator MaxCapRoadMatrix max tonage matrix for cluster
def calMaxCapRoadMatrix(maxCapRoadMatrix, customersList):
    newMatrix = list()
    for i in customersList:
        listMaxCapRoad = list()
        for j in customersList:
            if i == j:
                listMaxCapRoad.append(0)
            else:
                listMaxCapRoad.append(maxCapRoadMatrix[i, j])
        newMatrix.append(listMaxCapRoad)
    return np.array(newMatrix)


# Update the index corresponding to the original customer list
def updateIndexCustomer(nodes, customersList):
    customersList = np.array(customersList)
    customer = customersList[nodes]
    return customer


def calNewCostMaxcapDemand(costMatrix, maxCapRoadMatrix, demand, rule):

    rule_check = list()
    rule_check_ogn = list()
    for i in rule:
        rule_check.extend(i[1:])
        rule_check_ogn.extend(i)

    demand_idxnew = list()
    demand_new = list()
    for i in range(0, len(demand)):
        if i in rule_check:
            continue
        else:
            demand_idxnew.append(i)
            demand_new.append(demand[i])

    costMatrixNew = list()
    for i in demand_idxnew:
        listCost = list()
        for j in demand_idxnew:
            if i == j:
                listCost.append(0)
            elif i in rule_check_ogn:
                for k in rule:
                    if i in k:
                        # t = k[-1]
                        listCost.append(costMatrix[k[-1], j])
                        break
            else:
                listCost.append(costMatrix[i, j])
        costMatrixNew.append(listCost)

    maxCapNew = list()
    for i in demand_idxnew:
        listCap = list()
        for j in demand_idxnew:
            if i in rule_check_ogn:
                for k in rule:
                    if i in k:
                        # t = k[-1]
                        listCap.append(maxCapRoadMatrix[k[-1], j])
                        break
            else:
                listCap.append(maxCapRoadMatrix[i, j])
        maxCapNew.append(listCap)
    del listCap, listCost, rule_check

    return np.array(costMatrixNew), np.array(maxCapNew), np.array(demand_new), np.array(demand_idxnew), rule_check_ogn


def calCost(costMatrix, rout):
    cost = 0
    for i in range(0, len(rout)-1):
        cost += costMatrix[rout[i]][rout[i+1]]
    return cost


def calCostMatrixForRule(costMatrix, rule):
    costMatrixNew = list()
    for i in rule:
        listCost = list()
        for j in rule:
            if i == j:
                listCost.append(0)
            else:
                listCost.append(costMatrix[i, j])
        costMatrixNew.append(listCost)
    return np.array(costMatrixNew)


def main():
    from TabuSearch import TSP
    from savingVRP import saving, updateCost
    from dbscan_with_pre_com import cluster

    # costMatrix, maxCapRoadMatrix is numpy array
    costMatrix = np.genfromtxt('../data_01_150621/data_01_150621/matrix_cost.csv', delimiter=',')
    maxCapRoadMatrix = np.genfromtxt('../data_01_150621/data_01_150621/matrix_max_tonnage.csv', delimiter=',')
    demand = np.genfromtxt('../data_01_150621/data_01_150621/demand.csv', delimiter=',')
    vehicle = np.genfromtxt('../data_01_150621/data_01_150621/vehicle.csv', delimiter=',')
    with open('../data_01_150621/data_01_150621/rule.csv', newline='') as f:
        reader = csv.reader(f)
        rule_str = list(reader)

    startime = time.time()
    eps = 18000
    minSample = 3
    timeRunTabu = 10
    totalCost = 0
    goBackD = False

    # convert rule type string to int and routing for each rule
    rule = list()
    for i in rule_str:
        # remove item = ''
        try:
            index = i.index('')
            i = i[:index]
        except:
            pass

        # convert string to int
        v = list(map(int, i))
        if len(v) > 2:
            # calculate cost matrix for rule
            costMatrixOfRule = calCostMatrixForRule(costMatrix, v)
            # routing (time run tabu search is lenght of rule)
            routing_rule = TSP.find_way(costMatrixOfRule, len(v)/2)[0]
            # update index for rule and update routed rule
            rule.append(list(np.array(v)[routing_rule]))
        else:
            rule.append(v)

        # if you don't want to route, remove the hash sign in next line and comment(#) function if, else above
        # rule.append(v)

    # calculator costMatrixNew, maxCapRoadNew, demandNew, index of demandNew follow rules
    costMatrixNew, maxCapNew, demand_new, demand_idxnew, rule_check_ogn = calNewCostMaxcapDemand(costMatrix, maxCapRoadMatrix, demand, rule)

    # cost value to prohibit the vehicle from crossing an overloaded road
    costRoadErr = np.max(costMatrixNew)*len(costMatrixNew)

    # clustering
    cluster, noise = cluster(costMatrixNew, eps, minSample)

    for c in cluster:
        print("Cluster:", demand_idxnew[c[0]])

        # max tonage matrix for each cluster
        maxCapRoadMatrixCustomers = calMaxCapRoadMatrix(maxCapNew, c[0])

        # Saving
        route, vehicle, vehicleFixCustomer = saving(c[1], demand_new[c[0]], vehicle, maxCapRoadMatrixCustomers, c[0])

        print('route: ')
        for key, value in route.items():
            # create matrix for each route
            costMatrixForRoute = updateCost(costMatrixNew, maxCapNew, value['nodes'], value['Cap'], costRoadErr)

            # tabu search
            result = TSP.find_way(costMatrixForRoute, timeRunTabu, go_back=goBackD)
            result = list(result)
            # totalCost += result[1]

            # Update index for customers (fl demand new without delivery of pick up)
            idxCustomer = demand_idxnew[value['nodes']]

            # Update index for customers follow demand original
            shortestPath = list(updateIndexCustomer(result[0], idxCustomer))
            shortestPathOrigin = shortestPath.copy()

            check_err_cost = result[1]

            # add rules to the route
            for i in range(0, len(shortestPath)):
                if shortestPath[i] in rule_check_ogn:
                    for j in rule:
                        if shortestPath[i] in j:
                            shortestPath[i] = j
                            result[1] += calCost(costMatrix, j)
                            break

            totalCost += result[1]
            value['totalD'] = demand_new[value['nodes']].sum()
            value['nodes'] = idxCustomer
            print(f'{" " * 8}{key}:{value}')

            print(f'{" " * 8}The shortest path without rules: ', shortestPathOrigin)
            print(f'{" " * 8}The shortest path: ', shortestPath)
            print(f'{" " * 8}Total cost: ', result[1])

            # If the way goes wrong then print costMatrix of route
            if check_err_cost >= costRoadErr:
                matrixRoadErr = costMatrixForRoute.tolist()
                print(" " * 8, matrixRoadErr)
            print(f'{" " * 8}--------------------------')

        print(f'\nThe remaining vehicles: {vehicle}\nThe remaining customers: {vehicleFixCustomer}')
        print("===========================")

    print("List of noise points: ", demand_idxnew[noise])
    print("Total Cost: ", totalCost)
    print("Run time: ", time.time() - startime)


if __name__ == '__main__':
    main()
