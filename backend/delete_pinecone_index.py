import pinecone
import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()
PINECONE_API_KEY = os.getenv("PINECONE_API_KEY")

# Initialize Pinecone
pc = pinecone.Pinecone(api_key=PINECONE_API_KEY)

# Define the index name
index_name = "research-embeddings"

# Delete the index if it exists
if index_name in pc.list_indexes().names():
    pc.delete_index(index_name)
    print(f"✅ Successfully deleted Pinecone index: {index_name}")
else:
    print(f"⚠️ Index '{index_name}' does not exist.")
