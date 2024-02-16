import requests
from bs4 import BeautifulSoup
import csv
import re

def fetch_url(url):
    try:
        response = requests.get(url)
        response.raise_for_status()  # Raises an HTTPError if the HTTP request returned an unsuccessful status code
        return BeautifulSoup(response.text, 'html.parser')
    except requests.RequestException as e:
        print(f"Error fetching URL {url}: {e}")
        return None

def get_match_links(year_page_soup):
    links = []
    if year_page_soup:
        for td in year_page_soup.find_all('td', class_='text-center'):
            a = td.find('a', href=True)
            if a:
                links.append(a['href'])
    return links

def get_goal_details(match_page_soup):
    goals = []
    if match_page_soup:
        more_info = match_page_soup.find('div', class_='moreInfo')
        if more_info:
            for row in more_info.find_all('div', class_='row'):
                for player in row.find_all('a', class_='text-white'):
                    goal_info = {'minute': None, 'player': None}
                    goal_minute = player.find_previous('small')
                    if goal_minute and player:
                        goal_text = goal_minute.get_text().strip()
                        first_number = re.search(r'\d+', goal_text)
                        goal_info['minute'] = first_number.group(0) if first_number else None
                        goal_info['player'] = player.get_text().strip()
                        goals.append(goal_info)
    return goals

data = []
base_url = 'https://www.voetbalkrant.com'

for year in range(2007, 2023):
    print(f"Processing year: {year}")
    year_url = f'{base_url}/belgie/jupiler-pro-league/geschiedenis/{year}-{year+1}/wedstrijden'
    year_soup = fetch_url(year_url)
    match_links = get_match_links(year_soup)

    for match_link in match_links:
        match_soup = fetch_url(base_url + match_link)
        match_goals = get_goal_details(match_soup)
        for goal in match_goals:
            data.append({
                'Year': year,
                'Minute': goal['minute'],
                'Player': goal['player']
            })

with open('football_goals.csv', 'w', newline='', encoding='utf-8') as file:
    writer = csv.DictWriter(file, fieldnames=['Year', 'Minute', 'Player'])
    writer.writeheader()
    writer.writerows(data)

print("Data scraping complete. Check the football_goals.csv file.")