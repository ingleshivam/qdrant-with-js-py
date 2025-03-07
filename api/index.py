from flask import Flask,jsonify
from qdrant_client import QdrantClient, models

qdrant_url = "https://44b50d6d-d0a7-427b-be88-d25634c92006.us-east4-0.gcp.cloud.qdrant.io"
qdrant_apikey = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJhY2Nlc3MiOiJtIn0.nsoE8yGqhtjLv8J0dwSS3GTbH_Hyfvhtv3z5Q3ZCww4"
collectionName = "tenant_data"
client = QdrantClient(
    url=qdrant_url,
    api_key=qdrant_apikey
)
app = Flask(__name__)

@app.route("/api/callqdrant")
def qdrant_example():
    client.create_collection(
        collection_name=collectionName,
        shard_number=2,
        sharding_method=models.ShardingMethod.CUSTOM,
        vectors_config=models.VectorParams(size=3, distance=models.Distance.COSINE),
    )

    client.create_shard_key(collection_name=collectionName,shard_key="canada")
    client.create_shard_key(collection_name=collectionName,shard_key="germany")

    client.upsert(
        collection_name=collectionName,
        points=[
            models.PointStruct(
                id=1,
                payload={"group_id":"tenant_1"},
                vector=[0.9,0.1,0.1]
            ),
            models.PointStruct(
                id=2,
                payload={"group_id":"tenant_1"},
                vector=[0.1,0.9,0.1],
            ),
        ],
        shard_key_selector="canada"
    )

    client.upsert(
        collection_name=collectionName,
        points=[
            models.PointStruct(
                id=3,
                payload={"group_id":"tenant_2"},
                vector=[0.1,0.1,0.9],
            ),
        ],
        shard_key_selector="germany"
    )

    result = client.search(
        collection_name=collectionName,
        query_filter=models.Filter(
            must=[
                models.FieldCondition(
                    key="group_id",
                    match=models.MatchValue(
                        value="tenant_1",
                    ),
                ),
            ]
        ),
        query_vector=[0.1,0.1,0.9],
        limit=10,
    )

    result_dict = []
    for scored_point in result:
        result_dict.append({
            "id": scored_point.id,
            "score": scored_point.score,
            "payload": scored_point.payload
        })

    return jsonify(result_dict)

@app.route("/api/deletecollection")
def delete_collection():
    client.delete_collection(collectionName)
