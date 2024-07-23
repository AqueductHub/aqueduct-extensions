import os
from collections import Counter
from pathlib import Path
from tempfile import TemporaryDirectory

from files import get_file_from_aqueduct, upload_to_aqueduct
from pyaqueduct import API
from qiskit.visualization import plot_histogram


def collect_as_dict(filename: str) -> dict:
    """Collects shots into a frequency dictionary.

    Args:
        filename (str): source local filename.

    Returns:
        dict: frequency dict.
    """
    print(f"Collecting shots from file {filename}.")
    with open(filename, "r") as file:
        stats = Counter(line.strip() for line in file.readlines() if line.strip())
    return stats

if __name__ == "__main__":
    aq_url = os.environ.get("aqueduct_url", "")
    experiment_id = os.environ.get("experiment", "")

    width = int(os.environ.get("width", "1000"))
    height = int(os.environ.get("height", "800"))

    # default DPI
    dpi = 96
    figsize = (width / dpi, height / dpi)

    shots_file = os.environ.get("shots_file", None)
    image_file = os.environ.get("image_file", None)

    if not shots_file:
        raise ValueError("File name `shots_file` was not provided.")
    if not image_file:
        raise ValueError("File name `image_file` was not provided.")

    # API token is passed directly for environment varible
    # $API_TOKEN
    api = API(url=aq_url, timeout=2)

    with TemporaryDirectory() as directory:
        local_shots = get_file_from_aqueduct(api, experiment_id, shots_file, directory)
        dictionary = collect_as_dict(local_shots)
        local_image = Path(directory) / image_file
        print(f"Plotting image {local_image}: {width}x{height}.")
        plot_histogram(data=dictionary, figsize=figsize, filename=str(local_image))
        upload_to_aqueduct(api, experiment_id, local_image)
