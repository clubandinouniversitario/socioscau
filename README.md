# 🏔️ CAU - Club Andino Universitario Setup Instructions #
Website for members of [Club Andino Universitario](https://www.cau.cl). Accessible in https://socios.cau.cl
Main purpose is to manage mountain trips notices or others.
In the future it's expected to help the management of more functionalities.

## 📝 Prerequisites: ##
🐍 Python 3.8.9 or higher
🐘 PostgreSQL

## 🔧 Installation & Setup:##
1. 📦 Clone the Repository
```
git clone https://github.com/clubandinouniversitario/socioscau.git
```
2. 🔐 Create your own PostgreSQL database

<sub>Assuming you're in the PostgreSQL interactive terminal (psql):</sub>
```
CREATE DATABASE your_database_name;
CREATE USER your_user_name WITH PASSWORD 'your_password';
GRANT ALL PRIVILEGES ON DATABASE your_database_name TO your_user_name;
```
Remember to securely store your database name, user, and password for later use.

3. 🍃 Virtual Environment and installing requirements
A virtual environment is a tool that helps to keep dependencies required by different projects separate by creating isolated Python virtual environments for them.
Create the virtual environment. We recommend to do this in the root folder (socioscau):
```
python3 -m venv venv
```
Activate the virtual environment:
```
source venv/bin/activate
```
Activating a virtual environment is required to use pip and python commands for this project.
To deactivate it just use:
```
deactivate
```
Once activated, install the project's requirements:
```
pip install -r requirements.txt
```
4. 🔑 Setting up the .env File
There's a file named env_template.txt in the repository. Make a copy and rename it .env (yes, with a dot at the beginning and without extension). This file will be your local environment variables container, which will keep sensitive information like the DJANGO_SECRET_KEY and database credentials. Follow the instructions in the file.

🔹 DJANGO_SECRET_KEY: It's a secret key for a particular Django installation. This is used to provide cryptographic signing, and should be set to a unique, unpredictable value.

5. Now you can run the following commands in the folder socioscau/webcau:
```
python manage.py migrate
python manage.py collectstatic
python manage.py runserver
```


## 📂 Understanding the Repository Structure ##
Navigating through the project, it's essential to understand its layout to help developers locate specific functionalities or components. Here's a brief rundown of the directory structure and essential files:

### webcau ###

This is the core Django project folder. It holds the primary configuration and app initializations.

**settings.py:** The primary settings/configuration file for the entire Django project.
**urls.py:** The main URL configuration for the project. Here, URLs are mapped to views.

### avisos ###
Represents a Django app focusing on announcements and related features.

**models:** Folder that contains Python classes that define the database structure (tables, relationships, etc.).
**views:** Folder that contains the business logic and manages the app's HTTP responses.
**urls.py:** Local URL configurations specific to the avisos app.
**forms.py:** Defines forms used for the app, ensuring data validation and integrity.
**admin.py:** Customizes the Django Admin interface for this app.
**templates/avisos:** HTML templates related specifically to the avisos app.
**management/commands:** Contains custom management commands that can be executed via the manage.py script.

### static ###
This directory hosts static files like CSS, JavaScript, and images. These files don't change often and aren't generated dynamically.

css: Bootstrap + customized css
js: Bootstrap + customized JS
images: Contains various image assets used in the project.

### templates ###
Hosts global HTML templates not tied to a specific app. These might include error pages, layouts, or base templates.

### Root Files ###
**README.md:** The file you're reading now, explaining the project and its setup.
**env_template.txt:** Likely a template or example for setting up your environment variables.
**requirements.txt:** Lists all the Python packages required for the project.
**manage.py:** A Django utility script that helps with various tasks like database migrations, starting the development server, and creating apps.


## 🛠️ Development Guidelines ##
### 🔍 General Philosophy ###
Always aim for clean, maintainable, and well-documented code. Code should not only work, but it should be understandable for other developers who might take over your task or work with you. Remember, code reviews are not only for catching bugs but for ensuring code quality and maintainability.

### 🌳 Branching Strategy ###
When developing new features or fixes, we don't work directly on the main or master branch. Instead, we use a feature branching workflow.

### 📜 Steps for New Features: ###
Create a New Branch: Before you start with your feature, create a new branch for that feature. Name it relevantly so others have an idea of what it contains.

```
git checkout -b feature/your-feature-name
```

Develop Your Feature: Make your changes, updates, and develop the feature in this branch. Commit regularly to save your progress.

Stay Updated: Regularly pull changes from the main or master branch to ensure your feature branch is up-to-date and to resolve any potential merge conflicts.

```
git pull origin main
```
Push the Feature Branch: Once you've developed your feature, push your feature branch to the remote repository.

```
git push -u origin feature/your-feature-name
```
Open a Pull Request (PR): Go to the repository on GitHub and open a new pull request. This allows team members to review your code.

Add a detailed PR message, describing the feature you've added or the problem you're solving.
Attach any relevant issue numbers.
Code Review: Once the PR is opened, another developer should review the code. They should ensure it adheres to our coding standards and that it works as expected. Feedback should be constructive and aim at improving the overall quality of the code.

Merge: Once the PR has been approved and all CI tests pass, the feature branch can be merged into the main or master branch.

Clean Up: After merging, it's a good practice to delete the feature branch both locally and remotely.

```
git branch -d feature/your-feature-name       # deletes local branch
git push origin --delete feature/your-feature-name   # deletes remote branch
```
### ⚠️ Important Notes: ###
Always ensure that your feature is complete and tested before opening a PR.
If a PR has feedback that requires changes, make them in your feature branch, then push those changes. The PR will update automatically.



