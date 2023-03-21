import os


def get_file_paths(dir_path):
    files = []
    for file in os.listdir(dir_path):
        f = os.path.join(dir_path, file)

        if os.path.isfile(f):
            files.append(str(f))

    return files
