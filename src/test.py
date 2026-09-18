from sqlalchemy.exc import SQLAlchemyError

import db
import service

FILE_PATH = "documents/chunking_strategies.md"
STORAGE_PATH = "data"

storage = db.LocalFileStorage(STORAGE_PATH)
# try:
#     with db.get_db() as db_session:
#         doc_serv = service.DocumentService(db_session, storage)
#         doc_serv.insert_from_file(FILE_PATH, model.DocumentStatus.PENDING)

# except SQLAlchemyError as e:
#     print(f"error while saving!: {e}")

try:
    with db.get_db() as db_session:
        doc_serv = service.DocumentService(db_session, storage)
        for doc in doc_serv.list_doc():
            print(doc.id)
            print(storage.read(doc.storage_path))
except SQLAlchemyError as e:
    print(f"error! {e}")
