import streamlit as st
import networkx as nx
import numpy as np
import matplotlib.pyplot as plt
import random

import time

# --- Streamlit Configuration ---
st.set_page_config(page_title="Network Reliability Visualizer", layout="wide")

# --- Helper Functions ---

@st.cache_data
def generate_graph(graph_type, n):
    """Generates a graph based on type and number of nodes."""
    if graph_type == "Tree":
        return nx.random_labeled_tree(n)
    elif graph_type == "Cycle":
        return nx.cycle_graph(n)
    elif graph_type == "Complete":
        return nx.complete_graph(n)
    return nx.empty_graph(n)

@st.cache_data
def _run_monte_carlo_core(edges_list, n_nodes, q, trials):
    """Core simulation logic, cached for speed and to avoid flickering."""
    connected_count = 0
    # Re-create a skeleton graph to check connectivity
    G_base = nx.Graph()
    G_base.add_nodes_from(range(n_nodes))
    G_base.add_edges_from(edges_list)
    
    for i in range(trials):
        G_trial = G_base.copy()
        # Randomly remove edges
        for u, v in edges_list:
            if random.random() < q:
                G_trial.remove_edge(u, v)
        
        if nx.is_connected(G_trial):
            connected_count += 1
            
    return connected_count / trials

def run_monte_carlo(G, q, trials, progress_elements=None):
    """Wrapper that handles optional progress bar updates."""
    if progress_elements is None:
        # If no progress needed, just call the core logic
        return _run_monte_carlo_core(list(G.edges()), len(G.nodes()), q, trials)
    
    progress_bar, status_text = progress_elements
    connected_count = 0
    edges = list(G.edges())
    n_nodes = len(G.nodes())
    
    # Run in chunks to show progress while still benefiting from core logic for small batches
    # or just run the whole thing if trials are small.
    # To keep it simple and responsive, we'll run in 10 steps.
    steps = 10
    trials_per_step = max(1, trials // steps)
    total_connected = 0
    
    for step in range(steps):
        current_trials = trials_per_step if step < steps - 1 else trials - (trials_per_step * step)
        if current_trials <= 0: continue
        
        # We don't cache the chunks because the seed changes, 
        # but the main call for the curve will use the cached core function above.
        # Actually, for the main simulation with progress, we don't necessarily need caching 
        # because the progress bar IS the interaction.
        # But we want the CURVE to be cached.
        
        # Core logic for a single trial loop (not cached here to allow progress)
        step_connected = 0
        G_base = nx.Graph()
        G_base.add_nodes_from(range(n_nodes))
        G_base.add_edges_from(edges)
        
        for _ in range(current_trials):
            G_trial = G_base.copy()
            for u, v in edges:
                if random.random() < q:
                    G_trial.remove_edge(u, v)
            if nx.is_connected(G_trial):
                step_connected += 1
        
        total_connected += step_connected
        
        # Update progress bar
        progress = (step + 1) / steps
        progress_bar.progress(progress)
        status_text.text(f"Simulating Trial {(step + 1) * trials_per_step}/{trials}...")
        
    return total_connected / trials

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

run_sim = st.sidebar.button("Run Simulation", type="primary", use_container_width=True)

# Initialize session state for results
if 'reliability' not in st.session_state:
    st.session_state.reliability = None
if 'reliability_curve' not in st.session_state:
    st.session_state.reliability_curve = None
if 'last_config' not in st.session_state:
    st.session_state.last_config = None

current_config = (graph_type, n_nodes, q_fail, n_trials)

# Main Content
G = generate_graph(graph_type, n_nodes)
pos = nx.spring_layout(G, k=0.5, seed=42) # Calculate layout once with seed for consistency

# Check if we should run or if config changed
if run_sim or (st.session_state.reliability is None):
    # Main Reliability Calculation with Progress Bar (in Sidebar to avoid layout jumps)
    with st.sidebar:
        st.divider()
        st.write("**Simulation Progress**")
        p_bar = st.progress(0)
        p_text = st.empty()
        st.session_state.reliability = run_monte_carlo(G, q_fail, n_trials, progress_elements=(p_bar, p_text))
        p_text.text("Simulation Complete!")
        
        # Also pre-calculate the curve for the results section
        q_values = np.linspace(0, 1, 11)
        curve_data = []
        for q in q_values:
            curve_data.append(run_monte_carlo(G, q, min(n_trials, 50)))
        st.session_state.reliability_curve = curve_data
        st.session_state.last_config = current_config

# Display Results if available
if st.session_state.reliability is not None:
    # If the config has changed but we haven't clicked run, show a warning
    if st.session_state.last_config != current_config:
        st.warning("Configuration has changed. Click 'Run Simulation' to update results.")

    st.subheader(f"Results for {graph_type} Graph")
    col1, col2 = st.columns([1, 3])

    with col1:
        st.metric("Estimated Reliability", f"{st.session_state.reliability:.2%}")
        st.write(f"Number of Nodes: {n_nodes}")
        st.write(f"Number of Edges: {G.number_of_edges()}")

    with col2:
        # Plot the original graph
        fig_main, ax_main = plt.subplots(figsize=(15, 8))
        ax_main.set_xlim(-1.2, 1.2)
        ax_main.set_ylim(-1.2, 1.2)
        
        bridges = list(nx.bridges(G))
        edge_colors = ['red' if (u, v) in bridges or (v, u) in bridges else 'gray' for u, v in G.edges()]
        node_size = max(100, 500 - (n_nodes * 8))
        
        nx.draw(G, pos, with_labels=True, node_color='skyblue', node_size=node_size, edge_color=edge_colors, width=2.5, font_size=8, font_weight='bold', ax=ax_main)
        st.pyplot(fig_main, width="stretch")
        plt.close(fig_main)
        if len(bridges) > 0:
            st.caption("Bridges are highlighted in red")

    # Theory connection
    st.divider()
    st.subheader("Reliability Curve")

    fig_curve, ax_curve = plt.subplots(figsize=(12, 5))
    q_values = np.linspace(0, 1, 11)
    ax_curve.plot(q_values, st.session_state.reliability_curve, marker='o', linestyle='-', color='blue')
    ax_curve.set_xlabel("Failure Probability (q)")
    ax_curve.set_ylabel("Reliability")
    ax_curve.set_title("Network Reliability vs. Failure Probability")
    ax_curve.grid(True)
    st.pyplot(fig_curve, width="stretch")
else:
    st.info("Adjust the configuration and click 'Run Simulation' to start.")

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
        col_trial1, col_trial2 = st.columns(2)
        with col_trial1:
            st.write("**Simulation Process**")
            plot_placeholder1 = st.empty()
        with col_trial2:
            st.write("**Current Resulting Network**")
            plot_placeholder2 = st.empty()
        
        # Create persistent figures to avoid re-creation overhead
        fig_trial1, ax_trial1 = plt.subplots(figsize=(10, 10))
        fig_trial2, ax_trial2 = plt.subplots(figsize=(10, 10))
        
        for i, edge in enumerate(edges):
            u, v = edge
            if random.random() < q_fail:
                current_edges_status[edge] = 'lightcoral'
                failed_edges.append(edge)
            
            # Only re-draw every few edges or for the first/last few to balance speed
            if i % max(1, len(edges)//5) == 0 or i == len(edges)-1:
                # --- Plot 1: Simulation Process ---
                ax_trial1.clear()
                ax_trial1.set_xlim(-1.2, 1.2)
                ax_trial1.set_ylim(-1.2, 1.2)
                ax_trial1.set_axis_off()
                
                # Construct a temporary graph to find current connectivity
                G_temp = G.copy()
                G_temp.remove_edges_from(failed_edges)
                
                # Determine which nodes are 'cut off' (not in the largest component)
                if len(G_temp.nodes()) > 0:
                    components = sorted(nx.connected_components(G_temp), key=len, reverse=True)
                    largest_component = components[0] if components else set()
                    node_colors1 = ['skyblue' if n in largest_component else 'lightcoral' for n in G.nodes()]
                    
                    # For Plot 2: Different colors for different components
                    # Generate a color map for components
                    component_map = {}
                    colors = plt.cm.tab20(np.linspace(0, 1, len(components)))
                    for idx, comp in enumerate(components):
                        for node in comp:
                            component_map[node] = colors[idx]
                    node_colors2 = [component_map.get(n, 'lightcoral') for n in G.nodes()]
                else:
                    node_colors1 = ['lightcoral'] * len(G.nodes())
                    node_colors2 = ['lightcoral'] * len(G.nodes())
                
                edge_colors = [current_edges_status[e] if e in current_edges_status else current_edges_status[(e[1], e[0])] for e in G.edges()]
                nx.draw(G, pos, with_labels=True, node_color=node_colors1, node_size=node_size, edge_color=edge_colors, width=2.5, font_size=8, font_weight='bold', ax=ax_trial1)
                plot_placeholder1.pyplot(fig_trial1, width="stretch")
                
                # --- Plot 2: Resulting Components ---
                ax_trial2.clear()
                ax_trial2.set_xlim(-1.2, 1.2)
                ax_trial2.set_ylim(-1.2, 1.2)
                ax_trial2.set_axis_off()
                
                # Draw ONLY the edges that have not failed
                survived_edges = [e for e in G.edges() if e not in failed_edges and (e[1], e[0]) not in failed_edges]
                nx.draw_networkx_nodes(G, pos, node_color=node_colors2, node_size=node_size, ax=ax_trial2)
                nx.draw_networkx_labels(G, pos, font_size=8, font_weight='bold', ax=ax_trial2)
                nx.draw_networkx_edges(G, pos, edgelist=survived_edges, width=2.5, edge_color='green', ax=ax_trial2)
                
                plot_placeholder2.pyplot(fig_trial2, width="stretch")
                
                time.sleep(0.3) # Give time for class to see the failure
        
        plt.close(fig_trial1)
        plt.close(fig_trial2)
            
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
