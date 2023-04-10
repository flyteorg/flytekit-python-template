# {{ cookiecutter.project_name }}

A simple model training workflow that consists of three steps:
* Get the classic wine dataset using sklearn.
* Process the data that simplifies the 3-class prediction problem into a binary classification problem by consolidating class labels 1 and 2 into a single class.
* Train a LogisticRegression model to learn a binary classifier.
