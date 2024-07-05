extension=py-qiskit-simulation
venv=$extension/.aqueduct-extension-dev

# recreate and populate a clean virtual env
# comment these 3 lines if requirements are stable
rm -r $venv
python -m venv $venv
$venv/bin/pip install -r $extension/requirements.txt

export aqueduct_url="http://localhost:8000/"

export width=500
export height=400
export shots_file=measurements.01
export image_file=hist.png
export experiment=20240705-3

# run
$venv/bin/python $extension/plot_shots.py
code=$?
echo "Result code: $code"
exit $code
