from flask import Flask, render_template, request, jsonify
import plotly.graph_objects as go
import numpy as np
import pandas as pd

app = Flask(__name__)

# Exemple de données retournées par le modèle
# Une seule image (liste contenant un seul dictionnaire)
model_results = [{"feature_1": [1, 2, 2, 3, 3, 3, 4, 4, 5], "feature_2": [10, 15, 20, 25], "feature_3": 5}]

file = "data/time-series-port.pkl"
model_results = pd.read_pickle(file)
for i in range(len(model_results)):
    if 'count' not in model_results[i]:
        model_results[i]['count'] = len(model_results[i]['boxes'])

# model_results = [
#    {"date": "2024-11-01", "nombre_puits": 5, "taille_puits": [10, 12, 9, 11, 13]},
#    {"date": "2024-11-02", "nombre_puits": 9, "taille_puits": [11, 10, 13, 12, 14, 15, 2, 3, 4]},
#    {"date": "2024-11-03", "nombre_puits": 4, "taille_puits": [9, 10, 11, 8]},
#    {"date": "2024-11-04", "nombre_puits": 7, "taille_puits": [14, 15, 13, 16, 15, 17, 18]},
#]


@app.route("/")
def index():
    if len(model_results) == 1:  # Une seule image analysée
        features = [key for key, value in model_results[0].items() if isinstance(value, list)]
        plot_type = "single"
    else:  # Plusieurs images analysées
        features = [key for key in model_results[0] if key not in ["date", "boxes", "images_boxes", "cls"]]
        plot_type = "multiple"
    return render_template("index.html", features=features, plot_type=plot_type)

@app.route("/plot", methods=["POST"])
def plot():
    selected_feature = request.json.get("feature")
    plot_type = request.json.get("plot_type")

    if plot_type == "single":  # Une seule image analysée
        data = model_results[0].get(selected_feature, [])
        if isinstance(data, list):  # Distribution pour les features contenant une liste de valeurs
            fig = go.Figure()
            fig.add_trace(go.Histogram(x=data, nbinsx=10))
            fig.update_layout(
                title=f"Distribution de {selected_feature}",
                xaxis_title=selected_feature,
                yaxis_title="Fréquence",
                template="plotly_white",
            )
        else:
            return jsonify({"error": "Feature non valide pour un histogramme."}), 400

    else:  # Plusieurs images analysées
        timestamps = [entry["date"] for entry in model_results]
        values = [entry[selected_feature] for entry in model_results]
        if all(isinstance(v, (int, float)) for v in values):  # Line plot pour une valeur par image
            fig = go.Figure()
            fig.add_trace(go.Scatter(x=timestamps, y=values, mode="lines+markers"))
            fig.update_layout(
                title=f"Évolution de {selected_feature} dans le temps",
                xaxis_title="Temps",
                yaxis_title=selected_feature,
                template="plotly_white",
            )
        elif all(isinstance(v, list) for v in values):  # Line plot avec intervalle de confiance
            if all(v in [0, 1] for v in values[0]):
                # Plot la proportion de chaque classe
                proportions = [np.mean(v) for v in values]
                fig = go.Figure()
                fig.add_trace(go.Scatter(x=timestamps, y=proportions, fill="tozeroy", mode="lines+markers", fillcolor="LightSalmon"))
                fig.update_layout(
                    title=f"Proportion de chaque classe dans le temps",
                    xaxis_title="Temps",
                    yaxis_title="Proportion",
                    template="plotly_white",
                    shapes=[dict(type="rect", xref="paper", x0=0, x1=1, y0=0, y1=1, fillcolor="PaleTurquoise", layer="below", line_width=0)]
                )
            else:
                mean_values = [np.mean(v) for v in values]
                std_values = [np.std(v) for v in values]
                lower_bound = [m - s for m, s in zip(mean_values, std_values)]
                upper_bound = [m + s for m, s in zip(mean_values, std_values)]

                fig = go.Figure()
                fig.add_trace(go.Scatter(
                    x=timestamps, y=mean_values, mode="lines+markers", name="Moyenne"
                ))
                fig.add_trace(go.Scatter(
                    x=timestamps + timestamps[::-1],
                    y=upper_bound + lower_bound[::-1],
                    fill="toself",
                    fillcolor="rgba(0,100,250,0.2)",
                    line=dict(color="rgba(255,255,255,0)"),
                    name="Intervalle de confiance",
                    showlegend=True
                ))
                fig.update_layout(
                    title=f"Évolution de {selected_feature} avec intervalle de confiance",
                    xaxis_title="Temps",
                    yaxis_title=selected_feature,
                    template="plotly_white",
                )
        else:
            return jsonify({"error": "Format de feature non pris en charge."}), 400

    return jsonify(fig.to_json())

if __name__ == "__main__":
    app.run(debug=True)