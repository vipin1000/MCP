# MCP Demo Server with Claude Integration

**Project Owner:** Vipin Ruhal

## About This Demo

This is a demonstration environment showcasing the Model Context Protocol (MCP) server integrated with Claude Sonnet 4, an AI assistant created by Anthropic. This setup provides a powerful combination of file management capabilities and AI assistance.

## What is Claude?

I'm Claude Sonnet 4, a smart and efficient AI model designed for everyday use. I can help with:

- **Code Development**: Writing, reviewing, and debugging code in multiple programming languages
- **Data Analysis**: Processing CSVs, creating visualizations, and extracting insights
- **Creative Writing**: Stories, essays, poems, and other imaginative content  
- **Technical Documentation**: Clear explanations of complex concepts
- **Problem Solving**: Breaking down complex tasks into manageable steps
- **File Management**: Reading, writing, and organizing your project files

## Server Capabilities

This MCP server provides the following tools:

### Core File Operations
- **read_code()**: Safely read any file in the project directory
- **write_code()**: Atomically write content to files with proper error handling

### Enhanced Features
- **Notes Management**: Add, search, and retrieve notes from Notes.txt
- **Document Processing**: Read PDF and text files
- **Image Processing**: Create thumbnails and process image files
- **File Status**: Monitor file sizes, modification dates, and permissions

### Safety Features
- Thread-safe file operations with locks
- Atomic file writes using temporary files
- Automatic directory creation
- Comprehensive error handling

## Getting Started

1. The server runs on FastMCP framework
2. All file operations are relative to the project directory
3. Files are processed safely with proper encoding (UTF-8)
4. Logs provide metadata without exposing sensitive content

## File Structure

- `main.py` - Core MCP server setup and basic file operations
- `Notes.txt` - Persistent note storage (3KB+)
- `New.txt` - General text file storage (24KB+) 
- `PDF` - Document storage (1MB+)
- `Image` - Image file storage (2.3MB+)

## Working with Claude

I can help you:

1. **Analyze your codebase**: Understand structure, suggest improvements
2. **Debug issues**: Identify problems and propose solutions
3. **Create documentation**: Generate clear, helpful documentation
4. **Process data**: Work with your files to extract insights
5. **Automate tasks**: Create scripts and tools to streamline workflows

## Best Practices

- Use descriptive file names and organize content logically
- Keep notes updated for better searchability
- Utilize the atomic write operations for critical files
- Regular file status checks help monitor project health

## Support

This demo showcases the integration between MCP servers and AI assistants. For questions about:
- **Claude capabilities**: Ask me directly in our conversation
- **MCP protocol**: Check the official MCP documentation
- **Anthropic products**: Visit https://docs.anthropic.com

---

*This README was created by Claude Sonnet 4 to demonstrate AI-assisted documentation and project management capabilities.*