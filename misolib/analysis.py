import re
from misolib.common import get_compound_name


def _find_cross_feed(row, tol=1e-4):
    positive = set()
    negative = set()
    for rid, val in row.items():
        compound = re.search("(?<=R_EX_).*(?=_e)", rid)
        if compound and rid.endswith("INT"):
            global_rid = f"R_EX_{compound}_e"
            global_val = row[global_rid] if global_rid in row else 0
            adjusted_val = val - global_val
            if adjusted_val < -tol:
                negative.add(compound.group(0))
            elif adjusted_val > tol:
                positive.add(compound.group(0))
    return positive & negative


def _find_directed_cross_feed(row, tol=1e-4):
    strain = row.name[1]
    crossfeed = _find_cross_feed(row, tol)
    directed_crossfeed = {}
    for compound in crossfeed:
        rid = f"R_EX_{compound}_e_{strain}_INT"
        directed_crossfeed[compound] = row[rid] if rid in row else 0
    return directed_crossfeed


def compute_crossfeed(df, tol=1e-4):
    return df.apply(_find_cross_feed, axis=1, tol=tol)


def compute_directed_crossfeed(df, tol=1e-4):
    return df.apply(_find_directed_cross_feed, axis=1, tol=tol)


def find_suppliers(df):
    """Find suppliers.

    Args:
        df (DataFrame): MiSoS(oup) solution.
    """

    def find_suppliers(row):
        suppliers = set()
        for col, value in row.items():
            if col.startswith("y_") and value > 0.5:
                suppliers.add(col)
        return suppliers

    df["suppliers"] = df.apply(find_suppliers, axis=1)
    return df


def find_focal_strain_growth(df):
    """Find focal strain growth and add to DataFrame.
    Args:
        df (DataFrame): MiSoS(oup) solution.
    """
    df["strain_growth"] = df.apply(lambda row: row[f"Growth_{row.name[1]}"], axis=1)
    return df