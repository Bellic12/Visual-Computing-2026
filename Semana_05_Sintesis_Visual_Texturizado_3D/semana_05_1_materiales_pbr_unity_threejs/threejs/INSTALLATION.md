# Installation & Troubleshooting Guide

## ⚠️ Prerequisites Check

Before starting, ensure you have:

```bash
# Check Node.js version (should be 16+)
node --version

# Check npm version (should be 7+)
npm --version
```

If not installed, download from: https://nodejs.org/

---

## 🔧 Installation Steps

### Step 1: Navigate to Project Directory

```bash
# Navigate to threejs folder
cd threejs
```

### Step 2: Install Dependencies

```bash
# Using npm (recommended)
npm install

# Or using yarn
yarn install

# Or using pnpm
pnpm install
```

**Expected output:**
```
added XXX packages in XXs
```

### Step 3: Start Development Server

```bash
npm run dev
```

**Expected output:**
```
Local: http://localhost:3000
Press q to quit
```

Browser should open automatically. If not, manually navigate to: `http://localhost:3000`

---

## 🐛 Common Issues & Solutions

### Issue 1: Command Not Found (npm)

**Error:**
```
'npm' is not recognized as an internal or external command
```

**Solution:**
1. Install Node.js from https://nodejs.org/
2. Add Node.js to PATH:
   - Windows: Reinstall Node.js and select "Add to PATH"
   - Mac: Should be automatic
   - Linux: Use package manager

3. Restart terminal and retry

---

### Issue 2: Dependencies Installation Fails

**Error:**
```
npm ERR! code ERESOLVE
npm ERR! ERESOLVE unable to resolve dependency tree
```

**Solutions:**

**Option A (Recommended):**
```bash
npm install --legacy-peer-deps
```

**Option B: Clear Cache**
```bash
npm cache clean --force
rm -rf node_modules package-lock.json
npm install
```

**Option C: Use Exact Versions**
```bash
npm install --save --save-exact
```

---

### Issue 3: Port 3000 Already in Use

**Error:**
```
Error: listen EADDRINUSE: address already in use :::3000
```

**Solutions:**

**Option A: Use Different Port**
Edit `vite.config.js`:
```javascript
server: {
  port: 3001,  // Change to different port
  open: true,
}
```

**Option B: Kill Process Using Port**

Windows:
```bash
netstat -ano | findstr :3000
taskkill /PID <PID> /F
```

Mac/Linux:
```bash
lsof -ti:3000 | xargs kill -9
```

---

### Issue 4: Canvas Not Rendering

**Error:**
- Black screen
- No scene visible
- WebGL error in console

**Solutions:**

1. **Check browser compatibility:**
   - Open DevTools (F12)
   - Check if WebGL 2 is supported
   - Try a different browser (Chrome/Firefox)

2. **Verify Three.js is loaded:**
   ```javascript
   // In browser console:
   console.log(THREE);
   // Should show THREE object
   ```

3. **Check for shader errors:**
   ```javascript
   // In browser console:
   console.log(renderer.info);
   ```

4. **Rebuild project:**
   ```bash
   npm run build
   npm run preview
   ```

---

### Issue 5: GUI Not Appearing

**Error:**
- lil-gui panel not visible
- No control sliders

**Solutions:**

1. **Check lil-gui is installed:**
   ```bash
   npm list lil-gui
   ```

2. **Reinstall lil-gui:**
   ```bash
   npm uninstall lil-gui
   npm install lil-gui@0.19.1
   ```

3. **Check CSS is loaded:**
   - Open DevTools (F12)
   - Check Elements tab
   - Look for `lil-gui` CSS

---

### Issue 6: Hot Reload Not Working

**Error:**
- Changes to code don't reflect in browser
- Must refresh manually

**Solutions:**

1. **Check Vite configuration:**
   - vite.config.js should exist
   - Should have `plugins: [react()]`

2. **Restart dev server:**
   ```bash
   # Press Ctrl+C to stop
   npm run dev
   ```

3. **Check file paths:**
   - All imports use correct paths
   - No typos in filenames
   - Use relative paths: `./components/`

---

### Issue 7: Build Fails

**Error:**
```
vite v4.3.0 building for production...
error during build
```

**Solutions:**

1. **Check for build errors:**
   ```bash
   npm run build -- --debug
   ```

2. **Common causes:**
   - Missing semicolons (less common in JSX)
   - Undefined variables
   - Circular imports

3. **Fix and rebuild:**
   ```bash
   npm run build
   ```

---

### Issue 8: Memory Issues

**Error:**
- App crashes after a while
- Performance degrades over time
- Browser tab uses lots of RAM

**Solutions:**

1. **Reduce geometry complexity:**
   ```javascript
   // In PBRMaterialScene.jsx
   <sphereGeometry args={[1.5, 32, 32]} />  // From 64, 64
   ```

2. **Disable shadow maps:**
   ```javascript
   directionalLight.castShadow = false;
   ```

3. **Monitor performance:**
   - Open DevTools
   - Performance tab
   - Record and analyze

4. **Restart browser:**
   - Sometimes memory accumulates
   - Close and reopen browser

---

### Issue 9: Module Not Found

**Error:**
```
[ERR_MODULE_NOT_FOUND]: Cannot find module '@react-three/fiber'
```

**Solutions:**

1. **Install missing package:**
   ```bash
   npm install @react-three/fiber
   ```

2. **Install all missing packages:**
   ```bash
   npm install
   ```

3. **Check package.json:**
   - Verify dependency is listed
   - Check spelling

---

### Issue 10: React Version Conflict

**Error:**
```
React must be in scope when using JSX
```

**Solutions:**

1. **Add React import to top of JSX files:**
   ```javascript
   import React from 'react';
   ```

2. **Update React:**
   ```bash
   npm update react react-dom
   ```

---

## ✅ Verification Checklist

After installation, verify everything works:

- [ ] `npm install` completes without errors
- [ ] `npm run dev` starts without errors
- [ ] Browser opens to `http://localhost:3000`
- [ ] Canvas displays with purple grid
- [ ] Three objects visible (2 spheres, 1 cube)
- [ ] Shadows visible on ground
- [ ] lil-gui panel visible on right
- [ ] Sliders are interactive
- [ ] Orbit controls work (click+drag to rotate)
- [ ] No errors in browser console (F12)

---

## 🚀 First Run Checklist

```
1. Open terminal/command prompt
2. cd threejs
3. npm install
4. npm run dev
5. Browser opens to localhost:3000
6. Wait 5-10 seconds for scene to fully load
7. Try rotating with mouse (click+drag)
8. Try adjusting sliders in GUI panel
9. Open DevTools (F12) and check console
10. Everything working? ✅ Proceed with workshop!
```

---

## 📝 Environment Variables (Optional)

Create `.env.local` file if needed:

```
VITE_APP_TITLE=PBR Materials Workshop
VITE_DEBUG_MODE=false
```

Access in code:
```javascript
console.log(import.meta.env.VITE_APP_TITLE);
```

---

## 🔄 Updating Dependencies

Keep packages up to date (optional):

```bash
# Check for updates
npm outdated

# Update packages
npm update

# Update specific package
npm update three

# Update to latest (might break things)
npm install three@latest
```

---

## 🧹 Cleanup & Reset

If everything breaks, start fresh:

```bash
# Delete dependencies and lock file
rm -rf node_modules package-lock.json

# Reinstall fresh
npm install

# Clear npm cache (if needed)
npm cache clean --force

# Start dev server
npm run dev
```

---

## 📞 Getting Help

If you're still stuck:

1. **Check error in console:**
   - Press F12
   - Look at Console tab
   - Copy-paste full error message

2. **Search online:**
   - Google the error message
   - Check Three.js docs
   - Check React Three Fiber docs

3. **Check documentation files:**
   - README.md (overview)
   - DOCUMENTATION.md (technical)
   - threejs/README.md (getting started)

4. **Contact resources:**
   - Three.js Discord
   - Stack Overflow
   - GitHub Issues

---

## 🎓 Next Steps After Installation

1. **Explore the UI:**
   - Rotate camera around scene
   - Try adjusting all sliders
   - Observe material changes

2. **Read documentation:**
   - Open README.md (main folder)
   - Read DOCUMENTATION.md (technical)
   - Review code comments

3. **Customize:**
   - Try changing geometry sizes
   - Modify light positions
   - Create new materials

4. **Capture screenshots:**
   - Take GIFs of your work
   - Save to media/ folder
   - Update README

---

## 🔐 Security Notes

- Don't commit `node_modules/` (use .gitignore)
- Don't share `.env` files with secrets
- Keep npm packages updated
- Check vulnerabilities: `npm audit`

---

**Installation Guide Updated:** March 28, 2026  
**Version:** 1.0  
**Status:** Ready ✅
