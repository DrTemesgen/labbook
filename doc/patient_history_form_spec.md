# Patient History Form Specification (form_patient_hist_LANG.toml)

version 1 : 19/11/2025

This document describes how to define and configure **patient history forms** in LabBook using TOML files.

History forms allow the user to enter, edit and list historical patient information grouped by blocks.

All files must be UTF‑8 encoded.

---

## 1. File Location and Naming

History forms are stored in:

```
storage/resource/form/patient/
```

Naming convention:

```
form_patient_hist_LANG.toml
```

*LANG* must match a LabBook language code (fr, uk, us, es, ar, km, lo, mg, pt).

Examples:
- `form_patient_hist_fr.toml`
- `form_patient_hist_en.toml`

You may upload any test file through the administrator interface as long as it starts with `form_patient_hist_` and ends with `.toml`.

---

## 2. Required Sections

A history form TOML file must contain at least the following three top-level sections:

```
[description]
[history]
[layout]
```

No other top-level sections are allowed.

---

## 3. Section: description

This section contains the set of all fields that may appear in one or more history blocks.

Each field is declared with:

```
[[description.form_element]]
```

Two categories exist:

### 3.1. Custom fields (most common)

Mandatory keys:

- **id** — unique element identifier  
- **label** — label displayed to the user  
- **input_type** — type of widget

Possible `input_type` values:

```
text
textarea
number
select
radio
date
datetime-local
```

For `radio` and `select`, you **must** define:

```
options = [
    { value = "X", label = "Displayed text" },
    ...
]
```

Optional attributes:

```
attr_required = true  # field is mandatory, "*" is added after the label
attr_value    = "default content"

# for textarea
attr_rows     = "4"
attr_cols     = "50"

# for number
attr_min      = "0"
attr_max      = "10"
attr_step     = "1"
```

### 3.2. Display‑only elements

```
[[description.form_element]]
id   = "my_title"
label = "My Title"
type  = "h3"
```

Allowed `type`: `h1`, `h2`, `h3`, `h4`, `h5`, `h6`, `span`.

---

## 4. Section: history

This section defines:

- how the form’s history is grouped into blocks
- which fields appear as table columns

Example:

```
[history]
    [[history.block]]
    id = "clin"
    label = "Clinical signs"
    columns = ["clin_signs", "clin_datetime"]
```

Rules:

- **id** = prefix for all fields belonging to this block  
  Example: block `clin` → fields start with `clin_`

- **columns** lists the subset of fields visible in the table.  
  Other fields still exist and are editable, but not shown in the table.

You may define multiple blocks:

```
[history]

[[history.block]]
id      = "clin"
columns = ["clin_signs", "clin_datetime"]

[[history.block]]
id      = "treat"
columns = ["treat_drug", "treat_comment"]
```

---

## 5. Naming Rule: Block Fields

Every field belonging to a block must begin with:

```
block_id + "_"
```

Example:

```
[[description.form_element]]
id         = "clin_signs"
label      = "Clinical signs"
input_type = "text"

[[description.form_element]]
id         = "clin_datetime"
label      = "Date and time"
input_type = "datetime-local"
```

Block id: `clin`  
Field name: `clin_signs`, `clin_datetime`

---

## 6. Minimal working example: patient history form

```toml
# ======================================================================
# Minimal patient history form
# File example: form_patient_hist_fr.toml
# ======================================================================

[description]

# Block "med": a very simple medical history block

# Title (cosmetic only)
[[description.form_element]]
id    = "label_med"
label = "Medical history"
type  = "h3"

# Date and time of the event
[[description.form_element]]
id         = "med_datetime"
label      = "Date and time"
input_type = "datetime-local"

# Comment
[[description.form_element]]
id         = "med_comment"
label      = "Comment"
input_type = "textarea"
attr_rows  = "3"
attr_cols  = "40"

# ======================================================================
# LAYOUT SECTION (mandatory)
# ======================================================================

[layout]

# Block title
[[layout.rows]]
class    = "panel-heading row"
elements = [
    { element = "label_med", class = "panel-title" }
]

# Form fields + history table
[[layout.rows]]
class    = "row mt-2"
elements = [
    # Form on the left
    { class = "col-md-6", elements = [
        { element = "med_datetime", class = "flex-md-row" },
        { element = "med_comment",  class = "flex-md-row" }
    ] },
    # History table on the right (generated automatically for block "med")
    { element = "med", class = "col-md-6" }
]

# ======================================================================
# HISTORY SECTION (mandatory for history forms)
# ======================================================================

[history]

[[history.block]]
id      = "med"
columns = [
    "med_datetime",
    "med_comment"
]
```

---

## 7. Behaviour in LabBook

- Each block displays a dedicated history table.
- Clicking on a row fills the form with all field values for editing.
- Clicking **Save** stores a new record (previous values remain visible as history).
- The delete menu is only visible if user permission RECORD_25 is granted.
- The form auto‑detects unchanged values and prevents useless saves.

---

## End of Document
