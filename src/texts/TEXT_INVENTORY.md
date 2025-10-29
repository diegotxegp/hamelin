# 📋 HAMELIN Text Inventory

## Overview
This document lists all the customizable texts in HAMELIN organized by module. All texts are centralized in the `texts/` folder for easy modification.

---

## 🏥 Clinical Trial Texts
**File:** `clinical_trial_texts.py`

### Available Text Keys:

#### 1. `primary_variable`
- **Location:** Clinical Trial tab → Primary Variable selection
- **Content:** Explains primary outcome variable selection with examples for both classification and regression
- **Topics covered:**
  - Binary outcomes (Classification)
  - Categorical outcomes (Classification)
  - Continuous numerical outcomes (Regression)
  - Time-related outcomes (Regression)
  - Intelligent variable detection system
  - Sample requirements for different variable types

#### 2. `criteria`
- **Location:** Clinical Trial tab → Criteria section
- **Content:** Patient Selection Criteria (inclusion/exclusion)
- **Topics covered:**
  - Demographic criteria
  - Clinical criteria
  - Laboratory criteria
  - Exclusion criteria

#### 3. `investigational_drug`
- **Location:** Clinical Trial tab → Experimental Treatment section
- **Content:** Experimental Treatment Group identification
- **Topics covered:**
  - Treatment group identifier
  - Drug name/code
  - Dosage information

#### 4. `control_drug`
- **Location:** Clinical Trial tab → Control section
- **Content:** Control/Comparison Group identification
- **Topics covered:**
  - Control group types (placebo, standard care, active comparator)
  - Comparison requirements

#### 5. `disease`
- **Location:** Clinical Trial tab → Disease section
- **Content:** Medical condition being studied
- **Topics covered:**
  - Disease/condition name
  - ICD codes
  - Disease classification
  - Severity levels

---

## 📊 Patient Registry Texts
**File:** `patient_registry_texts.py`

### Available Text Keys:

#### 1. `primary_variable`
- **Location:** Patient Registry tab → Primary Variable selection
- **Content:** Primary variable selection for registry studies with classification and regression support
- **Topics covered:**
  - What is a Patient Registry
  - Categorical outcomes (Classification)
  - Binary outcomes (Classification)
  - Continuous numerical outcomes (Regression)
  - Discrete numerical outcomes
  - Intelligent variable detection
  - Selection requirements by variable type

#### 2. `criteria`
- **Location:** Patient Registry tab → Variable Configuration section
- **Content:** Variable selection and configuration instructions
- **Topics covered:**
  - Role in analysis (input/output)
  - Data types (binary/category/number/text)
  - Configuration best practices
  - Examples for each type

#### 3. `disease`
- **Location:** Patient Registry tab → Disease/Condition section
- **Content:** Medical condition or focus of the registry
- **Topics covered:**
  - Registry focus (disease, condition, population)
  - ICD codes
  - Target population

#### 4. `population`
- **Location:** Patient Registry tab → Population section
- **Content:** Target population definition
- **Topics covered:**
  - Population characteristics
  - Geographic scope
  - Demographic criteria

---

## 🔬 Observational Study Texts
**File:** `observational_study_texts.py`

### Available Text Keys:

#### 1. `primary_variable`
- **Location:** Observational Study tab → Primary Variable selection
- **Content:** Primary outcome of interest for observational studies with dual task support
- **Topics covered:**
  - Categorical outcomes (Classification)
  - Binary outcomes (Classification)
  - Continuous outcomes (Regression)
  - Time-related outcomes (Regression)
  - Intelligent detection system
  - Association vs causation note

#### 2. `criteria`
- **Location:** Observational Study tab → Variable Configuration section
- **Content:** Variable selection for observational analysis
- **Topics covered:**
  - Role in analysis (input/output)
  - Data types (binary/category/number/text)
  - Exposure variables
  - Outcome variables

#### 3. `exposure`
- **Location:** Observational Study tab → Exposure section
- **Content:** Exposure or risk factor identification
- **Topics covered:**
  - Types of exposures (environmental, behavioral, clinical)
  - Measurement of exposure
  - Temporal relationship

#### 4. `outcome`
- **Location:** Observational Study tab → Outcome section
- **Content:** Health outcome or event definition
- **Topics covered:**
  - Outcome types
  - Measurement methods
  - Time to event

---

## 🎨 How to Modify Texts

### Step-by-Step Guide:

1. **Locate the text file** for your study type:
   - Clinical Trial → `clinical_trial_texts.py`
   - Patient Registry → `patient_registry_texts.py`
   - Observational Study → `observational_study_texts.py`

2. **Find the text key** you want to modify (e.g., `"primary_variable"`)

3. **Edit the content** within the triple quotes:
   ```python
   "primary_variable": {
       "title": "Your New Title",
       "content": """
       <p>Your new HTML content here...</p>
       """
   }
   ```

4. **Save the file** - changes are immediate, no compilation needed!

---

## 🎨 HTML Formatting Reference

### Common Elements Used:

```html
<!-- Main Title -->
<p style="font-size: 14pt; font-weight: bold; margin-bottom: 15px; text-align: center;">
    Title Text
</p>

<!-- Regular Paragraph -->
<p style="margin-bottom: 15px; text-align: justify;">
    Regular text content
</p>

<!-- Bold Inline Text -->
<strong>Important text</strong>

<!-- Section with Left Margin -->
<p style="margin-left: 20px; margin-bottom: 8px;">
    Indented content
</p>

<!-- Highlighted Note Box -->
<p style="font-style: italic; background-color: #f0f8ff; padding: 10px; border-left: 4px solid #4a90e2;">
    <strong>Note:</strong> Important information
</p>

<!-- Warning Box -->
<p style="font-style: italic; background-color: #fff3cd; padding: 10px; border-left: 4px solid #ffc107;">
    <strong>Warning:</strong> Warning text
</p>

<!-- Info Box -->
<p style="background-color: #e8f4f8; padding: 10px;">
    ✓ Information with checkmark
</p>
```

---

## ⚙️ System Integration

### Text Manager (`text_manager.py`)
- Central class that loads all texts
- Provides `get_text(study_type, text_key)` method
- Used by all controllers

### Text Utils (`text_utils.py`)
- Utility functions for text processing
- HTML formatting helpers

---

## 🚀 Recent Updates

All primary variable texts have been updated to include:
- ✅ Support for both Classification and Regression
- ✅ Explanation of continuous vs discrete variables
- ✅ Intelligent variable detection system
- ✅ Sample requirements for different variable types
- ✅ Auto-filtering of inappropriate variables

---

## 📝 Best Practices

1. **Maintain HTML structure** when editing
2. **Don't change text keys** (e.g., "primary_variable")
3. **Test changes** by running the application
4. **Keep medical terminology accurate**
5. **Provide clear examples** for users
6. **Update all study types consistently** when making conceptual changes

---

## 🔧 Technical Notes

- All texts are stored as Python dictionaries
- HTML content is embedded as multi-line strings
- Qt's Rich Text format is used for rendering
- Changes take effect immediately (no restart needed)

---

## 📞 Need Help?

- See `GUIA_MODIFICACION.md` for detailed modification guide
- See `README.md` for technical architecture
- Check `text_manager.py` for implementation details

---

Last Updated: October 2025
Version: 2.0 (with Regression Support)
