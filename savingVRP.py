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


# sử lý trường hợp nối 2 route cần sử dụng 1 xe mới
def caseUseNewVehicle(router, capacity, capVehicle, key_i, key_j):
    capacity = np.append(capacity, router[key_i]['Cap'])
    capacity = np.append(capacity, router[key_j]['Cap'])
    capacity = delValue(capacity, capVehicle)
    capacity = np.sort(capacity)
    router[key_i]['Cap'] = capVehicle
    router[key_i]['nodes'].extend(router[key_j]['nodes'][1:])
    # loại bỏ route đã nối ra khỏi danh sách các route
    router.pop(key_j)
    return router, capacity


# trường hợp thêm 1 customer vào route cần sử dụng 1 xe mới
def caseAddCtmUseNewVeh(router, capacity, capVehicle, keyRoute, customer, vehicleFixDemand):
    capacity = np.append(capacity, router[keyRoute]['Cap'])
    capacity = delValue(capacity, capVehicle)
    router[keyRoute]['Cap'] = capVehicle
    router[keyRoute]['nodes'].append(customer)
    # xóa customer khỏi danh sách những khách hàng không thuộc route nào
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
        # kiểm tra với cặp khách hàng i[0]-i[1] đã nối được 2 route với nhau hay chưa(dùng để thêm khách hàng mới vào 1 route)
        # When want add customer[j] to router[k], check 
        checkConnect = False
        # kiểm tra với cặp khách hàng i[0]-i[1] thì khách hàng nào thuộc trong route đã xét(dùng để thêm khách hàng mới vào 1 route)
        vectorOfPair = -1
        # Lưu key của route đã xét (dùng để truy cập khi thêm khách hàng mới vào 1 route)
        keyRoute = None
        # kiểm tra cặp khách hàng i[0]-i[1] có thuộc route nào không (dùng để khởi tạo route mới)
        checkAvailable = False

        # initialize the route first
        # khởi tạo route đầu tiên
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

        # lặp các route để kiểm tra cho từng cặp khách hàng đầu vào, đưa ra quyết định nối hay thêm hay tạo mới
        for k_i, v_i in router.items():
            # Check for 2 customers on the same route
            # kiểm tra 2 khách hàng i[0]-i[1] có thuộc cùng 1 route hay không
            if i[0] in v_i['nodes'] and i[1] in v_i['nodes']:
                checkAvailable = True
                break

            # Check for 2 customers with customer_1 in route_1, we need check customer_2 in any route or not
            # nếu Khách hàng i[0] thuộc trong 1 route thì kiểm tra tiếp i[1] có thuộc trong route nào khác hay không
            if i[0] in v_i['nodes'] and i[1] not in v_i['nodes']:
                checkAvailable = True
                vectorOfPair = 0
                keyRoute = k_i
                for k_j, v_j in router.items():
                    if i[1] in v_j['nodes'] and k_i != k_j:
                        checkConnect = True
                        totalCap = (demand[v_i['nodes']].sum() + demand[v_j['nodes']].sum())

                    # nếu Khách hàng i[0] thuộc trong 1 route và i[1] thuộc 1 route khác
                    # kiểm tra các điều kiện về xe, trọng tải trên đường ....
                        checkMaxCap = nodesToNodes(maxCapRoad, i[0], i[1], v_i['Cap'], v_i['nodes'], v_j['nodes'][1:])
                        # trường hợp xe hiện tại vẫn đủ chở hàng sau khi nối 2 route
                        if totalCap <= v_i['Cap'] and (v_i['Cap'] <= maxCapRoad[i[0], i[1]]) and checkMaxCap:
                            capacity = np.append(capacity, v_j['Cap'])
                            capacity = np.sort(capacity)
                            v_i['nodes'].extend(v_j['nodes'][1:])
                            router.pop(k_j)

                            # cập nhật lại xe phù hợp nhất với tổng demand của mỗi route, và danh sách xe
                            router, capacity = updateRouter(router, capacity, demand)
                            break

                        # tìm xe phù hợp nhất với tổng demand khi nối 2 route
                        vehicle = getCap(capacity, totalCap)
                        if vehicle is not None:
                            checkMaxCap = nodesToNodes(maxCapRoad, i[0], i[1], vehicle, v_i['nodes'], v_j['nodes'][1:])

                        # trường hợp xe hiện tại không đủ và cần 1 xe mới (lấy ra xe mới và thêm lại xe cũ)
                        if vehicle is not None and vehicle <= maxCapRoad[i[0], i[1]] and checkMaxCap:
                            router, capacity = caseUseNewVehicle(router, capacity, vehicle, k_i, k_j)
                            # cập nhật lại xe phù hợp nhất với tổng demand của mỗi route, và danh sách xe
                            router, capacity = updateRouter(router, capacity, demand)
                            break

            # Check for 2 customers with customer_2 in route_1, we need check customer_1 in any route or not
            # nếu Khách hàng i[1] thuộc trong 1 route thì kiểm tra tiếp i[0] có thuộc trong route nào khác hay không
            # tương tự như trên nhưng kiểm tra với khách hàng i[1]
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

                            # cập nhật lại xe phù hợp nhất với tổng demand của mỗi route, và danh sách xe
                            router, capacity = updateRouter(router, capacity, demand)
                            break

                        vehicle = getCap(capacity, totalCap)
                        if vehicle is not None:
                            checkMaxCap = nodesToNodes(maxCapRoad, i[1], i[0], vehicle, v_i['nodes'], v_j['nodes'][1:])
                        if vehicle is not None and vehicle <= maxCapRoad[i[1], i[0]] and checkMaxCap:
                            router, capacity = caseUseNewVehicle(router, capacity, vehicle, k_i, k_j)
                            # cập nhật lại xe phù hợp nhất với tổng demand của mỗi route, và danh sách xe
                            router, capacity = updateRouter(router, capacity, demand)
                            break
            if checkConnect:
                break

        # trường hợp 1: nếu khách i[0] đã thuộc trong 1 route mà i[1] không thuộc route nào
        # tiến hành kiểm tra về xe, tải trọng ... nếu thỏa mãi thì thêm i[1] vào route chứ i[0]
        if not checkConnect and vectorOfPair == 0:
            totalCap = (demand[router[keyRoute]['nodes']].sum() + demand[i[1]])
            checkMaxCap = pointToNodes(maxCapRoad, i[0], i[1], router[keyRoute]['Cap'], router[keyRoute]['nodes'])

            # trường hợp xe hiện tại vẫn có thể chở hàng khi đã thêm khách hàng mới
            # kiểm tra về trọng tải triên đường nếu thỏa mãn thì thêm
            if totalCap <= router[keyRoute]['Cap'] and (router[keyRoute]['Cap'] <= maxCapRoad[i[0], i[1]]) and checkMaxCap:
                router[keyRoute]['nodes'].append(i[1])
                vehicleFixDemand.pop(i[1])
                continue

            vehicle = getCap(capacity, totalCap)
            if vehicle is not None:
                checkMaxCap = pointToNodes(maxCapRoad, i[0], i[1], vehicle, router[keyRoute]['nodes'])

            # trường hợp xe hiện tại không thể chở hàng khi thêm khách hàng mới
            # tìm xe phù hợp nhất, kiểm tra về trọng tải triên đường nếu thỏa mãn thì thêm.
            if vehicle is not None and vehicle <= maxCapRoad[i[0], i[1]] and checkMaxCap:
                router, capacity, vehicleFixDemand = caseAddCtmUseNewVeh(router, capacity, vehicle, keyRoute, i[1], vehicleFixDemand)
                # cập nhật lại xe phù hợp nhất với tổng demand của mỗi route, và danh sách xe
                router, capacity = updateRouter(router, capacity, demand)
                continue

        # tương tự như trường hợp 1 nhưng ngược lại với i[1] thuộc trong 1 route còn i[0] thì không
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
                # cập nhật lại xe phù hợp nhất với tổng demand của mỗi route, và danh sách xe
                router, capacity = updateRouter(router, capacity, demand)
                continue

        # nếu 2 khách hàng i[0]-i[1] không thuộc route nào
        # thì tiến hành kiểm tra về xe, trọng tải trên đường nếu thỏa mãn thì tạo chu trình mới
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

    # cập nhật lại xe phù hợp nhất với tổng demand của mỗi route
    # cập nhật lại chỉ số so với list customer đầu vào của các chu trình
    router = updateIndexCustomer(router, customersList)

    # cập nhật lại chỉ số so với list customer đầu vào của những khách hàng không thuộc route nào
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
