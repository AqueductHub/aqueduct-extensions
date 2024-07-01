import os
from typing import Iterable
from inspect import isclass
from pathlib import Path
from tempfile import TemporaryDirectory

import qiskit.providers.fake_provider
import qiskit.qasm3
import qiskit_aer.backends
from pyaqueduct import API
from qiskit import QuantumCircuit, transpile


def simulate(
        qasm_circuit_filename: str,
        backend_name: str,
        shots: int,
        save_shots: bool = False,
        qasm_version: str = "v2",
):
    """Simulates the circuit with a provided backend class name.
    Class names are taken from `qiskit.providers.fake_provider`
    and `qiskit_aer.backends`.

    Args:
        qasm_circuit_filename (str): QASM file name
        backend_name (str): Class name of we backend.
        shots (int): Number of times circuit is simulated.
        save_shots (bool, optional):
            Return the array with per-shot measurements. Defaults to False.
        qasm_version (str, optional):
            Circuit language standard, v2 or v3. Defaults to v2.

    Raises:
        NotImplementedError:
            For QASM not from {v2, v3} or unknown bakend.

    Returns:
        Iterable: collection of shots, or [].
    """
    if qasm_version == "v2":
        circuit = QuantumCircuit.from_qasm_file(qasm_circuit_filename)
    elif qasm_version == "v3":
        circuit = qiskit.qasm3.load(qasm_circuit_filename)
    else:
        raise NotImplementedError(
            f"QASM version {qasm_version} is not supported in this extension")
    print(f"Circuit {qasm_circuit_filename} successfully parsed with OpenQASM{qasm_version}")

    # to report shots in little-endians style, like STIM
    circuit = circuit.reverse_bits()
    backends = dict(vars(qiskit.providers.fake_provider))
    backends.update(vars(qiskit_aer.backends))
    backends = {k: v for k, v in backends.items() if isclass(v)}
    backend = backends.get(backend_name, None)
    print(f"Backend class for {backend_name}: {backend}")

    if not backend:
        raise NotImplementedError(f"Backend {backend_name} is not found in Qiskit.")
    backend_instance = backend()
    transpiled_circuit = transpile(circuit, backend_instance)
    result = backend_instance.run(transpiled_circuit, shots=shots, memory=save_shots).result()
    if save_shots:
        return result.get_memory()
    else:
        return []


def get_file(api, experiment, name, directory) -> Path:
    exp = api.get_experiment(experiment)
    print(f"Source experiment: {exp}")
    exp.download_file(
        file_name=name,
        destination_dir=directory,
    )
    print(f"File downloaded successfully: {Path(directory) / name}")
    return Path(directory) / name


def save_to_aqueduct(
        api: API,
        content: Iterable,
        experiment_id: str,
        filename: str,
        directory: str,
) -> None:
    """Saves content string as a file in aqueduct
    api (API): API of Aqueduct.
    content (Iterable): array to save.
    experiment_id (str):
        ID of the experiment where the file will be saved
    filename (str):
        name of the resulting file
    directory (str): temporary directory.
    """
    exp = api.get_experiment(experiment_id)
    print(f"Destination experiment: {exp}")
    fullname = Path(directory) / filename
    with open(fullname, "w") as file:
        for line in content:
            # double convertation for the case of np.ndarray
            file.write("".join(map(str, map(int, line))))
            file.write("\n")
    print(f"Uploading file {fullname}")
    exp.upload_file(str(fullname))


if __name__ == "__main__":
    aq_url = os.environ.get("aqueduct_url", "")
    aq_key = os.environ.get("aqueduct_key", "")
    print(f"Aqueduct server: {aq_url}")

    experiment_id = os.environ.get("experiment", "")
    qasm_filename = os.environ.get("qasm_file", "")
    result_filename = os.environ.get("result_file", "")

    simulator_type = os.environ.get("simulator_type", "")
    qasm_version = os.environ.get("qasm_version", "v2")
    shots = int(os.environ.get("shots", "1000"))
    memory = int(os.environ.get("memory", "0")) == 1

    # TODO add key support
    api = API(url=aq_url, timeout=2)

    with TemporaryDirectory() as directory:
        print(f"Downloading circuit file {qasm_filename}")
        qasm_file_path = get_file(
            api, experiment_id, qasm_filename, directory)
        print("Starting simulation.")
        measurements = simulate(
            qasm_circuit_filename=str(qasm_file_path),
            backend_name=simulator_type,
            shots=shots,
            qasm_version=qasm_version,
            save_shots=memory,
        )
        if memory:
            print(f"Saving shots to Aqueduct experiment {experiment_id}.")
            save_to_aqueduct(
                api=api,
                content=measurements,
                experiment_id=experiment_id,
                filename=result_filename,
                directory=directory,
            )
        print("Successfully finished")
