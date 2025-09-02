# GitHub Codebase Analyzer

A comprehensive GitHub codebase analyzer built with Jac and Jaseci programming languages. This tool analyzes GitHub repositories and generates detailed documentation including UML diagrams, API specifications, requirements analysis, technology stack documentation, and architecture analysis.

## 🌟 Features

- **Repository Analysis**: Complete GitHub repository scanning and analysis
- **Code Structure Analysis**: Extract functions, classes, and complexity metrics
- **Dependency Analysis**: Analyze project dependencies from multiple package managers
- **Technology Detection**: Automatically detect frameworks, libraries, and tools used
- **UML Diagram Generation**: Generate use case, class, and component diagrams
- **API Documentation**: Extract and document REST API endpoints with OpenAPI specs
- **Requirements Analysis**: Generate functional and non-functional requirements
- **Architecture Documentation**: Analyze and document system architecture
- **Technology Stack Report**: Comprehensive technology usage analysis

## 🏗️ Architecture

The project follows a modular architecture with specialized walkers for different analysis tasks:

```
src/
├── main.jac                    # Main entry point and orchestration
├── walkers/
│   └── github_api_walker.jac   # GitHub API integration
├── analyzers/
│   ├── code_analyzer.jac       # Code structure analysis
│   ├── dependency_analyzer.jac # Dependency analysis
│   └── technology_detector.jac # Technology detection
└── generators/
    └── documentation_generator.jac # Documentation generation
```

## 🚀 Quick Start

### Prerequisites

- Python 3.8 or higher
- Jaseci framework
- Git
- Optional: GitHub API token for enhanced rate limits

### Installation

1. Clone the repository:
```bash
git clone https://github.com/your-username/github-codebase-analyzer.git
cd github-codebase-analyzer
```

2. Install dependencies:
```bash
pip install -r requirements.txt
```

3. Install Jaseci (if not already installed):
```bash
pip install jaseci
```

4. Set up GitHub API token (optional but recommended):
```bash
export GITHUB_TOKEN=your_github_token_here
```

### Usage

1. **Basic Analysis**:
```bash
jac run src/main.jac
```

2. **Run Tests**:
```bash
jac run tests/test_analyzer.jac
```

3. **Custom Configuration**:
Edit `config/analysis_config.yaml` to customize analysis parameters.

## 📋 Configuration

The analyzer can be configured through `config/analysis_config.yaml`:

```yaml
analysis:
  depth: "full"  # Options: basic, full, files_only
  max_files: 1000
  excluded_extensions: [".png", ".jpg", ...]
  excluded_directories: ["node_modules", ".git", ...]

github:
  api_base_url: "https://api.github.com"
  rate_limit_delay: 1
  max_retries: 3

output:
  directory: "output"
  formats: ["markdown", "json", "html"]
```

## 📊 Generated Documentation

The analyzer generates comprehensive documentation in the `output/` directory:

- **README.md**: Complete project documentation
- **api/**: API specifications and documentation
- **uml/**: UML diagrams (PlantUML format)
- **requirements/**: Requirements analysis
- **architecture/**: Architecture documentation
- **dependencies/**: Dependency analysis
- **technology_stack.md**: Technology stack analysis

## 🧪 Example Output

For a typical Node.js/React project, the analyzer will generate:

### Technology Stack Detection
- **Frontend**: React, JavaScript, CSS
- **Backend**: Express.js, Node.js
- **Database**: MongoDB
- **Testing**: Jest, React Testing Library
- **Build Tools**: Webpack, Babel

### UML Diagrams
- Use case diagrams showing user interactions
- Class diagrams for object-oriented code
- Component diagrams showing system architecture

### API Documentation
- OpenAPI 3.0 specifications
- Endpoint documentation with parameters and responses
- Postman collection export

## 🛠️ Development

### Project Structure

```
github-codebase-analyzer/
├── src/
│   ├── main.jac                 # Main application entry
│   └── ...
├── walkers/                     # Specialized walker implementations
├── analyzers/                   # Code analysis modules
├── generators/                  # Documentation generators
├── config/                      # Configuration files
├── tests/                       # Test suite
├── output/                      # Generated documentation
├── requirements.txt             # Python dependencies
└── README.md                    # This file
```

### Adding New Analyzers

1. Create a new walker in the `analyzers/` directory
2. Implement the analysis logic following the existing patterns
3. Register the analyzer in `src/main.jac`
4. Add tests in `tests/test_analyzer.jac`

### Extending Technology Detection

Add new technology patterns to `analyzers/technology_detector.jac`:

```jac
has technology_patterns: dict = {
    "frameworks": {
        "NewFramework": [r"import.*newframework", "newframework"]
    }
};
```

## 🧪 Testing

Run the test suite:

```bash
jac run tests/test_analyzer.jac
```

The test suite covers:
- GitHub API integration
- Code structure analysis
- Dependency parsing
- Technology detection
- Documentation generation

## 📈 Performance

- **Analysis Speed**: ~1-5 minutes for typical repositories
- **File Limit**: Configurable (default: 1000 files)
- **Memory Usage**: Optimized for large repositories
- **Rate Limiting**: GitHub API rate limit aware

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch: `git checkout -b feature-name`
3. Make your changes and add tests
4. Commit your changes: `git commit -am 'Add new feature'`
5. Push to the branch: `git push origin feature-name`
6. Submit a pull request

## 📄 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## 🙏 Acknowledgments

- Jaseci team for the powerful graph-based programming framework
- GitHub API for providing comprehensive repository data
- PlantUML for UML diagram generation
- Open source community for inspiration and feedback

## 📞 Support

- **Issues**: [GitHub Issues](https://github.com/your-username/github-codebase-analyzer/issues)
- **Documentation**: [Wiki](https://github.com/your-username/github-codebase-analyzer/wiki)
- **Discussions**: [GitHub Discussions](https://github.com/your-username/github-codebase-analyzer/discussions)

---

**Built with ❤️ using Jac and Jaseci**
