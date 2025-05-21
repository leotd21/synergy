import streamlit as st
import plotly.graph_objects as go

def render_distribution_comparison(original_df, synthetic_df, metadata):
    st.subheader("📊 Distribution Comparison (Categorical Column)")

    # Find first column marked as 'categorical' in metadata
    metadata_dict = metadata.to_dict()["tables"]["table"]
    categorical_cols = [
        col for col, props in metadata_dict["columns"].items()
        if props.get("sdtype") == "categorical"
    ]

    if not categorical_cols:
        st.warning("No categorical columns found in metadata.")
        return

    col = categorical_cols[0]
    st.markdown(f"**Comparing distribution for:** `{col}`")

    orig_counts = original_df[col].value_counts(normalize=True).sort_index()
    synth_counts = synthetic_df[col].value_counts(normalize=True).sort_index()

    all_categories = sorted(set(orig_counts.index).union(set(synth_counts.index)))
    orig_vals = [orig_counts.get(cat, 0) for cat in all_categories]
    synth_vals = [synth_counts.get(cat, 0) for cat in all_categories]

    fig = go.Figure()
    fig.add_trace(go.Bar(x=all_categories, y=orig_vals, name="Original", marker_color="blue"))
    fig.add_trace(go.Bar(x=all_categories, y=synth_vals, name="Synthetic", marker_color="orange"))

    fig.update_layout(
        barmode='group',
        title=f"Distribution Comparison for `{col}`",
        xaxis_title=col,
        yaxis_title="Proportion",
        height=400
    )
    st.plotly_chart(fig, use_container_width=True)
