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

    def is_id_like(col):
        return (
            original_df[col].nunique() / total_rows > 0.95
            or original_df[col].dtype == object
            or "id" in col.lower()
        )

    # Filter categorical columns
    categorical_cols = [
        col for col, props in metadata_dict["columns"].items()
        if props.get("sdtype") == "categorical"
        and 2 <= original_df[col].nunique() <= 50
        and not is_datetime(col)
        # and not is_id_like(col)
    ]

    # Filter numerical columns
    numerical_cols = [
        col for col, props in metadata_dict["columns"].items()
        if props.get("sdtype") == "numerical"
        and original_df[col].nunique() / total_rows < 0.9
        and not is_datetime(col)
        # and not is_id_like(col)
    ]

    # Log filtered columns
    st.markdown("### 🧪 Filtered Columns")
    st.markdown(f"**Categorical candidates:** `{categorical_cols}`")
    st.markdown(f"**Numerical candidates:** `{numerical_cols}`")

    # Render comparison for the first available categorical column
    if categorical_cols:
        col = categorical_cols[0]
        st.markdown(f"### 🔤 Categorical Column Comparison: `{col}`")

        orig_counts = original_df[col].value_counts(normalize=True).sort_index()
        synth_counts = synthetic_df[col].value_counts(normalize=True).sort_index()

        all_categories = sorted(set(orig_counts.index).union(set(synth_counts.index)))
        orig_vals = [orig_counts.get(cat, 0) for cat in all_categories]
        synth_vals = [synth_counts.get(cat, 0) for cat in all_categories]

        fig_cat = go.Figure()
        fig_cat.add_trace(go.Bar(x=all_categories, y=orig_vals, name="Original", marker_color="blue"))
        fig_cat.add_trace(go.Bar(x=all_categories, y=synth_vals, name="Synthetic", marker_color="orange"))
        fig_cat.update_layout(
            barmode='group',
            title=f"Distribution Comparison for `{col}`",
            xaxis_title=col,
            yaxis_title="Proportion",
            height=400
        )
        st.plotly_chart(fig_cat, use_container_width=True)
    else:
        st.info("⚠️ No suitable categorical column found for display.")

    # Render comparison for the first available numerical column
    if numerical_cols:
        col = numerical_cols[0]
        st.markdown(f"### 🔢 Numerical Column Comparison: `{col}`")

        original_values = original_df[col].dropna()
        synthetic_values = synthetic_df[col].dropna()

        fig_num = go.Figure()
        fig_num.add_trace(go.Histogram(
            x=original_values,
            name='Original',
            opacity=0.6,
            marker_color='blue',
            nbinsx=30
        ))
        fig_num.add_trace(go.Histogram(
            x=synthetic_values,
            name='Synthetic',
            opacity=0.6,
            marker_color='orange',
            nbinsx=30
        ))
        fig_num.update_layout(
            barmode='overlay',
            title=f"Distribution Comparison for `{col}`",
            xaxis_title=col,
            yaxis_title='Count',
            height=400
        )
        st.plotly_chart(fig_num, use_container_width=True)
    else:
        st.info("⚠️ No suitable numerical column found for display.")
