import numpy as np
import time


# assign the most suitable vehicle to each customer
def fixCap(demand, capacity):
    capFixDemand = dict()
    for i in range(len(demand)):
        if i == 0:
            continue
        for j in capacity:
            if j >= demand[i]:
                capFixDemand[i] = j
                break
    return capFixDemand


# Sort the distance between each pair of customers (min->max)
def sortDistance(distance):
    distance = np.array(distance)
    distance = distance[1:, 1:]
    width, _ = distance.shape
    listDist = list()
    for i in range(width):
        for j in range(width):
            if i == j:
                pass
            else:
                listDist.append([i+1, j+1, distance[i, j]])

    listDist.sort(key=lambda x: int(x[2]))
    return listDist


# choose the most suitable car
def getCap(capacity, demand):
    vehicle = None
    for i in capacity:
        if demand <= i:
            vehicle = i
            break
    return vehicle


# removes elements equal to value in the array
def delValue(arr, value):
    arr = np.array(arr)
    index = None
    for i in range(len(arr)):
        if arr[i] == value:
            index = i
            break
    arr = np.delete(arr, index)
    return arr


# Vehicle updates for the routes
def updateRouter(router, capacity, demand):
    capacity = np.sort(capacity)
    while True:
        check = False
        for key, value in router.items():
            vehicle = getCap(capacity, demand[value['nodes']].sum())
            if vehicle is not None and vehicle < value['Cap']:
                capacity = np.append(capacity, value['Cap'])
                value['Cap'] = vehicle
                capacity = delValue(capacity, vehicle)
                capacity = np.sort(capacity)
                check = True
        if not check:
            break
    return router, capacity


# Check max tonage from customers to many customers (Used to check when adding 1 point to the route)
def pointToNodes(maxCapRoad, node1, node2, vehicle, nodeList):
    check = False
    for i in nodeList:
        if i == node1:
            continue
        if vehicle <= maxCapRoad[node2, i]:
            check = True

    for u in nodeList:
        for v in nodeList:
            if u == v or v == node1:
                continue
            if u == node1 or u == 0:
                break
            if maxCapRoad[v, u] < vehicle:
                check = False
    return check


# Check max tonage between 2 route (Used to check when connecting 2 routes)
def nodesToNodes(maxCapRoad, node1, node2, vehicle, nodeList1, nodeList2):
    nodeList = nodeList1.copy()
    nodeList.extend(nodeList2)
    check = True
    for i in nodeList:
        if i == node1 or i == node2:
            continue
        if maxCapRoad[node2, i] < vehicle:
            check = False

    for u in nodeList:
        for v in nodeList:
            if u == node1 or u == node2 or u == 0:
                break
            if u == v or (u == node1 and v == node2) or (u == node2 and v == node1):
                continue
            if maxCapRoad[v, u] < vehicle:
                check = False
    return check


# Update the index compared to the list of input customers for each route
def updateIndexCustomer(router, customersList):
    customersList = np.array(customersList)
    for key, value in router.items():
        customer = customersList[value['nodes']]
        value['nodes'] = customer
    return router


# Update index for vehicleFixCustomer
# Update the index compared to the list of input customers for customers who are not on any route
def updateIndexVehicleFixCustomer(vehicleFixCustomer, customersList):
    newVehicleFixCustomer = dict()
    for key, value in vehicleFixCustomer.items():
        for i in range(len(customersList)):
            if key == i:
                newVehicleFixCustomer[customersList[i]] = value
    return newVehicleFixCustomer


# s??? l?? tr?????ng h???p n???i 2 route c???n s??? d???ng 1 xe m???i
def caseUseNewVehicle(router, capacity, capVehicle, key_i, key_j):
    capacity = np.append(capacity, router[key_i]['Cap'])
    capacity = np.append(capacity, router[key_j]['Cap'])
    capacity = delValue(capacity, capVehicle)
    capacity = np.sort(capacity)
    router[key_i]['Cap'] = capVehicle
    router[key_i]['nodes'].extend(router[key_j]['nodes'][1:])
    # lo???i b??? route ???? n???i ra kh???i danh s??ch c??c route
    router.pop(key_j)
    return router, capacity


# tr?????ng h???p th??m 1 customer v??o route c???n s??? d???ng 1 xe m???i
def caseAddCtmUseNewVeh(router, capacity, capVehicle, keyRoute, customer, vehicleFixDemand):
    capacity = np.append(capacity, router[keyRoute]['Cap'])
    capacity = delValue(capacity, capVehicle)
    router[keyRoute]['Cap'] = capVehicle
    router[keyRoute]['nodes'].append(customer)
    # x??a customer kh???i danh s??ch nh???ng kh??ch h??ng kh??ng thu???c route n??o
    vehicleFixDemand.pop(customer)
    return router, capacity, vehicleFixDemand


# Algorithm Saving for capacity
def saving(distance, demand, capacity, maxCapRoad, customersList):
    distance = np.array(distance)
    demand = np.array(demand)
    capacity = np.sort(np.array(capacity))
    maxCapRoad = np.array(maxCapRoad)
    vehicleFixDemand = fixCap(demand, capacity)
    sortDist = sortDistance(distance)

    # print(vehicleFixDemand)
    router = dict()
    cout = 0

    # Browse each customer pair
    for i in sortDist:
        # ki???m tra v???i c???p kh??ch h??ng i[0]-i[1] ???? n???i ???????c 2 route v???i nhau hay ch??a(d??ng ????? th??m kh??ch h??ng m???i v??o 1 route)
        # When want add customer[j] to router[k], check 
        checkConnect = False
        # ki???m tra v???i c???p kh??ch h??ng i[0]-i[1] th?? kh??ch h??ng n??o thu???c trong route ???? x??t(d??ng ????? th??m kh??ch h??ng m???i v??o 1 route)
        vectorOfPair = -1
        # L??u key c???a route ???? x??t (d??ng ????? truy c???p khi th??m kh??ch h??ng m???i v??o 1 route)
        keyRoute = None
        # ki???m tra c???p kh??ch h??ng i[0]-i[1] c?? thu???c route n??o kh??ng (d??ng ????? kh???i t???o route m???i)
        checkAvailable = False

        # initialize the route first
        # kh???i t???o route ?????u ti??n
        if len(router) == 0:
            totalCap = demand[i[0]] + demand[i[1]]
            vehicle = getCap(capacity, totalCap)

            checkMaxCap = False
            if vehicle is not None and vehicle <= maxCapRoad[0, i[0]] and vehicle <= maxCapRoad[i[0], i[1]]:
                checkMaxCap = True
            if vehicle is not None and vehicle <= maxCapRoad[0, i[1]] and vehicle <= maxCapRoad[i[1], i[0]]:
                checkMaxCap = True

            if vehicle is not None and totalCap <= vehicle and checkMaxCap:
                nodes = [0]
                nodes.extend(i[0:2])
                router["route-" + str(cout)] = {'Cap': vehicle, 'nodes': nodes}
                capacity = delValue(capacity, vehicle)
                vehicleFixDemand.pop(i[0])
                vehicleFixDemand.pop(i[1])
            cout += 1
            continue

        # l???p c??c route ????? ki???m tra cho t???ng c???p kh??ch h??ng ?????u v??o, ????a ra quy???t ?????nh n???i hay th??m hay t???o m???i
        for k_i, v_i in router.items():
            # Check for 2 customers on the same route
            # ki???m tra 2 kh??ch h??ng i[0]-i[1] c?? thu???c c??ng 1 route hay kh??ng
            if i[0] in v_i['nodes'] and i[1] in v_i['nodes']:
                checkAvailable = True
                break

            # Check for 2 customers with customer_1 in route_1, we need check customer_2 in any route or not
            # n???u Kh??ch h??ng i[0] thu???c trong 1 route th?? ki???m tra ti???p i[1] c?? thu???c trong route n??o kh??c hay kh??ng
            if i[0] in v_i['nodes'] and i[1] not in v_i['nodes']:
                checkAvailable = True
                vectorOfPair = 0
                keyRoute = k_i
                for k_j, v_j in router.items():
                    if i[1] in v_j['nodes'] and k_i != k_j:
                        checkConnect = True
                        totalCap = (demand[v_i['nodes']].sum() + demand[v_j['nodes']].sum())

                    # n???u Kh??ch h??ng i[0] thu???c trong 1 route v?? i[1] thu???c 1 route kh??c
                    # ki???m tra c??c ??i???u ki???n v??? xe, tr???ng t???i tr??n ???????ng ....
                        checkMaxCap = nodesToNodes(maxCapRoad, i[0], i[1], v_i['Cap'], v_i['nodes'], v_j['nodes'][1:])
                        # tr?????ng h???p xe hi???n t???i v???n ????? ch??? h??ng sau khi n???i 2 route
                        if totalCap <= v_i['Cap'] and (v_i['Cap'] <= maxCapRoad[i[0], i[1]]) and checkMaxCap:
                            capacity = np.append(capacity, v_j['Cap'])
                            capacity = np.sort(capacity)
                            v_i['nodes'].extend(v_j['nodes'][1:])
                            router.pop(k_j)

                            # c???p nh???t l???i xe ph?? h???p nh???t v???i t???ng demand c???a m???i route, v?? danh s??ch xe
                            router, capacity = updateRouter(router, capacity, demand)
                            break

                        # t??m xe ph?? h???p nh???t v???i t???ng demand khi n???i 2 route
                        vehicle = getCap(capacity, totalCap)
                        if vehicle is not None:
                            checkMaxCap = nodesToNodes(maxCapRoad, i[0], i[1], vehicle, v_i['nodes'], v_j['nodes'][1:])

                        # tr?????ng h???p xe hi???n t???i kh??ng ????? v?? c???n 1 xe m???i (l???y ra xe m???i v?? th??m l???i xe c??)
                        if vehicle is not None and vehicle <= maxCapRoad[i[0], i[1]] and checkMaxCap:
                            router, capacity = caseUseNewVehicle(router, capacity, vehicle, k_i, k_j)
                            # c???p nh???t l???i xe ph?? h???p nh???t v???i t???ng demand c???a m???i route, v?? danh s??ch xe
                            router, capacity = updateRouter(router, capacity, demand)
                            break

            # Check for 2 customers with customer_2 in route_1, we need check customer_1 in any route or not
            # n???u Kh??ch h??ng i[1] thu???c trong 1 route th?? ki???m tra ti???p i[0] c?? thu???c trong route n??o kh??c hay kh??ng
            # t????ng t??? nh?? tr??n nh??ng ki???m tra v???i kh??ch h??ng i[1]
            if i[1] in v_i['nodes'] and i[0] not in v_i['nodes']:
                checkAvailable = True
                vectorOfPair = 1
                keyRoute = k_i
                for k_j, v_j in router.items():
                    if i[0] in v_j['nodes'] and k_i != k_j:
                        checkConnect = True
                        totalCap = (demand[v_i['nodes']].sum() + demand[v_j['nodes']].sum())
                        checkMaxCap = nodesToNodes(maxCapRoad, i[1], i[0], v_i['Cap'], v_i['nodes'], v_j['nodes'][1:])
                        if (totalCap <= v_i['Cap']) and (v_i['Cap'] <= maxCapRoad[i[1], i[0]]) and checkMaxCap:
                            capacity = np.append(capacity, v_j['Cap'])
                            capacity = np.sort(capacity)
                            v_i['nodes'].extend(v_j['nodes'][1:])
                            router.pop(k_j)

                            # c???p nh???t l???i xe ph?? h???p nh???t v???i t???ng demand c???a m???i route, v?? danh s??ch xe
                            router, capacity = updateRouter(router, capacity, demand)
                            break

                        vehicle = getCap(capacity, totalCap)
                        if vehicle is not None:
                            checkMaxCap = nodesToNodes(maxCapRoad, i[1], i[0], vehicle, v_i['nodes'], v_j['nodes'][1:])
                        if vehicle is not None and vehicle <= maxCapRoad[i[1], i[0]] and checkMaxCap:
                            router, capacity = caseUseNewVehicle(router, capacity, vehicle, k_i, k_j)
                            # c???p nh???t l???i xe ph?? h???p nh???t v???i t???ng demand c???a m???i route, v?? danh s??ch xe
                            router, capacity = updateRouter(router, capacity, demand)
                            break
            if checkConnect:
                break

        # tr?????ng h???p 1: n???u kh??ch i[0] ???? thu???c trong 1 route m?? i[1] kh??ng thu???c route n??o
        # ti???n h??nh ki???m tra v??? xe, t???i tr???ng ... n???u th???a m??i th?? th??m i[1] v??o route ch??? i[0]
        if not checkConnect and vectorOfPair == 0:
            totalCap = (demand[router[keyRoute]['nodes']].sum() + demand[i[1]])
            checkMaxCap = pointToNodes(maxCapRoad, i[0], i[1], router[keyRoute]['Cap'], router[keyRoute]['nodes'])

            # tr?????ng h???p xe hi???n t???i v???n c?? th??? ch??? h??ng khi ???? th??m kh??ch h??ng m???i
            # ki???m tra v??? tr???ng t???i tri??n ???????ng n???u th???a m??n th?? th??m
            if totalCap <= router[keyRoute]['Cap'] and (router[keyRoute]['Cap'] <= maxCapRoad[i[0], i[1]]) and checkMaxCap:
                router[keyRoute]['nodes'].append(i[1])
                vehicleFixDemand.pop(i[1])
                continue

            vehicle = getCap(capacity, totalCap)
            if vehicle is not None:
                checkMaxCap = pointToNodes(maxCapRoad, i[0], i[1], vehicle, router[keyRoute]['nodes'])

            # tr?????ng h???p xe hi???n t???i kh??ng th??? ch??? h??ng khi th??m kh??ch h??ng m???i
            # t??m xe ph?? h???p nh???t, ki???m tra v??? tr???ng t???i tri??n ???????ng n???u th???a m??n th?? th??m.
            if vehicle is not None and vehicle <= maxCapRoad[i[0], i[1]] and checkMaxCap:
                router, capacity, vehicleFixDemand = caseAddCtmUseNewVeh(router, capacity, vehicle, keyRoute, i[1], vehicleFixDemand)
                # c???p nh???t l???i xe ph?? h???p nh???t v???i t???ng demand c???a m???i route, v?? danh s??ch xe
                router, capacity = updateRouter(router, capacity, demand)
                continue

        # t????ng t??? nh?? tr?????ng h???p 1 nh??ng ng?????c l???i v???i i[1] thu???c trong 1 route c??n i[0] th?? kh??ng
        if not checkConnect and vectorOfPair == 1:
            totalCap = (demand[router[keyRoute]['nodes']].sum() + demand[i[0]])
            checkMaxCap = pointToNodes(maxCapRoad, i[1], i[0], router[keyRoute]['Cap'], router[keyRoute]['nodes'])
            if totalCap <= router[keyRoute]['Cap'] and (router[keyRoute]['Cap'] <= maxCapRoad[i[1], i[0]]) and checkMaxCap:
                router[keyRoute]['nodes'].append(i[0])
                vehicleFixDemand.pop(i[0])
                continue

            vehicle = getCap(capacity, totalCap)
            if vehicle is not None:
                checkMaxCap = pointToNodes(maxCapRoad, i[1], i[0], vehicle, router[keyRoute]['nodes'])
            if vehicle is not None and vehicle <= maxCapRoad[i[1], i[0]] and checkMaxCap:
                router, capacity, vehicleFixDemand = caseAddCtmUseNewVeh(router, capacity, vehicle, keyRoute, i[0], vehicleFixDemand)
                # c???p nh???t l???i xe ph?? h???p nh???t v???i t???ng demand c???a m???i route, v?? danh s??ch xe
                router, capacity = updateRouter(router, capacity, demand)
                continue

        # n???u 2 kh??ch h??ng i[0]-i[1] kh??ng thu???c route n??o
        # th?? ti???n h??nh ki???m tra v??? xe, tr???ng t???i tr??n ???????ng n???u th???a m??n th?? t???o chu tr??nh m???i
        if not checkAvailable:
            totalCap = demand[i[0]] + demand[i[1]]
            vehicle = getCap(capacity, totalCap)
            checkMaxCap = False
            if vehicle is not None and vehicle <= maxCapRoad[0, i[0]] and vehicle <= maxCapRoad[i[0], i[1]]:
                checkMaxCap = True
            if vehicle is not None and vehicle <= maxCapRoad[0, i[1]] and vehicle <= maxCapRoad[i[1], i[0]]:
                checkMaxCap = True

            if vehicle is not None and totalCap <= vehicle and checkMaxCap:
                nodes = [0]
                nodes.extend(i[0:2])
                router["route-" + str(cout)] = {'Cap': vehicle, 'nodes': nodes}
                capacity = delValue(capacity, vehicle)
                vehicleFixDemand.pop(i[0])
                vehicleFixDemand.pop(i[1])
            cout += 1
            continue

    # c???p nh???t l???i xe ph?? h???p nh???t v???i t???ng demand c???a m???i route
    # c???p nh???t l???i ch??? s??? so v???i list customer ?????u v??o c???a c??c chu tr??nh
    router = updateIndexCustomer(router, customersList)

    # c???p nh???t l???i ch??? s??? so v???i list customer ?????u v??o c???a nh???ng kh??ch h??ng kh??ng thu???c route n??o
    newVehicleFixCustomer = updateIndexVehicleFixCustomer(vehicleFixDemand, customersList)
    return router, capacity, newVehicleFixCustomer


# create a matrix with the maxcost values for the routes that cannot be traveled
def updateCost(costMatrix, maxCapRoadMatrix, nodesList, vehicle, maxCost):
    costMatrixOfNodes = list()
    for i in nodesList:
        listCost = list()
        for j in nodesList:
            if i == j:
                listCost.append(0)
            elif vehicle > maxCapRoadMatrix[i, j]:
                listCost.append(maxCost)
            else:
                listCost.append(costMatrix[i, j])
        costMatrixOfNodes.append(listCost)
    return np.array(costMatrixOfNodes)


# if __name__ == '__main__':
#     # costMatrix: is the square matrix of the cost between the customers (have depot)
#     # demand: is list customers of customers (have depot = 0)
#     #       ex: matrix costMatrix is: (s, a, b)x(s, a, b)
#     #       demand list is: (demand[s], demand[a], demand[b])
#     # capacity: is list capacity of the vehicle. (sort(min->max))
#     # maxCapRoadMatrix: is the square matrix of the maximum capacity of the road between 2 customers (have depot)

#     costMatrix = np.genfromtxt('../data/costMatrix100.csv', delimiter=',')
#     maxCapRoadMatrix = np.genfromtxt('../data/matrix_maxtonage_250221.csv', delimiter=',')
#     demand = np.genfromtxt('../data/demand_250221.csv', delimiter=',')
#     capacity = np.genfromtxt('../data/vehicle_230221.csv', delimiter=',')

#     # sorfD = sortDistance(costMatrix)
#     # print(sorfD)

#     customersList = list()
#     for i in range(0, 100):
#         customersList.append(i)

#     startime = time.process_time()
#     r, c, v = saving(costMatrix, demand, capacity, maxCapRoadMatrix, customersList)

#     print(f'route: ')
#     demand = np.array(demand)
#     for key, value in r.items():
#         value['totalD'] = demand[value['nodes']-3].sum()
#         print(f'{" " * 8}{key}:{value}')

#     print(f'\nThe remaining vehicles: {c}\nThe remaining customers:{v}')
#     print("Run time: ", time.process_time() - startime)
