import streamlit as st
import networkx as nx
import numpy as np
import matplotlib.pyplot as plt
import random

# --- Helper Functions ---

def generate_graph(graph_type, n):
    """Generates a graph based on type and number of nodes."""
    if graph_type == "Tree":
        return nx.random_labeled_tree(n)
    elif graph_type == "Cycle":
        return nx.cycle_graph(n)
    elif graph_type == "Complete":
        return nx.complete_graph(n)
    return nx.empty_graph(n)

def run_monte_carlo(G, q, trials):
    """Runs Monte Carlo simulation for network reliability."""
    connected_count = 0
    edges = list(G.edges())
    
    for _ in range(trials):
        # Create a copy of the graph for each trial
        G_trial = G.copy()
        for u, v in edges:
            if random.random() < q:
                G_trial.remove_edge(u, v)
        
        # Check if still connected
        if nx.is_connected(G_trial):
            connected_count += 1
            
    return connected_count / trials

# --- Streamlit UI ---

st.title("Network Reliability Monte Carlo Visualizer")
st.markdown("""
This app simulates **network reliability** under random edge failures. 
A network is considered 'reliable' if it remains connected after some edges fail.
""")

# Sidebar controls
st.sidebar.header("Configuration")
graph_type = st.sidebar.selectbox("Select Graph Type", ["Tree", "Cycle", "Complete"])
n_nodes = st.sidebar.slider("Number of Nodes (n)", min_value=3, max_value=50, value=8)
q_fail = st.sidebar.slider("Edge Failure Probability (q)", min_value=0.0, max_value=1.0, value=0.1, step=0.05)
n_trials = st.sidebar.slider("Monte Carlo Trials", min_value=10, max_value=2000, value=100, step=10)

# Main Content
G = generate_graph(graph_type, n_nodes)
reliability = run_monte_carlo(G, q_fail, n_trials)

st.subheader(f"Results for {graph_type} Graph")
col1, col2 = st.columns(2)

with col1:
    st.metric("Estimated Reliability", f"{reliability:.2%}")
    st.write(f"Number of Nodes: {n_nodes}")
    st.write(f"Number of Edges: {G.number_of_edges()}")

with col2:
    # Plot the original graph
    fig, ax = plt.subplots(figsize=(8, 8))
    pos = nx.spring_layout(G, k=0.5) # Increased k for more space between nodes
    
    # Highlight bridges
    bridges = list(nx.bridges(G))
    edge_colors = ['red' if (u, v) in bridges or (v, u) in bridges else 'gray' for u, v in G.edges()]
    
    # Dynamic node size based on node count
    node_size = max(100, 500 - (n_nodes * 8))
    
    nx.draw(G, pos, with_labels=True, node_color='skyblue', node_size=node_size, edge_color=edge_colors, width=2.5, font_size=8, font_weight='bold', ax=ax)
    st.pyplot(fig)
    if len(bridges) > 0:
        st.caption("Bridges are highlighted in red")

# Theory connection
st.divider()
st.subheader("Reliability Curve")

# Generate the curve data
q_values = np.linspace(0, 1, 11)
reliability_curve = []
for q in q_values:
    # Run a smaller number of trials for the curve for speed
    reliability_curve.append(run_monte_carlo(G, q, min(n_trials, 50)))

fig_curve, ax_curve = plt.subplots(figsize=(10, 4))
ax_curve.plot(q_values, reliability_curve, marker='o', linestyle='-', color='blue')
ax_curve.set_xlabel("Failure Probability (q)")
ax_curve.set_ylabel("Reliability")
ax_curve.set_title("Network Reliability vs. Failure Probability")
ax_curve.grid(True)
st.pyplot(fig_curve)

st.divider()
st.subheader("Simulate One Failure Case")
if st.button("Simulate One Trial"):
    G_trial = G.copy()
    failed_edges = []
    for u, v in G.edges():
        if random.random() < q_fail:
            G_trial.remove_edge(u, v)
            failed_edges.append((u, v))
            
    fig_trial, ax_trial = plt.subplots(figsize=(10, 10))
    is_conn = nx.is_connected(G_trial)
    
    # Use the same layout for consistency
    edge_colors = ['green' if (u, v) in G_trial.edges() or (v, u) in G_trial.edges() else 'lightcoral' for u, v in G.edges()]
    
    # Dynamic node size based on node count
    node_size = max(100, 500 - (n_nodes * 8))
    
    nx.draw(G, pos, with_labels=True, node_color='skyblue', node_size=node_size, edge_color=edge_colors, width=2.5, font_size=8, font_weight='bold', ax=ax_trial)
    st.pyplot(fig_trial)
    
    if is_conn:
        st.success("Network remained connected!")
    else:
        st.error("Network disconnected!")
    st.write(f"Failed edges: {len(failed_edges)}")
    st.write(f"Total edges: {G.number_of_edges()}")

st.divider()
st.subheader("Theory Check")
bridges = list(nx.bridges(G))
st.write(f"Number of bridges (cut-edges): {len(bridges)}")
if len(bridges) > 0:
    st.info(f"Theory: Reliability is at most (1-q)^k = {(1-q_fail)**len(bridges):.2%}")
else:
    st.info("This graph has no bridges. It is more robust than a tree!")
