from elasticsearch import Elasticsearch
from datetime import datetime

# Подключение к Elasticsearch
es = Elasticsearch(
    cloud_id="08b3dd79313b4064b845f7f3bb950f55:dXMtY2VudHJhbDEuZ2NwLmNsb3VkLmVzLmlvOjQ0MyRjNjhiNTI5MjhlZDk0ZjQyYjRjYTRkM2UwNWY1NzIwZCQ1MTM0YzJmOGRhMWY0Mzg3YTZmZTNiYzczYTE5MGVmMQ==",  # Ваш Cloud ID
    basic_auth=("elastic", "EDLUByRRMXi3R4Zu5vGtO0za")  # Учетные данные
)

def save_to_elasticsearch(index, data):
    """
    Сохраняет данные в указанный индекс Elasticsearch.
    """
    try:
        response = es.index(index=index, document=data)
        return response["_id"]  # Возвращает ID документа
    except Exception as e:
        raise RuntimeError(f"Failed to index data in Elasticsearch: {e}")
def search_in_elasticsearch(index, query):
    """
    Ищет данные в указанном индексе Elasticsearch.
    """
    try:
        body = {
            "query": {
                "multi_match": {
                    "query": query,
                    "fields": ["instructions", "document_text", "analysis"]
                }
            }
        }
        response = es.search(index=index, body=body)
        return [hit["_source"] for hit in response["hits"]["hits"]]
    except Exception as e:
        raise RuntimeError(f"Failed to search data in Elasticsearch: {e}")
