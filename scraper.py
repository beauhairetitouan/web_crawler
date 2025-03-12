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

    print(f"Scraping URL: {url} with depth {depth}")

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
                
        print(f"URL: {url}, Profondeur: {depth}, Liens internes: {len(internal_links)}, Liens externes: {len(external_links)}")

        # Autres statistiques
        video_count = len(soup.find_all('video'))
        table_count = len(soup.find_all('table'))
        form_count = len(soup.find_all('form'))

        # Créer les données pour l'URL actuelle
        current_data = {
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
        }

        # Initialisation du graphe
        graph_data = {url: list(internal_links | external_links)}

        # Récursivement scraper les liens internes si la profondeur est > 1
        # Limiter la profondeur maximale à 2
        if depth > 1 and depth <= 2:
            # Limiter le nombre de liens à scraper
            max_links = 20
            links_to_scrape = list(internal_links)[:max_links]
            print(f"Scraping {len(links_to_scrape)}/{len(internal_links)} liens internes pour la profondeur {depth-1}")
            
            for internal_link in links_to_scrape:
                # Scrape à la profondeur suivante pour les liens internes
                new_content, new_graph = scrape_url(internal_link, depth - 1, first_url, 0, scraped_urls)
                
                # Ajouter les données du graphe
                for key, value in new_graph.items():
                    # Éviter les doublons en fusionnant les listes si la clé existe déjà
                    if key in graph_data:
                        existing_links = set(graph_data[key])
                        new_links = set(value)
                        graph_data[key] = list(existing_links | new_links)
                    else:
                        graph_data[key] = value
                
                # Debug: vérifier les données retournées
                print(f"URL: {internal_link}, Profondeur: {depth-1}, Nœuds retournés dans le graphe: {len(new_graph)}")

        print(f"URL: {url}, Profondeur: {depth}, Nœuds dans le graphe: {len(graph_data)}")
        # Retourner les données actuelles et le graphe
        return current_data, graph_data

    except requests.RequestException as e:
        print(f"Erreur lors de la requête pour {url}: {e}")
        return {'error': f"Erreur lors de la requête: {e}"}, {}