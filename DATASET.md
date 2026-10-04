# The "Somatic Echo" Kinematics Dataset

Este documento actúa como registro del dataset de videos de *Contact Improvisation* que se están procesando para la tesis. El objetivo es construir el primer dataset cinemático a gran escala de interacciones humanas de alta oclusión.

## Videos Procesados / En Proceso

| ID | Archivo / Link | Origen | Descripción | Estado |
|----|---------------|--------|-------------|---------|
| 01 | `user_ci_video.mp4` | Archivo Personal | Gastón y Paula (Original PoC). Vuelos, caídas y oclusión extrema. | ✅ Completado |
| 02 | `el_club_ci.mov` | Archivo Personal | Jam grupal en "El Club". Prueba de estrés para el Tracker Bipartito (múltiples personas). | 🔄 Procesando (4K) |
| 03 | `public_ci_video.mp4` | YouTube (`NGf03Yg6fM0`) | Dueto clásico de YouTube. Extracción de 2 minutos. | ✅ Completado |
| 04 | `exploration_video.mp4` | YouTube (`zkreiRt8GEY`) | Dueto de alta calidad aportado por la tesista. Procesando video completo. | 🔄 Procesando |
| 05+ | `gaston_channel_*.mp4` | YouTube (`@gastonnoguera4953`) | Scraping automatizado de todo el canal de Gastón Noguera. Creación de dataset longitudinal. | 🤖 Scrapeando |

## Estructura de Salida
Por cada video en este dataset, el pipeline genera:
* `[video]_features.csv`: Series temporales crudas (17 Keypoints, Jerk, Energía, Distancias).
* `[video]_annotated.mp4`: Video renderizado con el HUD de telemetría y esqueletos YOLOv8.
* `[video]_report.html`: Dashboard estadístico interactivo.
