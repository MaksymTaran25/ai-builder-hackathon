#!/usr/bin/env node

import { scrapeWebsite } from './scraper.js';
import fs from 'fs/promises';
import path from 'path';

async function runStandalone() {
  const args = process.argv.slice(2);
  const targetUrl = args[0] || 'https://example.com';
  const maxPages = Number(args[1]) || 10;
  const maxDepth = Number(args[2]) || 2;
  const outputFile = args[3] || 'scraped_output.json';

  console.log(`Starting scraper for: ${targetUrl}`);
  console.log(`Max Pages: ${maxPages}, Max Depth: ${maxDepth}`);

  const startTime = Date.now();
  const result = await scrapeWebsite(targetUrl, {
    maxPages,
    maxDepth,
    includeExternal: false
  });
  const duration = ((Date.now() - startTime) / 1000).toFixed(2);

  console.log(`Scraping complete! Scraped ${result.total_pages_scraped} pages in ${duration}s.`);

  const outputPath = path.resolve(process.cwd(), outputFile);
  await fs.writeFile(outputPath, JSON.stringify(result, null, 2), 'utf-8');
  console.log(`JSON object saved to: ${outputPath}`);
}

runStandalone().catch(err => {
  console.error('Error running standalone scraper:', err);
  process.exit(1);
});
