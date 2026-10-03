# Bibliografía Recomendada (Estado del Arte)

Este documento recopila la bibliografía científica esencial para enmarcar la tesis sobre cinemática del Contact Improvisation (CI) en las áreas de Biomecánica, Ciencias Cognitivas y Computer Vision.

## 1. Computer Vision y Oclusión Severa (El Problema Técnico)

Para justificar por qué analizar CI es un desafío de vanguardia en Computer Vision, debes referenciar la literatura sobre "Close Human Interaction":
* **Fieraru, M., Zanfir, M., Oneata, E., Popa, A. I., Olaru, V., & Sminchisescu, C. (CVPR 2020).** *"Three-dimensional Reconstruction of Human Interactions"*. 
  * *Por qué leerlo:* Este grupo (y su dataset FlickrCI3D) demuestra matemáticamente por qué los trackers top-down tradicionales fallan cuando las personas se abrazan, luchan o bailan, debido a la fusión de *bounding boxes*.
* **OpenPose / YOLOv8-Pose Literature:** Referencias estándar sobre la estimación top-down vs bottom-up.

## 2. Ciencias Cognitivas y Contact Improvisation (El Sentido)

Para explicar el fenómeno del "Escucha Física" (Sincronización), el referente mundial es Asaf Bachrach (Investigador del CNRS y bailarín de CI):
* **Bachrach, A., et al. (2018).** *"Coordinated Interpersonal Behaviour in Collective Dance Improvisation: The Aesthetics of Kinaesthetic Togetherness"*.
  * *Por qué leerlo:* Mide empíricamente cómo los bailarines se sincronizan sin un líder claro (ideal para justificar tu análisis de Cross-Correlation).
* **Bachrach, A., et al. (2024).** *"De-sync: disruption of synchronization as a key factor in individual and collective creative processes"*.
* **Novack, C. J. (1991).** *"Sharing the dance: contact improvisation and American culture"*. 
  * *Por qué leerlo:* El texto fundacional antropológico sobre el CI. (Citado más de 300 veces).

## 3. Biomecánica (La Matemática del "Yield")

Para justificar por qué medir el *Jerk* (la tercera derivada) equivale a medir la suavidad y prevención de colisiones:
* **Flash, T., & Hogan, N. (1985).** *"The coordination of arm movements: an experimentally confirmed mathematical model"*.
  * *Por qué leerlo:* Es el paper clásico de biomecánica ("Minimum Jerk Model"). Demuestra que el sistema nervioso humano programa el movimiento para minimizar el Jerk. En el CI, esto se lleva al extremo al interactuar con el piso y otros cuerpos bajo gravedad compartida.
