import os
from inspect import isclass
from pathlib import Path
from tempfile import TemporaryDirectory

import numpy as np
import qiskit.providers.fake_provider
import qiskit.qasm3
import qiskit_aer.backends
from pyaqueduct import API
from pyaqueduct.experiment import Experiment
from qiskit import QuantumCircuit, transpile


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
    result = backend_instance.run(transpiled_circuit, shots=shots, memory=save_shots).result()
    print(result.get_counts())
    if save_shots:
        return result.get_memory()
    else:
        return []


def get_file(api, experiment, name, directory) -> Path:
    exp = api.get_experiment(experiment)
    exp.download_file(
        file_name=name,
        destination_dir=directory,
    )
    return Path(directory) / name


def save_to_aqueduct(
        api: API,
        content: np.array,
        experiment_id: str,
        filename: str,
        directory: str,
) -> None:
    """Saves content string as a file in aqueduct
    api (API): API of aqueduct
    content (np.array): array to save
    experiment_id (str):
        ID of the experiment where the file will be saved
    filename (str):
        name of the resulting file
    directory (str): temp dir
    """
    exp = api.get_experiment(experiment_id)
    fullname = Path(directory) / filename
    with open(fullname, "w") as file:
        for line in content:
            file.write("".join(map(str, map(int, line))))
            file.write("\n")
    exp.upload_file(str(fullname))



if __name__ == "__main__":
    qasm_filename = os.environ.get("qasm_file", "")
    simulator_type = os.environ.get("simulator_type", "")
    qasm_version = int(os.environ.get("qasm_version", "2"))
    shots = int(os.environ.get("shots", "1000"))
    memory = int(os.environ.get("memory", "0")) == 1

    aq_url = os.environ.get("aqueduct_url", "")
    aq_key = os.environ.get("aqueduct_key", "")

    experiment_id = os.environ.get("experiment", "")
    filename = os.environ.get("result_file", "")

    api = API(url=aq_url, timeout=10)
    with TemporaryDirectory() as directory:
        qasm_file = get_file(api, experiment_id, qasm_filename, directory)
        measurements = simulate(
            str(qasm_file),
            simulator_type,
            shots,
            qasm_version=qasm_version,
            save_shots=memory,
        )
        save_to_aqueduct(
            api,
            measurements,
            experiment_id=experiment_id,
            filename=filename,
            directory=directory,
        )
