import os
from inspect import isclass
from pathlib import Path
from tempfile import TemporaryDirectory
from typing import Iterable

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
    """Simulate the circuit with a provided backend class name.
    Classes names are taken from `qiskit.providers.fake_provider`
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
    # to report shots in little-endians style, like in STIM
    circuit = circuit.reverse_bits()
    print(
        f"Circuit {qasm_circuit_filename} successfully "
        f"parsed with OpenQASM{qasm_version}."
    )
    
    backends = dict(vars(qiskit.providers.fake_provider))
    backends.update(vars(qiskit_aer.backends))
    # from these namespaces, keep only classes
    backends = {k: v for k, v in backends.items() if isclass(v)}
    backend = backends.get(backend_name, None)
    print(f"Backend class for {backend_name}: {backend}")
    if not backend:
        raise NotImplementedError(f"Backend {backend_name} is not found in Qiskit.")

    backend_instance = backend()
    transpiled_circuit = transpile(circuit, backend_instance)
    result = backend_instance.run(
        transpiled_circuit,
        shots=shots,
        memory=save_shots
    ).result()
    print(f"Aggregated mesurements: {result.get_counts()}")
    return result.get_memory() if save_shots else []


def get_file(
        api: API,
        experiment_id: str,
        filename: str,
        directory: str
    ) -> Path:
    """Download a file to a local file system 
    from the Aqueduct.

    Args:
        api (A): Aqueduct API object
        experiment_id (str): experiment ID
        filename (str): file name in the experiment
        directory (str): destination directory

    Returns:
        Path: path to a downloaded file
    """
    exp = api.get_experiment_by_eid(experiment_id)
    print(f"Source experiment: {exp}")
    exp.download_file(
        file_name=filename,
        destination_dir=directory,
    )
    path = Path(directory) / filename
    print(f"File downloaded successfully: {path}")
    return path


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
    exp = api.get_experiment_by_eid(experiment_id)
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

    experiment_id = os.environ.get("experiment", "")
    qasm_filename = os.environ.get("qasm_file", "")
    result_filename = os.environ.get("result_file", "")

    simulator_type = os.environ.get("simulator_type", "")
    qasm_version = os.environ.get("qasm_version", "v2")
    shots = int(os.environ.get("shots", "1000"))
    memory = int(os.environ.get("memory", "0")) == 1

    # API token is passed directly for environment varible
    # $API_TOKEN
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
