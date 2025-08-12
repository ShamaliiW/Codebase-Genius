import from mtllm.llm {Model}

glob llm = Model(model_name="groq/llama3-8b-8192");

""" You are give a repository path {path}
    1. Locate the README.md file in the repository
    2. Read the README.md file
    3. Identify all the heading and subheading
    4. Return an outline of the README.md file
"""
def find_the_structure(path: str) -> str by llm();

node find_structure {
    can get with RepoMapper entry {
        visitor.project_skeleton = find_the_structure(visitor.path);
    }
}

walker RepoMapper {
    has path: str = "https://github.com/ShamaliiW/Langraph";
    has project_skeleton: str = "";

    can execute_report_mapping with `root entry{
        visit [-->(`?find_structure)];
    }
}

with entry {
    root ++> find_structure();
    agent = RepoMapper(path="https://github.com/ShamaliiW/Langraph") spawn root;
    agent.execute_report_mapping(here=root);
    print(agent.project_skeleton);
}
