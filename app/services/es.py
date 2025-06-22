import os

from dotenv import load_dotenv
from elasticsearch import Elasticsearch

load_dotenv()

ELASTIC_CLOUD_ID = os.getenv("ELASTIC_CLOUD_ID")
ELASTIC_CLOUD_USERNAME = os.getenv("ELASTIC_CLOUD_USERNAME")
ELASTIC_CLOUD_PASSWORD = os.getenv("ELASTIC_CLOUD_PASSWORD")

es_client = Elasticsearch(
    cloud_id=ELASTIC_CLOUD_ID,
    basic_auth=(ELASTIC_CLOUD_USERNAME, ELASTIC_CLOUD_PASSWORD),
)


def get_es_client():
    return es_client
