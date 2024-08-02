"""
Equivalent Frame Method for Flat Slab with Traverse Beam : Interior Strip
"""

import re
import numpy as np

from absl import app, flags
from absl.flags import FLAGS

from efm_stiffness import Slab_Beam_Stiffness, Column_Stiffness, Torsion_Stiffness
from efm_moment import calculate_veMoment

flags.DEFINE_float("E", 2000000, "MPa")
flags.DEFINE_float("fc1", 25, "Concrete strength for slab and beam, MP")
flags.DEFINE_float("fc2", 35, "Concrete strength for column, MPa")

flags.DEFINE_float("bw", 0, "beam width , mm")
flags.DEFINE_float("h", 0, "beam depth , mm")
flags.DEFINE_float("t", 0, "slab thickness , mm")

flags.DEFINE_float("l2", 0, "span , mm")
flags.DEFINE_float("lc", 0, "story heigth, mm")

METHOD = {"1": "linear", "2": "nearest", "3": "cubic"}

from utils import to_numpy, get_valid_integer, get_valid_list_input


def frame_data():
    # Numbers of span
    N = get_valid_integer("How many span? : ")

    # Each span length, l1
    while True:
        try:
            span = get_valid_list_input(
                "Define array of spans(l1) in meters, ex 4 4 5: "
            )
            span = span * 1e3  # Convert to numpy array in mm

            if span.size == N:
                print(f"span = {span} mm")
                break
            else:
                print(
                    f"You need to define exactly {N} spans. You provided {span.size}. Try again."
                )
        except ValueError as e:
            print(f"Input error: {e}. Please try again.")
        except Exception as e:
            print(f"Unexpected error: {e}. Please try again.")

    # Column type Square, Rectangle, Circle
    column_type = []
    for i in range(0, N + 1):
        while True:
            c = input(f"Column type for  C{i + 1} s|c : ").upper()
            if c in ["S", "C"]:
                column_type.append(c)
                break
            else:
                print(f"Wrong type, Try again")

    # Column dimension c1A, c2A
    print(f"\nDefine column width and height for each : ")
    print(f"You have {N + 1} columns")

    columns = []
    # [array([400., 400.]), array([400., 400.]), array([400., 400.])]
    for i in range(0, N + 1):
        while True:
            c = input(
                f"Define dimension (c1 x c2) for column {i + 1} in cm, ex. 40 60: "
            )
            try:
                c = to_numpy(c) * 10  # convert to mm
                if c.size == 2:
                    columns.append(c)
                    break
                else:
                    print(
                        "Invalid input. Please enter exactly two dimensions separated by a space, e.g., '40 60'."
                    )
            except ValueError as e:
                print(f"Input error: {e}. Please enter valid numeric dimensions.")

    return N, span, columns, column_type


def factor():
    sb = Slab_Beam_Stiffness()
    cs = Column_Stiffness()
    ts = Torsion_Stiffness(FLAGS.fc2)

    N, span, columns, column_type = frame_data()

    while True:
        while True:
            m = input(
                f"\nInterpolate method = ?, 1 = linear, 2 = nearest, 3 = cubic : "
            )
            if m in ["1", "2", "3"]:
                method = METHOD[m]
                break
            else:
                print("Wrong!!, Provide Again! : ")

        # Slab-Beam Stiffness
        Ksb = []
        COF = []
        FEM = []
        for i in range(0, len(span)):
            print(f"\nStretch : { i + 1 }")
            l1 = span[i]
            # left column
            c1A = columns[i][0]
            c2A = columns[i][1]
            # right column
            c1B = columns[i + 1][0]
            c2B = columns[i + 1][1]

            ksb, cof, fem = sb.traverse_beam_interia(
                c1A, c1B, FLAGS.bw, FLAGS.h, FLAGS.t, l1, FLAGS.l2, FLAGS.fc1, method
            )

            Ksb.append(ksb)
            COF.append(cof)
            FEM.append(fem)

        ask = input(f"\nChange intepolation method? ,  Y|N : ").upper()
        if ask != "Y":
            break
        else:
            pass

    # Equivalent column
    print(
        "==================================================================================="
    )
    print("Equivalent Column Stiffness")
    print(
        "==================================================================================="
    )
    while True:
        while True:
            m = input(
                f"\nInterpolate method = ?, 1 = linear, 2 = nearest, 3 = cubic : "
            )
            if m in ["1", "2", "3"]:
                method = METHOD[m]
                break
            else:
                print("Wrong!!, Provide Again! : ")

        Kec = []
        for i in range(0, len(span) + 1):
            print(f"\nColumn : { i + 1 }")

            c1A = columns[i][0]
            c2A = columns[i][1]

            c = column_type[i]
            Ic = (
                (1 / 12) * c1A * pow(c2A, 3)
                if c == "S"
                else (1 / 64) * np.pi * pow(c1A, 4)
            )  # mm4

            Kc = cs.kc(FLAGS.h, FLAGS.lc, Ic, FLAGS.fc2, method)

            # First joint
            if i == 0:
                l1 = span[0] / 2
                Kt = ts.ext_beam(FLAGS.bw, FLAGS.h, FLAGS.t, c2A, l1, FLAGS.l2)
            # Last joint
            elif i == len(span):
                l1 = span[i - 1] / 2
                Kt = ts.ext_beam(FLAGS.bw, FLAGS.h, FLAGS.t, c2A, l1, FLAGS.l2)
            # Interior joint
            else:
                l1 = (span[i - 1] + span[i]) / 2
                Kt = ts.tee(FLAGS.bw, FLAGS.h, FLAGS.t, c2A, l1, FLAGS.l2)

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

            Ks_bc = Ksb[i + 1][0]  # Next Ks

            Kec_a = Kec[i]
            Kec_b = Kec[i + 1]

            DFL = Ks_ab / (Ks_ab + Kec_a)
            DFR = Ks_ba / (Ks_ba + Ks_bc + Kec_b)
            DF.append([DFL, DFR])

        # Last span
        elif i == len(span) - 1:
            Ks_yz = Ksb[i][0]
            Ks_zy = Ksb[i][1]

            Ks_yx = Ksb[i - 1][1]  # Previous Ks

            Kec_y = Kec[i]
            Kec_z = Kec[i + 1]

            DFL = Ks_yz / (Ks_yx + Ks_yz + Kec_y)
            DFR = Ks_zy / (Ks_zy + Kec_z)
            DF.append([DFL, DFR])

        # Middle span a- b-c -d
        else:
            Ks_bc = Ksb[i][0]
            Ks_cb = Ksb[i][1]

            Ks_ba = Ksb[i - 1][1]  # Previous Ks
            Ks_cd = Ksb[i + 1][0]  # Next Ks

            Kec_b = Kec[i]
            Kec_c = Kec[i + 1]

            DFL = Ks_bc / (Ks_ba + Ks_bc + Kec_b)
            DFR = Ks_cb / (Ks_cb + Ks_cd + Kec_c)
            DF.append([DFL, DFR])

    return N, DF, COF, FEM


## Call
def main(_argv):
    N, DF, COF, FEM_COEFF = factor()

    print(
        "==================================================================================="
    )
    print("Distribution Table")
    print(
        "==================================================================================="
    )
    # Iteration moment distribution table
    while True:
        N_values = int(input(f"\nHow many iteration time? 10 is max! : "))

        # Limit 10 times for iteration
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
            FEM = input(f"\nDefine array of FEM in kN-m, You have only {N} spans :")
            FEM = toNumpy(FEM)

            if FEM.size == N * 2:
                print(f"LOAD = {FEM} kN-m")
                break
            else:
                print(f"You have {N} span, Try again : ")
        except Exception as e:
            print("Badly input.Try again")

    # fem_values = [item for item in FEM for _ in range(2)]
    # for i in range(1, len(fem_values), 2):
    #     fem_values[i] *= -1

    FEM = np.array(FEM)

    moment = moment_coeff * FEM

    print(f"Moment Coeff. : {moment_coeff}")
    print(f"Fiexd End Moment. : {FEM} kN-m")
    print(f"veM@support : {moment} kN-m")


if __name__ == "__main__":
    app.run(main)

# --------------------------------------------------------------------
"""
How to used?
-Please see FLAGS definition for unit informations
-Make sure you are in the project directory run python in terminal(Mac) or command line(Windows)
-Run app  
    % python rc/efm_tb.py --bw=250 --h=500 --t=150 --l2=5000 --lc=3000 --fc1=25 --fc2=35
"""
