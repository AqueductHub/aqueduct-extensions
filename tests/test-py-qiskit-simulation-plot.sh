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

export width=500
export height=400
export shots_file=measurements.01
export image_file=hist.png
export experiment="20240618-1"

curl -sf "$aqueduct_url" > /dev/null
# if aqueduct is up, run the script!
if [ $? = 0 ]; then
    $venv/bin/python $extension/plot_shots.py
    code=$?
    echo "Result code: $code"
else
    code=0
    echo "Extension test skipped"
fi
exit $code
