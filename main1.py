"""
Enhanced FastMCP server with improved error handling, logging, and additional features.
Run with:
    uv run server fastmcp_quickstart stdio
"""

from mcp.server.fastmcp import FastMCP
import os
import pdfplumber
from PIL import Image as PILImage
import io
import base64
import logging
from datetime import datetime
from typing import Optional, List
import json
from pathlib import Path

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('mcp_server.log'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

# Create an MCP server
mcp = FastMCP("Enhanced Demo Server")

# Configuration
class Config:
    BASE_DIR = Path(__file__).parent
    NOTES_FILE = BASE_DIR / "Notes.txt"
    TEXT_FILE = BASE_DIR / "New.txt" 
    PDF_FILE = BASE_DIR / "Tendernotice_1.pdf"
    IMAGE_FILE = BASE_DIR / "imgg.png"
    MAX_FILE_SIZE = 10 * 1024 * 1024  # 10MB
    THUMBNAIL_SIZE = (150, 150)  # Improved thumbnail size
    SUPPORTED_IMAGE_FORMATS = {'.png', '.jpg', '.jpeg', '.bmp', '.gif', '.tiff'}

def ensure_file(path: Path, create_dirs: bool = True) -> bool:
    """
    Ensure a file exists, optionally creating parent directories.
    Returns True if file exists or was created successfully.
    """
    try:
        if create_dirs:
            path.parent.mkdir(parents=True, exist_ok=True)
        
        if not path.exists():
            path.write_text("", encoding="utf-8")
            logger.info(f"Created new file: {path}")
        return True
    except Exception as e:
        logger.error(f"Failed to ensure file {path}: {e}")
        return False

def validate_file_size(path: Path) -> bool:
    """Check if file size is within acceptable limits."""
    try:
        return path.stat().st_size <= Config.MAX_FILE_SIZE
    except Exception:
        return False

def get_file_info(path: Path) -> dict:
    """Get file metadata information."""
    try:
        stat = path.stat()
        return {
            "exists": True,
            "size": stat.st_size,
            "modified": datetime.fromtimestamp(stat.st_mtime).isoformat(),
            "readable": os.access(path, os.R_OK),
            "writable": os.access(path, os.W_OK)
        }
    except Exception as e:
        return {"exists": False, "error": str(e)}

# ---------------- ENHANCED TOOLS ---------------- #

@mcp.tool()
def add_notes(message: str, add_timestamp: bool = True) -> str:
    """
    Append a note to Notes.txt with optional timestamp.
    
    Args:
        message: The note content to add
        add_timestamp: Whether to prepend timestamp (default: True)
    """
    try:
        if not message.strip():
            return "Error: Cannot add empty note"
        
        if not ensure_file(Config.NOTES_FILE):
            return "Error: Could not create notes file"
        
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        formatted_message = f"[{timestamp}] {message}" if add_timestamp else message
        
        with open(Config.NOTES_FILE, "a", encoding="utf-8") as f:
            f.write(formatted_message + "\n")
        
        logger.info(f"Added note: {message[:50]}...")
        return f"✓ Note saved successfully: {message[:100]}{'...' if len(message) > 100 else ''}"
    
    except Exception as e:
        logger.error(f"Failed to add note: {e}")
        return f"Error adding note: {str(e)}"

@mcp.tool()
def read_notes(limit: int = 10) -> str:
    """
    Read the most recent notes from Notes.txt.
    
    Args:
        limit: Maximum number of recent notes to return (default: 10)
    """
    try:
        if not Config.NOTES_FILE.exists():
            return "No notes file found"
        
        with open(Config.NOTES_FILE, "r", encoding="utf-8") as f:
            lines = [line.strip() for line in f if line.strip()]
        
        if not lines:
            return "No notes found"
        
        recent_notes = lines[-limit:] if limit > 0 else lines
        return "\n".join(recent_notes)
    
    except Exception as e:
        logger.error(f"Failed to read notes: {e}")
        return f"Error reading notes: {str(e)}"

@mcp.tool()
def search_notes(query: str) -> str:
    """
    Search for notes containing the specified query.
    
    Args:
        query: Search term to look for in notes
    """
    try:
        if not query.strip():
            return "Error: Search query cannot be empty"
        
        if not Config.NOTES_FILE.exists():
            return "No notes file found"
        
        with open(Config.NOTES_FILE, "r", encoding="utf-8") as f:
            lines = [line.strip() for line in f if line.strip()]
        
        matches = [line for line in lines if query.lower() in line.lower()]
        
        if not matches:
            return f"No notes found containing '{query}'"
        
        return f"Found {len(matches)} notes containing '{query}':\n" + "\n".join(matches)
    
    except Exception as e:
        logger.error(f"Failed to search notes: {e}")
        return f"Error searching notes: {str(e)}"

@mcp.tool()
def read_pdf(extract_metadata: bool = False) -> str:
    """
    Read and return text from PDF file with optional metadata.
    
    Args:
        extract_metadata: Whether to include PDF metadata (default: False)
    """
    try:
        if not Config.PDF_FILE.exists():
            return "PDF file not found"
        
        if not validate_file_size(Config.PDF_FILE):
            return "Error: PDF file too large"
        
        result = []
        
        with pdfplumber.open(Config.PDF_FILE) as pdf:
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
        
        logger.info(f"Successfully read PDF with {len(pdf.pages)} pages")
        return "".join(result)
    
    except Exception as e:
        logger.error(f"Failed to read PDF: {e}")
        return f"Error reading PDF: {str(e)}"

@mcp.tool()
def read_txt() -> str:
    """Read and return text from New.txt with file info."""
    try:
        if not ensure_file(Config.TEXT_FILE):
            return "Error: Could not access text file"
        
        with open(Config.TEXT_FILE, "r", encoding="utf-8") as f:
            content = f.read().strip()
        
        if not content:
            return "Text file exists but is empty"
        
        word_count = len(content.split())
        char_count = len(content)
        
        return f"Content ({word_count} words, {char_count} characters):\n\n{content}"
    
    except Exception as e:
        logger.error(f"Failed to read text file: {e}")
        return f"Error reading text file: {str(e)}"

@mcp.tool()
def write_txt(content: str, append: bool = False) -> str:
    """
    Write or append content to New.txt.
    
    Args:
        content: Text content to write
        append: Whether to append (True) or overwrite (False)
    """
    try:
        if not ensure_file(Config.TEXT_FILE):
            return "Error: Could not create text file"
        
        mode = "a" if append else "w"
        with open(Config.TEXT_FILE, mode, encoding="utf-8") as f:
            if append:
                f.write("\n" + content)
            else:
                f.write(content)
        
        action = "appended to" if append else "written to"
        logger.info(f"Content {action} text file")
        return f"✓ Content successfully {action} New.txt"
    
    except Exception as e:
        logger.error(f"Failed to write to text file: {e}")
        return f"Error writing to text file: {str(e)}"

@mcp.tool()
def create_thumbnail(image_path: str, size: str = "150x150") -> str:
    """
    Create a thumbnail from an image and return as base64-encoded PNG.
    
    Args:
        image_path: Path to the image file (relative or absolute)
        size: Thumbnail size in format "WIDTHxHEIGHT" (default: "150x150")
    """
    try:
        # Parse size
        try:
            width, height = map(int, size.split('x'))
            if width <= 0 or height <= 0 or width > 1000 or height > 1000:
                return "Error: Invalid size. Use format 'WIDTHxHEIGHT' with values 1-1000"
        except ValueError:
            return "Error: Invalid size format. Use 'WIDTHxHEIGHT' (e.g., '150x150')"
        
        # Resolve path
        if os.path.isabs(image_path):
            abs_path = Path(image_path)
        else:
            abs_path = Config.BASE_DIR / image_path
        
        if not abs_path.exists():
            return f"Error: Image file not found: {abs_path}"
        
        # Check file extension
        if abs_path.suffix.lower() not in Config.SUPPORTED_IMAGE_FORMATS:
            return f"Error: Unsupported image format. Supported: {', '.join(Config.SUPPORTED_IMAGE_FORMATS)}"
        
        if not validate_file_size(abs_path):
            return "Error: Image file too large"
        
        # Create thumbnail
        with PILImage.open(abs_path) as img:
            # Convert to RGB if necessary (for PNG with transparency)
            if img.mode in ('RGBA', 'LA', 'P'):
                img = img.convert('RGB')
            
            img.thumbnail((width, height), PILImage.Resampling.LANCZOS)
            
            buffer = io.BytesIO()
            img.save(buffer, format="PNG", optimize=True)
            base64_str = base64.b64encode(buffer.getvalue()).decode("utf-8")
            
            logger.info(f"Created thumbnail for {abs_path.name} ({img.size[0]}x{img.size[1]})")
            return f"data:image/png;base64,{base64_str}"
    
    except Exception as e:
        logger.error(f"Failed to create thumbnail: {e}")
        return f"Error creating thumbnail: {str(e)}"

@mcp.tool()
def get_file_status() -> str:
    """Get status information for all managed files."""
    try:
        files_info = {
            "Notes.txt": get_file_info(Config.NOTES_FILE),
            "New.txt": get_file_info(Config.TEXT_FILE),
            "PDF": get_file_info(Config.PDF_FILE),
            "Image": get_file_info(Config.IMAGE_FILE)
        }
        
        return json.dumps(files_info, indent=2)
    
    except Exception as e:
        logger.error(f"Failed to get file status: {e}")
        return f"Error getting file status: {str(e)}"

# ---------------- ENHANCED RESOURCES ---------------- #

@mcp.resource("notes://latest")
def get_latest_note() -> str:
    """Expose the latest note as a resource."""
    try:
        if not ensure_file(Config.NOTES_FILE):
            return "No notes file available"
        
        with open(Config.NOTES_FILE, "r", encoding="utf-8") as f:
            lines = [line.strip() for line in f if line.strip()]
        
        return lines[-1] if lines else "No notes found"
    
    except Exception as e:
        logger.error(f"Failed to get latest note: {e}")
        return f"Error: {str(e)}"

@mcp.resource("files://status")
def get_files_status() -> str:
    """Expose file status information as a resource."""
    return get_file_status()

# ---------------- ENHANCED PROMPTS ---------------- #

@mcp.prompt("text_summary")
def text_summary() -> str:
    """Provide a summarization-ready prompt with enhanced context."""
    try:
        if not ensure_file(Config.TEXT_FILE):
            return "No content file available for summarization."
        
        with open(Config.TEXT_FILE, "r", encoding="utf-8") as f:
            content = f.read().strip()
        
        if not content:
            return "No content found to summarize in New.txt"
        
        word_count = len(content.split())
        
        return f"""Please provide a comprehensive summary of the following text:

Text Statistics:
- Word count: {word_count}
- Character count: {len(content)}

Content:
{content}

Please include:
1. Main topics and themes
2. Key points and takeaways
3. Overall structure and flow
"""
    
    except Exception as e:
        logger.error(f"Failed to create summary prompt: {e}")
        return f"Error creating summary prompt: {str(e)}"

@mcp.prompt("analyze_notes")
def analyze_notes() -> str:
    """Provide a prompt for analyzing all notes."""
    try:
        if not Config.NOTES_FILE.exists():
            return "No notes available for analysis."
        
        with open(Config.NOTES_FILE, "r", encoding="utf-8") as f:
            lines = [line.strip() for line in f if line.strip()]
        
        if not lines:
            return "No notes found for analysis."
        
        return f"""Please analyze the following collection of {len(lines)} notes:

{chr(10).join(lines)}

Please provide:
1. Common themes and patterns
2. Chronological trends (if timestamps are present)
3. Key insights and observations
4. Suggestions for organization or follow-up actions
"""
    
    except Exception as e:
        logger.error(f"Failed to create notes analysis prompt: {e}")
        return f"Error creating analysis prompt: {str(e)}"

# ---------------- MAIN ---------------- #

def main():
    """Main entry point with startup logging."""
    logger.info("Starting Enhanced FastMCP Server")
    logger.info(f"Base directory: {Config.BASE_DIR}")
    
    # Ensure all files exist
    for file_path in [Config.NOTES_FILE, Config.TEXT_FILE]:
        ensure_file(file_path)
    
    # Log file status
    logger.info("File status check:")
    for name, path in [
        ("Notes", Config.NOTES_FILE),
        ("Text", Config.TEXT_FILE), 
        ("PDF", Config.PDF_FILE),
        ("Image", Config.IMAGE_FILE)
    ]:
        status = "exists" if path.exists() else "missing"
        logger.info(f"  {name}: {status}")
    
    logger.info("Server ready - available tools: add_notes, read_notes, search_notes, read_pdf, read_txt, write_txt, create_thumbnail, get_file_status")
    mcp.run()

if __name__ == "__main__":
    main()