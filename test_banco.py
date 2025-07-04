import sqlite3
import os

def teste_sqlite_basico():
    """
    Teste básico do SQLite
    """
    print("=== Teste SQLite Básico ===\n")
    
    # Nome do banco
    nome_banco = 'teste.db'
    
    try:
        # 1. Conectar/criar banco
        print("1. Conectando ao SQLite...")
        conn = sqlite3.connect(nome_banco)
        cursor = conn.cursor()
        
        # 2. Verificar versão
        cursor.execute('SELECT sqlite_version();')
        versao = cursor.fetchone()
        print(f"✅ SQLite versão: {versao[0]}")
        
        # 3. Criar uma tabela de teste
        print("\n2. Criando tabela de teste...")
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS usuarios (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                nome TEXT NOT NULL,
                email TEXT UNIQUE
            )
        ''')
        
        # 4. Inserir dados de teste
        print("\n3. Inserindo dados de teste...")
        dados_teste = [
            ('João Silva', 'joao@email.com'),
            ('Maria Santos', 'maria@email.com'),
            ('Pedro Oliveira', 'pedro@email.com')
        ]
        
        cursor.executemany(
            'INSERT OR IGNORE INTO usuarios (nome, email) VALUES (?, ?)',
            dados_teste
        )
        
        # 5. Consultar dados
        print("\n4. Consultando dados...")
        cursor.execute('SELECT * FROM usuarios')
        usuarios = cursor.fetchall()
        
        print("Usuários encontrados:")
        for usuario in usuarios:
            print(f"   ID: {usuario[0]}, Nome: {usuario[1]}, Email: {usuario[2]}")
        
        # 6. Salvar alterações
        conn.commit()
        
        # 7. Informações do arquivo
        print(f"\n5. Informações do banco:")
        print(f"   📁 Arquivo: {os.path.abspath(nome_banco)}")
        print(f"   💾 Tamanho: {os.path.getsize(nome_banco)} bytes")
        
        # 8. Fechar conexão
        conn.close()
        
        print(f"\n✅ Teste concluído com sucesso!")
        return True
        
    except sqlite3.Error as e:
        print(f"❌ Erro SQLite: {e}")
        return False
    except Exception as e:
        print(f"❌ Erro geral: {e}")
        return False

if __name__ == "__main__":
    teste_sqlite_basico()