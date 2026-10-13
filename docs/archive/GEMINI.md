# Tesis LIAA: Reglas del Proyecto (Project Guidelines)

Estas reglas dictan la arquitectura del proyecto y cómo el agente debe comportarse al editar archivos.

## 1. Separación de Repositorios (Iglesia y Estado)

Mantenemos una estricta separación entre el código de investigación y la escritura de la tesis.

### Repositorio Público (`/home/andisici/Documents/Exactas/tesis`)
- **Propósito:** Software científico open-source, pipelines de Machine Learning (YOLO, OpenCV), métricas.
- **Qué va aquí:** `src/`, `run_analysis.py`, archivos `README.md` técnicos, `DATASET.md`, y los `.csv` resultantes (Features).
- **Qué NO va aquí:** Archivos de video binarios crudos (`*.mp4`, `*.mov`), borradores de emails, notas de reuniones, ensayos o PDFs teóricos.

### Repositorio Privado (`/home/andisici/Documents/Exactas/tesis_escritura`)
- **Propósito:** La "cocina" privada de la tesis.
- **Qué va aquí:** Textos de capítulos, el diario de laboratorio (`07_Bitacora_de_Lab/`), ideas crudas (`01_Marco_Teorico/`), el dataset en video original (`06_Dataset_Crudo/`) y pitches de reuniones (`02_Reuniones_Pitch/`).
- **Qué NO va aquí:** Código Python ejecutable.

## 2. Desarrollo del Pipeline de CI
- Todos los scripts Python de análisis residen en el repositorio público.
- Si se incorporan métricas de la literatura (ej. LMA, SPARC, LDLJ), deben aislarse en módulos limpios (ej. `src/features/smoothness.py`).
- Siempre aplicar el filtro de oclusión y usar la distancia del Centro de Gravedad de ambos bailarines para medir el flujo del dueto.
