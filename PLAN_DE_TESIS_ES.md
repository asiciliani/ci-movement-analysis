# Plan de Tesis de Licenciatura

**Título propuesto:** *El Eco Somático: Análisis Cinemático Computacional de Transferencia de Energía y Algoritmos de Prevención de Impacto en Contact Improvisation.*  
**Carrera:** Licenciatura en Ciencias de la Computación (FCEN - UBA)  
**Tesista:** [Tu Nombre]  
**Director/a:** [A definir]  
**Co-director/a:** [A definir - idealmente perfil interdisciplinario/biomecánica/artes]  

---

## 1. Resumen

El *Contact Improvisation* (CI) es una práctica de movimiento diádico donde los bailarines comparten peso y momento de forma continua. Para evitar lesiones y mantener la fluidez, los practicantes de CI programan en su sistema nervioso "Algoritmos de Movimiento" (MAs) específicos; en particular, algoritmos para ceder ante el impacto (evasión de colisiones) y para conservar la energía cinética (uso del momentum en lugar de la fuerza muscular).

Esta tesis propone investigar computacionalmente si la interacción física con otro cuerpo reescribe temporalmente los algoritmos motores individuales de un bailarín. Utilizando técnicas de Visión en Computadora (Estimación de Pose 2D) y procesamiento de señales, se analizará si los patrones cinemáticos adquiridos durante la danza compartida persisten en el movimiento individual posterior (el "Eco Somático").

## 2. Motivación y Planteo del Problema

La mayoría de las investigaciones en análisis computacional del movimiento se centran en acciones individuales o deportes estructurados. El análisis de interacciones humanas de alta oclusión (como el CI) representa un desafío abierto en Computer Vision. 

El problema central es: **¿Cómo altera la necesidad diádica de evasión de colisiones y transferencia de momentum en CI la cinemática matemática del movimiento individual (solo) posterior de un bailarín?**

## 3. Metodología y Algoritmos Analizados

Se extraerá la cinemática 2D de videos para probar matemáticamente la existencia y transferencia de dos algoritmos principales de CI:

### MA 1: "The Yield" (Ceder al impacto y aterrizaje suave)
* **Concepto:** Al encontrarse con el suelo o con el compañero, el bailarín no se tensa ni choca, sino que absorbe la fuerza extendiendo el tiempo de desaceleración.
* **Firma Matemática:** **Jerk** (tasa de cambio de la aceleración, $\frac{da}{dt}$). Se medirá la desaceleración máxima y el *jerk* del Centro de Masa (CoM) al transicionar hacia el suelo. Un algoritmo activo de "Yield" minimiza matemáticamente el jerk.

### MA 2: "Momentum Ride" (Conservación de Energía Cinética)
* **Concepto:** En lugar de usar fuerza muscular (movimiento de arranque y parada), los expertos redirigen el momentum existente, manteniendo la fluidez del sistema.
* **Firma Matemática:** **Varianza y Suavidad de la Energía Cinética**. Se analizará el campo de vectores de velocidad, buscando curvas continuas sin estados de velocidad cero y la conservación de la energía ($E_k \approx v^2$).

## 4. Diseño Experimental (Protocolo A-B-A)

Se filmará a 10-15 parejas en una sesión continua de 10 minutos con el siguiente diseño intra-sujeto:
* **Fase A (Solo Base - 2 min):** Los bailarines se mueven de forma independiente. Establece los algoritmos de movimiento por defecto (Jerk y Energía Cinética base).
* **Fase B (Dúo de CI - 5 min):** Interacción física. La necesidad de compartir peso fuerza la activación de MA 1 y MA 2.
* **Fase C (Solo Eco - 2 min):** Se separan y vuelven a bailar solos. 

Se comparará estadísticamente la Fase A contra la Fase C. Si el descenso al suelo en la Fase C presenta un *Jerk* matemáticamente menor que en la Fase A, se probará la existencia del "Eco Somático".

## 5. Arquitectura Computacional

El desarrollo técnico para la Licenciatura incluye:
1. **Computer Vision:** Uso de YOLOv8-Pose para extracción multi-persona, junto con tracking de identidad persistente mediante bipartite Hungarian matching adaptado para manejar oclusión.
2. **Procesamiento de Señales:** Filtrado Savitzky-Golay para suavizar el ruido temporal del tracker antes de calcular derivadas de orden superior (Velocidad, Aceleración, Jerk).
3. **Análisis de Series Temporales:** Análisis de Componentes Principales (PCA) para grados de libertad, y métricas de correlación temporal.
4. **Modelado Estadístico:** Modelos Lineales Mixtos (LMM) en Python (`statsmodels`) para evaluar la significancia estadística de la diferencia entre Fase A y C considerando la dependencia intra-pareja.

## 6. Cronograma Propuesto (6 Meses)

* **Mes 1:** Reclutamiento de participantes y recolección de datos (filmación de las 15 parejas).
* **Mes 2:** Refinamiento del pipeline de estimación de pose y tracking sobre los videos recolectados.
* **Mes 3:** Extracción de features (Jerk, Energía Cinética, CoM) y validación de las series temporales.
* **Mes 4:** Análisis estadístico (Modelos Mixtos) e interpretación de resultados.
* **Mes 5:** Redacción de la tesis y generación de visualizaciones.
* **Mes 6:** Correcciones finales y defensa.
