from github import Github
from github import Auth
from config import load_config

config = load_config()
# Replace with your GitHub personal access token
access_token = config.get('GITHUB_TOKEN')

def git_preproc(org_name = "aws-samples") -> list:
    """
    Scans the specified GitHub organization for Markdown files in its repositories.
    
    Args:
        org_name (str): The name of the GitHub organization to scan.
        
    Returns:
        list: A list of Markdown file paths found in the organization's repositories.
    """
    # Replace with the name of the GitHub organization you want to scan
    org_name = "aws-samples"

    try:
        # Authenticate with your GitHub token
        auth = Auth.Token(access_token)
        g = Github(auth=auth)

        # Get the organization by its name
        org = g.get_organization(org_name)

        print(f"Scanning repositories in organization: {org.login}")

        markdown_repos = []
        markdown_files = []

        # Iterate through all repositories in the organization
        for repo in org.get_repos():  # Limit to first 5 repositories for performance
            Contents = repo.get_contents('')
            while Contents:
                content = Contents.pop(0)
                if content.type == "dir":
                    Contents.extend(repo.get_contents(content.path))
                else:
                    if content.type == "file" and content.path.endswith('.md'):
                        markdown_file = repo.name + '/' + content.path
                        markdown_repos.append(repo.name)
                        markdown_files.append(markdown_file)

    except Exception as e:
        print(f"An error occurred: {e}")

    print("Total Markdown repositories found:", len(set(markdown_repos)))
    #print(f"\n Markdown repositories found: {set(markdown_repos)}")

    print("Total Markdown files found:", len(set(markdown_files)))
    #print(f"\n Markdown files found: {set(markdown_files)}")

    ready_to_feed = []
    exclude_list = [
        "LICENSE.md", "CONTRIBUTING.md", "CODE_OF_CONDUCT.md", "CHANGELOG.md", "NOTICE.md",
        "PULL_REQUEST_TEMPLATE.md", "SUPPORT.md", "CONTRIBUTING.md", "CODE_OF_CONDUCT.md",
        "bug_report.md", "feature_request.md", "security.md", "README.rst", "README.txt",
        "README.rst", "README.txt", "CONTRIBUTING.md", "issue-template.md"
    ]
    exlcude_set = set(exclude_list)
    for file in markdown_files:
        if file.split("/")[-1] in exlcude_set:
            continue
            #print(f"Excluding file: {file}")
        else:
            #print(file)
            ready_to_feed.append(file)

    return ready_to_feed  # Return only the first 10 files for brevity

def main():
    """
    Main function to execute the GitHub Markdown file preprocessing.
    """
    markdown_files = git_preproc()
    print(f"Markdown files ready to feed: {markdown_files}")

if __name__ == "__main__":
    main()