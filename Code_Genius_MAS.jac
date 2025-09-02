import from byllm.llm {Model}
import os;
import subprocess;


# Global LLM
glob llm = Model(model_name="groq/meta-llama/llama-4-maverick-17b-128e-instruct");

# Repo Mapper
def clone_repo(repo_url: str, dest_dir: str = "temp_repo") -> str
    {
    project_root = os.getcwd();
    full_dest = os.path.join(project_root, dest_dir);

    os.makedirs(full_dest, exist_ok=True);

    repo_name = repo_url.rstrip("/").split("/")[-1].replace(".git", "");
    local_path = os.path.join(full_dest, repo_name);

    if os.path.exists(local_path){
        subprocess.run(["git", "-C", local_path, "pull"], check=True);
    } else{
        subprocess.run(["git", "clone", repo_url, local_path], check=True);
    }
        
    return local_path;
    }

""" You are given a repository path {path}.
    Analyze the repository and apply the ignore rules in .gitignore or similar.
    Return a list of files and folders that should be excluded. 
"""
def cleanup_fn(path: str) -> str by llm();

""" You are given a repository path {path}.
    Locate README.md, extract the main headings and subheadings. 
    Return the outline in a structured format. 
"""
def readme_outline_fn(path: str) -> str by llm();

""" You are given a repository path {path} and a list of ignored files/folders: {ignore_list}.
    Return the hierarchical file/folder structure excluding ignored items. 
"""
def repo_structure_fn(path: str, ignore_list: str) -> str by llm();

node repo_mapper_node {
    has path: str = "";
    has ignore_list: str = "";
    has readme_outline: str = "";
    has repo_structure: str = "";

    can get with RepoMapperAgent entry {
        self.ignore_list = cleanup_fn(self.path);
        self.readme_outline = readme_outline_fn(self.path);
        self.repo_structure = repo_structure_fn(self.path, self.ignore_list);

        visitor.ignore_list = self.ignore_list;
        visitor.readme_outline = self.readme_outline;
        visitor.repo_structure = self.repo_structure;
    }
}

walker RepoMapperAgent {
    has path: str = "";
    has ignore_list: str = "";
    has readme_outline: str = "";
    has repo_structure: str = "";

    can execute with entry {
        root ++> repo_mapper_node(path=self.path);
        visit [root -->];
    }
}

# Code Parser
""" You are given a repo path {path} and structure {repo_structure}.
    Collect and return the raw code content from all non-ignored source files.
"""
def code_parser_fn(path: str, repo_structure: str) -> str by llm();

node code_parser_node {
    has path: str = "";
    has repo_structure: str = "";
    has parsed_code: str = "";

    can get with CodeParserAgent entry {
        self.parsed_code = code_parser_fn(self.path, self.repo_structure);
        visitor.parsed_code = self.parsed_code;
    }
}

walker CodeParserAgent {
    has path: str = "";
    has repo_structure: str = "";
    has parsed_code: str = "";

    can execute with entry {
        root ++> code_parser_node(path=self.path, repo_structure=self.repo_structure);
        visit [root -->];
    }
}

# Doc Genie
""" You are given the parsed code {parsed_code}, 
    the README outline {readme_outline}, and repository structure {repo_structure}.
    Generate a clear, descriptive summary of what this repository does, 
    what kind of project it is, and the purpose of its code. 
"""
def doc_genie_fn(parsed_code: str, readme_outline: str, repo_structure: str) -> str by llm();

node doc_genie_node {
    has parsed_code: str = "";
    has readme_outline: str = "";
    has repo_structure: str = "";
    has repo_summary: str = "";

    can get with DocGenieAgent entry {
        self.repo_summary = doc_genie_fn(self.parsed_code, self.readme_outline, self.repo_structure);
        visitor.repo_summary = self.repo_summary;
    }
}

walker DocGenieAgent {
    has parsed_code: str = "";
    has readme_outline: str = "";
    has repo_structure: str = "";
    has repo_summary: str = "";

    can execute with entry {
        root ++> doc_genie_node(parsed_code=self.parsed_code, readme_outline=self.readme_outline, repo_structure=self.repo_structure);
        visit [root -->];
    }
}

# Supervisor Agent
walker SupervisorAgent {
    has path: str = "";
    has ignore_list: str = "";
    has readme_outline: str = "";
    has repo_structure: str = "";
    has parsed_code: str = "";
    has repo_summary: str = "";

    can analyze_repo with entry {
        # Step 1: Repo Mapping
        print("=== Running RepoMapperAgent ===");
        repo_mapper = RepoMapperAgent(path=self.path) spawn root;
        repo_mapper.execute(here=root);
        self.ignore_list = repo_mapper.ignore_list;
        self.readme_outline = repo_mapper.readme_outline;
        self.repo_structure = repo_mapper.repo_structure;

        # Step 2: Code Parsing
        print("=== Running CodeParserAgent ===");
        code_parser = CodeParserAgent(path=self.path, repo_structure=self.repo_structure) spawn root;
        code_parser.execute(here=root);
        self.parsed_code = code_parser.parsed_code;

        # Step 3: Documentation Generation
        print("=== Running DocGenieAgent ===");
        doc_genie = DocGenieAgent(parsed_code=self.parsed_code, readme_outline=self.readme_outline, repo_structure=self.repo_structure) spawn root;
        doc_genie.execute(here=root);
        self.repo_summary = doc_genie.repo_summary;

        # Final Output
        print("\n=== Repo Analysis Complete ===");
        print("Ignored Files/Folders:\n", self.ignore_list);
        print("README Outline:\n", self.readme_outline);
        print("Repo Structure:\n", self.repo_structure);
        print("Repo Summary:\n", self.repo_summary);
    }

}

# Run 
with entry {
    supervisor = SupervisorAgent(path="https://github.com/DinalieLiyanage/geveoFinal") spawn root;
    supervisor.analyze_repo(here=root);
}
