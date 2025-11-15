# Environment Configuration Setup Guide

## Overview
This project uses environment variables to manage sensitive configuration like API keys and endpoints. Never commit actual API keys or credentials to the repository.

## Files

### `.env` (LOCAL - NOT COMMITTED)
- **Purpose:** Stores your actual API keys and sensitive configuration
- **Status:** Listed in `.gitignore` - never pushed to GitHub
- **Location:** Project root directory
- **Content:** Your actual credentials and configuration values

### `.env.example` (COMMITTED)
- **Purpose:** Template showing what environment variables are needed
- **Status:** Safe to commit - contains no real credentials
- **Location:** Project root directory
- **Content:** Placeholder values and documentation

### `.gitignore` (COMMITTED)
- **Purpose:** Prevents sensitive files from being accidentally committed
- **Status:** Safe to commit
- **Entries:** `.env`, `.env.local`, and other sensitive patterns

## Setup Instructions

### Initial Setup
1. Copy `.env.example` to `.env`:
   ```bash
   cp .env.example .env
   ```

2. Edit `.env` with your actual credentials:
   ```bash
   # Azure OpenAI Configuration
   AZURE_OPENAI_ENDPOINT=https://your-resource-name.openai.azure.com/
   AZURE_OPENAI_API_KEY=your-actual-api-key-here
   AZURE_OPENAI_API_VERSION=2024-08-01-preview
   AZURE_OPENAI_DEPLOYMENT=GPT-4o-0806
   ```

3. Save the file - never commit it!

### Configuration Access in Python
```python
from config.config import Config

# All values are automatically loaded from .env
endpoint = Config.AZURE_OPENAI_ENDPOINT
api_key = Config.AZURE_OPENAI_API_KEY
temperature = Config.MODEL_TEMPERATURE
```

## Environment Variables Reference

### Azure OpenAI Configuration
| Variable | Default | Description |
|----------|---------|-------------|
| `AZURE_OPENAI_ENDPOINT` | (none) | Your Azure OpenAI endpoint URL |
| `AZURE_OPENAI_API_KEY` | (none) | Your Azure OpenAI API key |
| `AZURE_OPENAI_API_VERSION` | `2024-08-01-preview` | API version |
| `AZURE_OPENAI_DEPLOYMENT` | `GPT-4o-0806` | Deployment name |

### OpenModelica Configuration
| Variable | Default | Description |
|----------|---------|-------------|
| `OMC_COMMAND` | `omc` | OpenModelica compiler command |
| `SIMULATION_TIMEOUT` | `300` | Simulation timeout in seconds |

### Agent Configuration
| Variable | Default | Description |
|----------|---------|-------------|
| `MODEL_TEMPERATURE` | `0.7` | LLM temperature (0.0-1.0) |
| `MAX_TOKENS` | `4000` | Max tokens for LLM response |

### Visualization Configuration
| Variable | Default | Description |
|----------|---------|-------------|
| `FIGURE_DPI` | `300` | Figure resolution (DPI) |
| `FIGURE_SIZE_WIDTH` | `12` | Default figure width (inches) |
| `FIGURE_SIZE_HEIGHT` | `8` | Default figure height (inches) |
| `SEABORN_STYLE` | `darkgrid` | Seaborn plot style |
| `COLOR_PALETTE` | `husl` | Color palette for plots |

## Security Best Practices

### ✅ DO:
- Keep `.env` in `.gitignore`
- Use `.env.example` as a template
- Set strong API keys in `.env`
- Rotate API keys periodically
- Use different keys for dev/staging/prod
- Add environment-specific `.env` files (.env.local, .env.production) to `.gitignore`

### ❌ DON'T:
- Commit `.env` to version control
- Share API keys via email or chat
- Hardcode credentials in source code
- Use the same key across environments
- Log sensitive information
- Include credentials in stack traces

## If Credentials Were Accidentally Committed

If you accidentally committed credentials to GitHub:

1. **Immediately rotate the exposed keys** in your Azure/OpenAI dashboard
2. **Clean Git history:**
   ```bash
   # Option 1: Using git-filter-branch (simple)
   git filter-branch --force --index-filter \
   'git rm -r --cached --ignore-unmatch .env' \
   --prune-empty --tag-name-filter cat -- --all
   
   # Option 2: Using BFG (faster for large repos)
   bfg --delete-files .env
   ```

3. **Force push the cleaned history:**
   ```bash
   git push --all --force
   git push --tags --force
   ```

4. **Notify all collaborators** to rebase their branches

## Debugging Configuration Issues

### Check if variables are loaded:
```python
from config.config import Config
import os

print("Environment variables:")
print(f"API Key is set: {bool(os.getenv('AZURE_OPENAI_API_KEY'))}")
print(f"Endpoint: {Config.AZURE_OPENAI_ENDPOINT}")
```

### Common Issues:
- **Variables are empty:** Make sure `.env` exists and is readable
- **Module not found:** Ensure `python-dotenv` is installed: `pip install python-dotenv`
- **Path issues:** The config loader expects `.env` in the project root

## CI/CD Integration

For GitHub Actions or other CI/CD:
1. Add secrets in your platform's secret management
2. Set environment variables in workflow files
3. Never hardcode values in workflow YML files

Example GitHub Actions:
```yaml
env:
  AZURE_OPENAI_ENDPOINT: ${{ secrets.AZURE_OPENAI_ENDPOINT }}
  AZURE_OPENAI_API_KEY: ${{ secrets.AZURE_OPENAI_API_KEY }}
```

## Files Modified

- ✅ `config/config.py` - Now reads from `.env`
- ✅ `.env` - Created (empty template - add your credentials)
- ✅ `.env.example` - Created (template with placeholder values)
- ✅ `.gitignore` - Updated with comprehensive security rules
