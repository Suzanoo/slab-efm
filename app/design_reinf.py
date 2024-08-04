import os
import numpy as np
import pandas as pd

from beam_class import Beam

from utils_df import display_df


# ----------------------------------
class Design:
    def __init__(self, fc, fv, fy, c) -> None:
        """
        fc, fv, fy  in MPa
        c: covering in cm
        """
        self.fc = fc
        self.fv = fv
        self.fy = fy

        # instanciate
        self.beam = Beam(fc, fy, fv, c)

        # Trials
        self.main_reinf = 12
        self.trav_reinf = 9

        CURRENT = os.getcwd()

        # Display rebar df
        table = os.path.join(CURRENT, "data/Deform_Bar.csv")
        rebar_df = pd.read_csv(table)
        display_df(rebar_df)

    def definition(self, b, t):
        """
        b: width in cm
        t: thickness in cm
        """
        # Trials
        self.beam.section_properties(self.main_reinf, self.trav_reinf, b, t)

    def design_reinf(self, b, t):
        """
        b: width in cm
        t: thickness in cm
        c: covering in cm
        """
        self.definition(b, t)

        d, d1 = self.beam.eff_depth()
        𝜙Mn1 = self.beam.capacity(d)

        while True:
            # Define Mu
            Mu = float(input("See Distribute Design Moment and define Mu in kN-m : "))

            # Check classification
            classify = self.beam.classification(Mu, 𝜙Mn1)

            # Main bar required
            data = self.beam.mainbar_req(d, d1, 𝜙Mn1, Mu, classify)

            # Design main reinf
            no, main_dia, As_main = self.beam.main_design(data)

            print(f"Dia-{main_dia}mm @{np.ceil(b/no)} cm")

            ask = input("Design another section! Y|N :").upper()
            if ask == "Y":
                pass
            else:
                break

    def design_slab(self, b, t):
        self.design_reinf(b, t)

    def design_beam(self, bw, h):
        self.design_reinf(bw, h)

    def design_drop(self, dw, dh):
        self.design_reinf(dw, dh)
