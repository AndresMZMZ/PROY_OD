# generar_salida.py
"""
Módulo para generar archivos de salida .txt según el formato del proyecto.

Formato de salida (.txt):
1. Polarización (float con 3 decimales)
2. Nivel de resistencia (1 para baja)
3. m líneas con matriz de movimientos para resistencia baja
4. Nivel de resistencia (2 para media)
5. m líneas con matriz de movimientos para resistencia media
6. Nivel de resistencia (3 para alta)
7. m líneas con matriz de movimientos para resistencia alta
"""

from pathlib import Path
from typing import Dict
import math 


def format_polarization(pol_value):
    """
    Formatea la polarización como entero si es 0, o con decimales si no.
    
    Args:
        pol_value: Valor de polarización (puede ser float o string)
        
    Returns:
        String formateado
    """
    try:
        pol_float = float(pol_value)
        
        # Usar math.isclose() para comparar flotantes con seguridad.
        if math.isclose(pol_float, 0.0): 
            return "0"
        else:
            # limitar a 3 decimales.
            return f"{pol_float:.3f}".replace('.', ',') 
            
    # Especificar la excepción para evitar capturar errores inesperados.
    except (ValueError, TypeError): 
        return str(pol_value)


def generate_output_txt(resultado: Dict, output_path: str = None) -> str:
    """
    Genera el contenido de un archivo de salida .txt a partir del JSON de MiniZinc.
    
    Args:
        resultado: Dict con el resultado del modelo (JSON parseado)
        output_path: Ruta donde guardar el archivo (opcional)
        
    Returns:
        String con el contenido del archivo .txt
    """
    # Extraer datos
    # Nota: .get() es seguro y devuelve 0.0 o {} si la clave no existe.
    polarizacion = resultado.get("polarizacion", 0.0)
    matrices = resultado.get("matrices_movimiento", {})
    
    # Obtener dimensión (m) desde las matrices
    resistencia_baja = matrices.get("resistencia_baja", [])
    m = len(resistencia_baja)
    
    if m == 0:
        raise ValueError("No se encontraron matrices de movimiento en el resultado")
    
    resistencia_media = matrices.get("resistencia_media", [])
    resistencia_alta = matrices.get("resistencia_alta", [])
    
    # Construir contenido
    lines = []
    
    # Línea 1: Polarización
    lines.append(format_polarization(polarizacion))
    
    # Resistencia BAJA (k=1)
    lines.append("1")
    for fila in resistencia_baja:
        lines.append(",".join(map(str, fila)))
    
    # Resistencia MEDIA (k=2)
    lines.append("2")
    for fila in resistencia_media:
        lines.append(",".join(map(str, fila)))
    
    # Resistencia ALTA (k=3)
    lines.append("3")
    for fila in resistencia_alta:
        lines.append(",".join(map(str, fila)))
    
    # Unir con saltos de línea
    output_content = "\n".join(lines)
    
    # Guardar si se proporciona ruta
    if output_path:
        Path(output_path).write_text(output_content, encoding='utf-8')
    
    return output_content


def resultado_a_formato_proyecto(json_resultado: Dict) -> str:
    """
    Convierte un resultado JSON de MiniZinc al formato de texto del proyecto.
    
    Args:
        json_resultado: Dict con la salida del modelo
        
    Returns:
        String con el formato de salida requerido
    """
    return generate_output_txt(json_resultado)