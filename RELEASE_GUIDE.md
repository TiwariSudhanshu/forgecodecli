# ForgeCodeCLI Release Guide

## Quick Start - Create a GitHub Release

### Prerequisites
- Latest code committed
- `.exe` built in `dist/forgecodecli.exe`
- Git and GitHub CLI installed

### Steps

#### 1. Update Version Numbers
```bash
# Update in pyproject.toml
version = "3.0.0"

# Update in README if needed
```

#### 2. Build the .exe
```bash
cd C:\Users\ASUS\Desktop\forgecodecli
pyinstaller forgecodecli.spec
```

#### 3. Create GitHub Release (Option A: Using CLI)
```bash
gh release create v3.0.0 \
  --title "ForgeCodeCLI v3.0 - Git Operations" \
  --notes-file RELEASES.md \
  dist/forgecodecli.exe
```

#### 4. Create GitHub Release (Option B: Using Web UI)
1. Go to https://github.com/TiwariSudhanshu/forgecodecli/releases
2. Click "Create a new release"
3. Tag: `v3.0.0`
4. Title: `ForgeCodeCLI v3.0 - Git Operations`
5. Description: Copy from [RELEASES.md](RELEASES.md)
6. Upload binary: Drag `dist/forgecodecli.exe`
7. Publish

---

## Release Checklist

- [ ] All features implemented and tested
- [ ] Code committed and pushed
- [ ] RELEASES.md updated
- [ ] `.exe` file generated
- [ ] Version bumped in pyproject.toml
- [ ] GitHub release created
- [ ] Release announcement posted

---

## Distribution

### For End Users
- Download `.exe` from [Releases](https://github.com/TiwariSudhanshu/forgecodecli/releases)
- Run directly (no Python needed)
- Initialize with: `forgecodecli init`
- Start using: `forgecodecli`

### For Developers
```bash
pip install forgecodecli
# or
pip install git+https://github.com/TiwariSudhanshu/forgecodecli.git
```

---

## Notes
- `.exe` size: ~20.8 MB (includes Python runtime)
- Recommended: Include release notes linking to [README.md](README.md)
- Keep `RELEASES.md` updated for each version
