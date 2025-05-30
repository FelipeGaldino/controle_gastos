import pandas as pd 
import json 
import re
import unicodedata
from unidecode import unidecode


def clean_categorys(category):
    category = category.lower()                        # tudo minúsculo
    category = unidecode(category)                     # remover acentos
    category = unicodedata.normalize('NFKC', category) # normaliza o texto Unicode
    category = re.sub(r"\s+-\s+Parcela\s+\d+/\d+", "", category, flags=re.IGNORECASE) # Remove textos como ' - Parcela X/Y'
    category = re.sub(r'\bdesconto\s+antecipacao\b', ' ', category, flags=re.IGNORECASE)
    category = re.sub(r'\bcobranca\b', ' ', category, flags=re.IGNORECASE)
    category = category.strip() 
    return category

def classificar_descricao(descricao, categorias):
    for categoria, lista_comercios in categorias.items():
        for comercio in lista_comercios:
            if descricao == comercio: 
                return categoria
    return "outros"

with open('categorias.json', 'r', encoding='utf-8') as f:
    categorias = json.load(f)

df = pd.read_csv("Nubank_2025-04-11.csv")

lista_categorias = []
for i in range(len(df)):
    descri = clean_categorys(df["title"][i])
    categoria = classificar_descricao(descri, categorias)
    lista_categorias.append(categoria)

df["categoria"] = lista_categorias
df.to_csv("Nubank_classificado.csv", index=False)