from langchain.document_loaders import UnstructuredMarkdownLoader
from langchain.text_splitter import MarkdownHeaderTextSplitter

# Load the markdown document
#loader = UnstructuredMarkdownLoader("example.md")
#documents = loader.load()


def langchain_split_from_md_text(markdown_text) -> list:


    headers_to_split_on = [
        ("#", "Header 1"),
        ("##", "Header 2"),
        ("###", "Header 3"),
    ]

    # Initialize the splitter
    markdown_splitter = MarkdownHeaderTextSplitter(headers_to_split_on=headers_to_split_on,return_each_line=False,)

    # Use the first document's content for splitting
    split_documents = markdown_splitter.split_text(markdown_text)
    split_documents_copy = split_documents.copy()


    #print(documents)
    #print(markdown_text)
    #print(split_documents)

    # Now, `split_documents` will contain the document chunks split based on the defined headers.
    for i, doc in enumerate(split_documents_copy):
        print(f"Chunk {i+1}:")
        print(doc.page_content)
        print("Headers:", doc.metadata)
        print("-" * 40)

    return split_documents

def langchain_split_file_input(file_path):  # Replace with the actual path to your file

    try:
        with open(file_path, 'r', encoding='utf-8') as file:
            file_content = file.read()
        #print(file_content)
    except FileNotFoundError:
        print(f"Error: The file '{file_path}' was not found.")
    except Exception as e:
        print(f"An error occurred: {e}")

    # Define headers for splitting (updated to match all headers in example.md)
    headers_to_split_on = [
        ("#", "Header 1"),
        ("##", "Header 2"),
        ("###", "Header 3"),
    ]

    # Initialize the splitter
    markdown_splitter = MarkdownHeaderTextSplitter(headers_to_split_on=headers_to_split_on,return_each_line=False,)

    # Use the first document's content for splitting
    markdown_text = documents[0].page_content if documents else ""
    split_documents = markdown_splitter.split_text(file_content)
    #split_documents_copy = split_documents


    #print(documents)
    #print(markdown_text)
    #print(split_documents)

    # Now, `split_documents` will contain the document chunks split based on the defined headers.
    for i, doc in enumerate(split_documents):
        print(f"Chunk {i+1}:")
        print(doc.page_content)
        print("Headers:", doc.metadata)
        print("-" * 40)

    return split_documents