"""Functions for analysis."""
import re

import pandas as pd


def compute_crossfeed(data_frame: pd.DataFrame, tol=1e-4):
    """Compute crossfeed."""
    return data_frame.apply(_find_cross_feed, axis=1, tol=tol)


def compute_directed_crossfeed(data_frame: pd.DataFrame, tol=1e-4):
    """Compute directed crossfeed."""
    return data_frame.apply(_find_directed_cross_feed, axis=1, tol=tol)


def get_suppliers(data_frame: pd.DataFrame):
    """Get suppliers.

    Parameters
    ----------
    data_frame : pandas.DataFrame
        A solution dataframe from misosoup.
    """

    df = data_frame.reset_index()
    selector = ["strain"] + [column for column in df.columns if column.startswith("y_")]
    return (
        df[selector].apply(
            lambda row: frozenset(row.index[row == 1]) - frozenset([f"y_{row.strain}"]),
            axis=1,
        ),
    )


def get_communities(data_frame: pd.DataFrame):
    """Get communities.

    Parameters
    ----------
    data_frame : pandas.DataFrame
        A solution dataframe from misosoup.
    """
    df = data_frame.reset_index()
    selector = ["strain"] + [column for column in df.columns if column.startswith("y_")]
    return (
        df[selector].apply(
            lambda row: (frozenset(row.index[row == 1])),
            axis=1,
        ),
    )


def find_focal_strain_growth(data_frame: pd.DataFrame):
    """Find focal strain growth and add to DataFrame.

    Parameters
    ----------
    data_frame : pandas.DataFrame
        A solution dataframe from misosoup.
    """
    data_frame["strain_growth"] = data_frame.apply(
        lambda row: row[f"Growth_{row.name[1]}"], axis=1
    )
    return data_frame


def count_viable_environments(data_frame: pd.DataFrame):
    """Count the number of viable environments for each strain.

    Parameters
    ----------
    data_frame : pandas.DataFrame
        A solution dataframe from misosoup.
    """
    return (
        data_frame[data_frame.growth_rate > 1e-4]
        .groupby(["carbon_source", "strain"])
        .size()
        .groupby("strain")
        .size()
    )


def _find_cross_feed(row, tol=1e-4):
    positive = set()
    negative = set()
    for rid, val in row.items():
        compound = re.search("(?<=R_EX_).*(?=_e)", rid)
        if compound and rid.endswith("_i"):
            global_rid = f"R_EX_{compound}_e"
            global_val = row[global_rid] if global_rid in row else 0
            adjusted_val = val - global_val
            if adjusted_val < -tol:
                negative.add(compound.group(0))
            elif adjusted_val > tol:
                positive.add(compound.group(0))
    return frozenset(positive & negative)


def _find_directed_cross_feed(row, tol=1e-4):
    strain = row.name[1]
    crossfeed = _find_cross_feed(row, tol)
    directed_crossfeed = {}
    for compound in crossfeed:
        rid = f"R_EX_{compound}_e_{strain}_i"
        directed_crossfeed[compound] = row[rid] if rid in row else 0
    return frozenset(directed_crossfeed)
