#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
GitHub Codebase Analyzer - Pure Python Implementation
====================================================

A simplified version of the GitHub codebase analyzer that works without Jaseci,
but follows the same conceptual structure and provides the same functionality.
"""

import os
import sys

# Fix encoding issues on Windows
if sys.platform == "win32":
    os.environ["PYTHONIOENCODING"] = "utf-8"

import json
import yaml
import requests
import argparse
from pathlib import Path
from datetime import datetime
from typing import Dict, List, Optional, Any
import base64
import re
import ast

# Import PDF generator
try:
    from pdf_generator import PDFGenerator, AlternativePDFGenerator
    PDF_AVAILABLE = True
except ImportError as e:
    print(f"⚠️ PDF generation not available: {e}")
    PDF_AVAILABLE = False
    PDFGenerator = None
    AlternativePDFGenerator = None

# Try to import PlantUML for diagram generation
try:
    import plantuml
    PLANTUML_AVAILABLE = True
except ImportError:
    PLANTUML_AVAILABLE = False
    print("Info: PlantUML not available. UML diagrams will be generated as text files only.")

class Repository:
    """Repository data structure"""
    def __init__(self, url: str, name: str = "", description: str = ""):
        self.url = url
        self.name = name
        self.description = description
        self.language = ""
        self.stars = 0
        self.forks = 0
        self.created_at = ""
        self.updated_at = ""
        self.size = 0
        self.topics = []
        self.readme_content = ""
        self.files = []
        self.dependencies = []
        self.technologies = []
        self.api_endpoints = []
        self.analysis_complete = False

class File:
    """File data structure"""
    def __init__(self, path: str, name: str, extension: str, size: int, content: str = ""):
        self.path = path
        self.name = name
        self.extension = extension
        self.size = size
        self.content = content
        self.language = self._detect_language()
        self.line_count = 0
        self.function_count = 0
        self.class_count = 0
        self.complexity_score = 0.0
    
    def _detect_language(self) -> str:
        """Detect programming language from file extension"""
        extension_map = {
            "py": "Python", "js": "JavaScript", "ts": "TypeScript", "java": "Java",
            "cpp": "C++", "c": "C", "go": "Go", "rs": "Rust", "rb": "Ruby",
            "php": "PHP", "cs": "C#", "swift": "Swift", "kt": "Kotlin",
            "html": "HTML", "css": "CSS", "json": "JSON", "yaml": "YAML", "yml": "YAML"
        }
        return extension_map.get(self.extension.lower(), "Unknown")

class GitHubAPIClient:
    """GitHub API client for fetching repository data"""
    
    def __init__(self, token: Optional[str] = None):
        self.token = token or os.getenv("GITHUB_TOKEN", "")
        self.base_url = "https://api.github.com"
        self.headers = {
            "Accept": "application/vnd.github.v3+json",
            "User-Agent": "GitHub-Codebase-Analyzer",
            "Authorization": f"token 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"
        }
        
        if self.token:
            self.headers["Authorization"] = f"token {self.token}"
        else:
            print("⚠️ Warning: No GitHub token provided. Rate limiting may apply.")
    
    def fetch_repository_info(self, repo_url: str) -> Dict[str, Any]:
        """Fetch basic repository information"""
        try:
            owner, repo = self._parse_repo_url(repo_url)
            url = f"{self.base_url}/repos/{owner}/{repo}"
            
            response = requests.get(url, headers=self.headers)
            response.raise_for_status()
            
            return response.json()
        except Exception as e:
            print(f"❌ Error fetching repository info: {e}")
            return {"error": str(e)}
    
    def fetch_repository_tree(self, repo_url: str, branch: str = "main") -> List[Dict]:
        """Fetch complete file tree of the repository"""
        try:
            owner, repo = self._parse_repo_url(repo_url)
            url = f"{self.base_url}/repos/{owner}/{repo}/git/trees/{branch}?recursive=1"
            
            response = requests.get(url, headers=self.headers)
            response.raise_for_status()
            
            data = response.json()
            return data.get("tree", [])
        except Exception as e:
            print(f"❌ Error fetching repository tree: {e}")
            # Try with default branch
            if branch == "main":
                return self.fetch_repository_tree(repo_url, "master")
            return []
    
    def fetch_file_content(self, repo_url: str, file_path: str) -> str:
        """Fetch content of a specific file"""
        try:
            owner, repo = self._parse_repo_url(repo_url)
            url = f"{self.base_url}/repos/{owner}/{repo}/contents/{file_path}"
            
            response = requests.get(url, headers=self.headers)
            response.raise_for_status()
            
            data = response.json()
            if data.get("encoding") == "base64":
                content = base64.b64decode(data["content"]).decode('utf-8')
                return content
            
            return data.get("content", "")
        except Exception as e:
            print(f"❌ Error fetching file {file_path}: {e}")
            return ""
    
    def fetch_readme(self, repo_url: str) -> str:
        """Fetch README content"""
        readme_files = ["README.md", "readme.md", "README.rst", "README.txt", "README"]
        
        for readme_file in readme_files:
            content = self.fetch_file_content(repo_url, readme_file)
            if content:
                return content
        
        return "No README file found"
    
    def _parse_repo_url(self, repo_url: str) -> tuple:
        """Parse GitHub repository URL to extract owner and repo name"""
        parts = repo_url.replace("https://github.com/", "").split('/')
        if len(parts) < 2:
            raise ValueError("Invalid GitHub URL format")
        return parts[0], parts[1]

class CodeAnalyzer:
    """Analyze code structure and extract functions, classes"""
    
    def analyze_file(self, file_obj: File) -> None:
        """Analyze a single file"""
        if not file_obj.content:
            return
        
        file_obj.line_count = len(file_obj.content.split('\n'))
        
        if file_obj.language == "Python":
            self._analyze_python_code(file_obj)
        elif file_obj.language in ["JavaScript", "TypeScript"]:
            self._analyze_javascript_code(file_obj)
        else:
            self._analyze_generic_code(file_obj)
        
        file_obj.complexity_score = self._calculate_complexity(file_obj.content)
    
    def _analyze_python_code(self, file_obj: File) -> None:
        """Analyze Python code using AST"""
        try:
            tree = ast.parse(file_obj.content)
            
            functions = 0
            classes = 0
            
            for node in ast.walk(tree):
                if isinstance(node, ast.FunctionDef):
                    functions += 1
                elif isinstance(node, ast.ClassDef):
                    classes += 1
            
            file_obj.function_count = functions
            file_obj.class_count = classes
            
        except Exception as e:
            print(f"⚠️ Error analyzing Python file {file_obj.path}: {e}")
    
    def _analyze_javascript_code(self, file_obj: File) -> None:
        """Analyze JavaScript/TypeScript code using regex"""
        content = file_obj.content
        
        # Function patterns
        function_patterns = [
            r'function\s+\w+\s*\(',
            r'\w+\s*:\s*function\s*\(',
            r'\w+\s*=\s*function\s*\(',
            r'\w+\s*=\s*\([^)]*\)\s*=>',
            r'async\s+function\s+\w+\s*\('
        ]
        
        functions = 0
        for pattern in function_patterns:
            functions += len(re.findall(pattern, content, re.MULTILINE))
        
        # Class patterns
        classes = len(re.findall(r'class\s+\w+', content, re.MULTILINE))
        
        file_obj.function_count = functions
        file_obj.class_count = classes
    
    def _analyze_generic_code(self, file_obj: File) -> None:
        """Generic code analysis for unsupported languages"""
        content = file_obj.content.lower()
        
        # Simple heuristics
        function_keywords = ['function', 'def', 'func', 'sub', 'procedure', 'method']
        class_keywords = ['class', 'struct', 'interface', 'type']
        
        functions = sum(content.count(keyword) for keyword in function_keywords)
        classes = sum(content.count(keyword) for keyword in class_keywords)
        
        file_obj.function_count = functions
        file_obj.class_count = classes
    
    def _calculate_complexity(self, content: str) -> float:
        """Calculate a simple complexity score"""
        lines = content.split('\n')
        complexity = len(lines) * 0.1
        
        # Add complexity for control structures
        control_structures = ['if', 'for', 'while', 'switch', 'case', 'try', 'catch']
        for structure in control_structures:
            complexity += content.lower().count(structure) * 0.5
        
        return round(complexity, 2)

class DependencyAnalyzer:
    """Analyze project dependencies"""
    
    def __init__(self):
        self.package_managers = {
            "package.json": self._parse_npm_dependencies,
            "requirements.txt": self._parse_pip_dependencies,
            "Pipfile": self._parse_pipfile_dependencies,
            "Cargo.toml": self._parse_cargo_dependencies,
            "go.mod": self._parse_go_dependencies,
            "pom.xml": self._parse_maven_dependencies,
            "composer.json": self._parse_composer_dependencies
        }
    
    def analyze_repository(self, repo: Repository, github_client: GitHubAPIClient) -> List[Dict]:
        """Analyze dependencies in repository"""
        dependencies = []
        
        for file_name, parser in self.package_managers.items():
            content = github_client.fetch_file_content(repo.url, file_name)
            if content:
                try:
                    deps = parser(content)
                    dependencies.extend(deps)
                    print(f"✅ Found {len(deps)} dependencies in {file_name}")
                except Exception as e:
                    print(f"⚠️ Error parsing {file_name}: {e}")
        
        return dependencies
    
    def _parse_npm_dependencies(self, content: str) -> List[Dict]:
        """Parse NPM package.json dependencies"""
        dependencies = []
        data = json.loads(content)
        
        for dep_type in ["dependencies", "devDependencies"]:
            if dep_type in data:
                for name, version in data[dep_type].items():
                    dependencies.append({
                        "name": name,
                        "version": version,
                        "type": "npm",
                        "is_dev": dep_type == "devDependencies"
                    })
        
        return dependencies
    
    def _parse_pip_dependencies(self, content: str) -> List[Dict]:
        """Parse pip requirements.txt dependencies"""
        dependencies = []
        
        for line in content.split('\n'):
            line = line.strip()
            if line and not line.startswith('#'):
                name_version = re.split(r'[>=<~!]', line)[0].strip()
                version = line.replace(name_version, '').strip() or "*"
                
                dependencies.append({
                    "name": name_version,
                    "version": version,
                    "type": "pip",
                    "is_dev": False
                })
        
        return dependencies
    
    def _parse_pipfile_dependencies(self, content: str) -> List[Dict]:
        """Parse Pipfile dependencies"""
        # Simplified TOML parsing
        dependencies = []
        lines = content.split('\n')
        current_section = ""
        
        for line in lines:
            line = line.strip()
            if line.startswith('[') and line.endswith(']'):
                current_section = line[1:-1]
            elif '=' in line and current_section in ['packages', 'dev-packages']:
                name = line.split('=')[0].strip()
                version = line.split('=')[1].strip().replace('"', '')
                
                dependencies.append({
                    "name": name,
                    "version": version,
                    "type": "pipenv",
                    "is_dev": current_section == "dev-packages"
                })
        
        return dependencies
    
    def _parse_cargo_dependencies(self, content: str) -> List[Dict]:
        """Parse Cargo.toml dependencies"""
        dependencies = []
        lines = content.split('\n')
        in_dependencies = False
        
        for line in lines:
            line = line.strip()
            if line == '[dependencies]':
                in_dependencies = True
            elif line.startswith('[') and line != '[dependencies]':
                in_dependencies = False
            elif in_dependencies and '=' in line:
                name = line.split('=')[0].strip()
                version = line.split('=')[1].strip().replace('"', '')
                
                dependencies.append({
                    "name": name,
                    "version": version,
                    "type": "cargo",
                    "is_dev": False
                })
        
        return dependencies
    
    def _parse_go_dependencies(self, content: str) -> List[Dict]:
        """Parse go.mod dependencies"""
        dependencies = []
        
        for line in content.split('\n'):
            line = line.strip()
            if 'require' in line or (' v' in line and not line.startswith('module') and not line.startswith('go ')):
                parts = line.replace('require', '').strip().split()
                if len(parts) >= 2:
                    dependencies.append({
                        "name": parts[0],
                        "version": parts[1],
                        "type": "go",
                        "is_dev": False
                    })
        
        return dependencies
    
    def _parse_maven_dependencies(self, content: str) -> List[Dict]:
        """Parse Maven pom.xml dependencies (simplified)"""
        # This is a simplified version - a full implementation would use XML parsing
        dependencies = []
        
        artifact_pattern = r'<groupId>([^<]+)</groupId>\s*<artifactId>([^<]+)</artifactId>\s*<version>([^<]+)</version>'
        matches = re.findall(artifact_pattern, content, re.MULTILINE | re.DOTALL)
        
        for group_id, artifact_id, version in matches:
            dependencies.append({
                "name": f"{group_id}:{artifact_id}",
                "version": version,
                "type": "maven",
                "is_dev": False
            })
        
        return dependencies
    
    def _parse_composer_dependencies(self, content: str) -> List[Dict]:
        """Parse Composer composer.json dependencies"""
        dependencies = []
        data = json.loads(content)
        
        for dep_type in ["require", "require-dev"]:
            if dep_type in data:
                for name, version in data[dep_type].items():
                    dependencies.append({
                        "name": name,
                        "version": version,
                        "type": "composer",
                        "is_dev": dep_type == "require-dev"
                    })
        
        return dependencies

class TechnologyDetector:
    """Detect technologies, frameworks, and libraries"""
    
    def __init__(self):
        self.technology_patterns = {
            "frameworks": {
                "React": [r"import.*react", r"from ['\"]react['\"]", "react"],
                "Angular": [r"@angular", r"ng\.", "angular"],
                "Vue": [r"import.*vue", r"from ['\"]vue['\"]", "vue"],
                "Django": [r"from django", r"import django", "django"],
                "Flask": [r"from flask", r"import flask", "flask"],
                "Express": [r"express\(\)", r"require\(['\"]express['\"]", "express"],
                "Spring Boot": [r"@SpringBootApplication", r"spring-boot", "spring"],
                "Laravel": [r"use Illuminate", r"laravel/framework", "laravel"]
            },
            "databases": {
                "MongoDB": [r"mongodb://", r"mongoose", r"pymongo", "mongodb"],
                "PostgreSQL": [r"postgresql://", r"psycopg2", r"pg", "postgresql"],
                "MySQL": [r"mysql://", r"mysql2", r"pymysql", "mysql"],
                "Redis": [r"redis://", r"redis", r"jedis", "redis"],
                "SQLite": [r"sqlite3", r"sqlite", r"better-sqlite3", "sqlite"]
            },
            "testing": {
                "Jest": [r"describe\(", r"test\(", r"it\(", "jest"],
                "PyTest": [r"def test_", r"pytest", "pytest"],
                "JUnit": [r"@Test", r"junit", "junit"],
                "Mocha": [r"describe\(", r"it\(", "mocha"]
            }
        }
    
    def detect_technologies(self, repo: Repository) -> List[Dict]:
        """Detect technologies used in the repository"""
        detected = {}
        
        # Analyze file contents
        for file_obj in repo.files:
            if file_obj.content:
                tech_matches = self._analyze_file_content(file_obj.content)
                for tech_name, confidence in tech_matches.items():
                    detected[tech_name] = max(detected.get(tech_name, 0), confidence)
        
        # Analyze dependencies
        for dep in repo.dependencies:
            tech_matches = self._analyze_dependency(dep["name"])
            for tech_name, confidence in tech_matches.items():
                detected[tech_name] = max(detected.get(tech_name, 0), confidence)
        
        # Convert to list format
        technologies = []
        for tech_name, confidence in detected.items():
            if confidence > 0.1:  # Minimum confidence threshold
                technologies.append({
                    "name": tech_name,
                    "category": self._get_technology_category(tech_name),
                    "confidence": confidence
                })
        
        return technologies
    
    def _analyze_file_content(self, content: str) -> Dict[str, float]:
        """Analyze file content for technology patterns"""
        detected = {}
        
        for category, technologies in self.technology_patterns.items():
            for tech_name, patterns in technologies.items():
                confidence = 0.0
                
                for pattern in patterns:
                    if isinstance(pattern, str) and not pattern.startswith(r"\."):
                        matches = re.findall(pattern, content, re.IGNORECASE | re.MULTILINE)
                        if matches:
                            confidence = max(confidence, min(len(matches) * 0.3, 1.0))
                
                if confidence > 0:
                    detected[tech_name] = confidence
        
        return detected
    
    def _analyze_dependency(self, dependency_name: str) -> Dict[str, float]:
        """Analyze dependency name for technology hints"""
        detected = {}
        dep_lower = dependency_name.lower()
        
        for category, technologies in self.technology_patterns.items():
            for tech_name, patterns in technologies.items():
                for pattern in patterns:
                    if isinstance(pattern, str) and pattern.lower() in dep_lower:
                        detected[tech_name] = 0.8  # High confidence for dependency matches
                        break
        
        return detected
    
    def _get_technology_category(self, tech_name: str) -> str:
        """Get the category of a technology"""
        for category, technologies in self.technology_patterns.items():
            if tech_name in technologies:
                return category
        return "other"

class DocumentationGenerator:
    """Generate comprehensive documentation"""
    
    def __init__(self, output_dir: str = "output", generate_pdf: bool = True):
        self.output_dir = Path(output_dir)
        self.output_dir.mkdir(exist_ok=True)
        self.generate_pdf = generate_pdf and PDF_AVAILABLE
        
        # Initialize PDF generator if available
        if self.generate_pdf and PDF_AVAILABLE:
            try:
                self.pdf_generator = PDFGenerator(output_dir)
                # Only initialize alternative generator if WeasyPrint is available
                try:
                    self.alt_pdf_generator = AlternativePDFGenerator(output_dir)
                except Exception:
                    self.alt_pdf_generator = None
            except Exception as e:
                print(f"⚠️ Failed to initialize PDF generator: {e}")
                self.pdf_generator = None
                self.alt_pdf_generator = None
                self.generate_pdf = False
        else:
            self.pdf_generator = None
            self.alt_pdf_generator = None
    
    def generate_all_documentation(self, repo: Repository) -> None:
        """Generate all documentation types"""
        print("📝 Generating comprehensive documentation...")
        
        self._create_output_structure()
        
        # Generate different types of documentation
        self.generate_readme(repo)
        self.generate_technology_analysis(repo)
        self.generate_dependency_analysis(repo)
        self.generate_architecture_documentation(repo)
        self.generate_uml_diagrams(repo)
        self.generate_api_documentation(repo)
        
        # Generate PDF versions if enabled
        if self.generate_pdf and self.pdf_generator:
            print("📄 Generating PDF versions...")
            try:
                self.pdf_generator.generate_all_pdfs(repo.name)
            except Exception as e:
                print(f"⚠️ Primary PDF generation failed: {e}")
                if self.alt_pdf_generator:
                    try:
                        self.alt_pdf_generator.generate_all_pdfs(repo.name)
                    except Exception as e2:
                        print(f"⚠️ Alternative PDF generation also failed: {e2}")
                        print("📝 Markdown documentation still available in output directory")
                else:
                    print("📝 Markdown documentation still available in output directory")
        
        print(f"✅ Documentation generated in '{self.output_dir}' directory")
        if self.generate_pdf:
            print(f"📄 PDF versions available in '{self.output_dir}/pdf' directory")
    
    def _create_output_structure(self) -> None:
        """Create output directory structure"""
        subdirs = ["uml", "api", "analysis", "architecture", "pdf"]
        for subdir in subdirs:
            (self.output_dir / subdir).mkdir(exist_ok=True)
    
    def generate_readme(self, repo: Repository) -> None:
        """Generate comprehensive README.md"""
        
        # Calculate metrics
        total_files = len([f for f in repo.files if f.extension not in ['png', 'jpg', 'gif', 'ico']])
        total_loc = sum(f.line_count for f in repo.files)
        total_functions = sum(f.function_count for f in repo.files)
        total_classes = sum(f.class_count for f in repo.files)
        
        # Get top technologies
        top_techs = sorted(repo.technologies, key=lambda x: x["confidence"], reverse=True)[:5]
        tech_list = "\n".join([f"- **{tech['name']}** ({tech['category']})" for tech in top_techs])
        
        # Get primary language info
        primary_lang = repo.language or "Multiple"
        
        readme_content = f"""# {repo.name}

{repo.description}

## 📊 Project Overview

- **Primary Language:** {primary_lang}
- **Repository Size:** {repo.size} KB
- **Stars:** {repo.stars}
- **Forks:** {repo.forks}
- **Last Updated:** {repo.updated_at}

## 🚀 Technologies Used

{tech_list or "Analysis in progress..."}

See [Technology Analysis](./analysis/technology_analysis.md) for detailed information.

## 📋 Requirements

### System Requirements
- {primary_lang} runtime environment
- Package managers as specified in dependency files

### Dependencies
- **Total Dependencies:** {len(repo.dependencies)}
- **Production:** {len([d for d in repo.dependencies if not d.get('is_dev', False)])}
- **Development:** {len([d for d in repo.dependencies if d.get('is_dev', False)])}

See [Dependency Analysis](./analysis/dependency_analysis.md) for detailed information.

## 🛠️ Setup Instructions

### Prerequisites
```bash
# Install {primary_lang} runtime
# Install package managers
```

### Installation
```bash
# Clone the repository
git clone {repo.url}
cd {repo.name}

# Install dependencies (adjust based on project type)
# npm install        # for Node.js projects
# pip install -r requirements.txt  # for Python projects
# cargo build        # for Rust projects
```

### Running the Application
```bash
# Start the application (adjust based on project type)
# npm start          # for Node.js projects
# python main.py     # for Python projects
# cargo run          # for Rust projects
```

## 📈 Code Metrics

- **Total Files:** {total_files}
- **Total Lines of Code:** {total_loc:,}
- **Functions:** {total_functions}
- **Classes:** {total_classes}

## 🏛️ Architecture

This project follows a modular architecture. See [Architecture Documentation](./architecture/architecture_analysis.md) for detailed information.

### UML Diagrams
- [Use Case Diagram](./uml/use_case_diagram.puml)
- [Class Diagram](./uml/class_diagram.puml)
- [Component Diagram](./uml/component_diagram.puml)

## 📚 API Documentation

See [API Documentation](./api/api_specification.md) for endpoint information.

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Submit a pull request

## 📄 License

See LICENSE file for details.

---

*Analysis generated on {datetime.now().strftime("%Y-%m-%d %H:%M:%S")} by GitHub Codebase Analyzer*
"""
        
        self._write_file("README.md", readme_content)
        print("✅ README.md generated")
    
    def generate_technology_analysis(self, repo: Repository) -> None:
        """Generate technology stack analysis"""
        
        # Group technologies by category
        tech_by_category = {}
        for tech in repo.technologies:
            category = tech["category"]
            if category not in tech_by_category:
                tech_by_category[category] = []
            tech_by_category[category].append(tech)
        
        content = f"""# Technology Stack Analysis

## Overview

This document provides a comprehensive analysis of the technologies, frameworks, and libraries used in {repo.name}.

## Detected Technologies

"""
        
        for category, techs in tech_by_category.items():
            content += f"\n### {category.title()}\n\n"
            for tech in sorted(techs, key=lambda x: x["confidence"], reverse=True):
                confidence_bar = "🟢" if tech["confidence"] > 0.7 else "🟡" if tech["confidence"] > 0.4 else "🔴"
                content += f"- **{tech['name']}** {confidence_bar} (Confidence: {tech['confidence']:.2f})\n"
        
        content += f"""

## Technology Distribution

Total technologies detected: {len(repo.technologies)}

"""
        
        for category, techs in tech_by_category.items():
            content += f"- **{category.title()}:** {len(techs)} technologies\n"
        
        content += f"""

## Recommendations

Based on the detected technology stack:

1. **Primary Stack:** The project appears to use {repo.language or 'multiple languages'}
2. **Development Environment:** Ensure all detected technologies are properly configured
3. **Dependencies:** Review the dependency analysis for security and updates

---

*Generated on {datetime.now().strftime("%Y-%m-%d %H:%M:%S")}*
"""
        
        self._write_file("analysis/technology_analysis.md", content)
        print("✅ Technology analysis generated")
    
    def generate_dependency_analysis(self, repo: Repository) -> None:
        """Generate dependency analysis documentation"""
        
        # Group dependencies by type
        deps_by_type = {}
        for dep in repo.dependencies:
            dep_type = dep["type"]
            if dep_type not in deps_by_type:
                deps_by_type[dep_type] = {"prod": [], "dev": []}
            
            if dep.get("is_dev", False):
                deps_by_type[dep_type]["dev"].append(dep)
            else:
                deps_by_type[dep_type]["prod"].append(dep)
        
        content = f"""# Dependency Analysis

## Overview

This document provides a comprehensive analysis of the project dependencies for {repo.name}.

## Summary

- **Total Dependencies:** {len(repo.dependencies)}
- **Production Dependencies:** {len([d for d in repo.dependencies if not d.get('is_dev', False)])}
- **Development Dependencies:** {len([d for d in repo.dependencies if d.get('is_dev', False)])}

## Dependencies by Package Manager

"""
        
        for pkg_type, deps in deps_by_type.items():
            content += f"\n### {pkg_type.upper()}\n\n"
            
            if deps["prod"]:
                content += "#### Production Dependencies\n\n"
                for dep in sorted(deps["prod"], key=lambda x: x["name"]):
                    content += f"- **{dep['name']}** `{dep['version']}`\n"
            
            if deps["dev"]:
                content += "\n#### Development Dependencies\n\n"
                for dep in sorted(deps["dev"], key=lambda x: x["name"]):
                    content += f"- **{dep['name']}** `{dep['version']}`\n"
        
        content += """

## Security Considerations

1. **Regular Updates:** Keep dependencies up to date to avoid security vulnerabilities
2. **Vulnerability Scanning:** Use tools like `npm audit`, `safety`, or `cargo audit`
3. **License Compliance:** Review licenses of all dependencies

## Recommendations

1. **Dependency Management:** Use lock files to ensure consistent builds
2. **Minimal Dependencies:** Remove unused dependencies to reduce attack surface
3. **Version Pinning:** Consider pinning critical dependencies to specific versions

---

*Generated on """ + datetime.now().strftime("%Y-%m-%d %H:%M:%S") + "*"
        
        self._write_file("analysis/dependency_analysis.md", content)
        print("✅ Dependency analysis generated")
    
    def generate_architecture_documentation(self, repo: Repository) -> None:
        """Generate architecture documentation"""
        
        # Analyze file structure for architecture patterns
        directories = set()
        for file_obj in repo.files:
            if '/' in file_obj.path:
                directories.add(file_obj.path.split('/')[0])
        
        content = f"""# Architecture Documentation

## Overview

This document provides an architectural analysis of {repo.name}.

## Project Structure

The project follows a structured approach with the following main directories:

"""
        
        for directory in sorted(directories):
            files_in_dir = [f for f in repo.files if f.path.startswith(directory + "/")]
            content += f"- **{directory}/**: {len(files_in_dir)} files\n"
        
        content += f"""

## Language Distribution

"""
        
        # Analyze language distribution
        lang_stats = {}
        for file_obj in repo.files:
            lang = file_obj.language
            if lang not in lang_stats:
                lang_stats[lang] = {"files": 0, "lines": 0}
            lang_stats[lang]["files"] += 1
            lang_stats[lang]["lines"] += file_obj.line_count
        
        for lang, stats in sorted(lang_stats.items(), key=lambda x: x[1]["lines"], reverse=True):
            content += f"- **{lang}**: {stats['files']} files, {stats['lines']:,} lines\n"
        
        content += """

## Architectural Patterns

Based on the codebase analysis, the following patterns are observed:

1. **Modular Structure**: Code is organized into logical modules
2. **Separation of Concerns**: Different functionalities are separated
3. **Scalable Design**: Structure supports future growth

## Key Components

The main components of the system include:

"""
        
        # Identify key files
        key_files = [f for f in repo.files if any(keyword in f.name.lower() 
                    for keyword in ['main', 'app', 'server', 'client', 'api', 'config'])]
        
        for file_obj in key_files[:10]:  # Top 10 key files
            content += f"- **{file_obj.name}**: {file_obj.language} ({file_obj.line_count} lines)\n"
        
        content += """

## Data Flow

1. **Input Processing**: Data enters through defined interfaces
2. **Business Logic**: Core functionality processes the data
3. **Output Generation**: Results are formatted and returned

## Scalability Considerations

1. **Modular Design**: Components can be scaled independently
2. **Technology Stack**: Selected technologies support horizontal scaling
3. **Performance**: Code structure allows for optimization

---

*Generated on """ + datetime.now().strftime("%Y-%m-%d %H:%M:%S") + "*"
        
        self._write_file("architecture/architecture_analysis.md", content)
        print("✅ Architecture documentation generated")
    
    def generate_uml_diagrams(self, repo: Repository) -> None:
        """Generate UML diagrams in PlantUML format and convert to JPG images"""
        
        # Use Case Diagram
        use_case_uml = f"""@startuml
title Use Case Diagram - {repo.name}

actor User
actor Developer
actor System

rectangle "{repo.name}" {{
  usecase "Core Functionality" as UC1
  usecase "Data Processing" as UC2
  usecase "User Interface" as UC3
  usecase "API Access" as UC4
}}

User --> UC1
User --> UC3
Developer --> UC4
System --> UC2

UC1 --> UC2
UC3 --> UC1
UC4 --> UC2

@enduml"""
        
        # Class Diagram
        class_uml = f"""@startuml
title Class Diagram - {repo.name}

"""
        
        # Add some classes based on detected files
        python_files = [f for f in repo.files if f.language == "Python" and f.class_count > 0]
        for file_obj in python_files[:5]:  # Top 5 files with classes
            class_name = file_obj.name.replace('.py', '').title()
            class_uml += f"""class {class_name} {{
  +method1()
  +method2()
}}

"""
        
        class_uml += "@enduml"
        
        # Component Diagram
        component_uml = f"""@startuml
title Component Diagram - {repo.name}

"""
        
        # Add components based on directories
        directories = set()
        for file_obj in repo.files:
            if '/' in file_obj.path:
                directories.add(file_obj.path.split('/')[0])
        
        for directory in sorted(directories)[:5]:  # Top 5 directories
            component_uml += f'component "{directory}" as {directory}\n'
        
        # Add some relationships
        dir_list = list(sorted(directories)[:5])
        for i in range(len(dir_list) - 1):
            component_uml += f"{dir_list[i]} --> {dir_list[i+1]}\n"
        
        component_uml += "\n@enduml"
        
        # Write UML files (PlantUML text format)
        self._write_file("uml/use_case_diagram.puml", use_case_uml)
        self._write_file("uml/class_diagram.puml", class_uml)
        self._write_file("uml/component_diagram.puml", component_uml)
        
        # Always try to generate JPG images using online server
        print("📡 Generating JPG images from PlantUML...")
        self._generate_uml_images(use_case_uml, "use_case_diagram.jpg")
        self._generate_uml_images(class_uml, "class_diagram.jpg")
        self._generate_uml_images(component_uml, "component_diagram.jpg")
        print("✅ UML diagrams generated (PlantUML text + JPG images)")
        
    def _generate_uml_images(self, uml_content: str, filename: str) -> None:
        """Generate JPG image from PlantUML content using online server"""
        try:
            import base64
            import zlib
            
            def encode_plantuml(plantuml_text):
                """Encode PlantUML text for URL transmission"""
                # Remove @startuml and @enduml if present
                plantuml_text = plantuml_text.strip()
                if plantuml_text.startswith('@startuml'):
                    lines = plantuml_text.split('\n')
                    lines = lines[1:-1]  # Remove first and last line
                    plantuml_text = '\n'.join(lines)
                
                # Compress and encode
                compressed = zlib.compress(plantuml_text.encode('utf-8'))
                
                # Custom base64 encoding for PlantUML
                alphabet = '0123456789ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz-_'
                
                def encode_base64(data):
                    result = ''
                    for i in range(0, len(data), 3):
                        chunk = data[i:i+3]
                        while len(chunk) < 3:
                            chunk += b'\x00'
                        
                        b1, b2, b3 = chunk[0], chunk[1], chunk[2]
                        
                        result += alphabet[(b1 >> 2) & 0x3F]
                        result += alphabet[((b1 & 0x3) << 4) | ((b2 >> 4) & 0xF)]
                        result += alphabet[((b2 & 0xF) << 2) | ((b3 >> 6) & 0x3)]
                        result += alphabet[b3 & 0x3F]
                    
                    return result
                
                return encode_base64(compressed)
            
            # Encode for URL
            encoded = encode_plantuml(uml_content)
            
            # Try PlantUML server
            url = f"http://www.plantuml.com/plantuml/jpg/{encoded}"
            response = requests.get(url, timeout=15)
            
            if response.status_code == 200:
                # Save JPG file
                img_path = self.output_dir / "uml" / filename
                with open(img_path, 'wb') as f:
                    f.write(response.content)
                
                print(f"✅ Generated {filename}")
            else:
                print(f"⚠️ Failed to generate {filename}: Server returned {response.status_code}")
            
        except Exception as e:
            print(f"⚠️ Failed to generate {filename}: {e}")
            print(f"   PlantUML text saved as {filename.replace('.jpg', '.puml')}")
    
    def generate_api_documentation(self, repo: Repository) -> None:
        """Generate API documentation"""
        
        # Simple API endpoint detection
        api_files = []
        for file_obj in repo.files:
            if any(keyword in file_obj.content.lower() for keyword in 
                  ['@app.route', 'app.get', 'app.post', '@requestmapping', 'route::']):
                api_files.append(file_obj)
        
        content = f"""# API Documentation

## Overview

This document provides API documentation for {repo.name}.

"""
        
        if api_files:
            content += f"""## API Endpoints

Based on code analysis, the following API patterns were detected:

"""
            for file_obj in api_files:
                content += f"### {file_obj.name}\n\n"
                content += f"- **File**: `{file_obj.path}`\n"
                content += f"- **Language**: {file_obj.language}\n"
                content += f"- **Lines**: {file_obj.line_count}\n\n"
        else:
            content += """## API Analysis

No clear API endpoints were detected in the codebase. This could mean:

1. The project doesn't expose APIs
2. APIs are dynamically generated
3. API definitions are in configuration files

"""
        
        content += """## OpenAPI Specification

```yaml
openapi: 3.0.0
info:
  title: """ + repo.name + """ API
  version: 1.0.0
  description: """ + (repo.description or "API for " + repo.name) + """
servers:
  - url: http://localhost:3000
    description: Development server
paths:
  # API paths would be defined here based on detected endpoints
```

## Usage Examples

```bash
# Example API calls would be provided here
curl -X GET "http://localhost:3000/api/endpoint"
```

---

*Generated on """ + datetime.now().strftime("%Y-%m-%d %H:%M:%S") + "*"
        
        self._write_file("api/api_specification.md", content)
        print("✅ API documentation generated")
    
    def _write_file(self, filename: str, content: str) -> None:
        """Write content to file"""
        file_path = self.output_dir / filename
        file_path.parent.mkdir(parents=True, exist_ok=True)
        
        try:
            with open(file_path, 'w', encoding='utf-8') as f:
                f.write(content)
        except Exception as e:
            print(f"❌ Error writing {filename}: {e}")

class GitHubCodebaseAnalyzer:
    """Main analyzer class that orchestrates the analysis process"""
    
    def __init__(self, github_token: Optional[str] = None, output_dir: str = "output", generate_pdf: bool = True):
        self.github_client = GitHubAPIClient(github_token)
        self.code_analyzer = CodeAnalyzer()
        self.dependency_analyzer = DependencyAnalyzer()
        self.technology_detector = TechnologyDetector()
        self.doc_generator = DocumentationGenerator(output_dir, generate_pdf)
    
    def analyze_repository(self, repo_url: str) -> Repository:
        """Analyze a GitHub repository comprehensively"""
        
        print(f"🔍 Starting analysis of: {repo_url}")
        
        # Create repository object
        repo = Repository(repo_url)
        
        # Step 1: Fetch basic repository information
        print("📡 Fetching repository information...")
        repo_info = self.github_client.fetch_repository_info(repo_url)
        
        if "error" not in repo_info:
            repo.name = repo_info.get("name", "")
            repo.description = repo_info.get("description", "")
            repo.language = repo_info.get("language", "")
            repo.stars = repo_info.get("stargazers_count", 0)
            repo.forks = repo_info.get("forks_count", 0)
            repo.created_at = repo_info.get("created_at", "")
            repo.updated_at = repo_info.get("updated_at", "")
            repo.size = repo_info.get("size", 0)
            repo.topics = repo_info.get("topics", [])
            
            print(f"✅ Repository: {repo.name} ({repo.language})")
        else:
            print(f"❌ Failed to fetch repository info: {repo_info['error']}")
            return repo
        
        # Step 2: Fetch README
        print("📖 Fetching README...")
        repo.readme_content = self.github_client.fetch_readme(repo_url)
        
        # Step 2.5: Fetch .gitignore and build ignore patterns
        gitignore_content = self.github_client.fetch_file_content(repo_url, ".gitignore")
        ignore_patterns = set()
        if gitignore_content:
            for line in gitignore_content.splitlines():
                line = line.strip()
                if line and not line.startswith('#'):
                    ignore_patterns.add(line)

        # Step 3: Fetch file tree
        print("🗂️ Fetching file structure...")
        file_tree = self.github_client.fetch_repository_tree(repo_url)

        if not file_tree:
            print("❌ Failed to fetch file tree")
            return repo

        # Step 4: Process files (limit to reasonable number)
        print(f"📁 Processing {len(file_tree)} files...")

        # Filter files to analyze
        excluded_extensions = {'.png', '.jpg', '.jpeg', '.gif', '.ico', '.svg', 
                             '.pdf', '.zip', '.tar', '.gz', '.exe', '.bin'}

        files_to_analyze = []
        for item in file_tree:
            if item["type"] == "blob":  # File
                file_path = item["path"]
                file_name = file_path.split('/')[-1]
                extension = Path(file_name).suffix.lower()

                # Check .gitignore patterns
                ignored = False
                for pattern in ignore_patterns:
                    # Simple pattern matching: directory, extension, filename
                    if pattern.endswith('/') and file_path.startswith(pattern.rstrip('/')):
                        ignored = True
                        break
                    elif pattern.startswith('*.') and file_name.endswith(pattern.lstrip('*')):
                        ignored = True
                        break
                    elif pattern == file_name or pattern == file_path:
                        ignored = True
                        break
                # Skip large files, binary files, and ignored files
                if not ignored and item["size"] < 100000 and extension not in excluded_extensions:  # Max 100KB
                    files_to_analyze.append(item)

        # Limit number of files to analyze
        max_files = 50  # Reasonable limit for analysis
        if len(files_to_analyze) > max_files:
            print(f"⚠️ Limiting analysis to {max_files} files (out of {len(files_to_analyze)})")
            files_to_analyze = files_to_analyze[:max_files]

        # Analyze files
        for i, item in enumerate(files_to_analyze):
            file_path = item["path"]
            file_name = file_path.split('/')[-1]
            extension = Path(file_name).suffix.lower().lstrip('.')

            print(f"📄 Analyzing file {i+1}/{len(files_to_analyze)}: {file_name}")

            # Create file object
            file_obj = File(
                path=file_path,
                name=file_name,
                extension=extension,
                size=item["size"],
                content=""
            )

            # Fetch content for text files
            if file_obj.language != "Unknown" or extension in {'txt', 'md', 'yml', 'yaml', 'json', 'xml'}:
                content = self.github_client.fetch_file_content(repo_url, file_path)
                file_obj.content = content

                # Analyze code structure
                if content:
                    self.code_analyzer.analyze_file(file_obj)

            repo.files.append(file_obj)

        # Step 5: Analyze dependencies
        print("📦 Analyzing dependencies...")
        repo.dependencies = self.dependency_analyzer.analyze_repository(repo, self.github_client)

        # Step 6: Detect technologies
        print("🔍 Detecting technologies...")
        repo.technologies = self.technology_detector.detect_technologies(repo)

        print(f"✅ Detected {len(repo.technologies)} technologies")

        # Step 7: Generate documentation
        print("📝 Generating documentation...")
        self.doc_generator.generate_all_documentation(repo)

        repo.analysis_complete = True
        print("🎉 Analysis completed successfully!")

        return repo

def main():
    """Main function"""
    parser = argparse.ArgumentParser(description='GitHub Codebase Analyzer')
    parser.add_argument('--url', help='GitHub repository URL to analyze')
    parser.add_argument('--token', help='GitHub API token')
    parser.add_argument('--output', default='output', help='Output directory')
    parser.add_argument('--no-pdf', action='store_true', help='Skip PDF generation')
    
    args = parser.parse_args()
    
    if not args.url:
        print("GitHub Codebase Analyzer")
        print("========================")
        print("Usage: python analyzer.py --url <github_repo_url>")
        print("")
        print("Options:")
        print("  --url     GitHub repository URL to analyze")
        print("  --token   GitHub API token (optional)")
        print("  --output  Output directory (default: output)")
        print("  --no-pdf  Skip PDF generation (default: generate PDFs)")
        print("")
        print("Example:")
        print("  python analyzer.py --url https://github.com/owner/repo")
        print("  python analyzer.py --url https://github.com/owner/repo --no-pdf")
        return 0
    
    print("GitHub Codebase Analyzer")
    print("========================")
    
    # Parse GitHub URL
    try:
        parts = args.url.replace('https://github.com/', '').split('/')
        owner, repo = parts[0], parts[1]
        repo_url = args.url  # Use the full URL
    except (IndexError, ValueError):
        print("Error: Invalid GitHub URL. Use format: https://github.com/owner/repo")
        return 1
    
    try:
        # Analyze the repository
        generate_pdf = not args.no_pdf  # Generate PDF unless --no-pdf is specified
        analyzer = GitHubCodebaseAnalyzer(
            args.token, 
            output_dir=args.output,
            generate_pdf=generate_pdf
        )
        
        result_repo = analyzer.analyze_repository(repo_url)
        
        if result_repo and hasattr(result_repo, 'analysis_complete') and result_repo.analysis_complete:
            output_note = "PDFs and markdown files" if generate_pdf else "markdown files"
            print(f"\n✅ Analysis completed! Check the '{args.output}' directory for {output_note}.")
            print(f"📊 Summary:")
            print(f"   - Files analyzed: {len(result_repo.files) if result_repo.files else 0}")
            print(f"   - Dependencies found: {len(result_repo.dependencies) if result_repo.dependencies else 0}")
            print(f"   - Technologies detected: {len(result_repo.technologies) if result_repo.technologies else 0}")
            return 0
        else:
            print("\n❌ Analysis failed!")
            return 1
    
    except Exception as e:
        print(f"\n❌ Error during analysis: {e}")
        return 1
    
    return 0

if __name__ == "__main__":
    sys.exit(main())
