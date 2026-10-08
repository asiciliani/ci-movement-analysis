# Plan de Tesis de Licenciatura

**Título propuesto:** *Escucha física en Contact Improvisation: medición del acoplamiento interpersonal desde video con un tracker de dúos validado.*
**Carrera:** Licenciatura en Ciencias de la Computación (FCEN - UBA)
**Tesista:** [Tu Nombre] · **Director/a:** [A definir] · **Co-director/a:** [A definir]

---

## 1. Resumen
El Contact Improvisation (CI) es una práctica diádica en la que dos personas comparten peso y
momentum sin coreografía. Esta tesis construye y valida un instrumento de visión por computadora
para medir el **acoplamiento cinemático** entre dos bailarines a partir de video ordinario, y lo
usa para responder una pregunta concreta: **¿el acoplamiento entre los bailarines persiste cuando
no están en contacto físico?** (la "escucha física" que la comunidad describe cualitativamente).

## 2. Por qué esta rama y no otras (evidencia de la prueba de concepto, octubre 2026)
* Es la única pregunta que el instrumento puede contestar con un diseño propio. Con video público
  **no se puede decidir** (auditoría del 7/10, `AUDIT.md` 24-31): en 5 de 10 clips "dúo" el par
  trackeado era incorrecto (espectadores, una sombra, un montaje, un trío); el test de
  desplazamiento circular da "acoplamiento" también en esos pares equivocados; en los 6 clips con
  las personas correctas el acoplamiento sobrevive todos los nulos (incluidos pseudo-pares, 5/6),
  pero son casi todo contacto (control positivo), y sin contacto se pudo testear 1 clip (n.s.). La solución es de diseño: grabar en cada sesión un bloque solo-solo (mismo
  cuarto, cámara y silencio, sin relacionarse) como nulo que comparte todos los confundidores.
* **Validación externa con verdad conocida (7/10):** en los datos públicos de Bigand et al. (2024,
  *Current Biology*; 35 díadas, 1.120 ensayos con/sin cortina × misma/distinta música) el test
  ingenuo da "acoplamiento" en 63 % de los ensayos sin ningún canal entre los bailarines, mientras
  que nuestro contraste dentro de la díada (ver vs cortina) detecta el acoplamiento por el compañero
  (27-28 de 35 díadas, p < 0.001) y sobrevive degradado a video 2-D con ruido. Con 8 ensayos de 1 min
  por condición, 15-20 díadas dan potencia 0.8-0.98 (AUDIT 34-37). En CoMPAS3D (salsa, roles
  conocidos) el retardo NO identifica a quien lidera (AUDIT 36).
* Las medidas de suavidad por ventana (SPARC, jerk) están dominadas por el ruido del estimador de
  pose a 24-30 fps (ventanas adyacentes con 75 % de solapamiento correlacionan ≈ 0). Sirven sólo
  agregadas por minutos, y por eso la hipótesis del "eco somático" (A-B-A) queda como estudio
  secundario condicionado a grabaciones a 60 fps calibradas.
* El tracking en contacto es el problema técnico real: la detección simultánea cae de 89 % a 65 %
  en ventanas de contacto, y la verificación manual muestra etiquetas en terceros tras los
  levantamientos. Validarlo es una contribución de Computación en sí misma.

## 3. Hipótesis
* **H3 (acoplamiento):** la correlación cruzada con retardo entre las velocidades de los dos
  bailarines supera la batería de nulos de `METHODS.md` §7 (circular, local, bandas, cámara,
  escala, audio, pseudo-pares); el test circular solo es necesario pero no suficiente.
* **H3b (escucha física, contraste primario):** en frames **sin** contacto, el acoplamiento del
  bloque dúo-sin-contacto (N) es mayor que el del bloque solo-solo (S) de la misma díada
  (Wilcoxon entre díadas), y mayor que el de pseudo-pares entre díadas.
* **H3c (liderazgo) — descartada tal como estaba:** en CoMPAS3D (salsa, roles conocidos, mocap) el
  retardo de la correlación de señales de cuerpo entero no identifica a quien lidera (AUDIT 36).
  Sólo se retoma si una medida direccional a nivel de miembros se valida antes en ese dataset.
* **H1 (secundaria):** la suavidad agregada difiere entre contacto y no contacto (el PoC sugiere
  *menor* suavidad en contacto).

## 4. Metodología
1. **Instrumento.** YOLOv8-pose + BoT-SORT/ReID + capa de asignación de dos bailarines con cue de
   apariencia (color de ropa), compensación del movimiento de cámara, derivadas sólo sobre tramos
   detectados, unidades calibradas, piso de ruido por grabación (`METHODS.md`).
2. **Validación del tracker.** Auditoría de par (¿son las dos personas correctas?) como compuerta de
   inclusión, y anotación manual de identidad en ≥ 10 clips × 30 s (hojas de contacto de
   `audit_identity.py`); métricas: fracción de frames con etiqueta correcta, intercambios A/B,
   captura de terceros (espectadores, sombras). Taxonomía de fallas del corpus público como
   resultado. Comparación con y sin cue de apariencia y con/sin ReID.
3. **Corpus.** (a) Clips públicos filtrados automáticamente (cámara fija o compensable, dos personas
   de cuerpo entero, ≥ 640 px, ≥ 24 fps); (b) grabaciones propias con cámara fija, grilla de piso,
   consentimiento y comité de ética (`DATA_COLLECTION_PROTOCOL.md`).
4. **Análisis.** Tests dentro de cada video y combinación entre videos (test de signos, Wilcoxon,
   estimador intra-grupo con errores robustos); nulos por datos sustitutos para toda correlación.

## 5. Avances (PoC auditada)
Pipeline en dos etapas con tracks crudos; filtro de cámara; compensación; unidades; piso de ruido;
tests sintéticos; `analyze_claims.py` reproduce todos los números del plan desde `outputs/dataset/`.

## 6. Trabajo futuro (fuera de la tesis)
Eco somático A-B-A con grabaciones a 60 fps; grafos de proximidad en jams; modelos predictivos;
aplicaciones clínicas o de robótica.

## 7. Cronograma (6 meses)
* **Mes 1:** corpus propio (≥ 6 dúos, cámara fija) + anotación de identidad en 10 clips.
* **Mes 2:** validación del tracker (métricas de identidad; ablaciones apariencia / ReID).
* **Mes 3:** acoplamiento H3/H3b/H3c en el corpus propio (N vs S); el corpus público sólo como
  validación del instrumento y demostración de los nulos.
* **Mes 4:** H1 agregada; robustez (ventanas, umbral de contacto, surrogates alternativos).
* **Mes 5:** redacción y figuras reproducibles.
* **Mes 6:** correcciones y defensa.
