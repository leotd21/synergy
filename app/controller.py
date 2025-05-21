import streamlit as st
from app import ui, comparator
from services import file_manager, data_generator

def run():
    uploaded_file = ui.upload_file()
    if uploaded_file:
        df = file_manager.read_file(uploaded_file)
        st.session_state["original_df"] = df
        ui.display_dataframe("📊 Original Data", df)

        n_rows = ui.select_num_rows(len(df))
        model_type = ui.select_model()

        if ui.generate_button():
            with st.spinner("Generating data..."):
                try:
                    metadata, synth_df = data_generator.generate(df, n_rows, model_type)
                    st.session_state["synthetic_df"] = synth_df
                    st.session_state["metadata"] = metadata
                    st.success("Synthetic data generated!")

                except Exception as e:
                    st.error(f"Cannot generate data: {e}")
                    return  # prevent further display logic

        # Access persisted data
        original_df = st.session_state.get("original_df")
        synthetic_df = st.session_state.get("synthetic_df")
        metadata = st.session_state.get("metadata")

        if original_df is not None and synthetic_df is not None and metadata is not None:
            ui.display_dataframe("🧬 Synthetic Data", synthetic_df)
            ui.download_button(synthetic_df)
            comparator.render_distribution_comparison(original_df, synthetic_df, metadata)
