import pandas as pd
import numpy as np
import networkx as nx
import matplotlib.pyplot as plt
from scipy.stats import pearsonr


def polarization(opinions):
    values = np.array(list(opinions.values()), dtype=float)
    return np.mean((values - values.mean()) ** 2)


def global_disagreement(G, opinions):
    total = 0.0
    for node in G.nodes():
        neighbors = list(G.neighbors(node))
        if not neighbors:
            continue
        local = np.mean([(opinions[node] - opinions[n]) ** 2 for n in neighbors])
        total += local
    return total / (2 * len(G.nodes()))


def neighbor_correlation(G, opinions):
    nodes = list(G.nodes())
    node_values = []
    neighbor_avg_values = []

    for node in nodes:
        neighbors = list(G.neighbors(node))
        if not neighbors:
            continue

        node_values.append(opinions[node])
        neighbor_avg_values.append(np.mean([opinions[n] for n in neighbors]))

    if len(node_values) < 2:
        return 0.0

    corr, _ = pearsonr(node_values, neighbor_avg_values)

    if np.isnan(corr):
        return 0.0

    return corr


def degroot_update(G, opinions, alpha=0.5):
    """
    alpha 越高，agent 越保留自己的原本意見。
    alpha 越低，agent 越容易被鄰居影響。
    """
    new_opinions = {}

    for node in G.nodes():
        neighbors = list(G.neighbors(node))

        if not neighbors:
            new_opinions[node] = opinions[node]
            continue

        neighbor_mean = np.mean([opinions[n] for n in neighbors])
        new_opinions[node] = alpha * opinions[node] + (1 - alpha) * neighbor_mean

    return new_opinions


def build_network(network_type, n, seed=50):
    if network_type == "small_world":
        return nx.watts_strogatz_graph(n=n, k=4, p=0.1, seed=seed)

    if network_type == "scale_free":
        return nx.barabasi_albert_graph(n=n, m=2, seed=seed)

    if network_type == "random":
        return nx.erdos_renyi_graph(n=n, p=0.08, seed=seed)

    raise ValueError(f"Unknown network type: {network_type}")


def main():
    agents = pd.read_csv("reddit_agents.csv")
    n = len(agents)

    print(f"Loaded {n} agents from reddit_agents.csv")

    rng = np.random.default_rng(50)

    # 如果 initial_belief 全部都是 0，就先用隨機 dummy belief 測試流程
    if agents["initial_belief"].nunique() == 1 and agents["initial_belief"].iloc[0] == 0:
        print("initial_belief are all 0. Using dummy random beliefs for testing.")
        initial_values = rng.choice([-2, -1, 0, 1, 2], size=n)
    else:
        initial_values = agents["initial_belief"].astype(float).values

    network_types = ["small_world", "scale_free", "random"]
    all_results = []

    for network_type in network_types:
        print(f"Running network: {network_type}")

        G = build_network(network_type, n=n, seed=50)
        opinions = {i: float(initial_values[i]) for i in range(n)}

        for step in range(31):
            all_results.append({
                "network_type": network_type,
                "step": step,
                "polarization": polarization(opinions),
                "global_disagreement": global_disagreement(G, opinions),
                "neighbor_correlation": neighbor_correlation(G, opinions),
            })

            opinions = degroot_update(G, opinions, alpha=0.5)

    results = pd.DataFrame(all_results)
    results.to_csv("static_baseline_results.csv", index=False, encoding="utf-8-sig")
    print("Saved results to static_baseline_results.csv")

    for metric in ["polarization", "global_disagreement", "neighbor_correlation"]:
        plt.figure()
        for network_type in network_types:
            subset = results[results["network_type"] == network_type]
            plt.plot(subset["step"], subset[metric], label=network_type)

        plt.xlabel("Step")
        plt.ylabel(metric)
        plt.title(metric)
        plt.legend()
        plt.tight_layout()
        plt.savefig(f"{metric}.png", dpi=200)
        print(f"Saved {metric}.png")


if __name__ == "__main__":
    main()