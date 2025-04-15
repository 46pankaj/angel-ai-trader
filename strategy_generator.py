import openai

def generate_strategy(prompt, openai_api_key):
    openai.api_key = openai_api_key
    response = openai.ChatCompletion.create(
        model="gpt-4",
        messages=[
            {"role": "system", "content": "You're a trading strategy generator."},
            {"role": "user", "content": prompt}
        ]
    )
    return response['choices'][0]['message']['content']