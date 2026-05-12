"""MongoDB Atlas connection helpers.

The connection URI is read from the environment so no cluster host names
are ever committed to source control.
"""
from pymongo import MongoClient
from pymongo.database import Database, Collection
from pymongo.server_api import ServerApi


def load_mongo_client(uri: str) -> MongoClient:
    client = MongoClient(uri, server_api=ServerApi("1"))
    client.admin.command("ping")
    return client


def get_database(client: MongoClient, database_name: str) -> Database:
    return client.get_database(database_name)


def get_collection(database: Database, collection_name: str) -> Collection:
    return database.get_collection(collection_name)


def open_collection(uri: str, database_name: str,
                    collection_name: str) -> Collection:
    return get_collection(get_database(load_mongo_client(uri), database_name),
                          collection_name)
