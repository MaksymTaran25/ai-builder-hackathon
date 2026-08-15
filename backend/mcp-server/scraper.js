import axios from 'axios';
import * as cheerio from 'cheerio';
import { URL } from 'url';

/**
 * Normalizes a URL by stripping hashes/fragments and trailing slashes.
 */
export function normalizeUrl(rawUrl, baseUrl) {
  try {
    const parsed = new URL(rawUrl, baseUrl);
    parsed.hash = ''; // Remove fragment identifiers
    let search = parsed.search;
    let pathname = parsed.pathname;
    
    // Normalize trailing slash if not root
    if (pathname.length > 1 && pathname.endsWith('/')) {
      pathname = pathname.slice(0, -1);
    }
    return `${parsed.protocol}//${parsed.host}${pathname}${search}`;
  } catch (err) {
    return null;
  }
}

/**
 * Checks if a candidate URL belongs to the same domain/origin as the base URL.
 */
export function isSameDomain(candidateUrl, baseUrl) {
  try {
    const candidateHost = new URL(candidateUrl).hostname.replace(/^www\./, '');
    const baseHost = new URL(baseUrl).hostname.replace(/^www\./, '');
    return candidateHost === baseHost || candidateHost.endsWith(`.${baseHost}`);
  } catch (err) {
    return false;
  }
}

/**
 * Recursively scrapes a target URL and all its subpages.
 * 
 * @param {string} startUrl - The initial URL to start scraping from.
 * @param {Object} options - Scraper options.
 * @param {number} [options.maxPages=50] - Maximum number of pages to scrape.
 * @param {number} [options.maxDepth=3] - Maximum depth for link traversal.
 * @param {boolean} [options.includeExternal=false] - Whether to crawl external domain links.
 * @param {number} [options.timeout=10000] - Request timeout in milliseconds per page.
 * @returns {Promise<Object>} Structured JSON object containing scraped website data.
 */
export async function scrapeWebsite(startUrl, options = {}) {
  const {
    maxPages = 50,
    maxDepth = 3,
    includeExternal = false,
    timeout = 10000,
    userAgent = 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) MCP-Website-Scraper/1.0'
  } = options;

  const normalizedStart = normalizeUrl(startUrl);
  if (!normalizedStart) {
    throw new Error(`Invalid start URL provided: "${startUrl}"`);
  }

  const visited = new Set();
  const queue = [{ url: normalizedStart, depth: 0 }];
  const scrapedPages = [];
  const errors = [];

  const axiosInstance = axios.create({
    timeout,
    headers: {
      'User-Agent': userAgent,
      'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
      'Accept-Language': 'en-US,en;q=0.5'
    },
    maxRedirects: 5,
    validateStatus: () => true // Handle 4xx/5xx gracefully
  });

  while (queue.length > 0 && scrapedPages.length < maxPages) {
    const { url, depth } = queue.shift();

    if (visited.has(url)) {
      continue;
    }
    visited.add(url);

    try {
      const response = await axiosInstance.get(url);
      const statusCode = response.status;
      const contentType = response.headers['content-type'] || '';

      // Skip non-HTML responses (images, PDFs, ZIPs, etc.)
      if (!contentType.includes('text/html') && !contentType.includes('application/xhtml+xml')) {
        continue;
      }

      const html = response.data;
      if (typeof html !== 'string') {
        continue;
      }

      const $ = cheerio.load(html);

      // Extract metadata
      const title = $('title').text().trim() || $('meta[property="og:title"]').attr('content') || '';
      const metaDescription = $('meta[name="description"]').attr('content') || $('meta[property="og:description"]').attr('content') || '';
      const metaKeywords = $('meta[name="keywords"]').attr('content') || '';
      const ogType = $('meta[property="og:type"]').attr('content') || '';

      // Extract headings
      const headings = [];
      $('h1, h2, h3').each((_, el) => {
        const text = $(el).text().trim().replace(/\s+/g, ' ');
        if (text) {
          headings.push({
            tag: el.tagName.toLowerCase(),
            text
          });
        }
      });

      // Remove non-content elements before extracting clean text content
      const $content = cheerio.load(html);
      $content('script, style, noscript, svg, iframe, header, footer, nav').remove();
      const bodyText = $content('body').text().replace(/\s+/g, ' ').trim();

      // Extract all valid hyperlinks for crawling & reporting
      const linksFound = new Set();
      const nextQueueCandidates = [];

      $('a[href]').each((_, el) => {
        const href = $(el).attr('href');
        if (!href) return;

        // Skip mailto:, tel:, javascript:, etc.
        if (/^(mailto:|tel:|javascript:|#)/i.test(href.trim())) return;

        const resolved = normalizeUrl(href, url);
        if (!resolved) return;

        linksFound.add(resolved);

        // Check if we should queue this URL for further traversal
        if (depth < maxDepth && !visited.has(resolved)) {
          const isSame = isSameDomain(resolved, normalizedStart);
          if (isSame || includeExternal) {
            nextQueueCandidates.push(resolved);
          }
        }
      });

      // Add to scraped results
      scrapedPages.push({
        url,
        depth,
        status: statusCode,
        title,
        meta: {
          description: metaDescription,
          keywords: metaKeywords,
          og_type: ogType
        },
        headings,
        content: bodyText,
        links_found: Array.from(linksFound)
      });

      // Enqueue subpages
      for (const candidate of nextQueueCandidates) {
        if (!visited.has(candidate) && !queue.some(item => item.url === candidate)) {
          queue.push({ url: candidate, depth: depth + 1 });
        }
      }
    } catch (err) {
      errors.push({
        url,
        depth,
        error: err.message || 'Scraping failed'
      });
    }
  }

  return {
    base_url: normalizedStart,
    scraped_at: new Date().toISOString(),
    total_pages_scraped: scrapedPages.length,
    options: {
      max_pages: maxPages,
      max_depth: maxDepth,
      include_external: includeExternal
    },
    pages: scrapedPages,
    errors
  };
}
