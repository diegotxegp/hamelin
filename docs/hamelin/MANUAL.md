# HAMELIN — Manual de usuario

**HAMELIN** (Human-guided Automated Machine Learning for Clinical Studies) es una aplicación de escritorio para profesionales de investigación clínica (CRPs) que necesitan gestionar estudios clínicos, analizar datos de pacientes y construir modelos predictivos — sin necesidad de saber programar ni de conocimientos de Machine Learning.

Este documento describe, con el detalle suficiente para trabajar sin sorpresas, cómo está organizada la aplicación y qué hace cada pantalla. Está escrito a partir del código y de los textos de ayuda ya integrados en la propia app (página **Help**), no es una traducción libre: cuando algo aquí discrepe de lo que ves en pantalla, la aplicación manda.

> Para quién no es Hamelin: no sustituye a un bioestadístico o data scientist para análisis complejos, no gestiona consentimientos informados ni documentación regulatoria, no es un CDMS (úsalo junto a tu EDC — REDCap, OpenClinica, etc.), y no envía datos a ningún servicio en la nube: todo corre localmente en tu máquina.

---

## 1. Instalación y primer arranque

**Requisitos:**
- Windows 10/11 (64-bit), macOS 12+, o Ubuntu 20.04+.
- Python 3.12 (gestionado por `uv`).
- RAM: 8 GB mínimo; 16 GB recomendado para datasets grandes (>10.000 filas).
- Disco: espacio para la app + tus datasets.

**Arranque:**
```bash
cd hamelin/
uv run hamelin
```
En el primer arranque se muestra la página **Home** sin proyectos. No hace falta configuración previa.

**Modo debug** (más detalle en el log, trazas completas en los diálogos de error):
```bash
uv run hamelin --debug
```
Otros flags: `--config <ruta>` (config personalizada), `--version`, `--no-gui`.

---

## 2. Flujo de trabajo recomendado

```
PROJECT  →  DATA  →  TRAINING  →  MODELS
                                     │
                              FORECASTING (opcional)
```

1. **Project**: crea o abre un proyecto y rellena los metadatos del estudio.
2. **Data**: carga el dataset de pacientes (CSV, Excel, SPSS...). La generación de **Table 1** vive al final de esta misma pestaña.
3. **Training**: entrena un modelo predictivo con AutoML.
4. **Models**: página dedicada (justo después de Training en el menú) para inspeccionar y comparar todos los modelos entrenados en el proyecto.

**Forecasting** es opcional: predice cuándo alcanzarás tu objetivo de reclutamiento; úsalo si es relevante para tu estudio.

Cada paso es una pestaña del menú lateral izquierdo (Help y Settings están fijados abajo del todo; el resto, incluidos Models y Forecasting, está en la lista principal). Puedes ir hacia adelante y hacia atrás libremente.

![Página Home de Hamelin](images/home_page.png)
*Página Home: resumen rápido de proyectos, datasets y modelos, con acceso al resto de la app desde el menú lateral.*

---

## 3. Página "Project" (Proyectos)

![Página Projects con New Project, Quick Project y Delete All Projects](images/project_page.png)
*Pantalla selectora de proyectos, con los tres botones de acción arriba y las tarjetas de proyectos guardados debajo.*

### 3.1 Pantalla selectora
Al entrar en "Project" ves una lista de tarjetas, una por proyecto guardado, con nombre, tipo de estudio, nº de datasets/modelos y fecha de última modificación. Cada tarjeta tiene:
- **Select**: marca el proyecto como activo sin abrir su formulario de metadatos.
- **Open**: abre el formulario completo de metadatos de ese proyecto.

Arriba de la lista hay tres botones:

| Botón | Qué hace |
|---|---|
| **New Project** | Abre el formulario en blanco para crear un proyecto rellenando todos los campos. |
| **Quick Project** | Se salta el formulario: crea un proyecto al instante con datos de marcador de posición generados automáticamente (nombre, acrónimo, número de protocolo con timestamp). Útil para empezar a cargar datos ya; abre el proyecto después desde esta misma pantalla para rellenar los datos reales. |
| **Delete All Projects** | Borra permanentemente **todos** los proyectos guardados y todo su contenido (datasets, resultados, modelos), tras una confirmación. No se puede deshacer. Si tenías un proyecto abierto en otras pestañas (Data, Training...) en el momento de borrar, esas pestañas no se limpian automáticamente hasta que navegues o reinicies. |

### 3.2 Formulario de metadatos

| Campo | Obligatorio | Notas |
|---|---|---|
| Project Name | Sí | Nombre completo oficial del estudio. |
| Acronym | Sí | Código corto en mayúsculas, único, solo letras y números. **No se puede cambiar después de guardar** — es el nombre de la carpeta en disco. |
| Protocol Number | Sí | Identificador oficial del protocolo. |
| Principal Investigator | Sí | Nombre del investigador principal. |
| Contact Email | Sí | Debe tener formato de email válido. |
| Institution | Sí | Hospital/universidad/centro. |
| Study Type | No | Patient Registry / Observational Study / Clinical Trial. |
| Ethics Committee / Approval Number / Approval Date | No | Sección de aprobación ética. |
| Target Sample Size | Sí (>0) | Nº de pacientes objetivo; lo usa la página Forecasting. |
| Start Date / Expected End Date | No | Fechas de reclutamiento, también usadas en Forecasting. |
| Primary Objective / Secondary Objectives | No | Texto libre; aparece tal cual en los informes generados. |

Botones del formulario: **Save Project**, **Reset** (limpia el formulario), **← Back to Projects** (descarta sin guardar).

### 3.3 Dónde se guarda todo

```
workspace/Projects/<ACRÓNIMO>/          (nombre de carpeta siempre en inglés, "Projects")
    metadata.json                        : metadatos del proyecto
    data/                                 : datasets vinculados a este proyecto
    data/dataset_index.json               : registro de datasets
    results/                              : resultados de entrenamiento y exportaciones
```

Puedes hacer copia de seguridad de toda la carpeta `Projects/` a cualquier sitio. Fuera de un proyecto concreto:

```
workspace/logs/hamelin_YYYY-MM-DD.log     : log técnico de la app (uno por día)
workspace/logs/usage_log.csv              : registro de uso — ver sección 11
workspace/data/                            : datasets sueltos, aún no vinculados a un proyecto
```

`workspace/` está excluido de git (no se sube al repositorio); es contenido local, generado por el uso de la app.

---

## 4. Página "Data"

![Página Data con un dataset real cargado](images/data_page.png)
*Dataset real cargado (768 filas × 9 columnas): métricas arriba, vista previa de la tabla en el centro, y la lista de Variables & Types debajo (mientras se analiza en segundo plano).*

### 4.1 Formatos soportados
CSV, TSV, Excel (`.xlsx`, primera hoja), Parquet, JSON/JSONL, Feather, HDF5, HTML (una sola tabla), SPSS (`.sav`), Stata (`.dta`), SAS (`.xpt`, `.sas7bdat`), Ancho Fijo (`.fwf`), DataFrame serializado (`.pkl`/`.pickle` — abre solo ficheros de confianza). Son los 14 formatos que documenta Ludwig oficialmente. Requisitos: cabecera en la primera fila, una fila por paciente, sin celdas combinadas ni formato decorativo (en Excel).

### 4.2 Cargar un dataset
1. **Browse** → selecciona el fichero.
2. **Load**.

Con un proyecto activo, el fichero se copia automáticamente a `data/` del proyecto y queda registrado para recargarlo luego desde el selector "Project datasets", sin tener que volver a buscarlo. HAMELIN detecta automáticamente el tipo de cada columna y lanza en segundo plano un análisis con Ludwig para inferir el tipo de variable más adecuado para ML.

### 4.3 Vista previa y edición
La tabla de vista previa muestra todas las filas y columnas. Valores especiales: `NaN` (número faltante), `NaT` (fecha faltante), celda vacía (igual que los anteriores en la práctica), `inf` (desbordamiento numérico — trátalo como problema de calidad de datos).

- Clic en cabecera de columna → modo "selección de columnas". Clic en nº de fila → modo "selección de filas". Ctrl/Shift para selección múltiple.
- **Remove Selected**: oculta lo seleccionado del análisis (no se borra de verdad).
- **Restore All**: recupera todo lo oculto.
- **Remove Duplicates**: elimina filas duplicadas.
- **Exclude Outliers** / **Restore Excluded**: excluye/recupera outliers.
- **Export**: exporta el dataset "limpio" (con lo oculto ya fuera) en CSV, Excel o Word.

### 4.4 Lista de variables y tipos (Variable List)
Cada columna aparece con su tipo inferido: 🔢 number, ⭕ binary, 📝 category, 📅 date, 📄 text, 📈 sequence, ⏱ timeseries, ➡ vector. El análisis puede tardar hasta ~30s en datasets grandes (la primera vez que se usa en una sesión, ver sección 10.2 sobre el coste de importación de Ludwig).

Puedes anular el tipo de cualquier columna con el desplegable "Set type" junto a ella (la fila se resalta). **Reset Types to Inferred** revierte todas las anulaciones manuales (nunca toca los valores reales del dataset).

### 4.5 Informe de calidad y resumen
- **Generate Quality Report**: CSV con una fila por variable (tipo, nulos, % faltante, valores únicos, min/max/media para numéricas). Tú eliges dónde guardarlo.
- **Data Summary**: tarjeta de texto plano con un resumen del dataset, visible en la propia página; **Export Data Summary** lo guarda en `.txt`/`.md`.
- Gráfico automático de las 10 variables con más datos faltantes.

### 4.6 Table 1 (características basales)
Vive al final de esta misma pestaña Data (no tiene su propio botón "Browse" — usa el dataset ya cargado arriba).

1. En "Select Variables for Table 1", cada columna aparece marcada por defecto; las que HAMELIN sugiere excluir (identificadores, texto libre, varianza cero...) o que parecen buena variable de agrupación aparecen marcadas directamente en su fila.
2. **Apply All Recommendations** actúa sobre esas sugerencias automáticamente, o marca/desmarca tú mismo.
3. En "Table Settings": **Grouping Variable** (opcional — variable categórica que divide la tabla en grupos y añade un test estadístico: t-test/ANOVA para numéricas, Chi-cuadrado/Fisher para categóricas), **Missing data** (mantener o descartar filas con valores faltantes), **Show p-values**.
4. **Generate Table 1**.
5. **Export**: CSV, Excel o Word.

Interpretación: numéricas → media±DE (normal) o mediana (RIC) (sesgada); categóricas → n (%); p-valor <0.05 → diferencia significativa entre grupos.

---

## 5. Página "Forecasting" (opcional)

![Página Forecasting](images/forecasting_page.png)
*Página de pronóstico de reclutamiento (estado vacío, antes de generar una proyección).*

Ajusta un modelo estadístico sobre el ritmo de reclutamiento histórico para estimar cuándo se alcanzará el **Target Sample Size** del proyecto.

**Entradas necesarias:** un dataset cargado con una columna de fecha de inclusión (una fila por paciente), y el Target Sample Size (viene precargado desde los metadatos del proyecto).

**Parámetros:**
- **Enrollment Date Column**: solo se listan columnas de tipo fecha.
- **Target Sample Size**: editable aquí, aunque venga precargado.
- **Historical Period (days)**: cuántos días pasados usar para estimar la velocidad de reclutamiento (por defecto 90).
- **Confidence Level**: intervalo de confianza de la fecha estimada (0.95 por defecto).

**Gráfico**: línea sólida = reclutamiento histórico acumulado; línea discontinua = proyección; banda sombreada = intervalo de confianza (si es muy ancha, el reclutamiento ha sido irregular); líneas horizontales/verticales discontinuas = objetivo y fecha estimada.

**Panel de estado actual**: pacientes reclutados, objetivo, restantes, tasa media mensual, fecha de inicio del estudio.

**Export Timeline CSV**: tabla de hitos mensuales (mes, esperado, límite inferior/superior).

---

## 6. Página "Training"

### 6.1 Concepto
Entrenar un modelo significa enseñar a un programa a reconocer patrones en tus datos asociados a un resultado clínico de interés. HAMELIN usa **AutoML vía Ludwig**: selecciona y configura automáticamente el mejor algoritmo — no necesitas saber qué es un Random Forest o una red neuronal.

### 6.2 Paso 1 — Variables
- **Outcome variable**: la columna que quieres predecir.
- **Predictor variables**: clic para seleccionar (Ctrl/Shift para varias; no hay "Select All"). Regla general: incluye variables disponibles ANTES de conocer el resultado; excluye ID de paciente, códigos administrativos y columnas de fecha; excluye variables con >50% de valores faltantes salvo que vayas a imputarlas.
- **Secondary outcomes** (opcional): otros resultados clínicos a predecir junto al principal — esto entrena un modelo multi-output real, no es solo anotación. Una columna marcada a la vez como predictor y como resultado secundario se trata solo como predictor.

### 6.3 Paso 2 — Criterios de selección de pacientes
Constructor visual de reglas de inclusión/exclusión (Columna, Operador, Valor — sin caja de texto libre). Un paciente que NO cumple TODAS las reglas de inclusión queda excluido; un paciente que cumple CUALQUIER regla de exclusión también. Botón **Preview** en cada bloque para ver cuántas filas coinciden antes de comprometerte. **Save preset** / **Reset preset** guardan estos criterios como JSON reutilizable del proyecto, bajo `training_schemas/`.

### 6.4 Paso 3 — Configuración del modelo

Solo se muestran tres campos por defecto; el resto vive tras "▶ Advanced options".

| Campo | Detalle |
|---|---|
| **Model name** | Obligatorio. Nombre de la carpeta donde se guarda el modelo; aparecerá en el Historial y en "Models". |
| **Prediction type** | Binary classification (2 valores) / Multi-class classification (≥3 categorías) / Regression (número continuo). No es solo una sugerencia: fuerza a Ludwig a entrenar ese tipo de modelo. |
| **Evaluation metric** | **La lista cambia según el Prediction type**, porque Ludwig solo soporta ciertas métricas por tipo de salida: <br>• **Binary**: AUC-ROC, Accuracy, Precision, Recall, Specificity.<br>• **Multi-class**: Accuracy, Hits at K.<br>• **Regression**: RMSE, MAE, MSE, RMSPE (todas miden error medio — cuanto más bajo, mejor). |

### 6.5 Opciones avanzadas

![Sección Model Configuration con Advanced options desplegado](images/training_page_advanced.png)
*"Advanced options" desplegado: Time Budget y Final evaluation holdout se escriben directamente (sin flechas), Early Stopping y Missing numeric values strategy son las opciones nuevas. Con "Binary classification" seleccionado, Handle Class Imbalance está habilitado (aunque en este ejemplo sigue en Off, su valor por defecto); si se cambia a Multi-class o Regression, el interruptor se desactiva automáticamente.*

| Campo | Detalle |
|---|---|
| **Time budget (minutos)** | Límite de tiempo de búsqueda. El entrenamiento se detiene al alcanzarlo aunque no se hayan completado las iteraciones máximas. **Se escribe directamente en el campo** (sin flechas de incremento). |
| **Final evaluation holdout (%)** | Porcentaje de pacientes apartado ANTES de entrenar, nunca usado en el entrenamiento — solo para la evaluación final. Por defecto `0.20`. **Se escribe directamente** (p.ej. `0.2`), sin flechas. *(Nota técnica: este holdout se separa fuera de Ludwig antes de pasarle los datos; Ludwig hace además su propio split interno del resto — no es exactamente el mismo mecanismo que `preprocessing.split` de la configuración nativa de Ludwig.)* |
| **Random Seed** | Asegura resultados reproducibles entre ejecuciones con la misma semilla. |
| **Search strategy** | No optimisation (valores por defecto de Ludwig, más rápido) / Random search / Bayesian optimization (recomendado, más eficiente) / Grid Search (Exhaustive search — prueba TODAS las combinaciones, muy lento). |
| **Max. iterations** | Nº máximo de configuraciones a probar (si hay estrategia de búsqueda activa). Recomendado: 50–100. |
| **Parallel trials** | Núcleos de CPU a usar en paralelo. |
| **Early stopping (rounds)** | Rondas consecutivas de evaluación sin mejora antes de parar automáticamente. Por defecto 5; pon -1 para desactivarlo. |
| **Handle Class Imbalance** | Interruptor. **Solo disponible para Binary classification** — Ludwig no soporta balanceo de clases para multiclase ni regresión, así que el interruptor aparece desactivado (gris) y se desmarca automáticamente en esos casos. |
| **Missing numeric values strategy** | Desplegable (ya no es un simple interruptor on/off) con las estrategias reales que documenta Ludwig para columnas numéricas: *Ludwig default* (rellena con 0, sin tocar nada), *Fill with column mean*, *Fill with most frequent value*, *Forward fill*, *Backward fill*, *Drop rows with missing value*. |

### 6.6 Entrenar y monitorizar
1. **Start Training** (solo activo con un dataset cargado).
2. Barra de progreso y log de entrenamiento en tiempo real — no cierres la app mientras entrena.
3. Al terminar, el panel de Resultados muestra 4 tarjetas según lo entrenado: clasificación (AUC-ROC, Accuracy, Sensitivity, Specificity) o regresión (R², RMSE, MAE, Loss); cualquier otra métrica de Ludwig aparece en una línea más pequeña. Matriz de confusión y curva ROC para tareas de clasificación, cuando están disponibles.
4. **Stop** cancela en cualquier momento; se muestran los resultados parciales hasta el último trial completado.

**Interpretación rápida:**
- AUC-ROC: 0.5 = azar, 0.7 = aceptable, 0.8 = bueno, 0.9 = excelente (verifica que no haya data leakage), 1.0 = casi siempre indica fuga de datos.
- R²: 1.0 = ajuste perfecto, 0.7–0.9 = bueno/excelente, 0.5–0.7 = moderado, <0.5 = débil, <0 = peor que predecir siempre la media (el target puede no ser predecible con esos predictores).
- RMSE/MAE: mismas unidades que la variable de resultado; MAE más fácil de interpretar directamente, RMSE penaliza más los errores grandes.

**Export Trained Model**: guarda los artefactos del modelo en un ZIP (para predecir sobre pacientes nuevos, compartir, o archivar). Los resultados de cada entrenamiento también se guardan automáticamente en `results/` del proyecto.

---

## 7. Página "Models"

Vista dedicada (entre Training y Forecasting en el menú) a **todos** los modelos entrenados en el proyecto, no solo el último.

- Comparar varios modelos lado a lado según la métrica que elijas.
- Inspeccionar un modelo en profundidad (matriz de confusión, curva ROC, hiperparámetros usados).
- **Duplicar** un modelo con ligeros cambios: precarga Training con esa configuración; nada se guarda hasta que le des a entrenar de nuevo.
- Marcar favoritos y borrar modelos que ya no necesites.

Necesita un proyecto abierto para saber dónde buscar.

---

## 8. Página "Settings"

![Página Settings](images/settings_page.png)
*Página de configuración: apariencia, idioma, preferencias de exportación y opciones avanzadas.*

| Sección | Contenido |
|---|---|
| **Appearance** | Tema (Light/Dark/Auto según el SO) y tamaño de fuente (8–16pt, aplica sin reiniciar). |
| **Language** | Español/English — el cambio de idioma de la interfaz requiere reiniciar la app. Los informes generados (Table 1, Quality Report) siempre se generan en el idioma seleccionado aquí. |
| **Export Preferences** | Ya no hay un formato de exportación "por defecto" global: se elige en cada momento junto al botón de exportar correspondiente. Lo que queda aquí es **Decimal Places** (decimales en los informes exportados; 2 recomendado para informes clínicos, 4 para análisis interno). |
| **Advanced: Log Level** | DEBUG / INFO (por defecto) / WARNING / ERROR — verbosidad del log técnico. |
| **Debug mode** | Vía línea de comandos (`uv run hamelin --debug`), no desde aquí. |

---

## 9. Página "Help"

Manual de ayuda integrado en la propia app, con **8 secciones**: 1 Introduction, 2 Getting Started, 3 Projects, 4 Data (Table 1 incluido como parte de esta sección, no aparte), 5 Training, 6 Models (sección propia, en el mismo orden que el menú de navegación), 7 Forecasting, 8 Glossary. Settings no tiene sección propia — es autoexplicativo en pantalla. Cada sección es expandible/colapsable; botones **Expand All** / **Collapse All** arriba. Casi todos los campos de la interfaz tienen además un icono "?" propio que abre una explicación puntual sin salir de la página en la que estás.

Varios bloques incluyen ahora **capturas reales de la propia aplicación** directamente dentro del texto de ayuda (no solo en este manual externo) — por ejemplo, al expandir "Getting Started" verás la captura real de la pantalla de Proyectos con sus botones. Esto se implementó añadiendo soporte de imágenes a los bloques de ayuda (`_Block` en `help_page.py`); las imágenes viven en `src/hamelin/resources/help_images/` y no dependen de traducción (se muestran igual en inglés y español).

---

## 10. Arquitectura de la aplicación (para quien la mantenga)

### 10.1 Dos interfaces coexistiendo
HAMELIN tiene, a día de hoy, **dos capas de interfaz gráfica**:
- `src/hamelin/view/` + `controller/` + `model/` — la arquitectura MVC actual, descrita en todo este manual.
- `src/hamelin/interface/` — una app "modo simple" más antigua, con su propio `MainWindow`, widgets y utilidades, **embebida como la página "Models"** dentro de la interfaz nueva (`view/main_window.py`, carga perezosa con manejo de errores para que un fallo ahí no tumbe el resto de la app).

No es un accidente ni código muerto: sigue en uso activo. Retirarla o fusionarla con `view/` es un trabajo de esfuerzo medio-alto (reimplementar esa página en el stack nuevo, migrar ~26 archivos de test), pendiente para más adelante.

### 10.2 Por qué la primera carga de un dataset puede tardar
La inferencia de tipo de variable (sección 4.4) usa `ludwig.automl.base_config`, que internamente importa **todo** el subsistema de esquemas de Ludwig (encoders, decoders, combiners, hasta el esquema de modelos LLM, y `torchmetrics`) — no solo la parte de tipos. La primera vez que se usa en una sesión, esa importación puede tardar bastante (decenas de segundos en máquinas modestas). HAMELIN precalienta esa importación en segundo plano al arrancar (ver `prewarm_ludwig_type_inference()` en `analytics/variable_analyzer.py`), pero si cargas un dataset en los primeros segundos tras abrir la app, puedes notar el retraso igualmente. No es un fallo de HAMELIN — es el coste real de esa función concreta de Ludwig.

### 10.3 Todas las opciones de Training están verificadas contra la documentación oficial de Ludwig
Las métricas, estrategias de búsqueda y restricciones (p.ej. el balanceo de clases solo para binary) mostradas en la sección 6 de este manual se han contrastado explícitamente contra la documentación oficial de Ludwig (vendida localmente en `docs/ludwig/`, fuera del repositorio git). Si Ludwig se actualiza a una versión con un esquema de configuración distinto, esta sección debería revisarse de nuevo contra la doc de esa versión.

### 10.4 Esquema: de la pantalla Training a la configuración real de Ludwig

Ningún widget de la pantalla Training habla con Ludwig directamente. Todo pasa por un diccionario intermedio ("fields") que solo lleva lo que el usuario cambió de su valor neutro, y una función pura (`_fields_to_user_config`) que lo traduce a la sintaxis real de Ludwig:

```
┌─────────────────────┐      ┌───────────────────┐      ┌──────────────────────────┐
│  TrainingPage (UI)   │      │   fields: dict     │      │  Ludwig user_config      │
│                      │      │  (solo lo tocado)  │      │                          │
│  Prediction type ────┼─────▶│ problem_type       │      │ output_features[0].type  │
│  Evaluation metric ──┼─────▶│ metric              ├─────▶│ trainer.validation_metric│
│  Early stopping ─────┼─────▶│ early_stop          │      │ trainer.early_stop       │
│  Search strategy ────┼─────▶│ search, max_iter,   │      │ hyperopt.search_alg,     │
│                      │      │ parallel_trials     │      │ hyperopt.executor        │
│  Handle Imbalance ───┼─────▶│ class_imbalance      │      │ preprocessing.           │
│  (solo si binary)    │      │ (+ problem_type)    │      │ oversample_minority      │
│  Missing values ─────┼─────▶│ missing_strategy     │      │ defaults.number.         │
│  strategy            │      │                      │      │ preprocessing.           │
│                      │      │                      │      │ missing_value_strategy   │
└─────────────────────┘      └───────────────────┘      └──────────────────────────┘
                                                                      │
                                                                      ▼
                                                        auto_train(user_config=...)
                                                     (se fusiona con lo que Ludwig
                                                      infiere automáticamente del
                                                      dataset — nada se pisa si el
                                                      usuario no tocó esa opción)
```

Por eso un campo dejado en su valor por defecto **no** se envía a Ludwig — se deja que Ludwig decida, en vez de forzar explícitamente su propio valor por defecto. Ver `src/hamelin/analytics/automl/ludwig_backend.py::_fields_to_user_config`.

---

## 11. Registro de uso (usage log)

Aparte del log técnico, HAMELIN guarda en `workspace/logs/usage_log.csv` un registro estructurado de **qué hace el usuario en la interfaz**: clics en botones, campos de formulario rellenados, navegación entre páginas, con marca de tiempo (segundos incluidos) para cada evento. Es un CSV con columnas `timestamp, session_id, page, action, element, detail`, pensado para poder analizarse directamente en Excel/pandas — por ejemplo, para un estudio de usabilidad y eficacia de la herramienta.

Es un fichero separado del log técnico a propósito: uno es texto libre para depurar errores, el otro son datos tabulares para análisis. Ambos viven en `workspace/logs/`, fuera del control de versiones.

---

## 12. Glosario rápido

| Término | Significado |
|---|---|
| AutoML | Software que selecciona y configura automáticamente el mejor algoritmo para un dataset dado. |
| AUC-ROC | Métrica (0–1) de cuán bien un clasificador binario separa positivos de negativos. |
| Holdout set | Parte de los datos apartada del entrenamiento, usada solo para la evaluación final. |
| Hiperparámetro | Ajuste que controla cómo aprende el algoritmo (p.ej. learning rate), distinto de los parámetros que el modelo aprende de los datos. |
| Data leakage | Cuando información del futuro o del propio resultado se cuela en los datos de entrenamiento, dando un rendimiento irrealmente alto. |
| Ludwig | Framework de AutoML de código abierto (originalmente de Uber AI) que HAMELIN usa para entrenar modelos e inferir tipos de variable. |
| Overfitting | Cuando un modelo aprende demasiado bien los datos de entrenamiento y no generaliza a pacientes nuevos. |
| Random seed | Número que inicializa el generador aleatorio, para que los splits y las inicializaciones sean reproducibles. |

(Glosario clínico y de formatos de fichero completo disponible en la propia página Help de la app.)
