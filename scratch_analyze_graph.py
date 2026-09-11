import json
import os

try:
    with open('graphify-out/graph.json', 'r') as f:
        data = json.load(f)
    
    nodes = data.get('nodes', [])
    edges = data.get('edges', [])
    
    print(f"Total Nodes: {len(nodes)}")
    print(f"Total Edges: {len(edges)}")
    
    # Analyze node types
    node_types = {}
    for node in nodes:
        t = node.get('type', 'unknown')
        node_types[t] = node_types.get(t, 0) + 1
        
    print(f"Node Types: {node_types}")
    
    # Get top communities or most connected nodes
    degrees = {}
    for edge in edges:
        s = edge.get('source')
        t = edge.get('target')
        degrees[s] = degrees.get(s, 0) + 1
        degrees[t] = degrees.get(t, 0) + 1
        
    sorted_nodes = sorted(degrees.items(), key=lambda x: x[1], reverse=True)[:20]
    print("Top 20 most connected nodes:")
    for nid, deg in sorted_nodes:
        # find node name
        name = next((n.get('name') for n in nodes if n.get('id') == nid), nid)
        print(f"  - {name} ({deg} edges)")
        
except Exception as e:
    print(f"Error: {e}")
