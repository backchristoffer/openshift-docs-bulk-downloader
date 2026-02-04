import os
import re
import json
import signal
import sys
import argparse
import requests
from bs4 import BeautifulSoup
from tqdm import tqdm

# Global tracking for cleanup on signal
current_file_path = None

def signal_handler(sig, frame):
    """Handles SIGINT and SIGTERM to prevent file corruption."""
    global current_file_path
    print(f"\n[!] Signal {sig} received. Graceful shutdown initiated...")
    
    if current_file_path and os.path.exists(current_file_path):
        print(f"[!] Removing incomplete file: {current_file_path}")
        try:
            os.remove(current_file_path)
        except Exception as e:
            print(f"[!] Failed to remove {current_file_path}: {e}")
    
    print("[*] Exit complete.")
    sys.exit(0)

# Register signals
signal.signal(signal.SIGINT, signal_handler)
signal.signal(signal.SIGTERM, signal_handler)

def sanitize_name(name):
    return re.sub(r'[\\/*?:"<>|]', "", name).strip()

def get_pdf_link(href, version):
    slug = href.rstrip('/').split('/')[-1]
    title_slug = slug.capitalize()
    return (
        f"https://docs.redhat.com/en/documentation/openshift_container_platform/{version}/pdf/"
        f"{slug}/OpenShift_Container_Platform-{version}-{title_slug}-en-US.pdf"
    )

def verify_pdf(url):
    try:
        r = requests.head(url, allow_redirects=True, timeout=5)
        return r.status_code == 200
    except:
        return False

def scrape_version(version, cache_file, verify=False):
    base_url = f"https://docs.redhat.com/en/documentation/openshift_container_platform/{version}"
    print(f"[*] Accessing TOC for v{version}...")
    try:
        response = requests.get(base_url, timeout=15)
        response.raise_for_status()
    except Exception as e:
        print(f"[!] Error: Could not load version {version}. (Reason: {e})")
        return False
    
    soup = BeautifulSoup(response.text, "html.parser")
    toc_data = {}
    pattern = f"/en/documentation/openshift_container_platform/{version}/html/"
    links = [a for a in soup.find_all("a", href=True) if pattern in a['href']]
    
    for link in tqdm(links, desc=f"Mapping v{version}", unit="link"):
        href = link['href']
        category = "General"
        for p in link.find_parents(limit=6):
            header = p.find(['h2', 'h3', 'h4', 'strong'])
            if header:
                category = header.get_text(strip=True)
                break    
        category = sanitize_name(category)
        if category not in toc_data:
            toc_data[category] = []
        pdf_url = get_pdf_link(href, version)
        if verify:
            if not verify_pdf(pdf_url):
                continue
        if pdf_url not in toc_data[category]:
            toc_data[category].append(pdf_url)
            
    toc_data = {k: v for k, v in toc_data.items() if v}
    with open(cache_file, "w") as f:
        json.dump(toc_data, f, indent=4)
    print(f"[+] Found {sum(len(v) for v in toc_data.values())} PDFs across {len(toc_data)} categories.")
    return True

def download_version(cache_file, output_dir):
    global current_file_path
    if not os.path.exists(cache_file):
        print(f"[!] No cache found at {cache_file}. Run with --scrape first.")
        return False
    
    with open(cache_file, "r") as f:
        toc_data = json.load(f)
    
    print(f"[*] Starting download into: {output_dir}")
    for category, urls in toc_data.items():
        cat_dir = os.path.join(output_dir, category)
        os.makedirs(cat_dir, exist_ok=True)
        
        for url in urls:
            filename = url.split("/")[-1]
            path = os.path.join(cat_dir, filename)    
            if os.path.exists(path):
                continue
            try:
                # Track path for signal cleanup
                current_file_path = path
                r = requests.get(url, stream=True, timeout=30)
                
                if r.status_code == 200:
                    total = int(r.headers.get('content-length', 0))
                    with open(path, 'wb') as f, tqdm(
                        desc=f" {filename[:25]}", total=total, 
                        unit='iB', unit_scale=True, leave=False
                    ) as bar:
                        for chunk in r.iter_content(chunk_size=8192):
                            if chunk:
                                f.write(chunk)
                                bar.update(len(chunk))
                # Successful download, reset tracker
                current_file_path = None
            except Exception:
                # Cleanup if error occurred during stream
                if os.path.exists(path):
                    os.remove(path)
                current_file_path = None
                continue
    return True

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="OpenShift Documentation PDF Scraper and Downloader")
    parser.add_argument("--version", type=str, default="4.20", help="Version to target (e.g. 4.19)")
    parser.add_argument("--scrape", action="store_true", help="Scrape and cache the TOC")
    parser.add_argument("--verify", action="store_true", help="Verify PDF existence during scrape")
    parser.add_argument("--download", action="store_true", help="Download PDFs from cache")
    parser.add_argument("--cleanup", action="store_true", help="Delete the JSON cache file after downloading")
    
    args = parser.parse_args()
    c_file = f"toc_{args.version}.json"
    o_dir = f"openshift_v{args.version}"

    success = True
    
    if args.scrape:
        success = scrape_version(args.version, c_file, args.verify)
    if success and args.download:
        success = download_version(c_file, o_dir)
    if success and args.cleanup:
        if os.path.exists(c_file):
            os.remove(c_file)
            print(f"[+] Cleaned up cache file: {c_file}")
    
    if not any([args.scrape, args.download, args.cleanup]):
        parser.print_help()