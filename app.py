import requests
from bs4 import BeautifulSoup
from flask import Flask, request, jsonify, render_template, send_from_directory, current_app



app = Flask(__name__)

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/favicon.ico')
def favicon():
    return send_from_directory(current_app.root_path + '/static', 'favicon.ico')

@app.route('/scrape', methods=['POST'])
def scrape():
    """
    Extrait le contenu basique d'une URL donnée
    """
    # Récupérer l'URL depuis le corps de la requête
    data = request.get_json()
    url = data.get('url')
    
    # Vérifier si l'URL est présente
    if not url:
        return jsonify({'error': 'URL manquante'}), 400
    
    # Extraire le contenu de l'URL
    content = scrape_url(url)
    
    # Retourner le contenu
    return jsonify({'content': content})

def scrape_url(url):
    """
    Lit et extrait le contenu basique d'une URL donnée
    """
    try:
        # Faire la requête HTTP
        response = requests.get(url)
        response.raise_for_status()  # Vérifie si la requête a réussi
        
        # Parser le contenu HTML
        soup = BeautifulSoup(response.text, 'html.parser')
        
        # Afficher le nombre de textes, d'images, de liens internes, liens externes et de vidéos, de tableaux, de formulaires
        text_count = len(soup.get_text())
        image_count = len(soup.find_all('img'))
        internal_links = [a['href'] for a in soup.find_all('a', href=True) if url in a['href']]
        external_links = [a['href'] for a in soup.find_all('a', href=True) if url not in a['href'] and a['href'].startswith('http')]

        internal_link_count = len(internal_links)
        external_link_count = len(external_links)

        video_count = len(soup.find_all('video'))
        table_count = len(soup.find_all('table'))
        form_count = len(soup.find_all('form'))

        # Retourner le contenu
        return {
            'text_count': text_count,
            'image_count': image_count,
            'internal_link_count': internal_link_count,
            'external_link_count': external_link_count,
            'video_count': video_count,
            'table_count': table_count,
            'form_count': form_count,
        }
        
        
    except requests.RequestException as e:
        return f"Erreur lors de la requête: {e}"


if __name__ == "__main__":
    app.run(debug=True)

    