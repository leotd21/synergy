from sdv.single_table import (
    GaussianCopulaSynthesizer,
    CTGANSynthesizer,
    TVAESynthesizer
)
from sdv.metadata import Metadata
import streamlit as st

SYNTHESIZER_MAP = {
    "GaussianCopula": GaussianCopulaSynthesizer,
    "CTGAN": CTGANSynthesizer,
    "TVAE": TVAESynthesizer
}

def generate(data, num_rows, synthesizer_name):
    metadata = Metadata.detect_from_dataframe(data)
    metadata.validate()
    st.info(f"detected metadata: {metadata.to_dict()}", icon="🔥")

    synthesizer_cls = SYNTHESIZER_MAP.get(synthesizer_name, GaussianCopulaSynthesizer)
    synthesizer = synthesizer_cls(metadata)

    synthesizer.fit(data)
    return metadata, synthesizer.sample(num_rows)
