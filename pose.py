import matplotlib.pyplot as plt
import math
import numpy as np

def main():
  try:
    with open('energy', 'r') as file:
      energy_value = float(file.read().strip())
  except FileNotFoundError:
    print("FIle not found")
  except ValueError:
    print("Invalid float value")
  except Exception as e:
    print(f"An error occured: {e}")

  try:
    with open('runtime', 'r') as file:
      runtime_value = float(file.read().strip())
  except FileNotFoundError:
    print("FIle not found")
  except ValueError:
    print("Invalid int value")
  except Exception as e:
    print(f"An error occured: {e}")

  # poseMin values
  try:
    with open('poseEnvelopeMin/power', 'r') as file:
      pose_min_power = float(file.read().strip())
  except FileNotFoundError:
    print("FIle not found")
  except ValueError:
    print("Invalid float value")
  except Exception as e:
    print(f"An error occured: {e}")
  
  

  # poseMax values
  try:
    with open('poseEnvelopeMax/power', 'r') as file:
      pose_max_power = float(file.read().strip())
  except FileNotFoundError:
    print("FIle not found")
  except ValueError:
    print("Invalid float value")
  except Exception as e:
    print(f"An error occured: {e}")
  

  #Metric Calculation
  beta = 1.732 * 200
  
  EDD_metric = math.sqrt((energy_value**2) + ((1.732 * 200) * runtime_value)**2)

  power_value = energy_value / runtime_value

  EDD_max_runtime = math.sqrt((EDD_metric * EDD_metric) / ((pose_max_power**2) + ((1.732*200)**2)))
  EDD_max_energy = pose_max_power * EDD_max_runtime

  EDD_min_runtime = math.sqrt((EDD_metric * EDD_metric) / ((pose_min_power**2) + ((1.732*200)**2)))
  EDD_min_energy = pose_min_power * EDD_min_runtime

  EDD_curve_runtime = np.linspace(EDD_min_runtime,EDD_max_runtime, 100)
  EDD_curve_energy = np.sqrt((EDD_metric**2) - (((1.732*200) * EDD_curve_runtime)**2))

  #Pose Boundaries
  Point_B_runtime = EDD_max_runtime
  Point_B_energy = EDD_max_energy
  
  Point_E_runtime = EDD_min_runtime
  Point_E_energy = EDD_min_energy
  
  Point_D_runtime = runtime_value
  Point_D_energy = runtime_value * pose_min_power
  
  Point_C_runtime = (runtime_value) * math.sqrt((pose_min_power**2 + (1.732*200)**2)/ (power_value**2 + (1.732*200)**2)) 
  Point_C_energy = pose_min_power * Point_C_runtime  

  #Metric Calculations
  EDD_metric_limit = math.sqrt((Point_C_energy**2) + ((1.732 * 200) * Point_C_runtime)**2)

  Point_A_runtime = math.sqrt((EDD_metric_limit * EDD_metric_limit) / ((pose_max_power**2) + ((1.732*200)**2)))
  Point_A_energy = pose_max_power * Point_A_runtime

  EDD_curve_runtime_limit = np.linspace(Point_C_runtime,Point_A_runtime, 100)
  EDD_curve_energy_limit = np.sqrt((EDD_metric_limit**2) - (((1.732*200) * EDD_curve_runtime_limit)**2))

  contr_runtime_curve = np.linspace(Point_C_runtime,runtime_value,100)
  contr_energy_curve = ((contr_runtime_curve / runtime_value)**2) * np.sqrt(energy_value**2 + (1.732*200)**2)
  contr_energy_curve = contr_runtime_curve * np.sqrt( ((power_value*contr_runtime_curve)/runtime_value)**2 + ( (beta*contr_runtime_curve)/runtime_value )**2 - (beta)**2)

  #Plot
#  plt.plot([0,pose_min_runtime],[0,pose_min_energy], label= "poseMin")
#  plt.plot([0,pose_max_runtime],[0,pose_max_energy], label= "poseMax")
  plt.plot([0,runtime_value],[0,energy_value],color='black', label= "EP")
  plt.plot(EDD_curve_runtime, EDD_curve_energy, label = "Optimisation Bound")
  plt.plot(EDD_curve_runtime_limit, EDD_curve_energy_limit, linestyle='--', label = "Optimisation Limit")
  plt.plot(contr_runtime_curve,contr_energy_curve, label = "Contribution Bound")
  plt.plot([Point_D_runtime,runtime_value], [Point_D_energy,energy_value], linestyle='--')  

  plt.text(Point_A_runtime,Point_A_energy, 'A', fontsize=12, color='black')
  plt.text(Point_B_runtime,Point_B_energy, 'B', fontsize=12, color='black')
  plt.text(Point_C_runtime,Point_C_energy, 'C', fontsize=12, color='black')
  plt.text(Point_D_runtime,Point_D_energy, 'D', fontsize=12, color='black')
  plt.text(Point_E_runtime,Point_E_energy, 'E', fontsize=12, color='black')
  plt.xlabel('Runtime')
  plt.ylabel('Energy')
  plt.title('POSE')
  plt.grid(False)
  plt.legend()

  #Set axes to intersect at (0,0)
  plt.axhline(0, color='black', linewidth=0.5) # X-axis
  plt.axvline(0, color='black', linewidth=0.5) # Y-axis
  plt.xlim(Point_A_runtime - 5, Point_B_runtime + 5) # start X-axis at 0
  plt.ylim(Point_C_energy - 1000, Point_B_energy + 1000) # start Y-axis at 0

  # Save the plot as a JPG file
  plt.savefig('pose.jpg', format='jpg', dpi=600)

  # time, energy and metric results
  print(f"Unoptmised code '\u03B8', optimisation bound metric: {EDD_metric:.4f}")
  print(f"Runtime at '\u03B8': {runtime_value:.4f}")
  print(f"Runtime at A: {Point_A_runtime:.4f}")
  print(f"Runtime at B: {Point_B_runtime:.4f}")
  print(f"Runtime at C: {Point_C_runtime:.4f}")
  print(f"Runtime at D: {Point_D_runtime:.4f}")
  print(f"Runtime at E: {Point_E_runtime:.4f}")

  print(f"Energy at '\u03B8': {energy_value:.4f}")
  print(f"Energy at A: {Point_A_energy:.4f}")
  print(f"Energy at B: {Point_B_energy:.4f}")
  print(f"Energy at C: {Point_C_energy:.4f}")
  print(f"Energy at D: {Point_D_energy:.4f}")
  print(f"Energy at E: {Point_E_energy:.4f}")
  

if __name__ == "__main__":
  main()
