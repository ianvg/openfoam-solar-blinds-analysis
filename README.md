# OpenFOAM Solar Blinds Analysis

## 📖 Overview
This project uses OpenFOAM to analyze airflow and thermal behavior around window systems with solar blinds. The goal is to study how shading devices affect:

- Airflow patterns
- Heat transfer
- Ventilation performance
- Potential cooling load reduction

---

## Project Structure

.
├── baseCase/ # Base OpenFOAM case
├── meshStudy/ # Mesh refinement studies
│ ├── coarse/
│ ├── medium/
│ └── fine/
├── velocityStudy/ # Inlet velocity variations
├── system/ # Simulation control files
├── constant/ # Physical properties
├── 0/ # Initial conditions

---

## ⚙️ Requirements

- OpenFOAM (v13 recommended)
- Linux / WSL2 (Ubuntu 22.04 preferred)
- ParaView (for visualization)

---

## 🚀 Running a Case

Example:

```bash
cd baseCase
blockMesh
simpleFoam


---

## 💾 Step 3: Commit and push

```bash
git add .
git commit -m "Commit description"
git push
