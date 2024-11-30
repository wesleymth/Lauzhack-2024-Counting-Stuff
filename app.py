from flask import Flask, render_template, request
import plotly.graph_objects as go
import pandas as pd
import numpy as np

app = Flask(__name__)

# Convertir les données en DataFrame
def prepare_data(data):
    timestamps = [entry["timestamp"] for entry in data]
    processed_data = {"timestamp": pd.to_datetime(timestamps)}

    for key in data[0].keys():
        if key != "timestamp":
            processed_data[key] = [entry[key] if isinstance(entry[key], list) else [entry[key]] for entry in data]

    return pd.DataFrame(processed_data)

# Calcul des moyennes et des intervalles de confiance
def get_statistical_summary(values):
    means = [np.mean(v) for v in values]
    stds = [np.std(v) for v in values]
    cis = [1.96 * (s / np.sqrt(len(v))) if len(v) > 1 else 0 for v, s in zip(values, stds)]
    return means, cis

# Fonction pour créer le graphique Plotly
def create_plot(features):
    fig = go.Figure()
    timestamps = df["timestamp"]

    for feature in features:
        values = df[feature]

        if isinstance(values.iloc[0], list):
            # Calculer moyennes et IC pour les listes
            means, cis = get_statistical_summary(values)
            fig.add_trace(go.Scatter(
                x=timestamps, y=means, mode="lines+markers", name=f"Moyenne {feature}"
            ))
            fig.add_trace(go.Scatter(
                x=timestamps, y=[m - ci for m, ci in zip(means, cis)],
                mode="lines", line=dict(width=0), showlegend=False
            ))
            fig.add_trace(go.Scatter(
                x=timestamps, y=[m + ci for m, ci in zip(means, cis)],
                mode="lines", fill="tonexty", line=dict(width=0), name=f"IC {feature}"
            ))
        else:
            # Simple lineplot pour les valeurs uniques
            fig.add_trace(go.Scatter(
                x=timestamps, y=[v[0] for v in values], mode="lines+markers", name=feature
            ))

    fig.update_layout(
        title="Caractéristiques sélectionnées au fil du temps",
        xaxis_title="Temps",
        yaxis_title="Valeur",
        hovermode="x unified"
    )
    return fig.to_html(full_html=False)

@app.route('/', methods=["GET", "POST"])
def index():
    selected_features = request.form.getlist("features") if request.method == "POST" else []
    feature_options = [feature for feature in df.columns if feature != "timestamp"]

    # Générer le graphique si des features sont sélectionnées
    graph_html = create_plot(selected_features) if selected_features else ""

    return render_template("index.html", feature_options=feature_options, graph_html=graph_html)

if __name__ == '__main__':
    data = [
    {"timestamp": "2024-11-01", "nombre_puits": 5, "taille_puits": [10, 12, 9, 11, 13]},
    {"timestamp": "2024-11-02", "nombre_puits": 9, "taille_puits": [11, 10, 13, 12, 14, 15, 2, 3, 4]},
    {"timestamp": "2024-11-03", "nombre_puits": 4, "taille_puits": [9, 10, 11, 8]},
    {"timestamp": "2024-11-04", "nombre_puits": 7, "taille_puits": [14, 15, 13, 16, 15, 17, 18]},
]

    df = prepare_data(data)
    app.run(debug=True)
