# 📘 VASP Optical Properties – Workflow (Step-by-Step)

This project shows how to compute optical properties using VASP and visualize them using Python.

---

# ⚙️ Step 1: Run VASP Calculation

Run optical property calculations using VASP.

After completion, VASP will generate output files automatically.

---

# 📂 Step 2: Collect Output Files

After the calculation is finished, you will get the required XML output files:

```id="q3m7sk"
vasprun.DIAG.xml
vasprun.NONE.xml
vasprun.BSE.xml
```

Keep all files in one folder.

---

# 🐍 Step 3: Install Python Packages

Install required libraries:

```bash id="h8xq21"
pip install numpy matplotlib scipy
```

---

# 📄 Step 4: Run Python Script

Place the Python script in the same directory as the VASP output files.

Then run:

```bash id="p9k2nd"
python optical_pipeline.py
```

---

# 📊 Step 5: Data Processing

The script will automatically:

* Read optical data from VASP output files
* Extract dielectric function ε₁(ω), ε₂(ω)
* Compute optical properties:

  * Refractive index (n)
  * Extinction coefficient (k)
  * Absorption coefficient (α)
  * Reflectivity (R)
  * Transmittance (T)
  * Optical conductivity (σ₁, σ₂)
  * Energy loss function (ELF)
* Read excitonic transitions (BSE data)

---

# 📈 Step 6: Plotting

Python will generate all plots automatically and combine them into a single figure.

---

# 📁 Step 7: Output File

Final output:

```id="w6t9pa"
optical_full_pipeline_ALL_properties_FINAL.pdf
```

This file contains all optical property plots in publication quality.

---

# 🎯 Final Workflow Summary

```id="r1v0ms"
VASP run → Output files generated → Python analysis → Publication-quality plots
```


