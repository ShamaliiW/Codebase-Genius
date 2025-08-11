actor repo_analyzer:
    
    property repo_dir: "cloned_repo"
    
    action analyze_repo:
        
        files = ["script1.jac", "README.md", "script2.jac", "requirements.txt"]
        
        jac_files = 0
        readme_files = 0
        
        for f in files:
            if f.ends_with(".jac"):
                jac_files += 1
            if f == "README.md":
                readme_files += 1

        
        result = "Total Jac files found: " + jac_files.str() + "\n" +
                 "Total README files found: " + readme_files.str() + "\n"

        
        return result

    action save_report:
        result = analyze_repo()
        print("Saving Analysis Report:")
        print(result)

    
    save_report()
