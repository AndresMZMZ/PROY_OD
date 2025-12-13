# generar_dzn.py
"""
Módulo para parsear archivos .txt de entrada según el formato del proyecto
y generar archivos .dzn para MiniZinc.
"""

from pathlib import Path
from typing import Dict, List


def parse_input_text(text: str) -> Dict:
    """
    Parsea el contenido de un archivo .txt según el formato del proyecto.
    
    Args:
        text: String con el contenido del archivo
        
    Returns:
        Dict con las claves: n, m, p, v, s, ct, max_movs
        
    Raises:
        ValueError: Si el formato es incorrecto
    """
    lines = [line.strip() for line in text.strip().split('\n') if line.strip()]
    
    if len(lines) < 2:
         raise ValueError(f"Faltan las dos primeras líneas (n y m). Se encontraron solo {len(lines)} líneas.")

    try:
        # Línea 1: n (número de personas)
        n = int(lines[0])
        
        # Línea 2: m (número de opiniones)
        m = int(lines[1])
        
        # VALIDACIÓN DE LONGITUD DESPUÉS DE OBTENER M
        # El número total de líneas esperadas es 4 (n, m, p, v) + m (filas de s) + 2 (ct, max_movs)
        expected_lines = 4 + m + 2
        if len(lines) < expected_lines:
             raise ValueError(f"Faltan líneas de datos. Se esperaban {expected_lines} líneas para m={m}, pero se encontraron {len(lines)}.")
        
        # Línea 3: p (distribución inicial)
        p = [int(x.strip()) for x in lines[2].split(',')]
        if len(p) != m:
            raise ValueError(f"p debe tener {m} elementos (igual a m), pero tiene {len(p)}")
        
        # Línea 4: v (valores de opiniones)
        v = [float(x.strip()) for x in lines[3].split(',')]
        if len(v) != m:
            raise ValueError(f"v debe tener {m} elementos (igual a m), pero tiene {len(v)}")
        
        # Líneas 5 a 4+m: s (matriz m x 3 de resistencias)
        s = []
        for i in range(4, 4 + m):
            row = [int(x.strip()) for x in lines[i].split(',')]
            if len(row) != 3:
                raise ValueError(f"Cada fila de s debe tener 3 valores (baja, media, alta), pero la fila {i-3} tiene {len(row)}")
            s.append(row)
        
        # Línea 4+m+1: ct (costo total máximo)
        ct = float(lines[4 + m])
        
        # Línea 4+m+2: max_movs (movimientos máximos)
        max_movs = int(lines[4 + m + 1]) 
        
        # Validaciones adicionales
        if n <= 0:
            raise ValueError("n debe ser positivo")
        if m <= 0:
            raise ValueError("m debe ser positivo")
        if sum(p) != n:
            raise ValueError(f"La suma de p ({sum(p)}) debe ser igual a n ({n})")
        
        # Verificar que s sume p
        for i in range(m):
            if sum(s[i]) != p[i]:
                raise ValueError(
                    f"En opinión {i+1}: s[{i+1}] suma {sum(s[i])} pero p[{i+1}] = {p[i]}. "
                    f"Deben ser iguales."
                )
        
        if ct < 0:
            raise ValueError("ct debe ser no negativo")
        if max_movs < 0: 
            raise ValueError("max_movs debe ser no negativo")
        
        return {
            'n': n,
            'm': m,
            'p': p,
            'v': v,
            's': s,
            'ct': ct,
            'max_movs': max_movs 
        }
        
    except (ValueError, IndexError, TypeError) as e:
        # Captura errores si los datos no son números o el índice es incorrecto.
        raise ValueError(f"Error en el formato de datos o número de elementos: {e}")


def generate_dzn(parsed: Dict, output_path: str = None) -> str:
    n = parsed['n']
    m = parsed['m']
    p = parsed['p']
    v = parsed['v']
    s = parsed['s']
    ct = parsed['ct']
    max_movs = parsed['max_movs']
    
    # Formatear la lista p
    p_str = '[' + ', '.join(map(str, p)) + ']'
    
    # Formatear la lista v (con decimales)
    v_str = '[' + ', '.join(f"{val:.6f}" for val in v) + ']'
    
    # CORRECCIÓN PARA array[int, int]: Formato MiniZinc [| row1 | row2 | ... |]
    s_rows = []
    for row in s:
        # Crea la cadena de la fila: "1, 2, 3"
        s_rows.append(', '.join(map(str, row)))
        
    # Une las filas usando el separador de matriz de MiniZinc '|', 
    # y añade los delimitadores externos [| y |]
    s_str = '[| ' + ' | '.join(s_rows) + ' |]'
    
    # Construir el contenido del .dzn
    dzn_content = f"""% Archivo generado automáticamente
% Datos para el problema de minimización de polarización

n = {n};
m = {m};
p = {p_str};
v = {v_str};
s = {s_str};
ct = {ct};
maxMovs = {max_movs};
""" 
    
    # Guardar si se proporciona una ruta
    if output_path:
        Path(output_path).write_text(dzn_content, encoding='utf-8')
    
    return dzn_content


def parse_and_generate(input_txt_path: str, output_dzn_path: str) -> Dict:
    """
    Función conveniente que lee un .txt, lo parsea y genera el .dzn.
    """
    text = Path(input_txt_path).read_text(encoding='utf-8')
    parsed = parse_input_text(text)
    generate_dzn(parsed, output_dzn_path)
    
    return parsed