# 📝 Text Modification Guide - HAMELIN

## 🎯 What is this system?

**Centralized text system** that allows modifying all explanatory texts of the HAMELIN application without needing to touch Python code.

## 📍 File Location

All texts are in: `Hamelin/src/texts/`

### Main files to modify:
- `clinical_trial_texts.py` - Clinical Trial texts
- `patient_registry_texts.py` - Patient Registry texts  
- `observational_study_texts.py` - Observational Study texts

## ✏️ How to Modify Texts

### 1. To change the "Primary variable" text in Clinical Trial:

Edit the `clinical_trial_texts.py` file and look for:

```python
"primary_variable": {
    "title": "Primary Outcome Variable Selection",
    "content": """
    <p style="margin-top:0px; margin-bottom:0px;">
        <span style="font-size:16pt; font-weight:600;">Primary Outcome Variable Selection</span>
    </p>
    # ... rest of content
    """
}
```

### 2. Change the content to whatever you want:

```python
"primary_variable": {
    "title": "My New Title",
    "content": """
    <p style="margin-top:0px; margin-bottom:0px;">
        <span style="font-size:16pt; font-weight:600;">My New Title</span>
    </p>
    <p style="margin-top:12px;">
        This is my new explanatory text...
    </p>
    """
}
```

## 📋 Currently Available Texts

### Clinical Trial (`clinical_trial_texts.py`):
- `primary_variable` - Primary outcome variable (supports classification AND regression)
- `criteria` - Inclusion/exclusion criteria
- `investigational_drug` - Experimental group
- `control_drug` - Control group
- `disease` - Medical condition

### Patient Registry (`patient_registry_texts.py`):
- `primary_variable` - Primary variable for registries (classification/regression)

### Observational Study (`observational_study_texts.py`):
- `primary_variable` - Variable of interest for observational studies

## 🎨 Basic HTML Format

Texts use simple HTML. Most used elements:

```html
<!-- Main title -->
<span style="font-size:16pt; font-weight:600;">Big Title</span>

<!-- Paragraph -->
<p style="margin-top:12px;">Normal text</p>

<!-- Bold text -->
<span style="font-weight:600;">Important text</span>

<!-- List -->
<ul>
    <li>Item 1</li>
    <li>Item 2</li>
</ul>
```

## 🚀 Recent System Improvements

### Support for Continuous and Discrete Variables
HAMELIN now automatically detects:
- **Continuous variables** (real decimals): For regression
- **Discrete variables** (repeated integers): For classification
- **Automatic validation**: Filters variables with insufficient samples

### Intelligent Detection
The system verifies:
- ✅ If the variable has significant decimals (not just .0)
- ✅ Unique values ratio (>50% = continuous)
- ✅ Minimum distribution of 2 samples per class

### Automatic Optimization
- ✅ **Minimize** for error metrics (MSE, RMSE, MAE)
- ✅ **Maximize** for accuracy metrics (accuracy, ROC-AUC, recall)
- ✅ Automatic correction if Ludwig misconfigures

## 💡 Recommendations When Modifying Texts

### For Primary Variable:
Mention that it now supports:
- Categorical variables (classification)
- Continuous numerical variables (regression)
- Boolean variables (binary classification)

### For Settings:
Explain that "Goal" is automatically corrected based on the selected metric.

### For Validations:
Indicate that the system automatically filters variables with distribution problems.

## 🔧 Updated Text Example

```python
"primary_variable": {
    "title": "Primary Variable Selection",
    "content": """
    <p style="margin-top:0px; margin-bottom:0px;">
        <span style="font-size:16pt; font-weight:600;">Primary Variable Selection</span>
    </p>
    <p style="margin-top:12px;">
        Select the variable you want to predict. HAMELIN supports:
    </p>
    <ul>
        <li><b>Categorical variables</b>: For classification (predicting categories)</li>
        <li><b>Continuous numerical variables</b>: For regression (predicting numbers)</li>
        <li><b>Boolean variables</b>: For binary classification</li>
    </ul>
    <p style="margin-top:12px;">
        <b>Note:</b> Variables with insufficient samples are automatically filtered.
        All classes must have at least 2 samples for cross-validation.
    </p>
    """
}
```

## 📞 Technical Support

For technical information about how the system works internally, see:
- `text_manager.py` - Main logic
- `../controller/` - Integration with controllers
- `../my_ludwig/` - AutoML system and validations

## 📌 Important Notes

1. **Always maintain HTML structure** when modifying
2. **Don't change keys** (e.g., "primary_variable") - only content
3. **Test changes** by running the application after modifying
4. **Changes are immediate** - no recompilation required

## 🎯 Future Improvements

Areas where you could add new explanatory texts:
- Explanation of regression vs classification metrics
- Details about split strategy (stratified vs random)
- Information about training cancellation process
- Explanation of automatic validations


## � Textos Actualmente Disponibles

### Clinical Trial (`clinical_trial_texts.py`):
- `primary_variable` - Variable de resultado principal (soporta clasificación Y regresión)
- `criteria` - Criterios de inclusión/exclusión
- `investigational_drug` - Grupo experimental
- `control_drug` - Grupo control
- `disease` - Condición médica

### Patient Registry (`patient_registry_texts.py`):
- `primary_variable` - Variable principal para registros (clasificación/regresión)

### Observational Study (`observational_study_texts.py`):
- `primary_variable` - Variable de interés para estudios observacionales

## 🎨 Formato HTML Básico

Los textos usan HTML simple. Elementos más usados:

```html
<!-- Título principal -->
<span style="font-size:16pt; font-weight:600;">Título Grande</span>

<!-- Párrafo -->
<p style="margin-top:12px;">Texto normal</p>

<!-- Texto en negrita -->
<span style="font-weight:600;">Texto importante</span>

<!-- Lista -->
<ul>
    <li>Elemento 1</li>
    <li>Elemento 2</li>
</ul>
```

## 🚀 Novedades Recientes del Sistema

### Soporte para Variables Continuas y Discretas
HAMELIN ahora detecta automáticamente:
- **Variables continuas** (decimales reales): Para regresión
- **Variables discretas** (enteros repetidos): Para clasificación
- **Validación automática**: Filtra variables con muestras insuficientes

### Detección Inteligente
El sistema verifica:
- ✅ Si la variable tiene decimales significativos (no solo .0)
- ✅ Ratio de valores únicos (>50% = continua)
- ✅ Distribución mínima de 2 muestras por clase

### Optimización Automática
- ✅ **Minimize** para métricas de error (MSE, RMSE, MAE)
- ✅ **Maximize** para métricas de precisión (accuracy, ROC-AUC, recall)
- ✅ Corrección automática si Ludwig configura incorrectamente

## 💡 Recomendaciones al Modificar Textos

### Para Primary Variable:
Menciona que ahora soporta:
- Variables categóricas (clasificación)
- Variables numéricas continuas (regresión)
- Variables booleanas (clasificación binaria)

### Para Settings:
Explica que el "Goal" se corrige automáticamente según la métrica seleccionada.

### Para Validaciones:
Indica que el sistema filtra automáticamente variables con problemas de distribución.

## 🔧 Ejemplo de Texto Actualizado

```python
"primary_variable": {
    "title": "Primary Variable Selection",
    "content": """
    <p style="margin-top:0px; margin-bottom:0px;">
        <span style="font-size:16pt; font-weight:600;">Primary Variable Selection</span>
    </p>
    <p style="margin-top:12px;">
        Select the variable you want to predict. HAMELIN supports:
    </p>
    <ul>
        <li><b>Categorical variables</b>: For classification (predicting categories)</li>
        <li><b>Continuous numerical variables</b>: For regression (predicting numbers)</li>
        <li><b>Boolean variables</b>: For binary classification</li>
    </ul>
    <p style="margin-top:12px;">
        <b>Note:</b> Variables with insufficient samples are automatically filtered.
        All classes must have at least 2 samples for cross-validation.
    </p>
    """
}
```

## 📞 Soporte Técnico

Para información técnica sobre cómo funciona el sistema internamente, consulta:
- `text_manager.py` - Lógica principal
- `../controller/` - Cómo se integra con los controladores
- `../my_ludwig/` - Sistema de AutoML y validaciones

## 📌 Notas Importantes

1. **Siempre mantén la estructura HTML** al modificar
2. **No cambies las keys** (ej: "primary_variable") - solo el contenido
3. **Prueba los cambios** ejecutando la aplicación después de modificar
4. **Los cambios son inmediatos** - no requieren recompilar

## 🎯 Próximas Mejoras

Áreas donde podrías añadir nuevos textos explicativos:
- Explicación de métricas de regresión vs clasificación
- Detalles sobre la estrategia de split (estratificado vs aleatorio)
- Información sobre el proceso de cancelación de entrenamiento
- Explicación de las validaciones automáticas


<!-- List -->
<ul>
    <li style="margin-top:6px;">
        <span style="font-weight:600;">Element:</span> Description
    </li>
</ul>

<!-- Italic -->
<span style="font-style:italic;">Italic note</span>
```

## 🔄 Workflow

1. **Modify text** → Edit corresponding `.py` file
2. **Validate** → `python text_utils.py validate`
3. **Test** → Restart application and verify changes
4. **Repeat** → Make more changes if needed

## ✨ System Advantages

- ✅ **Code-free**: You only edit content, not logic
- ✅ **Centralized**: All texts in one place
- ✅ **Versioned**: Changes are recorded in Git
- ✅ **Easy**: You don't need to know PySide6 or Qt
- ✅ **Validation**: Script verifies HTML is correct

## 🚨 Important Points

1. **Restart application**: Changes require restarting HAMELIN
2. **Keep format**: Respect basic HTML structure
3. **Use triple quotes**: For multiline content use `"""`
4. **Always validate**: Use `text_utils.py validate` before testing

## 📞 Questions?

The system is designed to be intuitive. If you have any questions:

1. Use `text_utils.py` to explore existing texts
2. Copy the structure of texts that already work
3. Always validate before testing in the application

Now you can modify all HAMELIN texts easily and safely! 🎉