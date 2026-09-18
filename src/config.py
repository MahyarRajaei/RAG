import os

from dotenv import load_dotenv

load_dotenv()

########################################### Postgres DB #########################################
DB_USER = os.getenv("POSTGRES_USER")
DB_PASSWORD = os.getenv("POSTGRES_PASSWORD")
DB_HOST = os.getenv("POSTGRES_HOST", "localhost")
DB_PORT = os.getenv("POSTGRES_PORT")
DB_NAME = os.getenv("POSTGRES_DB")

SQLALCHEMY_DATABASE_URL = os.getenv(
    "DATABASE_URL",
    f"postgresql+psycopg2://{DB_USER}:{DB_PASSWORD}@{DB_HOST}:{DB_PORT}/{DB_NAME}",
)

########################################## Models #############################################

BASE_URL = os.getenv("NINE_ROUTER_API_BASE")
API_KEY = os.getenv("NINE_ROUTER_API_KEY")

LLM_MODEL = os.getenv("LLM_MODEL")

EMBEDDING_MODEL = os.getenv("EMBEDDING_MODEL")
EMBEDDING_DIM = int(os.getenv("EMBEDDING_DIM", "1024"))

RETRIEVAL_TYPE = os.getenv("RETRIEVAL_TYPE")
RETRIEVER_TOP_K = int(os.getenv("RETRIEVER_TOP_K"))
CHUNK_SIZE = int(os.getenv("CHUNK_SIZE"))
CHUNK_OVERLAP = int(os.getenv("CHUNK_OVERLAP"))
MIN_RELEVANCE_THRESHOLD = float(os.getenv("MIN_RELEVANCE_THRESHOLD"))
