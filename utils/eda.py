# utils/eda.py
import os
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
from sklearn.preprocessing import StandardScaler
from sklearn.cluster import KMeans
from sklearn.decomposition import PCA

def load_csv(filelike):
    """filelike: caminho (str) ou file-like (uploaded file). Retorna DataFrame."""
    if isinstance(filelike, str):
        df = pd.read_csv(filelike)
    else:
        # streamlit uploaded file is file-like
        df = pd.read_csv(filelike)
    return df

def get_column_types(df):
    numeric = df.select_dtypes(include=[np.number]).columns.tolist()
    categorical = df.select_dtypes(exclude=[np.number]).columns.tolist()
    return {"numeric": numeric, "categorical": categorical}

def describe_numeric(df):
    num = df.select_dtypes(include=[np.number])
    desc = num.describe().T
    desc['median'] = num.median()
    desc['variance'] = num.var()
    # reorder useful columns
    keep = ['count','mean','median','std','variance','min','25%','50%','75%','max']
    for k in keep:
        if k not in desc.columns:
            desc[k] = np.nan
    return desc[keep]

def generate_histograms(df, columns=None, outdir='outputs'):
    os.makedirs(outdir, exist_ok=True)
    if columns is None:
        columns = df.select_dtypes(include=[np.number]).columns.tolist()
    images = {}
    for col in columns:
        try:
            plt.figure()
            df[col].dropna().hist(bins=50)
            plt.title(f'Histograma - {col}')
            path = os.path.join(outdir, f'hist_{col}.png')
            plt.savefig(path, bbox_inches='tight')
            plt.close()
            images[col] = path
        except Exception as e:
            images[col] = f"erro: {e}"
    return images

def correlation_matrix(df, outdir='outputs'):
    os.makedirs(outdir, exist_ok=True)
    num = df.select_dtypes(include=[np.number])
    corr = num.corr()
    plt.figure(figsize=(10,8))
    plt.imshow(corr, interpolation='nearest')
    plt.colorbar()
    plt.xticks(range(len(corr.columns)), corr.columns, rotation=90)
    plt.yticks(range(len(corr.columns)), corr.columns)
    path = os.path.join(outdir, 'correlation_matrix.png')
    plt.title('Matriz de Correlação')
    plt.savefig(path, bbox_inches='tight')
    plt.close()
    return corr, path

def detect_outliers_iqr(df, columns=None):
    if columns is None:
        columns = df.select_dtypes(include=[np.number]).columns
    outlier_indices = set()
    detail = {}
    for col in columns:
        col_values = df[col].dropna()
        Q1 = col_values.quantile(0.25)
        Q3 = col_values.quantile(0.75)
        IQR = Q3 - Q1
        lower = Q1 - 1.5 * IQR
        upper = Q3 + 1.5 * IQR
        mask = (df[col] < lower) | (df[col] > upper)
        idxs = df[mask].index.tolist()
        detail[col] = {"count": len(idxs), "indices": idxs}
        outlier_indices.update(idxs)
    return sorted(list(outlier_indices)), detail

def cluster_analysis(df, n_clusters=3, features=None, outdir='outputs'):
    os.makedirs(outdir, exist_ok=True)
    num = df.select_dtypes(include=[np.number]).fillna(0)
    if features:
        X = num[features]
    else:
        # limit dims for stability (use first up to 10 numeric features)
        X = num.iloc[:, :min(10, num.shape[1])]
    scaler = StandardScaler()
    Xs = scaler.fit_transform(X)
    kmeans = KMeans(n_clusters=n_clusters, random_state=42)
    labels = kmeans.fit_predict(Xs)
    # 2D projection for plotting
    pca = PCA(n_components=2)
    proj = pca.fit_transform(Xs)
    plt.figure()
    plt.scatter(proj[:,0], proj[:,1], c=labels, s=10)
    plt.title(f'Clusters (k={n_clusters}) - projeção PCA 2D')
    path = os.path.join(outdir, f'clusters_k{n_clusters}.png')
    plt.savefig(path, bbox_inches='tight')
    plt.close()
    return labels, path
