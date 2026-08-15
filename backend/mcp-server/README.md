# Website Scraper MCP Server

An MCP (Model Context Protocol) server that takes a starting URL as input, recursively crawls all pages and subpages within the domain, and returns a structured JSON object containing page titles, metadata, headings, clean text content, and extracted links.

---

## Features

- **Recursive Subpage Crawling**: Automatically traverses internal subpages up to a configurable max depth and max page limit.
- **Domain Boundaries**: Restricts crawling to the same domain by default to prevent external site wandering.
- **Content Extraction**: Extracts HTML page title, meta description/keywords, structured headings (`h1`, `h2`, `h3`), and clean body text (excluding script/style elements).
- **Dual Runtime Support**: Complete implementations in both **Node.js** and **Python**.
- **MCP Tool Integration**: Standard `stdio` transport compatible with Claude Desktop, Cursor, Antigravity IDE, and custom agent frameworks.
- **Standalone CLI Runner**: Can also be executed directly from command line to output JSON files without an MCP client.

---

## JSON Output Structure

```json
{
  "base_url": "https://example.com",
  "scraped_at": "2026-08-15T13:47:00.000Z",
  "total_pages_scraped": 12,
  "options": {
    "max_pages": 50,
    "max_depth": 3,
    "include_external": false
  },
  "pages": [
    {
      "url": "https://example.com/",
      "depth": 0,
      "status": 200,
      "title": "Example Domain",
      "meta": {
        "description": "Example website meta description",
        "keywords": "example, test",
        "og_type": "website"
      },
      "headings": [
        { "tag": "h1", "text": "Welcome to Example Domain" }
      ],
      "content": "Full extracted clean body text content...",
      "links_found": [
        "https://example.com/about",
        "https://example.com/contact"
      ]
    }
  ],
  "errors": []
}
```

---

## Getting Started (Node.js)

### 1. Install Dependencies
```bash
npm install
```

### 2. Run MCP Server (stdio mode)
```bash
npm start
```

### 3. Run Standalone CLI Scraper
```bash
npm run scrape https://example.com 10 2 scraped_output.json
```
Arguments: `[target_url] [max_pages] [max_depth] [output_filename]`

---

## Getting Started (Python FastMCP)

### 1. Install Dependencies
```bash
pip install -r requirements.txt
```

### 2. Run FastMCP Server
```bash
python server.py
```

---

## MCP Configuration Example

To register this MCP server with Claude Desktop or Antigravity IDE, add the following to your `mcpServers` config:

```json
{
  "mcpServers": {
    "website-scraper": {
      "command": "node",
      "args": ["c:/Users/james/source/repos/ai-builder-hackathon/backend/mcp-server/index.js"]
    }
  }
}
```
