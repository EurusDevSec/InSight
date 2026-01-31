"""
Script khởi tạo Milvus collection cho InSight RAG
Chạy: python scripts/init-milvus.py
"""

from pymilvus import (
    connections,
    Collection,
    FieldSchema,
    CollectionSchema,
    DataType,
    utility
)

# Kết nối Milvus
print("Connecting to Milvus...")
connections.connect("default", host="localhost", port="19530")

# Tên collection
COLLECTION_NAME = "medical_knowledge"

# Xóa collection cũ nếu có
if utility.has_collection(COLLECTION_NAME):
    print(f"Dropping existing collection: {COLLECTION_NAME}")
    utility.drop_collection(COLLECTION_NAME)

# Định nghĩa schema
fields = [
    FieldSchema(name="id", dtype=DataType.INT64, is_primary=True, auto_id=True),
    FieldSchema(name="content", dtype=DataType.VARCHAR, max_length=65535),
    FieldSchema(name="source", dtype=DataType.VARCHAR, max_length=255),  # 'ADA', 'MOH', etc.
    FieldSchema(name="category", dtype=DataType.VARCHAR, max_length=100),  # 'insulin_dosing', 'emergency', etc.
    FieldSchema(name="embedding", dtype=DataType.FLOAT_VECTOR, dim=384)  # all-MiniLM-L6-v2
]

schema = CollectionSchema(fields, description="Medical knowledge base for diabetes management")

# Tạo collection
print(f"Creating collection: {COLLECTION_NAME}")
collection = Collection(COLLECTION_NAME, schema)

# Tạo index cho vector search
print("Creating index...")
index_params = {
    "metric_type": "COSINE",
    "index_type": "HNSW",
    "params": {"M": 16, "efConstruction": 256}
}
collection.create_index("embedding", index_params)

# Load collection
collection.load()

print("✅ Milvus collection created successfully!")
print(f"   Collection: {COLLECTION_NAME}")
print(f"   Fields: {[f.name for f in fields]}")

# Huy Ket noi Dissconnect
connections.disconnect("default")