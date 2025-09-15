from openai import OpenAI
import tiktoken

class LLMClient:
    def __init__(self, config):
        self.api_key = config.get('OPENAI_API_KEY')
        self.client = OpenAI(api_key=self.api_key)

    def truncate_prompt(prompt, model_name, max_tokens=8000):
        encoding = tiktoken.encoding_for_model(model_name)
        tokens = encoding.encode(prompt)
        if len(tokens) > max_tokens:
            tokens = tokens[:max_tokens]
            prompt = encoding.decode(tokens)
        return prompt

    def create_embedding(self, text, embedding_model, chat_model):
        try:
            response = self.client.embeddings.create(model=embedding_model, input=text)
        except Exception as e:
            print(f"Error creating embedding So Truncating some text: {e}")
            text = self.truncate_prompt(text, chat_model)
            response = self.client.embeddings.create(model=embedding_model, input=text)
        return response.data[0].embedding

    def chat(self, prompt, chat_model):
        response = self.client.chat.completions.create(
            model=chat_model,
            messages=[
                {"role": "system", "content": "You are a helpful assistant. Answer questions based on the provided context. If the context doesn't contain relevant information explain clearly."},
                {"role": "user", "content": prompt}
            ],
            temperature=0.7,
            max_tokens=500
        )
        return response.choices[0].message.content



