import numpy as np
import pyomo.environ as pyo


def queens_solver(matrix):
    
    n,m = matrix.shape

    model = pyo.ConcreteModel()
    model.name = "Queens_Solver"

    # Sets 
    model.I = pyo.RangeSet(1, n)
    model.J = pyo.RangeSet(1, m)
    # model.colors = pyo.Set(initialize=sorted(set(np.unique(matrix))))
    model.colors = pyo.RangeSet(1,n)

    indices_matrix = {}
    for c in range(1,n+1):
        indices_matrix[c] = []
        for i in range(n):
            for j in range(m):
                if matrix[i,j] == c:
                    indices_matrix[c].append((i,j))
    
    # Variables (square of the quadrant)
    model.x = pyo.Var(model.I, model.J, domain=pyo.Binary)

    # Constraints
    # Each row has to contain only 1 crown
    def row_constraint(model, i):
        return sum(model.x[i,j] for j in model.J) == 1
    model.row_constraint = pyo.Constraint(model.I, rule = row_constraint)

    # Each column has to contain only 1 crown
    def column_constraint(model, j):
        return sum(model.x[i,j] for i in model.I) == 1
    model.column_constraint = pyo.Constraint(model.J, rule = column_constraint)

    # Adjacent cell constraints (including diagonals)
    def adjacent_constraint(model, i, j):
        # Only top diagonals neighbors
        # diagonals = [(i-1, j-1), (i-1, j+1), (i+1, j-1), (i+1, j+1)]
        diagonals = [(i-1, j-1), (i-1, j+1)]
        neighbors = [(ii, jj) for (ii, jj) in diagonals
                    if 1 <= ii <= n and 1 <= jj <= m]
        return model.x[i, j] + sum(model.x[ii, jj] for (ii, jj) in neighbors) <= 1
    model.adjacent_constraint = pyo.Constraint(model.I, model.J, rule=adjacent_constraint)

    # # Color assignment constraints
    def color_constraint(model, c):
        suma = sum(model.x[i+1, j+1] for i,j in indices_matrix[c]) 
        return suma <= 1
    model.color_constraint = pyo.Constraint(model.colors, rule=color_constraint)

    # Objective (Optional - if needed for optimal arrangement)
    model.obj = pyo.Objective(expr=0, sense=pyo.maximize)

    solver = pyo.SolverFactory('gurobi')
    result = solver.solve(model, tee=False)  # tee=True prints solver log to screen
    # print("Solver status:", result.solver.status)
    # print("Termination condition:", result.solver.termination_condition)
    solution = np.zeros_like(matrix)
    for i in range(1, n+1):
        for j in range(1, m+1):
            if pyo.value(model.x[i, j]) == 1:
                solution[i-1, j-1] = 1

    return solution, model



def check_feasibility(model, solution, tol=1e-6):
    """
    Checks each constraint of the Pyomo model for feasibility using the provided solution.
    'solution' should be a NumPy array with the same shape as the grid (rows x columns).
    """
    # Assign candidate values to model variables.
    for i in model.I:
        for j in model.J:
            # Adjusting for 1-indexing in Pyomo vs 0-indexing in the solution array.
            model.x[i, j].value = solution[i-1, j-1]
    
    infeasible_constraints = []
    
    # Loop over all active constraints in the model.
    for constr in model.component_objects(pyo.Constraint, active=True):
        for index in constr:
            con = constr[index]
            try:
                body_val = pyo.value(con.body)
            except Exception as e:
                infeasible_constraints.append((constr.name, index, "Error evaluating body: " + str(e)))
                continue

            lb = pyo.value(con.lower) if con.has_lb() else None
            ub = pyo.value(con.upper) if con.has_ub() else None

            # Check equality constraints (lb == ub) or inequality constraints.
            if lb is not None and ub is not None:
                # For equality constraints, both bounds should be met.
                if abs(body_val - lb) > tol:
                    infeasible_constraints.append((constr.name, index, body_val, lb, ub))
            elif lb is not None:
                if body_val < lb - tol:
                    infeasible_constraints.append((constr.name, index, body_val, lb, ub))
            elif ub is not None:
                if body_val > ub + tol:
                    infeasible_constraints.append((constr.name, index, body_val, lb, ub))
    
    return infeasible_constraints



if __name__ == "__main__":
    matrix = np.array([
        [1,1,1,1,2,3,3,4,5],
        [1,1,1,2,2,2,4,4,5],
        [1,1,2,2,2,2,2,4,5],
        [1,2,2,6,2,7,2,2,5],
        [1,2,6,6,2,7,7,2,5],
        [1,2,2,2,2,2,2,2,5],
        [1,2,2,8,8,8,2,2,5],
        [1,2,2,9,8,8,2,2,5],
        [1,2,2,9,8,8,2,2,5],
    ])
    matrix = np.array([
        [1,1,1,1,1,1,2],
        [1,3,4,4,4,1,2],
        [1,3,4,5,5,5,2],
        [1,3,3,3,5,5,6],
        [1,7,7,5,5,6,6],
        [1,7,7,7,7,1,6],
        [1,1,1,1,1,1,6],
    ])


    # real_solution = np.array([
    #     [0,0,0,0,0,0,1,0,0],
    #     [1,0,0,0,0,0,0,0,0],
    #     [0,0,0,0,0,0,0,1,0],
    #     [0,0,0,0,0,1,0,0,0],
    #     [0,0,1,0,0,0,0,0,0],
    #     [0,0,0,0,0,0,0,0,1],
    #     [0,0,0,0,1,0,0,0,0],
    #     [0,1,0,0,0,0,0,0,0],
    #     [0,0,0,1,0,0,0,0,0],
    # ])

    solution, model = queens_solver(matrix)

    # Use the function to check your candidate solution:
    # violations = check_feasibility(model, real_solution)
    # if violations:
    #     print("The candidate solution is infeasible. Violations:")
    #     for v in violations:
    #         print(f"Constraint: {v[0]}, Index: {v[1]}, Body: {v[2]}, Bounds: ({v[3]}, {v[4]})")
    # else:
    #     print("The candidate solution is feasible!")

    # solution = queens_solver(matrix)
    print(f"Input Matrix:\n {matrix} \n")
    print(f"Solution: \n {solution}")

