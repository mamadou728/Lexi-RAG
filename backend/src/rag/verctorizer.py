import json
from langchain_text_splitters import RecursiveCharacterTextSplitter
from sympy import content

text_splitter = RecursiveCharacterTextSplitter(
    chunk_size=500,    # Each chunk will be approximately 1000 characters
    chunk_overlap=50,  # Overlap of 200 characters between chunks        
)

def load_and_chunk():
    try:
        with open("documents_mock.json", "r",) as f:
            data = json.load(f)
    
    except Exception as e:
        print(f"Error loading or chunking document: {e}")
        return []
    
    raw_documents = data.get("doments", [])
    print(f"Loaded {len(raw_documents)} raw chunks from JSON.")

    all_chunks = []
    for doc in raw_documents:
        source_text = doc["content"]        

        # Perform the split
        # This returns a list of string fragments
        text_fragments = text_splitter.split_text(source_text)

        for i, fragment in enumerate(text_fragments):
            chunk_object = {
                "chunk_index": i,
                "text": fragment,
                "original_doc_id": doc["_id"],
                "filename": doc["filename"],
                "matter_id": doc["matter_id"],       # Crucial for Matter filtering
                "sensitivity": doc["sensitivity"]    # Crucial for Security filtering
            }
            all_chunks.append(chunk_object)
            print(f"Generated {len(all_chunks)} chunks after splitting.")
            return all_chunks
        

# Run it
if __name__ == "__main__":  
    generated = load_and_chunk()
    if generated:
        print(f"json.dumps(generated[0], indent=2)")
        print(json.dumps(generated[0], indent=2))