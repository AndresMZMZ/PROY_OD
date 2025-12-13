# run_mzn.py
"""
Ejecutor de modelos MiniZinc con manejo robusto de salida JSON.
"""

import subprocess
import json
import shutil
from pathlib import Path


class MiniZincRunner:
    def __init__(self, minizinc_exe=None):
        """
        Inicializa el runner de MiniZinc.
        
        Args:
            minizinc_exe: Ruta al ejecutable de MiniZinc (opcional)
        """
        if minizinc_exe:
            self.minizinc = str(minizinc_exe)
        else:
            self.minizinc = shutil.which("minizinc")
        
        if not self.minizinc:
            raise FileNotFoundError(
                "No se encontró el ejecutable 'minizinc' en PATH.\n"
                "Instala MiniZinc desde: https://www.minizinc.org/\n"
                "Y asegúrate de agregarlo al PATH del sistema."
            )

    def run(self, mzn_path, dzn_path, solver="gecode", timeout=None, all_solutions=False):
        """
        Ejecuta un modelo MiniZinc.
        
        Args:
            mzn_path: Ruta al archivo .mzn
            dzn_path: Ruta al archivo .dzn
            solver: Nombre del solver (gecode, chuffed, gurobi, etc.)
            timeout: Tiempo máximo en segundos (None = sin límite)
            all_solutions: Si True, busca todas las soluciones
            
        Returns:
            Dict con los resultados o dict con error
        """
        mzn = Path(mzn_path)
        dzn = Path(dzn_path)
        
        # Validaciones
        if not mzn.exists():
            return {"error": f"No se encontró el archivo .mzn: {mzn}"}
        if not dzn.exists():
            return {"error": f"No se encontró el archivo .dzn: {dzn}"}

        # Construir comando
        cmd = [self.minizinc, str(mzn), str(dzn), "--solver", solver]
        
        if all_solutions:
            cmd.append("--all-solutions")
        
        # Ejecutar
        try:
            proc = subprocess.run(
                cmd,
                capture_output=True,
                text=True,
                timeout=timeout,
                encoding='utf-8'
            )
        except subprocess.TimeoutExpired:
            return {
                "error": f"Timeout: El modelo no terminó en {timeout} segundos",
                "timeout": True
            }
        except Exception as e:
            return {"error": f"Error ejecutando MiniZinc: {e}"}

        # Verificar código de salida
        if proc.returncode != 0:
            return {
                "error": proc.stderr.strip() if proc.stderr else "Error desconocido",
                "stderr": proc.stderr.strip(),
                "returncode": proc.returncode
            }

        # Procesar salida
        return self._parse_output(proc.stdout)

    def _parse_output(self, output: str):
        """
        Parsea la salida de MiniZinc y extrae el JSON.
        
        MiniZinc puede generar salidas como:
        ```
        { "resultado": 123 }
        ----------
        ==========
        ```
        
        Args:
            output: String con la salida completa de MiniZinc
            
        Returns:
            Dict con los datos parseados o dict con error
        """
        if not output or not output.strip():
            return {"error": "MiniZinc no produjo salida", "raw": output}
        
        lines = output.strip().split('\n')
        
        # Buscar líneas que contengan JSON
        json_lines = []
        in_json = False
        brace_count = 0
        
        for line in lines:
            # Detectar inicio de JSON
            if '{' in line:
                in_json = True
            
            if in_json:
                json_lines.append(line)
                brace_count += line.count('{') - line.count('}')
                
                # Si cerramos todos los braces, terminamos
                if brace_count == 0:
                    break
        
        if not json_lines:
            # Intentar encontrar una línea que sea JSON completo
            for line in lines:
                line = line.strip()
                if line.startswith('{') and line.endswith('}'):
                    json_lines = [line]
                    break
        
        if not json_lines:
            return {
                "error": "No se encontró JSON en la salida",
                "raw": output
            }
        
        # Unir líneas y parsear
        json_str = '\n'.join(json_lines)
        
        try:
            data = json.loads(json_str)
            return data
        except json.JSONDecodeError as e:
            return {
                "error": f"JSON inválido: {e}",
                "raw": output,
                "json_attempted": json_str
            }

    def check_solver(self, solver_name):
        """
        Verifica si un solver está disponible.
        
        Args:
            solver_name: Nombre del solver (e.g., 'gecode', 'gurobi')
            
        Returns:
            bool: True si el solver está disponible
        """
        try:
            proc = subprocess.run(
                [self.minizinc, "--solvers"],
                capture_output=True,
                text=True,
                timeout=5
            )
            return solver_name.lower() in proc.stdout.lower()
        #   Especificar errores de subproceso
        except (subprocess.TimeoutExpired, OSError): 
            return False

    def list_solvers(self):
        """
        Lista todos los solvers disponibles.
        
        Returns:
            List[str]: Lista de nombres de solvers
        """
        try:
            proc = subprocess.run(
                [self.minizinc, "--solvers"],
                capture_output=True,
                text=True,
                timeout=5
            )
            if proc.returncode == 0:
                # Parsear salida (formato puede variar según versión)
                lines = proc.stdout.strip().split('\n')
                solvers = []
                for line in lines:
                    # Típicamente: "Gecode 6.3.0" o "gecode"
                    parts = line.strip().split()
                    if parts:
                        solvers.append(parts[0].lower())
                return solvers
            return []
        #   Especificar errores de subproceso
        except (subprocess.TimeoutExpired, OSError):
            return []

# FUNCIONES DE UTILIDAD
def run_model_simple(mzn_path, dzn_path, solver="gecode", timeout=300):
    """
    Función conveniente para ejecutar un modelo rápidamente.
    
    Args:
        mzn_path: Ruta al .mzn
        dzn_path: Ruta al .dzn
        solver: Solver a usar
        timeout: Timeout en segundos
        
    Returns:
        Dict con resultados
    """
    runner = MiniZincRunner()
    return runner.run(mzn_path, dzn_path, solver=solver, timeout=timeout)