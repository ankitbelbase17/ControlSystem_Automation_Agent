# Quick Reference - Environment Configuration

## Essential Commands

### Setup (Do This First)
```bash
# Copy the template
cp .env.example .env

# Edit with your credentials (use your preferred editor)
nano .env
# OR
code .env
# OR
vim .env
```

### Verify Configuration Works
```bash
python -c "from config.config import Config; print(f'Endpoint: {Config.AZURE_OPENAI_ENDPOINT}')"
```

### Check Git Status
```bash
# Should show .env is ignored
git status --ignored

# Verify no .env history in git
git log --all -p -- .env | head -20
```

---

## File Locations

| File | Location | Purpose | Committed? |
|------|----------|---------|-----------|
| `.env` | Project root | Your credentials | NO |
| `.env.example` | Project root | Template | YES |
| `.gitignore` | Project root | Git rules | YES |
| `config/config.py` | config/ | Config loader | YES |
| `ENV_SETUP.md` | Project root | Full guide | YES |
| `SECURITY_CHECKLIST.md` | Project root | Verification | YES |

---

## Environment Variables

### Required (No Defaults)
```env
AZURE_OPENAI_ENDPOINT=https://your-resource.openai.azure.com/
AZURE_OPENAI_API_KEY=your-api-key-here
```

### Optional (Have Defaults)
```env
AZURE_OPENAI_API_VERSION=2024-08-01-preview
AZURE_OPENAI_DEPLOYMENT=GPT-4o-0806
MODEL_TEMPERATURE=0.7
MAX_TOKENS=4000
FIGURE_DPI=300
FIGURE_SIZE_WIDTH=12
FIGURE_SIZE_HEIGHT=8
SEABORN_STYLE=darkgrid
COLOR_PALETTE=husl
OMC_COMMAND=omc
SIMULATION_TIMEOUT=300
```

---

## Using Configuration in Code

```python
from config.config import Config

# Access any configuration value
endpoint = Config.AZURE_OPENAI_ENDPOINT
api_key = Config.AZURE_OPENAI_API_KEY
temperature = Config.MODEL_TEMPERATURE
timeout = Config.SIMULATION_TIMEOUT

# Get all config as dictionary
all_config = Config.to_dict()
```

---

## Troubleshooting

### Variables not loading?
1. Check `.env` exists in project root (not in subfolder)
2. Verify variable names match exactly (case-sensitive)
3. Check file permissions are readable
4. Ensure `python-dotenv` is installed: `pip install python-dotenv`

### "ModuleNotFoundError: dotenv"?
```bash
pip install python-dotenv
```

### Accidentally committed .env?
1. **Immediately rotate your API keys** in Azure/OpenAI
2. Run cleanup command (see ENV_SETUP.md)
3. Force push to remove history

### CI/CD environment variables?
Use your platform's secrets management:
- **GitHub Actions**: Settings → Secrets
- **GitLab**: Settings → CI/CD → Variables
- **Others**: Check their documentation

---

## Team Workflow

### For Team Lead
1. Create `.env.example` with template ✓ (Done)
2. Add to `.gitignore` ✓ (Done)
3. Share `.env.example` with team
4. Document setup in README

### For Team Members
1. Clone repository
2. Copy: `cp .env.example .env`
3. Edit `.env` with your credentials
4. Never commit `.env`
5. Read `ENV_SETUP.md` if questions

---

## Security Checklist

Before pushing to GitHub:
- [ ] No `.env` file in git
- [ ] `.env.example` has placeholder values only
- [ ] `config.py` uses `os.getenv()` for secrets
- [ ] `.gitignore` blocks `.env*`
- [ ] No API keys in code comments
- [ ] No secrets in stack traces/logs

---

## One-Liner Tests

```bash
# Test config loads
python -c "from config.config import Config; print('OK' if Config.AZURE_OPENAI_API_VERSION else 'FAIL')"

# Check .env is ignored
git check-ignore .env

# Search git history for exposed keys
git log --all -S "your-api-key" --oneline

# Show current .env variables
grep -E "^[A-Z_]+" .env | head -10
```

---

## Remember

✅ DO:
- Keep credentials in `.env`
- Rotate keys if exposed
- Use different keys per environment
- Check git before pushing

❌ DON'T:
- Commit `.env` to GitHub
- Share API keys
- Hardcode credentials
- Log sensitive data

---

**Questions?** Read `ENV_SETUP.md` for complete documentation.
