# AI-Powered Code Review System

> Automate your code reviews with LLM-powered analysis for GitLab and GitHub

**🔗 Repository**: [https://github.com/synthetic-horizons/ai-code-reviewer](https://github.com/synthetic-horizons/ai-code-reviewer)

## 📖 Overview

This project provides an automated AI code review system that integrates seamlessly with GitLab CI/CD and GitHub Actions. Using state-of-the-art language models via [OpenRouter](https://openrouter.ai), it provides instant, comprehensive code reviews on every merge/pull request.

### Key Features

✅ **Instant feedback** on merge/pull requests  
✅ **Multi-language support** with automatic detection  
✅ **Security-focused** analysis  
✅ **Cost-effective** using OpenRouter API  
✅ **Non-blocking** - never stops your deployments  
✅ **Easy setup** - just one script and configuration file

### What Gets Reviewed

The AI reviewer analyzes your code for:

1. **Bugs & Logic Errors**: Edge cases, potential runtime issues
2. **Security Vulnerabilities**: SQL injection, sensitive data exposure, authentication issues
3. **Best Practices**: Language-specific coding standards
4. **Performance**: Obvious optimization opportunities
5. **Code Quality**: Readability, maintainability, error handling

---

## 🚀 Quick Start

### Prerequisites

- A GitLab or GitHub repository
- An OpenRouter API key ([get one here](https://openrouter.ai/keys))
- For GitLab: GitLab CI/CD enabled
- For GitHub: GitHub Actions enabled

### Cost Estimate

Using Claude 3.5/4.5 Sonnet costs approximately **$0.01-0.05 per review**, making this solution extremely cost-effective compared to developer time.

---

## 📦 Installation

### Step 1: Add the Reviewer Script

Create the directory structure and get the Python script from the repository:

```bash
mkdir -p scripts/python
curl -o scripts/python/llm_reviewer.py https://raw.githubusercontent.com/synthetic-horizons/ai-code-reviewer/main/llm_reviewer.py
```

**For GitLab**: Rename it to `llm_mr_review.py`
**For GitHub**: Keep it as `llm_reviewer.py`

> 📖 **View the complete script**: [`llm_reviewer.py`](https://github.com/synthetic-horizons/ai-code-reviewer/blob/main/llm_reviewer.py)

### Step 2: Configure Your CI/CD

Choose your platform:

#### Option A: GitLab CI/CD

1. **Add this job to your `.gitlab-ci.yml`**:

```yaml
LLM Code Review:
  image: python:3.13-slim
  stage: test
  allow_failure: true
  script:
    - pip install requests
    - python scripts/python/llm_mr_review.py
  only:
    - merge_requests
```

2. **Set CI/CD Variables** (Settings → CI/CD → Variables):

| Variable | Value | Protected | Masked |
|----------|-------|-----------|--------|
| `OPENROUTER_API_KEY` | `sk-or-v1-...` | ✓ | ✓ |
| `LLM_MODEL` | `anthropic/claude-sonnet-4.5` | ✗ | ✗ |
| `GITLAB_PRIVATE_TOKEN` | `glpat-...` (optional) | ✓ | ✓ |

> 📖 **See full examples**: [`.gitlab-ci.example.yml`](https://github.com/synthetic-horizons/ai-code-reviewer/blob/main/.gitlab-ci.example.yml)

#### Option B: GitHub Actions

1. **Create `.github/workflows/llm-code-review.yml`** with this minimal config:

```yaml
name: LLM Code Review

on:
  pull_request:
    types: [opened, synchronize, reopened]

jobs:
  llm-code-review:
    runs-on: ubuntu-latest
    continue-on-error: true
    env:
      OPENROUTER_API_KEY: ${{ secrets.OPENROUTER_API_KEY }}
      LLM_MODEL: ${{ vars.LLM_MODEL }}
      GITHUB_TOKEN: ${{ secrets.GITHUB_TOKEN }}
    
    steps:
      - uses: actions/checkout@v4
      - uses: actions/setup-python@v5
        with:
          python-version: '3.13'
      - run: pip install requests
      - run: python scripts/python/llm_reviewer.py
```

2. **Set Repository Secrets and Variables** (Settings → Secrets and variables → Actions):

**Secrets**:
- `OPENROUTER_API_KEY`: Your OpenRouter API key
- `GITHUB_TOKEN`: Automatically provided by GitHub

**Variables**:
- `LLM_MODEL`: The model to use (e.g., `anthropic/claude-sonnet-4.5`)

> 📖 **See full examples**: [`.github-actions.example.yml`](https://github.com/synthetic-horizons/ai-code-reviewer/blob/main/.github-actions.example.yml)

### Step 3: Test It

1. Create a test branch
2. Make a small code change
3. Open a merge/pull request
4. Wait 10-30 seconds for the AI review comment to appear

---

## 🔧 Configuration

### Environment Variables

#### Required

| Variable | Description | Example |
|----------|-------------|---------|
| `OPENROUTER_API_KEY` | Your OpenRouter API key | `sk-or-v1-...` |
| `LLM_MODEL` | Model to use for reviews | `anthropic/claude-sonnet-4.5` |

#### Optional

| Variable | Description | Default |
|----------|-------------|---------|
| `GITLAB_PRIVATE_TOKEN` | GitLab personal access token | Uses `CI_JOB_TOKEN` if not set |

### Supported Models

You can use any OpenRouter-compatible model. Configure via CI/CD variable:

- `anthropic/claude-sonnet-4.5` (Recommended - best quality)
- `anthropic/claude-3.5-sonnet` (Fast and cost-effective)
- `google/gemini-2.0-flash-exp` (Very fast, experimental)
- `openai/gpt-4-turbo` (Good alternative)

**GitLab**: Set `LLM_MODEL` in CI/CD Variables (Settings → CI/CD → Variables)

**GitHub**: Set `LLM_MODEL` in Variables (Settings → Secrets and variables → Actions → Variables)

This allows you to take advantage of OpenRouter's flexibility and change models without modifying code.

### Supported Languages

The script automatically detects and reviews code in:

| Language | Extension | Language | Extension |
|----------|-----------|----------|-----------|
| Python | `.py` | JavaScript | `.js` |
| TypeScript | `.ts` | React (JS) | `.jsx` |
| React (TS) | `.tsx` | Java | `.java` |
| Go | `.go` | Rust | `.rs` |
| PHP | `.php` | Ruby | `.rb` |
| C | `.c` | C++ | `.cpp` |
| C# | `.cs` | HTML | `.html` |
| CSS | `.css` | SCSS | `.scss` |
| SQL | `.sql` | YAML | `.yml`, `.yaml` |
| JSON | `.json` | Markdown | `.md` |
| Shell | `.sh` | Dockerfile | `.dockerfile` |

To add more languages, edit the `ext_map` dictionary in [`llm_reviewer.py`](llm_reviewer.py:68-92).

---

## 🎯 How It Works

### Architecture Flow

```
Merge/Pull Request Created
         ↓
   CI/CD Triggered
         ↓
  Python Script Runs
         ↓
  Fetch MR/PR Changes
         ↓
  Detect Languages
         ↓
Build Context-Aware Prompt
         ↓
Send to OpenRouter API
         ↓
  Claude Analyzes Code
         ↓
 Receive Review Feedback
         ↓
Post Comment on MR/PR
         ↓
   Developer Notified
```

### The Review Process

1. **Fetch Changes**: Uses GitLab/GitHub API to get the diff
2. **Language Detection**: Analyzes file extensions to identify languages
3. **Context Building**: Creates a detailed prompt with project context
4. **AI Analysis**: Sends to OpenRouter API (Claude models)
5. **Post Review**: Comments back on the merge/pull request

### Review Guidelines

The AI reviewer follows these guidelines:

```python
Review Guidelines:
1. Analyze the code for bugs, logical errors, and edge cases.
2. Check for security vulnerabilities (e.g., injection, sensitive data exposure, auth issues).
3. Ensure adherence to best practices and coding standards for the detected languages.
4. Suggest performance improvements where obvious.
5. Check for readability, maintainability, and proper error handling.
6. Be concise, constructive, and polite.
```

---

## 🛠️ Customization

### Modifying the Review Prompt

Edit the `system_prompt` in the script to customize the review focus for your team's needs.

**Key sections to customize**:

- Review guidelines (lines 105-111)
- Project-specific context
- Security focus areas
- Performance criteria

> 📖 **View the prompt**: [`llm_reviewer.py#L98-L116`](https://github.com/synthetic-horizons/ai-code-reviewer/blob/main/llm_reviewer.py#L98-L116)

### Adding More Language Detections

Extend the `ext_map` dictionary around line 68 to support additional languages:

```python
ext_map = {
    # ... existing mappings
    ".swift": "Swift",
    ".kt": "Kotlin",
    ".vim": "VimScript",
}
```

> 📖 **See all supported languages**: [`llm_reviewer.py#L68-L92`](https://github.com/synthetic-horizons/ai-code-reviewer/blob/main/llm_reviewer.py#L68-L92)

### Adjusting AI Temperature

Lower temperature = more deterministic reviews:

```python
payload = {
    "model": LLM_MODEL,
    "messages": messages,
    "temperature": 0.2  # Range: 0.0 (focused) to 1.0 (creative)
}
```

### Integration with Other Tools

Combine with traditional quality gates:

```yaml
# Example: Add alongside SonarQube
stages:
  - test

LLM Code Review:
  stage: test
  # ... config as above

SonarQube Analysis:
  stage: test
  image: sonarsource/sonar-scanner-cli:latest
  script:
    - sonar-scanner -Dsonar.qualitygate.wait=true
  only:
    - merge_requests
```

**Recommended Stack:**

- **SonarQube/Ruff/Pylint**: Static analysis, code coverage
- **LLM Review**: Contextual analysis, security patterns, best practices  
- **Human Review**: Architecture decisions, business logic validation

---

## 🐛 Troubleshooting

### Common Issues

#### "Missing required environment variables"

**Problem**: The script can't find required API keys or tokens.

**Solution**:

- GitLab: Ensure `OPENROUTER_API_KEY` is set in CI/CD variables
- GitHub: Ensure `OPENROUTER_API_KEY` is set in repository secrets
- Verify the variable names are exact (case-sensitive)

#### "OpenRouter API Error: 401"

**Problem**: Invalid or expired API key.

**Solution**:

- Check your OpenRouter API key at <https://openrouter.ai/keys>
- Ensure the key is correctly copied (no extra spaces)
- Verify the key has sufficient credits

#### "No changes found in this MR"

**Problem**: The script can't fetch the diff.

**Solution**:

- For GitLab: Ensure the job runs `only: - merge_requests`
- For GitHub: Ensure workflow triggers on `pull_request` events
- Check that `CI_JOB_TOKEN` or `GITHUB_TOKEN` has API access

#### Review Takes Too Long

**Problem**: Large diffs cause timeouts.

**Solution**:

- Limit MR/PR size (aim for <50 files)
- Increase job timeout in CI/CD settings
- Consider switching to a faster model (e.g., `google/gemini-2.0-flash-exp`)

#### Script Fails But Doesn't Stop Pipeline

**Expected Behavior**: The script is configured with `allow_failure: true` (GitLab) or `continue-on-error: true` (GitHub) to never block deployments.

---

## 📊 Best Practices

### 1. Progressive Rollout

Start small and expand:

1. **Phase 1**: Single team, gather feedback
2. **Phase 2**: Multiple teams with customized prompts
3. **Phase 3**: Organization-wide deployment
4. **Phase 4**: Enhanced rules + custom models

### 2. Set Expectations

- AI reviews **augment**, not replace human reviews
- Use AI for first-pass screening
- Senior developers focus on architecture and business logic

### 3. Monitor Usage

Track these metrics:

- **Time to first feedback**: Reduction in wait time
- **Issues caught pre-merge**: Security/bug findings by AI
- **Review iteration count**: Fewer revision cycles?
- **Developer satisfaction**: Survey team on review quality

### 4. Optimize Costs

- Use `temperature: 0.2` for deterministic reviews
- Switch models based on project needs
- Monitor your OpenRouter usage dashboard

### 5. Keep It Updated

- Regularly review and update the `system_prompt`
- Add new language mappings as your stack grows
- Test new models for quality/cost improvements

---

## 🔒 Security Considerations

### API Key Management

- **Never** commit API keys to your repository
- Use CI/CD variables/secrets (masked and protected)
- Rotate keys periodically
- Limit key permissions to minimum required

### Token Permissions

**GitLab**:

- `CI_JOB_TOKEN`: Automatically provided, scoped to job
- `GITLAB_PRIVATE_TOKEN`: Only needed for private projects

**GitHub**:

- `GITHUB_TOKEN`: Automatically provided with Actions
- Has read/write access to repository by default

### Data Privacy

- Code diffs are sent to OpenRouter API
- Review OpenRouter's [privacy policy](https://openrouter.ai/privacy)
- For sensitive code, consider self-hosted LLM solutions
- Diffs are not stored permanently by default

---

## 🎓 Example Review Output

When you open a merge/pull request, you'll receive a comment like:

```markdown
## 🤖 AI Code Review (Model: anthropic/claude-4.5-sonnet)

### Overall Assessment
The changes look good overall. I've reviewed the authentication improvements 
and database query optimizations.

### File: src/auth/login.py
✅ **Security**: Password hashing implementation looks correct
⚠️ **Suggestion**: Consider adding rate limiting to prevent brute-force attacks
💡 **Best Practice**: Add logging for failed login attempts

### File: src/database/queries.py
✅ **Performance**: Good use of connection pooling
⚠️ **Security**: Parameterized queries correctly prevent SQL injection
⚠️ **Edge Case**: Consider handling empty result sets with a default value

### Summary
- 2 security improvements suggested
- 1 edge case to consider
- Overall code quality is high
```

---

## 📚 Additional Resources

### Documentation

- [OpenRouter API Documentation](https://openrouter.ai/docs)
- [GitLab CI/CD Documentation](https://docs.gitlab.com/ee/ci/)
- [GitHub Actions Documentation](https://docs.github.com/en/actions)

### Related Projects

- [SonarQube](https://www.sonarqube.org/) - Static code analysis
- [Ruff](https://github.com/astral-sh/ruff) - Python linter
- [Pyright](https://github.com/microsoft/pyright) - Type checking

### Example Configurations

- [`.gitlab-ci.example.yml`](.gitlab-ci.example.yml) - GitLab configuration examples
- [`.github-actions.example.yml`](.github-actions.example.yml) - GitHub Actions examples

---

## 🤝 Contributing

This is an open framework you can customize for your needs. Feel free to:

- Modify the review prompt for your team's standards
- Add support for more languages
- Integrate with other CI/CD platforms
- Share your improvements with the community

---

## 📝 License

This project is provided as-is for educational and commercial use. Customize it to fit your organization's needs.

---

## 👥 About

**Created by François Bossière, co-CEO of [Polynom](https://www.polynom.io)**

*Polynom is an AI Consulting firm specialized in building high impact Data & AI products.*

**Contact**: <francois@synthetic-horizons.com>

### Philosophy

> AI should augment, not replace, human expertise. This tool helps developers focus on what matters: architecture, mentoring, and innovation.

---

**Questions or Issues?** Open an issue or reach out to us at [www.polynom.io](https://www.polynom.io)

*Last Updated: January 2025*

---

## 🌟 Quick Reference

### GitLab Setup Checklist

- [ ] Copy `llm_reviewer.py` to `scripts/python/llm_mr_review.py`
- [ ] Add job config to `.gitlab-ci.yml`
- [ ] Set `OPENROUTER_API_KEY` in CI/CD variables (masked & protected)
- [ ] Set `LLM_MODEL` in CI/CD variables (e.g., `anthropic/claude-sonnet-4.5`)
- [ ] (Optional) Set `GITLAB_PRIVATE_TOKEN` in CI/CD variables
- [ ] Create test MR to verify setup
- [ ] Customize review guidelines if needed

### GitHub Setup Checklist

- [ ] Copy `llm_reviewer.py` to `scripts/python/llm_reviewer.py`
- [ ] Create `.github/workflows/llm-code-review.yml`
- [ ] Set `OPENROUTER_API_KEY` in repository secrets
- [ ] Set `LLM_MODEL` in repository variables (e.g., `anthropic/claude-sonnet-4.5`)
- [ ] Create test PR to verify setup
- [ ] Customize review guidelines if needed
