from openai import OpenAI
import os, yaml

with open("config.yaml", "r") as file:
    config = yaml.safe_load(file)

def openai_query(query):
    client = OpenAI(api_key=config['oai_api_key'])

    resp = client.responses.create(
        model="gpt-5",         
        temperature=1,         
        input=query,
        reasoning={ "effort": "low" },
        text={ "verbosity": "low" },
        tools=[{"type": "web_search"}]

    )
    return resp.output_text

if __name__ == '__main__':
    resp = openai_query("whats 1+1")
    print(resp)