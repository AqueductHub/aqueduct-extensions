extension=py-qiskit-simulation
venv=$extension/.aqueduct-extension-dev

# recreate and populate a clean virtual env
# comment these 3 lines if requirements are stable
rm -r $venv
python -m venv $venv
$venv/bin/pip install -r $extension/requirements.txt

export aqueduct_url="https://aqueduct-demo.azurewebsites.net/"

export aqueduct_key=""
export qasm_file="bell_state.qasm"
export simulator_type="QasmSimulator"
export qasm_version="v2"
export shots=2000
export experiment="20240618-1"
export result_file="measurements.01"
export memory=1

# run
$venv/bin/python $extension/qiskit_simulator.py
code=$?
echo "Result code: $code"
exit $code
