import numpy as np


# Check punching shear
def punching(fc, A, Vup):
    """
    A: punching resistance area in mm
    Vu: in kN
    """
    𝜙Vp = 0.85 * 0.25 * np.sqrt(fc) * A * 1e3  # kN --> f'c = N/mm2, A = mm2

    if 𝜙Vp > Vup:
        print(f"𝜙Vp = {𝜙Vp:.2f} kN > Vup ={Vup:.2f} kN --> Punching shear capacity OK")
    else:
        print(
            f"𝜙Vp = {𝜙Vp:.2f} kN < Vup ={Vup:.2f} kN --> Punching shear capacity NOT OK"
        )
