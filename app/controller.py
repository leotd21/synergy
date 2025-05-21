import streamlit as st
from app import ui, comparator
from services import file_manager, data_generator

def run():
    uploaded_file = ui.upload_file()

    # Check if a new file is uploaded → clear old synthetic data
    if uploaded_file:
        filename = uploaded_file.name
        if st.session_state.get("last_uploaded") != filename:
            st.session_state["synth_df"] = None
            st.session_state["metadata"] = None
            st.session_state["last_uploaded"] = filename
            st.info(f"New file uploaded: `{filename}`. Previous synthetic data cleared.")

        df = file_manager.read_file(uploaded_file)
        ui.display_dataframe("📊 Original Data", df)

        n_rows = ui.select_num_rows(len(df))
        model_type = ui.select_model()

        if ui.generate_button():
            with st.spinner("Generating data..."):
                try:
                    metadata, synth_df = data_generator.generate(df, n_rows, model_type)
                    st.session_state["synth_df"] = synth_df
                    st.session_state["metadata"] = metadata
                    st.success("✅ Synthetic data generated!")
                except Exception as e:
                    st.error(f"❌ Cannot generate data: {e}")
                    return

        # Only display if generation has happened
        if st.session_state.get("synth_df") is not None:
            ui.display_dataframe("🧬 Synthetic Data", st.session_state["synth_df"])
            ui.download_button(st.session_state["synth_df"])
            comparator.render_distribution_comparison(
                df, st.session_state["synth_df"], st.session_state["metadata"]
            )
