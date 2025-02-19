from flask import Flask, request, jsonify, render_template
import os
from scraper import scrape_url
from graph import generate_graph
from history import history, add_to_history, get_history, clear_history

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

    # Ajouter à l'historique avec la date et l'heure
    add_to_history(url)

    return jsonify({
        'content': content,
        'graph_url': f'/static/{graph_path}',  # URL du graphe à afficher dans l'iframe
        'history': get_history()  # Ajouter l'historique à la réponse
    })

@app.route('/history')
def history_route():
    return jsonify({'history': get_history()})

@app.route('/clear_history', methods=['POST'])
def clear_history_route():
    clear_history()
    return jsonify({'message': 'Historique vidé avec succès'})

if __name__ == "__main__":
    if not os.path.exists('static'):
        os.makedirs('static')
    app.run(debug=True)
