import requests
from bs4 import BeautifulSoup
from datetime import datetime

# Function to fetch latest insurance data from IRDAI
def fetch_irdai_data():
    try:
        # URL for IRDAI health insurance products
        url = "https://irdai.gov.in/health-insurance-products"
        response = requests.get(url)

        if response.status_code == 200:
            soup = BeautifulSoup(response.text, 'html.parser')
            # Extract and parse the latest insurance data
            insurance_data = []
            tables = soup.find_all('table')
            for table in tables:
                rows = table.find_all('tr')
                for row in rows:
                    cols = row.find_all('td')
                    if len(cols) > 5:  # Ensure row has enough columns
                        company = cols[2].text.strip()
                        policy = cols[4].text.strip()
                        date = cols[5].text.strip()
                        pdf_link = cols[7].find('a')['href'] if cols[7].find('a') else ""

                        insurance_data.append({
                            "company": company,
                            "policy": policy,
                            "date": date,
                            "pdf_link": pdf_link
                        })

            return insurance_data
        else:
            return []
    except Exception as e:
        print(f"Error fetching IRDAI data: {str(e)}")
        return []


# Function to fetch claim settlement ratios
def fetch_claim_settlement_data():
    try:
        # Based on search result, Ditto provides updated claim settlement ratios
        url = "https://joinditto.in/health-insurance/companies/"
        response = requests.get(url)

        if response.status_code == 200:
            soup = BeautifulSoup(response.text, 'html.parser')
            # Find the table with claim settlement data
            tables = soup.find_all('table')

            claim_data = []
            for table in tables:
                rows = table.find_all('tr')
                for row in rows[1:]:  # Skip header row
                    cols = row.find_all('td')
                    if len(cols) >= 5:
                        company = cols[0].text.strip()
                        csr = cols[1].text.strip()
                        hospitals = cols[2].text.strip()
                        premium = cols[3].text.strip()

                        claim_data.append({
                            "company": company,
                            "claim_settlement_ratio": csr,
                            "network_hospitals": hospitals,
                            "premium": premium
                        })

            return claim_data
        else:
            return []
    except Exception as e:
        print(f"Error fetching claim settlement data: {str(e)}")
        return []


# Enhanced function to scrape premium data from insurance company websites
def scrape_premium_data():
    try:
        # List of major health insurance company websites
        insurance_websites = {
            "HDFC ERGO": "https://www.hdfcergo.com/health-insurance/plans",
            "Star Health": "https://www.starhealth.in/health-insurance-plans",
            "Aditya Birla": "https://www.adityabirlacapital.com/health-insurance/plans",
            "Bajaj Allianz": "https://www.bajajallianz.com/health-insurance-plans.html",
            "ICICI Lombard": "https://www.icicilombard.com/health-insurance/health-plans",
            "Tata AIG": "https://www.tataaig.com/health-insurance/health-plans",
            "SBI General": "https://www.sbigeneral.in/health-insurance/health-plans",
            "Care Health": "https://www.careinsurance.com/health-insurance-policies.html"
        }

        premium_data = []

        for company, url in insurance_websites.items():
            try:
                headers = {
                    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
                }
                response = requests.get(url, headers=headers, timeout=10)

                if response.status_code == 200:
                    soup = BeautifulSoup(response.text, 'html.parser')

                    # Look for policy cards/containers (generic selectors that need customization per site)
                    policy_containers = soup.select('.plan-card, .product-card, .policy-card, .insurance-plan, .card')

                    for container in policy_containers:
                        try:
                            # Extract policy name
                            policy_name_elem = container.select_one('h2, h3, .plan-name, .policy-name, .title')
                            policy_name = policy_name_elem.text.strip() if policy_name_elem else "Unknown Policy"

                            # Extract premium information
                            premium_elem = container.select_one('.premium, .price, .amount, .rate')
                            premium = premium_elem.text.strip() if premium_elem else "Premium not found"

                            # Extract coverage information
                            coverage_elem = container.select_one('.coverage, .sum-insured, .cover-amount')
                            coverage = coverage_elem.text.strip() if coverage_elem else "Coverage not found"

                            # Extract features
                            feature_elems = container.select('li, .feature, .benefit')
                            features = [elem.text.strip() for elem in feature_elems]

                            premium_data.append({
                                "company": company,
                                "policy_name": policy_name,
                                "premium": premium,
                                "coverage": coverage,
                                "features": features[:5],  # Limit to top 5 features
                                "last_updated": datetime.now().strftime("%Y-%m-%d")
                            })
                        except Exception as e:
                            print(f"Error parsing policy from {company}: {str(e)}")
                            continue
            except Exception as e:
                print(f"Error scraping {company}: {str(e)}")
                continue

        return premium_data
    except Exception as e:
        print(f"Error in premium scraping: {str(e)}")
        return []


# Function to fetch terms and conditions from insurance company websites
def fetch_terms_and_conditions(company_name):
    try:
        # This is a simplified example - in practice, you'd need to map company names to their websites
        company_websites = {
            "HDFC ERGO": "https://www.hdfcergo.com/health-insurance",
            "Aditya Birla": "https://www.adityabirlacapital.com/health-insurance",
            "Bajaj Allianz": "https://www.bajajallianz.com/health-insurance.html",
            "Care": "https://www.careinsurance.com/health-insurance-policies.html",
            "Niva Bupa": "https://www.nivabupa.com/health-insurance",
            "Star Health": "https://www.starhealth.in/health-insurance",
            "ICICI Lombard": "https://www.icicilombard.com/health-insurance",
            "SBI General": "https://www.sbigeneral.in/health-insurance",
            "Tata AIG": "https://www.tataaig.com/health-insurance",
            "Max Bupa": "https://www.maxbupa.com/health-insurance",
            "Religare": "https://www.religarehealthinsurance.com/health-insurance",
        }

        # Try to find the best match for company name
        best_match = None
        for key in company_websites:
            if key.lower() in company_name.lower() or company_name.lower() in key.lower():
                best_match = key
                break

        if best_match:
            url = company_websites[best_match]
            response = requests.get(url)

            if response.status_code == 200:
                soup = BeautifulSoup(response.text, 'html.parser')

                # Look for terms and conditions sections
                terms_sections = soup.find_all(['div', 'section'], class_=lambda c: c and (
                        'terms' in c.lower() or 'conditions' in c.lower()))

                terms_text = []
                for section in terms_sections:
                    terms_text.append(section.get_text(strip=True))

                # If no specific terms sections found, try to extract from policy pages
                if not terms_text:
                    # Try to find links to terms and conditions pages
                    terms_links = soup.find_all('a', text=lambda t: t and (
                            'terms' in t.lower() or 'conditions' in t.lower()))

                    for link in terms_links:
                        if 'href' in link.attrs:
                            terms_url = link['href']
                            if not terms_url.startswith('http'):
                                # Handle relative URLs
                                if terms_url.startswith('/'):
                                    base_url = '/'.join(url.split('/')[:3])
                                    terms_url = base_url + terms_url
                                else:
                                    terms_url = url + '/' + terms_url

                            terms_response = requests.get(terms_url)
                            if terms_response.status_code == 200:
                                terms_soup = BeautifulSoup(terms_response.text, 'html.parser')
                                terms_content = terms_soup.get_text(strip=True)
                                terms_text.append(terms_content)

                return "\n".join(terms_text)
            else:
                return "Could not fetch terms and conditions. Website returned an error."
        else:
            return f"No website information available for {company_name}"
    except Exception as e:
        print(f"Error fetching terms and conditions: {str(e)}")
        return f"Error fetching terms and conditions: {str(e)}"
