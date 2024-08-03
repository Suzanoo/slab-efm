import numpy as np
import pandas as pd
from scipy.interpolate import griddata

from utils import isb

np.set_printoptions(precision=3)


# Ksb
class Slab_Beam_Stiffness:
    def __init__(self):
        pass

    # Calculated slab-beam stifness factors
    def get_slab_beam_stiffness(self, A_value, B_value, path, method):
        df = pd.read_csv(path)

        # Check if A, B is within the range, otherwise use the maximum or minimum value
        A_value = max(df["A"].min(), min(A_value, df["A"].max()))
        B_value = max(df["B"].min(), min(B_value, df["B"].max()))

        # Extract relevant columns
        points = df[["A", "B"]].values
        values = df.iloc[:, 2:].values

        # Interpolate values for columns 3 to 8
        interpolated_values = griddata(
            points, values, [(A_value, B_value)], method=method
        )

        # Create a DataFrame with the interpolated values
        interpolated_df = pd.DataFrame(interpolated_values, columns=df.columns[2:])

        # Add columns A and B with their values
        interpolated_df.insert(0, "A", A_value)
        interpolated_df.insert(1, "B", B_value)

        print(interpolated_df)

        return interpolated_df

    def flat(self, c1A, c1B, b, t, l1, fc, method="linear"):
        """
        c1A: width of column A, mm
        c1B: width of column B , mm
        l1: span along C1A-C1B, mm
        b: slab-beam strip width, mm
        t: slab thickness, mm
        """
        Ec = 4700 * np.sqrt(fc)
        Is = (1 / 12) * b * pow(t, 3)
        Ib = 0

        print(f"Slab-Beam Stiffness Coefficien: Flat Slab")
        print(f"c1A/l1 = {c1A/l1:.4f}")
        print(f"c1B/l1 = {c1B/l1:.4f}")

        # Calculate factor values
        df = self.get_slab_beam_stiffness(
            c1A / l1, c1B / l1, "data/slab-beam-coeff.csv", method
        )

        a = ["K.AB", "K.BA"]
        m = ["M.AB", "M.BA"]
        c = ["COF.AB", "COF.BA"]
        b = ["AB", "BA"]
        Ksb = []
        COF = []
        FEM = []

        for i in range(0, len(a)):
            k = df.at[0, a[i]]
            ksb = k * Ec * (Is + Ib) / l1

            Ksb.append(ksb)
            COF.append(df.at[0, c[i]])
            FEM.append(df.at[0, m[i]])

            print(f"Ksb.{b[i]} = {ksb:.2e} N/mm2")

        return Ksb, COF, FEM

    def drop_panel(self, dp1A, dp1B, bs, t, l1, fc, method="linear"):
        """
        dp1A: width of drop-panel A, mm
        dp1B: width of drop-panel B , mm
        l1: span along C1A-C1B, mm
        bs: slab-beam strip width, mm
        t: slab thickness, mm
        """
        Ec = 4700 * np.sqrt(fc)
        Is = (1 / 12) * bs * pow(t, 3)
        Ib = 0

        print(f"Slab-Beam Stiffness Factors: Flat with Drop-Panel")
        print(f"c1A/l1 = {dp1A/l1:.4f}")
        print(f"c1B/l1 = {dp1B/l1:.4f}")

        # Calculate factor values by interpolating
        df = self.get_slab_beam_stiffness(
            dp1A / l1, dp1B / l1, "data/slab-beam-coeff-with-drop.csv", method
        )

        a = ["K.AB", "K.BA"]
        m = ["M.AB", "M.BA"]
        c = ["COF.AB", "COF.BA"]
        b = ["AB", "BA"]
        Ksb = []
        COF = []
        FEM = []

        for i in range(0, len(a)):
            k = df.at[0, a[i]]
            ksb = k * Ec * (Is + Ib) / l1

            Ksb.append(ksb)
            COF.append(df.at[0, c[i]])
            FEM.append(df.at[0, m[i]])

            print(f"Ksb.{b[i]} = {ksb:.2e} N/mm2")

        return Ksb, COF, FEM

    def traverse_beam_interia(self, fc, c1A, c1B, l1, Is, Ib, method="linear"):
        """
        c1A: width of column A, mm
        c1B: width of column B , mm
        l1: span along C1A-C1B, mm
        """

        Ec = 4700 * np.sqrt(fc)

        print(f"Slab-Beam Stiffness Factors: Slab with Beam Traverse")
        print(f"c1A/l1 = {c1A/l1:.4f}")
        print(f"c1B/l1 = {c1B/l1:.4f}")

        # Calculate factor values by interpolating
        df = self.get_slab_beam_stiffness(
            c1A / l1, c1B / l1, "data/slab-beam-coeff.csv", method
        )

        a = ["K.AB", "K.BA"]
        m = ["M.AB", "M.BA"]
        c = ["COF.AB", "COF.BA"]
        b = ["AB", "BA"]
        Ksb = []
        COF = []
        FEM = []

        for i in range(0, len(a)):
            k = df.at[0, a[i]]
            ksb = k * Ec * (Is + Ib) / l1

            Ksb.append(ksb)
            COF.append(df.at[0, c[i]])
            FEM.append(df.at[0, m[i]])

            print(f"Ksb.{b[i]} = {ksb:.2e} N/mm2")

        return Ksb, COF, FEM

        # def traverse_beam_exteria(self, c1A, c1B, bw, h, t, l1, l2, fc, method="linear"):
        """
        c1A: width of column A, mm
        c1B: width of column B , mm
        l1: span along C1A-C1B, mm
        w: beam width, mm
        h: beam depth, mm
        bw: beam width, mm
        t: slab thickness, mm
        """
        bs = l2 / 2
        # b = bs + bw / 2

        hf = t
        hw = h - hf
        bf = bw + min(hw, 4 * t)

        Ec = 4700 * np.sqrt(fc)
        Is = (1 / 12) * bs * pow(t, 3)
        Ib = isb(bw, bf, hw, hf)

        print(f"Slab-Beam Stiffness Factors: Slab with Beam Traverse")
        print(f"c1A/l1 = {c1A/l1:.4f}")
        print(f"c1B/l1 = {c1B/l1:.4f}")

        # Calculate factor values by interpolating
        df = self.get_slab_beam_stiffness(
            c1A / l1, c1B / l1, "data/slab-beam-coeff.csv", method
        )

        a = ["K.AB", "K.BA"]
        m = ["M.AB", "M.BA"]
        c = ["COF.AB", "COF.BA"]
        b = ["AB", "BA"]
        Ksb = []
        COF = []
        FEM = []

        for i in range(0, len(a)):
            k = df.at[0, a[i]]
            ksb = k * Ec * (Is + Ib) / l1

            Ksb.append(ksb)
            COF.append(df.at[0, c[i]])
            FEM.append(df.at[0, m[i]])

            print(f"Ksb.{b[i]} = {ksb:.2e} N/mm2")

        return Ksb, COF, FEM


# Kc
class Column_Stiffness:
    """
    Kc: Column stiffness
    K: Stiffness factors
    COF: Carry over factors
    FEM: Fixed end moment factors
    """

    def __init__(self) -> None:
        pass

    # Calculated column stifness factors
    def get_columns_stiffness(self, A_value, method):
        df = pd.read_csv("data/column-coeff.csv")

        # Check if A_value is within the range, otherwise use the maximum or minimum value
        A_value = max(df["A"].min(), min(A_value, df["A"].max()))

        # Extract relevant columns
        points = df[["A"]].values
        values = df.iloc[:, 1:].values

        # Interpolate values for columns 2 to end
        interpolated_values = griddata(points, values, [(A_value)], method=method)

        # Create a DataFrame with the interpolated values
        interpolated_df = pd.DataFrame(interpolated_values, columns=df.columns[1:])

        # Add column A with its value
        interpolated_df.insert(0, "A", A_value)

        print(interpolated_df)

        return interpolated_df

    # Column stiffness(Kc)
    def kc(self, c1A, lc, Ic, fc, method="linear"):
        """
        Warning !!!

        -c1A : Thickness of slab with drop panel or
        column capital or
        beam above the column in direction of l1, mm
        """
        Ec = 4700 * np.sqrt(fc)

        print(f"c1A/lc = {c1A/lc:.4f}")
        df = self.get_columns_stiffness(c1A / lc, method)

        a = ["K.AB", "K.BA"]
        b = ["bot", "top"]
        Kc = []
        for i in range(0, len(a)):
            k = df.at[0, a[i]]
            kc = k * Ec * Ic / lc
            Kc.append(kc)
            print(f"Kc.{b[i]} = {kc:.2e} N/mm2")
        return Kc


# Kt
class Torsion_Stiffness:
    """
    flat slab: c1 x hf
    flat slab with capital: c1 x hc
    with traverse beam(exterior): L-beam,  h x (w + min(hw, 4 * t))
    with traverse beam(interior): T- beam,  h x (w + 2 * min(hw, 4 * t))

    c1: column dimension in the direction of l1
    c2: column dimension in the direction of l2
    t: slab thickness
    l2: the length of tortional member c/c
    """

    def __init__(self, fc):
        self.Ec = 4700 * np.sqrt(fc)

    def flat(self, c1, c2, t, l2):
        x1 = t
        y1 = c1
        C = (1 - 0.63 * x1 / y1) * (pow(x1, 3) * y1) / 3
        Kt = 9 * self.Ec * C / (l2 * pow((1 - c2 / l2), 3))

        print(f"C: {C:.2e} mm4")
        print(f"Kt = {Kt:.2e} N.mm")
        return Kt

    def drop_panel(self, c1, c2, td, l2):
        """
        td: drop thickness
        """
        x1 = c1
        y1 = td
        C = (1 - 0.63 * (x1 / y1)) * (pow(x1, 3) * y1) / 3
        Kt = 9 * self.Ec * C / (l2 * pow((1 - c2 / l2), 3))
        print(f"Kt = {Kt:.2e} N.mm")
        return Kt

    def ext_beam(self, bw, h, t, c2, l1, l2):
        """
        h: beam depth
        hf: flange thickness
        hw: h - hf
        bw: beam(web) width
        bf: flange width
        """
        hw = h - t
        hf = t
        bf = bw + min(hw, 4 * hf)
        bs = l1 + bw

        x1 = bw
        x2 = hf
        y1 = h
        y2 = bf - bw
        C1 = (1 - 0.63 * (x1 / y1)) * (pow(x1, 3) * y1) / 3
        C2 = (1 - 0.63 * (x2 / y2)) * (pow(x2, 3) * y2) / 3
        CA = C1 + C2

        y1 = hw
        y2 = bf
        C1 = (1 - 0.63 * (x1 / y1)) * (pow(x1, 3) * y1) / 3
        C2 = (1 - 0.63 * (x2 / y2)) * (pow(x2, 3) * y2) / 3
        CB = C1 + C2

        C = max(CA, CB)
        Is = (1 / 12) * bs * pow(hf, 3)
        Isb = isb(bw, bs, hw, hf)
        Kt = 9 * self.Ec * C / (l2 * pow((1 - c2 / l2), 3))
        Kt = Kt * Isb / Is
        print(f"Kt = {Kt:.2e} N.mm")
        return Kt

    def tee(self, bw, h, t, c2, l1, l2):
        """
        h: beam depth
        hf: flange thickness
        hw: h - hf
        bw: beam(web) width
        bf: flange width
        """
        hw = h - t
        hf = t
        bf = bw + 2 * min(hw, 4 * hf)
        bs = l1

        x1 = hf
        x2 = hw
        y1 = bf
        y2 = bw
        C1 = (1 - 0.63 * (x1 / y1)) * (pow(x1, 3) * y1) / 3
        C2 = (1 - 0.63 * (x2 / y2)) * (pow(x2, 3) * y2) / 3
        C = C1 + C2

        Is = (1 / 12) * bs * pow(hf, 3)
        Isb = isb(bw, bs, hw, hf)

        Kt = 9 * self.Ec * C / (l2 * pow((1 - c2 / l2), 3))
        Kt = Kt * Isb / Is
        print(f"Kt = {Kt:.2e} N.mm")
        return Kt
