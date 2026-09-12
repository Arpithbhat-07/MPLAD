# MPLADS AI Monitoring Platform

## Team Git Workflow

This guide explains exactly how to upload work safely during the hackathon.

**Repository URL:** `https://github.com/Arpithbhat-07/MPLAD.git`

---

## Branches and Ownership

| Branch     | What goes here                                                 |
| ---------- | -------------------------------------------------------------- |
| `main`     | Final stable, demo-ready project                               |
| `develop`  | Combined and tested work                                       |
| `frontend` | Dashboard, UI, charts, maps, styling                           |
| `backend`  | APIs, database, authentication, integrations                   |
| `ai`       | Risk scoring, anomaly detection, duplicate detection, datasets |
| `docs`     | README, screenshots, architecture, pitch content               |

## Non Negotiable Rules

1. **Never push directly to `main`.**
2. Pull the latest changes before starting work each day.
3. Make small commits with clear messages.
4. Do not use `git push --force`.
5. When a feature works, open a Pull Request to `develop`.
6. Only merge code that has been tested locally.

---

## One Time Setup for Every Team Member

### 1. Install Git

Check whether Git is installed:

```powershell
git --version
```

If this command does not work, install Git from [git-scm.com](https://git-scm.com/downloads), then reopen PowerShell.

### 2. Configure your Git identity

Run once on your laptop:

```powershell
git config --global user.name "Your Full Name"
git config --global user.email "your-github-email@example.com"
```

### 3. Clone the repository

```powershell
git clone https://github.com/Arpithbhat-07/MPLAD.git
cd MPLAD
```

### 4. See all available branches

```powershell
git branch -a
```

---

## Daily Workflow

Use these commands every time you begin, save, and upload work.

### Before starting work

Switch to your branch, then download the latest version of that branch.

#### Frontend team

```powershell
git checkout frontend
git pull origin frontend
```

#### Backend team

```powershell
git checkout backend
git pull origin backend
```

#### AI and data team

```powershell
git checkout ai
git pull origin ai
```

#### Documentation and pitch team

```powershell
git checkout docs
git pull origin docs
```

### Check what you changed

```powershell
git status
```

### Save your progress locally

Add all changed files:

```powershell
git add .
```

Create a clear commit:

```powershell
git commit -m "Add risk score dashboard cards"
```

### Upload your progress to GitHub

Push to **your own assigned branch**.

#### Frontend team

```powershell
git push origin frontend
```

#### Backend team

```powershell
git push origin backend
```

#### AI and data team

```powershell
git push origin ai
```

#### Documentation and pitch team

```powershell
git push origin docs
```

---

## If You Need a New Small Feature Branch

Use a feature branch only when your team branch has more than one person working at the same time.

Example: a frontend member building the map view.

```powershell
git checkout frontend
git pull origin frontend
git checkout -b frontend/map-view
```

After work is complete:

```powershell
git add .
git commit -m "Add map view for flagged works"
git push -u origin frontend/map-view
```

Then open a Pull Request on GitHub:

```text
frontend/map-view  ->  frontend
```

After review, merge it into `frontend`.

---

## How to Send Finished Work for Integration

When your branch is stable:

1. Push it using the commands above.
2. Open the repository on GitHub.
3. Click **Pull requests**.
4. Click **New pull request**.
5. Set the destination branch to `develop`.
6. Set your branch as the source branch.
7. Add a title such as `Frontend dashboard ready for integration`.
8. Briefly describe what works and what still needs testing.
9. Click **Create pull request**.
10. Tell the team lead to review and merge it.

Use this Pull Request description:

```text
What changed:
-
-

How to test:
-

Known issues:
- None / describe issue here
```

---

## Team Lead Commands

### Create branches after pushing the initial project

```powershell
git checkout -b develop
git push -u origin develop

git checkout -b frontend
git push -u origin frontend

git checkout develop
git checkout -b backend
git push -u origin backend

git checkout develop
git checkout -b ai-engine
git push -u origin ai-engine

git checkout develop
git checkout -b docs-pitch
git push -u origin docs-pitch
```

### Bring frontend work into the integration branch

Prefer a Pull Request on GitHub. If you need to do it locally:

```powershell
git checkout develop
git pull origin develop
git merge frontend
git push origin develop
```

### Bring backend work into the integration branch

```powershell
git checkout develop
git pull origin develop
git merge backend
git push origin develop
```

### Bring AI work into the integration branch

```powershell
git checkout develop
git pull origin develop
git merge ai
git push origin develop
```

### Final release before submission

Only after testing the complete project:

```powershell
git checkout main
git pull origin main
git merge develop
git push origin main
```

---

## If Git Says Your Branch Is Behind

Someone else pushed changes before you. First save your unfinished changes, then pull:

```powershell
git add .
git commit -m "Save work before syncing"
git pull origin YOUR-BRANCH-NAME
```

---

## Quick Emergency Commands

See changed files:

```powershell
git status
```

See recent commits:

```powershell
git log --oneline -5
```

Discard only changes you have definitely decided not to keep:

```powershell
git restore FILE-NAME
```

Check your current branch:

```powershell
git branch --show-current
```

---
