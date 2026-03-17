import streamlit as st
import networkx as nx
import numpy as np
import matplotlib.pyplot as plt
import random
import time

# --- Streamlit Configuration ---
st.set_page_config(page_title="Monte Carlo Simulation Suite", layout="wide")

# Global CSS to increase font sizes
st.markdown("""
    <style>
    /* Main titles and subheaders */
    h1 { font-size: 3rem !important; }
    h2 { font-size: 2.2rem !important; }
    h3 { font-size: 1.8rem !important; }
    
    /* Normal text and markdown */
    p, li, span, div { font-size: 1.2rem !important; }
    
    /* Metrics */
    [data-testid="stMetricValue"] { 
        font-size: 4rem !important; 
        font-weight: bold !important; 
        color: #007bff !important;
    }
    [data-testid="stMetricLabel"] { font-size: 1.5rem !important; }
    
    /* Sidebar text */
    [data-testid="stSidebar"] p, [data-testid="stSidebar"] span, [data-testid="stSidebar"] label {
        font-size: 1.2rem !important;
    }
    
    /* Button text */
    button p { font-size: 1.2rem !important; font-weight: bold !important; }
    
    /* Help text and captions */
    .stCaption { font-size: 1rem !important; }
    </style>
    """, unsafe_allow_html=True)

# --- Navigation ---
st.sidebar.title("Simulation Selection")
app_mode = st.sidebar.radio("Choose a Simulation:", ["Network Reliability", "Approximating Pi"])

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
    elif graph_type == "Degree-Constrained Graph (3 ≤ deg ≤ n−2)":
        if n < 5:
            return nx.complete_graph(n)
        
        while True:
            G = nx.erdos_renyi_graph(n, 0.5)
            if nx.is_connected(G):
                degrees = [d for n_node, d in G.degree()]
                if min(degrees) >= 3 and max(degrees) <= n - 2:
                    return G
    return nx.empty_graph(n)

@st.cache_data
def _run_monte_carlo_core(edges_list, n_nodes, q, trials):
    """Core simulation logic, cached for speed and to avoid flickering."""
    connected_count = 0
    G_base = nx.Graph()
    G_base.add_nodes_from(range(n_nodes))
    G_base.add_edges_from(edges_list)
    
    for i in range(trials):
        G_trial = G_base.copy()
        for u, v in edges_list:
            if random.random() < q:
                G_trial.remove_edge(u, v)
        
        if nx.is_connected(G_trial):
            connected_count += 1
            
    return connected_count / trials

def run_monte_carlo(G, q, trials, progress_elements=None):
    """Wrapper that handles optional progress bar updates."""
    if progress_elements is None:
        return _run_monte_carlo_core(list(G.edges()), len(G.nodes()), q, trials)
    
    progress_bar, status_text = progress_elements
    edges = list(G.edges())
    n_nodes = len(G.nodes())
    
    steps = 10
    trials_per_step = max(1, trials // steps)
    total_connected = 0
    
    for step in range(steps):
        current_trials = trials_per_step if step < steps - 1 else trials - (trials_per_step * step)
        if current_trials <= 0: continue
        
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
        
        progress = (step + 1) / steps
        progress_bar.progress(progress)
        status_text.text(f"Simulating Trial {(step + 1) * trials_per_step}/{trials}...")
        
    return total_connected / trials

# --- Pi Approximation logic ---
@st.cache_data
def run_pi_simulation(n_trials):
    """Calculates Pi using Monte Carlo and returns data for plotting."""
    x = np.random.uniform(-1, 1, n_trials)
    y = np.random.uniform(-1, 1, n_trials)
    distances = x**2 + y**2
    is_inside = distances <= 1
    
    intervals = np.linspace(1, n_trials, 100, dtype=int)
    hits_cumulative = np.cumsum(is_inside)
    pi_estimates = 4 * hits_cumulative[intervals-1] / intervals
    
    return x, y, is_inside, pi_estimates, intervals, hits_cumulative[-1]

def pi_approximation_page():
    st.title("Approximating Pi using Monte Carlo Simulation")
    st.markdown(r"""
    **The ratio of darts inside the circle to total darts is $\frac{\pi}{4}$.
    Therefore, $\pi = 4 \times \frac{\text{Hits Inside}}{\text{Total Darts}}$.**
    """)
    
    st.sidebar.header("Pi Simulation Config")
    n_darts = st.sidebar.slider("Number of Darts", 100, 10000, 1000, 100)
    
    run_btn = st.sidebar.button("Run Monte Carlo", type="primary", use_container_width=True)

    x_data, y_data, is_inside_data, pi_estimates, intervals, total_hits = run_pi_simulation(n_darts)
    current_pi = 4 * (total_hits / n_darts)
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.subheader("Dart Visualization")
        plot_placeholder = st.empty()
        
    with col2:
        st.subheader("Real-time Metrics")
        m_col1, m_col2 = st.columns(2)
        metric_total = m_col1.empty()
        metric_hits = m_col2.empty()
        metric_pi = st.empty()
        st.divider()
        st.subheader("Convergence Plot")
        plot_conv_placeholder = st.empty()

    if 'start_sim' not in st.session_state:
        st.session_state.start_sim = False

    if run_btn:
        st.session_state.start_sim = True

    if st.session_state.start_sim:
        st.session_state.start_sim = False
        batch_size = max(1, n_darts // 20)
        
        fig_conv, ax_conv = plt.subplots(figsize=(10, 6))
        ax_conv.axhline(y=np.pi, color='red', linestyle='--', label='True Pi')
        ax_conv.set_xlabel("Number of Darts", fontsize=14)
        ax_conv.set_ylabel("Pi Value", fontsize=14)
        ax_conv.tick_params(labelsize=12)
        ax_conv.grid(True)
        
        fig_dart, ax_dart = plt.subplots(figsize=(10, 10))
        ax_dart.add_patch(plt.Rectangle((-1, -1), 2, 2, fill=False, color='black', lw=3))
        ax_dart.add_patch(plt.Circle((0, 0), 1, fill=False, color='blue', lw=3))
        ax_dart.set_xlim(-1.1, 1.1)
        ax_dart.set_ylim(-1.1, 1.1)
        ax_dart.set_aspect('equal')
        
        for i in range(batch_size, n_darts + 1, batch_size):
            current_x = x_data[:i]
            current_y = y_data[:i]
            current_inside = is_inside_data[:i]
            hits = np.sum(current_inside)
            pi_val = 4 * hits / i
            
            metric_total.metric("Total Darts", i)
            metric_hits.metric("Hits Inside Circle", hits)
            metric_pi.metric("Estimated Pi", f"{pi_val:.5f}")
            
            ax_dart.scatter(current_x[current_inside], current_y[current_inside], color='green', s=10, alpha=0.6)
            ax_dart.scatter(current_x[~current_inside], current_y[~current_inside], color='red', s=10, alpha=0.6)
            plot_placeholder.pyplot(fig_dart, width="stretch")
            
            idx = np.searchsorted(intervals, i)
            if idx > 0:
                ax_conv.plot(intervals[:idx], pi_estimates[:idx], color='blue')
                plot_conv_placeholder.pyplot(fig_conv, width="stretch")
            
            time.sleep(0.1)
            
        plt.close(fig_dart)
        plt.close(fig_conv)
    else:
        fig_dart, ax_dart = plt.subplots(figsize=(10, 10))
        ax_dart.add_patch(plt.Rectangle((-1, -1), 2, 2, fill=False, color='black', lw=3))
        ax_dart.add_patch(plt.Circle((0, 0), 1, fill=False, color='blue', lw=3))
        ax_dart.scatter(x_data[is_inside_data], y_data[is_inside_data], color='green', s=10, alpha=0.6)
        ax_dart.scatter(x_data[~is_inside_data], y_data[~is_inside_data], color='red', s=10, alpha=0.6)
        ax_dart.set_xlim(-1.1, 1.1)
        ax_dart.set_ylim(-1.1, 1.1)
        ax_dart.set_aspect('equal')
        plot_placeholder.pyplot(fig_dart, width="stretch")
        plt.close(fig_dart)

        metric_total.metric("Total Darts", n_darts)
        metric_hits.metric("Hits Inside Circle", total_hits)
        metric_pi.metric("Estimated Pi", f"{current_pi:.5f}")

        fig_conv, ax_conv = plt.subplots(figsize=(10, 6))
        ax_conv.plot(intervals, pi_estimates, color='blue', label='Estimate')
        ax_conv.axhline(y=np.pi, color='red', linestyle='--', label='True Pi')
        ax_conv.set_xlabel("Number of Darts", fontsize=14)
        ax_conv.set_ylabel("Pi Value", fontsize=14)
        ax_conv.tick_params(labelsize=12)
        ax_conv.legend(fontsize=12)
        ax_conv.grid(True)
        plot_conv_placeholder.pyplot(fig_conv, width="stretch")
        plt.close(fig_conv)

# --- App Logic Router ---
if app_mode == "Approximating Pi":
    pi_approximation_page()
else:
    # --- Network Reliability Mode ---
    st.title("Network Reliability Monte Carlo Visualizer")
    st.markdown("""
    This app simulates **network reliability** under random edge failures. 
    A network is considered 'reliable' if it remains connected after some edges fail.
    """)

    st.sidebar.header("Configuration")
    graph_type = st.sidebar.selectbox("Select Graph Type", ["Tree", "Cycle", "Complete", "Degree-Constrained Graph (3 ≤ deg ≤ n−2)"])
    n_nodes = st.sidebar.slider("Number of Nodes (n)", min_value=3, max_value=50, value=8)
    q_fail = st.sidebar.slider("Edge Failure Probability (q)", min_value=0.0, max_value=1.0, value=0.1, step=0.05)
    n_trials = st.sidebar.slider("Monte Carlo Trials", min_value=10, max_value=2000, value=100, step=10)

    run_sim = st.sidebar.button("Run Simulation", type="primary", use_container_width=True)

    if 'reliability' not in st.session_state:
        st.session_state.reliability = None
    if 'reliability_curve' not in st.session_state:
        st.session_state.reliability_curve = None
    if 'last_config' not in st.session_state:
        st.session_state.last_config = None

    current_config = (graph_type, n_nodes, q_fail, n_trials)

    G = generate_graph(graph_type, n_nodes)
    pos = nx.spring_layout(G, k=0.5, seed=42)

    if run_sim or (st.session_state.reliability is None):
        with st.sidebar:
            st.divider()
            st.write("**Simulation Progress**")
            p_bar = st.progress(0)
            p_text = st.empty()
            st.session_state.reliability = run_monte_carlo(G, q_fail, n_trials, progress_elements=(p_bar, p_text))
            p_text.text("Simulation Complete!")
            
            q_values = np.linspace(0, 1, 11)
            curve_data = []
            for q in q_values:
                curve_data.append(run_monte_carlo(G, q, min(n_trials, 50)))
            st.session_state.reliability_curve = curve_data
            st.session_state.last_config = current_config

    if st.session_state.reliability is not None:
        if st.session_state.last_config != current_config:
            st.warning("Configuration has changed. Click 'Run Simulation' to update results.")

        st.divider()
        st.subheader(f"Results for {graph_type} Graph")
        
        # side-by-side layout: metrics on the left (1), graph on the right (3)
        res_col1, res_col2 = st.columns([1, 3])
        
        with res_col1:
            st.metric("Estimated Reliability", f"{st.session_state.reliability:.2%}")
            st.metric("Number of Nodes", n_nodes)
            st.metric("Number of Edges", G.number_of_edges())
        
        with res_col2:
            # Display graph visualization in the larger column
            fig_main, ax_main = plt.subplots(figsize=(15, 10))
            ax_main.set_xlim(-1.2, 1.2)
            ax_main.set_ylim(-1.2, 1.2)
            
            bridges = list(nx.bridges(G))
            edge_colors = ['red' if (u, v) in bridges or (v, u) in bridges else 'gray' for u, v in G.edges()]
            node_size = max(100, 500 - (n_nodes * 8))
            
            nx.draw(G, pos, with_labels=True, node_color='skyblue', node_size=node_size, edge_color=edge_colors, width=2.5, font_size=12, font_weight='bold', ax=ax_main)
            st.pyplot(fig_main, width="stretch")
            plt.close(fig_main)
            if len(bridges) > 0:
                st.caption("Bridges are highlighted in red")

        st.divider()
        st.subheader("Reliability Curve")

        fig_curve, ax_curve = plt.subplots(figsize=(12, 5))
        q_values = np.linspace(0, 1, 11)
        ax_curve.plot(q_values, st.session_state.reliability_curve, marker='o', linestyle='-', color='blue')
        ax_curve.set_xlabel("Failure Probability (q)", fontsize=14)
        ax_curve.set_ylabel("Reliability", fontsize=14)
        ax_curve.set_title("Network Reliability vs. Failure Probability", fontsize=16)
        ax_curve.tick_params(labelsize=12)
        ax_curve.grid(True)
        st.pyplot(fig_curve, width="stretch")
    else:
        st.info("Adjust the configuration and click 'Run Simulation' to start.")

    st.divider()
    st.subheader("Simulate One Failure Case (Animated)")
    if st.button("Simulate One Trial"):
        placeholder = st.empty()
        edges = list(G.edges())
        random.shuffle(edges)
        
        current_edges_status = {edge: 'green' for edge in edges}
        failed_edges = []
        node_size = max(100, 500 - (n_nodes * 8))

        with placeholder.container():
            col_trial1, col_trial2 = st.columns(2)
            with col_trial1:
                st.write("**Simulation Process**")
                plot_placeholder1 = st.empty()
            with col_trial2:
                st.write("**Current Resulting Network**")
                plot_placeholder2 = st.empty()
            
            fig_trial1, ax_trial1 = plt.subplots(figsize=(10, 10))
            fig_trial2, ax_trial2 = plt.subplots(figsize=(10, 10))
            
            for i, edge in enumerate(edges):
                u, v = edge
                if random.random() < q_fail:
                    current_edges_status[edge] = 'lightcoral'
                    failed_edges.append(edge)
                
                if i % max(1, len(edges)//5) == 0 or i == len(edges)-1:
                    ax_trial1.clear()
                    ax_trial1.set_xlim(-1.2, 1.2)
                    ax_trial1.set_ylim(-1.2, 1.2)
                    ax_trial1.set_axis_off()
                    
                    G_temp = G.copy()
                    G_temp.remove_edges_from(failed_edges)
                    
                    if len(G_temp.nodes()) > 0:
                        components = sorted(nx.connected_components(G_temp), key=len, reverse=True)
                        largest_component = components[0] if components else set()
                        node_colors1 = ['skyblue' if n in largest_component else 'lightcoral' for n in G.nodes()]
                        
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
                    nx.draw(G, pos, with_labels=True, node_color=node_colors1, node_size=node_size, edge_color=edge_colors, width=2.5, font_size=12, font_weight='bold', ax=ax_trial1)
                    plot_placeholder1.pyplot(fig_trial1, width="stretch")
                    
                    ax_trial2.clear()
                    ax_trial2.set_xlim(-1.2, 1.2)
                    ax_trial2.set_ylim(-1.2, 1.2)
                    ax_trial2.set_axis_off()
                    
                    survived_edges = [e for e in G.edges() if e not in failed_edges and (e[1], e[0]) not in failed_edges]
                    nx.draw_networkx_nodes(G, pos, node_color=node_colors2, node_size=node_size, ax=ax_trial2)
                    nx.draw_networkx_labels(G, pos, font_size=12, font_weight='bold', ax=ax_trial2)
                    nx.draw_networkx_edges(G, pos, edgelist=survived_edges, width=2.5, edge_color='green', ax=ax_trial2)
                    
                    plot_placeholder2.pyplot(fig_trial2, width="stretch")
                    
                    time.sleep(0.3)
            
            plt.close(fig_trial1)
            plt.close(fig_trial2)
                
        G_trial = G.copy()
        G_trial.remove_edges_from(failed_edges)
        is_conn = nx.is_connected(G_trial)
        
        if is_conn:
            st.success("Network remained connected!")
        else:
            st.error("Network disconnected!")
        st.write(f"Failed edges: {len(failed_edges)}")
        st.write(f"Total edges: {G.number_of_edges()}")
