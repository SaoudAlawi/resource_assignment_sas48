
from ortools.linear_solver import pywraplp
from fastapi import FastAPI
from pydantic import BaseModel
from typing import List

class Item(BaseModel):

    # user_ids:list
    # drop_zone_ids:list

    food_cost: list
    water_cost:list
    travel_dist:list


def solve(food_cost= None,water_cost=None,travel_dist=None):

# Formulate cost matrixes havinf to hubs and 4 indivedulas

    # food_cost = [[20,20],
    #             [10,10],
    #             [-10,-10],
    #             [-20,-20]]
    
    # water_cost = [[0,0],
    #             [3,3],
    #             [3,3],
    #             [-10,-10]]
    

    # travel_dist = [[5000,56],
    #             [0,0],
    #             [90,300],
    #             [90,100]]
    num_workers = len(food_cost)
    num_hub = len(food_cost[0])

    # Solver
    # Create the mip solver with the SCIP backend.
    solver = pywraplp.Solver.CreateSolver("SCIP")

    if not solver:
        return

    # Variables
    # x[i, j] is an array of 0-1 variables, which will be 1
    # if worker i is assigned to task j.
    x = {}
    for i in range(num_workers):
        for j in range(num_hub):
            x[i, j] = solver.IntVar(0, 1, "")

    # Constraints
    # Each worker is assigned to at most 1 task.
    for i in range(num_workers):
        solver.Add(solver.Sum([x[i, j] for j in range(num_hub)]) == 1)

    # # Each task is assigned to exactly one worker.
    # for j in range(num_hub):
    #     solver.Add(solver.Sum([x[i, j] for i in range(num_workers)]) == 1)

# Objective function: minimize total cost (sum of two assignment cost matrices)

# Objective
    objective_terms = []
    for i in range(num_workers):
        for j in range(num_hub):
            objective_terms.append((water_cost[i][j]+food_cost[i][j] +travel_dist[i][j]) * x[i, j])
    solver.Minimize(solver.Sum(objective_terms))

    # Solve
    status = solver.Solve()

    
    if status == pywraplp.Solver.OPTIMAL or status == pywraplp.Solver.FEASIBLE:
        response = []
        print(f"Total cost = {solver.Objective().Value()}\n")
        for j in range(num_hub):
            
            for i in range(num_workers):
                # Test if x[i,j] is 1 (with tolerance for floating point arithmetic).
                if x[i, j].solution_value() > 0.5:
                    response.append([j, i])
        return response
    else:
        print("No solution found.")


app = FastAPI()


@app.get("/assign")
async def opt(request:Item):

    # user_ids = request.user_ids
    # drop_zone_ids = request.drop_zone_ids

    food_cost = request.food_cost
    water_cost = request.water_cost
    travel_dist= request.travel_dist
    
    print (food_cost)
    
    result_dict = {}
    pairs = solve(food_cost,water_cost,travel_dist)
    # Iterate through the pairs and build the dictionary
    for pair in pairs:
        key, value = pair
        if key not in result_dict:
            result_dict[key] = []
        result_dict[key].append(value)
    return {"result": result_dict}
