import streamlit as st
import plotly.graph_objects as go
import pandas as pd

def render_distribution_comparison(original_df, synthetic_df, metadata):
    st.subheader("📊 Distribution Comparison")

    metadata_dict = metadata.to_dict()["tables"]["table"]
    total_rows = len(original_df)

    def is_datetime(col):
        return (
            pd.api.types.is_datetime64_any_dtype(original_df[col])
            or metadata_dict["columns"].get(col, {}).get("sdtype") == "datetime"
        )

    # Filter categorical columns
    categorical_cols = [
        col for col, props in metadata_dict["columns"].items()
        if props.get("sdtype") == "categorical"
        and 2 <= original_df[col].nunique() <= 50
        and not is_datetime(col)
    ]

    # Filter numerical columns (not mostly unique, not datetime)
    numerical_cols = [
        col for col, props in metadata_dict["columns"].items()
        if props.get("sdtype") == "numerical"
        and original_df[col].nunique() / total_rows < 0.9
        and not is_datetime(col)
    ]

    column_types = {
        "Categorical": categorical_cols,
        "Numerical": numerical_cols
    }

    selected_type = st.radio("Select column type:", ["Categorical", "Numerical"])

    if not column_types[selected_type]:
        st.warning(f"No suitable {selected_type.lower()} columns found for comparison.")
        return

    selected_col = st.selectbox(
        f"Select a {selected_type.lower()} column to compare:",
        column_types[selected_type]
    )

    st.markdown(f"**Comparing distribution for:** `{selected_col}`")

    if selected_type == "Categorical":
        orig_counts = original_df[selected_col].value_counts(normalize=True).sort_index()
        synth_counts = synthetic_df[selected_col].value_counts(normalize=True).sort_index()

        all_categories = sorted(set(orig_counts.index).union(set(synth_counts.index)))
        orig_vals = [orig_counts.get(cat, 0) for cat in all_categories]
        synth_vals = [synth_counts.get(cat, 0) for cat in all_categories]

        fig = go.Figure()
        fig.add_trace(go.Bar(x=all_categories, y=orig_vals, name="Original", marker_color="blue"))
        fig.add_trace(go.Bar(x=all_categories, y=synth_vals, name="Synthetic", marker_color="orange"))
        fig.update_layout(
            barmode='group',
            title=f"Distribution Comparison for `{selected_col}`",
            xaxis_title=selected_col,
            yaxis_title="Proportion",
            height=400
        )

    else:  # Numerical
        original_values = original_df[selected_col].dropna()
        synthetic_values = synthetic_df[selected_col].dropna()

        fig = go.Figure()
        fig.add_trace(go.Histogram(
            x=original_values,
            name='Original',
            opacity=0.6,
            marker_color='blue',
            nbinsx=30
        ))
        fig.add_trace(go.Histogram(
            x=synthetic_values,
            name='Synthetic',
            opacity=0.6,
            marker_color='orange',
            nbinsx=30
        ))
        fig.update_layout(
            barmode='overlay',
            title=f"Distribution Comparison for `{selected_col}`",
            xaxis_title=selected_col,
            yaxis_title='Count',
            height=400
        )

    st.plotly_chart(fig, use_container_width=True)
