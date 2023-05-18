def query(api_key, query):
    import openai
    #    openai.api_key = api_key  # should get this from env automatically
    #print(f"ai.query: query={query}")
    # TODO actually use the chat completion API properly
    response = openai.ChatCompletion.create(
        model="gpt-4",
        messages=[
            # {"role": "user", "content": "Hello!"}
            {"role": "user", "content": query}
        ]
    )
    return response.choices[0].message["content"]
