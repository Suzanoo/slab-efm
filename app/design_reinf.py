import os
import numpy as np
import pandas as pd

from beam_class import Beam

from utils_df import display_df


# ----------------------------------
def design_reinf(fc, fy, fv, b, t, c):
    """
    fc, fv in MPa
    b: width in cm
    t: thickness in cm
    c: covering in cm
    """
    CURRENT = os.getcwd()

    print(f"\nGEOMETRY")
    print(f"Column strip = {b/2} cm, thickness = {t} cm,")
    print(f"Molumn strip = {b/2} cm, thickness = {t} cm,")

    # Trials
    main_reinf = 12
    trav_reinf = 9

    # instanciate
    beam = Beam(fc, fy, fv, c)

    # Trials
    beam.section_properties(main_reinf, trav_reinf, b, t)

    # Calculate effective depth, and 𝜙Mn
    d, d1 = beam.eff_depth()
    𝜙Mn1 = beam.capacity(d)

    # --------------------------------
    ## Design
    # --------------------------------
    # Display rebar df
    table = os.path.join(CURRENT, "data/Deform_Bar.csv")
    rebar_df = pd.read_csv(table)
    display_df(rebar_df)

    while True:
        # Define Mu
        Mu = float(input("See Distribute Design Moment and efine Mu in kN-m : "))

        # Check classification
        classify = beam.classification(Mu, 𝜙Mn1)

        # Main bar required
        data = beam.mainbar_req(d, d1, 𝜙Mn1, Mu, classify)

        # Design main reinf
        no, main_dia, As_main = beam.main_design(data)

        print(f"Dia-{main_dia}mm @{np.ceil(b/no)} cm")

        ask = input("Design another section! Y|N :").upper()
        if ask == "Y":
            pass
        else:
            break
