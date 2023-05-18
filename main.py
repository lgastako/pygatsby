import os

from uuid import uuid4
from langchain.prompts import load_prompt

import fire
import nltk

from embeddings import embed

import ai
import tdb


# TODO ...
#nltk.download('punkt')
#print("Loading english tokenizer")
tokenizer = nltk.data.load('tokenizers/punkt/english.pickle')
#print("tokenizer loaded")

def condense_whitespace(s):
    return " ".join(s.split())

def clean_sentence(s):
    return condense_whitespace(s.strip().replace("\n", " "))

def parse_snippets(content):
    return list(map(clean_sentence, tokenizer.tokenize(content)))

def format_history(pairs):
    return "\n\n".join(map(lambda pair: f"{pair[0]}: {pair[1]}", pairs))

def format_history_with_restrictions(max_length, pairs):
    result = "<history not available>"
    for n in range(len(pairs)):
        formatted = format_history(pairs)
        if len(formatted) <= max_length:
            result = formatted
            break
        pairs = pairs[1:]  # TODO is this right or do we want -1?
    return result

def top_k_to_context_with_restrictions(max_length, top_k):
    result = "<history not available>"
    for n in range(len(top_k)):
        contextified = top_k_to_context(top_k)
        if len(contextified) <= max_length:
            result = contextified
            break
        top_k = top_k[1:]  # TODO is this right or do we want -1?
    return result

def top_k_to_context(top_k):
    return "\n\n".join(top_k)

def is_empty(xs):
    return xs is None or len(xs) == 0

def top_k_data_to_sentences(top_k_ids, top_k_data):
    return list(map(lambda id: top_k_data[id], top_k_ids))

template = load_prompt("prompts/gatsby.yaml")

def fill_prompt(query, history, context, character_name):
    return str(template.format_prompt(query=query,
                                      history=history,
                                      context=context,
                                      character_name=character_name))

def run_talk_loop(oai_api_key, session_id, character_name):
    import vdb
    while True:
        print("> ", end="")
        query = input()
        k = 10
        embedding = embed(query)
        #print(f"embedding size: {len(embedding)}")
        #print(f"embedding: {embedding}")
        top_k_ids = vdb.get_top_k(k, embedding)
        #print(f"got top k ids: {top_k_ids}")
        assert not is_empty(top_k_ids)
        fetched_history = tdb.fetch_history(session_id)
        #print(f"got history: {fetched_history}")
        top_k_data = tdb.retrieve_all(top_k_ids)
        #print(f"got top k data: {top_k_data}")
        history = format_history_with_restrictions(1500, fetched_history)
        #print(f"history: {history}")
        top_k_sentences = top_k_data_to_sentences(top_k_ids, top_k_data)
        context = top_k_to_context_with_restrictions(1500, top_k_sentences)
        #print(f"context: {context}")
        prompt = fill_prompt(query, history, context, character_name)
        #print(f"prompt: {prompt}")
        result = ai.query(oai_api_key, prompt)
        #print(f"result: {result}")
        tdb.add_history(session_id, query, result)
        print(f"{character_name}: {result}")


class CLI:
    @staticmethod
    def populate(filename):
        import vdb
        print("Populating...")
        pinecone_key = os.environ["PINECONE_API_KEY"]
        # print(f"Usng PINECONE_API_KEY: {pinecone_key}")
        vdb.init(pinecone_key)
        print("Pinecone initialized...")
        with open(filename) as f:
            content = f.read()
        snippets = parse_snippets(content)
        print("Snippets parsed...")
        for n, sentence in enumerate(snippets):
            n = n + 1
            print(f"Processing sentence #{n}")
            id_ = uuid4()
            embedding = embed(sentence)
            print(f"embedding size: {len(embedding)}")
            # print(f"embedding: {embedding}")
            tdb.insert(id_, sentence)
            # TODO batch
            vdb.insert_vector(id_, embedding)
            print(f"Inserted sentence: {sentence}")

    @staticmethod
    def talk():
        import vdb
        character_name = "Jay Gatsby"
        print("Ambient AI CHARBOT")
        print(f"Character: {character_name}")
        oai_api_key = os.environ["OPENAI_API_KEY"]
        pc_api_key  = os.environ["PINECONE_API_KEY"]
        vdb.init(pc_api_key)
        #print("Pinecone initialized.")
        session_id = uuid4()
        run_talk_loop(oai_api_key, session_id, character_name)

def main():
    fire.Fire(CLI)

if __name__ == "__main__":
    main()
