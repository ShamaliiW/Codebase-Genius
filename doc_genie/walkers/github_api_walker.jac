"""
GitHub API Integration Walker
============================

This walker handles all GitHub API interactions for fetching repository data,
file contents, and metadata required for analysis.
"""

import:py from github, requests, base64, json, os;
import:py from typing;

walker GitHubAPIWalker {
    has api_token: str = "";
    has base_url: str = "https://api.github.com";
    has headers: dict;
    
    can init {
        # Initialize GitHub API headers
        self.api_token = os.getenv("GITHUB_TOKEN", "");
        
        if self.api_token {
            self.headers = {
                "Authorization": f"token {self.api_token}",
                "Accept": "application/vnd.github.v3+json"
            };
        } else {
            self.headers = {
                "Accept": "application/vnd.github.v3+json"
            };
            print("Warning: No GitHub token found. Rate limiting may apply.");
        }
    }
    
    can fetch_repository_info(repo_url: str) -> dict {
        """Fetch basic repository information from GitHub API"""
        
        # Extract owner and repo from URL
        parts = repo_url.replace("https://github.com/", "").split('/');
        if len(parts) < 2 {
            return {"error": "Invalid GitHub URL format"};
        }
        
        owner = parts[0];
        repo = parts[1];
        
        api_url = f"{self.base_url}/repos/{owner}/{repo}";
        
        try {
            response = requests.get(api_url, headers=self.headers);
            response.raise_for_status();
            return response.json();
        } except Exception as e {
            print(f"Error fetching repository info: {e}");
            return {"error": str(e)};
        }
    }
    
    can fetch_repository_tree(repo_url: str) -> list {
        """Fetch complete file tree of the repository"""
        
        parts = repo_url.replace("https://github.com/", "").split('/');
        owner = parts[0];
        repo = parts[1];
        
        api_url = f"{self.base_url}/repos/{owner}/{repo}/git/trees/main?recursive=1";
        
        try {
            response = requests.get(api_url, headers=self.headers);
            response.raise_for_status();
            data = response.json();
            return data.get("tree", []);
        } except Exception as e {
            print(f"Error fetching repository tree: {e}");
            return [];
        }
    }
    
    can fetch_file_content(repo_url: str, file_path: str) -> str {
        """Fetch content of a specific file"""
        
        parts = repo_url.replace("https://github.com/", "").split('/');
        owner = parts[0];
        repo = parts[1];
        
        api_url = f"{self.base_url}/repos/{owner}/{repo}/contents/{file_path}";
        
        try {
            response = requests.get(api_url, headers=self.headers);
            response.raise_for_status();
            data = response.json();
            
            if data.get("encoding") == "base64" {
                content = base64.b64decode(data["content"]).decode('utf-8');
                return content;
            }
            
            return data.get("content", "");
        } except Exception as e {
            print(f"Error fetching file {file_path}: {e}");
            return "";
        }
    }
    
    can fetch_readme(repo_url: str) -> str {
        """Fetch README content"""
        
        readme_files = ["README.md", "readme.md", "README.rst", "README.txt"];
        
        for readme_file in readme_files {
            content = self.fetch_file_content(repo_url, readme_file);
            if content {
                return content;
            }
        }
        
        return "No README file found";
    }
    
    can fetch_package_files(repo_url: str) -> dict {
        """Fetch common package/dependency files"""
        
        package_files = {
            "package.json": "",
            "requirements.txt": "",
            "Pipfile": "",
            "poetry.lock": "",
            "Cargo.toml": "",
            "go.mod": "",
            "pom.xml": "",
            "build.gradle": "",
            "composer.json": ""
        };
        
        for file_name in package_files.keys() {
            content = self.fetch_file_content(repo_url, file_name);
            if content {
                package_files[file_name] = content;
            }
        }
        
        return package_files;
    }
}

walker RepositoryDataFetcher {
    has github_walker: GitHubAPIWalker;
    
    can init {
        self.github_walker = spawn GitHubAPIWalker();
    }
    
    can populate_repository with Repository entry {
        """Populate repository node with data from GitHub API"""
        
        print(f"Fetching data for repository: {here.url}");
        
        # Fetch basic repository information
        repo_info = self.github_walker.fetch_repository_info(here.url);
        
        if "error" not in repo_info {
            here.name = repo_info.get("name", "");
            here.description = repo_info.get("description", "");
            here.language = repo_info.get("language", "");
            here.stars = repo_info.get("stargazers_count", 0);
            here.forks = repo_info.get("forks_count", 0);
            here.created_at = repo_info.get("created_at", "");
            here.updated_at = repo_info.get("updated_at", "");
            here.size = repo_info.get("size", 0);
            here.topics = repo_info.get("topics", []);
        }
        
        # Fetch README content
        here.readme_content = self.github_walker.fetch_readme(here.url);
        
        # Fetch file tree and create file nodes
        file_tree = self.github_walker.fetch_repository_tree(here.url);
        self.create_file_structure(here, file_tree);
        
        print(f"Repository data populated: {here.name}");
    }
    
    can create_file_structure(repo: Repository, tree: list) {
        """Create file and directory nodes from GitHub tree"""
        
        for item in tree {
            if item["type"] == "blob" {  # File
                file_node = spawn File(
                    path=item["path"],
                    name=item["path"].split('/')[-1],
                    extension=self.get_file_extension(item["path"]),
                    size=item["size"],
                    content="",  # Will be fetched when needed
                    language=self.detect_language(item["path"]),
                    line_count=0,
                    function_count=0,
                    class_count=0
                );
                
                repo ++contains++ file_node;
                
            } elif item["type"] == "tree" {  # Directory
                dir_node = spawn Directory(
                    path=item["path"],
                    name=item["path"].split('/')[-1],
                    file_count=0,
                    subdirectory_count=0
                );
                
                repo ++contains++ dir_node;
            }
        }
    }
    
    can get_file_extension(file_path: str) -> str {
        """Extract file extension"""
        if '.' in file_path {
            return file_path.split('.')[-1].lower();
        }
        return "";
    }
    
    can detect_language(file_path: str) -> str {
        """Detect programming language from file extension"""
        
        extension_map = {
            "py": "Python",
            "js": "JavaScript",
            "ts": "TypeScript",
            "java": "Java",
            "cpp": "C++",
            "c": "C",
            "go": "Go",
            "rs": "Rust",
            "rb": "Ruby",
            "php": "PHP",
            "cs": "C#",
            "swift": "Swift",
            "kt": "Kotlin",
            "scala": "Scala",
            "r": "R",
            "m": "Objective-C",
            "sh": "Shell",
            "sql": "SQL",
            "html": "HTML",
            "css": "CSS",
            "scss": "SCSS",
            "json": "JSON",
            "xml": "XML",
            "yaml": "YAML",
            "yml": "YAML",
            "md": "Markdown"
        };
        
        ext = self.get_file_extension(file_path);
        return extension_map.get(ext, "Unknown");
    }
}
