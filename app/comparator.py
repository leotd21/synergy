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
    ]

    # Filter numerical columns
    numerical_cols = [
        col for col, props in metadata_dict["columns"].items()
        if props.get("sdtype") == "numerical"
        and not is_datetime(col)
    ]

    # Log filtered columns
    st.markdown("### 🧪 Filtered Columns")
    st.markdown(f"**Categorical candidates:** `{categorical_cols}`")
    st.markdown(f"**Numerical candidates:** `{numerical_cols}`")

    # ---- Categorical Comparison ----
    if categorical_cols:
        st.markdown("### 🔤 Categorical Column Comparison")
        selected_cat = st.selectbox("Select a categorical column:", categorical_cols, key="cat_col")

        orig_counts = original_df[selected_cat].value_counts(normalize=True).sort_index()
        synth_counts = synthetic_df[selected_cat].value_counts(normalize=True).sort_index()

        all_categories = sorted(set(orig_counts.index).union(set(synth_counts.index)))
        orig_vals = [orig_counts.get(cat, 0) for cat in all_categories]
        synth_vals = [synth_counts.get(cat, 0) for cat in all_categories]

        fig_cat = go.Figure()
        fig_cat.add_trace(go.Bar(x=all_categories, y=orig_vals, name="Original", marker_color="blue"))
        fig_cat.add_trace(go.Bar(x=all_categories, y=synth_vals, name="Synthetic", marker_color="orange"))
        fig_cat.update_layout(
            barmode='group',
            title=f"Distribution Comparison for `{selected_cat}`",
            xaxis_title=selected_cat,
            yaxis_title="Proportion",
            height=400
        )
        st.plotly_chart(fig_cat, use_container_width=True)
    else:
        st.info("⚠️ No suitable categorical columns available.")

    # ---- Numerical Comparison ----
    if numerical_cols:
        st.markdown("### 🔢 Numerical Column Comparison")
        selected_num = st.selectbox("Select a numerical column:", numerical_cols, key="num_col")

        original_values = original_df[selected_num].dropna()
        synthetic_values = synthetic_df[selected_num].dropna()

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
            title=f"Distribution Comparison for `{selected_num}`",
            xaxis_title=selected_num,
            yaxis_title='Count',
            height=400
        )
        st.plotly_chart(fig_num, use_container_width=True)
    else:
        st.info("⚠️ No suitable numerical columns available.")
