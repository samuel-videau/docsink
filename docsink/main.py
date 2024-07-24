import subprocess
import datetime
import os
import argparse
import replicate

from fnmatch import fnmatch
from .config import load_config, set_last_update_time, get_last_update_time, get_config_value

def parse_docsinkignore():
    ignore_patterns = []
    if os.path.exists('.docsinkignore'):
        with open('.docsinkignore', 'r') as f:
            for line in f:
                line = line.strip()
                if line and not line.startswith('#'):
                    ignore_patterns.append(line)
    return ignore_patterns

def should_ignore(file_path, ignore_patterns):
    return any(fnmatch(file_path, pattern) for pattern in ignore_patterns)

def get_recent_files_changed(since):
    ignore_patterns = parse_docsinkignore()
    
    # Get commit hashes since the last update
    commit_hashes = subprocess.check_output(['git', 'log', '--since', since.isoformat(), '--format=%H']).decode('utf-8').split()
    
    commits_with_changes = []
    for commit_hash in commit_hashes:        
        commit_message = subprocess.check_output(['git', 'log', '--format=%B', '-n', '1', commit_hash]).decode('utf-8').strip()
        commit_changes = subprocess.check_output(['git', 'show', '--pretty=format:', '--name-status', commit_hash]).decode('utf-8').strip()

        # Filter out ignored files
        filtered_changes = [line.split('\t')[-1] for line in commit_changes.split('\n') if line and not should_ignore(line.split('\t')[-1], ignore_patterns)]

        if not filtered_changes:
            continue  # Skip this commit if all changes are in ignored files
        
        # Get detailed diff for non-ignored files
        diff_command = ['git', 'show', commit_hash, '--'] + [line.split('\t')[-1] for line in filtered_changes]
        try:
            diff = subprocess.check_output(diff_command).decode('utf-8')
        except subprocess.CalledProcessError:
            print(f"Warning: Could not get diff for commit {commit_hash}. Skipping.")
            continue
        
        commits_with_changes.append(f"Message: {commit_message}\nChanges:\n{''.join(filtered_changes)}\nDiff:\n{diff}\n")
    
    # remove duplicates
    return commits_with_changes

def update_doc_with_claude(file_content, commits):

    sys_prompt = f"""
    Your role: Update documentation to reflect recent changes.

    Instructions:
    1. Maintain existing structure and custom sections.
    2. Update content only for changes within the document's scope.
    3. Output file content exclusively.
    4. Return an empty string if no changes are required.

    Guidelines:
    - Focus on relevant, impactful changes.
    - Use concise, clear language.
    - Ensure consistency with existing style.
    - Verify accuracy of updated information.
    - Remove outdated content.

    Output: Updated file content or empty string.
    """

    prompt = f"""
    --- DIF FROM LAST COMMITS ---

    {commits}

    
    --- CURRENT DOCUMENTATION CONTENT ---

    {file_content}
    """

    input = {
        "max_tokens": 16384,
        "prompt": prompt,
        "system_prompt": sys_prompt,
    }

    print(input)

    output = replicate.run(
        "meta/meta-llama-3.1-405b-instruct",
        input=input
    )

    print("output:")
    print(output)
    return "".join(output)

def read_file_content(file_path):
    try:
        with open(file_path, 'r') as file:
            return file.read()
    except FileNotFoundError:
        print(f"File not found: {file_path}")
        return ""
    except Exception as e:
        print(f"An error occurred while reading {file_path}: {e}")
        return ""

def docsink(api_key=None):
    if not api_key:
        api_key = input("Please enter your Replicate API key: ")
    os.environ["REPLICATE_API_TOKEN"] = api_key
    config = load_config()
    last_update = get_last_update_time(config)
    changes = get_recent_files_changed(last_update)

    #print("Files changed since last update:")
    #print(files_paths)


    # Read all the files and append their content
    #for file_path in files_paths:
    #    content = read_file_content(file_path)
    #    all_files_content += file_path + "\n\n" + content + "\n\n"
    
    if changes:
        docs_folder = get_config_value('docs_folder')
        os.makedirs(docs_folder, exist_ok=True)
        
        for filename in os.listdir(docs_folder):
            if filename.endswith(('.md', '.txt', '.rst')):  # Add other doc extensions if needed
                file_path = os.path.join(docs_folder, filename)
                
                with open(file_path, 'r') as f:
                    current_content = f.read()
                
                updated_content = update_doc_with_claude(current_content, '\n'.join(changes))
                
                if updated_content is None or updated_content == "":
                    print(f"Failed to update {filename}. Skipping.")
                    continue

                with open(file_path, 'w') as f:
                    f.write(updated_content)
                
                print(f"docsink: Updated {filename}")
        
        set_last_update_time(config, datetime.datetime.now())
        print("docsink: All documentation files updated successfully!")
    else:
        print("docsink: No new commits since last update. Documentation is up to date.")

def main():
    parser = argparse.ArgumentParser(description="docsink: Automated documentation updater")
    parser.add_argument("--api-key", help="Your Replicate API key")
    args = parser.parse_args()

    docsink(args.api_key)

if __name__ == "__main__":
    main()