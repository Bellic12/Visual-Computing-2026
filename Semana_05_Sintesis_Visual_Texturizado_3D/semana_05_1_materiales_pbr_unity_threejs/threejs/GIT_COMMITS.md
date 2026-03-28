# Git Commit Guide

## Understanding Commits

Each commit should represent a logical unit of work with a clear, descriptive message in English.

---

## Commit Messages Format

### Basic Format
```
<type>: <subject>

<body (optional)>

<footer (optional)>
```

### Types of Commits

| Type | Description | Example |
|------|-------------|---------|
| `feat` | New feature | `feat: add orbit controls` |
| `fix` | Bug fix | `fix: material not updating` |
| `docs` | Documentation | `docs: update readme` |
| `style` | Code style (formatting) | `style: format code with prettier` |
| `refactor` | Code refactoring | `refactor: extract texture generation` |
| `test` | Add tests | `test: add material tests` |
| `chore` | Maintenance tasks | `chore: update dependencies` |
| `perf` | Performance improvements | `perf: optimize shadow maps` |

---

## Example Commits

### Initialization
```bash
git add .
git commit -m "chore: initialize react three fiber project"
```

### Main Features
```bash
git commit -m "feat: implement pbr material scene"
git commit -m "feat: add lil-gui controls panel"
git commit -m "feat: generate procedural textures"
```

### Fixes and Refinements
```bash
git commit -m "fix: material not updating on slider change"
git commit -m "fix: shadow casting not working"
```

### Documentation
```bash
git commit -m "docs: add technical documentation"
git commit -m "docs: update installation guide"
```

### Performance
```bash
git commit -m "perf: reduce sphere segments for better performance"
git commit -m "perf: optimize texture resolution"
```

---

## Workflow Steps

### 1. Check Status
```bash
git status
```

Shows what files have changed.

### 2. Add Files to Staging

Add specific files:
```bash
git add src/components/PBRMaterialScene.jsx
git add src/App.jsx
```

Or add all changes:
```bash
git add .
```

### 3. Create Commit

```bash
git commit -m "feat: implement pbr material system"
```

### 4. View Commit History
```bash
git log --oneline
```

Output example:
```
a1b2c3d feat: add pbr material comparison
d4e5f6g feat: implement gui controls
h7i8j9k docs: update readme
```

---

## Best Practices

### ✅ Do
- ✅ Write concise, descriptive subjects (50 chars max)
- ✅ Use imperative mood ("add" not "added")
- ✅ Reference issues if applicable: `fix: update GUI #123`
- ✅ Keep commits small and focused
- ✅ Write meaningful commit messages

### ❌ Don't
- ❌ Use vague messages like "fix stuff" or "updates"
- ❌ Mix multiple features in one commit
- ❌ Commit with misleading messages
- ❌ Use ALL CAPS for entire message
- ❌ Include uncommitted changes

---

## Complete Commit Examples

### With Body (Detailed)
```
feat: add dynamic material property adjustment

Implement real-time controls for roughness, metalness,
and light intensity. Materials update instantly when
sliders are moved through lil-gui interface.

- Add useState hook for material properties
- Implement onChange callbacks for sliders
- Update materials on every property change
- Tested on Chrome, Firefox, Safari
```

### Simple Feature
```
feat: add background grid visualization
```

### Bug Fix with Context
```
fix: resolve memory leak in gui panel

GUI panels were accumulating in memory on each re-render.
Added proper cleanup in useEffect return statement to
destroy GUI instances when component unmounts.

Fixes #42
```

---

## Typical Workshop Commits Sequence

```
1. git commit -m "chore: initialize project structure"
2. git commit -m "feat: setup vite and react three fiber"
3. git commit -m "feat: add perspective camera and orbit controls"
4. git commit -m "feat: implement lighting system"
5. git commit -m "feat: create procedural texture generation"
6. git commit -m "feat: add pbr material with texture maps"
7. git commit -m "feat: implement lil-gui control panel"
8. git commit -m "feat: add comparison scene with basic material"
9. git commit -m "style: add css styling and responsive design"
10. git commit -m "docs: write complete readme documentation"
11. git commit -m "docs: add technical documentation"
12. git commit -m "docs: add installation guide"
```

---

## Quick Reference Commands

```bash
# See what changed
git status
git diff

# Stage files
git add <file>
git add .
git add *.jsx          # All JSX files

# Commit
git commit -m "type: message"
git commit -am "type: message"    # Stage and commit

# Undo (before push)
git reset HEAD~1       # Undo last commit (keep changes)
git reset --hard HEAD~1    # Undo last commit (discard)

# View history
git log
git log --oneline
git log --oneline -10  # Last 10 commits

# View specific commit
git show a1b2c3d

# Amend last commit
git add <file>
git commit --amend    # Modify last commit

# Push to remote
git push origin main
```

---

## Common Scenarios

### Scenario 1: Forgot to Add a File
```bash
# Add the file
git add forgotten_file.js

# Amend previous commit
git commit --amend

# No commit message option: use previous message
```

### Scenario 2: Committed to Wrong Branch
```bash
# Undo commit (keep changes)
git reset HEAD~1

# Switch to correct branch
git checkout correct-branch

# Commit there
git commit -m "correct-message"
```

### Scenario 3: Need to Combine Multiple Commits
```bash
# Interactive rebase of last 3 commits
git rebase -i HEAD~3

# Follow prompts to squash commits
```

### Scenario 4: Accidentally Committed Sensitive Info
```bash
# Remove file from history
git rm --cached sensitive_file.env

# Commit removal
git commit -m "chore: remove sensitive files"
```

---

## Viewing Your Commits

### See Pretty Log
```bash
git log --graph --oneline --all --decorate
```

### See Changes in Specific Commit
```bash
git show a1b2c3d
```

### See Who Changed What
```bash
git blame src/App.jsx
```

---

## Collaboration Tips

### Before Starting Work
```bash
git pull origin main
```

### Share Your Work
```bash
git push origin main
```

### Rebase on Latest
```bash
git fetch origin
git rebase origin/main
```

---

## Commit Message Template (Optional)

Create `.gitmessage` file:
```
<type>: <subject> (imperative, not capitalized, max 50 chars)

<body (wrap to 72 chars, explain what and why not how)>

<footer (reference issues)>
```

Use it:
```bash
git config commit.template .gitmessage
```

---

## Final Checklist for Workshop

Before final submission:

- [ ] All code committed with descriptive messages
- [ ] Commits summarize the development journey
- [ ] 10-15 commits minimum for the workshop
- [ ] No "fix typo" or meaningless commits
- [ ] All features have corresponding commits
- [ ] Documentation commits are present
- [ ] English language used for all messages
- [ ] Push all commits to repository

---

## Push to Repository

```bash
# Verify commits are created
git log --oneline

# Push to remote (GitLab)
git push origin main

# Or if using different branch
git push origin feature-branch

# Force push (use carefully!)
git push origin main --force-with-lease
```

---

**Commit Guide Updated:** March 28, 2026  
**Version:** 1.0  
**Status:** Ready for Use ✅
