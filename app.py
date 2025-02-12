import requests
from bs4 import BeautifulSoup
from flask import Flask, request, jsonify, render_template
from pyvis.network import Network
import os

app = Flask(__name__)

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/scrape', methods=['POST'])
def scrape():
    data = request.get_json()
    url = data.get('url')
    
    if not url:
        return jsonify({'error': 'URL manquante'}), 400

    # Scraping du site
    content, graph_data = scrape_url(url)

    # Génération du graphe interactif
    graph_path = generate_graph(graph_data)

    return jsonify({
        'content': content,
        'graph_url': f'/static/{graph_path}'  # URL du graphe à afficher dans l'iframe
    })

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

def generate_graph(graph_data):
    net = Network(height="500px", width="100%", directed=True)

    
    for node, links in graph_data.items():
        net.add_node(node, label=node, color='red', size=30, font_size=16)
        for link in links:
            net.add_node(link, label=link)
            net.add_edge(node, link)

        # de gauche à droite
    net.set_options("""
    var options = {
        "physics": {
            "enabled": false
        },
        "stabilization": {
            "iterations": 200,
            "updateInterval": 25
        },
        "layout": {
            "hierarchical": {
                "direction": "LR",
                "sortMethod": "directed"
            }
        }
    }
    """)
    
    graph_path = 'graph.html'
    net.save_graph(f'static/{graph_path}')
    return graph_path

if __name__ == "__main__":
    if not os.path.exists('static'):
        os.makedirs('static')
    app.run(debug=True)
