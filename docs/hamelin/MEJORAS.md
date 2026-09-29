# HAMELIN — Lista de mejoras propuestas

Resultado de recorrer toda la aplicación (proyecto → datos → Table 1 → entrenamiento → evaluación → predicción → previsión de reclutamiento → ayuda/ajustes), de una ejecución completa de extremo a extremo con datos reales y de contrastarla con la documentación oficial de Ludwig 0.17 (`docs/ludwig/`). Ordenada por **valor clínico/científico frente a esfuerzo**. Cada punto indica de dónde sale (observación en la app o sección de la doc de Ludwig).

Leyenda de esfuerzo: **S** = horas, **M** = días, **L** = semanas.

---

## P1 — Victorias rápidas (alto valor, esfuerzo S–M)

| # | Mejora | Por qué / de dónde sale | Esf. |
|---|---|---|---|
| 1 | **IC 95 % también para AUC-ROC, sensibilidad, especificidad, precisión y recall** en Evaluation. | Hoy solo se calculan para exactitud/R²/RMSE/MAE porque la vieja `test_predictions.csv` no tenía probabilidades por clase. Ahora sí (`y_prob_<clase>`, ver `LudwigBackend._build_predictions_frame`), así que el *bootstrap* de `interface/utils/bootstrap_ci.py` puede ampliarse. Es la métrica que más se cita en clínica. | S |
| 2 | **Curva de calibración y curva precisión-recall** en Evaluation. | `docs/ludwig/03_user_guide/user_guide__visualizations.md` (*Calibration Plot*, *Precision Recall Curves*, *Binary Threshold vs. Metric*). Un AUC alto con probabilidades mal calibradas es peligroso en clínica. | M |
| 3 | **Ofrecer `calibration: true`** (escalado de temperatura) como opción en Training. | `configuration__features__binary_features.md` y `category_features.md`: `calibration` (por defecto `false`) reajusta las probabilidades con el conjunto de validación. Casi gratis: una casilla + una clave en `_fields_to_user_config`. | S |
| 4 | **Corregir el desajuste de la métrica de regresión**: la primera opción de la lista («RMSE») no se envía a Ludwig y este optimiza MSE. | `training_page.py` (`metric_combo.currentIndex() != 0`). Para binaria/multiclase coincide con el defecto de Ludwig; para regresión no. Enviar siempre la métrica elegida. | S |
| 5 | **Aviso de datos fuera de rango en Prediction** (por fila y global): valores a más de 3 DE de la media de entrenamiento, o categorías no vistas. | `training_report.json` ya guarda media y DE por variable (`data_schema.input_features`). Evita usar el modelo en pacientes distintos a los del entrenamiento (HCAI: límites visibles). | M |
| 6 | **Anonimizar el `usage_log.csv`**: hoy `field_filled` guarda el valor de campos como email o investigador principal. | `metadata_page._log_filled_fields`. Para un estudio con participantes conviene registrar solo *qué* campo se rellenó (y su longitud), no el contenido. | S |
| 7 | **Traducir al español los textos que ya están en `strings.py`** (avisos, etiquetas y ayudas de Training, Data, Forecasting, Metadata y Table 1). | Los textos en inglés se movieron del código a `strings.py` (herramienta `tools/extract_ui_strings.py`); el español lleva de momento el mismo texto inglés como marcador. `python tools/untranslated_strings.py` lista lo pendiente. | M |
| 8 | **Modo «entrenamiento rápido» sin Ray/hyperopt** (una sola configuración por defecto de Ludwig, en segundos). | «Duplicate and Retrain» ya usa `train_with_config` y tarda ~40 s frente a >6 min de AutoML (medido en la ejecución de extremo a extremo). Útil para explorar datasets y para demos. | M |
| 9 | **Mostrar el tiempo restante y explicar el sobrepaso del límite**: con 300 s el entrenamiento tardó ≈ 370–400 s (arranque de Ray, último trial, evaluación). | Medido en la ejecución completa. Poner «límite de búsqueda» en la etiqueta y una cuenta atrás. | S |
| 10 | **Prueba de humo automática**: convertir `tests/` lentos en marcas (`@pytest.mark.slow`) y arreglar o eliminar los 5 tests de `tests/interface/` que fallan. | La suite tarda ≈ 13 min; los fallos previos ocultan regresiones nuevas. | S |

---

## P2 — Mejoras metodológicas (esfuerzo M)

| # | Mejora | Por qué / de dónde sale |
|---|---|---|
| 11 | **División de datos por paciente (sin fuga)**: elegir una columna de ID y separar por grupo (`hash`) o por fecha (`datetime`). | `configuration__preprocessing.md` (*Splitting*: `random`, `fixed`, `stratify`, `datetime`, `hash`). Con medidas repetidas por paciente, la división aleatoria filtra información al test y sobrestima el rendimiento. Hoy Hamelin separa el hold-out por su cuenta con estratificación simple. |
| 12 | **Validación cruzada k-fold** con media ± DE de las métricas. | `user_guide__api__LudwigModel.md`: `kfold_cross_validate`. Con n de cientos de pacientes (lo normal en clínica) un único hold-out da intervalos muy anchos. |
| 13 | **Pesos de clase y submuestreo**: exponer `positive_class_weight`, `class_weights` (categórica) y `undersample_majority`. | `binary_features.md` y `category_features.md` (`class_weights`, `positive_class_weight`), `configuration__preprocessing.md` (*Data Balancing*). Hoy solo hay `oversample_minority` y solo para binaria. |
| 14 | **Umbral de decisión en el propio modelo** (`threshold` de la salida binaria) y análisis de decisión: sensibilidad/especificidad frente a umbral, curva de decisión. | `binary_features.md` (`threshold`, por defecto 0,5), `user_guide__visualizations.md` (*Binary Threshold vs. Metric*, *Confidence Thresholding*). La matriz de confusión con umbral de Evaluation ya lo explora; falta poder **guardarlo** y usarlo en Prediction. |
| 15 | **Importancia de variables / explicabilidad** (SHAP o la de Ludwig) por modelo y por paciente. | Es el requisito HCAI de transparencia más pedido. Verificar en la doc de Ludwig 0.17 qué método de explicación ofrece antes de implementar; si no, permutation importance con las predicciones guardadas. |
| 16 | **Curvas de aprendizaje** (pérdida por época) y **informe de hyperopt**. | `user_guide__visualizations.md` (*Learning Curves*, `hyperopt_report`). Hoy solo se guardan métricas finales (`_FlatTrainStats` con un valor por métrica), así que no se ve sobreajuste ni cuántas configuraciones se probaron. |
| 17 | **Selección de arquitectura**: dejar elegir el *combiner* (`concat`, `tabnet`, `ft_transformer`, `tab_transformer`) además de AutoML. | `configuration__combiner.md`, `configuration__encoder_selection_guide.md`. En la ejecución real AutoML eligió `Ft_transformer` con 768 filas: un MLP/`concat` sería más razonable y rápido para tabulares pequeños. |
| 18 | **Reglas de calidad clínica**: rangos plausibles por variable (edad 0–120…), y detección de «cero = dato faltante» (p. ej. `insu` o `skin` en diabetes). | La exclusión de *outliers* a 3 DE es solo estadística y no distingue errores de valores raros pero válidos. |
| 19 | **Modelo tipo *model card* / TRIPOD-AI**: exportar un PDF con uso previsto, población, datos, métricas con IC, calibración, subgrupos y limitaciones. | Une lo que ya existe (informe del modelo, Table 1, notas) en el documento que exigen revistas y comités. Muy alineado con HCAI (responsabilidad y trazabilidad). |
| 20 | **Auditoría / trazabilidad**: registrar quién, cuándo y con qué versión del dataset (hash) y de Ludwig se entrenó cada modelo, y bloquear predicciones con datasets de esquema distinto. | `training_report.json` ya guarda versiones y semilla; falta mostrarlo y verificarlo en Prediction. |

---

## P3 — Ampliaciones de mayor alcance (esfuerzo L)

| # | Mejora | Notas |
|---|---|---|
| 21 | **Exportar el modelo para despliegue**: ONNX / `torch.export` y servidor REST. | `user_guide__model_export.md`, `user_guide__serving.md`. Hoy «Export Trained Model» guarda un informe JSON, no un modelo reutilizable fuera de Hamelin. |
| 22 | **Datos no tabulares**: texto libre (notas clínicas), imágenes, series temporales. | Ludwig los soporta (`configuration__features__text_features.md`, `image_features.md`, `time_series_features.md`) y es su mayor ventaja; la interfaz solo trata número/categoría/binaria/fecha. |
| 23 | **Gestión de proyectos**: renombrar, duplicar, archivar, exportar/importar como ZIP, varias versiones de dataset con comparación. | Ahora solo se crea, abre y borra. |
| 24 | **Equidad por subgrupos** más completa: sensibilidad/especificidad y calibración por grupo, no solo exactitud. | Evaluation → *Break down by* muestra solo la exactitud por grupo. |
| 25 | **Accesibilidad**: paleta segura para daltonismo también en gráficos (mapa de calor viridis ya lo es), navegación por teclado, tamaños de fuente, contraste alto, etiquetas para lectores de pantalla. | El cuestionario HCAI (bloque D) mide bienestar/carga cognitiva; conviene cubrirlo con auditoría WCAG básica. |
| 26 | **Empaquetado y distribución**: instaladores firmados (Windows/macOS), actualizaciones automáticas, integración continua que construya y pruebe el ejecutable. | `hamelin.spec` ya genera un ejecutable en carpeta; falta CI y firma. |
| 27 | **Retirar `src/hamelin/interface/`** (≈ 8 000 líneas de la app antigua y sus tests) cuando ya solo se use su lógica sin Qt: moverla a `analytics/`. | Tras portar la página Evaluation, lo único vivo son utilidades (`get_model_paths.py`, `metric_labels.py`, `bootstrap_ci.py`, `print_confusion_matrix.py`). |

---

## Observaciones concretas de la ejecución completa (a vigilar)

- El entrenamiento AutoML con **300 s de límite tardó ≈ 370–400 s** en total (ver P1-9).
- **Ray arranca en cada entrenamiento** (≈ 10–20 s) y deja avisos en consola de `experiment_state`/«Could not fetch metrics for trial…» para trials interrumpidos por el límite de tiempo: son inocuos pero asustan a un usuario que mire la consola.
- (Resuelto) La clave sin uso `model.default_time_limit` se eliminó de la configuración: el valor por defecto (500 s) vive en el campo de Training.
- La página **Dashboard** sigue oculta y sin sección de ayuda: decidir si se recupera (con notas/proveniencia dentro de Evaluation) o se elimina.
- Los ficheros grandes (`data_page.py` ≈ 2 100 líneas, `training_page.py` ≈ 1 900) se benefician de dividirse por secciones, como se ha hecho con `evaluation_page.py` y sus paneles.
