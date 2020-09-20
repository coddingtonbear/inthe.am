import argparse
import os.path
import subprocess


def main(config):
    output_path = "{}{}".format(config.input_file, ".tmp.png")
    script_path = os.path.abspath(
        os.path.join(
            os.path.dirname(__file__),
            os.path.splitext(os.path.basename(__file__))[0] + ".scm",
        )
    )
    with open(script_path, "r") as input_file:
        script = input_file.read()
    for size in (
        152,
        120,
        76,
        60,
        10,
    ):
        output_path = os.path.abspath(
            os.path.join(
                os.path.dirname(__file__),
                "../",
                "inthe_am/taskmanager/static/icon-%s.png" % size,
            )
        )
        actual_script = script.format(
            file_path=config.input_file,
            output_path=output_path,
            width=size,
            height=size,
        )
        subprocess.call(
            [config.gimp_bin, "-n", "-i", "-b", actual_script,],
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
        )
        print(output_path)
    os.unlink(output_path)


def get_default_icon_path():
    return os.path.abspath(
        os.path.join(os.path.dirname(__file__), "../", "assets/icon.xcf",)
    )


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--input_file", dest="input_file", type=str, default=get_default_icon_path()
    )
    parser.add_argument(
        "--gimp-bin", dest="gimp_bin", default="gimp", type=str,
    )
    args = parser.parse_args()
    main(args)
