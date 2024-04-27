import requests
from bs4 import BeautifulSoup
from datetime import datetime
import time
import csv
from datetime import datetime

filename = 'fight_details.csv'
fieldnames = ['fighter_name', 'mat_number', 'fight_number', 'date', 'time', 'datetime']

base_url = 'https://asjjf.org'
event_url = base_url + '/main/schedule/1494'
academy_of_interest = 'Yawara'

current_year = datetime.now().year

def fetch_html(url):
    response = requests.get(url)
    response.raise_for_status()  # Raises an HTTPError for bad requests
    return response.text

def parse_html(html):
    soup = BeautifulSoup(html, 'html.parser')
    return soup

def extract_bracket_links(soup):
    # Look for all 'a' tags where the href contains 'public/bracketsView'
    bracket_links = [a['href'] for a in soup.find_all('a', href=True) if 'public/bracketsView' in a['href']]
    return bracket_links

from bs4 import BeautifulSoup


# Function to parse the HTML and extract relevant details of matches where the fighter belongs to 'Yawara'
def extract_academy_fight_details(url, academy_name):
    html = fetch_html(url)
    soup = parse_html(html)
    
    # Find all text elements that contain the academy
    academy_elements = soup.find_all(string=lambda text: academy_name in text if text else False)
    
    # For each element find its fight details
    fights = []
    for element in academy_elements:
        fight = {}
        
        # The parent 'g' element that contains all details of the fight
        fight_detail_element = element.parent.parent
        
        # Extracting the fighter's name
        fighter_name_tag = element.parent.find_previous_sibling("text")
        if fighter_name_tag and 'ff1name' in fighter_name_tag.get('id'):
            fight['fighter_name'] = fighter_name_tag.get_text()
        
       # Extracting mat number, date, and time
        date_time_mat = fight_detail_element.find_all(lambda tag: tag.name == "text" and ('mft' in tag.get('id') or 'mfn' in tag.get('id')))
        for detail in date_time_mat:
            if 'mfn' in detail.get('id') and "Fight" in detail.get_text():
                fight['fight_number'] = detail.get_text()
            elif 'mfn' in detail.get('id') and "Mat" in detail.get_text():
                fight['mat_number'] = detail.get_text()
            elif 'mft' in detail.get('id'):
                if ":" in detail.get_text():
                    fight['time'] = detail.get_text()
                else:
                    fight['date'] = detail.get_text()

        # Combining date and time into a datetime object
        if 'date' in fight and 'time' in fight:
            date_time_str = f"{current_year} {fight['date']} {fight['time']}"
            # Adjust the format below based on the actual format of 'date' and 'time'
            fight['datetime'] = datetime.strptime(date_time_str, "%Y %d %b %H:%M%p")
        

        # If we have extracted all the details add to the list
        if 'fighter_name' in fight and 'fight_number' in fight and 'mat_number' in fight and 'datetime' in fight:
            fights.append(fight)

    print(fights)  
    return fights


def main(url):
    html = fetch_html(url)
    soup = parse_html(html)
    bracket_links = extract_bracket_links(soup)

    all_fights = []
    
    # Print all bracket URLs found
    for link in bracket_links:
        # go through each link, do the extraction and sleep one second
        barcket_fights = extract_academy_fight_details(base_url + link, academy_of_interest)
        all_fights.extend(barcket_fights)
        time.sleep(1)

    with open(filename, mode='w', newline='') as file:
        writer = csv.DictWriter(file, fieldnames=fieldnames)

        # Write the header
        writer.writeheader()

        # Write the rows
        for fight in all_fights:
            # Convert datetime object to string if necessary
            fight['datetime'] = fight['datetime'].strftime('%Y-%m-%d %H:%M')
            writer.writerow(fight)

        print(f"Data has been written to {filename}")

if __name__ == "__main__":
    main(event_url)
