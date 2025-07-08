from github import Github
from github import Auth
from config import load_config

config = load_config()
# Replace with your GitHub personal access token
access_token = config.get('GITHUB_TOKEN')

def locate_md(org_name = "aws-samples", repo_name = "aws-genai-llm-chatbot", markdown_file_path = "README.md") -> str:

    # Replace with the name of the GitHub organization you want to scan
    org_name = org_name
    print(f"Locating Markdown file in organization: {org_name}, repository: {repo_name}, path: {markdown_file_path}")

    try:
        # Authenticate with your GitHub token
        auth = Auth.Token(access_token)
        g = Github(auth=auth)
        print("Authentication to Github has no issue")

        # Get the organization by its name
        org = g.get_organization(org_name)
        repo = g.get_repo(org_name + "/" + repo_name)
        print(f"Repo setup done: {repo_name} in organization {org_name}")

        # Get the contents of the specified markdown file
        contents = repo.get_contents(markdown_file_path)
        print("--------------------------")
        print(contents)
        print("--------------------------")
        print(type(contents))
        print("---------------------------")

        if contents:
            # If contents is a list, it's a directory; if it's a ContentFile, it's a file
            if isinstance(contents, list):
                print(f"{markdown_file_path} is a directory, not a file.")
                return ""
            else:
                # Decode the content from base64
                file_content = contents.decoded_content.decode('utf-8')
                print(type(file_content))
                print(f"File content of {markdown_file_path} in {repo_name}:\n{file_content[:500]}...")
                return file_content
        else:   
            print(f"No content found for {markdown_file_path} in {repo_name}.")
            return ""

    except Exception as e:
        print(f"An error occurred: {e}")
        return ""

def main():
    """
    Main function to locate a specific Markdown file in a GitHub repository.
    """
    org_name = "aws-samples"
    repo_name = "aws-genai-llm-chatbot"
    markdown_file_path = "docs/documentation/access-control.md"
    file_content = locate_md(org_name, repo_name, markdown_file_path)

if __name__ == "__main__":
    main()
    """    Main function to locate a specific Markdown file in a GitHub repository.
    """