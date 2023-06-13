import argparse

from craic.main import yaml_reader

def interface():
    argParser = argparse.ArgumentParser(prog="CRAIC", description="Structural analysis toolkit")

    # Get name of input file
    argParser.add_argument("-i", "--ifile", help="Name of setup file", default="setup.yaml")

    # Parse the arguments
    args = argParser.parse_args()

    yaml_reader(args.ifile)



if __name__ == "__main__":
    interface()