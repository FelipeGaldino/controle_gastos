import sqlite3
import os
from datetime import datetime

class GerenciadorCategorias:
    """
    Classe para gerenciar a tabela de categorias
    """
    
    def __init__(self, db_path='controle_gastos.db'):
        self.db_path = db_path
    
    def conectar(self):
        """Conecta ao banco SQLite"""
        return sqlite3.connect(self.db_path)
    
    def criar_tabela_categorias(self):
        """
        Cria a tabela categorias com a estrutura especificada
        """
        try:
            conn = self.conectar()
            cursor = conn.cursor()
            
            # Criar tabela categorias
            sql_criar_tabela = '''
                CREATE TABLE IF NOT EXISTS categorias (
                    id_categoria INTEGER PRIMARY KEY AUTOINCREMENT,
                    id_usuario INTEGER NOT NULL,
                    tipo TEXT NOT NULL CHECK (tipo IN ('entrada', 'saida')),
                    categoria TEXT NOT NULL,
                    created_at DATETIME DEFAULT current_timestamp,
                    updated_at DATETIME DEFAULT current_timestamp,
                    FOREIGN KEY (id_usuario) REFERENCES usuario(id_usuario)
                )
            '''
            
            cursor.execute(sql_criar_tabela)
            
            # Criar índices para melhor performance
            cursor.execute('''
                CREATE INDEX IF NOT EXISTS idx_categorias_usuario 
                ON categorias(ID_USUARIO)
            ''')
            
            cursor.execute('''
                CREATE INDEX IF NOT EXISTS idx_categorias_tipo 
                ON categorias(tipo)
            ''')
            
            conn.commit()
            
            print("✅ Tabela 'categorias' criada com sucesso!")
            print("\n📋 Estrutura da tabela:")
            print("   - ID_CATEGORIA: INTEGER (chave primária, auto incremento)")
            print("   - ID_USUARIO: INTEGER (chave estrangeira para usuario)")
            print("   - tipo: TEXT ('entrada' ou 'saida')")
            print("   - categoria: TEXT (nome da categoria)")
            print("   - created_at: DATETIME (automático)")
            print("   - updated_at: DATETIME (automático)")
            
            conn.close()
            return True
            
        except sqlite3.Error as e:
            print(f"❌ Erro ao criar tabela: {e}")
            return False
    
    def inserir_categoria(self, id_usuario, tipo, categoria):
        """
        Insere uma nova categoria
        
        Args:
            id_usuario (int): ID do usuário
            tipo (str): 'entrada' ou 'saida'
            categoria (str): Nome da categoria
        """
        try:
            # Validar tipo
            if tipo.lower() not in ['entrada', 'saida']:
                print("❌ Erro: Tipo deve ser 'entrada' ou 'saida'")
                return None
            
            conn = self.conectar()
            cursor = conn.cursor()
            
            # Verificar se usuário existe
            cursor.execute('SELECT ID_USUARIO FROM usuario WHERE ID_USUARIO = ?', (id_usuario,))
            if not cursor.fetchone():
                print(f"❌ Erro: Usuário com ID {id_usuario} não existe!")
                conn.close()
                return None
            
            # Inserir categoria
            sql_inserir = '''
                INSERT INTO categorias (ID_USUARIO, tipo, categoria)
                VALUES (?, ?, ?)
            '''
            
            cursor.execute(sql_inserir, (id_usuario, tipo.lower(), categoria))
            conn.commit()
            
            # Pegar ID da categoria inserida
            categoria_id = cursor.lastrowid
            
            print(f"✅ Categoria inserida com sucesso!")
            print(f"   ID Categoria: {categoria_id}")
            print(f"   ID Usuário: {id_usuario}")
            print(f"   Tipo: {tipo}")
            print(f"   Categoria: {categoria}")
            
            conn.close()
            return categoria_id
            
        except sqlite3.Error as e:
            print(f"❌ Erro ao inserir categoria: {e}")
            return None
    
    def listar_categorias(self, id_usuario=None, tipo=None):
        """
        Lista categorias com filtros opcionais
        
        Args:
            id_usuario (int): Filtrar por usuário específico
            tipo (str): Filtrar por tipo ('entrada' ou 'saida')
        """
        try:
            conn = self.conectar()
            cursor = conn.cursor()
            
            # Construir query com filtros
            sql = '''
                SELECT c.ID_CATEGORIA, c.ID_USUARIO, u.nome, c.tipo, c.categoria, 
                       c.created_at, c.updated_at
                FROM categorias c
                LEFT JOIN usuario u ON c.ID_USUARIO = u.ID_USUARIO
                WHERE 1=1
            '''
            params = []
            
            if id_usuario:
                sql += ' AND c.ID_USUARIO = ?'
                params.append(id_usuario)
            
            if tipo:
                sql += ' AND c.tipo = ?'
                params.append(tipo.lower())
            
            sql += ' ORDER BY c.tipo, c.categoria'
            
            cursor.execute(sql, params)
            categorias = cursor.fetchall()
            
            if categorias:
                filtro_info = ""
                if id_usuario:
                    filtro_info += f" (Usuário: {id_usuario})"
                if tipo:
                    filtro_info += f" (Tipo: {tipo})"
                
                print(f"\n📂 Categorias cadastradas ({len(categorias)}){filtro_info}:")
                print("-" * 90)
                print(f"{'ID':<4} {'User':<6} {'Nome Usuário':<15} {'Tipo':<8} {'Categoria':<20} {'Criado em':<15}")
                print("-" * 90)
                
                for cat in categorias:
                    id_cat, id_user, nome_user, tipo_cat, categoria, created, updated = cat
                    
                    nome_user = nome_user[:14] if nome_user else "N/A"
                    categoria_nome = categoria[:19] if categoria else "N/A"
                    created_formatado = created[:10] if created else "N/A"
                    
                    print(f"{id_cat:<4} {id_user:<6} {nome_user:<15} {tipo_cat:<8} {categoria_nome:<20} {created_formatado:<15}")
                
                print("-" * 90)
            else:
                print("📭 Nenhuma categoria encontrada")
            
            conn.close()
            return categorias
            
        except sqlite3.Error as e:
            print(f"❌ Erro ao listar categorias: {e}")
            return []
    
    def listar_por_tipo(self, tipo):
        """
        Lista categorias por tipo específico
        """
        return self.listar_categorias(tipo=tipo)
    
    def listar_por_usuario(self, id_usuario):
        """
        Lista categorias de um usuário específico
        """
        return self.listar_categorias(id_usuario=id_usuario)
    
    def buscar_categoria_por_id(self, id_categoria):
        """
        Busca categoria por ID
        """
        try:
            conn = self.conectar()
            cursor = conn.cursor()
            
            cursor.execute('''
                SELECT c.*, u.nome 
                FROM categorias c
                LEFT JOIN usuario u ON c.ID_USUARIO = u.ID_USUARIO
                WHERE c.ID_CATEGORIA = ?
            ''', (id_categoria,))
            
            categoria = cursor.fetchone()
            
            if categoria:
                print(f"✅ Categoria encontrada:")
                print(f"   ID Categoria: {categoria[0]}")
                print(f"   ID Usuário: {categoria[1]}")
                print(f"   Nome Usuário: {categoria[7]}")
                print(f"   Tipo: {categoria[2]}")
                print(f"   Categoria: {categoria[3]}")
                print(f"   Criado em: {categoria[4]}")
            else:
                print(f"❌ Categoria com ID {id_categoria} não encontrada")
            
            conn.close()
            return categoria
            
        except sqlite3.Error as e:
            print(f"❌ Erro ao buscar categoria: {e}")
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
                WHERE type='table' AND name='categorias'
            ''')
            
            if cursor.fetchone():
                print("✅ Tabela 'categorias' existe!")
                
                # Mostrar estrutura da tabela
                cursor.execute('PRAGMA table_info(categorias)')
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
                cursor.execute('SELECT COUNT(*) FROM categorias')
                total = cursor.fetchone()[0]
                print(f"\n📊 Total de registros: {total}")
                
                # Contar por tipo
                cursor.execute('''
                    SELECT tipo, COUNT(*) 
                    FROM categorias 
                    GROUP BY tipo
                ''')
                tipos = cursor.fetchall()
                
                if tipos:
                    print("\n📊 Por tipo:")
                    for tipo, count in tipos:
                        print(f"   {tipo}: {count}")
                
            else:
                print("❌ Tabela 'categorias' não existe!")
                return False
            
            conn.close()
            return True
            
        except sqlite3.Error as e:
            print(f"❌ Erro ao verificar tabela: {e}")
            return False
    
    def inserir_categorias_exemplo(self):
        """
        Insere categorias de exemplo
        """
        try:
            conn = self.conectar()
            cursor = conn.cursor()
            
            # Buscar um usuário existente para usar como exemplo
            cursor.execute('SELECT ID_USUARIO FROM usuario LIMIT 1')
            resultado = cursor.fetchone()
            
            if not resultado:
                print("❌ Nenhum usuário encontrado. Crie um usuário primeiro!")
                conn.close()
                return False
            
            id_usuario = resultado[0]
            conn.close()
            
            print(f"📝 Inserindo categorias de exemplo para usuário ID: {id_usuario}")
            
            # Categorias de exemplo
            categorias_exemplo = [
                ('entrada', 'Salário'),
                ('entrada', 'Freelance'),
                ('entrada', 'Investimentos'),
                ('saida', 'Mercado'),
                ('saida', 'Transporte'),
                ('saida', 'Lazer'),
                ('saida', 'Contas'),
                ('saida', 'Saúde')
            ]
            
            for tipo, categoria in categorias_exemplo:
                self.inserir_categoria(id_usuario, tipo, categoria)
            
            return True
            
        except sqlite3.Error as e:
            print(f"❌ Erro ao inserir categorias de exemplo: {e}")
            return False

# Script principal
def main():
    print("=== Gerenciador de Tabela Categorias ===\n")
    
    # Criar instância do gerenciador
    gc = GerenciadorCategorias('controle_gastos.db')
    
    print("1. Criando tabela categorias...")
    if gc.criar_tabela_categorias():
        
        print("\n" + "="*60)
        print("\n2. Verificando estrutura da tabela...")
        gc.verificar_tabela()
        
        print("\n" + "="*60)
        print("\n3. Inserindo categorias de exemplo...")
        if gc.inserir_categorias_exemplo():
            
            print("\n" + "="*60)
            print("\n4. Listando todas as categorias...")
            gc.listar_categorias()
            
            print("\n" + "="*60)
            print("\n5. Categorias de ENTRADA:")
            gc.listar_por_tipo('entrada')
            
            print("\n" + "="*60)
            print("\n6. Categorias de SAÍDA:")
            gc.listar_por_tipo('saida')
        
        print("\n" + "="*60)
        print("\n✅ Tabela categorias criada e configurada com sucesso!")
        print(f"📁 Banco: {os.path.abspath(gc.db_path)}")
        
        print("\n🎯 Próximos passos:")
        print("   - Inserir mais categorias personalizadas")
        print("   - Criar tabela de gastos/transações")
        print("   - Implementar relatórios por categoria")
    
    else:
        print("❌ Falha ao criar tabela categorias")

if __name__ == "__main__":
    main()