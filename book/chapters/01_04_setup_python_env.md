# 1.4 - Setup your python environment

In this lesson we will start creating the game. We will create a python environment and have a basic initial structure of the game, to start coding it.

This is the step by step approach that you can follow:

## Create a new folder for the project

Find a suitable location for your project and create a new folder, for example:

```
mkdir my_game
cd my_game
```

Now you are in the project folder. Optionally you can also open it in your favorite file explorer. The folder should be completely empty, with no files or subfolders for now, otherwise it will become a mess very soon.

### Create a virtual environment

### What is a virtual environment?

A virtual environment is a self-contained directory that contains a Python interpreter and libraries. It allows you to isolate your project's dependencies from the system Python and from other projects. This is very useful because it allows you to control exactly which libraries your project uses, without affecting other projects or the system as a whole.

Think of a virtual environment like a sandbox where you can play with different libraries and versions of Python, without affecting the rest of your system.

### How to create a virtual environment

To create a virtual environment, you can use the following command:

```
python3 -m venv .venv
```

This will create a new directory called `.venv` in the current directory, which will contain a Python interpreter and all the necessary libraries for your project.

Once the virtual environment is created, you can activate it by running the following command:

```
source .venv/bin/activate
```

Activating the virtual environment will set the environment variables to point to the virtual environment's Python interpreter and libraries. This will enable us to use the virtual environment's Python interpreter and libraries for our project, instead of the system's Python interpreter and libraries. Why do we have to do so? Well, because we want to control exactly which libraries our project uses, without affecting other projects or the system as a whole.

Now to test our virtual environment, let's create a test script. Go ahead and create a file called `main.py` and add the following code:

```python
print("Hello, world!")
```

Now let's run the script. Back in the terminal, with the virtual environment activated, run the following command:

```
python main.py
```

You should see the following output in the terminal

```
Hello, world!
```

That's it! You have successfully created a virtual environment and tested it.

Now that we have a virtual environment set up, let's move forward with the game.