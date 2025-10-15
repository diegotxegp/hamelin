# Centralized Text System - HAMELIN

## 📋 Description

This system allows managing all explanatory texts of the HAMELIN application in a centralized way, facilitating modification and maintenance without needing to touch the controller code.

## 📁 File Structure

```
src/texts/
├── __init__.py                     # Exports the text manager
├── text_manager.py                 # Main text manager
├── clinical_trial_texts.py         # Texts for Clinical Trial
├── patient_registry_texts.py       # Texts for Patient Registry
└── observational_study_texts.py    # Texts for Observational Study
```

## 🔧 How to Modify Texts

### 1. Modify Existing Texts

To change the text of a specific tab, edit the corresponding file:

**Clinical Trial** → `clinical_trial_texts.py`
**Patient Registry** → `patient_registry_texts.py`
**Observational Study** → `observational_study_texts.py`

### 2. Modification Example

```python
# In clinical_trial_texts.py
CLINICAL_TRIAL_TEXTS = {
    "primary_variable": {
        "title": "Your New Title",
        "content": """
        <p style="margin-top:0px; margin-bottom:0px;">
            <span style="font-size:16pt; font-weight:600;">New Title</span>
        </p>
        <p style="margin-top:12px;">
            Your new explanatory content here...
        </p>
        """
    }
}
```

### 3. HTML Structure

Texts use basic HTML with inline styles. Common elements:

```html
<!-- Main title -->
<span style="font-size:16pt; font-weight:600;">Title</span>

<!-- Normal paragraph -->
<p style="margin-top:12px;">Normal text</p>

<!-- Bold text -->
<span style="font-weight:600;">Highlighted text</span>

<!-- List -->
<ul>
    <li style="margin-top:6px;">
        <span style="font-weight:600;">Element:</span> Description
    </li>
</ul>

<!-- Italic text -->
<span style="font-style:italic;">Important note</span>
```

## 🎯 Available Tabs

### Clinical Trial
- `primary_variable` - "Primary variable" tab
- `criteria` - "Criteria" tab
- `investigational_drug` - "Investigational drug" tab
- `control_drug` - "Control drug" tab
- `disease` - "Disease/Disorder" tab

### Patient Registry
- `primary_variable` - "Primary variable" tab

### Observational Study
- `primary_variable` - "Primary variable" tab

## 🔄 Adding New Texts

### 1. Add new tab to existing study

```python
# In corresponding file (e.g.: clinical_trial_texts.py)
CLINICAL_TRIAL_TEXTS = {
    # ... existing texts ...
    
    "new_tab": {
        "title": "New Title",
        "content": """
        <p>New tab content...</p>
        """
    }
}
```

### 2. Add new study type

1. Create file `new_study_texts.py`
2. Import it in `text_manager.py`
3. Add it to the `self.texts` dictionary

## 🛠️ Usage in Code

Controllers automatically load texts using:

```python
from texts import text_manager

# Load complete HTML text
textEdit.setHtml(text_manager.get_html_content('clinical_trial', 'primary_variable'))

# Get only content
content = text_manager.get_text('clinical_trial', 'primary_variable', 'content')

# Get only title
title = text_manager.get_text('clinical_trial', 'primary_variable', 'title')
```

## ✅ System Advantages

- **Centralized**: All texts in one place
- **Code-free**: Modify texts without touching controllers
- **Reusable**: Extensible system for new tabs
- **Versionable**: Texts are in version control
- **Maintainable**: Easy localization and updates

## 🚀 Next Steps

1. **Add more texts**: Expand to cover all tabs
2. **Internationalization**: Support for multiple languages
3. **Validation**: Verify HTML texts are valid
4. **Visual editor**: Graphical interface for editing texts

## 📝 Important Notes

- Changes in text files require restarting the application
- Keep valid HTML format to avoid rendering errors
- Inline styles are necessary for Qt
- Use triple quotes `"""` for multiline HTML content