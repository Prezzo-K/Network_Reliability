# Network Reliability Monte Carlo Visualizer

An interactive web application built with **Streamlit** to simulate and visualize the reliability of different network structures under random edge failures.

## 🚀 Overview
This project explores the mathematical and computational aspects of **Network Reliability**. It uses **Monte Carlo simulations** to estimate the probability that a graph remains connected when its edges fail with a probability $q$.

## 🛠️ Features
- **Interactive Graph Generation**: Choose between **Tree**, **Cycle**, and **Complete** graphs.
- **Monte Carlo Engine**: Simulate up to 2,000 trials with real-time progress tracking.
- **Visual Failure Animation**: Watch a "step-by-step" simulation of edge failures to see how networks disconnect in real-time.
- **Reliability Curves**: Visualize how reliability drops as the failure probability $q$ increases.
- **Theoretical Integration**: 
    - **Bridge Analysis**: Identifies cut-edges and calculates the $(1-q)^k$ reliability bound.
    - **Min-Cut Calculation**: Computes the minimum cut size ($\lambda$) to show how robustness scales.

## 📥 Installation
1. Ensure you have Python installed.
2. Install the required dependencies:
   ```bash
   pip install -r requirements.txt
   ```

## 🏃 How to Run
Launch the app using Streamlit:
```bash
streamlit run app.py
```

## 📊 Mathematical Concepts
- **Reliability ($R$)**: The probability that the graph is connected.
- **Monte Carlo Estimation**: $R \approx \frac{\text{Connected Trials}}{\text{Total Trials}}$.
- **Bridges**: Edges whose removal disconnects the graph.
- **Minimum Cut ($\lambda$)**: The smallest number of edges whose removal disconnects the graph. For small $q$, the failure probability is dominated by $C \cdot q^\lambda$.

## 👥 Project Team
- **Math Lead**: Theory development and proofs.
- **Computational Lead**: Monte Carlo simulation development and visualization (This App).
