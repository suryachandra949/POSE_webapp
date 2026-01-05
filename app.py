from flask import Flask, render_template, request, jsonify
import pandas as pd
import json
import math
import numpy as np

app = Flask(__name__)

points_df = pd.read_csv("points_LU.csv")



def compute_intersections(point, pmin, pmax):
    """
    point = {"runtime": float, "energy": float}
    pmin, pmax = floats

    RETURN:
    [
        {"x": float, "y": float, "label": str},
        ...
    ]
    """

    # ---- YOUR EXISTING CODE GOES HERE ----


    #Metric Calculation
    beta = 1.732 * 200

    energy_value = point["energy"] 
    runtime_value = point["runtime"]
    power_value = energy_value / runtime_value

    EDD_metric = math.sqrt((energy_value**2) + ((1.732 * 200) * runtime_value)**2)

    EDD_max_runtime = math.sqrt((EDD_metric * EDD_metric) / ((pmax**2) + ((1.732*200)**2)))
    EDD_max_energy = pmax * EDD_max_runtime

    EDD_min_runtime = math.sqrt((EDD_metric * EDD_metric) / ((pmin**2) + ((1.732*200)**2)))
    EDD_min_energy = pmin * EDD_min_runtime

    Point_D_runtime = runtime_value
    Point_D_energy = runtime_value * pmin

    Point_C_runtime = (runtime_value) * math.sqrt((pmin**2 + (1.732*200)**2)/ (power_value**2 + (1.732*200)**2)) 
    Point_C_energy = pmin * Point_C_runtime

    #Metric Calculations
    EDD_metric_limit = math.sqrt((Point_C_energy**2) + ((1.732 * 200) * Point_C_runtime)**2)

    Point_A_runtime = math.sqrt((EDD_metric_limit * EDD_metric_limit) / ((pmax**2) + ((1.732*200)**2)))
    Point_A_energy = pmax * Point_A_runtime 


    intersections = []


    intersections.append({
        "x": EDD_max_runtime,
        "y": EDD_max_energy,
        "label": "B",
        "line": "pmax"
    })

    intersections.append({
        "x": EDD_min_runtime,
        "y": EDD_min_energy,
        "label": "E",
        "line": "pmin"
    })

    intersections.append({
        "x": Point_A_runtime,
        "y": Point_A_energy,
        "label": "A",
        "line": "pmax"
    })

    intersections.append({
        "x": Point_C_runtime,
        "y": Point_C_energy,
        "label": "C",
        "line": "pmin"
    })

    intersections.append({
        "x": Point_D_runtime,
        "y": Point_D_energy,
        "label": "D",
        "line": "pmin"
    })

    return intersections,EDD_metric,EDD_metric_limit,runtime_value,energy_value



@app.route("/")
def index():
    return render_template(
        "index.html",
        points=points_df.to_dict(orient="records"),
        power_sets=json.dumps({
            "case1": pd.read_csv("power_LU.csv").set_index("name")["m"].to_dict(),
            "case2": pd.read_csv("power_LU_AI.csv").set_index("name")["m"].to_dict(),
            "case3": pd.read_csv("power_LU.csv").set_index("name")["m"].to_dict(),
        })
    )



@app.route("/compute", methods=["POST"])
def compute():
    data = request.json

    point = data["point"]
    pmin = data["pmin"]
    pmax = data["pmax"]

    intersections,EDD_metric,EDD_metric_limit,code_runtime,code_energy = compute_intersections(point, pmin, pmax)

    #metrics list
    B = []
    A = []
    C = []
    E = []
    # Extract intersection energies
    e_edd_vals =[]
    e_limit_vals =[]
    D_line_runtime=[]
    D_line_energy=[]
    D_line_energy.append(code_energy)
    D_line_runtime.append(code_runtime)
    power_value = code_energy/code_runtime
    for pt in intersections:
        if pt["label"] == "B" or pt["label"] == "E":
            e_edd_vals.append(pt["y"])
            if pt["label"] == "B":
                B.append(pt["x"])
                B.append(pt["y"])
            else:
                E.append(pt["x"])
                E.append(pt["y"])
        elif pt["label"] == "A" or  pt["label"] == "C":
            e_limit_vals.append(pt["y"])
            if pt["label"] == "C":
                Point_C_runtime = pt["x"]
                C.append(pt["x"])
                C.append(pt["y"])
            else:
                A.append(pt["x"])
                A.append(pt["y"])
        elif pt["label"] == "D":
            D_line_runtime.append(pt["x"])
            D_line_energy.append(pt["y"])

    # Convert to parametric angles
    beta = 1.732 * 200
    theta_min = math.asin(min(e_edd_vals) / EDD_metric)
    theta_max = math.asin(max(e_edd_vals) / EDD_metric)

    theta = np.linspace(theta_min, theta_max, 200)

    edd_runtime = (EDD_metric / beta) * np.cos(theta)
    edd_energy = EDD_metric * np.sin(theta)

    # EDD limit curve
    theta_max_limit = math.asin(max(e_limit_vals) / EDD_metric_limit)
    theta_min_limit = math.asin(min(e_limit_vals) / EDD_metric_limit)

    theta = np.linspace(theta_min, theta_max, 200)
    theta_limit = np.linspace(theta_min_limit, theta_max_limit, 200)

    edd_runtime = (EDD_metric / beta) * np.cos(theta)
    edd_energy = EDD_metric * np.sin(theta)

    edd_runtime_limit = (EDD_metric_limit / beta) * np.cos(theta_limit)
    edd_energy_limit = EDD_metric_limit * np.sin(theta_limit)

    # C_line curve
    C_line_runtime = np.linspace(Point_C_runtime,code_runtime,200)
    C_line_energy = C_line_runtime * np.sqrt( ((power_value*C_line_runtime)/code_runtime)**2 + ( (beta*C_line_runtime)/code_runtime )**2 - (beta)**2)


    return jsonify({
        "intersections": intersections,
        "edd_curve": {
            "runtime": edd_runtime.tolist(),
            "energy": edd_energy.tolist()
        },
        "edd_curve_limit": {
            "runtime": edd_runtime_limit.tolist(),
            "energy": edd_energy_limit.tolist()
        },
        "D_line":{
            "runtime": D_line_runtime,
            "energy": D_line_energy
        },

        "C_line":{
            "runtime": C_line_runtime.tolist(),
            "energy": C_line_energy.tolist()
        },
        "metrics":{
            "point_metrics": [
            {
                "label": "θ",
                "runtime": code_runtime,
                "energy": code_energy
            },
            {
                "label": "A",
                "runtime": A[0],
                "energy": A[1]
            },
            {
                "label": "B",
                "runtime": B[0],
                "energy": B[1]
            },
            {
                "label": "C",
                "runtime": C[0],
                "energy": C[1]
            },
            {
                "label": "D",
                "runtime": D_line_runtime[1],
                "energy": D_line_energy[1]
            },
            {
                "label": "E",
                "runtime": E[0],
                "energy": E[1]
            }
        ],
        "derived_metrics": [
            {
                "name":"Best Case Energy Saved by Reducing Power Consumption",
                "Absolute": code_energy - E[1],
                "value_unit":"J",
                "Relative": code_energy/E[1]
            },
            {
                "name": "Worst Case Slowdown as a result of Power Optimisation",
                "Absolute": E[0] - code_runtime,
                "value_unit":"s",
                "Relative": E[0]/code_runtime            
            },
            {
                "name": "Best Case Improvement in EDD metric from Power Optimisation",
                "Absolute": (EDD_metric - EDD_metric_limit)/100,
                "value_unit":"%",
                "Relative": EDD_metric/EDD_metric_limit            
            },
            {
                "name": "Minimum Speed Up Guaranteed to Outperform θ",
                "Absolute": code_runtime - B[0],
                "value_unit":"s",
                "Relative": code_runtime/B[0]             
            },
            {
                "name": "Speed Up Required to Dominate Power Optimisation",
                "Absolute": code_runtime - A[0],
                "value_unit":"s",
                "Relative": code_runtime/A[0]             
            }

        ]
        }
    })

if __name__ == "__main__":
    app.run(debug=True)
