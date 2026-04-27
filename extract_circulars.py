
import os
import re
import urllib.request
import urllib.error
from xml.etree import ElementTree


def clean_filename(filename):
    """Remove spaces and special characters from filename."""
    # Replace spaces with underscores
    filename = filename.replace(" ", "_")
    # Remove any other problematic characters
    filename = re.sub(r'[<>:"/\\|?*]', '', filename)
    # Clean up multiple underscores
    filename = re.sub(r'_+', '_', filename)
    return filename

def parse_rss_feed(xml_content, PDF_DIR):
    """Parse RSS XML and extract circular items."""
    circulars = []
    
    # Parse XML
    root = ElementTree.fromstring(xml_content)
    
    # Find all items
    for item in root.findall(".//item"):
        title_elem = item.find("title")
        link_elem = item.find("link")
        guid_elem = item.find("guid")
        desc_elem = item.find("description")
        
        # Get updated date
        updated_elem = item.find("{http://www.w3.org/2005/Atom}updated")
        if updated_elem is None:
            # Try alternative namespace
            updated_elem = item.find(".//{http://purl.org/syndication/feed/1.0}updated")
        
        title = title_elem.text if title_elem is not None and title_elem.text else "Untitled"
        link = link_elem.text if link_elem is not None and link_elem.text else ""
        guid = guid_elem.text if guid_elem is not None and guid_elem.text else ""
        description = desc_elem.text if desc_elem is not None and desc_elem.text else ""
        
        # Parse date
        date_str = ""
        if updated_elem is not None and updated_elem.text:
            date_str = updated_elem.text
        else:
            # Try to extract from guid or other fields
            date_match = re.search(r'(\d{4}-\d{2}-\d{2})', guid)
            if date_match:
                date_str = date_match.group(1)
        
        # Clean the link - some have double slashes or malformed URLs
        if link:
            link = link.replace("//", "/").replace("https:/", "https://")
        
        circular = {
            "title": title.strip() if title else "",
            "link": link.strip() if link else "",
            "guid": guid.strip() if guid else "",
            "description": description.strip() if description else "",
            "date": date_str,
            "local_pdf_path": os.path.join(PDF_DIR, clean_filename(guid) + '.pdf') if link.endswith('.pdf') else ''
        }
        circulars.append(circular)
    
    return circulars

def download_pdf(url, local_path):
    """Download a PDF file from URL to local path."""
    try:
        # Create directory if it doesn't exist
        os.makedirs(os.path.dirname(local_path), exist_ok=True)
        
        # Add headers to mimic browser request
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
        }
        
        request = urllib.request.Request(url, headers=headers)
        
        with urllib.request.urlopen(request, timeout=30) as response:
            # Check if it's actually a PDF
            content_type = response.headers.get('Content-Type', '')
            if 'pdf' not in content_type.lower() and not url.lower().endswith('.pdf'):
                print(f"  Warning: Not a PDF file: {url}")
                return False
            
            content = response.read()
            
            with open(local_path, 'wb') as f:
                f.write(content)
            
            return True
            
    except urllib.error.HTTPError as e:
        print(f"  HTTP Error {e.code}: {url}")
        return False
    except urllib.error.URLError as e:
        print(f"  URL Error: {url} - {str(e)}")
        return False
    except Exception as e:
        print(f"  Error downloading {url}: {str(e)}")
        return False



