from google import genai
from google.genai import types
import json

client = genai.Client(api_key="AIzaSyBYoPvmaMksSDmRVvwQg3PKEdPLpRqrRso")

json_path = 'categorias.json'
with open(json_path, 'r', encoding='utf-8') as f:
    categorias = json.load(f)

print(len((categorias.keys())))
for chaves in categorias.keys():
    print(chaves)

# response = client.models.generate_content(
#     model="gemini-2.0-flash",
#     config=types.GenerateContentConfig(
#         system_instruction=f"leia as categorias do meu cartao de credito : {categorias} ajude a classificar o gasto, retorne o nome exato da categoria"),
#     contents="drogasil"
# )




# print(response.text)