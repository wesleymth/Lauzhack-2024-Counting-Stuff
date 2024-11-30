# Lauzhack-2024

```sh
# Navigate to directory
cd .../Lauzhack-2024

# Create a new conda environment with Python 3.12
conda create -n lauz24 python=3.12

# Activate the environment
conda activate lauz24

# Install the required dependencies
pip install -r requirements.cv.txt
pip install -r requirements.flask.txt
pip install -r requirements.llms.txt

# # Install local src package
pip install -e .
```