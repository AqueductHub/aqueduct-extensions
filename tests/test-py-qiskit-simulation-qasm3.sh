extension=py-qiskit-simulation
venv=$extension/.aqueduct-extension-dev

# recreate and populate a clean virtual env
# comment these 3 lines if requirements are stable
rm -r $venv
python -m venv $venv
$venv/bin/pip install -r $extension/requirements.txt

export aqueduct_url="http://localhost:8000/"

export aqueduct_key=""
export qasm_file=$(realpath tests/data/bell_state.qasm3)
export simulator_class="Fake20QV1"
export qasm_version=3
export shots=2000

# run
$venv/bin/python $extension/qiskit_simulator.py
code=$?
echo "Result code: $code"
exit $code
