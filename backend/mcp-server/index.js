#!/usr/bin/env node

import { Server } from '@modelcontextprotocol/sdk/server/index.js';
import { StdioServerTransport } from '@modelcontextprotocol/sdk/server/stdio.js';
import { CallToolRequestSchema, ListToolsRequestSchema } from '@modelcontextprotocol/sdk/types.js';
import { scrapeWebsite } from './scraper.js';

// Initialize MCP Server
const server = new Server(
  {
    name: 'mcp-website-scraper',
    version: '1.0.0',
  },
  {
    capabilities: {
      tools: {},
    },
  }
);

// Register tool definitions
server.setRequestHandler(ListToolsRequestSchema, async () => {
  return {
    tools: [
      {
        name: 'scrape_website',
        description: 'Scrapes a target URL and recursively crawls all pages and subpages within the same domain, returning a comprehensive JSON object with titles, metadata, headings, page content, and links.',
        inputSchema: {
          type: 'object',
          properties: {
            url: {
              type: 'string',
              description: 'The starting website URL to scrape (e.g. https://example.com or https://docs.example.com/api)',
            },
            max_pages: {
              type: 'number',
              description: 'Maximum number of pages to scrape (default: 50, max: 200)',
              default: 50,
            },
            max_depth: {
              type: 'number',
              description: 'Maximum recursion depth for link crawling (default: 3)',
              default: 3,
            },
            include_external: {
              type: 'boolean',
              description: 'Whether to crawl external domain links (default: false)',
              default: false,
            },
          },
          required: ['url'],
        },
      },
    ],
  };
});

// Handle tool execution requests
server.setRequestHandler(CallToolRequestSchema, async (request) => {
  const { name, arguments: args } = request.params;

  if (name === 'scrape_website') {
    if (!args || typeof args.url !== 'string') {
      throw new Error('Missing required parameter: "url" must be a valid string.');
    }

    const maxPages = Math.min(Math.max(Number(args.max_pages) || 50, 1), 200);
    const maxDepth = Math.max(Number(args.max_depth) || 3, 0);
    const includeExternal = Boolean(args.include_external);

    try {
      const scrapingResult = await scrapeWebsite(args.url, {
        maxPages,
        maxDepth,
        includeExternal,
      });

      return {
        content: [
          {
            type: 'text',
            text: JSON.stringify(scrapingResult, null, 2),
          },
        ],
      };
    } catch (error) {
      return {
        isError: true,
        content: [
          {
            type: 'text',
            text: JSON.stringify(
              {
                error: 'Scraping failed',
                message: error.message,
                url: args.url,
              },
              null,
              2
            ),
          },
        ],
      };
    }
  }

  throw new Error(`Unknown tool: ${name}`);
});

// Start transport
async function main() {
  const transport = new StdioServerTransport();
  await server.connect(transport);
  console.error('MCP Website Scraper Server running on stdio');
}

main().catch((err) => {
  console.error('Fatal error starting MCP server:', err);
  process.exit(1);
});
