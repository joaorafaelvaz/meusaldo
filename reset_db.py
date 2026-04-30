import os
import sys

# Add the project root to the path so we can import backend modules
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from backend.database import engine, Base
from backend import models

def reset_database():
    print("Aviso: Isso irá deletar todas as tabelas e recriá-las.")
    print("Conectado ao banco de dados:", engine.url)
    
    try:
        # Drop all tables
        print("Apagando tabelas antigas...")
        Base.metadata.drop_all(bind=engine)
        
        # Create all tables with the new schema
        print("Criando tabelas com o novo schema...")
        Base.metadata.create_all(bind=engine)
        
        print("Sucesso! Banco de dados recriado.")
    except Exception as e:
        print(f"Erro ao recriar o banco de dados: {e}")

if __name__ == "__main__":
    reset_database()
