import faiss
import numpy as np
import json
import os
import time
from datetime import datetime
import ollama  # Using Mistral-7B for embeddings

# ✅ FAISS Index Setup (1536 dimensions to match OpenAI/Mistral embeddings)
DIMENSION = 1536
index = faiss.IndexFlatL2(DIMENSION)

# ✅ Tab Metadata Storage (Store metadata separately)
TAB_STORAGE_FILE = "tab_metadata.json"

# ✅ Load existing tab metadata if it exists
if os.path.exists(TAB_STORAGE_FILE):
    with open(TAB_STORAGE_FILE, "r") as f:
        tab_metadata = json.load(f)
else:
    tab_metadata = {}

# ✅ Function to generate embeddings using local Ollama (Mistral-7B)
def generate_embedding(text):
    response = ollama.embeddings("mistral", text)
    return np.array(response["embedding"], dtype=np.float32)

# ✅ Function to add a tab to FAISS and store metadata
def add_tab(title, url):
    tab_id = str(hash(url))  # Simple hash for unique ID
    timestamp = datetime.utcnow().isoformat()

    # Generate embedding for title + URL
    embedding_vector = generate_embedding(title + " " + url)

    # Store in FAISS
    index.add(np.array([embedding_vector]))

    # Store metadata
    tab_metadata[tab_id] = {"title": title, "url": url, "timestamp": timestamp}

    # Save metadata to JSON
    with open(TAB_STORAGE_FILE, "w") as f:
        json.dump(tab_metadata, f)

    print(f"✅ Tab added: {title} - {url}")

# ✅ Function to search for similar tabs
def search_tabs(query, top_k=5):
    query_embedding = generate_embedding(query)
    distances, indices = index.search(np.array([query_embedding]), top_k)

    # Retrieve tab metadata
    results = []
    for idx in indices[0]:
        if idx < len(tab_metadata):
            tab_id = list(tab_metadata.keys())[idx]
            results.append(tab_metadata[tab_id])

    return results

# ✅ Function to delete old tabs (e.g., after 24-48 hours)
def cleanup_old_tabs(expiration_hours=48):
    now = datetime.utcnow()
    expired_tabs = [tab_id for tab_id, meta in tab_metadata.items()
                    if (now - datetime.fromisoformat(meta["timestamp"])).total_seconds() > expiration_hours * 3600]

    for tab_id in expired_tabs:
        del tab_metadata[tab_id]  # Remove from metadata
        print(f"🗑️ Deleted old tab: {tab_id}")

    # Save updated metadata
    with open(TAB_STORAGE_FILE, "w") as f:
        json.dump(tab_metadata, f)

# ✅ Example Usage
if __name__ == "__main__":
    # Add some sample tabs
    add_tab("Real Estate Market Trends", "https://example.com/real-estate-trends")
    add_tab("AI in Finance", "https://example.com/ai-finance")

    # Search for relevant tabs
    query = "real estate"
    results = search_tabs(query)
    print("\n🔍 Search Results:")
    for res in results:
        print(f"- {res['title']} ({res['url']})")

    # Run cleanup job (optional)
    cleanup_old_tabs()
