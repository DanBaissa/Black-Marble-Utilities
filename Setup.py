import argparse
import subprocess
import sys

def install(library):
    """
    Install the given library using pip, if it's not already installed.
    """
    try:
        # Check if the library is already installed
        subprocess.check_call([sys.executable, "-m", "pip", "show", library])
        print(f"{library} is already installed.")
    except subprocess.CalledProcessError:
        # If the library is not found, install it
        print(f"Installing {library}...")
        subprocess.check_call([sys.executable, "-m", "pip", "install", library])

def main(libraries):
    for lib in libraries:
        install(lib)

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Install Python libraries using pip.")
    parser.add_argument('libraries', nargs='*', default=[
        "geopandas", "matplotlib", "numpy", "pandas", "rasterio", "rasterstats",
        "shapely", "h5py", "requests", "scikit-image", "astropy"
    ], help="The names of the libraries to install. If none are provided, a default set of libraries will be installed.")

    args = parser.parse_args()
    main(args.libraries)
