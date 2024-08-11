import numpy as np


# def to_numpy(x):
#     x = re.findall(r"[-+]?(?:\d*\.\d+|\d+)", x)
#     return np.array([float(n) for n in x])


def to_numpy(s):
    return np.fromstring(s, sep=" ")


def get_valid_number(prompt):
    while True:
        user_input = input(prompt)
        try:
            # Try to convert the input to a float
            value = float(user_input)
            return value
        except ValueError:
            print("Invalid input. Please enter a valid number.")


def get_valid_integer(prompt):
    while True:
        user_input = input(prompt)
        if user_input.isdigit():
            return int(user_input)
        else:
            print("Invalid input. Please enter a valid number.")



def get_valid_list_input(prompt):
    while True:
        user_input = input(prompt)
        try:
            array = to_numpy(user_input)
            if len(array) == 0:
                raise ValueError("No valid numbers found.")
            return array
        except ValueError as e:
            print(
                f"Invalid input: {e}. Please enter a space-separated list of numbers."
            )



def convert_input_to_list(input_string):
    return list(map(int, input_string.split()))



def add_sign(array):
    """
    Input: np.array([100, 50])
    Output: np.array([100, -100, 50, -50])
    """
    nums = len(array)
    result = []

    for i in range(nums):
        result.append(array[i])  # Positive moment at the start of the span
        result.append(-array[i])  # Negative moment at the end of the span

    return np.array(result)



# Inertia for L-Shape and Tee
def isb(bw, bf, hw, hf):
    A1 = bw * hw
    A2 = bf * hf
    d1 = hw / 2
    d2 = hw + hf / 2

    A = A1 + A2

    yd = (A1 * d1 + A2 * d2) / A
    print(f"\nNA = {yd:.0f} mm from bottom")

    I1 = (1 / 12) * bw * pow(hw, 3) + A1 * (yd - d1) ** 2
    I2 = (1 / 12) * bf * pow(hf, 3) + A2 * (yd - d2) ** 2
    I = I1 + I2
    # print(f"I = {I:.2e} mm4")
    return I
