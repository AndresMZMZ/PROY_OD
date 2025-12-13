# 🎯 MinPol - Minimización de Polarización

Proyecto de optimización discreta usando MiniZinc para minimizar la polarización en poblaciones.

---

## 📂 Estructura
```
PROY_OD/
├── BateriaPruebas/       # 35 instancias de prueba (.txt)
├── ProyectoGUIFuentes/   # Interfaz gráfica + scripts Python
├── ProyectoMZN/          # Modelo MiniZinc (Proyecto.mzn)
```

---

## 🚀 Instalación

### 1. MiniZinc
Descarga desde: https://www.minizinc.org/software.html

Verifica:
```bash
minizinc --version
```

### 2. Python
```bash
cd ProyectoGUIFuentes
pip install -r requirements.txt
```

---

## 🎮 Uso
```bash
cd ProyectoGUIFuentes
python gui_pysimple.py
```

1. Cargar archivo .txt
2. Seleccionar solver (gecode o gurobi)
3. Ejecutar
4. Guardar salida

---

## 📋 Archivos Principales

- `ProyectoMZN/Proyecto.mzn` - Modelo de optimización
- `ProyectoGUIFuentes/gui_pysimple.py` - Interfaz gráfica
- `BateriaPruebas/Prueba*.txt` - Casos de prueba

---

## ⚠️ Notas

- MiniZinc debe estar en PATH
---

## 📅 Entrega

**Fecha límite:** 14 de diciembre

**Incluir:**
- Modelo MiniZinc
- GUI funcional
- 5 instancias propias
- Informe PDF
- Video (máx 15 min)