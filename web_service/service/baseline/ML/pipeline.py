import pandas as pd
import joblib


def predict_pipeline(js):
    """
    Пайплайн препроцессинга данных и осуществления предсказания
    input: список словарей со значениями objects и subjects
    output: список словарей со значениями objects и subjects и двумя результирующими ключами - вероятностей (probabilities) и предсказаний(predictions)
    """

    classes_dict = {
        "behind": 0,
        "has": 1,
        "holding": 2,
        "in": 3,
        "near": 4,
        "of": 5,
        "on": 6,
        "on top of": 7,
        "wearing": 8,
        "with": 9,
    }

    model_pkl_file = "service/baseline/src/RFClf.pkl"
    vectorizer_file = "service/baseline/src/CountVectorizer.pkl"
    # repo='https://github.com/NLP-team-MOVS2023/nlp_project_MOVS.git'

    # with dvc.api.open(model_pkl_file, repo=repo, mode='rb') as file:
    #     model = joblib.load(file)

    # with dvc.api.open(vectorizer_file, repo=repo, mode='rb') as file:
    #     vec = joblib.load(file)

    with open(model_pkl_file, "rb") as f:
        model = joblib.load(f)

    with open(vectorizer_file, "rb") as f:
        vec = joblib.load(f)

    df = pd.DataFrame.from_dict(js, orient="index").T

    X_objects = pd.DataFrame(vec.transform(df["objects"]).todense())
    X_subjects = pd.DataFrame(vec.transform(df["subjects"]).todense())

    X = pd.concat([X_objects, X_subjects], axis=1).reset_index(drop=True)
    X.columns = range(X.columns.size)

    preds = model.predict(X)
    probs = []
    for i, pred in enumerate(preds):
        probs.append(model.predict_proba(X)[i, classes_dict[pred]])

    df["probabilities"] = probs
    df["predicates"] = preds

    res = df.to_dict("index")
    return res
