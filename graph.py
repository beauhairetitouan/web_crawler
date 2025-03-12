from pyvis.network import Network
from urllib.parse import urlparse

def generate_graph(graph_data):
    net = Network(height="600px", width="100%", directed=True, font_color="black", bgcolor="white")

    nodes = set()
    positions = {}

    for node, links in graph_data.items():
        parsed_main = urlparse(node)
        main_domain = parsed_main.netloc

        # Ajouter le nœud principal (centré)
        if node not in nodes:
            net.add_node(node, label=f"[PAGE PRINCIPALE]\n{node}", color='red', size=40, shape="ellipse", font={"size": 18, "bold": True})
            nodes.add(node)
            positions[node] = (0, 0)

        

        # Placement vertical des liens
        num_links = len(links)
        start_y = -(num_links * 25)
        y_step = 50
        x_internal =  -400  # Espacement horizontal plus grand
        x_external = 400

        for i, link in enumerate(links):
            parsed_link = urlparse(link)
            link_domain = parsed_link.netloc

            if link_domain == main_domain:
                link_color = 'blue'
                node_shape = "dot"
                x_pos = x_internal
            else:
                link_color = 'green'
                node_shape = "square"
                x_pos = x_external

            y_pos = start_y + (i * y_step)

            if link not in nodes:
                net.add_node(link, label=link, color=link_color, size=20, shape=node_shape, font={"size": 12})
                nodes.add(link)
                positions[link] = (x_pos, y_pos)

            # Ajouter l’arête avec le texte du lien
            net.add_edge(node, link, color=link_color, width=1.5, smooth=True, title=f"Lien : {link}")

    # Appliquer la disposition des nœuds
    for node, (x, y) in positions.items():
        net.get_node(node)["x"] = x
        net.get_node(node)["y"] = y

    # Ajouter une légende
    legend_html = """
    <div style="position: fixed; top: 10px; left: 10px; background: white; padding: 10px; border-radius: 10px; border: 1px solid black; font-family: Arial, sans-serif;">
        <b>Légende du graphe</b><br>
        🔴 <b>Page principale</b><br>
        🔵 <b>Liens internes</b><br>
        🟢 <b>Liens externes</b><br>
    </div>
    """

    
    net.set_options("""
{
    "nodes": {
        "borderWidth": 2,
        "shadow": true
    },
    "edges": {
        "color": "gray",
        "smooth": {
            "type": "dynamic"
        }
    },
    "physics": {
        "enabled": false
    },
    "interaction": {
        "zoomView": true,
        "dragView": true,
        "multiselect": true,
        "navigationButtons": true,
        "keyboard": {
            "enabled": true,
            "bindToWindow": true
        }
    }
}
""")



    graph_path = 'graph.html'
    net.save_graph(f'static/{graph_path}')

    # Ajouter la légende au fichier HTML
    with open(f'static/{graph_path}', "a", encoding="utf-8") as file:
        file.write(legend_html)

    return graph_path
