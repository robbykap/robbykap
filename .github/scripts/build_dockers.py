import argparse
from pathlib import Path
import subprocess
import os


def find_build_docker_scripts(dir: Path):
    for file in dir.iterdir():
        if file.is_file() and file.name.startswith('build') and file.name.endswith('docker.sh'):
            return file.absolute()


def find_assignments(files: list[Path]) -> list[Path]:
    assignments = set()
    for file in files:
        file = Path(file)
        # Check if the file is within a solution folder inside an hw folder
        if file.parent.name == 'solution' and file.parent.parent.name not in assignments:
            assignments.add(file.parent.parent)
    return assignments


def find_docker_scripts(files: list[Path]) -> list[Path]:
    docker_files = []
    changed_assignments = find_assignments(files)
    for dir in changed_assignments:
        dockerfile = find_build_docker_scripts(dir)
        if dockerfile:
            docker_files.append(dockerfile)
    return docker_files


def find_relative_paths(root: Path, files: list[str]) -> list[Path]:
    abs_files = []
    for file in files:
        abs_path = (root / file).resolve()
        abs_files.append(abs_path)
    return abs_files


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('--files')
    args = parser.parse_args()

    files = args.files.split()
    files = find_relative_paths(Path(__file__).parent.parent.parent.absolute(), files)
    docker_files = find_docker_scripts(files)

    if not docker_files:
        print('No docker files found')
        exit(0)

    print('Building docker images:')
    for docker in docker_files:
        print(f' - {Path(docker).name}')

    processes = []
    # Standard out goes to a file,
    # while error messages go straight to the screen.
    # After the files finish, their output is printed.
    for docker in docker_files:
        # create a pipe to connect the StringIO to the process
        r_fd, w_fd = os.pipe()
        p = subprocess.Popen(['bash', docker], cwd=docker.parent,
                             bufsize=1,
                             stdout=w_fd,
                             universal_newlines=True)
        processes.append((p, r_fd, w_fd))

    for p, read_pipe, write_pipe in processes:
        p.wait()
    for p, read_pipe, write_pipe in processes:
        # close the write-end of the pipe in the parent process
        os.close(write_pipe)
        print(os.read(read_pipe, 1024).decode())
        # close the read end of the pipe
        os.close(read_pipe)

    print('Finished building docker images')