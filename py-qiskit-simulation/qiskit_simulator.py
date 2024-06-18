import os
from inspect import isclass

from qiskit import QuantumCircuit, transpile
import qiskit.qasm3
import qiskit.providers.fake_provider
import qiskit_aer.backends
import numpy as np


def simulate(
        qasm_circuit_filename: str,
        backend_name: str,
        shots: int,
        save_shots: bool = False,
        qasm_version: int = 2,
) -> np.array:
    if qasm_version == 2:
        circuit = QuantumCircuit.from_qasm_file(qasm_circuit_filename)
    elif qasm_version == 3:
        circuit = qiskit.qasm3.load(qasm_circuit_filename)
    else:
        raise NotImplementedError(
            f"QASM version {qasm_version} is not supported in this extension")

    backends = dict(vars(qiskit.providers.fake_provider))
    backends.update(vars(qiskit_aer.backends))
    backends = {k: v for k, v in backends.items() if isclass(v)}
    backend = backends.get(backend_name, None)
    if not backend:
        raise NotImplementedError(f"Backend {backend_name} is not found in Qiskit.")
    backend_instance = backend()
    transpiled_circuit = transpile(circuit, backend_instance)
    print(backend_instance.run(transpiled_circuit, shots=shots, memory=save_shots).result())

if __name__ == "__main__":
    filename = os.environ.get("qasm_file", "")
    simulator_class = os.environ.get("simulator_class", "")
    shots = int(os.environ.get("shots", "1000"))
    simulate(filename, simulator_class, shots, save_shots=True)
