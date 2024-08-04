import numpy as np

from utils import get_valid_number


# Check punching shear
def punching(fc):
    # Punching Area
    c1A = get_valid_number("Column width(along l1) in cm : ")
    c2A = get_valid_number("Column depth(along l2) in cm : ")
    d = get_valid_number("Effective depth in cm : ")
    Pu = get_valid_number("See EFM Table table and define axial load in kN : ")

    Ap = (c1A + c2A + 2 * d) * d * 1e2  # convert cm2 to mm2

    𝜙Vp = 0.85 * 0.25 * np.sqrt(fc) * Ap * 1e-3  # convert N to kN

    if 𝜙Vp > Pu:
        print(f"𝜙Vp = {𝜙Vp:.2f} kN > Pu ={Pu:.2f} kN --> Punching shear capacity OK")
    else:
        print(
            f"𝜙Vp = {𝜙Vp:.2f} kN < Pu ={Pu:.2f} kN --> Punching shear capacity NOT OK"
        )
