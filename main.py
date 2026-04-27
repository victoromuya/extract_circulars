import json
import os
import urllib.request
import urllib.parse
from datetime import datetime
from xml.etree import ElementTree
from extract_circulars import clean_filename, parse_rss_feed
from download_pdfs import download_pdf


RSS_URL = "https://www.cbn.gov.ng/api/rssfeed/circularsfeed"
OUTPUT_JSON = "cbn_circulars.json"
PDF_DIR = "cbn_pdfs"

def main():
    print("=" * 60)
    print("CBN Circulars Extractor")
    print("=" * 60)
    
    # Create PDF directory
    if not os.path.exists(PDF_DIR):
        os.makedirs(PDF_DIR)
        print(f"\nCreated directory: {PDF_DIR}")
    
    # Fetch RSS feed
    print(f"\nFetching RSS feed from: {RSS_URL}")
    
    try:
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
        }
        request = urllib.request.Request(RSS_URL, headers=headers)
        
        with urllib.request.urlopen(request, timeout=60) as response:
            xml_content = response.read().decode('utf-8')
        
        print(f"Successfully fetched RSS feed")
        
    except Exception as e:
        print(f"Error fetching RSS feed: {str(e)}")
        # Use sample data as fallback
        print("Using embedded sample data...")
        xml_content = None
    
    # Parse circulars
    if xml_content:
        circulars = parse_rss_feed(xml_content, PDF_DIR)
    else:
        # Use sample data from the fetched content
        circulars = []
    
    print(f"\nFound {len(circulars)} circular items")
    
    # Download PDFs
    print(f"\nDownloading PDF files to '{PDF_DIR}' directory...")
    print("-" * 60)
    
    downloaded_count = 0
    failed_count = 0
    
    for i, circular in enumerate(circulars):
        url = circular.get("link", "")
        
        # Skip if no URL or not a PDF
        if not url or ".pdf" not in url.lower():
            continue
        
        # Generate filename from title or use a portion of URL
        title = circular.get("title", "unknown")
        if title and title != "Untitled":
            filename = clean_filename(title) + ".pdf"
        else:
            # Extract filename from URL
            parsed = urllib.parse.urlparse(url)
            filename = os.path.basename(parsed.path)
            if not filename.endswith(".pdf"):
                filename = f"circular_{i+1}.pdf"
        
        # Ensure .pdf extension
        if not filename.lower().endswith(".pdf"):
            filename += ".pdf"
        
        local_path = os.path.join(PDF_DIR, filename)
        
        print(f"\n[{i+1}/{len(circulars)}] {title[:50]}...")
        print(f"  URL: {url}")
        
        # Download the file
        if download_pdf(url, local_path):
            circular["local_pdf_path"] = local_path
            downloaded_count += 1
            print(f"  Saved: {local_path}")
        else:
            failed_count += 1
            print(f"  Failed to download")
    
    # Save JSON
    print("\n" + "=" * 60)
    print("Saving to JSON file...")
    
    output_data = {
        "extraction_date": datetime.now().isoformat(),
        "source_url": RSS_URL,
        "total_circulars": len(circulars),
        "downloaded_pdfs": downloaded_count,
        "failed_downloads": failed_count,
        "circulars": circulars
    }
    
    with open(OUTPUT_JSON, 'w', encoding='utf-8') as f:
        json.dump(output_data, f, indent=2, ensure_ascii=False)
    
    print(f"\nJSON file saved: {OUTPUT_JSON}")
    print(f"Total circulars: {len(circulars)}")
    print(f"PDFs downloaded: {downloaded_count}")
    print(f"Failed downloads: {failed_count}")
    print("\nDone!")

if __name__ == "__main__":
    main()