import dash
from dash import html, dcc, Input, Output, State
import networkx as nx
import plotly.graph_objects as go

# Inițializare aplicație
app = dash.Dash(__name__)

# Definire stiluri CSS
styles = {
    'container': {
        'max-width': '1200px',
        'margin': '0 auto',
        'padding': '20px'
    },
    'title': {
        'text-align': 'center',
        'margin-bottom': '20px'
    },
    'card': {
        'border': '1px solid #ddd',
        'border-radius': '5px',
        'padding': '15px',
        'margin-bottom': '20px',
        'background-color': 'white'
    },
    'input': {
        'width': '100%',
        'padding': '8px',
        'margin-bottom': '10px',
        'border': '1px solid #ddd',
        'border-radius': '4px'
    },
    'button': {
        'background-color': '#007bff',
        'color': 'white',
        'padding': '8px 15px',
        'border': 'none',
        'border-radius': '4px',
        'cursor': 'pointer',
        'margin-bottom': '10px'
    }
}

# Layout-ul aplicației
app.layout = html.Div(style=styles['container'], children=[
    html.H1("Vizualizare Graf Interactiv", style=styles['title']),
    
    # Secțiunea pentru adăugarea nodurilor
    html.Div(style=styles['card'], children=[
        html.H4("Adaugă Nod"),
        dcc.Input(
            id="node-name",
            placeholder="Nume nod",
            style=styles['input']
        ),
        dcc.Input(
            id="node-index",
            placeholder="Index nod",
            type="number",
            style=styles['input']
        ),
        html.Button(
            "Adaugă Nod",
            id="add-node",
            style=styles['button']
        ),
    ]),
    
    # Secțiunea pentru adăugarea legăturilor
    html.Div(style=styles['card'], children=[
        html.H4("Adaugă Legătură"),
        dcc.Dropdown(
            id="source-node",
            placeholder="Nod sursă",
            style={'margin-bottom': '10px'}
        ),
        dcc.Dropdown(
            id="target-node",
            placeholder="Nod destinație",
            style={'margin-bottom': '10px'}
        ),
        html.Button(
            "Adaugă Legătură",
            id="add-edge",
            style=dict(styles['button'], **{'background-color': '#28a745'})
        ),
    ]),
    
    # Graful
    dcc.Graph(id="network-graph", style={'height': '600px'}),
    
    # Store pentru datele grafului
    dcc.Store(id="graph-data", data={'nodes': [], 'edges': []}),
])

# Callback pentru actualizarea opțiunilor din dropdown-uri
@app.callback(
    [Output("source-node", "options"),
     Output("target-node", "options")],
    [Input("graph-data", "data")]
)
def update_dropdowns(data):
    nodes = data['nodes']
    options = [{'label': f"{node['name']} (Index: {node['index']})", 'value': node['name']} 
               for node in nodes]
    return options, options

# Callback pentru adăugarea nodurilor
@app.callback(
    [Output("graph-data", "data"),
     Output("node-name", "value"),
     Output("node-index", "value")],
    [Input("add-node", "n_clicks")],
    [State("node-name", "value"),
     State("node-index", "value"),
     State("graph-data", "data")],
    prevent_initial_call=True
)
def add_node(n_clicks, name, index, data):
    if name and index is not None:
        data['nodes'].append({'name': name, 'index': index})
        return data, "", None
    return data, dash.no_update, dash.no_update

# Callback pentru adăugarea legăturilor
@app.callback(
    [Output("graph-data", "data", allow_duplicate=True),
     Output("source-node", "value"),
     Output("target-node", "value")],
    [Input("add-edge", "n_clicks")],
    [State("source-node", "value"),
     State("target-node", "value"),
     State("graph-data", "data")],
    prevent_initial_call=True
)
def add_edge(n_clicks, source, target, data):
    if source and target:
        data['edges'].append({'source': source, 'target': target})
        return data, None, None
    return data, dash.no_update, dash.no_update

# Callback pentru actualizarea grafului
@app.callback(
    Output("network-graph", "figure"),
    [Input("graph-data", "data")]
)
def update_graph(data):
    # Creare graf NetworkX
    G = nx.Graph()
    
    # Adăugare noduri
    for node in data['nodes']:
        G.add_node(node['name'], index=node['index'])
    
    # Adăugare legături
    for edge in data['edges']:
        G.add_edge(edge['source'], edge['target'])
    
    # Calculare layout
    pos = nx.spring_layout(G)
    
    # Creare trasee pentru legături
    edge_x = []
    edge_y = []
    for edge in G.edges():
        x0, y0 = pos[edge[0]]
        x1, y1 = pos[edge[1]]
        edge_x.extend([x0, x1, None])
        edge_y.extend([y0, y1, None])
    
    # Creare figura Plotly
    fig = go.Figure()
    
    # Adăugare legături
    fig.add_trace(go.Scatter(
        x=edge_x, y=edge_y,
        line=dict(width=1, color='#888'),
        hoverinfo='none',
        mode='lines'
    ))
    
    # Adăugare noduri
    node_x = [pos[node][0] for node in G.nodes()]
    node_y = [pos[node][1] for node in G.nodes()]
    node_text = [f"Nume: {node}<br>Index: {G.nodes[node]['index']}" for node in G.nodes()]
    
    fig.add_trace(go.Scatter(
        x=node_x, y=node_y,
        mode='markers+text',
        hoverinfo='text',
        text=[node for node in G.nodes()],
        hovertext=node_text,
        marker=dict(
            size=20,
            color='#1f77b4',
            line_width=2
        )
    ))
    
    # Actualizare layout
    fig.update_layout(
        showlegend=False,
        hovermode='closest',
        margin=dict(b=20,l=5,r=5,t=40),
        xaxis=dict(showgrid=False, zeroline=False, showticklabels=False),
        yaxis=dict(showgrid=False, zeroline=False, showticklabels=False)
    )
    
    return fig

if __name__ == '__main__':
    app.run_server(debug=True)