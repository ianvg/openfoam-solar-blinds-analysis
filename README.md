# OpenFOAM Solar Blinds Analysis
The OpenFOAM version used here is based on OpenFOAM v13, available from the OpenFOAM Foundation; please note that the website is the .org version. Please note that a separately maintained branch of OpenFOAM is made available by OpenCFD LTD; please note that their website is the .com version. The OpenFOAM The download for OpenFOAM v13 can be found [here](https://cfd.direct/openfoam/download/). The guide for running OpenFOAM v13 can be found [here](https://doc.cfd.direct/openfoam/user-guide-v13/). To run OpenFOAM v13 on Windows requires the installation of WSL. Note that while OpenFOAM will work with multiple versions of Linux operating systems, OpenFOAM [specifically recommends](https://openfoam.org/download/windows/) that the Ubuntu 22.04 LTS to be used with OpenFOAM v13. 

This project assumes contributors use **SSH** for GitHub authentification.

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
## GitHub authentification: SSH only
This repository should be used with SSH authentification only for Git operations.

Do not use use HTTPS clone URLs for this project.
1. Check whether an SSH key already exists:
```
ls -al ~/.ssh
```
Look for files such as:
```
id_ed25519
id_ed25519.pub
```
If they do not exist, create a new SSH key.

2. Generate a new SSH key:
```
ssh-keygen -t ed25519 -C "your_email@example.com"
```
Press "Enter" to accept the default file location.

3. Start the SSH agent:
```
eval "$(ssh-agent -s)"
```
4. Add the SSH key to the agent:
```
ssh-add ~/.ssh/id_ed25519
```
5. Display your public key:
```
cat ~/.ssh/id_ed25519.pub
```
Copy the full output and add it to your GitHub account:
- GitHub
- Settings
- SSH and GPG keys
- New SSH key
6. Test GitHub SSH access:
```
ssh -T git@github.com
```
If successful, GitHub should confirm that authentification worked.
When working inside WSL, create and use your SSH key inside Ubuntu so Git commands run from the Linux terminal authenticate correctly.


## Cloning this repository
First you must choose or create a working directory (folder), then clone the project into that directory.
For example:
```
# This creates a folder if it does not already exists in the ~/OpenFOAM/projects location.
mkdir -p ~/OpenFOAM/projects
# This navigates to the directory that was just created.
cd ~/OpenFOAM/projects
```
Clone the repository using its SSH URL:
```
# This code clones (copies) over the contents of the respository to the folder that you are currently in. Replace **USERNAME/REPOSITORY.git** with actual repository path.
git clone git@github.com:USERNAME/REPOSITORY.git
# This navigates to the folder you are in.
cd REPOSITORY
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
## Verify the Git Remote uses SSH
After cloning, verify the remote within the project directory:
```
git remote -v
```
The output should look like this:
```
origin  git@github.com:USERNAME/REPOSITORY.git (fetch)
origin  git@github.com:USERNAME/REPOSITORY.git (push)
```
If the remote is incorrectly set to HTTPS, change it to SSH:
```
git remote set-url origin git@github.com:USERNAME/REPOSITORY.git
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
1. Move into the repository:
```
cd ~/OpenFOAM/projects/REPOSITORY
```
2. Before making changes, update your local copy:
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
3. Staging changes:
   
    1. Stage all your changes with ".":
    ```
    git add .
    ```
  
    2. Stage specific files:
    ```
    git add README.md
    ```

4. Commit them with a clear message:
```
git commit -m "Add installation and Git contribution instructions"
```
5. Push the branch:
    1. If you are pushing for the first time to the branch then use:
    ```
    git push -u origin descriptive-branch-name
    ```
    2. After the first push, future pushes on that branch can be done with:
    ```
    git push
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
