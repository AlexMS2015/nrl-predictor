import pandas as pd
from scipy.stats import loguniform
from sklearn.preprocessing import StandardScaler, OneHotEncoder
from sklearn.compose import ColumnTransformer
from sklearn.pipeline import Pipeline
from sklearn.metrics import accuracy_score
from sklearn.model_selection import (
    train_test_split,
    TimeSeriesSplit,
    RandomizedSearchCV,
)
from sklearn.linear_model import LogisticRegression


import mlflow
from mlflow import MlflowClient
import mlflow.sklearn
from datetime import datetime
import subprocess

tracking_uri = "https://mlflow-tracking-server-aysxrq6qeq-ts.a.run.app"


ENV = "dev"

mlflow.set_tracking_uri(tracking_uri)
mlflow.set_experiment("nrl_winner_batch")

timestamp = datetime.now().strftime("%Y-%m-%d-%H:%M")
mlflow.start_run(run_name=f"logreg_{timestamp}")
mlflow.autolog()

commit_hash = subprocess.check_output(["git", "rev-parse", "HEAD"]).decode().strip()
mlflow.set_tag("git_commit", commit_hash)


df = pd.read_csv("train_df.csv")
df = df.sort_values(["year", "round_num"])
X = df.drop(columns=["year", "home_win"])
y = df.home_win

test_size = (df.year >= 2025).sum()  # won't work in 2026
X_train, X_test, y_train, y_test = train_test_split(
    X, y, test_size=test_size, shuffle=False
)
num_cols = X.select_dtypes(exclude="object").columns
cat_cols = X.select_dtypes(include="object").columns

# the 20 and 6 need to be dynamic...
tss = TimeSeriesSplit(n_splits=20)
splits = list(tss.split(X_train))[-6:]


param_grid = {"logreg__penalty": ["l1", "l2"], "logreg__C": loguniform(0.1, 100)}

preprocess = ColumnTransformer(
    [
        ("num", StandardScaler(), num_cols),
        (
            "cat",
            OneHotEncoder(drop="first", handle_unknown="ignore"),
            cat_cols,
        ),  # WRONG - it uses a different OHE for home and away team - combine it (but lose H/A info)?
    ]
)

pipe = Pipeline(
    [("preprocess", preprocess), ("logreg", LogisticRegression(solver="liblinear"))]
)

cv = RandomizedSearchCV(
    estimator=pipe,
    param_distributions=param_grid,
    n_iter=5,
    scoring="accuracy",
    cv=splits,
    refit=True,
    verbose=0,
    random_state=2025,
    n_jobs=1,
)
cv.fit(X_train, y_train)


final_model = cv.best_estimator_
y_pred_test = final_model.predict(X_test)
test_accuracy = accuracy_score(y_test, y_pred_test)
print(test_accuracy)  # rather log
mlflow.log_metric("test_accuracy", test_accuracy)


run_id = mlflow.active_run().info.run_id
mlflow.end_run()  # turn off autolog for next cell
mlflow.start_run(run_id=run_id)

deploy_model = final_model.fit(X, y)
info = mlflow.sklearn.log_model(
    deploy_model, artifact_path="deploy_model", registered_model_name="nrl_model_batch"
)
version = info.registered_model_version

client = MlflowClient()
client.set_model_version_tag("nrl_model_batch", version, "environment", ENV)
if ENV == "dev":
    client.set_registered_model_alias("nrl_model_batch", "dev", version)
elif ENV == "prod":
    client.set_registered_model_alias("nrl_model_batch", "staging", version)
    # check if promote to prod...
