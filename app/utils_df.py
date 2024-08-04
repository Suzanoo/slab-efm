from tabulate import tabulate


def display_df(df):
    print(
        tabulate(
            df,
            headers=df.columns,
            floatfmt=".2f",
            showindex=False,
            tablefmt="psql",
        )
    )


def multiply_row_by_array(df, column_name, row_namw, array):
    # Extract the  row
    fem_row = df.loc[df[column_name] == row_namw].iloc[0, 1:]

    # Multiply the  row by the  array
    new_fem_values = fem_row.values * array

    # Update the DataFrame with the new values
    df.loc[df[column_name] == row_namw, df.columns[1:]] = new_fem_values

    return df
