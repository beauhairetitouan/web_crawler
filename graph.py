from pyvis.network import Network

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
