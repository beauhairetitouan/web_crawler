import http
import requests
from bs4 import BeautifulSoup
from urllib.parse import urlparse, urljoin
import time

def scrape_url(url, depth, first_url, rec, scraped_urls=None):
    if scraped_urls is None:
        scraped_urls = set()

    # Si la profondeur est 0 ou si l'URL a déjà été scrappée, on arrête
    if depth == 0 or url in scraped_urls:
        return {}, {}

    try:
        # Ajouter l'URL au set des URLs déjà scrappées
        scraped_urls.add(url)

        # Récupération de la page
        response = requests.get(url, timeout=10)  # Ajout d'un timeout pour éviter les blocages
        response.raise_for_status()

        # Parser le contenu HTML
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

            # Exclure le lien courant (l'URL actuelle)
            if full_url == first_url:
                continue
            if rec != 1:
                if parsed_href.netloc == domain:
                    internal_links.add(full_url)
            else:
                if parsed_href.netloc == domain:
                    internal_links.add(full_url)
                elif parsed_href.netloc:
                    external_links.add(full_url)
                

        # Autres statistiques
        video_count = len(soup.find_all('video'))
        table_count = len(soup.find_all('table'))
        form_count = len(soup.find_all('form'))

        # Récursivement scraper les liens internes si la profondeur est > 0
        if depth > 1:
            # Initialisation des structures de données
            graph_data = {url: list(internal_links | external_links)}
            internal_graph_data = {}

            for internal_link in internal_links:
                # Scrape à la profondeur suivante pour les liens internes pointant vers le même domaine
                new_content, new_graph = scrape_url(internal_link, depth - 1,first_url, 0, scraped_urls)

                # Ajouter les données et le graphe interne
                internal_graph_data.update(new_graph)

            # Combine les données obtenues
            graph_data.update(internal_graph_data)

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

        # Si on ne scrappe pas récursivement (profondeur 1), on renvoie seulement les données actuelles
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
        }, {url: list(internal_links | external_links)}

    except requests.RequestException as e:
        return {'error': f"Erreur lors de la requête: {e}"}, {}
