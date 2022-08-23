from ast import And
from re import M
from flask import request
import bin.helpers.responses.error as error_response
import bin.helpers.responses.data as data_response
import googlemaps 
import numpy as np
import random as rand


class SimannealHandler:
    def __init__(self, mysql):
        self.mysql = mysql
        self.gmaps = googlemaps.Client(key='AIzaSyCXEykmj3RsEDFNBrLCmA-lmxKCWqT-zCI')  

    def fitness_TSP(self, solution, distance_matrix):
        distance = np.zeros([1,1])
        for truck in range(0, len(solution[0,:])-1):
            departure_node = int(solution[0][truck])
            next_node = int(solution[0][truck+1])
            distance += distance_matrix[departure_node][next_node]
            del departure_node, next_node
            fitness = 1/distance
        return fitness
    
    def swap_search(self, solution):
        #choice 2 random nodes
        swap_nodes = rand.sample(range(1, len(solution[0,:])-1), 2)
        swap1 = swap_nodes[0]
        swap2 = swap_nodes[1]

        #swap the value
        new_solution = np.array(solution)
        temp = np.array(new_solution[0][swap1])
        new_solution[0][swap1] = new_solution[0][swap2]
        new_solution[0][swap2] = temp
        del swap1, swap2, swap_nodes, temp
        return new_solution 

    def insertion_search(self, solution):
        #choice 2 random nodes
        insertion_nodes = rand.sample(range(1, len(solution[0,:])-1), 2)
        while abs(insertion_nodes[0] - insertion_nodes[1] == 1 or insertion_nodes[0] - insertion_nodes[1] == 0):
            insertion_nodes = rand.sample(range(1, len(solution[0,:])-1), 2)
        insertion1 = insertion_nodes[0]
        insertion2 = insertion_nodes[1] #--> target

        #insertion the value
        new_solution = np.array(solution)
        if insertion1 < insertion2:
            temp = np.array(new_solution)
            new_solution[0][insertion2-1] = new_solution[0][insertion1]
            if insertion1 == (insertion2-2):
                new_solution[0][insertion1] = temp[0][insertion1+1]
            else:
                new_solution[0][insertion1:insertion2-1] = np.array(temp[0][insertion1+1:insertion2])
        elif insertion1 > insertion2:
            temp = np.array(new_solution)
            new_solution[0][insertion1-1] = new_solution[0][insertion2]
            if insertion1 == (insertion1-2):
                new_solution[0][insertion2] = temp[0][insertion2+1]
            else:
                new_solution[0][insertion2:insertion1-1] = np.array(temp[0][insertion2+1:insertion1])
        return new_solution

    def twoopt_search(self, solution):
        edge_nodes = rand.sample(range(1, len(solution[0,:])-2), 2)
        while abs(edge_nodes[0]-edge_nodes[1]) == 1:
            edge_nodes = rand.sample(range(1, len(solution[0,:])-2), 2)
        edge_a = edge_nodes[0]
        edge_b = edge_nodes[0]+1
        edge_c = edge_nodes[1]
        edge_d = edge_nodes[1]+1
        
        #swap with 2opt
        new_solution = np.array(solution)
        node_a = new_solution[0][edge_a]
        node_b = new_solution[0][edge_c]
        node_c = new_solution[0][edge_b]
        node_d = new_solution[0][edge_d]

        new_solution[0][edge_a] = node_a
        new_solution[0][edge_b] = node_b
        new_solution[0][edge_c] = node_c
        new_solution[0][edge_d] = node_d

        del edge_a, edge_b, edge_c, edge_d, node_a, node_b, node_c, node_d
        return new_solution

    def convert(self, seconds):
        min, sec = divmod(seconds, 60)
        hour, min = divmod(min, 60)
        return str(hour)+'h '+str(min)+'m '+str(sec)+'s'

    def run_simanneal(self):
        try:
            _json = request.json
            mode = _json['mode']
            gudang_id = _json['gudang_id']
            if mode and request.method == 'POST':
                partners = self.mysql.query('SELECT partners.longitude, partners.latitude, partners.id as partner_id FROM deliveries INNER JOIN partners ON deliveries.partner_id=partners.id WHERE status="Pending"')
                if(len(partners) < 1) :
                    return error_response.not_found('partners not found')

                gudangs = self.mysql.query('SELECT latitude, longitude, id as gudang_id FROM gudangs WHERE id='+str(gudang_id)+'')
                if(len(gudangs) < 1) :
                    return error_response.not_found('gudangs not found')

                nodes = []
                gudang = {
                    'latitude': gudangs[0]['latitude'],
                    'longitude': gudangs[0]['longitude'],
                    'gudang_id': gudangs[0]['gudang_id']
                }
                nodes.append(gudang)

                for a, elemenA in enumerate(partners):
                    partner = {
                        'latitude': elemenA['latitude'],
                        'longitude': elemenA['longitude'],
                        'partner_id': elemenA['partner_id'],
                    }
                    nodes.append(partner)

                distance_details = []
                distance_matrix = []
                for i, elemenI in enumerate(nodes):
                    distance_matrix.append([])
                    for j, elemenJ in enumerate(nodes):
                        detail = self.gmaps.distance_matrix([str(elemenI['latitude']) + " " + str(elemenI['longitude'])], [str(elemenJ['latitude']) + " " + str(elemenJ['longitude'])], mode=mode)['rows'][0]['elements'][0]
                        data = {
                            'source': elemenI,
                            'destination': elemenJ,
                            'details': detail
                        }
                        distance_details.append(data)
                        distance_matrix[i].append(detail['distance']['value'])
                
                # distance_matrix = np.array(distance_matrix)
                num_node = len(nodes)

                #run algorithm
                #step 1 define parameter
                t_max = 100
                t_min = 1
                cooling_rate = 0.9
                max_iteration = 50

                t_now = t_max
                iteration = 1

                #step 2 create initial solution x
                X_old = np.zeros([1, num_node+1], dtype=int)
                X_old[0,1:-1] = np.random.permutation(num_node-1)+1

                #step 3 create fitness f(X_old)
                X_fitness = self.fitness_TSP(X_old, distance_matrix)
                # X_new = self.twoopt_search(X_old)
                # data = {
                #     'x': str(X_old),
                #     'y': str(X_new)
                # }
                iterations = []
                #step 4 looping SA
                while t_now > t_min:
                    #randomize r
                    r = np.random.random()

                    #creating new solution
                    if r <= 0.33:
                        X_new = self.swap_search(X_old)
                    elif r > 0.33 and r <= 0.66:
                        X_new = self.insertion_search(X_old)
                    else:
                        X_new = self.twoopt_search(X_old)
                    del r

                    #evaluation fitness of the new solution
                    X_new_fitness = self.fitness_TSP(X_new, distance_matrix)

                    #wanna keep the X_new?
                    if X_new_fitness > X_fitness:
                        X_old = np.array(X_new)
                        X_fitness = np.array(X_new_fitness)
                    del X_new, X_new_fitness

                    #update iteration
                    iteration += 1

                    #update temperature
                    if iteration == max_iteration:
                        t_now = t_now * cooling_rate
                        iteration = 1

                    iterations.append(iteration)

                X_old = X_old.flatten().tolist()

                result = []
                for b, elemenX in enumerate(X_old):
                    result.append(nodes[elemenX])

                result_detail = []
                index = []
                total_distance = 0
                total_duration = 0
                for i in range(0, len(result)):
                    for j in range(i+1, len(result), len(result)):
                        if i == len(result)-2:
                            j = 0
                        index.append(str(i)+','+str(j))
                        for k, detail in enumerate(distance_details):
                            if result[i]['longitude'] == detail['source']['longitude'] and result[i]['latitude'] == detail['source']['latitude'] and result[j]['longitude'] == detail['destination']['longitude'] and result[j]['latitude'] == detail['destination']['latitude']:
                                data = {
                                    'from': detail['source'],
                                    'to': detail['destination'],
                                    'distance': detail['details']['distance']['value'],
                                    'duration': detail['details']['duration']['value']
                                }
                                total_distance += detail['details']['distance']['value']
                                total_duration += detail['details']['duration']['value']
                                result_detail.append(data)

                data = {
                    'nodes': result,
                    'edge': result_detail,
                    'total_distance': str(total_distance/1000)+'km',
                    'total_duration': self.convert(total_duration),
                }
 
                return data_response.data(data, 'Get Partners Success')                    
            else:
                return error_response.not_found("Not found error")
        except Exception as e:
            return error_response.internal_server(str(e))
    