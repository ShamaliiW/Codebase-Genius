import os;
import from mtllm.llm {Model};

glob llm = Model(model_name="groq/llama3-8b-8192");


# scans the README.md and create a clean and intelligent map of the project files and folders"""
node Find_Structure {
    has path: str;

    can Find_the_Structure with RepoMapper entry {
       
    }
}

# summarizes the content under each section by section heading"""
node summarize_section {
    has 

    can summarize_section_by_section with RepoMapper entry {
        
    }
}

# Agent that runs the nodes Find_Structure and summarize_section
walker RepoMapper {}