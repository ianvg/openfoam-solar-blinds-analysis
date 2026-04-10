# OpenFOAM Solar Blinds Analysis
The OpenFOAM version used here is based on OpenFOAM v13, available from the OpenFOAM Foundation; please note that the website is the .org version. Please note that a separately maintained branch of OpenFOAM is made available by OpenCFD LTD; please note that their website is the .com version. The OpenFOAM The download for OpenFOAM v13 can be found [here](https://cfd.direct/openfoam/download/). The guide for running OpenFOAM v13 can be found [here](https://doc.cfd.direct/openfoam/user-guide-v13/). To run OpenFOAM v13 on Windows requires the installation of WSL. Note that while OpenFOAM will work with multiple versions of Linux operating systems, OpenFOAM [specifically recommends](https://openfoam.org/download/windows/) that the Ubuntu 22.04 LTS to be used with OpenFOAM v13. 

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

# Test edit
