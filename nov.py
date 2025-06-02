import pandas as pd 
import json 
import re
import unicodedata
from unidecode import unidecode
import glob
import os
from google import genai
from google.genai import types

def clean_categorys(category):
    category = category.lower()                        # tudo minúsculo
    category = unidecode(category)                     # remover acentos
    category = unicodedata.normalize('NFKC', category) # normaliza o texto Unicode

    category = re.sub(r"\s+-\s+Parcela\s+\d+/\d+", "", category, flags=re.IGNORECASE) # Remove textos como ' - Parcela X/Y'
    category = re.sub(r'\bdesconto\s+antecipacao\b', ' ', category, flags=re.IGNORECASE)
    category = re.sub(r'\bcobranca\b', ' ', category, flags=re.IGNORECASE)
    
    category = re.sub(r'[^a-zA-Z]', ' ', category)
    category = re.sub(r'\s+', ' ', category )         # Remove múltiplos espaços consecutivos e substitui por um único espaço
    
    category = category.strip() 
    return category

def classificar_descricao(descricao, categorias):
    for categoria, lista_comercios in categorias.items():
        for comercio in lista_comercios:
            if descricao == comercio: 
                return categoria
    return "outros"


class ModelGo:
    def __init__(self):
        self.client = genai.Client(api_key="AIzaSyBYoPvmaMksSDmRVvwQg3PKEdPLpRqrRso")

    def call_gemini(self,categorias,describe):
        response = self.client.models.generate_content(
            model="gemini-2.0-flash-lite",
            config=types.GenerateContentConfig(
                system_instruction=f"abaixo esta a descricao da compra e aqui estao as categorias do meu cartao de credito : {categorias} ajude a classificar o gasto dentro das categorias, retorne o nome exato da categoria"),
            contents=describe
        )
        return response.text


json_path = 'categorias.json'
with open(json_path, 'r', encoding='utf-8') as f:
    categorias = json.load(f)

card = "c6"
pasta = f"dados/2025/{card}/"
arquivos_csv = glob.glob(os.path.join(pasta, '*.csv'))
getmodel = ModelGo()

for i in range(len(arquivos_csv)):
    if card == "c6":
        df = pd.read_csv(arquivos_csv[i], sep=';', encoding='utf-8')
    else:
        df = pd.read_csv(arquivos_csv[i])
    lista_categorias = []
    for i in range(len(df)):
        if card == "c6":
            description = df["Descrição"][i]
            cat = df["Categoria"][i]
            price = df["Valor (em R$)"][i]
        else:
            description = df["title"][i]
            cat = " "
            price = df["amount"][i]
        description = clean_categorys(description)
        categoria   = classificar_descricao(description, categorias)

        if categoria == "outros":
            

            print(f"\nDescrição não classificada: {description} {price}")
            print("Categorias disponíveis : ")
            for chaves in categorias.keys():
                print(chaves)
            print(" ")

            sugestion_ia = getmodel.call_gemini(categorias,description+" "+cat)
            print(f"Sugerido pela IA : \n{sugestion_ia}")
            
            nova_categoria = input("Informe a categoria correta (ou ENTER para manter como 'outros'): ").strip().lower()

            if nova_categoria and nova_categoria != "outros":
                if nova_categoria not in categorias:
                    categorias[nova_categoria] = []  # Cria categoria nova, se necessário

                if description not in categorias[nova_categoria]:
                    categorias[nova_categoria].append(description)

                    # Salva JSON imediatamente
                    with open(json_path, 'w', encoding='utf-8') as f:
                        json.dump(categorias, f, ensure_ascii=False, indent=2)

                categoria = nova_categoria

        lista_categorias.append(categoria)


    df["categoria"] = lista_categorias
    df.to_csv("Nubank_classificado.csv", index=False)

