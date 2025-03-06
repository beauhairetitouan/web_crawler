import http
import requests
from bs4 import BeautifulSoup
from urllib.parse import urlparse, urljoin

def scrape_url(url):
    try:
        response = requests.get(url, timeout=10)  # Ajout d'un timeout pour éviter les blocages
        response.raise_for_status()

        soup = BeautifulSoup(response.text, 'html.parser')

        # Statistiques de base
        text_content = soup.get_text(strip=True)  # Suppression des espaces inutiles
        text_count = len(text_content)
        image_count = len(soup.find_all('img'))

        # Taille de la page en octets
        page_size = len(response.content)
        
        # Récupérer le nom de domaine
        parsed_url = urlparse(url)
        domain = parsed_url.netloc

        # Trouver les liens internes et externes
        internal_links = set()
        external_links = set()

        for link in soup.find_all('a', href=True):
            
            href = link.get('href').strip()
            
            # Éviter les ancres (#) et liens vides
            if href.startswith("#") or href == "":
                continue

            full_url = urljoin(url, href)  # Gestion des liens relatifs
            parsed_href = urlparse(full_url)

            if parsed_href.netloc == domain:  
                internal_links.add(full_url)
            elif parsed_href.netloc:  # Vérification que le lien externe est valide
                external_links.add(full_url)

        # Autres statistiques
        video_count = len(soup.find_all('video'))
        table_count = len(soup.find_all('table'))
        form_count = len(soup.find_all('form'))

        # Structure du graphe (Noeud principal et ses liens)
        graph_data = {url: list(internal_links | external_links)}

        return {
            'text_count': text_count,
            'page_size_bytes': page_size,
            'image_count': image_count,
            'internal_link_count': len(internal_links),
            'external_link_count': len(external_links),
            'video_count': video_count,
            'table_count': table_count,
            'form_count': form_count,
            'internal_links': list(internal_links),  # Convertir en liste pour JSON
            'external_links': list(external_links)
        }, graph_data

    except requests.RequestException as e:
        return {'error': f"Erreur lors de la requête: {e}"}, {}

