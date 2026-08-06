import os

from dotenv import load_dotenv

load_dotenv()

EMBEDDING_MODEL_NAME = os.getenv(
    "EMBEDDING_MODEL_NAME", "paraphrase-multilingual-MiniLM-L12-v2"
)

# Default kept under EMBEDDING_MODEL_NAME's 128-token max sequence length,
# so chunks aren't silently truncated at embed time.
CHUNK_SIZE_TOKENS = int(os.getenv("CHUNK_SIZE_TOKENS", "100"))
CHUNK_OVERLAP_TOKENS = int(os.getenv("CHUNK_OVERLAP_TOKENS", "20"))
