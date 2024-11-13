from flask import Flask
import requests
import re
from bs4 import BeautifulSoup

app = Flask(__name__)
def fetch_sec_data(arr):
    for item in arr:
        # Ensure CIK is 10 digits
        cik = item['CIK'].zfill(10)
        formatted_cik = cik.lstrip('0')  # Remove leading zeros for formatted CIK
        url = f'https://data.sec.gov/submissions/CIK{cik}.json'

        try:
            # Fetch data from the URL
            response = requests.get(url)
            response.raise_for_status()  # Check for HTTP errors
            
            # Parse JSON response
            json_data = response.json()
            filings = json_data.get('filings', {}).get('recent')

            if filings:
                # Extract the first accession number and primary document
                first_accession_number = filings.get('accessionNumber', [None])[0]
                formatted_acc = first_accession_number.replace('-', '') if first_accession_number else None
                first_primary_document = filings.get('primaryDocument', [None])[0]
                
                if formatted_acc and first_primary_document:
                    link = f'https://www.sec.gov/Archives/edgar/data/{formatted_cik}/{formatted_acc}/{first_primary_document}'
                    print(link)
                    
                   # Call appropriate function based on formType
                    if item.get('formType') == '4':
                        #scrape4(link)
                        True
                    else:
                        True
                        #scrape144(link)
                else:
                    print("No valid accession number or primary document found.")
            else:
                print("No recent filings found.")
        
        except requests.exceptions.RequestException as error:
            print(f"Error fetching {url}: {error}")

def fetch_and_parse_entries(url):
    headers = {
        'accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.7',
        'accept-language': 'en-ZA,en-GB;q=0.9,en-US;q=0.8,en;q=0.7',
        'cache-control': 'max-age=0',
        'cookie': 'nmstat=891756e9-a78e-9bb3-a82e-c13770ef859a; _gid=GA1.2.2109077336.1730302428; _ga=GA1.1.417854797.1730136641; _4c_=%7B%22_4c_s_%22%3A%22dZLLboMwEEV%2FJfI6IBu%2FMLsqlaou2qpVH8sowSZYaQEZNzSN%2BPeOgfSBVDbGZ%2B69Ho19Ql1pKpQRSTHFXEqWpGKJ9ubYouyEnNVhOaAM6YLkZKNExLVRERNcR8rkOJJcig0nRZEQjpboY8iSiiSCKpLyfol0dc5wRpvW7qo%2FupRQJhjobOMnYeiGUAGVlPKZFkjQniM386yx7rqfqLHAZTqLCgSkjZuf%2Bq80bybpCeW1NnA8UTFJYxwVLfThPwNJMAqhtX7P%2FdofmyDrzHbR6j0UtDnY3Kw7q305%2BAf5REtjd6UPGKcDDr0hAn%2BdrXTdzW0T%2FbYpooBuXd21JjhXpavfzILQIK7hRtHL4AjNOlMY5wYZ7FrrQ5%2BtyeNdfZgAvIKRRSN7toHqxePqAfjtL3K%2FuruZ0NXF%2Bun6EjaMwNCYVDKeBisYQf15rpiqBBZ4czA3%2F4qyVDAcvr7vvwA%3D%22%7D; _ga_300V1CHKH1=GS1.1.1730305771.6.1.1730307079.0.0.0; _ga_CSLL4ZEK4L=GS1.1.1730305771.6.1.1730307079.0.0.0',
        'priority': 'u=0, i',
        'referer': 'https://www.sec.gov/cgi-bin/browse-edgar?action=getcurrent',
        'sec-ch-ua': '"Chromium";v="130", "Google Chrome";v="130", "Not?A_Brand";v="99"',
        'sec-ch-ua-mobile': '?0',
        'sec-ch-ua-platform': '"Windows"',
        'sec-fetch-dest': 'document',
        'sec-fetch-mode': 'navigate',
        'sec-fetch-site': 'same-origin',
        'sec-fetch-user': '?1',
        'upgrade-insecure-requests': '1',
        'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/130.0.0.0 Safari/537.36'
    }
    
    try:
        # Make the request
        response = requests.get(url, headers=headers)
        response.raise_for_status()  # Check for HTTP errors
        soup = BeautifulSoup(response.content, 'lxml')
        
        # Find all <entry> elements
        entries = soup.find_all('entry')

        # Process each <entry> element
        entry_list = []
        for entry in entries:
            # Extract relevant information from each entry

            # Extract CIK from <title>
            title_tag = entry.find('title')
            title_text = title_tag.text if title_tag else ""
            cik_match = re.search(r'\((\d+)\)', title_text) if title_text else None
            cik = cik_match.group(1) if cik_match else None

            # Extract time from <updated>
            updated_tag = entry.find('updated')
            time = updated_tag.text if updated_tag else None

            # Extract form type from <category>
            category_tag = entry.find('category')
            form_type = category_tag.get('term') if category_tag else None

            # Append extracted data if valid
            if cik and time and form_type in ['4', '144']:
                entry_list.append({
                    "CIK": cik,
                    "time": time,
                    "formType": form_type
                })

        return entry_list

    except requests.exceptions.RequestException as e:
        print(f"An error occurred: {e}")
        return []
        
@app.route('/')
def home():
    return 'Hello, World!'

@app.route('/activate')
def activate():
    url = 'https://www.sec.gov/cgi-bin/browse-edgar?action=getcurrent&CIK=&type=&company=&dateb=&owner=include&start=0&count=40&output=atom'
    entries = fetch_and_parse_entries(url)
    fetch_sec_data(entries)
    return 'Script running'
