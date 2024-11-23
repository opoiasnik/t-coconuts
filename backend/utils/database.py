from pymongo import MongoClient

client = MongoClient('mongodb://localhost:27017/')
db = client['document_validator']

def save_document(document_name, validation_results):
    db.documents.insert_one({
        "document_name": document_name,
        "validation_results": validation_results
    })

def get_validation_results(document_id):
    return db.documents.find_one({"_id": document_id})
