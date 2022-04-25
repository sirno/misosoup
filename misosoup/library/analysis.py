"""Functions for analysis."""
import re

import pandas as pd
import numpy as np


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
    return df[selector].apply(
        lambda row: frozenset(row.index[row == 1]) - frozenset([f"y_{row.strain}"]),
        axis=1,
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
    return df[selector].apply(
        lambda row: (frozenset(row.index[row == 1])),
        axis=1,
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


def get_unique_strains(data_frame: pd.DataFrame):
    """Get all strains included in the dataset.

    Parameters
    ----------
    data_frame : pandas.DataFrame
        A solution dataframe from misosoup.
    """
    regex = re.compile(r"Growth_(\w+)")
    return [regex.match(c).groups()[0] for c in data_frame.columns if regex.match(c)]


def get_unique_focal_strains(data_frame: pd.DataFrame):
    """Get all focal strains included in the dataset.

    Parameters
    ----------
    data_frame : pandas.DataFrame
        A solution dataframe from misosoup.
    """
    return data_frame.reset_index().strain.unique()


def get_unique_carbon_sources(data_frame: pd.DataFrame):
    """Get all unique carbon sources in the dataset.

    Parameters
    ----------
    data_frame : pandas.DataFrame
        A solution dataframe from misosoup.
    """
    return data_frame.reset_index().carbon_source.unique()


def count_carbon_sources_for_strain(data_frame: pd.DataFrame):
    """Count the number of viable environments for each strain.

    Parameters
    ----------
    data_frame : pandas.DataFrame
        A solution dataframe from misosoup.
    """
    df = data_frame.reset_index()
    strains = get_unique_strains(df)
    unique_carbon_sources = [
        len(df[df[f"Growth_{strain}"] > 0].carbon_source.unique()) for strain in strains
    ]
    return pd.DataFrame({"strain": strains, "carbon_sources": unique_carbon_sources})


def count_carbon_sources_as_focal_strain(data_frame: pd.DataFrame):
    """Count the number of viable environments as focal strain.

    Parameters
    ----------
    data_frame : pandas.DataFrame
        A solution dataframe from misosoup.
    """
    df = data_frame.reset_index()
    strains = get_unique_strains(df)
    unique_carbon_sources = [
        len(df[(df.strain == strain) & (df.growth_rate > 0)].carbon_source.unique())
        for strain in strains
    ]
    return pd.DataFrame(
        {"strain": strains, "focal_carbon_sources": unique_carbon_sources}
    )


def count_carbon_sources_for_isolation(data_frame: pd.DataFrame):
    """Count the number of viable environments as focal strain.

    Parameters
    ----------
    data_frame : pandas.DataFrame
        A solution dataframe from misosoup.
    """
    df = data_frame.reset_index()
    strains = get_unique_strains(df)
    supplied = np.array(map(lambda x: len(x) == 0, get_suppliers(df)))
    unique_carbon_sources = [
        len(
            df[
                (df.strain == strain) & (df.growth_rate > 0) & supplied
            ].carbon_source.unique()
        )
        for strain in strains
    ]
    return pd.DataFrame(
        {"strain": strains, "isolated_carbon_sources": unique_carbon_sources}
    )


def count_carbon_sources_as_supplier_strain(data_frame: pd.DataFrame):
    """Count the number of viable environments as supplier strain.

    Parameters
    ----------
    data_frame : pandas.DataFrame
        A solution dataframe from misosoup.
    """
    df = data_frame.reset_index()
    strains = get_unique_strains(df)
    unique_carbon_sources = [
        len(
            df[
                (df.strain != strain) & (df[f"Growth_{strain}"] > 0)
            ].carbon_source.unique()
        )
        for strain in strains
    ]
    return pd.DataFrame(
        {"strain": strains, "supplier_carbon_sources": unique_carbon_sources}
    )


def count_communities_as_supplier_strain(data_frame: pd.DataFrame):
    """Count the number of communities as supplier strain.

    Parameters
    ----------
    data_frame : pandas.DataFrame
        A solution dataframe from misosoup.
    """
    df = data_frame.reset_index()
    strains = get_unique_strains(df)
    unique_communities = [
        len(df[(df.strain != strain) & (df[f"Growth_{strain}"] > 0)])
        for strain in strains
    ]
    return pd.DataFrame({"strain": strains, "communities": unique_communities})


def count_isolated_strains_on_carbon_source(data_frame: pd.DataFrame):
    """Count the number of strains in isolation on a carbon source.

    Parameters
    ----------
    data_frame : pandas.DataFrame
        A solution dataframe from misosoup.
    """
    df = data_frame.reset_index()
    indicator_columns = [column for column in df.columns if column.startswith("y_")]
    return pd.DataFrame(
        df[df[indicator_columns].sum(axis=1) == 1]
        .groupby("carbon_source")
        .size()
        .rename("isolated_strains")
    )


def count_non_redundant_supplying_communities_on_carbon_source(
    data_frame: pd.DataFrame,
):
    """Count the number of non-redundant supplying communities on a carbon source.

    Parameters
    ----------
    data_frame : pandas.DataFrame
        A solution dataframe from misosoup.
    """
    df = data_frame.reset_index()
    supplying_communities = pd.DataFrame(
        {
            "carbon_source": df.carbon_source,
            "supplying_community": get_suppliers(df),
        }
    )
    return (
        supplying_communities.groupby("carbon_source")
        .apply(lambda group: len(frozenset(group.supplying_community)) - 1)
        .rename("supplying_community")
        .to_frame()
    )


def count_exchanged_metabolites_on_carbon_source(data_frame: pd.DataFrame):
    """Count the number of metabolites exchanged on a carbon source.

    Parameters
    ----------
    data_frame : pandas.DataFrame
        A solution dataframe from misosoup.
    """
    df = data_frame.reset_index()
    metabolites_exchanged = pd.DataFrame(
        {
            "carbon_source": df.carbon_source,
            "metabolites_exchanged": compute_crossfeed(df),
        }
    )
    return (
        metabolites_exchanged.groupby("carbon_source")
        .apply(lambda group: len(frozenset(group.metabolites_exchanged)) - 1)
        .rename("metabolites_exchanged")
        .to_frame()
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
