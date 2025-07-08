import os
from git_file_preprocess import git_preproc
from langchain_split import langchain_split_from_md_text
from locate_md import locate_md
from core_rag import CoreRAG
from config import load_config

#markdown_files = git_preproc(org_name="aws-samples")
#print(f"Markdown files ready for processing: {markdown_files}")

config = load_config()

def main(org_name="aws-samples"):  
    """
#    Main function to execute the GitHub Markdown file preprocessing and LangChain splitting.
#    """
    docs = []  # Initialize an empty list to store documents for vector store
    core_rag = CoreRAG(config)
    info = core_rag.get_collection_info()
    if info['document_count'] != 0:
        print(f"Clearing existing collection...")
        core_rag.vector_store.clear()
    info = core_rag.get_collection_info()
    print(f"Collection info after clearing: {info}")
    # Step 1: Preprocess GitHub Markdown files
    markdown_files = git_preproc(org_name="aws-samples")
    print(f"Markdown files ready for processing: {markdown_files}")
    if not markdown_files:
        print("No Markdown files found to process.")
        exit(1)
    else:
        print(f"gitpreproc completed successfully.")
        #print(f"Markdown files ready for processing: {markdown_files[:5]}...")  # Print first 5 files for brevity
    # Step 2: getting markdown file content for each file
    for i, file_path in enumerate(markdown_files):
        source = org_name + "/" + file_path
        print(f"Processing file {i+1}/{len(markdown_files)}: {file_path}")
        repository_name = file_path.split('/')[0] if '/' in file_path else "unknown_repo"
        print(f"Repository Name: {repository_name}")
        before,seperator,after = file_path.partition('/') if '/' in file_path else file_path
        markdown_file_path = after
        print(f"Markdown File Path: {markdown_file_path}")
        markdown_file_name = file_path.split('/')[-1] if isinstance(file_path, list) else file_path
        print(f"Markdown File Name: {markdown_file_name}")
        file_content = locate_md(org_name="aws-samples", repo_name=repository_name, markdown_file_path=markdown_file_path)
        if not file_content:
            print(f"No content found for {file_path}. Skipping to next file.")
            continue
        else:
            print(f"Content for {file_path} retrieved successfully.")
            # Print the first 500 characters of the file content for verification
            print(f"File content for {file_path}:\n{file_content[:500]}...")  # Print first 500 characters
            # Step 3: Split the Markdown files using LangChainyty
            print(f"Processing file: {file_path}")
            split_documents = langchain_split_from_md_text(file_content)
            file_to_write_tmp = markdown_file_name.replace('.md', '.txt') if markdown_file_name.endswith('.md') else markdown_file_name + ".txt"
            file_to_write = repository_name + file_to_write_tmp.replace('/', '_')  # Ensure the file name is unique and does not contain slashes
            if split_documents:
                print(f"Split documents for {file_path}:")
                for i, doc in enumerate(split_documents):
                    print(f"Chunk {i+1}: {doc.page_content[:100]}...")  # Print first 100 characters of each chunk
                    #print(doc.page_content)
                    print("Headers:", doc.metadata)
                    print(type(doc.metadata))
                    #print(f"Headers: {doc.metadata.get('headers', 'No headers found')}")
                    folder_path = "md_chunks"
                    if not os.path.exists(folder_path):
                        os.makedirs(folder_path)  # Use os.makedirs to create nested directories if needed
                    full_file_path = os.path.join(folder_path, file_to_write)
                    print(f"Writing to file: {full_file_path}")
                    try:
                        with open(full_file_path, "a", encoding="utf-8") as f:
                            # Write to file as before
                            file_doc = {
                                "text": doc.page_content,
                                "metadata": {"source": source, "org_name": org_name, "repository_name": repository_name, "markdown_file":markdown_file_path, **doc.metadata}
                            }
                            f.write(str(file_doc) + "\n\n\n")
                            # Append the actual document (or dict) to docs for vector store
                            docs.append({
                                "text": doc.page_content,
                                "metadata": {"source": source, "org_name": org_name, "repository_name": repository_name, "markdown_file":markdown_file_path, **doc.metadata}
                            })
                    except IOError as e:
                        print(f"Error creating file: {e}")
            else:
                print(f"No documents found in {file_path} after splitting.")
        # Step 4: Write the split documents to file and chromaDB
        if docs:
            print(f"Adding documents to vector store.")
            core_rag.add_documents(docs)
            print(f"Documents added successfully.")
            info = core_rag.get_collection_info()
            print(f"Collection info after adding documents: {info}")
        else:
            print(f"No documents to add.")

if __name__ == "__main__":
    main(org_name="aws-samples")
    """    Main function to execute the GitHub Markdown file preprocessing and LangChain splitting.
    """