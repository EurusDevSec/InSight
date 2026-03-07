"""Tạo Milvus collections cho InSight Knowledge Base
Chạy: python scripts/setup_milvus.py
"""

from pymilvus import (
    connections,
    Collection,
    FieldSchema,
    CollectionSchema,
    DataType,
    utility,
)

HNSW_INDEX_PARAMS = {
    "index_type": "HNSW",
    "metric_type": "COSINE",
    "params": {"M": 16, "efConstruction": 256},
}


def create_collection(name, fields, description):
    """Create a Milvus collection, dropping existing one if present."""
    if utility.has_collection(name):
        print(f"  Dropping existing collection: {name}")
        utility.drop_collection(name)

    schema = CollectionSchema(fields, description=description)
    print(f"  Creating collection: {name}")
    collection = Collection(name, schema)
    collection.create_index("embedding", HNSW_INDEX_PARAMS)
    collection.load()
    print(f"  ✅ Collection '{name}' ready!\n")
    return collection


# Connect
connections.connect("default", host="localhost", port="19530")
print("✅ Connected to Milvus\n")

# === Collection 1: Medical Knowledge ===
medical_fields = [
    FieldSchema(name="id", dtype=DataType.INT64, is_primary=True, auto_id=True),
    FieldSchema(name="text", dtype=DataType.VARCHAR, max_length=4096),
    FieldSchema(name="source", dtype=DataType.VARCHAR, max_length=256),
    FieldSchema(name="category", dtype=DataType.VARCHAR, max_length=64),
    FieldSchema(name="embedding", dtype=DataType.FLOAT_VECTOR, dim=768),
]
create_collection(
    "medical_knowledge",
    medical_fields,
    "Medical knowledge for RAG",
)

# === Collection 2: Food Embeddings ===
food_fields = [
    FieldSchema(name="id", dtype=DataType.INT64, is_primary=True, auto_id=True),
    FieldSchema(name="food_name", dtype=DataType.VARCHAR, max_length=256),
    FieldSchema(name="description", dtype=DataType.VARCHAR, max_length=1024),
    FieldSchema(name="embedding", dtype=DataType.FLOAT_VECTOR, dim=768),
]
create_collection(
    "food_embeddings",
    food_fields,
    "Food image/text embeddings",
)

print("🎉 Milvus setup complete!")
connections.disconnect("default")
