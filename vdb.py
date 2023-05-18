import pinecone

index_name = "pygatsby"
namespace  = "pygatsby"

def init(api_key):
    pinecone.init(api_key=api_key,
                  environment="us-east1-gcp")

def connect_to_index():
    return pinecone.Index(index_name)


def get_top_k(k, embedding):
    index = connect_to_index()
    return index.query(vector=embedding,
                       top_k=k,
                       data_source=namespace)

def insert_vector(id, vector):
    data = (str(id), vector)
    #print(f"inserting into pinecode, data={data}")
    index = connect_to_index()
    index.upsert(vectors=[data],
                 namespace=namespace)
