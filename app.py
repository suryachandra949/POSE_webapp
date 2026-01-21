from flask import Flask, render_template, request, jsonify
import pandas as pd
import json
import math
import numpy as np

app = Flask(__name__)


DATASETS = {
    "MG": {
        "points": "data/points_MG.csv",
        "cases": {
            "case1": "data/power_MG.csv",
            "case2": "data/power_MG_AI.csv",
            "case3": "data/power_MG_analysis.csv",
        }
    },
    "FFT": {
        "points": "data/points_FT.csv",
        "cases": {
            "case1": "data/power_FT.csv",
            "case2": "data/power_FT_AI.csv",
            "case3": "data/power_FT_adapt.csv",
        }
    },
    "CG": {
        "points": "data/points_CG.csv",
        "cases": {
            "case1": "data/power_CG.csv",
            "case2": "data/power_CG_AI.csv",
            "case3": "data/power_CG_analysis.csv",
        }
    },
    "LU": {
        "points": "data/points_LU.csv",
        "cases": {
            "case1": "data/power_LU.csv",
            "case2": "data/power_LU_AI.csv",
            "case3": "data/power_LU_AI.csv",
        }
    },
    "BT": {
        "points": "data/points_BT.csv",
        "cases": {
            "case1": "data/power_BT.csv",
            "case2": "data/power_BT_AI.csv",
            "case3": "data/power_BT_analysis.csv",
        }
    },
    "EP": {
        "points": "data/points_EP.csv",
        "cases": {
            "case1": "data/power_EP.csv",
            "case2": "data/power_EP_AI.csv",
            "case3": "data/power_EP_analysis.csv",
        }
    },
    "SP": {
        "points": "data/points_SP.csv",
        "cases": {
            "case1": "data/power_SP.csv",
            "case2": "data/power_SP_AI.csv",
            "case3": "data/power_SP_analysis.csv",
        }
    },
    "HACC": {
        "points": "data/points_HACC.csv",
        "cases": {
            "case1": "data/power_HACC.csv",
            "case2": "data/power_HACC_AI.csv",
            "case3": "data/power_HACC_analysis.csv",
        }
    }

}

def plotCurves(metric,code_energy,code_runtime,power_value,alpha,beta,A,B,C,E,n):
    
    if metric == "EDS": 
        # Curves
        edd_runtime = np.linspace(B[0],E[0],200)
        edd_energy = code_energy + ((beta/alpha)*code_runtime) - ((beta/alpha)*edd_runtime)

        # EDD limit curve
        edd_runtime_limit = np.linspace(A[0],C[0],200)
        edd_energy_limit = C[1] + ((beta/alpha)*C[0]) - ((beta/alpha)*edd_runtime_limit)


        # C_line curve
        C_line_runtime = np.linspace(C[0],code_runtime,200)
        C_line_energy = ((C_line_runtime**2)/code_runtime) *  (power_value +  beta/alpha) - (C_line_runtime * (beta/alpha))
    
    elif metric == "EDD":
        # Curves

        edd_runtime = np.linspace(B[0],E[0],200)
        edd_energy = np.sqrt((code_energy)**2 + ((beta/alpha)*code_runtime)**2 - ((beta/alpha)*edd_runtime)**2)

        # EDD limit curve
        edd_runtime_limit = np.linspace(A[0],C[0],200)
        edd_energy_limit = np.sqrt((C[1])**2 + ((beta/alpha)*C[0])**2 - ((beta/alpha)*edd_runtime_limit)**2)


        # C_line curve
        C_line_runtime = np.linspace(C[0],code_runtime,200)
        C_line_energy = C_line_runtime * np.sqrt( ((power_value*C_line_runtime)/code_runtime)**2 + ( (beta*C_line_runtime)/(alpha*code_runtime) )**2 - (beta/alpha)**2)

    elif metric == "EDP":
        # Curves

        edd_runtime = np.linspace(B[0],E[0],200)
        edd_energy = code_energy * np.power((code_runtime/edd_runtime),n)

        # EDD limit curve
        edd_runtime_limit = np.linspace(A[0],C[0],200)
        edd_energy_limit = C[1] * np.power((C[0]/edd_runtime_limit),n)


        # C_line curve
        C_line_runtime = np.linspace(C[0],code_runtime,200)
        C_line_energy = (power_value * C_line_runtime)* np.power((C_line_runtime/code_runtime),n+1)

    return edd_runtime,edd_energy,edd_runtime_limit,edd_energy_limit,C_line_runtime,C_line_energy




def compute_intersections(point, pmin, pmax, alpha, beta, metric,n):

    #Metric Calculation

    energy_value = point["energy"] 
    runtime_value = point["runtime"]
    power_value = energy_value / runtime_value

    if metric == "EDD":

      EDD_metric = math.sqrt(((alpha*energy_value)**2) + ((beta) * runtime_value)**2)

      EDD_max_runtime = math.sqrt((EDD_metric * EDD_metric) / (((alpha*pmax)**2) + ((beta)**2)))
      EDD_max_energy = pmax * EDD_max_runtime

      EDD_min_runtime = math.sqrt((EDD_metric * EDD_metric) / (((alpha*pmin)**2) + ((beta)**2)))
      EDD_min_energy = pmin * EDD_min_runtime

      Point_D_runtime = runtime_value
      Point_D_energy = runtime_value * pmin
 
      Point_C_runtime = runtime_value * math.sqrt(((alpha*pmin)**2 + beta**2)/(((alpha*power_value)**2 + beta**2)))
      Point_C_energy = pmin * Point_C_runtime

      #Metric Calculations
      EDD_metric_limit = math.sqrt((alpha*Point_C_energy)**2 + (beta * Point_C_runtime)**2)

      Point_A_runtime = math.sqrt((EDD_metric_limit * EDD_metric_limit) / (((alpha*pmax)**2) + (beta**2)))
      Point_A_energy = pmax * Point_A_runtime 

    elif metric == "EDS":

      EDD_metric = (alpha*energy_value) + ((beta) * runtime_value)

      EDD_max_runtime = ((EDD_metric)/ ((alpha*pmax) + beta))
      EDD_max_energy = pmax * EDD_max_runtime

      EDD_min_runtime = ((EDD_metric) / ((alpha*pmin) + beta))
      EDD_min_energy = pmin * EDD_min_runtime

      Point_D_runtime = runtime_value
      Point_D_energy = runtime_value * pmin
 
      Point_C_runtime = runtime_value * (((alpha*pmin) + beta)/((alpha*power_value) + beta))
      Point_C_energy = pmin * Point_C_runtime

      #Metric Calculations
      EDD_metric_limit = ((alpha*Point_C_energy) + (beta * Point_C_runtime))

      Point_A_runtime = ((EDD_metric_limit) / ((alpha*pmax) + beta))
      Point_A_energy = pmax * Point_A_runtime   

    elif metric == "EDP":

      EDD_metric = energy_value *  (runtime_value**n)

      EDD_max_runtime = (EDD_metric / pmax)**(1/(n+1))
      EDD_max_energy = pmax * EDD_max_runtime

      EDD_min_runtime =  (EDD_metric / pmin)**(1/(n+1))
      EDD_min_energy = pmin * EDD_min_runtime

      Point_D_runtime = runtime_value
      Point_D_energy = runtime_value * pmin
 
      Point_C_runtime = runtime_value *((pmin/power_value) ** (1/(n+1)))
      Point_C_energy = pmin * Point_C_runtime

      #Metric Calculations
      EDD_metric_limit = (Point_C_energy) * (Point_C_runtime**n)

      Point_A_runtime = (EDD_metric_limit / pmax)**(1/(n+1))
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



def load_power_sets(cfg):
    power_sets = {}
    for case, path in cfg["cases"].items():
        df = pd.read_csv(path)
        if "role" not in df.columns:
            df["role"] = "other"
        power_sets[case] = {
            "slopes": df.set_index("name")["m"].to_dict(),
            "roles": df.set_index("name")["role"].to_dict(),
        }
    return power_sets



@app.route("/load_dataset/<name>")
def load_dataset(name):
    if name not in DATASETS:
        return jsonify({"error": "unknown dataset"}), 400

    cfg = DATASETS[name]

    points = pd.read_csv(cfg["points"]).to_dict(orient="records")

    power_sets = load_power_sets(cfg)

    return jsonify({
        "points": points,
        "power_sets": power_sets
    })

@app.route("/")
def index():
    # load default dataset (MG) to render the page
    cfg = DATASETS["MG"]
    points = pd.read_csv(cfg["points"]).to_dict(orient="records")
    power_sets = load_power_sets(cfg)

    return render_template("index.html", points=points, power_sets=power_sets)




@app.route("/compute", methods=["POST"])
def compute():
    data = request.json

    point = data["point"]
    pmin = data["pmin"]
    pmax = data["pmax"]
    alpha = float(data["alpha"])
    beta = float(data["beta"])
    n = float(data.get("n")) 
    metric = data["option"]



    intersections,EDD_metric,EDD_metric_limit,code_runtime,code_energy = compute_intersections(point, pmin, pmax,alpha,beta,metric,n)

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

    edd_runtime,edd_energy,edd_runtime_limit,edd_energy_limit,C_line_runtime,C_line_energy = plotCurves(metric,code_energy,code_runtime,power_value,alpha,beta,A,B,C,E,n)


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
            },
            {
                "label": metric,
                "runtime": EDD_metric,
                "energy": EDD_metric_limit
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
