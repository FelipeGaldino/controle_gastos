from google import genai
from google.genai import types
import json
import xml.etree.ElementTree as ET
import re

client = genai.Client(api_key="AIzaSyBYoPvmaMksSDmRVvwQg3PKEdPLpRqrRso")

json_path = 'categorias.json'
# with open(json_path, 'r', encoding='utf-8') as f:
#     categorias = json.load(f)

# print(len((categorias.keys())))
# for chaves in categorias.keys():
#     print(chaves)



# response = client.models.generate_content(
#     model="gemini-2.0-flash",
#     config=types.GenerateContentConfig(
#         system_instruction=f"leia as categorias do meu cartao de credito : {categorias} ajude a classificar o gasto, retorne o nome exato da categoria"),
#     contents="drogasil"
# )

# print(response.text)




# prompt_tarefas_3 = f"""Voce é um gestor financeiro personalizado 
# estou começando hoje dia {data} com o saldo para pagamentos a vista de R${saldo_a_vista:.2f}
# e no cartão de credito eu tenho o limite de R${saldo_credito:.2f}.

# voce primeiro deve identificar se o que o usuario mandou é entrada ou saida de dinheiro
# respondendo em xml <tipo>entrada</tipo> ou <tipo>saida</tipo> 

# se for saida de dinheiro classificar de acordo com as categorias {categorias}
# e me retornar apenas <categoria>nome_categoria</categoria> 
# e valor <valor>R$00,00</valor>
        
# se for entrada de dinheiro me retornar apenas <valor>R$00,00</valor>

# """







def go_gemini(prompt_tarefa,entrada_usuario):
    response = client.models.generate_content(
        model="gemini-2.0-flash",
        config=types.GenerateContentConfig(
            system_instruction=prompt_tarefa),
        contents=entrada_usuario)
    return response.text

def extract(texto):
    resultado = []

    # Divide o texto sempre que encontrar <tipo>
    blocos = re.split(r"(?=<tipo>)", texto, flags=re.IGNORECASE)

    for bloco in blocos:
        if not bloco.strip():
            continue

        # Detecta tipo no bloco
        tipo_match = re.search(r"<tipo>(.*?)</tipo>", bloco, re.IGNORECASE)
        tipo = tipo_match.group(1).strip().lower() if tipo_match else None

        if tipo == "saida":
            matches = re.findall(
                r"<categoria_saida>(.*?)</categoria_saida>\s*<valor>(.*?)</valor>",
                bloco,
                re.IGNORECASE | re.DOTALL
            )
            for cat, val in matches:
                resultado.append({
                    "tipo": tipo,
                    "categoria": cat.strip(),
                    "valor": val.strip()
                })

        elif tipo == "entrada":
            matches = re.findall(
                r"<categoria_entrada>(.*?)</categoria_entrada>\s*<valor>(.*?)</valor>",
                bloco,
                re.IGNORECASE | re.DOTALL
            )
            for cat, val in matches:
                resultado.append({
                    "tipo": tipo,
                    "categoria": cat.strip(),
                    "valor": val.strip()
                })

    return resultado


# CADASTRO INICIAL 
categorias_entrada = ["salario", "investimentos", "renda extra", "transferencias"]
categorias_saida = ["farmacia", "alimentacao", "transporte", "moradia", "transferencias"]
# data               = "05/01/2025"
# saldo_a_vista      = float(input("Digite o seu saldo a vista | (dinheiro que tem em todas as contas para pagar a vista) : "))
# qnt_cartao_credito = int(input("Digite a quantidade de cartoes de credito que possui : "))
# saldo_credito      = 0
# for i in range(qnt_cartao_credito):
#     saldo_credito += float(input(f"Digite o limite disponivel do cartao de credito {i+1} : "))


prompt_tarefas = f"""Voce é um gestor financeiro personalizado 
Voce deve classificar as entradas e saidas de dinheiro do usuario

voce primeiro deve identificar se o que o usuario mandou é entrada ou saida de dinheiro
respondendo em xml <tipo>entrada</tipo> ou <tipo>saida</tipo> e com alguma das categorias de 
entrada {categorias_entrada} <categoria_entrada>nome_categoria</categoria_entrada> 

se for saida de dinheiro classificar de acordo com as categorias {categorias_saida}
e me retornar apenas <categoria_saida>nome_categoria</categoria_saida> 
e valor <valor>R$00,00</valor>
        
se for entrada de dinheiro me retornar apenas <valor>R$00,00</valor>

"""



response = go_gemini(prompt_tarefas,"depositei 100 reais")
xml_extract = extract(response)
print(response)
print(xml_extract)
print("--------------------------------------------------")
response = go_gemini(prompt_tarefas,"gastei dez conto no mercado")
xml_extract = extract(response)
print(response)
print(xml_extract)
print("--------------------------------------------------")
response = go_gemini(prompt_tarefas,"comprei uma marmita de 15 ")
xml_extract = extract(response)
print(response)
print(xml_extract)
print("--------------------------------------------------")
response = go_gemini(prompt_tarefas,"vinte de uber")
xml_extract = extract(response)
print(response)
print(xml_extract)
print("--------------------------------------------------")
response = go_gemini(prompt_tarefas,"vinte de gasolina")
xml_extract = extract(response)
print(response)
print(xml_extract)
print("--------------------------------------------------")
response = go_gemini(prompt_tarefas,"5 reais na padaria")
xml_extract = extract(response)
print(response)
print(xml_extract)
print("--------------------------------------------------")
response = go_gemini(prompt_tarefas,"50 conto de luz")
xml_extract = extract(response)
print(response)
print(xml_extract)
print("--------------------------------------------------")
response = go_gemini(prompt_tarefas,"gastei dez reais no mercado e 34 de gasolina e fiz um pix de 45 reais")
xml_extract = extract(response)
print(response)
print(xml_extract)
print("--------------------------------------------------")
response = go_gemini(prompt_tarefas,"gastei 50 reais na padaria e 304 de gasolina e fiz recebi 45 reais")
xml_extract = extract(response)
print(response)
print(xml_extract)
print("--------------------------------------------------")