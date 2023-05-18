from sentence_transformers import SentenceTransformer

model = SentenceTransformer("paraphrase-MiniLM-L6-v2")

def embed(s):
    raw_embedding = model.encode([s])[0]
    return list(map(lambda x: x.item(), raw_embedding))
