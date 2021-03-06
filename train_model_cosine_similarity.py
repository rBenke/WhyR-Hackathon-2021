import numpy as np
import pandas as pd

from gensim.models.doc2vec import Doc2Vec
from plotly.subplots import make_subplots
from sklearn.model_selection import StratifiedKFold
from sklearn.metrics import accuracy_score, f1_score

from utils.plotting import result_trace, result_mean_trace

target = 'label'
vector_size = '100-better-data-window-9'


def predict(model, item1, item2, threshold=0.5):
    return int(model.docvecs.similarity(item1, item2) > threshold)


df_train = pd.read_csv('data/train.csv')
df_train['ltable_id'] = 'A_' + df_train['ltable_id'].astype(str)
df_train['rtable_id'] = 'B_' + df_train['rtable_id'].astype(str)

model = Doc2Vec.load(f'models/doc2vec-{vector_size}.model')

n_splits = 10
cv = StratifiedKFold(n_splits=n_splits).split(df_train, df_train[target])
threshold = 0.7

results_train_acc = []
results_train_f1 = []
results_test_acc = []
results_test_f1 = []

for train_id, test_idx in cv:
    y_true_train = df_train.iloc[train_id][target]
    y_true_test = df_train.iloc[test_idx][target]
    y_pred_train = df_train.iloc[train_id].apply(
        lambda row: predict(model, row['ltable_id'], row['rtable_id'], threshold), axis=1)
    y_pred_test = df_train.iloc[test_idx].apply(
        lambda row: predict(model, row['ltable_id'], row['rtable_id'], threshold), axis=1)

    results_train_acc.append(accuracy_score(y_true_train, y_pred_train))
    results_train_f1.append(f1_score(y_true_train, y_pred_train))
    results_test_acc.append(accuracy_score(y_true_test, y_pred_test))
    results_test_f1.append(f1_score(y_true_test, y_pred_test))

x = np.arange(n_splits)

fig = make_subplots(rows=1, cols=2, shared_yaxes=True,
                    subplot_titles=['Accuracy', 'F1 Score'])
fig.add_trace(result_trace(x, results_train_acc, 'Accuracy train', 'blue'), row=1, col=1)
fig.add_trace(result_mean_trace(x, results_train_acc, 'Accuracy train', 'blue'), row=1, col=1)
fig.add_trace(result_trace(x, results_test_acc, 'Accuracy test', 'red'), row=1, col=1)
fig.add_trace(result_mean_trace(x, results_test_acc, 'Accuracy test', 'red'), row=1, col=1)
fig.add_trace(result_trace(x, results_train_f1, 'F1 train', 'blue'), row=1, col=2)
fig.add_trace(result_mean_trace(x, results_train_f1, 'F1 train', 'blue'), row=1, col=2)
fig.add_trace(result_trace(x, results_test_f1, 'F1 train', 'red'), row=1, col=2)
fig.add_trace(result_mean_trace(x, results_test_f1, 'F1 train', 'red'), row=1, col=2)

fig.update_layout(yaxis_range=[0, 1])

fig.write_html(f'outputs/cosine-similarity-{vector_size}.html')
