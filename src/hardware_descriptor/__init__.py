import networkx as nx
from qiskit.providers.backend import BackendV2
from qiskit_aer.noise.noise_model import NoiseModel


class Topology:

    graph: nx.DiGraph = nx.DiGraph(name="connectivity graph")

    def __init__(self, noise_model_or_backend: BackendV2 | NoiseModel):
        if isinstance(noise_model_or_backend, NoiseModel):
            self.noise_model = noise_model_or_backend
        else:
            self.noise_model = NoiseModel.from_backend(noise_model_or_backend)

    def _build_graph(self, noise_model: NoiseModel):
        qubits = noise_model.noise_qubits

        # add single qubit gate errors and nodes
        for qubit in qubits:
            # extract the readout error if it is defined
            readout_error = noise_model._local_readout_errors.get((qubit,), None)
            readout_rate: float = readout_error.to_dict()["probabilities"][0][1] if readout_error is not None else 0.0
            assert isinstance(readout_rate, float)

            # extract the X error if it is defined
            x_error = self.noise_model._local_quantum_errors.get("x", {}).get((qubit,), None)
            x_rate: float = sum(x_error.to_dict().get("probabilities", [])[1:]) if x_error is not None else 0.0
            assert isinstance(x_rate, float)

            # extract the Z error if it is defined
            z_error = self.noise_model._local_quantum_errors.get("z", {}).get((qubit,), None)
            z_rate: float = sum(z_error.to_dict().get("probabilities", [])[1:]) if z_error is not None else 0.0
            assert isinstance(z_rate, float)

            # extract the reset error if it is defined
            reset_error = self.noise_model._local_quantum_errors.get("reset", {}).get((qubit,), None)
            reset_rate: float = (
                sum(reset_error.to_dict().get("probabilities", [])[1:]) if reset_error is not None else 0.0
            )
            assert isinstance(reset_rate, float)

            sum_error = readout_rate + x_rate + z_rate + reset_rate

            self.graph.add_node(qubit, readout=readout_rate, x=x_rate, z=z_rate, reset=reset_rate, sum_error=sum_error)

        # add two-qubit gate errors and edges
        cx_errors = noise_model._local_quantum_errors.get("cx", {})
        for (control, target), err_obj in cx_errors.items():
            print(f"errors between C: {control} and X: {target} are {err_obj}")

            cx_probs = err_obj.to_dict().get("probabilities", [])
            cx_error = 1.0 - cx_probs[0] if cx_probs else 0.0
            assert isinstance(cx_error, float)

            self.graph.add_edge(control, target, cx=cx_error)

    def draw(self):
        import matplotlib.pyplot as plt

        pos = nx.spring_layout(self.graph, seed=42)

        # Node labels include error rate
        node_labels = {n: f"{n}\nErr: {d['sum_error']:.3g}" for n, d in self.graph.nodes(data=True)}

        # Edge labels include error rate
        edge_labels = {(u, v): f"{d['cx']:.3g}" for u, v, d in self.graph.edges(data=True)}

        nx.draw(
            self.graph,
            pos,
            with_labels=True,
            labels=node_labels,
            node_color="lightblue",
            node_size=1000,
            font_weight="bold",
        )
        nx.draw_networkx_edge_labels(self.graph, pos, edge_labels=edge_labels)
        plt.show()
