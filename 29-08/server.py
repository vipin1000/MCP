
# import sqlite3
# import argparse
# from mcp.server.fastmcp import FastMCP

# mcp = FastMCP('sqlite-demo')

# def init_db():
#     conn = sqlite3.connect('demo.db')
#     cursor = conn.cursor()
#     cursor.execute('''
#         CREATE TABLE IF NOT EXISTS people (
#             id INTEGER PRIMARY KEY AUTOINCREMENT,
#             name TEXT NOT NULL,
#             age INTEGER NOT NULL,
#             profession TEXT NOT NULL
#         )
#     ''')
#     conn.commit()
#     return conn, cursor

# @mcp.tool()
# def add_data(query: str) -> bool:
#     """Add new data to the people table using a SQL INSERT query.

#     Args:
#         query (str): SQL INSERT query following this format:
#             INSERT INTO people (name, age, profession)
#             VALUES ('John Doe', 30, 'Engineer')
        
#     Schema:
#         - name: Text field (required)
#         - age: Integer field (required)
#         - profession: Text field (required)
#         Note: 'id' field is auto-generated
    
#     Returns:
#         bool: True if data was added successfully, False otherwise
    
#     Example:
#         >>> query = '''
#         ... INSERT INTO people (name, age, profession)
#         ... VALUES ('Alice Smith', 25, 'Developer')
#         ... '''
#         >>> add_data(query)
#         True
#     """
#     conn, cursor = init_db()
#     try:
#         cursor.execute(query)
#         conn.commit()
#         return True
#     except sqlite3.Error as e:
#         print(f"Error adding data: {e}")
#         return False
#     finally:
#         conn.close()

# @mcp.tool()
# def read_data(query: str = "SELECT * FROM people") -> list:
#     """Read data from the people table using a SQL SELECT query.

#     Args:
#         query (str, optional): SQL SELECT query. Defaults to "SELECT * FROM people".
#             Examples:
#             - "SELECT * FROM people"
#             - "SELECT name, age FROM people WHERE age > 25"
#             - "SELECT * FROM people ORDER BY age DESC"
    
#     Returns:
#         list: List of tuples containing the query results.
#               For default query, tuple format is (id, name, age, profession)
    
#     Example:
#         >>> # Read all records
#         >>> read_data()
#         [(1, 'John Doe', 30, 'Engineer'), (2, 'Alice Smith', 25, 'Developer')]
        
#         >>> # Read with custom query
#         >>> read_data("SELECT name, profession FROM people WHERE age < 30")
#         [('Alice Smith', 'Developer')]
#     """
#     conn, cursor = init_db()
#     try:
#         cursor.execute(query)
#         return cursor.fetchall()
#     except sqlite3.Error as e:
#         print(f"Error reading data: {e}")
#         return []
#     finally:
#         conn.close()



# if __name__ == "__main__":
#     # Start the server
#     print("🚀Starting server... ")

#     # Debug Mode
#     #  uv run mcp dev server.py

#     # Production Mode
#     # uv run server.py --server_type=sse

#     parser = argparse.ArgumentParser()
#     parser.add_argument(
#         "--server_type", type=str, default="sse", choices=["sse", "stdio"]
#     )

#     args = parser.parse_args()
#     mcp.run(args.server_type)



# # # Example usage
# # if __name__ == "__main__":
# #     # Example INSERT query
# #     insert_query = """
# #     INSERT INTO people (name, age, profession)
# #     VALUES ('John Doe', 30, 'Engineer')
# #     """
    
# #     # Add data
# #     if add_data(insert_query):
# #         print("Data added successfully")
    
# #     # Read all data
# #     results = read_data()
# #     print("\nAll records:")
# #     for record in results:
# #         print(record)





#!/usr/bin/env python3
"""
Unified Advanced MCP Server - main.py
Author: Vipin Ruhal
Description: Combines SQLite demo tools with advanced file operations,
directory management, code analysis, data processing, and database management.
"""

from mcp.server.fastmcp import FastMCP
import os
import shutil
import json
import csv
import sqlite3
import ast
import threading
import argparse
from datetime import datetime
from typing import Dict, List, Any

# Create MCP server
mcp = FastMCP("Unified Advanced MCP Server")

_base_dir = os.path.dirname(__file__)
_file_lock = threading.Lock()

# =============================================
# DEMO SQLITE TOOLS (demo.db)
# =============================================

def init_db():
    conn = sqlite3.connect("demo.db")
    cursor = conn.cursor()
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS people (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL,
            age INTEGER NOT NULL,
            profession TEXT NOT NULL
        )
    ''')
    conn.commit()
    return conn, cursor

@mcp.tool()
def add_data(query: str) -> bool:
    """Add new data to the demo.db people table."""
    conn, cursor = init_db()
    try:
        cursor.execute(query)
        conn.commit()
        return True
    except sqlite3.Error as e:
        print(f"Error adding data: {e}")
        return False
    finally:
        conn.close()

@mcp.tool()
def read_data(query: str = "SELECT * FROM people") -> list:
    """Read data from demo.db people table."""
    conn, cursor = init_db()
    try:
        cursor.execute(query)
        return cursor.fetchall()
    except sqlite3.Error as e:
        print(f"Error reading data: {e}")
        return []
    finally:
        conn.close()

# =============================================
# ADVANCED FILE OPERATIONS
# (list_files, delete_file, copy_file, move_file, get_file_info)
# =============================================

@mcp.tool()
def list_files(directory: str = ".") -> List[Dict[str, Any]]:
    """List all files in a directory with detailed metadata."""
    abs_path = directory if os.path.isabs(directory) else os.path.join(_base_dir, directory)
    if not os.path.exists(abs_path):
        return [{"error": f"Directory not found: {abs_path}"}]
    
    files_info = []
    try:
        for item in os.listdir(abs_path):
            item_path = os.path.join(abs_path, item)
            stat_info = os.stat(item_path)
            files_info.append({
                "name": item,
                "path": item_path,
                "is_file": os.path.isfile(item_path),
                "is_directory": os.path.isdir(item_path),
                "size": stat_info.st_size,
                "modified": datetime.fromtimestamp(stat_info.st_mtime).isoformat(),
                "created": datetime.fromtimestamp(stat_info.st_ctime).isoformat(),
                "permissions": oct(stat_info.st_mode)[-3:]
            })
        return sorted(files_info, key=lambda x: x["name"])
    except Exception as e:
        return [{"error": f"Error listing files: {str(e)}"}]

# (Keep all other advanced tools: delete_file, copy_file, move_file, get_file_info,
# create_directory, remove_directory, list_directory_tree, analyze_python_code,
# count_lines_of_code, find_in_files, read/write CSV/JSON, full SQLite CRUD, etc.)
# I’ll skip repeating them here since they remain unchanged from your main2.py.

# =============================================
# UTILITY FUNCTIONS
# =============================================

def _format_bytes(bytes_value: int) -> str:
    for unit in ['B', 'KB', 'MB', 'GB', 'TB']:
        if bytes_value < 1024.0:
            return f"{bytes_value:.1f} {unit}"
        bytes_value /= 1024.0
    return f"{bytes_value:.1f} PB"

def _analyze_json_structure(data) -> Dict[str, Any]:
    if isinstance(data, dict):
        return {"type": "object", "keys_count": len(data), "keys": list(data.keys())[:10]}
    elif isinstance(data, list):
        return {"type": "array", "length": len(data), "item_types": list(set(type(item).__name__ for item in data[:100]))}
    else:
        return {"type": type(data).__name__, "value": str(data)[:100]}

# =============================================
# MAIN ENTRYPOINT
# =============================================

if __name__ == "__main__":
    print("🚀 Unified Advanced MCP Server started.")
    parser = argparse.ArgumentParser()
    parser.add_argument("--server_type", type=str, default="sse", choices=["sse", "stdio"])
    args = parser.parse_args()
    mcp.run(args.server_type)
