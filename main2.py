#!/usr/bin/env python3
"""
Advanced MCP Server - main2.py
Author: Vipin Ruhal
Description: Enhanced MCP server with advanced file operations, directory management,
code analysis, data processing, and database management capabilities.
"""

from mcp.server.fastmcp import FastMCP
import os
import shutil
import json
import csv
import sqlite3
import ast
import threading
from datetime import datetime
from typing import Dict, List, Any


# Create MCP server
mcp = FastMCP("Advanced Demo Server")

_base_dir = os.path.dirname(__file__)
_file_lock = threading.Lock()

# =============================================
# ADVANCED FILE OPERATIONS
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
            
            file_info = {
                "name": item,
                "path": item_path,
                "is_file": os.path.isfile(item_path),
                "is_directory": os.path.isdir(item_path),
                "size": stat_info.st_size,
                "modified": datetime.fromtimestamp(stat_info.st_mtime).isoformat(),
                "created": datetime.fromtimestamp(stat_info.st_ctime).isoformat(),
                "permissions": oct(stat_info.st_mode)[-3:]
            }
            files_info.append(file_info)
        
        return sorted(files_info, key=lambda x: x["name"])
    except Exception as e:
        return [{"error": f"Error listing files: {str(e)}"}]


@mcp.tool()
def delete_file(file_path: str) -> str:
    """Safely delete a file with confirmation."""
    abs_path = file_path if os.path.isabs(file_path) else os.path.join(_base_dir, file_path)
    
    if not os.path.exists(abs_path):
        return f"File not found: {abs_path}"
    
    if os.path.isdir(abs_path):
        return f"Cannot delete directory with delete_file. Use remove_directory instead."
    
    try:
        with _file_lock:
            os.remove(abs_path)
        return f"File deleted successfully: {abs_path}"
    except Exception as e:
        return f"Error deleting file: {str(e)}"


@mcp.tool()
def copy_file(source: str, destination: str) -> str:
    """Copy file from source to destination."""
    source_abs = source if os.path.isabs(source) else os.path.join(_base_dir, source)
    dest_abs = destination if os.path.isabs(destination) else os.path.join(_base_dir, destination)
    
    if not os.path.exists(source_abs):
        return f"Source file not found: {source_abs}"
    
    try:
        with _file_lock:
            os.makedirs(os.path.dirname(dest_abs), exist_ok=True)
            shutil.copy2(source_abs, dest_abs)
        return f"File copied successfully: {source_abs} -> {dest_abs}"
    except Exception as e:
        return f"Error copying file: {str(e)}"


@mcp.tool()
def move_file(source: str, destination: str) -> str:
    """Move/rename file from source to destination."""
    source_abs = source if os.path.isabs(source) else os.path.join(_base_dir, source)
    dest_abs = destination if os.path.isabs(destination) else os.path.join(_base_dir, destination)
    
    if not os.path.exists(source_abs):
        return f"Source file not found: {source_abs}"
    
    try:
        with _file_lock:
            os.makedirs(os.path.dirname(dest_abs), exist_ok=True)
            shutil.move(source_abs, dest_abs)
        return f"File moved successfully: {source_abs} -> {dest_abs}"
    except Exception as e:
        return f"Error moving file: {str(e)}"


@mcp.tool()
def get_file_info(file_path: str) -> Dict[str, Any]:
    """Get detailed file information."""
    abs_path = file_path if os.path.isabs(file_path) else os.path.join(_base_dir, file_path)
    
    if not os.path.exists(abs_path):
        return {"error": f"File not found: {abs_path}"}
    
    try:
        stat_info = os.stat(abs_path)
        return {
            "name": os.path.basename(abs_path),
            "path": abs_path,
            "size": stat_info.st_size,
            "size_human": _format_bytes(stat_info.st_size),
            "is_file": os.path.isfile(abs_path),
            "is_directory": os.path.isdir(abs_path),
            "modified": datetime.fromtimestamp(stat_info.st_mtime).isoformat(),
            "created": datetime.fromtimestamp(stat_info.st_ctime).isoformat(),
            "accessed": datetime.fromtimestamp(stat_info.st_atime).isoformat(),
            "permissions": oct(stat_info.st_mode)[-3:],
            "extension": os.path.splitext(abs_path)[1] if os.path.isfile(abs_path) else None
        }
    except Exception as e:
        return {"error": f"Error getting file info: {str(e)}"}


# =============================================
# DIRECTORY MANAGEMENT
# =============================================

@mcp.tool()
def create_directory(dir_path: str) -> str:
    """Create a new directory (including parent directories)."""
    abs_path = dir_path if os.path.isabs(dir_path) else os.path.join(_base_dir, dir_path)
    
    try:
        os.makedirs(abs_path, exist_ok=True)
        return f"Directory created successfully: {abs_path}"
    except Exception as e:
        return f"Error creating directory: {str(e)}"


@mcp.tool()
def remove_directory(dir_path: str, force: bool = False) -> str:
    """Remove a directory. Use force=True to remove non-empty directories."""
    abs_path = dir_path if os.path.isabs(dir_path) else os.path.join(_base_dir, dir_path)
    
    if not os.path.exists(abs_path):
        return f"Directory not found: {abs_path}"
    
    if not os.path.isdir(abs_path):
        return f"Path is not a directory: {abs_path}"
    
    try:
        if force:
            shutil.rmtree(abs_path)
        else:
            os.rmdir(abs_path)
        return f"Directory removed successfully: {abs_path}"
    except OSError as e:
        if not force and "Directory not empty" in str(e):
            return f"Directory not empty. Use force=True to remove non-empty directory: {abs_path}"
        return f"Error removing directory: {str(e)}"


@mcp.tool()
def list_directory_tree(path: str = ".", max_depth: int = 3) -> str:
    """Show directory structure as a tree."""
    abs_path = path if os.path.isabs(path) else os.path.join(_base_dir, path)
    
    if not os.path.exists(abs_path):
        return f"Path not found: {abs_path}"
    
    def _build_tree(directory, prefix="", depth=0):
        if depth > max_depth:
            return ""
        
        tree_str = ""
        try:
            items = sorted(os.listdir(directory))
            for i, item in enumerate(items):
                item_path = os.path.join(directory, item)
                is_last = i == len(items) - 1
                
                current_prefix = "└── " if is_last else "├── "
                tree_str += f"{prefix}{current_prefix}{item}\n"
                
                if os.path.isdir(item_path) and depth < max_depth:
                    extension = "    " if is_last else "│   "
                    tree_str += _build_tree(item_path, prefix + extension, depth + 1)
        except PermissionError:
            tree_str += f"{prefix}[Permission Denied]\n"
        
        return tree_str
    
    tree = f"{os.path.basename(abs_path) or abs_path}\n"
    tree += _build_tree(abs_path)
    return tree


# =============================================
# CODE ANALYSIS & PROCESSING
# =============================================

@mcp.tool()
def analyze_python_code(file_path: str) -> Dict[str, Any]:
    """Analyze Python code for functions, classes, imports, and complexity."""
    abs_path = file_path if os.path.isabs(file_path) else os.path.join(_base_dir, file_path)
    
    if not os.path.exists(abs_path):
        return {"error": f"File not found: {abs_path}"}
    
    try:
        with open(abs_path, 'r', encoding='utf-8') as f:
            content = f.read()
        
        tree = ast.parse(content)
        
        analysis = {
            "file_path": abs_path,
            "total_lines": len(content.splitlines()),
            "functions": [],
            "classes": [],
            "imports": [],
            "global_variables": [],
            "complexity_score": 0
        }
        
        for node in ast.walk(tree):
            if isinstance(node, ast.FunctionDef):
                analysis["functions"].append({
                    "name": node.name,
                    "line_number": node.lineno,
                    "args_count": len(node.args.args),
                    "has_docstring": ast.get_docstring(node) is not None
                })
            
            elif isinstance(node, ast.ClassDef):
                methods = [n.name for n in node.body if isinstance(n, ast.FunctionDef)]
                analysis["classes"].append({
                    "name": node.name,
                    "line_number": node.lineno,
                    "methods": methods,
                    "method_count": len(methods),
                    "has_docstring": ast.get_docstring(node) is not None
                })
            
            elif isinstance(node, ast.Import):
                for alias in node.names:
                    analysis["imports"].append({
                        "type": "import",
                        "name": alias.name,
                        "alias": alias.asname,
                        "line_number": node.lineno
                    })
            
            elif isinstance(node, ast.ImportFrom):
                for alias in node.names:
                    analysis["imports"].append({
                        "type": "from_import",
                        "module": node.module,
                        "name": alias.name,
                        "alias": alias.asname,
                        "line_number": node.lineno
                    })
            
            elif isinstance(node, ast.Assign) and isinstance(node.targets[0], ast.Name):
                # Global variable assignment (simplified detection)
                if hasattr(node.targets[0], 'id'):
                    analysis["global_variables"].append({
                        "name": node.targets[0].id,
                        "line_number": node.lineno
                    })
        
        # Simple complexity calculation
        analysis["complexity_score"] = len(analysis["functions"]) + len(analysis["classes"]) * 2
        analysis["summary"] = {
            "functions_count": len(analysis["functions"]),
            "classes_count": len(analysis["classes"]),
            "imports_count": len(analysis["imports"]),
            "estimated_complexity": "Low" if analysis["complexity_score"] < 10 else "Medium" if analysis["complexity_score"] < 25 else "High"
        }
        
        return analysis
        
    except SyntaxError as e:
        return {"error": f"Syntax error in Python file: {str(e)}"}
    except Exception as e:
        return {"error": f"Error analyzing code: {str(e)}"}


@mcp.tool()
def count_lines_of_code(file_path: str) -> Dict[str, int]:
    """Count total lines, code lines, comment lines, and blank lines."""
    abs_path = file_path if os.path.isabs(file_path) else os.path.join(_base_dir, file_path)
    
    if not os.path.exists(abs_path):
        return {"error": f"File not found: {abs_path}"}
    
    try:
        with open(abs_path, 'r', encoding='utf-8') as f:
            lines = f.readlines()
        
        total_lines = len(lines)
        blank_lines = 0
        comment_lines = 0
        code_lines = 0
        
        for line in lines:
            stripped = line.strip()
            if not stripped:
                blank_lines += 1
            elif stripped.startswith('#'):
                comment_lines += 1
            else:
                code_lines += 1
        
        return {
            "file_path": abs_path,
            "total_lines": total_lines,
            "code_lines": code_lines,
            "comment_lines": comment_lines,
            "blank_lines": blank_lines,
            "code_percentage": round((code_lines / total_lines) * 100, 2) if total_lines > 0 else 0
        }
        
    except Exception as e:
        return {"error": f"Error counting lines: {str(e)}"}


@mcp.tool()
def find_in_files(search_term: str, directory: str = ".", file_extensions: List[str] = None) -> List[Dict[str, Any]]:
    """Search for text across multiple files."""
    abs_path = directory if os.path.isabs(directory) else os.path.join(_base_dir, directory)
    
    if not os.path.exists(abs_path):
        return [{"error": f"Directory not found: {abs_path}"}]
    
    if file_extensions is None:
        file_extensions = ['.py', '.txt', '.md', '.json', '.csv', '.js', '.html', '.css']
    
    results = []
    
    try:
        for root, dirs, files in os.walk(abs_path):
            for file in files:
                if any(file.endswith(ext) for ext in file_extensions):
                    file_path = os.path.join(root, file)
                    try:
                        with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
                            lines = f.readlines()
                        
                        matches = []
                        for line_num, line in enumerate(lines, 1):
                            if search_term.lower() in line.lower():
                                matches.append({
                                    "line_number": line_num,
                                    "line_content": line.strip(),
                                    "match_position": line.lower().find(search_term.lower())
                                })
                        
                        if matches:
                            results.append({
                                "file_path": file_path,
                                "matches_count": len(matches),
                                "matches": matches
                            })
                    
                    except Exception:
                        continue  # Skip files that can't be read
        
        return results
        
    except Exception as e:
        return [{"error": f"Error searching files: {str(e)}"}]


# =============================================
# DATA PROCESSING
# =============================================

import pdfplumber

@mcp.tool()
def read_pdf(file_path: str,extract_metadata: bool = False) -> dict:
    """
    Read and return text from PDF file with optional metadata.
    
    Args:
        extract_metadata: Whether to include PDF metadata (default: False)
    """
   
        
    result = []
    abs_path = os.path.join(_base_dir, file_path)    
    with pdfplumber.open(abs_path) as pdf:
        if extract_metadata and pdf.metadata:
                result.append(f"PDF Metadata: {json.dumps(pdf.metadata, indent=2, default=str)}\n")
            
        result.append(f"Total pages: {len(pdf.pages)}\n")
            
        text_content = ""
        for i, page in enumerate(pdf.pages, 1):
                page_text = page.extract_text() or ""
                if page_text.strip():
                    text_content += f"\n--- Page {i} ---\n{page_text}\n"        
        if text_content.strip():
                result.append(text_content)
        else:
                result.append("No readable text found in PDF")
        return "".join(result)
    return f"Error reading PDF: {str(e)}"





@mcp.tool()
def read_csv_file(file_path: str, delimiter: str = ",") -> Dict[str, Any]:
    """Read and parse CSV files with detailed information."""
    abs_path = file_path if os.path.isabs(file_path) else os.path.join(_base_dir, file_path)
    
    if not os.path.exists(abs_path):
        return {"error": f"File not found: {abs_path}"}
    
    try:
        with open(abs_path, 'r', encoding='utf-8') as f:
            # Detect delimiter if not specified
            if delimiter == ",":
                sample = f.read(1024)
                f.seek(0)
                sniffer = csv.Sniffer()
                try:
                    delimiter = sniffer.sniff(sample).delimiter
                except:
                    delimiter = ","
            
            reader = csv.DictReader(f, delimiter=delimiter)
            rows = list(reader)
        
        if not rows:
            return {"error": "CSV file is empty or has no data rows"}
        
        headers = list(rows[0].keys())
        
        # Analyze data types
        column_info = {}
        for header in headers:
            values = [row[header] for row in rows if row[header].strip()]
            column_info[header] = {
                "non_empty_count": len(values),
                "unique_count": len(set(values)),
                "sample_values": values[:5] if values else []
            }
        
        return {
            "file_path": abs_path,
            "row_count": len(rows),
            "column_count": len(headers),
            "headers": headers,
            "column_info": column_info,
            "data": rows[:100],  # Return first 100 rows
            "preview_note": f"Showing first 100 rows of {len(rows)} total rows" if len(rows) > 100 else "All rows shown"
        }
        
    except Exception as e:
        return {"error": f"Error reading CSV: {str(e)}"}


@mcp.tool()
def write_csv_file(file_path: str, data: List[Dict[str, Any]], delimiter: str = ",") -> str:
    """Write data to CSV file."""
    abs_path = file_path if os.path.isabs(file_path) else os.path.join(_base_dir, file_path)
    
    if not data:
        return "Error: No data provided to write"
    
    try:
        os.makedirs(os.path.dirname(abs_path), exist_ok=True)
        
        with _file_lock:
            with open(abs_path, 'w', newline='', encoding='utf-8') as f:
                if isinstance(data[0], dict):
                    writer = csv.DictWriter(f, fieldnames=data[0].keys(), delimiter=delimiter)
                    writer.writeheader()
                    writer.writerows(data)
                else:
                    writer = csv.writer(f, delimiter=delimiter)
                    writer.writerows(data)
        
        return f"CSV file written successfully: {abs_path} ({len(data)} rows)"
        
    except Exception as e:
        return f"Error writing CSV: {str(e)}"


@mcp.tool()
def read_json_file(file_path: str) -> Dict[str, Any]:
    """Read and parse JSON files."""
    abs_path = file_path if os.path.isabs(file_path) else os.path.join(_base_dir, file_path)
    
    if not os.path.exists(abs_path):
        return {"error": f"File not found: {abs_path}"}
    
    try:
        with open(abs_path, 'r', encoding='utf-8') as f:
            data = json.load(f)
        
        return {
            "file_path": abs_path,
            "data_type": type(data).__name__,
            "size_info": _analyze_json_structure(data),
            "data": data
        }
        
    except json.JSONDecodeError as e:
        return {"error": f"Invalid JSON format: {str(e)}"}
    except Exception as e:
        return {"error": f"Error reading JSON: {str(e)}"}


@mcp.tool()
def write_json_file(file_path: str, data: Any, indent: int = 2) -> str:
    """Write data to JSON file."""
    abs_path = file_path if os.path.isabs(file_path) else os.path.join(_base_dir, file_path)
    
    try:
        os.makedirs(os.path.dirname(abs_path), exist_ok=True)
        
        with _file_lock:
            with open(abs_path, 'w', encoding='utf-8') as f:
                json.dump(data, f, indent=indent, ensure_ascii=False, default=str)
        
        return f"JSON file written successfully: {abs_path}"
        
    except Exception as e:
        return f"Error writing JSON: {str(e)}"


# =============================================
# DATABASE MANAGEMENT (SQLite CRUD)
# =============================================

@mcp.tool()
def create_database(db_name: str) -> str:
    """Create a new SQLite database."""
    abs_path = db_name if os.path.isabs(db_name) else os.path.join(_base_dir, db_name)
    
    if not db_name.endswith('.db'):
        abs_path += '.db'
    
    try:
        conn = sqlite3.connect(abs_path)
        conn.close()
        return f"Database created successfully: {abs_path}"
    except Exception as e:
        return f"Error creating database: {str(e)}"


@mcp.tool()
def create_table(db_path: str, table_name: str, columns: Dict[str, str]) -> str:
    """Create a table in SQLite database. columns format: {'column_name': 'data_type'}"""
    abs_path = db_path if os.path.isabs(db_path) else os.path.join(_base_dir, db_path)
    
    if not os.path.exists(abs_path):
        return f"Database not found: {abs_path}"
    
    try:
        column_definitions = []
        for col_name, col_type in columns.items():
            column_definitions.append(f"{col_name} {col_type}")
        
        create_sql = f"CREATE TABLE IF NOT EXISTS {table_name} ({', '.join(column_definitions)})"
        
        conn = sqlite3.connect(abs_path)
        cursor = conn.cursor()
        cursor.execute(create_sql)
        conn.commit()
        conn.close()
        
        return f"Table '{table_name}' created successfully in {abs_path}"
    except Exception as e:
        return f"Error creating table: {str(e)}"


@mcp.tool()
def insert_data(db_path: str, table_name: str, data: Dict[str, Any]) -> str:
    """Insert data into database table."""
    abs_path = db_path if os.path.isabs(db_path) else os.path.join(_base_dir, db_path)
    
    if not os.path.exists(abs_path):
        return f"Database not found: {abs_path}"
    
    try:
        columns = list(data.keys())
        placeholders = ', '.join(['?' for _ in columns])
        values = list(data.values())
        
        insert_sql = f"INSERT INTO {table_name} ({', '.join(columns)}) VALUES ({placeholders})"
        
        conn = sqlite3.connect(abs_path)
        cursor = conn.cursor()
        cursor.execute(insert_sql, values)
        conn.commit()
        row_id = cursor.lastrowid
        conn.close()
        
        return f"Data inserted successfully into {table_name}. Row ID: {row_id}"
    except Exception as e:
        return f"Error inserting data: {str(e)}"


@mcp.tool()
def select_data(db_path: str, table_name: str, where_clause: str = None, limit: int = 100) -> Dict[str, Any]:
    """Select data from database table."""
    abs_path = db_path if os.path.isabs(db_path) else os.path.join(_base_dir, db_path)
    
    if not os.path.exists(abs_path):
        return {"error": f"Database not found: {abs_path}"}
    
    try:
        select_sql = f"SELECT * FROM {table_name}"
        if where_clause:
            select_sql += f" WHERE {where_clause}"
        select_sql += f" LIMIT {limit}"
        
        conn = sqlite3.connect(abs_path)
        conn.row_factory = sqlite3.Row  # This enables column access by name
        cursor = conn.cursor()
        cursor.execute(select_sql)
        
        rows = cursor.fetchall()
        columns = [description[0] for description in cursor.description]
        
        # Convert rows to list of dictionaries
        data = [dict(row) for row in rows]
        
        conn.close()
        
        return {
            "table_name": table_name,
            "columns": columns,
            "row_count": len(data),
            "data": data
        }
    except Exception as e:
        return {"error": f"Error selecting data: {str(e)}"}


@mcp.tool()
def update_data(db_path: str, table_name: str, set_clause: str, where_clause: str) -> str:
    """Update data in database table."""
    abs_path = db_path if os.path.isabs(db_path) else os.path.join(_base_dir, db_path)
    
    if not os.path.exists(abs_path):
        return f"Database not found: {abs_path}"
    
    try:
        update_sql = f"UPDATE {table_name} SET {set_clause} WHERE {where_clause}"
        
        conn = sqlite3.connect(abs_path)
        cursor = conn.cursor()
        cursor.execute(update_sql)
        rows_affected = cursor.rowcount
        conn.commit()
        conn.close()
        
        return f"Updated {rows_affected} rows in table '{table_name}'"
    except Exception as e:
        return f"Error updating data: {str(e)}"


@mcp.tool()
def delete_data(db_path: str, table_name: str, where_clause: str) -> str:
    """Delete data from database table."""
    abs_path = db_path if os.path.isabs(db_path) else os.path.join(_base_dir, db_path)
    
    if not os.path.exists(abs_path):
        return f"Database not found: {abs_path}"
    
    try:
        delete_sql = f"DELETE FROM {table_name} WHERE {where_clause}"
        
        conn = sqlite3.connect(abs_path)
        cursor = conn.cursor()
        cursor.execute(delete_sql)
        rows_affected = cursor.rowcount
        conn.commit()
        conn.close()
        
        return f"Deleted {rows_affected} rows from table '{table_name}'"
    except Exception as e:
        return f"Error deleting data: {str(e)}"


@mcp.tool()
def list_tables(db_path: str) -> List[Dict[str, Any]]:
    """List all tables in the database with their info."""
    abs_path = db_path if os.path.isabs(db_path) else os.path.join(_base_dir, db_path)
    
    if not os.path.exists(abs_path):
        return [{"error": f"Database not found: {abs_path}"}]
    
    try:
        conn = sqlite3.connect(abs_path)
        cursor = conn.cursor()
        
        # Get table names
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name NOT LIKE 'sqlite_%'")
        tables = cursor.fetchall()
        
        table_info = []
        for (table_name,) in tables:
            # Get table info
            cursor.execute(f"PRAGMA table_info({table_name})")
            columns_info = cursor.fetchall()
            
            # Get row count
            cursor.execute(f"SELECT COUNT(*) FROM {table_name}")
            row_count = cursor.fetchone()[0]
            
            table_info.append({
                "table_name": table_name,
                "row_count": row_count,
                "columns": [{"name": col[1], "type": col[2], "not_null": bool(col[3]), "primary_key": bool(col[5])} for col in columns_info]
            })
        
        conn.close()
        return table_info
    except Exception as e:
        return [{"error": f"Error listing tables: {str(e)}"}]


# =============================================
# UTILITY FUNCTIONS
# =============================================

def _format_bytes(bytes_value: int) -> str:
    """Convert bytes to human readable format."""
    for unit in ['B', 'KB', 'MB', 'GB', 'TB']:
        if bytes_value < 1024.0:
            return f"{bytes_value:.1f} {unit}"
        bytes_value /= 1024.0
    return f"{bytes_value:.1f} PB"


def _analyze_json_structure(data) -> Dict[str, Any]:
    """Analyze JSON data structure."""
    if isinstance(data, dict):
        return {
            "type": "object",
            "keys_count": len(data),
            "keys": list(data.keys())[:10]  # First 10 keys
        }
    elif isinstance(data, list):
        return {
            "type": "array",
            "length": len(data),
            "item_types": list(set(type(item).__name__ for item in data[:100]))  # Types of first 100 items
        }
    else:
        return {
            "type": type(data).__name__,
            "value": str(data)[:100]  # First 100 characters
        }


if __name__ == "__main__":
    print("Advanced MCP Server - main2.py")
    print("Author: Vipin Ruhal")
    print("Server ready with advanced file operations, directory management,")
    print("code analysis, data processing, and database management capabilities.")
