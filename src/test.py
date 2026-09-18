from sqlalchemy.exc import SQLAlchemyError

import db
import model
import repository as repos
import service

FILE_PATH = "documents/rag_overview.md"
try:
    with db.get_db() as db_session:
        doc_serv = service.DocumentService(db_session)
        doc_serv.insert_from_file(FILE_PATH, model.DocumentStatus.PENDING)

except SQLAlchemyError:
    print("error while saving!")

try:
    with db.get_db() as db_session:
        doc_repo = repos.DocumentRepository(db_session)
        docs = doc_repo.list_all()
        for doc in docs:
            print(doc.content_hash)
        # doc_repo.add()
except SQLAlchemyError:
    print("error!")
