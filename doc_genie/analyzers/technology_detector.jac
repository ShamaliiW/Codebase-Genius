"""
Technology Detection Walker
==========================

This walker detects technologies, frameworks, and libraries used in the project
based on file extensions, imports, dependencies, and configuration files.
"""

import:py from re, json;
import:py from typing;

walker TechnologyDetector {
    has technology_patterns: dict = {
        "frameworks": {
            "React": [r"import.*react", r"from ['\"]react['\"]", "react"],
            "Angular": [r"@angular", r"ng\.", "angular"],
            "Vue": [r"import.*vue", r"from ['\"]vue['\"]", "vue"],
            "Django": [r"from django", r"import django", "django"],
            "Flask": [r"from flask", r"import flask", "flask"],
            "Express": [r"express\(\)", r"require\(['\"]express['\"]", "express"],
            "Spring Boot": [r"@SpringBootApplication", r"spring-boot", "spring"],
            "Laravel": [r"use Illuminate", r"laravel/framework", "laravel"],
            "Rails": [r"Rails\.application", r"gem ['\"]rails['\"]", "rails"],
            "ASP.NET": [r"using Microsoft\.AspNetCore", r"Microsoft.AspNetCore", "aspnet"]
        },
        "databases": {
            "MongoDB": [r"mongodb://", r"mongoose", r"pymongo", "mongodb"],
            "PostgreSQL": [r"postgresql://", r"psycopg2", r"pg", "postgresql"],
            "MySQL": [r"mysql://", r"mysql2", r"pymysql", "mysql"],
            "Redis": [r"redis://", r"redis", r"jedis", "redis"],
            "SQLite": [r"sqlite3", r"sqlite", r"better-sqlite3", "sqlite"],
            "Oracle": [r"oracle://", r"cx_Oracle", r"ojdbc", "oracle"],
            "Cassandra": [r"cassandra", r"datastax", "cassandra"]
        },
        "cloud": {
            "AWS": [r"boto3", r"aws-sdk", r"@aws-sdk", "aws"],
            "Google Cloud": [r"google-cloud", r"gcp", r"googleapis", "gcloud"],
            "Azure": [r"azure", r"@azure", r"microsoft-azure", "azure"],
            "Docker": [r"FROM ", r"COPY ", r"RUN ", "docker"],
            "Kubernetes": [r"apiVersion:", r"kind:", r"kubectl", "kubernetes"]
        },
        "testing": {
            "Jest": [r"describe\(", r"test\(", r"it\(", "jest"],
            "PyTest": [r"def test_", r"pytest", "pytest"],
            "JUnit": [r"@Test", r"junit", "junit"],
            "Mocha": [r"describe\(", r"it\(", "mocha"],
            "RSpec": [r"describe ", r"it ", "rspec"]
        },
        "build_tools": {
            "Webpack": [r"webpack", r"webpack.config", "webpack"],
            "Gradle": [r"build.gradle", r"gradle", "gradle"],
            "Maven": [r"pom.xml", r"mvn", "maven"],
            "Make": [r"Makefile", r"make ", "make"],
            "Gulp": [r"gulpfile", r"gulp", "gulp"],
            "Grunt": [r"Gruntfile", r"grunt", "grunt"]
        },
        "languages": {
            "TypeScript": [r"\.ts$", r"\.tsx$", "typescript"],
            "JavaScript": [r"\.js$", r"\.jsx$", "javascript"],
            "Python": [r"\.py$", r"#!/usr/bin/env python", "python"],
            "Java": [r"\.java$", r"public class", "java"],
            "C#": [r"\.cs$", r"using System", "csharp"],
            "Go": [r"\.go$", r"package main", "golang"],
            "Rust": [r"\.rs$", r"fn main", "rust"],
            "PHP": [r"\.php$", r"<?php", "php"],
            "Ruby": [r"\.rb$", r"#!/usr/bin/env ruby", "ruby"],
            "Swift": [r"\.swift$", r"import Foundation", "swift"]
        }
    };
    
    can detect_technologies with Repository entry {
        """Main entry point for technology detection"""
        
        print("Detecting technologies used in the project...");
        
        detected_technologies = {};
        
        # Analyze files for technology patterns
        for file_node in -->(here) {
            if hasattr(file_node, 'content') and file_node.content {
                tech_matches = self.analyze_file_content(file_node.content, file_node.path);
                for tech_name, confidence in tech_matches.items() {
                    if tech_name not in detected_technologies {
                        detected_technologies[tech_name] = confidence;
                    } else {
                        detected_technologies[tech_name] = max(detected_technologies[tech_name], confidence);
                }
            }
        }
        
        # Analyze dependencies for technology hints
        for dep_node in -->(here) {
            if hasattr(dep_node, 'name') {
                tech_matches = self.analyze_dependency(dep_node.name);
                for tech_name, confidence in tech_matches.items() {
                    if tech_name not in detected_technologies {
                        detected_technologies[tech_name] = confidence;
                    } else {
                        detected_technologies[tech_name] = max(detected_technologies[tech_name], confidence);
                }
            }
        }
        
        # Create technology nodes
        self.create_technology_nodes(here, detected_technologies);
        
        print(f"Detected {len(detected_technologies)} technologies");
    }
    
    can analyze_file_content(content: str, file_path: str) -> dict {
        """Analyze file content for technology patterns"""
        
        detected = {};
        
        for category, technologies in self.technology_patterns.items() {
            for tech_name, patterns in technologies.items() {
                confidence = 0.0;
                
                for pattern in patterns {
                    if isinstance(pattern, str) and not pattern.startswith(r"\.") {
                        # Text pattern matching
                        matches = re.findall(pattern, content, re.IGNORECASE | re.MULTILINE);
                        if matches {
                            confidence = max(confidence, min(len(matches) * 0.2, 1.0));
                    } elif pattern.startswith(r"\.") and pattern.endswith("$") {
                        # File extension pattern
                        if re.search(pattern, file_path, re.IGNORECASE) {
                            confidence = 1.0;
                    }
                }
                
                if confidence > 0.1 {  # Minimum confidence threshold
                    detected[tech_name] = confidence;
        }
        
        return detected;
    }
    
    can analyze_dependency(dependency_name: str) -> dict {
        """Analyze dependency name for technology hints"""
        
        detected = {};
        dep_lower = dependency_name.lower();
        
        for category, technologies in self.technology_patterns.items() {
            for tech_name, patterns in technologies.items() {
                for pattern in patterns {
                    if isinstance(pattern, str) and not pattern.startswith(r"\.") and not pattern.startswith(r"@") {
                        if pattern.lower() in dep_lower {
                            detected[tech_name] = 0.8;  # High confidence for dependency matches
                            break;
                    }
        }
        
        return detected;
    }
    
    can create_technology_nodes(repo: Repository, technologies: dict) {
        """Create technology nodes and connect them to repository"""
        
        for tech_name, confidence in technologies.items() {
            category = self.get_technology_category(tech_name);
            
            tech_node = spawn Technology(
                name=tech_name,
                category=category,
                version="unknown",
                confidence=confidence
            );
            
            repo ++uses++ tech_node;
        }
    }
    
    can get_technology_category(tech_name: str) -> str {
        """Get the category of a technology"""
        
        for category, technologies in self.technology_patterns.items() {
            if tech_name in technologies {
                return category;
        }
        
        return "other";
    }
    
    can generate_technology_summary(repo: Repository) -> dict {
        """Generate a summary of detected technologies"""
        
        summary = {
            "frameworks": [],
            "databases": [],
            "cloud": [],
            "testing": [],
            "build_tools": [],
            "languages": [],
            "other": []
        };
        
        for tech_node in -->(repo) {
            if hasattr(tech_node, 'category') and hasattr(tech_node, 'name') {
                category = tech_node.category;
                if category in summary {
                    summary[category].append({
                        "name": tech_node.name,
                        "confidence": tech_node.confidence
                    });
                } else {
                    summary["other"].append({
                        "name": tech_node.name,
                        "confidence": tech_node.confidence
                    });
            }
        }
        
        # Sort by confidence
        for category in summary.keys() {
            summary[category].sort(key=lambda x: x["confidence"], reverse=True);
        }
        
        return summary;
    }
}

walker APIAnalyzer {
    """Analyze API endpoints and generate OpenAPI specifications"""
    
    has api_patterns: dict = {
        "rest_endpoints": [
            r"@app\.route\(['\"]([^'\"]+)['\"].*methods=\[['\"]([^'\"]+)['\"]",  # Flask
            r"app\.get\(['\"]([^'\"]+)['\"]",  # Express.js GET
            r"app\.post\(['\"]([^'\"]+)['\"]",  # Express.js POST
            r"app\.put\(['\"]([^'\"]+)['\"]",  # Express.js PUT
            r"app\.delete\(['\"]([^'\"]+)['\"]",  # Express.js DELETE
            r"@RequestMapping\(['\"]([^'\"]+)['\"]",  # Spring Boot
            r"@GetMapping\(['\"]([^'\"]+)['\"]",  # Spring Boot GET
            r"@PostMapping\(['\"]([^'\"]+)['\"]",  # Spring Boot POST
            r"Route::get\(['\"]([^'\"]+)['\"]",  # Laravel GET
            r"Route::post\(['\"]([^'\"]+)['\"]"   # Laravel POST
        ],
        "graphql": [
            r"type\s+(\w+)\s*\{",
            r"Query\s*\{",
            r"Mutation\s*\{",
            r"@GraphQLQuery",
            r"graphql"
        ]
    };
    
    can analyze_api_endpoints with Repository entry {
        """Analyze API endpoints in the codebase"""
        
        print("Analyzing API endpoints...");
        
        endpoints = [];
        
        for file_node in -->(here) {
            if hasattr(file_node, 'content') and file_node.content {
                file_endpoints = self.extract_endpoints_from_file(file_node);
                endpoints.extend(file_endpoints);
            }
        }
        
        # Create API endpoint nodes
        for endpoint_data in endpoints {
            endpoint_node = spawn APIEndpoint(
                path=endpoint_data["path"],
                method=endpoint_data["method"],
                description=endpoint_data["description"],
                parameters=endpoint_data["parameters"],
                response_schema=endpoint_data["response_schema"]
            );
            
            here ++exposes++ endpoint_node;
        }
        
        print(f"Found {len(endpoints)} API endpoints");
    }
    
    can extract_endpoints_from_file(file_node: File) -> list {
        """Extract API endpoints from a single file"""
        
        endpoints = [];
        content = file_node.content;
        
        for pattern in self.api_patterns["rest_endpoints"] {
            matches = re.finditer(pattern, content, re.MULTILINE);
            
            for match in matches {
                path = match.group(1);
                method = self.extract_method_from_pattern(pattern, match);
                
                endpoint = {
                    "path": path,
                    "method": method,
                    "description": f"API endpoint in {file_node.name}",
                    "parameters": [],
                    "response_schema": {}
                };
                
                endpoints.append(endpoint);
            }
        }
        
        return endpoints;
    }
    
    can extract_method_from_pattern(pattern: str, match) -> str {
        """Extract HTTP method from regex pattern"""
        
        if "methods=" in pattern {
            return match.group(2) if len(match.groups()) > 1 else "GET";
        } elif ".get(" in pattern or "GetMapping" in pattern {
            return "GET";
        } elif ".post(" in pattern or "PostMapping" in pattern {
            return "POST";
        } elif ".put(" in pattern or "PutMapping" in pattern {
            return "PUT";
        } elif ".delete(" in pattern or "DeleteMapping" in pattern {
            return "DELETE";
        } else {
            return "GET";  # Default
        }
    }
}
