# 📝 Text Modification Guide - HAMELIN

## 🎯 What have I implemented?

I have created a **centralized text system** that allows you to modify all explanatory texts of the HAMELIN application without needing to touch Python code.

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

## 🛠️ Utility Tools

I created a script to help you: `text_utils.py`

### Useful commands:

```bash
# Activate environment and go to texts folder
cd /home/diegotxe/Visual-Studio/HAMELIN && source .venv/bin/activate && cd Hamelin/src/texts

# View all available sections
python text_utils.py list

# View Clinical Trial subsections
python text_utils.py show clinical_trial

# View current Primary Variable text
python text_utils.py show clinical_trial primary_variable

# Validate that all texts are well formatted
python text_utils.py validate
```

## 📋 Currently Available Texts

### Clinical Trial (`clinical_trial_texts.py`):
- `primary_variable` - ✅ **Already fixed** (the one you mentioned)
- `criteria` - Inclusion/exclusion criteria
- `investigational_drug` - Experimental group
- `control_drug` - Control group
- `disease` - Medical condition

### Patient Registry (`patient_registry_texts.py`):
- `primary_variable` - Primary variable for registries

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