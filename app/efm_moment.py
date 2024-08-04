import pandas as pd
import numpy as np

from utils_df import display_df, multiply_row_by_array


def calculate_fixend_moment(qu, l1, l2):
    """
    qu: area load, kN/m2
    l1: distance along, m
    l2: slab-beam cross section width, m
    """
    return qu * l2 * l1**2


def calculate_balance_moment(DF_row, FEM_row):
    # Sum moment at node before calculate Balance.M
    def calculate_FEM_X(FEM):
        FEM_X = [FEM[0]]  # first
        for i in range(1, len(FEM)):
            if i == len(FEM) - 1:  # last
                FEM_X.append(FEM[i])
            elif i % 2 != 0:
                FEM_X.append(FEM[i] + FEM[i + 1])
            else:
                FEM_X.append(FEM[i] + FEM[i - 1])
        return FEM_X

    # Calculate DF * FEM_X
    DF = np.array([DF_row])
    FEM_X = np.array([calculate_FEM_X(FEM_row)])
    Bal_M = -DF * FEM_X

    return Bal_M.flatten()


def calculate_carry_over_moment(COF_row, Bal_M_row):
    # Cross over balance moment before multiply by COF
    def calculate_COM_X(Bal_M_row):
        COF_X = []
        for i in range(0, len(Bal_M_row)):
            if i % 2 == 0:
                COF_X.append(Bal_M_row[i + 1])
            else:
                COF_X.append(Bal_M_row[i - 1])
        return COF_X

    # Calculate COF * COF_X
    COF = np.array([COF_row])
    COF_X = np.array([calculate_COM_X(Bal_M_row)])
    COM = COF * COF_X

    return COM.flatten()


def calculate_moment_at_support(num_spans, DF, COF, FEM, fem, num_iter):
    # Generate joint names (A, B, C, ...)
    joints = [chr(ord("A") + i) for i in range(num_spans + 1)]

    # Generate column names based on joint names
    columns = ["Slab-Beam"]  # Set the first column name to "Slab-Beam"
    for i in range(len(joints) - 1):
        column_name_forward = f"{joints[i]}{joints[i + 1]}"
        column_name_reverse = f"{joints[i + 1]}{joints[i]}"
        columns.extend([column_name_forward, column_name_reverse])

    # Create an empty DataFrame with the generated columns
    df = pd.DataFrame(columns=columns)

    # Fill the first row with provided DF values
    df.loc[0, "Slab-Beam"] = "DF"
    df.loc[0, df.columns[1:]] = [item for sublist in DF for item in sublist]

    # Fill the second row with COF values
    df.loc[1, "Slab-Beam"] = "COF"
    df.loc[1, df.columns[1:]] = [item for sublist in COF for item in sublist]

    # Fill the third row with Moment coeff. or moment values
    df.loc[2, "Slab-Beam"] = "FEM"
    df.loc[2, df.columns[1:]] = [item for sublist in FEM for item in sublist]

    # FEM x FEM.coeff
    df = multiply_row_by_array(df, "Slab-Beam", "FEM", fem)

    DF_row = df.iloc[0].values[1:]
    COF_row = df.iloc[1].values[1:]

    # Iteration
    for i in range(1, num_iter):
        # Calculate Balance Moment using the provided function
        Bal_M = calculate_balance_moment(DF_row, df.iloc[-1].values[1:])

        # Fill the fourth row with calculated Bal.M values
        df.loc[(2 * i + 1), "Slab-Beam"] = "Balance Moment"
        df.loc[(2 * i + 1), df.columns[1:]] = Bal_M

        # Calculate Carry Over Moment
        COM = calculate_carry_over_moment(COF_row, df.iloc[-1].values[1:])

        # Fill row with calculated COM values
        df.loc[(2 * i + 2), "Slab-Beam"] = "Carry-over"
        df.loc[(2 * i + 2), df.columns[1:]] = COM

    # Sum each column starting from FEM row
    moment = df.iloc[2:, 1:].sum()

    # Convert the sum to a DataFrame and transpose it
    sum_row = pd.DataFrame([["veM@support"] + moment.tolist()], columns=df.columns)
    df = pd.concat([df, sum_row])

    print("Moment Distribution")
    display_df(df)

    return df


def calculate_shear(num_spans, df, qu, l1, l2):
    """
    qu : area load in kN
    l1, l2 in m
    """
    # Grab moment row from df
    i = df[df["Slab-Beam"] == "veM@support"].index[0]
    M = df.iloc[i, 1:].tolist()

    # Calculate reaction
    V = []
    for i in range(num_spans):
        ML = M[2 * i]
        MR = M[2 * i + 1]

        V.append(((qu * l1[i] * l2) / 2) + (ML + MR) / l1[i])
        V.append(((qu * l1[i] * l2) / 2) - (ML + MR) / l1[i])

    # Concat reaction into df
    Vij = pd.DataFrame([["veV@support"] + V], columns=df.columns)

    return Vij


def calculate_possitive_moment(num_spans, df, qu, l1, l2):
    """
    qu : area load in kN
    l1, l2 in m
    """
    # Grab moment row from df
    Mij = df[df["Slab-Beam"] == "veM@support"].iloc[0, 1:].tolist()

    # Calculate max.x amd max.M+
    X = []
    poss_M = []

    # Calculate Max.M+ for each span
    for i in range(num_spans):
        # Fetch ML, MR of each span and take to absolute value
        ML = np.abs(Mij[2 * i])
        MR = np.abs(Mij[2 * i + 1])

        # Calculate distance where Vu=0 --> Max.M+
        x = (l1[i] / 2) + (ML - MR) / (qu * l2 * l1[i])

        # Calculate M+
        M_poss = (1 / 8) * qu * l2 * l1[i] ** 2

        M0 = M_poss - (ML + MR) / 2

        X.append(x)
        poss_M.append(M0)

    # --------------------
    # Generate joint names (A, B, C, ...)
    joints = [chr(ord("A") + i) for i in range(num_spans + 1)]

    # Generate column names based on joint names
    columns = ["Slab-Beam"]  # Set the first column name to "Slab-Beam"
    for i in range(len(joints) - 1):  # AB BC CD ...
        columns.append(f"{joints[i]}{joints[i + 1]}")

    # Create an empty DataFrame with the generated columns
    df = pd.DataFrame(columns=columns)

    # Fill the first row with provided DF values
    df.loc[0, "Slab-Beam"] = "max.X"
    df.loc[0, df.columns[1:]] = X

    # Fill the 2nd row with provided DF values
    df.loc[1, "Slab-Beam"] = "max.M+"
    df.loc[1, df.columns[1:]] = poss_M

    print(f"\nMaximum Possitive Span Moments")
    display_df(df)

    return df


def calculate_face_moments(columns, qu, l2, df):
    """
    qu : area load in kN
    l1, l2 in m
    """

    # Extract Mu and Vu
    Mij = df[df["Slab-Beam"] == "veM@support"].iloc[0, 1:].tolist()
    Vij = df[df["Slab-Beam"] == "veV@support"].iloc[0, 1:].tolist()

    # Extract c1 values from columns
    c1_values = [c[0] for c in columns]

    # Calculate M_face and V_face for each node
    M_face = []
    V_face = []

    for i in range(len(Vij)):
        Vi = Vij[i]
        Mi = Mij[i]  # Adjust indexing for spans
        c1 = c1_values[i % len(c1_values)]  # Adjust indexing for spans

        # Rigth face
        if i % 2 == 0:
            M_face_value = 0.5 * Vi * c1 - Mi - 0.5 * qu * l2 * (c1 / 2) ** 2
            V_face_value = (qu * l2 * c1 / 2) - Vi

        # Left face
        else:
            M_face_value = -(-0.5 * Vi * c1 - Mi + 0.5 * qu * l2 * (c1 / 2) ** 2)
            V_face_value = -((qu * l2 * c1 / 2) - Vi)

        M_face.append(M_face_value)
        V_face.append(V_face_value)

    # Create M.face df and V.face df
    M_face = pd.DataFrame([["veM@face"] + M_face], columns=df.columns)
    V_face = pd.DataFrame([["veV@face"] + V_face], columns=df.columns)

    return M_face, V_face


def efm_table(num_spans, columns, l1, l2, qu, df):
    """
    columns : list of column dimension in m
    qu : area load in kN
    l1, l2 in m
    """
    # Calculate shear
    Vu_df = calculate_shear(num_spans, df, qu, l1, l2)
    df = pd.concat([df, Vu_df])

    # Calculate Max.M+ of each span
    poss_moment_df = calculate_possitive_moment(num_spans, df, qu, l1, l2)

    M_face, V_face = calculate_face_moments(columns, qu, l2, df)

    # Concat M.face
    df = pd.concat([df, M_face])

    # Concat V.face
    df = pd.concat([df, V_face])

    print(f"\nEFM Table")
    display_df(df)

    return df, poss_moment_df


def calculate_design_moments(neg_moment_df, poss_moment_df):
    # Initialize an empty list to store the rows of the new DataFrame
    new_df_rows = []

    # Get the list of spans from poss_moment_df
    spans = poss_moment_df.columns[1:]

    # Iterate through the spans and generate the new DataFrame rows with weights
    for idx, span in enumerate(spans):
        if idx == 0:
            # First span
            weights = [100, 60, 75]
        elif idx == len(spans) - 1:
            # Last span
            weights = [75, 60, 100]
        else:
            # Intermediate spans
            weights = [75, 60, 75]

        # Get the values from neg_moment_df and poss_moment_df for the current span
        Mu_L = (
            neg_moment_df.loc[neg_moment_df["Slab-Beam"] == "veM@face", span].values[0]
            if span in neg_moment_df.columns
            else None
        )
        M_plus = (
            poss_moment_df.loc[poss_moment_df["Slab-Beam"] == "max.M+", span].values[0]
            if span in poss_moment_df.columns
            else None
        )
        Mu_R = (
            neg_moment_df.loc[
                neg_moment_df["Slab-Beam"] == "veM@face", span[::-1]
            ].values[0]
            if span[::-1] in neg_moment_df.columns
            else None
        )

        # Add rows to new_df for the current span with weights
        new_df_rows.append([span, "L", Mu_L, weights[0]])
        new_df_rows.append([span, "M", M_plus, weights[1]])
        new_df_rows.append([span, "R", Mu_R, weights[2]])

    # Create the new DataFrame
    new_df = pd.DataFrame(
        new_df_rows, columns=["Slab-Beam", "Locate", "Mu(kN)", "Weight(%)"]
    )

    # Distribute Mu to columns strip and middle strip
    new_df["Column Strip(kN)"] = new_df["Mu(kN)"] * new_df["Weight(%)"] / 100
    new_df["Middle Strip(kN)"] = new_df["Mu(kN)"] * (1 - new_df["Weight(%)"] / 100)

    print(f"\nDistribute Design Moment:")
    display_df(new_df)

    return new_df
