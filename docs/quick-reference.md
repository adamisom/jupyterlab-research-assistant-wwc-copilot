# JupyterLab Extension Development - Quick Reference

## Essential Commands

1. **Build extension**: `jlpm build`
2. **Link extension for development**: `jupyter labextension develop . --overwrite`
3. **Run JupyterLab**: `jupyter lab`

## Checking if Extension is Active

- **Command Palette**: Press `Cmd+Shift+C` (Mac) or `View → Show Command Palette`, look for commands starting with your extension name
- **Browser Console**: Press `F12` or `Cmd+Option+I`, check for extension loading messages or errors
- **Terminal**: Check JupyterLab startup logs for extension loading messages
- **Extension List**: Run `jupyter labextension list` to verify extension is enabled

## For Future Development

- **TypeScript/React changes**: Run `jlpm watch` in a separate terminal, then refresh browser
- **Python changes**: Restart JupyterLab
- **Manual build**: `jlpm build` when needed
