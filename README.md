
# Setup Instructions

## Cloning the Repository

First, clone the repository to your local machine:

```bash
git clone https://github.com/hectorpine/python-to-web-app.git
cd python-to-web-app
```

## Setting Up a Virtual Environment

Before installing the packages, it's a good idea to create a virtual environment to keep dependencies required by different projects separate and organized. You can create a virtual environment by running:

```bash
python -m venv env
```

Activate the virtual environment:

### On Windows:
```bash
env\Scripts\activate
```

### On MacOS/Linux:
```bash
source env/bin/activate
```

## Installing Dependencies

With the virtual environment activated, install the required packages using pip:

```bash
pip install simplegmail pydantic fastapi
```

This command installs `simplegmail`, `pydantic`, and `fastapi` packages needed for the project.
```

