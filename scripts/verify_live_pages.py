import urllib.request
import re
import sys
import ssl

sys.stdout.reconfigure(encoding='utf-8')

def check_url(url, lang):
    ctx = ssl._create_unverified_context()
    req = urllib.request.Request(url, headers={'User-Agent': 'Mozilla/5.0'})
    with urllib.request.urlopen(req, context=ctx) as resp:
        html = resp.read().decode('utf-8')

    print(f"=== CHECKING {url} ({lang}) ===")
    
    # FAQs
    faqs = re.findall(r'cf-faq-question-text[^>]*>(.*?)</span>', html)
    print(f"Total FAQ items found: {len(faqs)}")
    for i, q in enumerate(faqs, 1):
        print(f"  {i}. {q.strip()}")

    # Patient Stories
    stories = re.findall(r'ts-flow-name">(.*?)</h5>', html)
    print(f"\nPatient Stories found: {len(stories)}")
    for s in stories:
        print(f"  - {s.strip()}")

    treatments = re.findall(r'ts-flow-treatment">(.*?)</p>', html)
    for t in treatments:
        print(f"  - Treatment: {t.strip()}")

    quotes = re.findall(r'ts-flow-quote">"(.*?)"</p>', html)
    for q in quotes:
        print(f"  - Quote: {q.strip()[:60]}...")

    # Special Offers
    if 'दन्त स्वास्थ्य विशेष छुट अफर' in html:
        print("\n[SUCCESS] Nepali Special Offer found in HTML!")
    elif 'Dental Care Special Offer' in html:
        print("\n[NOTICE] English Special Offer found in HTML")
    else:
        print("\n[INFO] Special offer text check...")

if __name__ == '__main__':
    check_url('https://carefirstdental.org/en/', 'EN')
    print('\n' + '='*50 + '\n')
    check_url('https://carefirstdental.org/ne/', 'NE')
