import sqlite3
import os
from contextlib import contextmanager

class SQLiteManager:
    """
    Classe para gerenciar operações SQLite
    """
    
    def __init__(self, db_path='meu_banco.db'):
        """
        Inicializa o gerenciador SQLite
        
        Args:
            db_path (str): Caminho para o arquivo do banco de dados
        """
        self.db_path = db_path
        
    @contextmanager
    def conectar(self):
        """
        Context manager para conexões seguras
        """
        conn = None
        try:
            conn = sqlite3.connect(self.db_path)
            # Configurar para retornar resultados como dicionários
            conn.row_factory = sqlite3.Row
            yield conn
        except sqlite3.Error as e:
            if conn:
                conn.rollback()
            raise e
        finally:
            if conn:
                conn.close()
    
    def criar_banco(self):
        """
        Cria o banco de dados (arquivo será criado automaticamente)
        """
        try:
            with self.conectar() as conn:
                cursor = conn.cursor()
                
                # Executar um comando simples para criar o arquivo
                cursor.execute('SELECT sqlite_version();')
                versao = cursor.fetchone()
                
                print(f"✅ Banco SQLite criado: {self.db_path}")
                print(f"📊 Versão SQLite: {versao[0]}")
                print(f"📁 Localização: {os.path.abspath(self.db_path)}")
                
                return True
                
        except sqlite3.Error as e:
            print(f"❌ Erro ao criar banco: {e}")
            return False
    
    def verificar_banco(self):
        """
        Verifica se o banco existe e está funcionando
        """
        if not os.path.exists(self.db_path):
            print(f"❌ Banco não encontrado: {self.db_path}")
            return False
        
        try:
            with self.conectar() as conn:
                cursor = conn.cursor()
                
                # Informações básicas
                cursor.execute('SELECT sqlite_version();')
                versao = cursor.fetchone()[0]
                
                # Listar tabelas
                cursor.execute("SELECT name FROM sqlite_master WHERE type='table';")
                tabelas = cursor.fetchall()
                
                # Tamanho do arquivo
                tamanho = os.path.getsize(self.db_path)
                
                print(f"✅ Banco SQLite funcionando!")
                print(f"📊 Versão: {versao}")
                print(f"📁 Arquivo: {os.path.abspath(self.db_path)}")
                print(f"💾 Tamanho: {tamanho} bytes")
                print(f"🗂️  Tabelas: {len(tabelas)}")
                
                if tabelas:
                    print("   Tabelas existentes:")
                    for tabela in tabelas:
                        print(f"   - {tabela[0]}")
                else:
                    print("   (Nenhuma tabela criada ainda)")
                
                return True
                
        except sqlite3.Error as e:
            print(f"❌ Erro ao verificar banco: {e}")
            return False
    
    def executar_sql(self, sql, parametros=None):
        """
        Executa comando SQL
        
        Args:
            sql (str): Comando SQL
            parametros (tuple): Parâmetros para o comando
        """
        try:
            with self.conectar() as conn:
                cursor = conn.cursor()
                
                if parametros:
                    cursor.execute(sql, parametros)
                else:
                    cursor.execute(sql)
                
                # Se for SELECT, retornar resultados
                if sql.strip().upper().startswith('SELECT'):
                    return cursor.fetchall()
                
                # Para outros comandos, confirmar
                conn.commit()
                print(f"✅ SQL executado com sucesso!")
                print(f"📝 Linhas afetadas: {cursor.rowcount}")
                
                return True
                
        except sqlite3.Error as e:
            print(f"❌ Erro ao executar SQL: {e}")
            return False
    
    def listar_tabelas(self):
        """
        Lista todas as tabelas do banco
        """
        try:
            with self.conectar() as conn:
                cursor = conn.cursor()
                
                cursor.execute("""
                    SELECT name, sql 
                    FROM sqlite_master 
                    WHERE type='table' AND name NOT LIKE 'sqlite_%'
                """)
                
                tabelas = cursor.fetchall()
                
                if tabelas:
                    print(f"\n📋 Tabelas no banco ({len(tabelas)}):")
                    for i, tabela in enumerate(tabelas, 1):
                        print(f"{i:2d}. {tabela[0]}")
                else:
                    print("📋 Nenhuma tabela encontrada")
                
                return [tabela[0] for tabela in tabelas]
                
        except sqlite3.Error as e:
            print(f"❌ Erro ao listar tabelas: {e}")
            return []
    
    def deletar_banco(self):
        """
        Deleta o arquivo do banco de dados
        """
        try:
            if os.path.exists(self.db_path):
                os.remove(self.db_path)
                print(f"✅ Banco deletado: {self.db_path}")
                return True
            else:
                print(f"⚠️  Banco não existe: {self.db_path}")
                return False
                
        except Exception as e:
            print(f"❌ Erro ao deletar banco: {e}")
            return False
    
    def backup_banco(self, backup_path=None):
        """
        Cria backup do banco
        """
        if not backup_path:
            backup_path = f"{self.db_path}.backup"
        
        try:
            import shutil
            shutil.copy2(self.db_path, backup_path)
            print(f"✅ Backup criado: {backup_path}")
            return True
            
        except Exception as e:
            print(f"❌ Erro ao criar backup: {e}")
            return False

# Exemplo de uso
if __name__ == "__main__":
    print("=== Gerenciador SQLite ===\n")
    
    # Criar instância do gerenciador
    db = SQLiteManager('controle_gastos.db')
    
    print("1. Criando banco de dados...")
    if db.criar_banco():
        
        print("\n" + "="*50)
        print("\n2. Verificando banco...")
        db.verificar_banco()
        
        print("\n" + "="*50)
        print("\n3. Listando tabelas...")
        db.listar_tabelas()
        
        print("\n" + "="*50)
        print("\n🎉 SQLite configurado com sucesso!")
        print("\nPróximos passos:")
        print("- Criar tabelas para seu projeto")
        print("- Inserir dados")
        print("- Fazer consultas")
        
        print(f"\n📁 Arquivo do banco: {os.path.abspath(db.db_path)}")
    
    else:
        print("❌ Falha na configuração do SQLite")