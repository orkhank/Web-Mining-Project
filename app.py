import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
import seaborn as sns
import streamlit as st
from sklearn.model_selection import train_test_split
from preprocess import preprocess_pipeline, clean_data
from st_pages import show_pages_from_config
from sklearn.preprocessing import LabelEncoder
from sklearn.feature_extraction.text import CountVectorizer
from sklearn.naive_bayes import MultinomialNB
from sklearn.pipeline import Pipeline
from sklearn.metrics import (
    RocCurveDisplay,
    accuracy_score,
    auc,
    confusion_matrix,
    f1_score,
    precision_score,
    recall_score,
    roc_curve,
)
from preprocess import *


class SpamClassifierApp:
    def __init__(self):
        self.dataset_folder = "datasets/archive"
        self.dataset_dict = {
            "Spam Assassin": f"{self.dataset_folder}/completeSpamAssassin.csv",
            "EnronSpam": f"{self.dataset_folder}/enronSpamSubset.csv",
            "LingSpam": f"{self.dataset_folder}/lingSpam.csv",
        }
        self.algorithmList = ["Naive Bayes", "SVM", "Random Forest"]
        self.cleaning_utils = {
            "remove_hyperlink": remove_hyperlink,
            "replace_newline": replace_newline,
            "to_lower": to_lower,
            "remove_number": remove_number,
            "remove_punctuation": remove_punctuation,
            "remove_whitespace": remove_whitespace,
        }

    def load_data(self):
        with st.sidebar:
            dataset_selectbox = st.selectbox("# Dataset", self.dataset_dict.keys())
            algorithm_selectbox = st.selectbox("# Algorithm", self.algorithmList)
            preprocess_utils_multibox = st.multiselect("# Preprocess", self.cleaning_utils.keys())

        if (not dataset_selectbox )or (not algorithm_selectbox) or( not preprocess_utils_multibox):
            st.stop()

        data = clean_data(pd.read_csv(self.dataset_dict[dataset_selectbox]))
        return data, algorithm_selectbox, preprocess_utils_multibox

    def preprocess_data(self, data , algorithm_selectbox, preprocess_utils):
        # Your preprocess pipeline here
        pass

    def split_data(self, data , algorithm_selectbox, preprocess_utils):
        emails_train, emails_test, target_train, target_test = train_test_split(
            data["Body"], data["Label"], test_size=0.2, random_state=42
        )

        X_train = [preprocess_pipeline(x, [self.cleaning_utils.get(util) for util in preprocess_utils]) for x in emails_train]
        X_test = [preprocess_pipeline(x, [self.cleaning_utils.get(util) for util in preprocess_utils]) for x in emails_test]
        le = LabelEncoder()
        
        y_train = np.array(le.fit_transform(target_train.values))
        y_test = np.array(le.transform(target_test.values))

        return X_train, X_test, y_train, y_test

    def train_naive_bayes(self, X_train, y_train):
        naive_bayes_clf = Pipeline([("vectorizer", CountVectorizer()), ("nb", MultinomialNB())])
        naive_bayes_clf.fit(X_train, y_train)
        return naive_bayes_clf

    def evaluate_naive_bayes(self, clf, X_test, y_test):
        y_predict = [1 if o > 0.5 else 0 for o in clf.predict(X_test)]

        st.write("Accuracy: {:.2f}%".format(100 * accuracy_score(y_test, y_predict)))
        st.write("Precision: {:.2f}%".format(100 * precision_score(y_test, y_predict)))
        st.write("Recall: {:.2f}%".format(100 * recall_score(y_test, y_predict)))
        st.write("F1 Score: {:.2f}%".format(100 * f1_score(y_test, y_predict)))

        # Confusion Matrix
        cf_matrix = confusion_matrix(y_test, y_predict)
        fig = plt.figure()
        ax = fig.add_subplot()
        sns.heatmap(
            cf_matrix, annot=True, ax=ax, cmap="Blues", fmt=""
        )  # annot=True to annotate cells

        ax.set_xlabel("Predicted labels")
        ax.set_ylabel("True labels")
        ax.set_title("Confusion Matrix")
        ax.xaxis.set_ticklabels(["Not Spam", "Spam"])
        ax.yaxis.set_ticklabels(["Not Spam", "Spam"])

        st.pyplot(ax.figure)  # type: ignore

        # ROC Curve
        y = np.array([0, 0, 1, 1])
        pred = np.array([0.1, 0.4, 0.35, 0.8])
        fpr, tpr, thresholds = roc_curve(y, pred)
        roc_auc = auc(fpr, tpr)
        display = RocCurveDisplay(
            fpr=fpr, tpr=tpr, roc_auc=roc_auc, estimator_name="example estimator"
        )
        st.pyplot(display.plot().figure_)


if __name__ == "__main__":
    app = SpamClassifierApp()
    data, algorithm_selectbox, preprocess_utils = app.load_data()
    X_train, X_test, y_train, y_test = app.split_data(data,algorithm_selectbox, preprocess_utils)
    naive_bayes_clf = app.train_naive_bayes(X_train, y_train)
    app.evaluate_naive_bayes(naive_bayes_clf, X_test, y_test)
