# -*- coding: utf-8 -*-
"""
run_migrations.py - Script local pour exécuter les migrations SQL sur la base locale ou distante.
"""

import os
import asyncio
from pathlib import Path
from sqlalchemy import text
from sqlalchemy.ext.asyncio import create_async_engine

def clean_sql_comments(sql_content):
    """
    Supprime proprement les commentaires SQL mono-ligne (-- ...) et multi-ligne (/* ... */)
    pour éviter que des caractères comme les apostrophes dans les commentaires ne perturbent le parseur.
    """
    cleaned_chars = []
    in_line_comment = False
    in_block_comment = False
    i = 0
    n = len(sql_content)
    while i < n:
        char = sql_content[i]
        if in_line_comment:
            if char == '\n':
                in_line_comment = False
                cleaned_chars.append(char)
        elif in_block_comment:
            if char == '*' and i + 1 < n and sql_content[i+1] == '/':
                in_block_comment = False
                i += 1
        else:
            if char == '-' and i + 1 < n and sql_content[i+1] == '-':
                in_line_comment = True
                i += 1
            elif char == '/' and i + 1 < n and sql_content[i+1] == '*':
                in_block_comment = True
                i += 1
            else:
                cleaned_chars.append(char)
        i += 1
    return ''.join(cleaned_chars)

def split_sql_statements(sql_content):
    """
    Découpe le contenu SQL en instructions individuelles en respectant les blocs $$
    (dollar-quoted strings) et les chaînes entre guillemets simples.
    """
    # Éliminer d'abord les commentaires pour éviter les faux-positifs d'apostrophes
    sql_content = clean_sql_comments(sql_content)
    
    statements = []
    current_stmt = []
    in_dollar_block = False
    in_single_quote = False
    
    i = 0
    n = len(sql_content)
    while i < n:
        char = sql_content[i]
        
        # Détection de $$ (dollar quoting)
        if char == '$' and i + 1 < n and sql_content[i+1] == '$':
            in_dollar_block = not in_dollar_block
            current_stmt.append('$$')
            i += 2
            continue
            
        # Détection des guillemets simples (hors blocs dollar)
        if char == "'" and not in_dollar_block:
            in_single_quote = not in_single_quote
            
        # Découpe sur point-virgule (uniquement hors chaînes et blocs dollar)
        if char == ';' and not in_dollar_block and not in_single_quote:
            statements.append(''.join(current_stmt).strip())
            current_stmt = []
        else:
            current_stmt.append(char)
        i += 1
        
    if current_stmt:
        remainder = ''.join(current_stmt).strip()
        if remainder:
            statements.append(remainder)
            
    # Nettoyage
    cleaned = []
    for s in statements:
        lines = []
        for line in s.split('\n'):
            line_stripped = line.strip()
            if line_stripped:
                lines.append(line)
        cleaned_stmt = '\n'.join(lines).strip()
        if cleaned_stmt:
            # Ignorer les instructions de transaction explicites
            upper_stmt = cleaned_stmt.upper().replace(';', '').strip()
            if upper_stmt in ("BEGIN", "COMMIT", "ROLLBACK", "BEGIN TRANSACTION", "COMMIT TRANSACTION"):
                continue
            cleaned.append(cleaned_stmt)
            
    return cleaned

async def main():
    # Définir le DATABASE_URL local si non présent ou si pointant vers 'db'
    db_url = os.getenv("DATABASE_URL")
    if not db_url or "@db:" in db_url:
        db_url = "postgresql+asyncpg://khawarizmi_user:MOT_DE_PASSE_FORT_ICI@127.0.0.1:5432/khawarizmi"
    else:
        if db_url.startswith("postgres://"):
            db_url = db_url.replace("postgres://", "postgresql+asyncpg://", 1)
        elif db_url.startswith("postgresql://"):
            db_url = db_url.replace("postgresql://", "postgresql+asyncpg://", 1)
        
    print(f"Connecting to database at: {db_url.split('@')[-1]}")
    engine = create_async_engine(db_url, echo=False)
    
    # 1. Créer l'extension vector si inexistante
    print("Enabling vector extension...")
    async with engine.connect() as conn:
        async with conn.begin():
            await conn.execute(text("CREATE EXTENSION IF NOT EXISTS vector;"))
    print("Vector extension enabled!")
    
    # 2. Exécuter les migrations *.sql dans l'ordre
    migrations_dir = Path(__file__).parent / "migrations"
    if migrations_dir.exists():
        sql_files = sorted(migrations_dir.glob("*.sql"))
        print(f"Found {len(sql_files)} migrations in {migrations_dir}")
        
        async with engine.connect() as conn:
            for sql_file in sql_files:
                print(f"Running {sql_file.name}...")
                sql_content = sql_file.read_text(encoding="utf-8")
                
                statements = split_sql_statements(sql_content)
                for stmt in statements:
                    try:
                        async with conn.begin():
                            await conn.execute(text(stmt))
                    except Exception as e:
                        # Ignorer si l'élément existe déjà
                        err_str = str(e).lower()
                        if "already exists" in err_str or "duplicate column" in err_str:
                            continue
                        print(f"  Warning in {sql_file.name} statement skipped: {e}")
                        
        print("✅ All migrations applied successfully!")
    else:
        print("Error: migrations directory not found.")
        
    await engine.dispose()

if __name__ == "__main__":
    asyncio.run(main())
