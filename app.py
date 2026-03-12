import streamlit as st
import networkx as nx
import numpy as np
import matplotlib.pyplot as plt
import random

import time

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
    """Runs Monte Carlo simulation for network reliability with a progress bar."""
    connected_count = 0
    edges = list(G.edges())
    
    # Check if we are in a Streamlit context
    progress_bar = st.empty()
    status_text = st.empty()
    
    for i in range(trials):
        # Create a copy of the graph for each trial
        G_trial = G.copy()
        for u, v in edges:
            if random.random() < q:
                G_trial.remove_edge(u, v)
        
        # Check if still connected
        if nx.is_connected(G_trial):
            connected_count += 1
        
        # Update progress bar occasionally
        if (i + 1) % max(1, trials // 10) == 0:
            progress_bar.progress((i + 1) / trials)
            status_text.text(f"Simulating Trial {i+1}/{trials}...")
            # No sleep here to keep it fast, the 10% frequency reduces flickering
            
    progress_bar.empty()
    status_text.empty()
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
pos = nx.spring_layout(G, k=0.5) # Calculate layout once
reliability = run_monte_carlo(G, q_fail, n_trials)

st.subheader(f"Results for {graph_type} Graph")
col1, col2 = st.columns(2)

with col1:
    st.metric("Estimated Reliability", f"{reliability:.2%}")
    st.write(f"Number of Nodes: {n_nodes}")
    st.write(f"Number of Edges: {G.number_of_edges()}")

with col2:
    # Plot the original graph
    fig_main, ax_main = plt.subplots(figsize=(8, 8))
    # Consistent limits for main plot too
    ax_main.set_xlim(-1.2, 1.2)
    ax_main.set_ylim(-1.2, 1.2)
    
    # Highlight bridges
    bridges = list(nx.bridges(G))
    edge_colors = ['red' if (u, v) in bridges or (v, u) in bridges else 'gray' for u, v in G.edges()]
    
    # Dynamic node size based on node count
    node_size = max(100, 500 - (n_nodes * 8))
    
    nx.draw(G, pos, with_labels=True, node_color='skyblue', node_size=node_size, edge_color=edge_colors, width=2.5, font_size=8, font_weight='bold', ax=ax_main)
    st.pyplot(fig_main)
    plt.close(fig_main)
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
st.subheader("Simulate One Failure Case (Animated)")
if st.button("Simulate One Trial"):
    # First, draw the initial state
    placeholder = st.empty()
    edges = list(G.edges())
    random.shuffle(edges) # Randomize order for effect
    
    current_edges_status = {edge: 'green' for edge in edges}
    failed_edges = []
    
    # Dynamic node size based on node count
    node_size = max(100, 500 - (n_nodes * 8))

    # Animate the "coin flip" for each edge
    with placeholder.container():
        fig_trial, ax_trial = plt.subplots(figsize=(8, 8))
        plot_placeholder = st.empty()
        
        for i, edge in enumerate(edges):
            u, v = edge
            if random.random() < q_fail:
                current_edges_status[edge] = 'lightcoral'
                failed_edges.append(edge)
            
            # Only re-draw every few edges or for the first/last few to balance speed
            if i % max(1, len(edges)//5) == 0 or i == len(edges)-1:
                ax_trial.clear()
                # Use a consistent axis limit to prevent jumping
                ax_trial.set_xlim(-1.2, 1.2)
                ax_trial.set_ylim(-1.2, 1.2)
                edge_colors = [current_edges_status[e] if e in current_edges_status else current_edges_status[(e[1], e[0])] for e in G.edges()]
                nx.draw(G, pos, with_labels=True, node_color='skyblue', node_size=node_size, edge_color=edge_colors, width=2.5, font_size=8, font_weight='bold', ax=ax_trial)
                plot_placeholder.pyplot(fig_trial)
                time.sleep(0.3) # Give time for class to see the failure
        plt.close(fig_trial)
            
    # Final Connectivity Check
    G_trial = G.copy()
    G_trial.remove_edges_from(failed_edges)
    is_conn = nx.is_connected(G_trial)
    
    if is_conn:
        st.success("Network remained connected!")
    else:
        st.error("Network disconnected!")
    st.write(f"Failed edges: {len(failed_edges)}")
    st.write(f"Total edges: {G.number_of_edges()}")
