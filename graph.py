from pyvis.network import Network
from urllib.parse import urlparse

def generate_graph(graph_data):
    # Débogage: afficher les clés du graph_data pour voir ce qui est collecté
    print(f"Nombre total de nœuds dans graph_data: {len(graph_data)}")
    print(f"Premier nœud: {next(iter(graph_data))}")
    
    net = Network(height="600px", width="100%", directed=True, font_color="black", bgcolor="white")
    nodes = set()
    positions = {}
    
    # Trouver le nœud principal (premier nœud dans graph_data)
    main_node = None
    for node in graph_data:
        main_node = node
        break
    
    if main_node is None:
        print("Aucun nœud principal trouvé dans graph_data")
        return "error.html"
    
    print(f"Nœud principal: {main_node}")
    print(f"Nombre de liens depuis le nœud principal: {len(graph_data.get(main_node, []))}")
    
    # Initialiser les ensembles pour chaque profondeur
    depth_1_nodes = set()
    depth_2_nodes = set()
    
    # Remplir les ensembles en fonction de la profondeur
    if main_node:
        # Liens directs depuis la page principale (profondeur 1)
        depth_1_nodes = set(graph_data.get(main_node, []))
        print(f"Nombre de nœuds de profondeur 1: {len(depth_1_nodes)}")
        
        # Collecter les liens de profondeur 2
        for node in depth_1_nodes:
            if node in graph_data:
                for link in graph_data[node]:
                    if link != main_node and link not in depth_1_nodes:
                        depth_2_nodes.add(link)
        
        print(f"Nombre de nœuds de profondeur 2: {len(depth_2_nodes)}")
    
    parsed_main = urlparse(main_node)
    main_domain = parsed_main.netloc
    
    # Ajouter le nœud principal
    if main_node not in nodes:
        net.add_node(main_node, label=f"[PAGE PRINCIPALE]\n{main_node}", color='red', size=40, shape="ellipse", font={"size": 18, "bold": True})
        nodes.add(main_node)
        positions[main_node] = (0, 0)
    
    # Placer les nœuds de profondeur 1
    num_depth_1 = len(depth_1_nodes)
    start_y_depth_1 = -(num_depth_1 * 30)
    y_step_depth_1 = 60
    
    internal_depth_1 = []
    external_depth_1 = []
    
    for link in depth_1_nodes:
        parsed_link = urlparse(link)
        link_domain = parsed_link.netloc
        if link_domain == main_domain:
            internal_depth_1.append(link)
        else:
            external_depth_1.append(link)
    
    # Ajouter les liens internes de profondeur 1
    for i, link in enumerate(internal_depth_1):
        y_pos = start_y_depth_1 + (i * y_step_depth_1)
        if link not in nodes:
            net.add_node(link, label=link, color='blue', size=20, shape="dot", font={"size": 12})
            nodes.add(link)
            positions[link] = (-400, y_pos)
        
        net.add_edge(main_node, link, color='blue', width=1.5, smooth=True, title=f"Lien : {link}")
    
    # Ajouter les liens externes de profondeur 1
    for i, link in enumerate(external_depth_1):
        y_pos = start_y_depth_1 + (i * y_step_depth_1)
        if link not in nodes:
            net.add_node(link, label=link, color='green', size=20, shape="square", font={"size": 12})
            nodes.add(link)
            positions[link] = (400, y_pos)
        
        net.add_edge(main_node, link, color='green', width=1.5, smooth=True, title=f"Lien : {link}")
    
    # Placer les nœuds de profondeur 2
    num_depth_2 = len(depth_2_nodes)
    start_y_depth_2 = -(num_depth_2 * 20)
    y_step_depth_2 = 40
    x_depth_2 = -800
    
    for i, link in enumerate(depth_2_nodes):
        parsed_link = urlparse(link)
        link_domain = parsed_link.netloc
        
        if link_domain == main_domain:
            link_color = 'purple'
            node_shape = "dot"
        else:
            link_color = 'green'
            node_shape = "square"
        
        y_pos = start_y_depth_2 + (i * y_step_depth_2)
        if link not in nodes:
            net.add_node(link, label=link, color=link_color, size=15, shape=node_shape, font={"size": 10})
            nodes.add(link)
            positions[link] = (x_depth_2, y_pos)
        
        # Trouver tous les parents de profondeur 1 pour ce nœud
        for d1_node in depth_1_nodes:
            if d1_node in graph_data and link in graph_data[d1_node]:
                net.add_edge(d1_node, link, color='gray', width=1, smooth=True, title=f"Lien : {link}")
    
    print(f"Nombre total de nœuds ajoutés au graphe: {len(nodes)}")
    
    # Appliquer les positions des nœuds
    for node, (x, y) in positions.items():
        net.get_node(node)["x"] = x
        net.get_node(node)["y"] = y
    
    # Ajouter la légende
    legend_html = """
    <div style="position: fixed; top: 10px; left: 10px; background: white; padding: 10px; border-radius: 10px; border: 1px solid black; font-family: Arial, sans-serif;">
        <b>Légende du graphe</b><br>
        🔴 <b>Page principale (Profondeur 0)</b><br>
        🔵 <b>Liens internes (Profondeur 1)</b><br>
        🟣 <b>Liens internes (Profondeur 2)</b><br>
        🟢 <b>Liens externes</b><br>
    </div>
    """
    
    # Configuration du graphe
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
    
    # Sauvegarder le graphe
    graph_path = 'graph.html'
    net.save_graph(f'static/{graph_path}')
    
    # Ajouter la légende au fichier HTML
    with open(f'static/{graph_path}', "a", encoding="utf-8") as file:
        file.write(legend_html)
    
    return graph_path