#------------------------------------------------------
# Name      : Gogul Ilango
# Purpose   : Implement Logistic Regression from scratch
#             using python and numpy
# Variants  : 1. LR without L2 regularization
#             2. LR with L2 regularization
# Libraries : numpy, scikit-learn
#------------------------------------------------------

# organize imports
import numpy as np
from sklearn.linear_model import LogisticRegression
from sklearn.model_selection import train_test_split
from sklearn.metrics import accuracy_score

# ignore all warnings
def warn(*args, **kwargs):
    pass
import warnings
warnings.warn = warn

# load scikit-learn's breast cancer dataset
from sklearn.datasets import load_breast_cancer
data = load_breast_cancer()

print(data.keys())
print("No.of.data points (rows) : {}".format(len(data.data)))
print("No.of.features (columns) : {}".format(len(data.feature_names)))
print("No.of.classes            : {}".format(len(data.target_names)))
print("Class names              : {}".format(list(data.target_names)))

# split the dataset into training and testing 
X_train, X_test, y_train, y_test = train_test_split(data.data, data.target, test_size=0.20, random_state=9)

print("X_train : " + str(X_train.shape))
print("y_train : " + str(y_train.shape))
print("X_test : " + str(X_test.shape))
print("y_test : " + str(y_test.shape))

#---------------------------------------------
# logistic regression without regularization
#---------------------------------------------
def sigmoid(score):
	return (1 / (1 + np.exp(-score)))

def predict_probability(features, weights):
	score = np.dot(features, weights)
	return sigmoid(score)

def feature_derivative(errors, feature):
	derivative = np.dot(np.transpose(errors), feature)
	return derivative

def l2_feature_derivative(errors, feature, weight, l2_penalty, feature_is_constant):
	derivative = np.dot(np.transpose(errors), feature)
	if not feature_is_constant:
		derivative -= 2 * l2_penalty * weight
	return derivative

def compute_log_likelihood(features, labels, weights):
	indicators = (labels==+1)
	scores     = np.dot(features, weights)
	ll         = np.sum((np.transpose(np.array([indicators]))-1)*scores - np.log(1. + np.exp(-scores)))
	return ll

def l2_compute_log_likelihood(features, labels, weights, l2_penalty):
	indicators = (labels==+1)
	scores     = np.dot(features, weights)
	ll         = np.sum((np.transpose(np.array([indicators]))-1)*scores - np.log(1. + np.exp(-scores))) - (l2_penalty * np.sum(weights[1:]**2))
	return ll

# logistic regression without L2 regularization
def logistic_regression(features, labels, weights, lr, epochs):

	# initialize the weight coefficients
	weights = np.array(weights)

	# loop over epochs times
	for epoch in range(epochs):

		# predict probability for each row in the dataset
		predictions = predict_probability(features, weights)

		# calculate the indicator value
		indicators = (labels==+1)

		# calculate the errors
		errors = np.transpose(np.array([indicators])) - predictions

		# loop over each weight coefficient
		for j in range(len(weights)):

			# calculate the derivative of jth weight cofficient
			derivative = feature_derivative(errors, features[:,j])
			weights[j] += lr * derivative

		# compute the log-likelihood
		if epoch <= 15 or (epoch <= 100 and epoch % 10 == 0) or (epoch <= 1000 and epoch % 100 == 0) \
		    or (epoch <= 10000 and epoch % 1000 == 0) or epoch % 10000 == 0:
			ll = compute_log_likelihood(features, labels, weights)
			print('iteration %*d: log likelihood of observed labels = %.8f' % \
                (int(np.ceil(np.log10(epochs))), epoch, ll))

	return weights

# logistic regression with L2 regularization
def l2_logistic_regression(features, labels, weights, lr, epochs, l2_penalty):

	# initialize the weight coefficients
	weights = np.array(weights)

	# loop over epochs times
	for epoch in range(epochs):

		# predict probability for each row in the dataset
		predictions = predict_probability(features, weights)

		# calculate the indicator value
		indicators = (labels==+1)

		# calculate the errors
		errors = np.transpose(np.array([indicators])) - predictions

		# loop over each weight coefficient
		for j in range(len(weights)):

			isIntercept = (j==0)

			# calculate the derivative of jth weight cofficient
			derivative = l2_feature_derivative(errors, features[:,j], weights[j], l2_penalty, isIntercept)
			weights[j] += lr * derivative

		# compute the log-likelihood
		if epoch <= 15 or (epoch <= 100 and epoch % 10 == 0) or (epoch <= 1000 and epoch % 100 == 0) \
		    or (epoch <= 10000 and epoch % 1000 == 0) or epoch % 10000 == 0:
			ll = l2_compute_log_likelihood(features, labels, weights, l2_penalty)
			print('iteration %*d: log likelihood of observed labels = %.8f' % \
                (int(np.ceil(np.log10(epochs))), epoch, ll))

	return weights

# logistic regression without regularization
def lr_without_regularization():
	# initialize weights to zero
	init_weights  = np.zeros((len(data.feature_names),1))

	# hyper-parameters
	learning_rate = 1e-7
	epochs        = 500

	# perform logistic regression and get the learned weights
	learned_weights = logistic_regression(X_train, y_train, init_weights, learning_rate, epochs)

	# make predictions using learned weights on testing data
	predictions = predict_probability(X_test, learned_weights)
	class_predictions = (predictions.flatten()>0.5)
	print("Accuracy of our LR classifier: {}".format(accuracy_score(np.expand_dims(y_test, axis=1), (predictions.flatten())>0.5)))

	# using scikit-learn's logistic regression classifier
	model = LogisticRegression(random_state=9)
	model.fit(X_train, y_train)
	sk_predictions = model.predict(X_test)
	print("Accuracy of scikit-learn's LR classifier: {}".format(accuracy_score(y_test, sk_predictions)))

# logistic regression with regularization
def lr_with_regularization():
	# initialize weights to zero
	init_weights  = np.zeros((len(data.feature_names),1))

	# hyper-parameters
	learning_rate = 1e-7
	epochs        = 1000
	l2_penalty    = 50

	# perform logistic regression and get the learned weights
	learned_weights = l2_logistic_regression(X_train, y_train, init_weights, learning_rate, epochs, l2_penalty)

	# make predictions using learned weights on testing data
	test_predictions  = (predict_probability(X_test, learned_weights).flatten()>0.5)
	train_predictions = (predict_probability(X_train, learned_weights).flatten()>0.5)
	print("Accuracy of our LR classifier on training data: {}".format(accuracy_score(np.expand_dims(y_train, axis=1), train_predictions)))
	print("Accuracy of our LR classifier on testing data: {}".format(accuracy_score(np.expand_dims(y_test, axis=1), test_predictions)))

	# using scikit-learn's logistic regression classifier
	model = LogisticRegression(random_state=9)
	model.fit(X_train, y_train)
	sk_test_predictions  = model.predict(X_test)
	sk_train_predictions = model.predict(X_train)
	print("Accuracy of scikit-learn's LR classifier on training data: {}".format(accuracy_score(y_train, sk_train_predictions)))
	print("Accuracy of scikit-learn's LR classifier on testing data: {}".format(accuracy_score(y_test, sk_test_predictions)))

lr_with_regularization()