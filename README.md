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
- Linux / WSL2 (Ubuntu 22.04 LTS preferred)
- ParaView (for visualization)

---
# Installation and setup on Windows
1. On Windows, first install WSL. Ubuntu 22.04 LTS is the recommended Linux distrubtion for this project.
Powershell install command:
```
wsl --install -d Ubuntu-22.04
```
After installation, restart if prompted, then launch WSL and create your Linux username and password.
To confirm WSL is installed, and which version is installed, run the below commands:
```
wsl --status
wsl -l -v
```
2. Install OpenFOAM v13
Inside Ubuntu on WSL, follow the OpenFOAM Foundation installation instructions for v13.
After installation, open a new Ubuntu shell and verify OpenFOAM is available.
```
foamRun
```
You can also check your environment with:
```
foamInstallationTest
```
3. Install Git
Install Ubuntu:
```
sudo apt update
sudo apt install git -y
```
Check installation with:
```
git --version
```
4. Clone this repository
First you must choose or create a working directory (folder), then clone the project into that directory.
For example:
```
# This creates a folder if it does not already exists in the ~/OpenFOAM/projects location.
mkdir -p ~/OpenFOAM/projects
# This navigates to the directory that was just created.
cd ~/OpenFOAM/projects
# This code clones (copies) over the contents of the respository to the folder that you are currently in.
git clone <repositoryurl>
# This navigates to the folder you are in.
cd <repository-folder>
```
Example if you are using SSH:
```
git clone git@github.com/USERNAME/REPOSITORY.git
```
5. Configure Git identity
Set your name and email so your commits are attributed correctly.
```
git config --global user.name "Your name"
git config --global user.email "your_email@example.com"
```
Check that your Git identity is set correctly:
```
git config --global --list
```
6. Set up SSH authentification for GitHub
SSH is recommended HTTPS.
Generate new SSH key in Ubuntu:
```
ssh-keygen -t ed25519 -C "your_email@example.com"
```
Start the SSH agent and add the key:
```
eval "$(ssh-agent -s)"
ssh-add ~/.ssh/id_ed25519
```
Display the public key:
```
cat ~/.ssh/id_ed25519.pub
```
Copy that key and add it to your GitHub account under SSH and GPG keys.
Test the connection:
```
ssh -T git@github.com
```
## Running the project
1. Run the base case
```
cd baseCase
blockMesh
simpleFoam
```
Depending on the solver and case configuration, additional preprocessing or different solvers may be required.

## Viewing results
1. To inspect results in ParaView
```
paraFoam
```
## Contributing to the project
1. Before making changes, update your local copy:
```
git pull
```
Create a new branch for your work:
```
git checkout -b descriptive-branch-name
```
Examples:
```
git checkout -b add-readme-install-guide
git checkout -b update-mesh-study-case
git checkout -b fix-boundary-conditions
```
Make your edits, then review the changes:
```
git status
git diff
```
Stage your changes:
```
git add .
```
Commit them with a clear message:
```
git commit -m "Add installation and Git contribution instructions"
```
Push the branch:
```
git push -u origin descriptive-branch-name
```

## If you are working directly on your own fork
If you forked the project, your workflow may look like this:
```
git clone git@github.com:YOUR-USERNAME/REPOSITORY.git
cd REPOSITORY
git checkout -b my-change
git add .
git commit -m "Describe the change"
git push -u origin my-change
```
Then create a pull request form your fork to the main repository.

To keep your branch up to date, update from the main branch:
```
git checkout main
git pull
git checkout your-branch-name
git merge main
```
## Example Git contribution sequence:
```
cd ~/OpenFOAM/projects/openfoam-solar-blinds-analysis
git pull
git checkout -b add-installation-guide

# make edits to README.md

git status
git add README.md
git commit -m "Expand installation and Git setup instructions"
git push -u origin add-installation-guide
```

## Basic commit and push
```
git add .
git commit -m "Commit description"
git push
```


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
