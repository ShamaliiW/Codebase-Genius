"""
Dependency Analysis Walker
=========================

This walker analyzes project dependencies from various package managers
and build tools to create dependency graphs and identify technologies used.
"""

import:py from json, re, yaml, xml.etree.ElementTree;
import:py from typing;

walker DependencyAnalyzer {
    has package_managers: dict = {
        "package.json": "npm",
        "requirements.txt": "pip",
        "Pipfile": "pipenv",
        "poetry.lock": "poetry",
        "Cargo.toml": "cargo",
        "go.mod": "go",
        "pom.xml": "maven",
        "build.gradle": "gradle",
        "composer.json": "composer"
    };
    
    can analyze_dependencies with Repository entry {
        """Main entry point for dependency analysis"""
        
        print("Analyzing project dependencies...");
        
        # Get all package/dependency files
        package_files = self.get_package_files(here);
        
        for file_path, content in package_files.items() {
            if content and file_path in self.package_managers {
                manager = self.package_managers[file_path];
                dependencies = self.parse_dependencies(file_path, content, manager);
                self.create_dependency_nodes(here, dependencies, manager);
            }
        }
        
        print(f"Dependency analysis completed for {here.name}");
    }
    
    can get_package_files(repo: Repository) -> dict {
        """Get all package/dependency files from repository"""
        
        package_files = {};
        
        # Walk through file nodes to find package files
        for file_node in -->(here) {
            if hasattr(file_node, 'name') and file_node.name in self.package_managers.keys() {
                package_files[file_node.name] = file_node.content;
            }
        }
        
        return package_files;
    }
    
    can parse_dependencies(file_name: str, content: str, manager: str) -> list {
        """Parse dependencies based on package manager"""
        
        dependencies = [];
        
        try {
            if manager == "npm" {
                dependencies = self.parse_npm_dependencies(content);
            } elif manager == "pip" {
                dependencies = self.parse_pip_dependencies(content);
            } elif manager == "pipenv" {
                dependencies = self.parse_pipfile_dependencies(content);
            } elif manager == "cargo" {
                dependencies = self.parse_cargo_dependencies(content);
            } elif manager == "go" {
                dependencies = self.parse_go_dependencies(content);
            } elif manager == "maven" {
                dependencies = self.parse_maven_dependencies(content);
            } elif manager == "gradle" {
                dependencies = self.parse_gradle_dependencies(content);
            } elif manager == "composer" {
                dependencies = self.parse_composer_dependencies(content);
            }
        } except Exception as e {
            print(f"Error parsing {file_name}: {e}");
        }
        
        return dependencies;
    }
    
    can parse_npm_dependencies(content: str) -> list {
        """Parse NPM package.json dependencies"""
        
        dependencies = [];
        
        try {
            data = json.loads(content);
            
            # Production dependencies
            if "dependencies" in data {
                for name, version in data["dependencies"].items() {
                    dependencies.append({
                        "name": name,
                        "version": version,
                        "type": "npm",
                        "is_dev": False
                    });
                }
            }
            
            # Development dependencies
            if "devDependencies" in data {
                for name, version in data["devDependencies"].items() {
                    dependencies.append({
                        "name": name,
                        "version": version,
                        "type": "npm",
                        "is_dev": True
                    });
                }
            }
        } except Exception as e {
            print(f"Error parsing package.json: {e}");
        }
        
        return dependencies;
    }
    
    can parse_pip_dependencies(content: str) -> list {
        """Parse pip requirements.txt dependencies"""
        
        dependencies = [];
        lines = content.split('\n');
        
        for line in lines {
            line = line.strip();
            if line and not line.startswith('#') {
                # Handle different version specifiers
                name_version = re.split(r'[>=<~!]', line)[0].strip();
                version = line.replace(name_version, '').strip();
                
                dependencies.append({
                    "name": name_version,
                    "version": version or "*",
                    "type": "pip",
                    "is_dev": False
                });
            }
        }
        
        return dependencies;
    }
    
    can parse_pipfile_dependencies(content: str) -> list {
        """Parse Pipfile dependencies"""
        
        dependencies = [];
        
        try {
            # Simple parsing - could use toml library for better parsing
            lines = content.split('\n');
            current_section = "";
            
            for line in lines {
                line = line.strip();
                
                if line.startswith('[') and line.endswith(']') {
                    current_section = line[1:-1];
                } elif '=' in line and current_section in ['packages', 'dev-packages'] {
                    name = line.split('=')[0].strip();
                    version = line.split('=')[1].strip().replace('"', '');
                    
                    dependencies.append({
                        "name": name,
                        "version": version,
                        "type": "pipenv",
                        "is_dev": current_section == "dev-packages"
                    });
                }
            }
        } except Exception as e {
            print(f"Error parsing Pipfile: {e}");
        }
        
        return dependencies;
    }
    
    can parse_cargo_dependencies(content: str) -> list {
        """Parse Cargo.toml dependencies"""
        
        dependencies = [];
        
        try {
            # Simple TOML parsing
            lines = content.split('\n');
            in_dependencies = False;
            
            for line in lines {
                line = line.strip();
                
                if line == '[dependencies]' {
                    in_dependencies = True;
                } elif line.startswith('[') and line != '[dependencies]' {
                    in_dependencies = False;
                } elif in_dependencies and '=' in line {
                    name = line.split('=')[0].strip();
                    version = line.split('=')[1].strip().replace('"', '');
                    
                    dependencies.append({
                        "name": name,
                        "version": version,
                        "type": "cargo",
                        "is_dev": False
                    });
                }
            }
        } except Exception as e {
            print(f"Error parsing Cargo.toml: {e}");
        }
        
        return dependencies;
    }
    
    can parse_go_dependencies(content: str) -> list {
        """Parse go.mod dependencies"""
        
        dependencies = [];
        lines = content.split('\n');
        
        for line in lines {
            line = line.strip();
            if line.startswith('require') or (not line.startswith('module') and not line.startswith('go ') and ' v' in line) {
                parts = line.replace('require', '').strip().split();
                if len(parts) >= 2 {
                    name = parts[0];
                    version = parts[1];
                    
                    dependencies.append({
                        "name": name,
                        "version": version,
                        "type": "go",
                        "is_dev": False
                    });
                }
            }
        }
        
        return dependencies;
    }
    
    can parse_maven_dependencies(content: str) -> list {
        """Parse Maven pom.xml dependencies"""
        
        dependencies = [];
        
        try {
            root = xml.etree.ElementTree.fromstring(content);
            
            # Find dependencies section
            for dep in root.findall('.//{http://maven.apache.org/POM/4.0.0}dependency') {
                group_id = dep.find('.//{http://maven.apache.org/POM/4.0.0}groupId');
                artifact_id = dep.find('.//{http://maven.apache.org/POM/4.0.0}artifactId');
                version = dep.find('.//{http://maven.apache.org/POM/4.0.0}version');
                scope = dep.find('.//{http://maven.apache.org/POM/4.0.0}scope');
                
                if group_id is not None and artifact_id is not None {
                    name = f"{group_id.text}:{artifact_id.text}";
                    ver = version.text if version is not None else "unknown";
                    is_dev = scope is not None and scope.text in ["test", "provided"];
                    
                    dependencies.append({
                        "name": name,
                        "version": ver,
                        "type": "maven",
                        "is_dev": is_dev
                    });
                }
            }
        } except Exception as e {
            print(f"Error parsing pom.xml: {e}");
        }
        
        return dependencies;
    }
    
    can parse_gradle_dependencies(content: str) -> list {
        """Parse Gradle build.gradle dependencies"""
        
        dependencies = [];
        
        # Simple regex-based parsing
        dependency_pattern = r'(implementation|compile|api|testImplementation|testCompile)\s+[\'"]([^\'\"]+)[\'"]';
        matches = re.findall(dependency_pattern, content);
        
        for scope, dep_string in matches {
            parts = dep_string.split(':');
            if len(parts) >= 2 {
                name = f"{parts[0]}:{parts[1]}";
                version = parts[2] if len(parts) > 2 else "unknown";
                is_dev = "test" in scope.lower();
                
                dependencies.append({
                    "name": name,
                    "version": version,
                    "type": "gradle",
                    "is_dev": is_dev
                });
            }
        }
        
        return dependencies;
    }
    
    can parse_composer_dependencies(content: str) -> list {
        """Parse Composer composer.json dependencies"""
        
        dependencies = [];
        
        try {
            data = json.loads(content);
            
            # Production dependencies
            if "require" in data {
                for name, version in data["require"].items() {
                    dependencies.append({
                        "name": name,
                        "version": version,
                        "type": "composer",
                        "is_dev": False
                    });
                }
            }
            
            # Development dependencies
            if "require-dev" in data {
                for name, version in data["require-dev"].items() {
                    dependencies.append({
                        "name": name,
                        "version": version,
                        "type": "composer",
                        "is_dev": True
                    });
                }
            }
        } except Exception as e {
            print(f"Error parsing composer.json: {e}");
        }
        
        return dependencies;
    }
    
    can create_dependency_nodes(repo: Repository, dependencies: list, manager: str) {
        """Create dependency nodes and connect them to repository"""
        
        for dep_data in dependencies {
            dep_node = spawn Dependency(
                name=dep_data["name"],
                version=dep_data["version"],
                type=dep_data["type"],
                is_dev=dep_data["is_dev"]
            );
            
            repo ++depends_on++ dep_node;
        }
        
        print(f"Created {len(dependencies)} dependency nodes for {manager}");
    }
}
