from dataclasses import dataclass


@dataclass(frozen=True)
class ProxyConfig:
    """
    Configuration for various proxies, defaults are included for every setting so only the
    non-default values need to be changed when creating one
    """

    qubits: int
    force_recalculate: bool = False

    entanglement_samples: int = 1000

    expressivity_samples: int = 1000
    expressivity_bins: int = 100
