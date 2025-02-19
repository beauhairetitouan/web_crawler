import requests
from bs4 import BeautifulSoup

def scrape_url(url):
    try:
        response = requests.get(url)
        response.raise_for_status()

        soup = BeautifulSoup(response.text, 'html.parser')

        # Statistiques de base
        text_count = len(soup.get_text())
        image_count = len(soup.find_all('img'))
        internal_links = [a['href'] for a in soup.find_all('a', href=True) if url in a['href']]
        external_links = [a['href'] for a in soup.find_all('a', href=True) if url not in a['href'] and a['href'].startswith('http')]

        video_count = len(soup.find_all('video'))
        table_count = len(soup.find_all('table'))
        form_count = len(soup.find_all('form'))

        # Structure du graphe (Noeud principal et ses liens)
        graph_data = {url: internal_links + external_links}

        return {
            'text_count': text_count,
            'image_count': image_count,
            'internal_link_count': len(internal_links),
            'external_link_count': len(external_links),
            'video_count': video_count,
            'table_count': table_count,
            'form_count': form_count,
        }, graph_data

    except requests.RequestException as e:
        return {'error': f"Erreur lors de la requête: {e}"}, {}
