# solver.py
"""
Capa de abstracción del solver para el proyecto.
Permite cambiar entre Gecode (por defecto) y Gurobi sin modificar el resto del sistema.

El propósito es:
- Tener un único punto donde se define cómo se resuelve el modelo.
- Mantener la estructura simple y fiel al enunciado.
"""

from ortools.sat.python import cp_model  # Para Gecode (CP-SAT)
# Si se usa Gurobi:
# from gurobipy import Model, GRB


class SolverBackend:
    def __init__(self, backend="gecode"):
        """
        backend: "gecode" | "gurobi"
        """
        self.backend = backend

    def solve(self, model_data):
        """
        model_data contiene las variables y restricciones que definió tu team.
        Esta función recibe esa estructura y la resuelve usando el backend elegido.
        """

        if self.backend == "gecode":
            return self._solve_gecode(model_data)

        elif self.backend == "gurobi":
            return self._solve_gurobi(model_data)

        else:
            raise ValueError(f"Backend no soportado: {self.backend}")
    
    # SOLVER: GECODE (CP-SAT)
    
    def _solve_gecode(self, model_data):
        model = cp_model.CpModel()

        # 1. Crear variables
        variables = {}
        for var_name, domain in model_data["variables"].items():
            lo, hi = domain
            variables[var_name] = model.NewIntVar(lo, hi, var_name)

        # 2. Crear restricciones
        for cons in model_data["constraints"]:
            expr = cons(variables)
            model.Add(expr)

        # 3. Función objetivo
        if "objective" in model_data:
            model.Minimize(model_data["objective"](variables))

        # Resolver
        solver = cp_model.CpSolver()
        status = solver.Solve(model)

        if status not in [cp_model.OPTIMAL, cp_model.FEASIBLE]:
            return None

        # Retornar solución simple
        return {name: solver.Value(var) for name, var in variables.items()}
    
    # SOLVER: GUROBI
    
    def _solve_gurobi(self, model_data):
        # Descomenta y termina este método SOLO SI EL PROFESOR LO PIDE.
        raise NotImplementedError("Gurobi será implementado solo si el profesor lo exige.")

