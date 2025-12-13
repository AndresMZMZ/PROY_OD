# gui_pysimple.py
"""
Interfaz gráfica para el proyecto de Minimización de Polarización.
Permite cargar archivos .txt, generar .dzn y ejecutar el modelo MiniZinc.
"""

import PySimpleGUI as sg
from pathlib import Path
import json

# Importar módulos locales
from generar_dzn import parse_input_text, generate_dzn
from run_mzn import MiniZincRunner
from generar_salida import generate_output_txt
 
# CONFIGURACIÓN DE RUTAS Y CONSTANTES 
BASE_DIR = Path(__file__).resolve().parent
PROJECT_ROOT = BASE_DIR.parent
MZN_DIR = PROJECT_ROOT / "ProyectoMZN"
DEFAULT_MZN = str(MZN_DIR / "Proyecto.mzn")
SAVED_DZN = str(MZN_DIR / "DatosProyecto.dzn")

# Constante para evitar duplicación de literales
ALL_FILES = "All Files" 

 
# DISEÑO DE LA INTERFAZ 
sg.theme('DarkBlue3')

layout = [
    [
        sg.Text("🎯 MinPol - Minimización de Polarización", font=("Arial", 14, "bold")),
        sg.Push(),
        sg.Button("Salir", button_color=("white", "red"))
    ],
    [sg.HorizontalSeparator()],
    
    # Sección de entrada
    [sg.Frame("📄 Entrada (formato .txt del enunciado)", [
        [sg.Multiline(
            size=(90, 12),
            key="-INPUT-",
            font=("Courier", 10),
            tooltip="Pega el contenido del archivo .txt o usa 'Cargar archivo .txt'"
        )],
        [
            sg.Button("📂 Cargar archivo .txt", key="-LOAD-"),
            sg.Text("", size=(50, 1), key="-LOADED-FILE-", text_color="green")
        ]
    ], font=("Arial", 10, "bold"))],
    
    [sg.HorizontalSeparator()],
    
    # Configuración del modelo
    [sg.Frame("⚙️ Configuración del Modelo", [
        [
            sg.Text("Archivo .mzn:", size=(12, 1)),
            sg.Input(DEFAULT_MZN, key="-MZN-", size=(60, 1), readonly=True),
            sg.FileBrowse("Buscar", file_types=(("MiniZinc", "*.mzn"),))
        ],
        [
            sg.Text("Solver:", size=(12, 1)),
            sg.Combo(["gecode", "chuffed", "coin-bc", "gurobi"], 
                      default_value="gecode", 
                      key="-SOLVER-",
                      size=(15, 1),
                      tooltip="Usa gecode para pruebas pequeñas, gurobi para grandes (requiere licencia)"),
            sg.Text("Timeout (seg):", pad=((20, 5), 0)),
            sg.Input("300", key="-TIMEOUT-", size=(8, 1), tooltip="Tiempo máximo de ejecución (0 = sin límite)")
        ]
    ], font=("Arial", 10, "bold"))],
    
    [sg.HorizontalSeparator()],
    
    # Botones de acción
    [
        sg.Button("▶️ Generar .dzn y Ejecutar", key="-RUN-", size=(25, 1), button_color=("white", "green")),
        sg.Button("📝 Generar .dzn (solo)", key="-GEN-", size=(20, 1)),
        sg.Button("💾 Guardar .dzn como...", key="-SAVE-", size=(20, 1)),
        sg.Push(),
        sg.Button("💾 Guardar salida .txt", key="-SAVE-OUT-", size=(20, 1), disabled=True),
        sg.Button("🧹 Limpiar", key="-CLEAR-")
    ],
    
    [sg.HorizontalSeparator()],
    
    # Sección de salida
    [sg.Frame("📊 Resultados", [
        [sg.Multiline(
            size=(100, 14),
            key="-OUT-",
            font=("Courier", 9),
            disabled=True,
            autoscroll=True
        )]
    ], font=("Arial", 10, "bold"))],
    
    # Barra de estado
    [sg.StatusBar("Listo. Carga un archivo o pega la entrada.", size=(120, 1), key="-STATUS-", relief=sg.RELIEF_SUNKEN)]
]

window = sg.Window(
    "MinPol - Proyecto ADA II",
    layout,
    finalize=True,
    resizable=True,
    icon=None 
)

 
# INICIALIZAR RUNNER DE MINIZINC 
try:
    runner = MiniZincRunner()
    window["-STATUS-"].update(f"✅ MiniZinc encontrado: {runner.minizinc}")
except Exception as e:
    runner = None
    window["-STATUS-"].update(f"⚠️ Advertencia: {e}")
    sg.popup_warning(
        f"No se encontró MiniZinc en PATH.\n\n{e}\n\n"
        "Puedes continuar generando .dzn, pero no podrás ejecutar el modelo.",
        title="MiniZinc no encontrado"
    )

 
# LOOP PRINCIPAL DE LA INTERFAZ 
ultimo_resultado = None 

while True:
    event, values = window.read()
    
    # Evento: Cerrar ventana o botón Salir
    if event in (sg.WINDOW_CLOSED, "Salir"):
        break
    
    # Evento: Cargar archivo .txt
    if event == "-LOAD-":
        filename = sg.popup_get_file(
            "Seleccione archivo .txt de entrada",
            #   Usar la constante ALL_FILES
            file_types=(("Text Files", "*.txt"), (ALL_FILES, "*.*")), 
            initial_folder=str(PROJECT_ROOT / "BateriaPruebas")
        )
        if filename:
            try:
                txt = Path(filename).read_text(encoding="utf-8")
                window["-INPUT-"].update(txt)
                window["-LOADED-FILE-"].update(f"📁 {Path(filename).name}")
                window["-STATUS-"].update(f"✅ Archivo cargado: {filename}")
            except Exception as e:
                sg.popup_error(f"Error leyendo archivo:\n{e}")
                window["-STATUS-"].update("❌ Error cargando archivo")
    
    # Evento: Limpiar
    if event == "-CLEAR-":
        window["-INPUT-"].update("")
        window["-OUT-"].update("")
        window["-LOADED-FILE-"].update("")
        window["-STATUS-"].update("🧹 Limpiado")
        window["-SAVE-OUT-"].update(disabled=True)
        ultimo_resultado = None
    
    # Evento: Generar .dzn solamente
    if event == "-GEN-":
        txt = values["-INPUT-"].strip()
        if not txt:
            sg.popup_error("No hay texto de entrada.\nCarga un archivo o pega el contenido.")
            continue
        
        try:
            parsed = parse_input_text(txt)
            dzn_text = generate_dzn(parsed, SAVED_DZN)
            window["-OUT-"].update(dzn_text)
            window["-STATUS-"].update(f"✅ .dzn generado en: {SAVED_DZN}")
        except Exception as e:
            sg.popup_error(f"Error parseando entrada:\n\n{e}")         
            window["-STATUS-"].update("❌ Error en parseo")
    
    # Evento: Guardar .dzn como...
    if event == "-SAVE-":
        txt = values["-INPUT-"].strip()
        if not txt:
            sg.popup_error("No hay texto de entrada.")
            continue
        
        save_path = sg.popup_get_file(
            "Guardar .dzn como",
            save_as=True,
            #   Usar la constante ALL_FILES
            file_types=(("DZN Files", "*.dzn"), (ALL_FILES, "*.*")),
            default_extension=".dzn",
            initial_folder=str(MZN_DIR)
        )
        if not save_path:
            continue
        
        try:
            parsed = parse_input_text(txt)
            dzn_text = generate_dzn(parsed, save_path)
            window["-OUT-"].update(dzn_text)
            window["-STATUS-"].update(f"💾 .dzn guardado en: {save_path}")
            sg.popup_ok(f"Archivo guardado correctamente:\n{save_path}")
        except Exception as e:
            sg.popup_error(f"Error creando .dzn:\n\n{e}")
            window["-STATUS-"].update("❌ Error guardando")
    
    # Evento: Generar .dzn y EJECUTAR modelo
    if event == "-RUN-":
        mzn_path = values["-MZN-"]
        txt = values["-INPUT-"].strip()
        solver = values["-SOLVER-"]
        
        # Validaciones
        if not txt:
            sg.popup_error("No hay texto de entrada.\nCarga un archivo o pega el contenido.")
            continue
        
        if not Path(mzn_path).exists():
            sg.popup_error(f"No se encontró el archivo .mzn:\n{mzn_path}\n\nSelecciona el Proyecto.mzn correcto.")
            continue
        
        if not runner:
            sg.popup_error("MiniZinc no está disponible.\nNo se puede ejecutar el modelo.")
            continue
        
        # Parsear entrada
        try:
            parsed = parse_input_text(txt)
        except Exception as e:
            sg.popup_error(f"Error parseando entrada:\n\n{e}")
            window["-STATUS-"].update("❌ Error en parseo")
            continue
        
        # Generar .dzn
        try:
            dzn_path = SAVED_DZN
            generate_dzn(parsed, dzn_path)
            window["-STATUS-"].update(f"⏳ Ejecutando MiniZinc con {solver}... (esto puede tomar tiempo)")
            window.refresh()
        except Exception as e:
            sg.popup_error(f"Error generando .dzn:\n\n{e}")
            window["-STATUS-"].update("❌ Error generando .dzn")
            continue
        
        # Ejecutar MiniZinc
        try:
            timeout_val = int(values["-TIMEOUT-"])
            if timeout_val <= 0:
                timeout_val = None
        except ValueError: 
            timeout_val = 300
        
        try:
            res = runner.run(mzn_path, dzn_path, solver=solver, timeout=timeout_val)
        except Exception as e:
            # Capturar errores de ejecución de forma segura
            res = {"error": str(e), "raw": "Error al intentar ejecutar el modelo."} 
            sg.popup_error(f"Error ejecutando MiniZinc:\n\n{e}")
            window["-STATUS-"].update("❌ Error de ejecución") 
        
        # Mostrar resultado
        if isinstance(res, dict) and "error" in res:
            error_msg = f"❌ ERROR:\n{res.get('error')}\n\n"
            if "raw" in res:
                error_msg += f"SALIDA CRUDA:\n{res.get('raw')}"
            window["-OUT-"].update(error_msg)
            window["-STATUS-"].update("❌ Error al ejecutar MiniZinc")
            window["-SAVE-OUT-"].update(disabled=True)
            ultimo_resultado = None
            sg.popup_error(f"Error ejecutando modelo:\n\n{res.get('error')}")
        else:
            # Guardar resultado
            ultimo_resultado = res
            
            # Formatear resultado bonito
            output_text = "✅ SOLUCIÓN ENCONTRADA\n" + "=" * 60 + "\n\n"
            output_text += json.dumps(res, indent=2, ensure_ascii=False)
            window["-OUT-"].update(output_text)
            
            # Habilitar botón de guardar
            window["-SAVE-OUT-"].update(disabled=False)
            
            # Extraer polarización si existe
            if "polarizacion" in res:
                pol = res["polarizacion"]
                window["-STATUS-"].update(f"✅ Ejecución exitosa | Polarización: {pol}")
            else:
                window["-STATUS-"].update("✅ Ejecución finalizada correctamente")
    
    # Evento: Guardar salida como .txt
    if event == "-SAVE-OUT-":
        if not ultimo_resultado:
            sg.popup_error("No hay resultado para guardar.\nEjecuta el modelo primero.")
            continue
        
        save_path = sg.popup_get_file(
            "Guardar salida como .txt",
            save_as=True,
            #   Usar la constante ALL_FILES
            file_types=(("Text Files", "*.txt"), (ALL_FILES, "*.*")),
            default_extension=".txt",
            initial_folder=str(MZN_DIR)
        )
        
        if not save_path:
            continue
        
        try:
            salida_txt = generate_output_txt(ultimo_resultado, save_path)
            window["-STATUS-"].update(f"💾 Salida guardada en: {save_path}")
            sg.popup_ok(f"Archivo de salida guardado:\n{save_path}\n\n{salida_txt}")
        except Exception as e:
            sg.popup_error(f"Error generando salida:\n\n{e}")
            window["-STATUS-"].update("❌ Error guardando salida")

# Cerrar ventana
window.close()