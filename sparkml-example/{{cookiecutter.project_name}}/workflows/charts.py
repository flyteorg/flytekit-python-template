from io import StringIO

import altair as alt
import pandas as pd


def plot_subgroup_performance(df: pd.DataFrame) -> str:
    """Plot the subgroup performance of a model.

    Assumes that the dataframe has a column called "target" and a column called
    "prediction". All other columns  are treated as features.

    Args:
        df (pd.DataFrame): a dataframe of features, target, and prediction

    Returns:
        str: chart as an html string
    """
    bucketed_data = df.copy()
    bucketed_data = bucketed_data[~bucketed_data.columns.str.startswith("__")]
    assert "target" in bucketed_data.columns, "target column is missing"
    assert "prediction" in bucketed_data.columns, "prediction column is missing"

    for col in bucketed_data.columns:
        if col not in ["target", "prediction"]:
            if len(bucketed_data[col].unique()) > 4:
                bucketed_data[col] = pd.qcut(
                    bucketed_data[col], 4, duplicates="drop"
                ).apply(lambda x: f"{col}[{x.left:.1f}-{x.right:.1f}]")
            else:
                bucketed_data[col] = bucketed_data[col].apply(lambda x: f"{col}={x}")
    # Calculate the average target and prediction for each subgroup
    grouped_data = []
    for col in bucketed_data.columns:
        if col not in ["target", "prediction"]:
            subgroup = (
                bucketed_data.groupby(col)
                .agg(
                    {
                        "target": "mean",
                        "prediction": "mean",
                    }
                )
                .reset_index()
                .rename(columns={col: "subgroup"})
            )
            subgroup["feature"] = col
            grouped_data.append(subgroup)

    grouped_data = pd.concat(grouped_data, axis=0, ignore_index=True)
    grouped_data["error"] = grouped_data["prediction"] - grouped_data["target"]

    grouped_data["error_sign"] = (grouped_data["error"] > 0).astype(int)

    # Create a vertical arrow chart
    arrow_base = (
        alt.Chart(grouped_data)
        .mark_rule(opacity=0.8)
        .encode(
            x=alt.X("subgroup:N", title="Subgroup"),
            y=alt.Y("target:Q", title="Observed vs Predicted Average"),
            y2="prediction:Q",
            color=alt.Color("feature:N", title="Feature"),
            tooltip=[
                alt.Tooltip("feature", title="Feature"),
                alt.Tooltip("subgroup", title="Subgroup"),
                alt.Tooltip("target", title="Observed Average", format=".2f"),
            ],
        )
    )

    arrow_head = (
        alt.Chart(grouped_data)
        .mark_point(filled=True, size=50)
        .encode(
            x=alt.X("subgroup:N"),
            y=alt.Y("prediction:Q"),
            shape=alt.Shape(
                "error_sign:N",
                scale=alt.Scale(domain=[0, 1], range=["triangle-down", "triangle-up"]),
            ),
            color=alt.Color("feature:N"),
            tooltip=[
                alt.Tooltip(
                    "feature",
                    title="Feature",
                ),
                alt.Tooltip("subgroup", title="Subgroup"),
                alt.Tooltip("error", title="Error", format=".2f"),
                alt.Tooltip("prediction", title="Predicted Average", format=".2f"),
            ],
        )
    )

    arrow_chart = arrow_base + arrow_head

    # Add a title to the chart
    arrow_chart = arrow_chart.properties(
        title={
            "text": "Observed vs Predicted Average by Subgroup",
            "subtitle": "Base of the arrow represents Observed Average, Tip represents Predicted Average",
            "fontSize": 16,
            "subtitleFontSize": 12,
        }
    )

    # Configure the chart appearance
    chart = (
        arrow_chart.configure_axis(labelFontSize=12, titleFontSize=14)
        .configure_legend(titleFontSize=12, labelFontSize=12)
        .configure_axisX(labelAngle=45)
    )
    chart = chart.properties(width=800, height=400)

    str_io = StringIO()
    chart.save(str_io, format="html", embed_options={"renderer": "svg"})
    return str_io.getvalue()
