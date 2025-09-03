
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

# from mcp.server.fastmcp import FastMCP
# import os
# import shutil
# import json
# import csv
# import sqlite3
# import ast
# import threading
# import argparse
# from datetime import datetime
# from typing import Dict, List, Any

# # Create MCP server
# mcp = FastMCP("Unified Advanced MCP Server")

# _base_dir = os.path.dirname(__file__)
# _file_lock = threading.Lock()

# # =============================================
# # DEMO SQLITE TOOLS (demo.db)
# # =============================================

# def init_db():
#     conn = sqlite3.connect("demo.db")
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

# # @mcp.tool()
# # def add_data(query: str) -> bool:
# #     """Add new data to the demo.db people table."""
# #     conn, cursor = init_db()
# #     try:
# #         cursor.execute(query)
# #         conn.commit()
# #         return True
# #     except sqlite3.Error as e:
# #         print(f"Error adding data: {e}")
# #         return False
# #     finally:
# #         conn.close()
# @mcp.tool()
# def add_data(query: str) -> dict:
#     """Add new data to the demo.db people table."""
#     conn, cursor = init_db()
#     try:
#         cursor.execute(query)
#         conn.commit()
#         return {"success": True}
#     except sqlite3.Error as e:
#         print(f"Error adding data: {e}")
#         return {"success": False, "error": str(e)}
#     finally:
#         conn.close()

# @mcp.tool()
# def read_data(query: str = "SELECT * FROM people") -> list:
#     """Read data from demo.db people table."""
#     conn, cursor = init_db()
#     try:
#         cursor.execute(query)
#         return cursor.fetchall()
#     except sqlite3.Error as e:
#         print(f"Error reading data: {e}")
#         return []
#     finally:
#         conn.close()

# # =============================================
# # ADVANCED FILE OPERATIONS
# # =============================================

# @mcp.tool()
# def list_files(directory: str = ".") -> List[Dict[str, Any]]:
#     """List all files in a directory with detailed metadata."""
#     abs_path = directory if os.path.isabs(directory) else os.path.join(_base_dir, directory)
#     if not os.path.exists(abs_path):
#         return [{"error": f"Directory not found: {abs_path}"}]
    
#     files_info = []
#     try:
#         for item in os.listdir(abs_path):
#             item_path = os.path.join(abs_path, item)
#             stat_info = os.stat(item_path)
#             files_info.append({
#                 "name": item,
#                 "path": item_path,
#                 "is_file": os.path.isfile(item_path),
#                 "is_directory": os.path.isdir(item_path),
#                 "size": stat_info.st_size,
#                 "modified": datetime.fromtimestamp(stat_info.st_mtime).isoformat(),
#                 "created": datetime.fromtimestamp(stat_info.st_ctime).isoformat(),
#                 "permissions": oct(stat_info.st_mode)[-3:]
#             })
#         return sorted(files_info, key=lambda x: x["name"])
#     except Exception as e:
#         return [{"error": f"Error listing files: {str(e)}"}]

# @mcp.tool()
# def delete_file(file_path: str) -> str:
#     """Safely delete a file with confirmation."""
#     abs_path = file_path if os.path.isabs(file_path) else os.path.join(_base_dir, file_path)
#     if not os.path.exists(abs_path):
#         return f"File not found: {abs_path}"
#     if os.path.isdir(abs_path):
#         return f"Cannot delete directory with delete_file. Use remove_directory instead."
#     try:
#         with _file_lock:
#             os.remove(abs_path)
#         return f"File deleted successfully: {abs_path}"
#     except Exception as e:
#         return f"Error deleting file: {str(e)}"

# @mcp.tool()
# def copy_file(source: str, destination: str) -> str:
#     """Copy file from source to destination."""
#     source_abs = source if os.path.isabs(source) else os.path.join(_base_dir, source)
#     dest_abs = destination if os.path.isabs(destination) else os.path.join(_base_dir, destination)
#     if not os.path.exists(source_abs):
#         return f"Source file not found: {source_abs}"
#     try:
#         with _file_lock:
#             os.makedirs(os.path.dirname(dest_abs), exist_ok=True)
#             shutil.copy2(source_abs, dest_abs)
#         return f"File copied successfully: {source_abs} -> {dest_abs}"
#     except Exception as e:
#         return f"Error copying file: {str(e)}"

# @mcp.tool()
# def move_file(source: str, destination: str) -> str:
#     """Move/rename file from source to destination."""
#     source_abs = source if os.path.isabs(source) else os.path.join(_base_dir, source)
#     dest_abs = destination if os.path.isabs(destination) else os.path.join(_base_dir, destination)
#     if not os.path.exists(source_abs):
#         return f"Source file not found: {source_abs}"
#     try:
#         with _file_lock:
#             os.makedirs(os.path.dirname(dest_abs), exist_ok=True)
#             shutil.move(source_abs, dest_abs)
#         return f"File moved successfully: {source_abs} -> {dest_abs}"
#     except Exception as e:
#         return f"Error moving file: {str(e)}"

# @mcp.tool()
# def get_file_info(file_path: str) -> Dict[str, Any]:
#     """Get detailed file information."""
#     abs_path = file_path if os.path.isabs(file_path) else os.path.join(_base_dir, file_path)
#     if not os.path.exists(abs_path):
#         return {"error": f"File not found: {abs_path}"}
#     try:
#         stat_info = os.stat(abs_path)
#         return {
#             "name": os.path.basename(abs_path),
#             "path": abs_path,
#             "size": stat_info.st_size,
#             "is_file": os.path.isfile(abs_path),
#             "is_directory": os.path.isdir(abs_path),
#             "modified": datetime.fromtimestamp(stat_info.st_mtime).isoformat(),
#             "created": datetime.fromtimestamp(stat_info.st_ctime).isoformat(),
#             "accessed": datetime.fromtimestamp(stat_info.st_atime).isoformat(),
#             "permissions": oct(stat_info.st_mode)[-3:],
#             "extension": os.path.splitext(abs_path)[1] if os.path.isfile(abs_path) else None
#         }
#     except Exception as e:
#         return {"error": f"Error getting file info: {str(e)}"}

# # =============================================
# # DIRECTORY MANAGEMENT
# # =============================================

# @mcp.tool()
# def create_directory(dir_path: str) -> str:
#     """Create a new directory (including parent directories)."""
#     abs_path = dir_path if os.path.isabs(dir_path) else os.path.join(_base_dir, dir_path)
#     try:
#         os.makedirs(abs_path, exist_ok=True)
#         return f"Directory created successfully: {abs_path}"
#     except Exception as e:
#         return f"Error creating directory: {str(e)}"

# @mcp.tool()
# def remove_directory(dir_path: str, force: bool = False) -> str:
#     """Remove a directory. Use force=True to remove non-empty directories."""
#     abs_path = dir_path if os.path.isabs(dir_path) else os.path.join(_base_dir, dir_path)
#     if not os.path.exists(abs_path):
#         return f"Directory not found: {abs_path}"
#     if not os.path.isdir(abs_path):
#         return f"Path is not a directory: {abs_path}"
#     try:
#         if force:
#             shutil.rmtree(abs_path)
#         else:
#             os.rmdir(abs_path)
#         return f"Directory removed successfully: {abs_path}"
#     except Exception as e:
#         return f"Error removing directory: {str(e)}"

# @mcp.tool()
# def list_directory_tree(path: str = ".", max_depth: int = 3) -> str:
#     """Show directory structure as a tree."""
#     abs_path = path if os.path.isabs(path) else os.path.join(_base_dir, path)
#     if not os.path.exists(abs_path):
#         return f"Path not found: {abs_path}"
#     def _build_tree(directory, prefix="", depth=0):
#         if depth > max_depth:
#             return ""
#         tree_str = ""
#         try:
#             items = sorted(os.listdir(directory))
#             for i, item in enumerate(items):
#                 item_path = os.path.join(directory, item)
#                 is_last = i == len(items) - 1
#                 current_prefix = "└── " if is_last else "├── "
#                 tree_str += f"{prefix}{current_prefix}{item}\n"
#                 if os.path.isdir(item_path) and depth < max_depth:
#                     extension = "    " if is_last else "│   "
#                     tree_str += _build_tree(item_path, prefix + extension, depth + 1)
#         except PermissionError:
#             tree_str += f"{prefix}[Permission Denied]\n"
#         return tree_str
#     tree = f"{os.path.basename(abs_path) or abs_path}\n"
#     tree += _build_tree(abs_path)
#     return tree

# # =============================================
# # CODE ANALYSIS & PROCESSING
# # =============================================

# @mcp.tool()
# def analyze_python_code(file_path: str) -> Dict[str, Any]:
#     """Analyze Python code for functions, classes, imports, and complexity."""
#     abs_path = file_path if os.path.isabs(file_path) else os.path.join(_base_dir, file_path)
#     if not os.path.exists(abs_path):
#         return {"error": f"File not found: {abs_path}"}
#     try:
#         with open(abs_path, 'r', encoding='utf-8') as f:
#             content = f.read()
#         tree = ast.parse(content)
#         analysis = {
#             "file_path": abs_path,
#             "total_lines": len(content.splitlines()),
#             "functions": [],
#             "classes": [],
#             "imports": [],
#             "global_variables": [],
#             "complexity_score": 0
#         }
#         for node in ast.walk(tree):
#             if isinstance(node, ast.FunctionDef):
#                 analysis["functions"].append({
#                     "name": node.name,
#                     "line_number": node.lineno,
#                     "args_count": len(node.args.args),
#                     "has_docstring": ast.get_docstring(node) is not None
#                 })
#             elif isinstance(node, ast.ClassDef):
#                 methods = [n.name for n in node.body if isinstance(n, ast.FunctionDef)]
#                 analysis["classes"].append({
#                     "name": node.name,
#                     "line_number": node.lineno,
#                     "methods": methods,
#                     "method_count": len(methods),
#                     "has_docstring": ast.get_docstring(node) is not None
#                 })
#             elif isinstance(node, ast.Import):
#                 for alias in node.names:
#                     analysis["imports"].append({
#                         "type": "import",
#                         "name": alias.name,
#                         "alias": alias.asname,
#                         "line_number": node.lineno
#                     })
#             elif isinstance(node, ast.ImportFrom):
#                 for alias in node.names:
#                     analysis["imports"].append({
#                         "type": "from_import",
#                         "module": node.module,
#                         "name": alias.name,
#                         "alias": alias.asname,
#                         "line_number": node.lineno
#                     })
#             elif isinstance(node, ast.Assign) and isinstance(node.targets[0], ast.Name):
#                 analysis["global_variables"].append({
#                     "name": node.targets[0].id,
#                     "line_number": node.lineno
#                 })
#         analysis["complexity_score"] = len(analysis["functions"]) + len(analysis["classes"]) * 2
#         analysis["summary"] = {
#             "functions_count": len(analysis["functions"]),
#             "classes_count": len(analysis["classes"]),
#             "imports_count": len(analysis["imports"]),
#             "estimated_complexity": "Low" if analysis["complexity_score"] < 10 else "Medium" if analysis["complexity_score"] < 25 else "High"
#         }
#         return analysis
#     except Exception as e:
#         return {"error": f"Error analyzing code: {str(e)}"}

# @mcp.tool()
# def count_lines_of_code(file_path: str) -> Dict[str, int]:
#     """Count total lines, code lines, comment lines, and blank lines."""
#     abs_path = file_path if os.path.isabs(file_path) else os.path.join(_base_dir, file_path)
#     if not os.path.exists(abs_path):
#         return {"error": f"File not found: {abs_path}"}
#     try:
#         with open(abs_path, 'r', encoding='utf-8') as f:
#             lines = f.readlines()
#         total_lines = len(lines)
#         blank_lines = sum(1 for line in lines if not line.strip())
#         comment_lines = sum(1 for line in lines if line.strip().startswith('#'))
#         code_lines = total_lines - blank_lines - comment_lines
#         return {
#             "file_path": abs_path,
#             "total_lines": total_lines,
#             "code_lines": code_lines,
#             "comment_lines": comment_lines,
#             "blank_lines": blank_lines,
#             "code_percentage": round((code_lines / total_lines) * 100, 2) if total_lines > 0 else 0
#         }
#     except Exception as e:
#         return {"error": f"Error counting lines: {str(e)}"}

# @mcp.tool()
# def find_in_files(search_term: str, directory: str = ".", file_extensions: List[str] = None) -> List[Dict[str, Any]]:
#     """Search for text across multiple files."""
#     abs_path = directory if os.path.isabs(directory) else os.path.join(_base_dir, directory)
#     if not os.path.exists(abs_path):
#         return [{"error": f"Directory not found: {abs_path}"}]
#     if file_extensions is None:
#         file_extensions = ['.py', '.txt', '.md', '.json', '.csv', '.js', '.html', '.css']
#     results = []
#     try:
#         for root, _, files in os.walk(abs_path):
#             for file in files:
#                 if any(file.endswith(ext) for ext in file_extensions):
#                     file_path = os.path.join(root, file)
#                     try:
#                         with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
#                             lines = f.readlines()
#                         matches = []
#                         for line_num, line in enumerate(lines, 1):
#                             if search_term.lower() in line.lower():
#                                 matches.append({
#                                     "line_number": line_num,
#                                     "line_content": line.strip(),
#                                     "match_position": line.lower().find(search_term.lower())
#                                 })
#                         if matches:
#                             results.append({
#                                 "file_path": file_path,
#                                 "matches_count": len(matches),
#                                 "matches": matches
#                             })
#                     except Exception:
#                         continue
#         return results
#     except Exception as e:
#         return [{"error": f"Error searching files: {str(e)}"}]

# # =============================================
# # DATA PROCESSING
# # =============================================

# @mcp.tool()
# def read_csv_file(file_path: str, delimiter: str = ",") -> Dict[str, Any]:
#     """Read and parse CSV files with detailed information."""
#     abs_path = file_path if os.path.isabs(file_path) else os.path.join(_base_dir, file_path)
#     if not os.path.exists(abs_path):
#         return {"error": f"File not found: {abs_path}"}
#     try:
#         with open(abs_path, 'r', encoding='utf-8') as f:
#             if delimiter == ",":
#                 sample = f.read(1024)
#                 f.seek(0)
#                 try:
#                     delimiter = csv.Sniffer().sniff(sample).delimiter
#                 except:
#                     delimiter = ","
#             reader = csv.DictReader(f, delimiter=delimiter)
#             rows = list(reader)
#         if not rows:
#             return {"error": "CSV file is empty or has no data rows"}
#         headers = list(rows[0].keys())
#         column_info = {}
#         for header in headers:
#             values = [row[header] for row in rows if row[header].strip()]
#             column_info[header] = {
#                 "non_empty_count": len(values),
#                 "unique_count": len(set(values)),
#                 "sample_values": values[:5]
#             }
#         return {
#             "file_path": abs_path,
#             "row_count": len(rows),
#             "column_count": len(headers),
#             "headers": headers,
#             "column_info": column_info,
#             "data": rows[:100],
#             "preview_note": f"Showing first 100 rows of {len(rows)} total rows" if len(rows) > 100 else "All rows shown"
#         }
#     except Exception as e:
#         return {"error": f"Error reading CSV: {str(e)}"}

# @mcp.tool()
# def write_csv_file(file_path: str, data: List[Dict[str, Any]], delimiter: str = ",") -> str:
#     """Write data to CSV file."""
#     abs_path = file_path if os.path.isabs(file_path) else os.path.join(_base_dir, file_path)
#     if not data:
#         return "Error: No data provided to write"
#     try:
#         os.makedirs(os.path.dirname(abs_path), exist_ok=True)
#         with _file_lock:
#             with open(abs_path, 'w', newline='', encoding='utf-8') as f:
#                 if isinstance(data[0], dict):
#                     writer = csv.DictWriter(f, fieldnames=data[0].keys(), delimiter=delimiter)
#                     writer.writeheader()
#                     writer.writerows(data)
#                 else:
#                     writer = csv.writer(f, delimiter=delimiter)
#                     writer.writerows(data)
#         return f"CSV file written successfully: {abs_path} ({len(data)} rows)"
#     except Exception as e:
#         return f"Error writing CSV: {str(e)}"

# @mcp.tool()
# def read_json_file(file_path: str) -> Dict[str, Any]:
#     """Read and parse JSON files."""
#     abs_path = file_path if os.path.isabs(file_path) else os.path.join(_base_dir, file_path)
#     if not os.path.exists(abs_path):
#         return {"error": f"File not found: {abs_path}"}
#     try:
#         with open(abs_path, 'r', encoding='utf-8') as f:
#             data = json.load(f)
#         return {
#             "file_path": abs_path,
#             "data_type": type(data).__name__,  # e.g., 'dict' or 'list'
#             "content": data
#         }
#     except json.JSONDecodeError as e:
#         return {"error": f"Invalid JSON format: {str(e)}"}
#     except Exception as e:
#         return {"error": str(e)}

# @mcp.tool()
# def write_json_file(file_path: str, content: Any, indent: int = 4) -> Dict[str, Any]:
#     """Write data to a JSON file."""
#     abs_path = file_path if os.path.isabs(file_path) else os.path.join(_base_dir, file_path)
#     try:
#         with open(abs_path, 'w', encoding='utf-8') as f:
#             json.dump(content, f, ensure_ascii=False, indent=indent)
#         return {
#             "file_path": abs_path,
#             "status": "success",
#             "data_type": type(content).__name__
#         }
#     except TypeError as e:
#         return {"error": f"Content not serializable to JSON: {str(e)}"}
#     except Exception as e:
#         return {"error": str(e)}


# # =============================================
# # MAIN ENTRYPOINT
# # =============================================

# if __name__ == "__main__":
#     print("🚀 Unified Advanced MCP Server started.")
#     parser = argparse.ArgumentParser()
#     parser.add_argument("--server_type", type=str, default="sse", choices=["sse", "stdio"])
#     args = parser.parse_args()
#     mcp.run(args.server_type)




from mcp.server.fastmcp import FastMCP
import os
import pdfplumber
import json
import argparse
import requests
import duckduckgo_search
from bs4 import BeautifulSoup



mcp = FastMCP("PDFSummarizer")

_base_dir = os.path.dirname(__file__)
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
def scrape_url(url: str) -> str:
    """
    Fetch and return cleaned text content from a webpage.
    """
    try:
        resp = requests.get(url, timeout=10)
        resp.raise_for_status()

        soup = BeautifulSoup(resp.text, "html.parser")

        # Remove scripts and styles
        for s in soup(["script", "style", "noscript"]):
            s.extract()

        text = soup.get_text(separator="\n")
        lines = [line.strip() for line in text.splitlines() if line.strip()]
        return "\n".join(lines[:2000])  # limit size for LLM
    except Exception as e:
        return f"Error scraping {url}: {str(e)}"


# ----------------------------
# Web Search Tool
# ----------------------------
# @mcp.tool()
# def web_search(query: str, max_results: int = 5) -> str:
#     """
#     Perform a DuckDuckGo web search and return top results.
#     """
#     try:
#         results = duckduckgo_search.DDGS().text(query, max_results=max_results)
#         output = []
#         for i, r in enumerate(results, 1):
#             output.append(f"{i}. {r['title']} - {r['href']}\n{r['body']}\n")
#         return "\n".join(output)
#     except Exception as e:
#         return f"Error performing web search: {str(e)}"




















from urllib.parse import urljoin, urlparse
import chromadb
from sentence_transformers import SentenceTransformer



# Vector DB + embeddings
chroma_client = chromadb.PersistentClient(path="web_cache")
collection = chroma_client.get_or_create_collection("website_pages")
embedder = SentenceTransformer("all-MiniLM-L6-v2")


@mcp.tool()
def crawl_site(base_url: str, max_pages: int = 20, exclude_urls: list[str] = None) -> str:
    """
    Crawl a website starting from base_url and cache its text content in ChromaDB.
    
    Args:
        base_url (str): Homepage URL of the website to crawl.
        max_pages (int): Max number of pages to crawl (default: 20).
        exclude_urls (list[str]): List of substrings/URLs to skip.
    
    Returns:
        str: Number of pages successfully crawled and indexed.
    """
    if exclude_urls is None:
        exclude_urls = []

    visited, to_visit = set(), [base_url]
    parsed_base = urlparse(base_url).netloc

    while to_visit and len(visited) < max_pages:
        url = to_visit.pop(0)

        # Skip excluded
        if any(excl in url for excl in exclude_urls):
            continue

        if url in visited:
            continue
        try:
            resp = requests.get(url, timeout=10)
            resp.raise_for_status()
            soup = BeautifulSoup(resp.text, "html.parser")

            # Clean up HTML
            for s in soup(["script", "style", "noscript"]):
                s.extract()

            text = soup.get_text(separator="\n")
            lines = [line.strip() for line in text.splitlines() if line.strip()]
            content = "\n".join(lines)

            # Save into Chroma
            embedding = embedder.encode([content])[0]
            collection.add(
                documents=[content],
                embeddings=[embedding],
                ids=[url]
            )

            visited.add(url)

            # Collect new internal links
            for link in soup.find_all("a", href=True):
                full_url = urljoin(base_url, link["href"])
                if urlparse(full_url).netloc == parsed_base and full_url not in visited:
                    if not any(excl in full_url for excl in exclude_urls):
                        to_visit.append(full_url)

        except Exception as e:
            print(f"⚠️ Failed {url}: {e}")

    return f"Crawled and indexed {len(visited)} pages from {base_url}"


@mcp.tool()
def ask_site(question: str, top_k: int = 3) -> str:
    """
    Query across all crawled pages of the website.
    
    Args:
        question (str): The natural language question to ask.
        top_k (int): Number of top results to return (default: 3).
    
    Returns:
        str: Relevant content snippets from the website.
    """
    try:
        embedding = embedder.encode([question])[0]
        results = collection.query(
            query_embeddings=[embedding],
            n_results=top_k
        )
        docs = results["documents"]
        urls = results["ids"]

        # Format nicely
        output = []
        for i, (doc, url) in enumerate(zip(docs[0], urls[0])):
            snippet = doc[:500].replace("\n", " ")  # limit size
            output.append(f"[Result {i+1}] {url}\n{snippet}...\n")

        return "\n".join(output) if output else "No relevant content found."
    except Exception as e:
        return f"Error querying site: {str(e)}"

































































if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--server_type", type=str, default="sse", choices=["sse", "stdio"])
    args = parser.parse_args()
    mcp.run(args.server_type)

