# GitHub Codebase Analyzer - Usage Examples

## Quick Start

### Analyze a GitHub Repository

#### Option 1: Direct Python Command
```bash
# Basic usage
python analyzer.py --url https://github.com/microsoft/vscode

# With GitHub token for better rate limits
python analyzer.py --url https://github.com/facebook/react --token YOUR_GITHUB_TOKEN

# Specify output directory
python analyzer.py --url https://github.com/golang/go --output my_analysis
```

#### Option 2: Using the Launcher
```bash
# Using the Python launcher
python launcher.py --url https://github.com/microsoft/vscode

# Run tests
python launcher.py --test

# Check installation
python launcher.py --check
```

#### Option 3: Using Platform Scripts

**Windows:**
```cmd
analyze.bat "https://github.com/microsoft/vscode"
```

**Linux/macOS:**
```bash
chmod +x analyze.sh
./analyze.sh "https://github.com/microsoft/vscode"
```

## Example Analysis Results

After running the analyzer on a repository, you'll get:

### Generated Documentation Structure
```
output/
├── README.md                              # Comprehensive project documentation
├── analysis/
│   ├── technology_analysis.md            # Detected technologies and frameworks
│   └── dependency_analysis.md            # Dependencies and security analysis
├── architecture/
│   └── architecture_analysis.md          # System architecture documentation
├── uml/
│   ├── use_case_diagram.puml             # PlantUML use case diagram
│   ├── class_diagram.puml                # PlantUML class diagram
│   └── component_diagram.puml            # PlantUML component diagram
└── api/
    └── api_specification.md              # API documentation
```

### Sample Analysis: VS Code Repository

**Technologies Detected:**
- Express (Web Framework)
- Jest & Mocha (Testing)
- TypeScript (Primary Language)
- PostgreSQL & SQLite (Databases)

**Dependencies Found:**
- 148 total dependencies (45 production, 103 development)
- Major packages: electron, typescript, webpack, etc.

**Code Metrics:**
- 50+ files analyzed (limited for demo)
- Thousands of lines of code
- Multiple TypeScript modules and utilities

## Setting Up GitHub Token

For better rate limits and access to private repositories:

1. **Create a GitHub Personal Access Token:**
   - Go to GitHub Settings > Developer settings > Personal access tokens
   - Generate new token with `repo` scope
   - Copy the token

2. **Set Environment Variable:**

   **Windows:**
   ```cmd
   set GITHUB_TOKEN=your_token_here
   ```

   **Linux/macOS:**
   ```bash
   export GITHUB_TOKEN=your_token_here
   ```

3. **Or pass directly:**
   ```bash
   python analyzer.py --url https://github.com/owner/repo --token your_token_here
   ```

## Customization

### Configuration File
Edit `config/analysis_config.yaml` to customize:
- File exclusions
- Analysis depth
- Output formats
- Rate limiting settings

### Adding New Technologies
Extend the technology detection patterns in `analyzer.py`:
```python
"new_framework": [r"import.*newframework", "newframework"]
```

## Troubleshooting

### Common Issues

1. **Rate Limiting:**
   - Set GITHUB_TOKEN environment variable
   - Analyze smaller repositories first
   - Wait between analyses

2. **Permission Errors:**
   - Ensure repository is public or you have access
   - Check GitHub token permissions

3. **Large Repositories:**
   - Analysis is limited to 50 files by default
   - Modify `max_files` variable for more comprehensive analysis

### Error Messages

- `403 Client Error: rate limit exceeded` → Set GitHub token
- `404 Client Error: Not Found` → Check repository URL or permissions
- `ImportError` → Install missing dependencies with `pip install -r requirements.txt`

## Example Workflows

### 1. Quick Technology Assessment
```bash
# Analyze a repository to understand its tech stack
python analyzer.py --url https://github.com/owner/repo
# Check: output/analysis/technology_analysis.md
```

### 2. Dependency Security Review
```bash
# Analyze dependencies for security assessment
python analyzer.py --url https://github.com/owner/repo
# Check: output/analysis/dependency_analysis.md
```

### 3. Architecture Documentation
```bash
# Generate architecture documentation for a project
python analyzer.py --url https://github.com/owner/repo
# Check: output/architecture/architecture_analysis.md
# Check: output/uml/*.puml files
```

### 4. API Documentation Generation
```bash
# Extract and document APIs
python analyzer.py --url https://github.com/owner/repo
# Check: output/api/api_specification.md
```

## Advanced Usage

### Batch Analysis
Create a script to analyze multiple repositories:

```python
repositories = [
    "https://github.com/microsoft/vscode",
    "https://github.com/facebook/react",
    "https://github.com/golang/go"
]

for repo in repositories:
    os.system(f"python analyzer.py --url {repo} --output analysis_{repo.split('/')[-1]}")
```

### Integration with CI/CD
Add to your CI pipeline:

```yaml
# GitHub Actions example
- name: Analyze Codebase
  run: |
    pip install -r requirements.txt
    python analyzer.py --url ${{ github.repository_url }}
    # Upload results as artifacts
```

## Limitations

- Analysis limited to public repositories (unless token provided)
- File analysis limited to 50 files by default (configurable)
- Some complex dependency structures may not be fully captured
- API detection based on common patterns (may miss custom implementations)

## Support

For questions, issues, or contributions:
- Check the main README.md for project information
- Review the generated documentation for insights
- Modify the analyzer.py file for custom analysis needs
