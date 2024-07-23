extension=py-qiskit-simulation
venv=$extension/.aqueduct-extension-dev

# recreate and populate a clean virtual env
# comment these 3 lines if requirements are stable
rm -r $venv
python -m venv $venv
$venv/bin/pip install -r $extension/requirements.txt
if [ $? != 0 ]; then
    echo "failed to install requirements"
    exit 1
fi

export aqueduct_url="http://localhost:8000/"

export qasm_file="bell_state.qasm3"
export simulator_type="AerSimulator"
export qasm_version="v3"
export memory=1
export experiment="20240618-1"
export result_file="measurements.01"
export shots=2000

curl -sf "$aqueduct_url" > /dev/null
# if aqueduct is up, run the script!
if [ $? = 0 ]; then
    $venv/bin/python $extension/qiskit_simulator.py
    code=$?
    echo "Result code: $code"
else
    code=0
    echo "Extension test skipped"
fi
exit $code