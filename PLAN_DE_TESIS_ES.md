# Plan de Tesis de Licenciatura

**Título propuesto:** *Cinemática Computacional: Extracción Empírica de Firmas de Movimiento en Contact Improvisation.*  
**Carrera:** Licenciatura en Ciencias de la Computación (FCEN - UBA)  
**Tesista:** [Tu Nombre]  
**Director/a:** [A definir]  
**Co-director/a:** [A definir]  

---

## 1. Resumen

El *Contact Improvisation* (CI) es una práctica de movimiento diádico donde los bailarines comparten peso de forma continua. Esta tesis propone investigar computacionalmente si es posible **detectar empíricamente los "rasgos" (firmas cinemáticas) que definen al CI** utilizando Inteligencia Artificial. Mediante técnicas de Visión en Computadora (Estimación de Pose 2D) y análisis de series temporales, se extraerán las métricas físicas fundamentales que separan a un dúo de CI de cualquier otra interacción humana: la evasión de colisiones (minimización de *Jerk*), la transferencia de momentum, y la sincronización (escucha física).

## 2. Motivación y Planteo del Problema

La mayoría de las investigaciones en análisis computacional del movimiento se centran en posturas aisladas o deportes estructurados. El análisis de interacciones humanas de alta oclusión (como el CI) representa un desafío abierto en Computer Vision. 
El problema central es: **¿Cuáles son las firmas matemáticas exactas de un dúo de Contact Improvisation exitoso?** Al extraer estos rasgos empíricamente, podemos cuantificar habilidades somáticas que antes se consideraban puramente subjetivas.

## 3. Firmas Cinemáticas (Traits) Analizadas

Se extraerá la cinemática 2D de videos reales (jams, prácticas y performances) para detectar empíricamente tres rasgos fundamentales del CI:

### Rasgo 1: "The Yield" (Ceder al impacto)
* **Concepto:** El bailarín absorbe la fuerza extendiendo el tiempo de desaceleración al ir al suelo o chocar con su compañero.
* **Firma Matemática:** Minimización del **Jerk** ($\frac{da}{dt}$). Un algoritmo activo de "Yield" aplana la curva de jerk, evitando picos de colisión.

### Rasgo 2: "Momentum Ride" (Transferencia de Energía)
* **Concepto:** Los expertos redirigen el momentum existente en lugar de usar fuerza muscular.
* **Firma Matemática:** Conservación de la **Energía Cinética del Sistema** ($E_{total} \approx E_A + E_B$). Cuando el bailarín A frena, la energía se transfiere al bailarín B sin perder fluidez.

### Rasgo 3: "Physical Listening" (Acoplamiento de Osciladores)
* **Concepto:** Los cuerpos se sincronizan para compartir el centro de gravedad.
* **Firma Matemática:** Alta **Correlación Cruzada (Cross-Correlation)** temporal entre las velocidades de ambos bailarines, comportándose matemáticamente como un péndulo acoplado.

## 4. Diseño Experimental (Análisis Descriptivo)

Se abandonan los protocolos de laboratorio rígidos (como el A-B-A) en favor de un análisis ecológico y descriptivo. Se procesará un corpus de videos de CI extraídos de *jams* y prácticas reales. El análisis comparará empíricamente:
1. Las distribuciones de Jerk y Energía entre bailarines **Novatos vs. Expertos** para probar que los "rasgos del CI" son habilidades motrices adquiribles.
2. Momentos de danza individual vs. danza de contacto dentro del mismo flujo natural para observar cuándo se activan las firmas de acoplamiento.

## 5. Avances Previos (Prueba de Concepto - PoC)

Para validar la viabilidad computacional de este proyecto, ya se ha desarrollado una Prueba de Concepto (PoC) en Python. El pipeline actual es capaz de:
* Ingestar videos crudos de *Contact Improvisation*.
* Extraer el esqueleto de múltiples bailarines y mantener sus identidades.
* Calcular derivadas de alto orden (Aceleración y Jerk) mediante filtros de Savitzky-Golay.
* Estimar proxies de Energía Cinética y proximidad espacial.
* Generar dashboards visuales (KDE, Boxplots) y videos anotados automáticamente.

La existencia de este pipeline garantiza que el riesgo técnico central (la extracción de features cinemáticos) está resuelto.

## 6. Extensión Exploratoria: Arquitectura Híbrida (YOLO + VLMs)

Durante situaciones de oclusión severa (ej. *puppy piles* o levantamientos invertidos), los trackers heurísticos top-down como YOLO suelen fallar al generar "esqueletos araña". Como extensión exploratoria, se propone diseñar conceptualmente un **Tracker Híbrido**:
1. **Pipeline Base:** YOLOv8 procesa los frames a alta velocidad.
2. **Trigger de Oclusión:** Cuando la intersección (IoU) de dos *bounding boxes* supera un umbral crítico (ej. > 0.85), el sistema pausa.
3. **Escalamiento Semántico:** Ese frame se envía a un Modelo Fundacional Multimodal (VLM) para desenredar los cuerpos basándose en contexto semántico.

## 7. Arquitectura Computacional

1. **Computer Vision:** YOLOv8-Pose con tracking de identidad persistente (bipartite Hungarian matching).
2. **Procesamiento de Señales:** Filtrado Savitzky-Golay para suavizar el ruido temporal.
3. **Análisis de Series Temporales:** Análisis de Componentes Principales (PCA) y métricas de correlación temporal.
4. **Modelado Estadístico:** Modelos Lineales Mixtos (LMM) y distribuciones de densidad (KDE).

## 8. Cronograma Propuesto (6 Meses)

* **Mes 1:** Recolección de corpus de videos (jams y prácticas) y curaduría de clips.
* **Mes 2:** Refinamiento del pipeline de estimación de pose sobre los videos recolectados.
* **Mes 3:** Extracción de features (Jerk, Energía, Cross-Correlation) y validación de las señales.
* **Mes 4:** Análisis estadístico descriptivo (Novatos vs Expertos, Distribuciones).
* **Mes 5:** Redacción de la tesis y generación de visualizaciones (Storytelling Graphs).
* **Mes 6:** Correcciones finales y defensa.
