from sqlalchemy.exc import SQLAlchemyError

import db
import model
import repository
import service
from rag.embedding import LangChainEmbeddingProvider

FILE_PATH = "documents/chunking_strategies.md"
STORAGE_PATH = "data"

storage = db.LocalFileStorage(STORAGE_PATH)
try:
    with db.get_db() as db_session:
        doc_serv = service.DocumentService(db_session, storage)
        doc_serv.insert_from_file(FILE_PATH, model.DocumentStatus.PENDING)

except SQLAlchemyError as e:
    print(f"error while saving!: {e}")

# try:
#     with db.get_db() as db_session:
#         doc_serv = service.DocumentService(db_session, storage)
#         for doc in doc_serv.list_doc():
#             print(doc.id)
#             print(storage.read(doc.storage_path))
# except SQLAlchemyError as e:
#     print(f"error! {e}")


#### chunking test
# try:
#     with db.get_db() as db_session:
#         doc_serv = service.DocumentService(db_session, storage)
#         doc_id = doc_serv.list_doc()[0].id
#         doc_content = doc_serv.get_content(doc_id).decode("utf-8")
#         chunks = chunking.chunk_text(
#             doc_content, config.CHUNK_SIZE, config.CHUNK_OVERLAP
#         )
#         for index, chunk in enumerate(chunks):
#             print("index:", index, "\n\n", chunk.text)

# except SQLAlchemyError as e:
#     print(f"error! {e}")


### ingestion pipeline
try:
    with db.get_db() as db_session:
        # doc_serv = service.DocumentService(db_session, storage)
        # for doc in doc_serv.list_doc():
        #     doc_id = doc.id
        #     print(f"ingesting: {doc_id}")
        #     ing_pipe = service.IngestionPipeline(
        #         db_session, storage, embedding_provider
        #     )
        #     ing_pipe.process(doc_id)
        emb = LangChainEmbeddingProvider()
        chunk_repo = repository.ChunkRepository(db_session)
        chunks = chunk_repo.search_by_embedding(
            emb.embed_query("explain about Software design principles.")
        )
        for chunk in chunks:
            print(chunk.text)
            print("*" * 50)
except SQLAlchemyError as e:
    print(f"error! {e}")
