import sqlite3
import os
from datetime import datetime

class GerenciadorEntradaDinheiro:
    """
    Classe para gerenciar a tabela de entrada_dinheiro
    """
    
    def __init__(self, db_path='controle_gastos.db'):
        self.db_path = db_path
    
    def conectar(self):
        """Conecta ao banco SQLite"""
        return sqlite3.connect(self.db_path)
    
    def criar_tabela_entrada_dinheiro(self):
        """
        Cria a tabela entrada_dinheiro com a estrutura especificada
        """
        try:
            conn = self.conectar()
            cursor = conn.cursor()
            
            # Criar tabela entrada_dinheiro
            sql_criar_tabela = '''
                CREATE TABLE IF NOT EXISTS entrada_dinheiro (
                    ID_ENTRADA INTEGER PRIMARY KEY AUTOINCREMENT,
                    ID_CATEGORIA INTEGER NOT NULL,
                    ID_USUARIO INTEGER NOT NULL,
                    data_registro DATE NOT NULL,
                    valor DECIMAL(10,2) NOT NULL,
                    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
                    updated_at DATETIME DEFAULT CURRENT_TIMESTAMP,
                    FOREIGN KEY (ID_CATEGORIA) REFERENCES categorias(ID_CATEGORIA),
                    FOREIGN KEY (ID_USUARIO) REFERENCES usuario(ID_USUARIO)
                )
            '''
            
            cursor.execute(sql_criar_tabela)
            
            # Criar índices para melhor performance
            cursor.execute('''
                CREATE INDEX IF NOT EXISTS idx_entrada_categoria 
                ON entrada_dinheiro(ID_CATEGORIA)
            ''')
            
            cursor.execute('''
                CREATE INDEX IF NOT EXISTS idx_entrada_usuario 
                ON entrada_dinheiro(ID_USUARIO)
            ''')
            
            cursor.execute('''
                CREATE INDEX IF NOT EXISTS idx_entrada_data 
                ON entrada_dinheiro(data_registro)
            ''')
            
            conn.commit()
            
            print("✅ Tabela 'entrada_dinheiro' criada com sucesso!")
            print("\n📋 Estrutura da tabela:")
            print("   - ID_ENTRADA: INTEGER (chave primária, auto incremento)")
            print("   - ID_CATEGORIA: INTEGER (chave estrangeira para categorias)")
            print("   - ID_USUARIO: INTEGER (chave estrangeira para usuario)")
            print("   - data_registro: DATE (obrigatório)")
            print("   - valor: DECIMAL(10,2) (obrigatório)")
            print("   - created_at: DATETIME (automático)")
            print("   - updated_at: DATETIME (automático)")
            
            conn.close()
            return True
            
        except sqlite3.Error as e:
            print(f"❌ Erro ao criar tabela: {e}")
            return False
    
    def inserir_entrada(self, id_categoria, id_usuario, data_registro, valor):
        """
        Insere uma nova entrada de dinheiro
        
        Args:
            id_categoria (int): ID da categoria (deve ser do tipo 'entrada')
            id_usuario (int): ID do usuário
            data_registro (str): Data no formato DD/MM/YYYY
            valor (float): Valor da entrada
        """
        try:
            conn = self.conectar()
            cursor = conn.cursor()
            
            # Verificar se usuário existe
            cursor.execute('SELECT ID_USUARIO FROM usuario WHERE ID_USUARIO = ?', (id_usuario,))
            if not cursor.fetchone():
                print(f"❌ Erro: Usuário com ID {id_usuario} não existe!")
                conn.close()
                return None
            
            # Verificar se categoria existe e é do tipo 'entrada'
            cursor.execute('''
                SELECT ID_CATEGORIA, tipo, categoria 
                FROM categorias 
                WHERE ID_CATEGORIA = ? AND tipo = 'entrada'
            ''', (id_categoria,))
            
            categoria = cursor.fetchone()
            if not categoria:
                print(f"❌ Erro: Categoria com ID {id_categoria} não existe ou não é do tipo 'entrada'!")
                conn.close()
                return None
            
            # Converter data para formato SQLite (YYYY-MM-DD)
            if '/' in data_registro:
                dia, mes, ano = data_registro.split('/')
                data_sqlite = f"{ano}-{mes.zfill(2)}-{dia.zfill(2)}"
            else:
                data_sqlite = data_registro
            
            # Inserir entrada
            sql_inserir = '''
                INSERT INTO entrada_dinheiro (ID_CATEGORIA, ID_USUARIO, data_registro, valor)
                VALUES (?, ?, ?, ?)
            '''
            
            cursor.execute(sql_inserir, (id_categoria, id_usuario, data_sqlite, valor))
            conn.commit()
            
            # Pegar ID da entrada inserida
            entrada_id = cursor.lastrowid
            
            print(f"✅ Entrada de dinheiro inserida com sucesso!")
            print(f"   ID Entrada: {entrada_id}")
            print(f"   Categoria: {categoria[2]} (ID: {id_categoria})")
            print(f"   Usuário ID: {id_usuario}")
            print(f"   Data: {data_registro}")
            print(f"   Valor: R$ {valor:,.2f}")
            
            conn.close()
            return entrada_id
            
        except sqlite3.Error as e:
            print(f"❌ Erro ao inserir entrada: {e}")
            return None
        except ValueError as e:
            print(f"❌ Erro no formato da data: {e}")
            return None
    
    def listar_entradas(self, id_usuario=None, data_inicio=None, data_fim=None):
        """
        Lista entradas com filtros opcionais
        
        Args:
            id_usuario (int): Filtrar por usuário específico
            data_inicio (str): Data início (DD/MM/YYYY)
            data_fim (str): Data fim (DD/MM/YYYY)
        """
        try:
            conn = self.conectar()
            cursor = conn.cursor()
            
            # Construir query com filtros
            sql = '''
                SELECT e.ID_ENTRADA, e.ID_CATEGORIA, c.categoria, e.ID_USUARIO, u.nome,
                       e.data_registro, e.valor, e.created_at
                FROM entrada_dinheiro e
                LEFT JOIN categorias c ON e.ID_CATEGORIA = c.ID_CATEGORIA
                LEFT JOIN usuario u ON e.ID_USUARIO = u.ID_USUARIO
                WHERE 1=1
            '''
            params = []
            
            if id_usuario:
                sql += ' AND e.ID_USUARIO = ?'
                params.append(id_usuario)
            
            if data_inicio:
                if '/' in data_inicio:
                    dia, mes, ano = data_inicio.split('/')
                    data_inicio_sqlite = f"{ano}-{mes.zfill(2)}-{dia.zfill(2)}"
                else:
                    data_inicio_sqlite = data_inicio
                sql += ' AND e.data_registro >= ?'
                params.append(data_inicio_sqlite)
            
            if data_fim:
                if '/' in data_fim:
                    dia, mes, ano = data_fim.split('/')
                    data_fim_sqlite = f"{ano}-{mes.zfill(2)}-{dia.zfill(2)}"
                else:
                    data_fim_sqlite = data_fim
                sql += ' AND e.data_registro <= ?'
                params.append(data_fim_sqlite)
            
            sql += ' ORDER BY e.data_registro DESC, e.ID_ENTRADA DESC'
            
            cursor.execute(sql, params)
            entradas = cursor.fetchall()
            
            if entradas:
                filtro_info = ""
                if id_usuario:
                    filtro_info += f" (Usuário: {id_usuario})"
                if data_inicio:
                    filtro_info += f" (De: {data_inicio})"
                if data_fim:
                    filtro_info += f" (Até: {data_fim})"
                
                print(f"\n💰 Entradas de dinheiro ({len(entradas)}){filtro_info}:")
                print("-" * 100)
                print(f"{'ID':<6} {'Categoria':<15} {'Usuário':<15} {'Data':<12} {'Valor':<12} {'Criado em':<12}")
                print("-" * 100)
                
                total_valor = 0
                
                for entrada in entradas:
                    id_entrada, id_cat, categoria, id_user, nome_user, data_reg, valor, created = entrada
                    
                    categoria_nome = categoria[:14] if categoria else "N/A"
                    nome_user = nome_user[:14] if nome_user else "N/A"
                    
                    # Formatar data
                    try:
                        data_formatada = datetime.strptime(data_reg, '%Y-%m-%d').strftime('%d/%m/%Y')
                    except:
                        data_formatada = data_reg
                    
                    created_formatado = created[:10] if created else "N/A"
                    valor_formatado = f"R$ {valor:,.2f}" if valor else "R$ 0,00"
                    
                    print(f"{id_entrada:<6} {categoria_nome:<15} {nome_user:<15} {data_formatada:<12} {valor_formatado:<12} {created_formatado:<12}")
                    
                    if valor:
                        total_valor += valor
                
                print("-" * 100)
                print(f"💎 TOTAL: R$ {total_valor:,.2f}")
                
            else:
                print("📭 Nenhuma entrada encontrada")
            
            conn.close()
            return entradas
            
        except sqlite3.Error as e:
            print(f"❌ Erro ao listar entradas: {e}")
            return []
    
    def buscar_entrada_por_id(self, id_entrada):
        """
        Busca entrada por ID
        """
        try:
            conn = self.conectar()
            cursor = conn.cursor()
            
            cursor.execute('''
                SELECT e.*, c.categoria, c.tipo, u.nome 
                FROM entrada_dinheiro e
                LEFT JOIN categorias c ON e.ID_CATEGORIA = c.ID_CATEGORIA
                LEFT JOIN usuario u ON e.ID_USUARIO = u.ID_USUARIO
                WHERE e.ID_ENTRADA = ?
            ''', (id_entrada,))
            
            entrada = cursor.fetchone()
            
            if entrada:
                print(f"✅ Entrada encontrada:")
                print(f"   ID Entrada: {entrada[0]}")
                print(f"   Categoria: {entrada[7]} (ID: {entrada[1]})")
                print(f"   Usuário: {entrada[9]} (ID: {entrada[2]})")
                print(f"   Data: {entrada[3]}")
                print(f"   Valor: R$ {entrada[4]:,.2f}")
                print(f"   Criado em: {entrada[5]}")
            else:
                print(f"❌ Entrada com ID {id_entrada} não encontrada")
            
            conn.close()
            return entrada
            
        except sqlite3.Error as e:
            print(f"❌ Erro ao buscar entrada: {e}")
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
                WHERE type='table' AND name='entrada_dinheiro'
            ''')
            
            if cursor.fetchone():
                print("✅ Tabela 'entrada_dinheiro' existe!")
                
                # Mostrar estrutura da tabela
                cursor.execute('PRAGMA table_info(entrada_dinheiro)')
                colunas = cursor.fetchall()
                
                print("\n📋 Estrutura da tabela:")
                print("-" * 70)
                print(f"{'Coluna':<18} {'Tipo':<15} {'Null':<6} {'Padrão':<15}")
                print("-" * 70)
                
                for coluna in colunas:
                    nome = coluna[1]
                    tipo = coluna[2]
                    not_null = "NÃO" if coluna[3] else "SIM"
                    padrao = coluna[4] if coluna[4] else ""
                    
                    print(f"{nome:<18} {tipo:<15} {not_null:<6} {padrao:<15}")
                
                print("-" * 70)
                
                # Contar registros
                cursor.execute('SELECT COUNT(*) FROM entrada_dinheiro')
                total = cursor.fetchone()[0]
                print(f"\n📊 Total de registros: {total}")
                
                # Somar valor total
                cursor.execute('SELECT SUM(valor) FROM entrada_dinheiro')
                total_valor = cursor.fetchone()[0]
                if total_valor:
                    print(f"💰 Valor total: R$ {total_valor:,.2f}")
                
            else:
                print("❌ Tabela 'entrada_dinheiro' não existe!")
                return False
            
            conn.close()
            return True
            
        except sqlite3.Error as e:
            print(f"❌ Erro ao verificar tabela: {e}")
            return False
    
    def inserir_exemplo(self):
        """
        Insere entrada de exemplo
        """
        try:
            conn = self.conectar()
            cursor = conn.cursor()
            
            # Buscar usuário e categoria de entrada
            cursor.execute('SELECT ID_USUARIO FROM usuario LIMIT 1')
            usuario = cursor.fetchone()
            
            cursor.execute("SELECT ID_CATEGORIA FROM categorias WHERE tipo = 'entrada' LIMIT 1")
            categoria = cursor.fetchone()
            
            if not usuario:
                print("❌ Nenhum usuário encontrado. Crie um usuário primeiro!")
                return False
            
            if not categoria:
                print("❌ Nenhuma categoria de entrada encontrada. Crie uma categoria primeiro!")
                return False
            
            conn.close()
            
            # Inserir entrada de exemplo
            return self.inserir_entrada(
                id_categoria=categoria[0],
                id_usuario=usuario[0],
                data_registro="15/04/2025",
                valor=8000.90
            )
            
        except sqlite3.Error as e:
            print(f"❌ Erro ao inserir exemplo: {e}")
            return False

# Script principal
def main():
    print("=== Gerenciador de Tabela Entrada Dinheiro ===\n")
    
    # Criar instância do gerenciador
    ged = GerenciadorEntradaDinheiro('controle_gastos.db')
    
    print("1. Criando tabela entrada_dinheiro...")
    if ged.criar_tabela_entrada_dinheiro():
        
        print("\n" + "="*70)
        print("\n2. Verificando estrutura da tabela...")
        ged.verificar_tabela()
        
        print("\n" + "="*70)
        print("\n3. Inserindo entrada de exemplo...")
        if ged.inserir_exemplo():
            
            print("\n" + "="*70)
            print("\n4. Listando entradas...")
            ged.listar_entradas()
        
        print("\n" + "="*70)
        print("\n✅ Tabela entrada_dinheiro criada e configurada com sucesso!")
        print(f"📁 Banco: {os.path.abspath(ged.db_path)}")
        
        print("\n🎯 Próximos passos:")
        print("   - Inserir mais entradas")
        print("   - Criar tabela de saídas")
        print("   - Implementar relatórios financeiros")
    
    else:
        print("❌ Falha ao criar tabela entrada_dinheiro")

if __name__ == "__main__":
    main()