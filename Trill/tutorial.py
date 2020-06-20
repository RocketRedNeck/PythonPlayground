# Machine Learning Tutorial from https://machinelearningmastery.com/machine-learning-in-python-step-by-step/

# Work through the tutorial. It will take you 5-to-10 minutes, max!

# You do not need to understand everything. (at least not right now) 
# Your goal is to run through the tutorial end-to-end and get a result. 
# You do not need to understand everything on the first pass. 
# List down your questions as you go. 
# Make heavy use of the help(“FunctionName”) help syntax in Python to learn about 
# all of the functions that you’re using.

# You do not need to know how the algorithms work. 
# It is important to know about the limitations and how to configure machine learning algorithms.
# But learning about algorithms can come later. You need to build up this algorithm knowledge 
# slowly over a long period of time. 
# Today, start off by getting comfortable with the platform.

# You do not need to be a Python programmer. 
# The syntax of the Python language can be intuitive if you are new to it. 
# Just like other languages, focus on function calls (e.g. function()) and assignments (e.g. a = “b”). 
# This will get you most of the way. 
# You are a developer, you know how to pick up the basics of a language real fast. 
# Just get started and dive into the details later.

# You do not need to be a machine learning expert. 
# You can learn about the benefits and limitations of various algorithms later, 
# and there are plenty of posts that you can read later to brush up on the steps of 
# a machine learning project and the importance of evaluating accuracy using cross validation.

# What about other steps in a machine learning project.
# We did not cover all of the steps in a machine learning project because this is your 
# first project and we need to focus on the key steps. Namely, loading data, looking at the data, 
# evaluating some algorithms and making some predictions. In later tutorials we can look at other data 
# preparation and result improvement tasks.

# Check the versions of libraries
import sys
print(f'Python: {sys.version}')
import scipy
print(f'scipy: {scipy.__version__}')
import numpy
print(f'numpy: {numpy.__version__}')
import matplotlib
print(f'matplotlib: {matplotlib.__version__}')
import pandas
print(f'pandas: {pandas.__version__}')
import sklearn
print(f'sklearn: {sklearn.__version__}')

# LOAD DATA

# Load library pieces we really need
from pandas import read_csv
from pandas.plotting import scatter_matrix
from matplotlib import pyplot
from sklearn.model_selection import train_test_split
from sklearn.model_selection import cross_val_score
from sklearn.model_selection import StratifiedKFold
from sklearn.metrics import classification_report
from sklearn.metrics import confusion_matrix
from sklearn.metrics import accuracy_score
from sklearn.linear_model import LogisticRegression
from sklearn.tree import DecisionTreeClassifier
from sklearn.neighbors import KNeighborsClassifier
from sklearn.discriminant_analysis import LinearDiscriminantAnalysis
from sklearn.naive_bayes import GaussianNB
from sklearn.svm import SVC

# Load dataset
# We can load the data directly from the UCI Machine Learning repository.
# We are using pandas to load the data. 
# We will also use pandas next to explore the data both with descriptive statistics and data visualization.
#
# Note that we are specifying the names of each column when loading the data. 
# This will help later when we explore the data.
url = "https://raw.githubusercontent.com/jbrownlee/Datasets/master/iris.csv"
names = ['sepal-length', 'sepal-width', 'petal-length', 'petal-width', 'class']
dataset = read_csv(url, names=names)

# SUMMARIZE THE DATASET

# In this step we are going to take a look at the data a few different ways:
# 1. Dimensions of the dataset.
# 2. Peek at the data itself.
# 3. Statistical summary of all attributes.
# 4. Breakdown of the data by the class variable.

print(dataset.shape)
print(dataset.head(20))
print(dataset.describe())
print(dataset.groupby('class').size())

# DATA VISUALIZATION

# We are going to look at two types of plots:
# 1. Univariate plots to better understand each attribute.
# 2. Multivariate plots to better understand the relationships between attributes.

# box and whisker plots
# This gives us a much clearer idea of the distribution of the input attributes
dataset.plot(kind='box', subplots=True, layout=(2,2), sharex=False, sharey=False)

# histograms
# It looks like perhaps two of the input variables have a Gaussian distribution. 
# This is useful to note as we can use algorithms that can exploit this assumption
dataset.hist()

# show plots and pause until windows closed
print('\nCLOSE Figures to Continue')
pyplot.show()

# Now we can look at the interactions between the variables.
# Let’s look at scatterplots of all pairs of attributes. 
# This can be helpful to spot structured relationships between input variables.
# Note the diagonal grouping of some pairs of attributes. 
# This suggests a high correlation and a predictable relationship.
scatter_matrix(dataset)
print('\nCLOSE Figures to Continue')
pyplot.show()

# EVALUATE SOME ALGORITHMS

# Now it is time to create some models of the data and estimate their accuracy on unseen data.
# Here is what we are going to cover in this step:
#
# 1. Separate out a validation dataset.
# 2. Set-up the test harness to use 10-fold cross validation.
# 3. Build multiple different models to predict species from flower measurements
# 4. Select the best model.

# We need to know that the model we created is good.
# Later, we will use statistical methods to estimate the accuracy of the models that 
# we create on unseen data. We also want a more concrete estimate of the accuracy of the best model on 
# unseen data by evaluating it on actual unseen data.
#
# That is, we are going to hold back some data that the algorithms will not get to see and we will 
# use this data to get a second and independent idea of how accurate the best model might actually be.
#
# We will split the loaded dataset into two, 80% of which we will use to train, evaluate and select 
# among our models, and 20% that we will hold back as a validation dataset.

# Split-out validation dataset
array = dataset.values
X = array[:,0:4]
y = array[:,4]
X_train, X_validation, Y_train, Y_validation = train_test_split(X, y, test_size=0.20, random_state=1)

# You now have training data in the X_train and Y_train for preparing models and a 
# X_validation and Y_validation sets that we can use later.

# We will use stratified 10-fold cross validation to estimate model accuracy.
#
# This will split our dataset into 10 parts, train on 9 and test on 1 and repeat 
# for all combinations of train-test splits.
#
# Stratified means that each fold or split of the dataset will aim to have the same 
# distribution of example by class as exist in the whole training dataset.
#
# For more on the k-fold cross-validation technique, see the tutorial:
#
# A Gentle Introduction to k-fold Cross-Validation 
# (https://machinelearningmastery.com/k-fold-cross-validation/)
#
# We set the random seed via the random_state argument to a fixed number to ensure 
# that each algorithm is evaluated on the same splits of the training dataset.
#
# The specific random seed does not matter, learn more about pseudorandom number generators here:
#
# Introduction to Random Number Generators for Machine Learning in Python
# (https://machinelearningmastery.com/introduction-to-random-number-generators-for-machine-learning/)
#
# We are using the metric of ‘accuracy‘ to evaluate models.
#
# This is a ratio of the number of correctly predicted instances divided by the total number 
# of instances in the dataset multiplied by 100 to give a percentage (e.g. 95% accurate). 
# We will be using the scoring variable when we run build and evaluate each model next.

# Build Models
# We don’t know which algorithms would be good on this problem or what configurations to use.
#
# We get an idea from the plots that some of the classes are partially linearly separable in some dimensions, so we are expecting generally good results.
#
# Let’s test 6 different algorithms:
#
# 1. Logistic Regression (LR)
# 2. Linear Discriminant Analysis (LDA)
# 3. K-Nearest Neighbors (KNN).
# 4. Classification and Regression Trees (CART).
# 5. Gaussian Naive Bayes (NB).
# 6. Support Vector Machines (SVM).
# 
# This is a good mixture of simple linear (LR and LDA), nonlinear (KNN, CART, NB and SVM) algorithms.
# Let’s build and evaluate our models

# Spot Check Algorithms
models = []
models.append(('LR', LogisticRegression(solver='liblinear', multi_class='ovr')))
models.append(('LDA', LinearDiscriminantAnalysis()))
models.append(('KNN', KNeighborsClassifier()))
models.append(('CART', DecisionTreeClassifier()))
models.append(('NB', GaussianNB()))
models.append(('SVM', SVC(gamma='auto')))
# evaluate each model in turn
results = []
names = []
print(' name,   mean, (stddev)')
for name, model in models:
	kfold = StratifiedKFold(n_splits=10, random_state=1, shuffle=True)
	cv_results = cross_val_score(model, X_train, Y_train, cv=kfold, scoring='accuracy')
	results.append(cv_results)
	names.append(name)
	print(f'{name:5s}, {cv_results.mean():.4f}, ({cv_results.std():.4f})')

# Note, you’re results may vary given the stochastic nature of the learning algorithms.
# For more on this see the post:
# Embrace Randomness in Machine Learning
# (https://machinelearningmastery.com/randomness-in-machine-learning/)

# We now have 6 models and accuracy estimations for each. 
# We need to compare the models to each other and select the most accurate.

# In this case, we can see that it looks like Support Vector Machines (SVM) 
# has the largest estimated accuracy score at about 0.98 or 98%.
#
# We can also create a plot of the model evaluation results and compare the spread 
# and the mean accuracy of each model. There is a population of accuracy measures for 
# each algorithm because each algorithm was evaluated 10 times (via 10 fold-cross validation).
#
# A useful way to compare the samples of results for each algorithm is to create a box 
# and whisker plot for each distribution and compare the distributions.

# Compare Algorithms
pyplot.boxplot(results, labels=names)
pyplot.title('Algorithm Comparison')
print('\nCLOSE Figures to Continue')
pyplot.show()

# We can see that the box and whisker plots are squashed at the top of the range, 
# with many evaluations achieving 100% accuracy, and some pushing down into the high 
# 80% accuracies

# MAKE PREDICTIONS

# We must choose an algorithm to use to make predictions.
#
# The results in the previous section suggest that the SVM was perhaps the most accurate 
# model. We will use this model as our final model.
#
# Now we want to get an idea of the accuracy of the model on our validation set.
#
# This will give us an independent final check on the accuracy of the best model. 
# It is valuable to keep a validation set just in case you made a slip during training, 
# such as overfitting to the training set or a data leak. Both of these issues will result in 
# an overly optimistic result.

# We can fit the model on the entire training dataset and make predictions on the validation dataset.

# Make predictions on validation dataset
model = SVC(gamma='auto')
model.fit(X_train, Y_train)
predictions = model.predict(X_validation)

# You might also like to make predictions for single rows of data.
# For examples on how to do that, see the tutorial:
#
# How to Make Predictions with scikit-learn
# (https://machinelearningmastery.com/make-predictions-scikit-learn/)
#
# You might also like to save the model to file and load it later to make predictions on new data. 
# For examples on how to do this, see the tutorial:
#
# Save and Load Machine Learning Models in Python with scikit-learn
# (https://machinelearningmastery.com/save-load-machine-learning-models-python-scikit-learn/)

# We can evaluate the predictions by comparing them to the expected results in the 
# validation set, then calculate classification accuracy, as well as a confusion matrix 
# and a classification report.

# Evaluate predictions
print("ACCURACY SCORE")
print(accuracy_score(Y_validation, predictions))
print("CONFUSION MATRIX")
print(confusion_matrix(Y_validation, predictions))
print("CLASSIFICATION REPORT")
print(classification_report(Y_validation, predictions))

# We can see that the accuracy is 0.966 or about 96% on the hold out dataset.
#
# The confusion matrix provides an indication of the three errors made.
#
# Finally, the classification report provides a breakdown of each class by precision, 
# recall, f1-score and support showing excellent results (granted the validation dataset 
# was small).


