#!/usr/bin/env python3
"""
Minimal MCP Server - PDF Reader Only
Author: Vipin Ruhal
Description: Provides a single tool to read and extract text from PDF files.
"""

from mcp.server.fastmcp import FastMCP
import json
import pdfplumber
from pathlib import Path
import argparse

# Create MCP server
mcp = FastMCP("PDF Reader MCP Server")

BASE_DIR = Path(__file__).parent
PDF_FILE = BASE_DIR / "Tendernotice_1.pdf"

# =============================================
# PDF READING TOOL
# =============================================
@mcp.tool()
def read_pdf(extract_metadata: bool = False) -> str:
    """
    Read and return text from PDF file with optional metadata.
    
    Args:
        extract_metadata: Whether to include PDF metadata (default: False)
    """
   
        
    result = []
        
    with pdfplumber.open(PDF_FILE) as pdf:
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

# =============================================
# MAIN ENTRYPOINT
# =============================================
if __name__ == "__main__":
    print("🚀 Unified Advanced MCP Server started.")
    parser = argparse.ArgumentParser()
    parser.add_argument("--server_type", type=str, default="sse", choices=["sse", "stdio"])
    args = parser.parse_args()
    mcp.run(args.server_type)
