# Binder Setup Guide

This extension is configured to work on Binder.org. The `binder/postBuild` script automatically installs and builds everything.

## Quick Start

1. Go to [mybinder.org](https://mybinder.org)
2. Paste your repo URL: `https://github.com/adamisom/jupyterlab-research-assistant-wwc-copilot`
3. Click "launch"

**Direct link:**

```
https://mybinder.org/v2/gh/adamisom/jupyterlab-research-assistant-wwc-copilot/HEAD
```

## Setting API Keys

### Semantic Scholar API Key

To use your Semantic Scholar API key (for higher rate limits), set it in a notebook cell:

```python
import os
os.environ['SEMANTIC_SCHOLAR_API_KEY'] = 'your-api-key-here'
```

Or use the helper script:

```python
%run binder/set_api_key.py
```

**Note:** You may need to restart the kernel after setting the environment variable.

### AI Extraction (OpenAI/Claude)

1. Go to **Settings → Settings Editor → Research Assistant**
2. Enable "AI Extraction"
3. Select provider (OpenAI or Claude)
4. Enter your API key
5. Select model (e.g., `gpt-4-turbo` for OpenAI)

## Features Enabled on Binder

✅ **Conflict Detection** - Automatically installed with transformers library  
✅ **Semantic Scholar API** - Works with or without API key (falls back to OpenAlex)  
✅ **Meta-Analysis** - Full support  
✅ **WWC Assessment** - Full support  
✅ **PDF Import** - Full support

## Getting Your API Keys

- **Semantic Scholar**: https://www.semanticscholar.org/product/api
- **OpenAI**: Search for "OpenAI API keys" to find the API key management page
- **Anthropic Claude**: Search for "Anthropic Claude console" to find the API key management page

## Troubleshooting

If conflict detection doesn't work:

- The transformers library should install automatically
- First run will download the NLI model (~500MB-1GB) - this is normal
- Check browser console for any errors

If Semantic Scholar search fails:

- The system automatically falls back to OpenAlex (no API key needed)
- Check that your API key is set correctly if you want higher rate limits
