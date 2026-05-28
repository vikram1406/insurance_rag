import os
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

# ── Paths ──────────────────────────────────────────────────────────────────
BASE_DIR        = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DATA_DIR        = os.path.join(BASE_DIR, "data")
LIFE_DIR        = os.path.join(DATA_DIR, "life")
GENERAL_DIR     = os.path.join(DATA_DIR, "general")
DATABASE_DIR    = os.path.join(DATA_DIR, "database")
VECTORSTORE_DIR = os.path.join(BASE_DIR, "vectorstore_db")

# ── OpenRouter LLM settings ────────────────────────────────────────────────
OPENROUTER_API_KEY  = os.getenv("OPENROUTER_API_KEY")
OPENROUTER_BASE_URL = "https://openrouter.ai/api/v1"
LLM_MODEL           = "meta-llama/llama-3.1-8b-instruct:free"   # free model

# ── Embedding settings ─────────────────────────────────────────────────────
EMBEDDING_MODEL = "BAAI/bge-small-en-v1.5"   # free HuggingFace model

# ── Chunking settings ──────────────────────────────────────────────────────
CHUNK_SIZE    = 1000
CHUNK_OVERLAP = 200

# ── Retrieval settings ─────────────────────────────────────────────────────
TOP_K_RESULTS = 5

# ── Colours for terminal messages ─────────────────────────────────────────
class Colors:
    GREEN  = "\033[92m"
    YELLOW = "\033[93m"
    RED    = "\033[91m"
    BLUE   = "\033[94m"
    RESET  = "\033[0m"

def print_success(msg: str) -> None:
    print(f"{Colors.GREEN}✅ {msg}{Colors.RESET}")

def print_warning(msg: str) -> None:
    print(f"{Colors.YELLOW}⚠️  {msg}{Colors.RESET}")

def print_error(msg: str) -> None:
    print(f"{Colors.RED}❌ {msg}{Colors.RESET}")

def print_info(msg: str) -> None:
    print(f"{Colors.BLUE}ℹ️  {msg}{Colors.RESET}")

def check_api_key() -> bool:
    """Check that the OpenRouter API key is present."""
    if not OPENROUTER_API_KEY:
        print_error("OPENROUTER_API_KEY not found in .env file!")
        print_info("Please add:  OPENROUTER_API_KEY=your_key_here  to your .env file")
        return False
    print_success("OpenRouter API key found!")
    return True

def get_all_data_dirs() -> list[str]:
    """Return all directories that contain insurance documents."""
    return [LIFE_DIR, GENERAL_DIR, DATABASE_DIR]