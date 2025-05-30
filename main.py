
# Mostra resultado
# print(df)
import json
import re
import pandas as pd
from collections import defaultdict

# Função para compilar regex
def gerar_regex(nome):
    nome = re.escape(nome.strip())
    return re.compile(fr"^{nome}\b", re.IGNORECASE)

def extrair_nome_empresa(descricao):
    descricao = descricao.strip() # Remove espaços no início/fim
    descricao = descricao.lower()
    descricao = re.sub(r"\s+-\s+Parcela\s+\d+/\d+", "", descricao, flags=re.IGNORECASE) # Remove textos como ' - Parcela X/Y'
    descricao = re.sub(r"^(Desconto Antecipação|Estorno|Pagamento recebido)\s+", "", descricao, flags=re.IGNORECASE) # Remove textos como 'Desconto Antecipação ...' ou 'Estorno ...' ou 'Pagamento recebido'
    return descricao.strip()

# Função para aplicar
def categorizar(transacao):
    transacao = transacao.lower().strip()
    for categoria, regexs in categorias_regex.items():
        if any(regex.search(transacao) for regex in regexs):
            return categoria
    return "outros"

def recategorizar_outros(df, categoria_dict):
    """
    Função para recategorizar itens da categoria 'outros' interativamente
    """
    # Fazer cópia do DataFrame para não alterar o original
    df_novo = df.copy()
    categoria_dict_novo = categoria_dict.copy()
    
    # Filtrar apenas registros categorizados como 'outros'
    outros_df = df_novo[df_novo['categoria'] == 'outros'].copy()
    
    print("=== RECATEGORIZAÇÃO DE 'OUTROS' ===")
    print(f"Encontrados {len(outros_df)} registros categorizados como 'outros'\n")
    
    # Obter descrições únicas da categoria 'outros'
    descricoes_outros = outros_df['descricao'].unique()
    
    print("Descrições encontradas em 'outros':")
    for i, desc in enumerate(descricoes_outros, 1):
        count = len(outros_df[outros_df['descricao'] == desc])
        print(f"{i}. {desc} ({count} ocorrências)")
    
    print("\n" + "="*50)
    print("CATEGORIAS DISPONÍVEIS:")
    categorias_disponiveis = [cat for cat in categoria_dict_novo.keys() if cat != 'outros']
    for i, cat in enumerate(categorias_disponiveis, 1):
        print(f"{i}. {cat}")
    
    print(f"{len(categorias_disponiveis) + 1}. [CRIAR NOVA CATEGORIA]")
    print(f"{len(categorias_disponiveis) + 2}. [MANTER EM OUTROS]")
    print("="*50)
    
    # Processar cada descrição única
    for desc in descricoes_outros:
        print(f"\n📝 Recategorizando: '{desc}'")
        registros_com_desc = outros_df[outros_df['descricao'] == desc]
        print(f"   Registros encontrados: {len(registros_com_desc)}")
        
        # Mostrar alguns exemplos
        print("   Exemplos:")
        for _, row in registros_com_desc.head(3).iterrows():
            print(f"   - {row['date']} | {row['descricao']} | R$ {row['amount']}")
        
        while True:
            try:
                print(f"\nEscolha a nova categoria para '{desc}':")
                print("Opções:")
                for i, cat in enumerate(categorias_disponiveis, 1):
                    print(f"  {i}. {cat}")
                print(f"  {len(categorias_disponiveis) + 1}. [CRIAR NOVA CATEGORIA]")
                print(f"  {len(categorias_disponiveis) + 2}. [MANTER EM OUTROS]")
                
                escolha = input("Digite o número da opção: ").strip()
                
                if escolha.isdigit():
                    escolha = int(escolha)
                    
                    if 1 <= escolha <= len(categorias_disponiveis):
                        # Categoria existente escolhida
                        nova_categoria = categorias_disponiveis[escolha - 1]
                        
                        # Atualizar DataFrame
                        df_novo.loc[df_novo['descricao'] == desc, 'categoria'] = nova_categoria
                        
                        # Atualizar dicionário
                        if desc not in categoria_dict_novo[nova_categoria]:
                            categoria_dict_novo[nova_categoria].append(desc)
                        
                        # Remover de 'outros' no dicionário
                        if desc in categoria_dict_novo['outros']:
                            categoria_dict_novo['outros'].remove(desc)
                        
                        print(f"✅ '{desc}' movido para categoria '{nova_categoria}'")
                        break
                        
                    elif escolha == len(categorias_disponiveis) + 1:
                        # Criar nova categoria
                        while True:
                            nova_categoria = input("Digite o nome da nova categoria: ").strip().lower()
                            if nova_categoria and nova_categoria not in categoria_dict_novo:
                                # Atualizar DataFrame
                                df_novo.loc[df_novo['descricao'] == desc, 'categoria'] = nova_categoria
                                
                                # Criar nova categoria no dicionário
                                categoria_dict_novo[nova_categoria] = [desc]
                                categorias_disponiveis.append(nova_categoria)
                                
                                # Remover de 'outros' no dicionário
                                if desc in categoria_dict_novo['outros']:
                                    categoria_dict_novo['outros'].remove(desc)
                                
                                print(f"✅ Nova categoria '{nova_categoria}' criada com '{desc}'")
                                break
                            else:
                                print("Nome inválido ou categoria já existe. Tente novamente.")
                        break
                        
                    elif escolha == len(categorias_disponiveis) + 2:
                        # Manter em outros
                        print(f"⏭️  '{desc}' mantido em 'outros'")
                        break
                    else:
                        print("Opção inválida. Tente novamente.")
                else:
                    print("Por favor, digite um número válido.")
                    
            except (ValueError, KeyboardInterrupt):
                print("Operação cancelada ou entrada inválida.")
                break
    
    # Limpar categoria 'outros' se estiver vazia
    if not categoria_dict_novo['outros']:
        categoria_dict_novo['outros'] = []
    
    return df_novo, categoria_dict_novo

def mostrar_resumo_recategorizacao(df_original, df_novo, categoria_dict_novo):
    """
    Mostra um resumo das mudanças realizadas
    """
    print("\n" + "="*60)
    print("📊 RESUMO DA RECATEGORIZAÇÃO")
    print("="*60)
    
    # Contar registros por categoria no DataFrame novo
    contagem_nova = df_novo['categoria'].value_counts()
    
    print("Distribuição final por categoria:")
    for categoria, count in contagem_nova.items():
        print(f"  {categoria}: {count} registros")
    
    # Mostrar quantos ainda restam em 'outros'
    outros_restantes = len(df_novo[df_novo['categoria'] == 'outros'])
    print(f"\n🔍 Registros ainda em 'outros': {outros_restantes}")
    
    if outros_restantes > 0:
        print("Descrições que permaneceram em 'outros':")
        for desc in df_novo[df_novo['categoria'] == 'outros']['descricao'].unique():
            count = len(df_novo[(df_novo['categoria'] == 'outros') & (df_novo['descricao'] == desc)])
            print(f"  - {desc} ({count} ocorrências)")
    
    print("\n📋 Dicionário atualizado:")
    for categoria, descricoes in categoria_dict_novo.items():
        if descricoes:  # Só mostrar categorias que têm descrições
            print(f"  {categoria}: {descricoes}")















with open('categorias.json', 'r', encoding='utf-8') as f:
    categorias = json.load(f)

df = pd.read_csv("Nubank_2025-05-11.csv")

# Compilar todas as regex
categorias_regex = {
    categoria: [gerar_regex(nome) for nome in nomes]
    for categoria, nomes in categorias.items()
}


# Aplicação no DataFrame
df["descricao"] = df["descricao"].apply(extrair_nome_empresa)
df["categoria"] = df["descricao"].apply(categorizar)





df_novo, dict_novo = recategorizar_outros(df, categorias)

print(df_novo)

print(" ------ ")

print(dict_novo)




conta_agua = df[df['categoria'] == 'outros']

print(f"Total de registros: {len(conta_agua)}")
print(f"Soma total: R$ {conta_agua['amount'].sum():.2f}")
print(f"Valor médio: R$ {conta_agua['amount'].mean():.2f}")
print(f"Maior valor: R$ {conta_agua['amount'].max():.2f}")
print(f"Menor valor: R$ {conta_agua['amount'].min():.2f}")

print(conta_agua )
