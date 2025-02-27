import argparse
from pathlib import Path
import subprocess
import os
import json


class DockerBuildResult:
    """
    A class to represent the result JSON object.

    Attributes:
    json (dict): The JSON object.

    Example:
    {
        "updated_images": ["image1", "image2"],
        "failed_images": ["image3", "image4"],
        "message": "Failed to build one or more docker images.",
        "status": "failure",
        "error": ["Error message 1", "Error message 2"]
    }

    {
        "updated_images": ["image1", "image2"],
        "failed_images": [],
        "message": "Successfully built all docker images.",
        "status": "success",
        "error": []
    }
    """

    def __init__(self):
        self.json = {
            "updated_images": [],
            "failed_images": [],
            "message": "",
            "status": "success",
            "error": []
        }

    def add_updated_image(self, docker_image: Path):
        self.json["updated_images"].append(str(docker_image.name))

    def add_failed_image(self, docker_image: Path):
        self.json["failed_images"].append(str(docker_image.name))

    def set_status(self, status: str):
        self.json["status"] = status

    def set_message(self, message: str):
        self.json["message"] = message

    def add_error_message(self, error: str):
        self.json["error"].append(error)

    def get_status(self):
        return self.json["status"]

    def set_updated(self, val: bool):
        self.json["updated"] = val

    def output(self):
        return self.json


def find_build_docker_scripts(dir: Path) -> Path | None:
    """
    Finds the build docker scripts in the given directory.

    :param dir: The directory to search in. (Ideally, this is an assignment folder)
    """
    for file in dir.iterdir():
        if file.is_file() and file.name.startswith('build') and file.name.endswith('docker.sh'):
            return file.absolute()
    return None


def find_assignments(files: list[Path]) -> list[Path]:
    """
    Finds the assignment directories from the list of changed files.

    :param files: The list of changed files.
    :return: A list of assignment folders.
    """
    assignments = []
    for file in files:
        file = Path(file)

        # Check if the file is in a solution folder and the
        # assignment folder is not already in the list of assignments
        if 'solution' in file.parent.name and file.parent.parent.name not in assignments:
            assignments.append(file.parent.parent)

    return assignments


def find_docker_images(files: list[Path]) -> list[Path]:
    """
    Finds the docker scripts for the changed assignments.

    :param files: The list of changed files in the repository.
    :return: A list of docker scripts.
    """
    docker_images = []

    # Find the assignment folders from the list of changed files
    changed_assignments = find_assignments(files)

    for assignment in changed_assignments:
        docker_image = find_build_docker_scripts(assignment)

        if docker_image:
            docker_images.append(docker_image)

    return docker_images


def run_docker_scripts(docker_scripts: list[Path], result):
    """
    Runs the docker scripts and prints their output.

    :param docker_scripts: The list of docker scripts to run.
    :param result: The result JSON object.
    """
    processes = []

    for docker_image in docker_scripts:
        r_fd, w_fd = os.pipe()  # Create a pipe

        # Run script with stdout redirected to write pipe
        p = subprocess.Popen(
            ['bash', str(docker_image)], cwd=docker_image.parent,
            stdout=w_fd, stderr=subprocess.PIPE, universal_newlines=True
        )

        os.close(w_fd)
        processes.append((p, r_fd, docker_image))

    for p, read_pipe, docker_image in processes:
        stderr = p.stderr.read()  # Read stderr
        p.stderr.close()
        p.wait()

        if p.returncode == 0:
            result.add_updated_image(docker_image)
        else:
            result.set_status("failure")
            result.add_failed_image(docker_image)
            result.add_error_message(stderr)

    if result.get_status() == "failure":
        result.set_message("Failed to build one ore more docker images.\nSee "
                           "https://github.com/BYU-CS-Course-Ops/CS235-course-content/tree/main/.github/logs"
                           "/docker_output.json for more details")
    else:
        result.set_status("success")
        result.set_message("Successfully built all docker images.")

    result.set_updated(True)


def main(files: str, output_file: str):
    docker_files = find_docker_images(
        [
            (Path(__file__).parent.parent.parent.absolute() / file).resolve()
            for file in files.split()
        ]
    )
    result = DockerBuildResult()

    if not docker_files:
        result.set_updated(False)
        with open(output_file, 'w') as f:
            f.write(json.dumps(result.output(), indent=4))
        f.close()
        exit(0)

    run_docker_scripts(docker_files, result)

    with open(output_file, 'w') as f:
        f.write(json.dumps(result.output(), indent=4))
    f.close()


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('--files')
    parser.add_argument('--output-file', required=True)
    args = parser.parse_args()

    main(
        files=args.files,
        output_file=args.output_file
    )
