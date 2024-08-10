### Clone the GitHub Repository

Open your terminal and run the following command to clone the repository.

```bash
git clone https://github.com/Niskarsha007/Train_Simulation.git
```

Navigate to the cloned repository directory:

```bash
    cd Train_Simulation
```

### Create a Virtual Environment

Create a virtual environment named .venv:

```bash
# on windows
python -m venv .venv
# on mac
python3 -m venv .venv
```

### Activate the Virtual Environment

- On windows

```bash
.venv/Scripts/activate
```

- On mac and linux

```bash
source .venv/bin/activate
```

### Install Required Modules

Install all the required modules listed in the requirements.txt file:

```bash
pip install -r requirements.txt
```

### Run the Python Code

Run your Python code

```bash
python trainsim.py
```

---

### OR 

In the prompt, you must make sure pip is installed.
This will allow a user to install the modules required to run the MRMS.
Run the following.
-	py -m ensurepip –upgrade

Once pip is installed, a user can then run the following.
-	pip install git+https://github.com/remykarem/py2pddl#egg=py2pddl
-	pip install pddl_parser
-	pip install pygame

Once these steps are completed, the MRMS should be able to run.



#### After you are done playing with the application you can deactivate virtual env or close terminal (To do that follow steps below.)

---

### Deactivating the Virtual Environment (or you can close your terminal)

Once you are done running or playing with your code, you can deactivate the virtual environment by running:

```bash
deactivate
```




