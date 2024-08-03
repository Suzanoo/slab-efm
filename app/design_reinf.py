import os
import pandas as pd

from beam_class import Beam


from utils import display_df, convert_input_to_list
from plot_section import create_html


# ----------------------------------
def design(fc, fy, fv, b, t, c):
    """
    b: width in cm
    t: thickness in cm
    c: covering in cm
    """
    CURRENT = os.getcwd()

    # Trials
    main_reinf = 12
    trav_reinf = 9

    print(f"\n==========Design reinforcement==========")

    # print("PROPERTIES")
    # print(
    #     f"f'c = {fc} Mpa, fy = {fy} Mpa, fv = {fv} MPa, Es = {Es:.0f} MPa"
    # )
    # print(f"𝜙b = {𝜙b}, 𝜙v = {𝜙v}")

    # print(f"\nGEOMETRY")
    # print(f"b = {b} cm, t = {t} cm,")

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
    N = []
    main_reinf = []
    traverse_reinf = []
    # spacing = []
    n = 1

    # Display rebar df
    table = os.path.join(CURRENT, "data/Deform_Bar.csv")
    df = pd.read_csv(table)
    display_df(df)

    # Design reinforce
    while True:
        print(f"\n--------------- SECTION-{n} -----------------")
        Mu = float(input("Define Mu in kN-m : "))
        # Vu = float(input("Define Vu in kN : "))

        # Check classification
        classify = beam.classification(Mu, 𝜙Mn1)

        # Main bar required
        data = beam.mainbar_req(d, d1, 𝜙Mn1, Mu, classify)

        # Design main reinf
        no, main_dia, As_main = beam.main_design(data)

        # Design traverse
        # traverse_dia, Av, s = beam.traverse_design(d, Vu)

        # Collect for plotting
        N.append(no)
        main_reinf.append(main_dia)
        # traverse_reinf.append(traverse_dia)
        # spacing.append(s)

        ask = input("Design another section! Y|N :").upper()
        if ask == "Y":
            n += n
        else:
            break

    # Lay rebars in each layer
    bottom_reinf = []
    top_reinf = []
    middle_reinf = []

    print(f"\nYou have {n} section. Next is to locate the rebars step :  ")
    ask = input("Do you want to change number of section to display  ! Y|N : ")
    if ask == "Y":
        n = int(input("New n = ? : "))

    for i in range(n):
        bott = convert_input_to_list(
            input(f"Section-{i+1}, Lay rebars in bottom layer, ex. 3 2 : ")
        )
        top = convert_input_to_list(
            input(f"Section-{i+1}, Lay rebars in top layer, ex. 3 2 : ")
        )
        # middle = int(
        #     input(f"Section-{i+1}, How many middle rebar? Even numbers only, ex. 4 : ")
        # )
        # TODO check middle is even number
        bottom_reinf.append(bott)
        top_reinf.append(top)
        # middle_reinf.append(middle)

    # create_html(
    #     None,
    #     n,
    #     b,
    #     t,
    #     c,
    #     traverse_reinf,
    #     main_reinf,
    #     bottom_reinf,
    #     top_reinf,
    #     middle_reinf,
    # )
