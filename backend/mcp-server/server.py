import asyncio
import json
from datetime import datetime, timezone
from urllib.parse import urlparse, urljoin
import httpx
from bs4 import BeautifulSoup
from mcp.server.fastmcp import FastMCP

# Initialize FastMCP Server
mcp = FastMCP("mcp-website-scraper")

def normalize_url(raw_url: str, base_url: str = None) -> str:
    """Normalizes a URL by resolving relative paths and stripping fragments."""
    try:
        if base_url:
            resolved = urljoin(base_url, raw_url)
        else:
            resolved = raw_url
        parsed = urlparse(resolved)
        if not parsed.scheme or not parsed.netloc:
            return None
        # Remove fragment
        clean_url = f"{parsed.scheme}://{parsed.netloc}{parsed.path}"
        if parsed.query:
            clean_url += f"?{parsed.query}"
        if len(parsed.path) > 1 and clean_url.endswith('/'):
            clean_url = clean_url[:-1]
        return clean_url
    except Exception:
        return None

def is_same_domain(candidate_url: str, base_url: str) -> bool:
    """Checks if candidate URL belongs to the same domain as base URL."""
    try:
        cand_host = urlparse(candidate_url).netloc.replace('www.', '')
        base_host = urlparse(base_url).netloc.replace('www.', '')
        return cand_host == base_host or cand_host.endswith(f".{base_host}")
    except Exception:
        return False

async def scrape_site_async(start_url: str, max_pages: int = 50, max_depth: int = 3, include_external: bool = False) -> dict:
    normalized_start = normalize_url(start_url)
    if not normalized_start:
        raise ValueError(f"Invalid URL: {start_url}")

    visited = set()
    queue = [(normalized_start, 0)]
    scraped_pages = []
    errors = []

    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) MCP-Website-Scraper/1.0",
        "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8"
    }

    async with httpx.AsyncClient(headers=headers, timeout=10.0, follow_redirects=True) as client:
        while queue and len(scraped_pages) < max_pages:
            url, depth = queue.pop(0)

            if url in visited:
                continue
            visited.add(url)

            try:
                response = await client.get(url)
                content_type = response.headers.get("content-type", "")

                if "text/html" not in content_type and "application/xhtml+xml" not in content_type:
                    continue

                soup = BeautifulSoup(response.text, "html.parser")

                title = soup.title.string.strip() if soup.title and soup.title.string else ""
                
                meta_desc = ""
                desc_tag = soup.find("meta", attrs={"name": "description"}) or soup.find("meta", attrs={"property": "og:description"})
                if desc_tag and desc_tag.get("content"):
                    meta_desc = desc_tag["content"].strip()

                headings = []
                for h in soup.find_all(["h1", "h2", "h3"]):
                    text = h.get_text(strip=True)
                    if text:
                        headings.append({"tag": h.name.lower(), "text": text})

                # Strip script and style tags
                for script in soup(["script", "style", "noscript", "header", "footer", "nav"]):
                    script.extract()

                body_text = " ".join(soup.get_text().split())

                links_found = set()
                next_candidates = []

                for a_tag in soup.find_all("a", href=True):
                    href = a_tag["href"].strip()
                    if href.startswith(("mailto:", "tel:", "javascript:", "#")):
                        continue
                    resolved = normalize_url(href, url)
                    if not resolved:
                        continue

                    links_found.add(resolved)

                    if depth < max_depth and resolved not in visited:
                        if is_same_domain(resolved, normalized_start) or include_external:
                            next_candidates.append(resolved)

                scraped_pages.append({
                    "url": url,
                    "depth": depth,
                    "status": response.status_code,
                    "title": title,
                    "meta": {
                        "description": meta_desc
                    },
                    "headings": headings,
                    "content": body_text,
                    "links_found": list(links_found)
                })

                for cand in next_candidates:
                    if cand not in visited and not any(item[0] == cand for item in queue):
                        queue.append((cand, depth + 1))

            except Exception as e:
                errors.append({
                    "url": url,
                    "depth": depth,
                    "error": str(e)
                })

    return {
        "base_url": normalizedStart if 'normalizedStart' in locals() else normalized_start,
        "scraped_at": datetime.now(timezone.utc).isoformat(),
        "total_pages_scraped": len(scraped_pages),
        "options": {
            "max_pages": max_pages,
            "max_depth": max_depth,
            "include_external": include_external
        },
        "pages": scraped_pages,
        "errors": errors
    }

@mcp.tool()
async def scrape_website(url: str, max_pages: int = 50, max_depth: int = 3, include_external: bool = False) -> str:
    """Scrapes a target website URL and recursively crawls all subpages, returning structured JSON content."""
    result = await scrape_site_async(url, max_pages=max_pages, max_depth=max_depth, include_external=include_external)
    return json.dumps(result, indent=2)

if __name__ == "__main__":
    mcp.run()
