import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
import random
import os
from sklearn.datasets import load_boston
from sklearn.preprocessing import StandardScaler
from sklearn.model_selection import train_test_split
from sklearn.model_selection import KFold
from sklearn.model_selection import cross_val_score
from sklearn.linear_model import LinearRegression
from sklearn.linear_model import Lasso
from sklearn.linear_model import ElasticNet
from sklearn.tree import DecisionTreeRegressor
from sklearn.neighbors import KNeighborsRegressor
from sklearn.svm import SVR
from sklearn.ensemble import AdaBoostRegressor
from sklearn.ensemble import GradientBoostingRegressor
from sklearn.ensemble import RandomForestRegressor
from sklearn.ensemble import ExtraTreesRegressor
from sklearn.metrics import mean_squared_error

pd.options.display.float_format = '{:,.2f}'.format
sns.set(color_codes=True)

dataset = load_boston()
print("[INFO] keys : {}".format(dataset.keys()))

print("[INFO] features shape : {}".format(dataset.data.shape))
print("[INFO] target shape   : {}".format(dataset.target.shape))

print("[INFO] feature names")
print(dataset.feature_names)

print("[INFO] dataset summary")
print(dataset.DESCR)

df = pd.DataFrame(dataset.data)
print("[INFO] df type : {}".format(type(df)))
print("[INFO] df shape: {}".format(df.shape))
print(df.head())

df.columns = dataset.feature_names
print(df.head())

df["PRICE"] = dataset.target
print(df.head())

print(df.dtypes)

print(df.describe())

# correlation between attributes
print("PEARSON CORRELATION")
print(df.corr(method="pearson"))
sns.heatmap(df.corr(method="pearson"))
plt.savefig("heatmap_pearson.png")
plt.clf()
plt.close()

print("SPEARMAN CORRELATION")
print(df.corr(method="spearman"))
sns.heatmap(df.corr(method="spearman"))
plt.savefig("heatmap_spearman.png")
plt.clf()
plt.close()

print("KENDALL CORRELATION")
print(df.corr(method="kendall"))
sns.heatmap(df.corr(method="kendall"))
plt.savefig("heatmap_kendall.png")
plt.clf()
plt.close()

file_report = "boston_housing.txt"
with open(file_report, "w") as f:
	f.write("Features shape : {}".format(df.drop("PRICE", axis=1).shape))
	f.write("\n")
	
	f.write("Target shape   : {}".format(df["PRICE"].shape))
	f.write("\n")
	
	f.write("\nColumn names")
	f.write("\n")
	f.write(str(df.columns))
	f.write("\n")
	
	f.write("\nStatistical summary")
	f.write("\n")
	f.write(str(df.describe()))
	f.write("\n")
	
	f.write("\nDatatypes")
	f.write("\n")
	f.write(str(df.dtypes))
	f.write("\n")
	
	f.write("\nPEARSON correlation")
	f.write("\n")
	f.write(str(df.corr(method="pearson")))
	f.write("\n")

	f.write("\nSPEARMAN correlation")
	f.write("\n")
	f.write(str(df.corr(method="spearman")))
	f.write("\n")
	
	f.write("\nKENDALL correlation")
	f.write("\n")
	f.write(str(df.corr(method="kendall")))

# visualize the dataset
colors = ["y", "b", "g", "r"]

cols = list(df.columns.values)

if not os.path.exists("plots/univariate/box"):
    os.makedirs("plots/univariate/box")

if not os.path.exists("plots/univariate/density"):
    os.makedirs("plots/univariate/density")

# draw a boxplot with vertical orientation
for i, col in enumerate(cols):
	sns.boxplot(df[col], color=random.choice(colors), orient="v")
	plt.savefig("plots/univariate/box/box_" + str(i) + ".png")
	plt.clf()
	plt.close()

# draw a histogram and fit a kernel density estimate (KDE)
for i, col in enumerate(cols):
	sns.distplot(df[col], color=random.choice(colors))
	plt.savefig("plots/univariate/density/density_" + str(i) + ".png")
	plt.clf()
	plt.close()

if not os.path.exists("plots/multivariate"):
    os.makedirs("plots/multivariate")

# bivariate plot between target and reason of absence
for i, col in enumerate(cols):
	if (i == len(cols) - 1):
		pass
	else: 
		sns.jointplot(x=col, y="PRICE", data=df);
		plt.savefig("plots/multivariate/target_vs_" + str(i) + ".png")
		plt.clf()
		plt.close()

X = df.drop("PRICE", axis=1)
Y = df["PRICE"]
print(X.shape)
print(Y.shape)

scaler = StandardScaler().fit(X)
scaled_X = scaler.transform(X)

seed = 9
test_size = 0.20

X_train, X_test, Y_train, Y_test = train_test_split(X, Y, test_size = test_size, random_state = seed)

print(X_train.shape)
print(X_test.shape)
print(Y_train.shape)
print(Y_test.shape)

# user variables to tune
folds   = 10
metric  = "neg_mean_squared_error"

# hold different regression models in a single dictionary
models = {}
models["Linear"]        = LinearRegression()
models["Lasso"]         = Lasso()
models["ElasticNet"]    = ElasticNet()
models["KNN"]           = KNeighborsRegressor()
models["DecisionTree"]  = DecisionTreeRegressor()
models["SVR"]           = SVR()
models["AdaBoost"]      = AdaBoostRegressor()
models["GradientBoost"] = GradientBoostingRegressor()
models["RandomForest"]  = RandomForestRegressor()
models["ExtraTrees"]    = ExtraTreesRegressor()

# 10-fold cross validation for each model
model_results = []
model_names   = []
for model_name in models:
	model   = models[model_name]
	k_fold  = KFold(n_splits=folds, random_state=seed)
	results = cross_val_score(model, X_train, Y_train, cv=k_fold, scoring=metric)
	
	model_results.append(results)
	model_names.append(model_name)
	print("{}: {}, {}".format(model_name, round(results.mean(), 3), round(results.std(), 3)))

# box-whisker plot to compare regression models
figure = plt.figure()
figure.suptitle('Regression models comparison')
axis = figure.add_subplot(111)
plt.boxplot(model_results)
axis.set_xticklabels(model_names, rotation = 45, ha="right")
axis.set_ylabel("Mean Squared Error (MSE)")
plt.margins(0.05, 0.1)
plt.show()

# create and fit the best regression model
best_model = GradientBoostingRegressor(random_state=seed)
best_model.fit(X_train, Y_train)

# make predictions using the model
predictions = best_model.predict(X_test)
print("[INFO] MSE : {}".format(round(mean_squared_error(Y_test, predictions), 3)))

plt.scatter(predictions, Y_test, alpha=0.5)
plt.show()