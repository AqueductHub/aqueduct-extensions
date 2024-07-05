from pathlib import Path
from typing import Iterable

from pyaqueduct import API


def get_file_from_aqueduct(
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
    print(f"Downloading file {filename} from experiment {experiment_id}.")
    exp = api.get_experiment_by_eid(experiment_id)
    exp.download_file(
        file_name=str(filename),
        destination_dir=str(directory),
    )
    path = Path(directory) / filename
    print(f"File downloaded successfully: {path}")
    return path


def upload_to_aqueduct(
        api: API,
        experiment_id: str,
        file: str | Path):
    """Upload a file to an Aqueduct.

    Args:
        api (API): API instance
        experiment_id (str): ID of an experiment
        file (str | Path): file to upload
    """
    print(f"Uploading file {file} to experiment {experiment_id}")
    exp = api.get_experiment_by_eid(experiment_id)
    exp.upload_file(str(file))


def save_content_to_aqueduct(
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
    fullname = Path(directory) / filename
    with open(fullname, "w") as file:
        for line in content:
            # double convertation for the case of np.ndarray
            file.write("".join(map(str, map(int, line))))
            file.write("\n")
    upload_to_aqueduct(api, experiment_id, fullname)
