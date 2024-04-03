import subprocess
import sys

# List of libraries to be installed
libraries = [
    "geopandas", "matplotlib", "numpy", "pandas", "rasterio", "rasterstats",
    "shapely", "h5py", "requests", "scikit-image", "astropy"
]


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

if __name__ == "__main__":
    for lib in libraries:
        install(lib)
