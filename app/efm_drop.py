'''
Equivalent Frame Method for Flat Slab with Drop Panel
'''

import re
import numpy as np

from absl import app, flags
from absl.flags import FLAGS

from efm_stiffness import Slab_Beam_Stiffness, Column_Stiffness, Torsion_Stiffness
from efm_moment import calculate_veMoment

flags.DEFINE_float("E", 2000000, "MPa")
flags.DEFINE_float("fc1", 25, "Concrete strength for slab and beam, MP")
flags.DEFINE_float("fc2", 35, "Concrete strength for column, MPa")

flags.DEFINE_float("t", 0, "slab thickness , mm")
flags.DEFINE_float("td", 0, "drop thickness , mm")

flags.DEFINE_float("l2", 0, "strip width , mm")
flags.DEFINE_float("lc", 0, "story heigth, mm")


METHOD = {
    '1' : 'linear',
    '2' : 'nearest',
    '3' : 'cubic'
}


def toNumpy(x):
    x = re.findall(r"[-+]?(?:\d*\.\d+|\d+)", x)
    return np.array([float(n) for n in x])


def frame_data():
    print("===================================================================================")
    print("Equivalent Frame Method, EFM")
    print("===================================================================================")

    # Number span 
    N = int(input("How many span? : "))  # TODO error raise if not digit

    # Span length, l1
    while True:
        try:
            span = input(f"Define array of spans in meters : ")
            span = toNumpy(span) * 1e3 # mm

            if span.size == N:
                print(f"span = {span} mm")
                break
            else:
                print(f"You have {N} span, Try again")
        except Exception as e:
            print("Badly input.Try again")


    # Column type Square, Rectangle, Circle
    column_type = []
    for i in range(0, N + 1):
        while True:
            c = input(f"Column type , S = rectangle/Square, C = Circle,  C{i + 1} = S or C : ").upper()
            if c in ["S", "C"]:
                column_type.append(c)
                break
            else:
                print(f"Wrong type, Try again")

   
    # Column dimension c1A, c2A
    print(f"\nDefine column width and height for each : ")
    print(f"You have {N + 1} columns")

    columns = []
    for i in range(0, N + 1):
        while True:
            c = input(f"Define dimension (w, h) for column {i + 1} in mm : ")
            c = toNumpy(c)
            if c.size == 2:
                columns.append(c)
                break
            else:
                print(f"Wrong dimension!, Try again")


    # Drop dimension dp1A, dp2A
    print(f"\nDefine drop panel width and height for each : ")
    print(f"You have {N + 1} columns")

    drop = []
    for i in range(0, N + 1):
        while True:
            c = input(f"Define dimension (w, h) for drop panel {i + 1} in mm : ")
            c = toNumpy(c)
            if c.size == 2:
                drop.append(c)
                break
            else:
                print(f"Wrong dimension!, Try again")

    return N, span, columns, drop, column_type


def factor():
    sb = Slab_Beam_Stiffness()
    cs = Column_Stiffness()
    ts = Torsion_Stiffness(FLAGS.fc1)

    N, span, columns, drop, column_type = frame_data()

    # Slab-Beam Stiffness
    print("===================================================================================")
    print("Slab-Beam Stiffness")
    print("===================================================================================")
    while True:
        while True:
            m = input(f"\nInterpolate method = ?, 1 = linear, 2 = nearest, 3 = cubic : ")
            if m in ['1', '2', '3']:
                method = METHOD[m]
                break
            else:
                print("Wrong!!, Provide Again! : ")

        Ksb = []
        COF = []
        FEM_COEFF = []
        for i in range(0, len(span)):
            print(f"\nStretch : { i + 1 }")
            l1 = span[i]

            # left drop
            dp1A = drop[i][0]
            dp2A = drop[i][1]
            # right drop
            dp1B = drop[i + 1][0]
            dp2B = drop[i + 1][1]

            ksb, cof, fem_coeff = sb.drop_panel(dp1A, dp1B, FLAGS.l2, FLAGS.t, l1, FLAGS.fc1, method)
            Ksb.append(ksb)
            COF.append(cof)
            FEM_COEFF.append(fem_coeff)

        ask = input(f"\nChange intepolation method? ,  Y|N : ").upper()
        if ask != "Y":
            break
        else:
            pass


    # Equivalent column
    print("===================================================================================")
    print("Equivalent Column Stiffness")
    print("===================================================================================")   
    while True: 
        while True:
            m = input(f"\nInterpolate method = ?, 1 = linear, 2 = nearest, 3 = cubic : ")
            if m in ['1', '2', '3']:
                method = METHOD[m]
                break
            else:
                print("Wrong!!, Provide Again! : ")

        Kec = []
        for i in range(0, len(span) + 1):
            print(f"\nColumn : { i + 1 }")
            c1A = columns[i][0]
            c2A = columns[i][1]

            dp1A = drop[i][0]
            dp2A = drop[i][1]

            c = column_type[i]
            Ic =  (1 / 12) * c1A * pow(c2A, 3) if c == 'S' else (1 / 64) * np.pi * pow(c1A, 4) # mm4

            Kc = cs.kc(FLAGS.td, FLAGS.lc, Ic, FLAGS.fc2)
            Kt = ts.drop_panel(dp1A, dp2A, FLAGS.td, FLAGS.l2)

            kec = 1 / ((1 / sum(Kc)) + (1 / (2 * Kt)))
            Kec.append(kec)

            print(f"Kec = {kec:.2e} N-mm")

        ask = input(f"\nChange intepolation method? ,  Y|N : ").upper()
        if ask != "Y":
            break
        else:
            pass



    # # Distribution factor, DF
    DF = []
    for i in range(0, len(span)): 

        # First span
        if i == 0:
            Ks_ab = Ksb[i][0]
            Ks_ba = Ksb[i][1]

            Ks_bc = Ksb[i + 1][0] # Next Ks
            
            Kec_a = Kec[i]
            Kec_b = Kec[i + 1]

            DFL = Ks_ab / (Ks_ab + Kec_a)
            DFR = Ks_ba / (Ks_ba + Ks_bc + Kec_b)
            DF.append([DFL, DFR])

        # Last span 
        elif i == len(span) - 1:
            Ks_yz = Ksb[i][0]
            Ks_zy = Ksb[i][1]

            Ks_yx = Ksb[i - 1][1] # Previous Ks

            Kec_y = Kec[i]
            Kec_z = Kec[i + 1]

            DFL = Ks_yz / (Ks_yx + Ks_yz + Kec_y)
            DFR = Ks_zy / (Ks_zy + Kec_z)
            DF.append([DFL, DFR])

        # Middle span a- b-c -d
        else:
            Ks_bc = Ksb[i][0]
            Ks_cb = Ksb[i][1]

            Ks_ba = Ksb[i - 1][1] # Previous Ks
            Ks_cd = Ksb[i + 1][0] # Next Ks
            
            Kec_b = Kec[i]
            Kec_c = Kec[i + 1]

            DFL = Ks_bc / (Ks_ba + Ks_bc + Kec_b)
            DFR = Ks_cb / (Ks_cb + Ks_cd + Kec_c)
            DF.append([DFL, DFR])

    return N, DF, COF, FEM_COEFF


##Call
def main(_argv):
    N, DF, COF, FEM_COEFF = factor()

    print("===================================================================================")
    print("Distribution Table")
    print("===================================================================================")
    # Iteration moment distribution table
    while True:
        N_values = int(input(f"\nHow many iteration time? 10 is max! : "))
        N_values = 10 if N_values > 10 else N_values

        moment_coeff = np.array(calculate_veMoment(N, DF, COF, FEM_COEFF, N_values))

        ask = input("Iterated Again Y|N : ").upper()
        if ask == "Y":
            pass
        else:
            break

    # FEM
    while True:
        try:
            FEM = input(f"\nDefine array of FEM in kN-m, You have only {N} spans : ")
            FEM = toNumpy(FEM)

            if FEM.size == N * 2:
                print(f"FEM = {FEM} kN-m")
                break
            else:
                print(f"You have {N} span, Try again : ")
        except Exception as e:
            print("Badly input.Try again")


    FEM = np.array(FEM)

    moment = moment_coeff * FEM

    print(f"Moment Coeff. : {moment_coeff}")
    print(f"Fiexd End Moment. : {FEM} kN-m")
    print(f"veM@support : {moment} kN-m")

          
if __name__ == "__main__":
    app.run(main)

# FEM_values = [  162.1, 72.7, 162.1  ]
# --------------------------------------------------------------------
"""
How to used?
-Please see FLAGS definition for unit informations
-Make sure you are in the project directory run python in terminal(Mac) or command line(Windows)
-Run app  
    % python rc/efm_drop.py --t=180 --td=775 --l2=6000 --lc=3000  --fc1=25
"""