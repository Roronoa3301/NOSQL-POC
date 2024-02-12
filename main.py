from chains.query_builder_chain.query_builder_chain import get_mongo_query
import pymongo
import os
from dotenv import load_dotenv

load_dotenv()

my_client = pymongo.MongoClient(os.getenv("MONGO_CLIENT_URL"))
my_db = my_client[os.getenv("MONGO_DB_NAME")]
my_collection = my_db[os.getenv("MONGO_COLLECTION_NAME")]

user_input = "What restaurants serve American Cusine?"
query_builder_chain = get_mongo_query(user_input)
print("MongoDB Raw Query", query_builder_chain)

my_query = query_builder_chain
print("MongoDB Query", my_query)

result = my_collection.aggregate(my_query)
for x in result:
    print(x)
