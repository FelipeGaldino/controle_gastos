import sqlite3
import os
from datetime import datetime

class GerenciadorUsuario:
    """
    Classe para gerenciar a tabela de usuários
    """
    
    def __init__(self, db_path='controle_gastos.db'):
        self.db_path = db_path
    
    def conectar(self):
        """Conecta ao banco SQLite"""
        return sqlite3.connect(self.db_path)
    
    def criar_tabela_usuario(self):
        """
        Cria a tabela usuario com a estrutura especificada
        """
        try:
            conn = self.conectar()
            cursor = conn.cursor()
            
            # Criar tabela usuario
            sql_criar_tabela = '''
                CREATE TABLE IF NOT EXISTS usuario (
                    id_usuario INTEGER PRIMARY KEY AUTOINCREMENT,
                    nome TEXT NOT NULL,
                    cpf TEXT UNIQUE NOT NULL,
                    data_registro DATE NOT NULL,
                    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
                    updated_at DATETIME DEFAULT CURRENT_TIMESTAMP
                )
            '''
            
            cursor.execute(sql_criar_tabela)
            conn.commit()
            
            print("✅ Tabela 'usuario' criada com sucesso!")
            print("\n📋 Estrutura da tabela:")
            print("   - id_usuario: INTEGER (chave primária, auto incremento)")
            print("   - nome: TEXT (obrigatório)")
            print("   - cpf: TEXT (único, obrigatório)")
            print("   - data_registro: DATE (obrigatório)")
            print("   - created_at: DATETIME (automático)")
            print("   - updated_at: DATETIME (automático)")
            
            conn.close()
            return True
            
        except sqlite3.Error as e:
            print(f"❌ Erro ao criar tabela: {e}")
            return False
    
    def inserir_usuario(self, nome, cpf, data_registro=None):
        """
        Insere um novo usuário na tabela
        
        Args:
            nome (str): Nome do usuário
            cpf (str): CPF do usuário
            data_registro (str): Data de registro (formato DD/MM/YYYY)
        """
        try:
            conn = self.conectar()
            cursor = conn.cursor()
            
            # Se não informar data_registro, usar data atual
            if not data_registro:
                data_registro = datetime.now().strftime('%d/%m/%Y')
            
            # Converter data para formato SQLite (YYYY-MM-DD)
            if '/' in data_registro:
                dia, mes, ano = data_registro.split('/')
                data_sqlite = f"{ano}-{mes.zfill(2)}-{dia.zfill(2)}"
            else:
                data_sqlite = data_registro
            
            # Inserir usuário
            sql_inserir = '''
                INSERT INTO usuario (nome, cpf, data_registro)
                VALUES (?, ?, ?)
            '''
            
            cursor.execute(sql_inserir, (nome, cpf, data_sqlite))
            conn.commit()
            
            # Pegar ID do usuário inserido
            user_id = cursor.lastrowid
            
            print(f"✅ Usuário inserido com sucesso!")
            print(f"   ID: {user_id}")
            print(f"   Nome: {nome}")
            print(f"   CPF: {cpf}")
            print(f"   Data Registro: {data_registro}")
            
            conn.close()
            return user_id
            
        except sqlite3.IntegrityError as e:
            if "UNIQUE constraint failed" in str(e):
                print(f"❌ Erro: CPF {cpf} já existe na base de dados!")
            else:
                print(f"❌ Erro de integridade: {e}")
            return None
            
        except sqlite3.Error as e:
            print(f"❌ Erro ao inserir usuário: {e}")
            return None
    
    def listar_usuarios(self):
        """
        Lista todos os usuários
        """
        try:
            conn = self.conectar()
            cursor = conn.cursor()
            
            cursor.execute('''
                SELECT id_usuario, nome, cpf, data_registro, created_at, updated_at
                FROM usuario
                ORDER BY id_usuario
            ''')
            
            usuarios = cursor.fetchall()
            
            if usuarios:
                print(f"\n👥 Usuários cadastrados ({len(usuarios)}):")
                print("-" * 80)
                print(f"{'ID':<4} {'Nome':<20} {'CPF':<15} {'Data Reg.':<12} {'Criado em':<20}")
                print("-" * 80)
                
                for usuario in usuarios:
                    id_user, nome, cpf, data_reg, created, updated = usuario
                    
                    # Formatar datas
                    if data_reg:
                        try:
                            data_formatada = datetime.strptime(data_reg, '%Y-%m-%d').strftime('%d/%m/%Y')
                        except:
                            data_formatada = data_reg
                    else:
                        data_formatada = "N/A"
                    
                    created_formatado = created[:16] if created else "N/A"
                    
                    print(f"{id_user:<4} {nome:<20} {cpf:<15} {data_formatada:<12} {created_formatado:<20}")
                
                print("-" * 80)
            else:
                print("📭 Nenhum usuário cadastrado ainda")
            
            conn.close()
            return usuarios
            
        except sqlite3.Error as e:
            print(f"❌ Erro ao listar usuários: {e}")
            return []
    
    def buscar_usuario_por_cpf(self, cpf):
        """
        Busca usuário por CPF
        """
        try:
            conn = self.conectar()
            cursor = conn.cursor()
            
            cursor.execute('''
                SELECT * FROM usuario WHERE cpf = ?
            ''', (cpf,))
            
            usuario = cursor.fetchone()
            
            if usuario:
                print(f"✅ Usuário encontrado:")
                print(f"   ID: {usuario[0]}")
                print(f"   Nome: {usuario[1]}")
                print(f"   CPF: {usuario[2]}")
                print(f"   Data Registro: {usuario[3]}")
            else:
                print(f"❌ Usuário com CPF {cpf} não encontrado")
            
            conn.close()
            return usuario
            
        except sqlite3.Error as e:
            print(f"❌ Erro ao buscar usuário: {e}")
            return None
    
    def verificar_tabela(self):
        """
        Verifica se a tabela existe e mostra sua estrutura
        """
        try:
            conn = self.conectar()
            cursor = conn.cursor()
            
            # Verificar se tabela existe
            cursor.execute('''
                SELECT name FROM sqlite_master 
                WHERE type='table' AND name='usuario'
            ''')
            
            if cursor.fetchone():
                print("✅ Tabela 'usuario' existe!")
                
                # Mostrar estrutura da tabela
                cursor.execute('PRAGMA table_info(usuario)')
                colunas = cursor.fetchall()
                
                print("\n📋 Estrutura da tabela:")
                print("-" * 60)
                print(f"{'Coluna':<15} {'Tipo':<12} {'Null':<6} {'Padrão':<15}")
                print("-" * 60)
                
                for coluna in colunas:
                    nome = coluna[1]
                    tipo = coluna[2]
                    not_null = "NÃO" if coluna[3] else "SIM"
                    padrao = coluna[4] if coluna[4] else ""
                    
                    print(f"{nome:<15} {tipo:<12} {not_null:<6} {padrao:<15}")
                
                print("-" * 60)
                
                # Contar registros
                cursor.execute('SELECT COUNT(*) FROM usuario')
                total = cursor.fetchone()[0]
                print(f"\n📊 Total de registros: {total}")
                
            else:
                print("❌ Tabela 'usuario' não existe!")
                return False
            
            conn.close()
            return True
            
        except sqlite3.Error as e:
            print(f"❌ Erro ao verificar tabela: {e}")
            return False

# Script principal
def main():
    print("=== Gerenciador de Tabela Usuario ===\n")
    
    # Criar instância do gerenciador
    gu = GerenciadorUsuario('controle_gastos.db')
    
    print("1. Criando tabela usuario...")
    if gu.criar_tabela_usuario():
        
        print("\n" + "="*60)
        print("\n2. Verificando estrutura da tabela...")
        gu.verificar_tabela()
        
        print("\n" + "="*60)
        print("\n3. Inserindo usuário de exemplo...")
        
        # Inserir o usuário do exemplo
        gu.inserir_usuario(
            nome="João Silva",
            cpf="545.554.454-41",
            data_registro="15/04/2025"
        )
        
        print("\n" + "="*60)
        print("\n4. Listando usuários...")
        gu.listar_usuarios()
        
        print("\n" + "="*60)
        print("\n✅ Tabela usuario criada e configurada com sucesso!")
        print(f"📁 Banco: {os.path.abspath(gu.db_path)}")
        
        print("\n🎯 Próximos passos:")
        print("   - Inserir mais usuários")
        print("   - Criar outras tabelas (gastos, categorias, etc.)")
        print("   - Implementar operações CRUD completas")
    
    else:
        print("❌ Falha ao criar tabela usuario")

if __name__ == "__main__":
    main()