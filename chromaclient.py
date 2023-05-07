'''Later this will be a for a client/server mode'''
import chromadb
from chromadb.config import Settings

client = chromadb.Client(Settings(
    chroma_db_impl="duckdb+parquet",
    persist_directory="./db" # Optional, defaults to .chromadb/ in the current directory
)) 