extension=py-qiskit-simulation
venv=$extension/.aqueduct-extension-dev

# recreate and populate a clean virtual env
# comment these 3 lines if requirements are stable
rm -r $venv
python -m venv $venv
$venv/bin/pip install -r $extension/requirements.txt

export aqueduct_url="https://aqueduct-demo.azurewebsites.net/"

export width=400
export height=500

# run
$venv/bin/python $extension/plot_shots.py
code=$?
echo "Result code: $code"
exit $code
