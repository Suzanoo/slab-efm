"""
Equivalent Frame Method for Flat Slab with Drop Panel
"""

import numpy as np

from absl import app, flags
from absl.flags import FLAGS

from efm_stiffness import Slab_Beam_Stiffness, Column_Stiffness, Torsion_Stiffness
from efm_moment import (
    calculate_fixend_moment,
    calculate_moment_at_support,
    efm_table,
    calculate_design_moments,
)

from utils import (
    to_numpy,
    add_sign,
    get_valid_integer,
    get_valid_number,
    get_valid_list_input,
)

from design_reinf import Design
from punching_shear import punching

# Flags defination
flags.DEFINE_float("E", 2000000, "MPa")
flags.DEFINE_float("fc1", 25, "Concrete strength for slab and beam, MP")
flags.DEFINE_float("fc2", 35, "Concrete strength for column, MPa")
flags.DEFINE_float("fy", 390, "Yeild strength for main reinforcement, MPa")
flags.DEFINE_float("fv", 235, "Yeild strength for traverse , MPa")
flags.DEFINE_float("c", 2.5, "Concrete covering , cm")

flags.DEFINE_float("t", 0, "slab thickness , mm")
flags.DEFINE_float("td", 0, "drop thickness , mm")

flags.DEFINE_float("l2", 0, "strip width , mm")
flags.DEFINE_float("lc", 0, "story heigth, mm")

flags.DEFINE_string("type", "int", "Interior or Exterior beam")

np.set_printoptions(precision=3)

METHOD = {"1": "linear", "2": "nearest", "3": "cubic"}


def frame_data():
    # Number of span
    N = get_valid_integer("How many span? : ")

    # l1 (span length)
    while True:
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
        ask = input("Try again! Y|N : ").upper()
        if ask == "Y":
            pass
        else:
            break

    # Column Type
    print(f"\nColumn Type Definition S = Square or Rectangle, C = Circle")

    # Column type Square, Rectangle, Circle
    column_type = []
    while True:
        for i in range(0, N + 1):
            while True:
                c = input(f"Column type for  C{i + 1} s|c : ").upper()
                if c in ["S", "C"]:
                    column_type.append(c)
                    break
                else:
                    print(f"Wrong type, Try again")

        ask = input("Try again! Y|N : ").upper()
        if ask == "Y":
            column_type = []
        else:
            break

    # Column dimension c1A, c2A
    print(f"\nColumn dimension represented by c1A x c1B")
    print("c1A is the dimension parallel to l1 (width).")
    print("c1B is the dimension perpendicular to l1")
    print(f"You have {N + 1} columns.")

    columns = []
    # [array([400., 400.]), array([400., 400.]), array([400., 400.])]
    while True:
        for i in range(0, N + 1):
            while True:
                c = input(
                    f"Define dimension (c1A x c1B) for column {i + 1} in cm, ex. 40 60: "
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

        ask = input("Try again! Y|N : ").upper()
        if ask == "Y":
            columns = []
        else:
            break

    # Drop dimension dp1A, dp2A
    print(f"\nDrop panel dimension represented by c1A x c1B")
    print("c1A is the dimension parallel to l1 (width).")
    print("c1B is the dimension perpendicular to l1")
    print(f"You have {N + 1} drops.")

    drops = []
    while True:
        for i in range(0, N + 1):
            while True:
                c = input(
                    f"Define drop panel dimension (c1A x c1B) for column {i + 1} in cm, ex. 100 100: "
                )
                try:
                    c = to_numpy(c) * 10  # convert to mm
                    if c.size == 2:
                        drops.append(c)
                        break
                    else:
                        print(
                            "Invalid input. Please enter exactly two dimensions separated by a space, e.g., '40 60'."
                        )
                except ValueError as e:
                    print(f"Input error: {e}. Please enter valid numeric dimensions.")

        ask = input("Try again! Y|N : ").upper()
        if ask == "Y":
            drops = []
        else:
            break

    # Drop dimension dp1A, dp2A
    print(f"\nDefine drop panel width and height for each : ")
    print(f"You have {N + 1} columns")

    return N, span, columns, drops, column_type


def factor(span, columns, drops, column_type):
    sb = Slab_Beam_Stiffness()
    cs = Column_Stiffness()
    ts = Torsion_Stiffness(FLAGS.fc1)

    # Slab-Beam Stiffness
    # Slab-Beam Stiffness
    print(f"\n==========Slab-Beam Stiffness Interpolation==========")
    while True:
        while True:
            m = input(f"Interpolate method = ?, 1 = linear, 2 = nearest, 3 = cubic : ")
            if m in ["1", "2", "3"]:
                method = METHOD[m]
                break
            else:
                print("Valid 1, 2, or 3 only, Try Again! : ")

        Ksb = []
        COF = []
        FEM_COEFF = []
        for i in range(0, len(span)):
            print(f"\nStretch : { i + 1 }")
            l1 = span[i]

            # left drop
            dp1A = drops[i][0]
            dp2A = drops[i][1]
            # right drops
            dp1B = drops[i + 1][0]
            dp2B = drops[i + 1][1]

            if type == "int":
                ksb, cof, fem_coeff = sb.drop_panel(
                    dp1A, dp1B, FLAGS.l2, FLAGS.t, l1, FLAGS.fc1, method
                )
            else:
                ksb, cof, fem_coeff = sb.drop_panel(
                    dp1A, dp1B, FLAGS.l2 / 2, FLAGS.t, l1, FLAGS.fc1, method
                )
            Ksb.append(ksb)
            COF.append(cof)
            FEM_COEFF.append(fem_coeff)

        ask = input(f"\nChange intepolation method? ,  Y|N : ").upper()
        if ask != "Y":
            break
        else:
            pass

    # Equivalent column
    print(f"\n==========Equivalent Column Stiffness Interpolation==========")
    while True:
        while True:
            m = input("Interpolate method = ?, 1 = linear, 2 = nearest, 3 = cubic : ")
            if m in ["1", "2", "3"]:
                method = METHOD[m]
                break
            else:
                print("Valid 1, 2, or 3 only, Try Again! : ")

        Kec = []
        for i in range(0, len(span) + 1):
            print(f"\nColumn : { i + 1 }")
            c1A = columns[i][0]
            c2A = columns[i][1]

            dp1A = drops[i][0]
            dp2A = drops[i][1]

            c = column_type[i]
            Ic = (
                (1 / 12) * c1A * pow(c2A, 3)
                if c == "S"
                else (1 / 64) * np.pi * pow(c1A, 4)
            )  # mm4

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

    return DF, COF, FEM_COEFF


##Call
def main(_argv):
    print(
        "======================== Equivalent Frame Method, EFM ========================"
    )
    print(f"\n[INFO], Flat slab design use EFM method]")
    print("See EFM_Method.pdf for more information :")

    print(f"\n-Give information :")
    print("-Interpolate slab-beam stiffness from table :")
    print("-Interpolate column stiffness from table :")
    print("-Calculate negative moment at support, M-  :")
    print("-Calculate possitive moment, M+, :")
    print("-Calculate Shear at support :")
    print("-Calculate M and V at column face :")

    ##
    print(f"\n==========Information==========")
    N, span, columns, drops, column_type = frame_data()

    # Get coefficients
    DF, COF, FEM_COEFF = factor(span, columns, drops, column_type)

    print(f"\n==========EFM Table==========")
    # Define area load
    qu = get_valid_number("Define qu(1.4DL+ 1.7LL) , kN/m2 : ")

    # Calculate Fixedd End Moment
    fem = []
    for i in range(len(span)):
        m = calculate_fixend_moment(qu, span[i] * 1e-3, FLAGS.l2 * 1e-3)
        fem.append(m)

    fem = add_sign(
        np.array(fem)
    )  # ex. convert np.array([100, 50]) to np.array([100 -100 50 -50])

    # Calculate moment at support
    print(
        f"\n[INFO] Next is moment distribution iteration. Distribute util all carry over moment = 0"
    )
    while True:
        N_values = get_valid_integer("How many iteration time? 15 is max! : ")

        # Limit 15 times for iteration
        num_iter = 15 if N_values > 15 else N_values

        df = calculate_moment_at_support(N, DF, COF, FEM_COEFF, fem, num_iter)

        ask = input("Iterated Again Y|N : ").upper()
        if ask == "Y":
            pass
        else:
            break

    # Generate EFM table
    df, poss_moment_df = efm_table(
        N,
        [
            c * 1e-3 for c in columns
        ],  # Convert columns to meters by multiplying with 1e-3
        span * 1e-3,
        FLAGS.l2 * 1e-3,
        qu,  # kN/m2
        df,
    )

    calculate_design_moments(df, poss_moment_df)

    # Design reinforcement
    print(f"\n==========Design Reinforcement==========")
    ask = input("Do you want to design reinforcement? Y|N : ").upper()
    if ask == "Y":
        print("M- for drop panel, M+ for slab design : ")
        drop_width = get_valid_number("Drop width in cm ? : ")

        design = Design(FLAGS.fc1, FLAGS.fv, FLAGS.fy, FLAGS.c)

        print("Design drop panel")
        design.design_drop(drop_width, FLAGS.td * 1e-1)

        print("Design slab")
        design.design_slab(FLAGS.l2 * 1e-1, FLAGS.t * 1e-1)

    # Check punching shear
    ask = input(f"\nDo you want to check punching sheart? Y|N : ").upper()
    if ask == "Y":
        punching(FLAGS.fc1)

    print("======================== ********** ========================")


if __name__ == "__main__":
    app.run(main)

# FEM_values = [  162.1, 72.7, 162.1  ]
# --------------------------------------------------------------------
"""
    % python app/efm_drop.py --t=180 --td=775 --l2=6000 --lc=3000  --fc1=25
    % python app/efm_drop.py --t=240 --td=500 --l2=3000 --lc=2750 --fc1=35 --fc2=35
"""
