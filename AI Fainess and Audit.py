#1.Load COMPAS Dataset
from aif360.datasets import CompasDataset
compas = CompasDataset()

#2. Explore the data
df, _ = compas.convert_to_dataframe()
print(df.head())

#3. Split Dataset
train, test = compas.split([0.7], shuffle=True)

#4. Bias Metrics - Before Mitigation
from aif360.metrics import BinaryLabelDatasetMetric

metric = BinaryLabelDatasetMetric(train, 
    privileged_groups=[{'race': 1}],  # Caucasian
    unprivileged_groups=[{'race': 0}]  # African-American
)

print("Disparate Impact:", metric.disparate_impact())
print("Statistical Parity Difference:", metric.statistical_parity_difference())

#5. Train Basic Classifier
from sklearn.linear_model import LogisticRegression
from aif360.algorithms.preprocessing import Reweighing

X_train = train.features
y_train = train.labels.ravel()

model = LogisticRegression(max_iter=1000)
model.fit(X_train, y_train)

#6. Predict and Analyze
from aif360.metrics import ClassificationMetric
from aif360.datasets import BinaryLabelDataset

test_pred = test.copy()
pred_labels = model.predict(test.features)
test_pred.labels = pred_labels.reshape(-1, 1)

cm = ClassificationMetric(test, test_pred,
    unprivileged_groups=[{'race': 0}],
    privileged_groups=[{'race': 1}]
)

print("Equal Opportunity Difference:", cm.equal_opportunity_difference())
print("Average Odds Difference:", cm.average_odds_difference())

#7. Visualizations
import seaborn as sns
import matplotlib.pyplot as plt

df['two_year_recid'] = df['two_year_recid'].replace({0: 'No', 1: 'Yes'})

plt.figure(figsize=(8, 5))
sns.countplot(x='race', hue='two_year_recid', data=df)
plt.title("Recidivism Distribution by Race")
plt.show()

