import json

import streamlit as st
from streamlit_annotation_tools import text_labeler


def labeler_page():
    st.title("NER Annotator")
    with st.expander("Rotular Parágrafos", expanded=True):
        if 'json_data' not in st.session_state:
            return  # Se não houver dados, não faça nada

        annotations = st.session_state.json_data.get('annotations', [])
        if 'current_index' not in st.session_state:
            st.session_state.current_index = 0  # Initialize current index
            # Initialize review status
            st.session_state.reviewed = [False] * len(annotations)

        current_index = st.session_state.current_index
        if annotations:
            current_annotation = annotations[current_index]
            text = current_annotation[0]
            entities_info = current_annotation[1]
            entities = entities_info.get(
                'entities', entities_info.get('incorrect_spans', []))

            labels_dict = {}
            for ent in entities:
                start, end, label = ent
                if label not in labels_dict:
                    labels_dict[label] = []
                labels_dict[label].append(
                    {"start": start, "end": end, "label": text[start:end]})

            updated_labels = text_labeler(text, labels_dict)

            # Navigation buttons and go-to index input
            col1, col2, col3, col4 = st.columns([0.85, 5, 0.5, 0.5])

            with col1:
                jump_to_index = st.number_input(f'Ir para texto: {current_index + 1} de {len(annotations)}', min_value=1, max_value=len(
                    annotations), value=current_index+1)
                if jump_to_index - 1 != current_index:
                    st.session_state.current_index = jump_to_index - 1
                    st.experimental_rerun()

            with col2:
                # Use a unique key for the checkbox based on current_index
                reviewed = st.checkbox(
                    "Marcar como revisado", value=st.session_state.reviewed[current_index], key=f"reviewed_{current_index}")
                st.session_state.reviewed[current_index] = reviewed

            with col3:
                if st.button('Salvar', key='save'):
                    if updated_labels:
                        new_entities = [[label_dict['start'], label_dict['end'], key]
                                        for key, lst in updated_labels.items() for label_dict in lst]
                        annotations[current_index][1]['entities'] = new_entities
                    st.session_state.json_data['annotations'] = annotations
                    st.success("Sucesso!")

            with col4:
                st.download_button(
                    label="Baixar",
                    data=json.dumps(st.session_state.json_data, indent=2),
                    file_name='updated_annotations.json',
                    mime='application/json'
                )


if __name__ == "__main__":
    st.set_page_config(layout="wide")
    with st.sidebar:
        uploaded_file = st.file_uploader(
            "Procurar arquivo JSON", type=['json'])
        if uploaded_file is not None and 'json_data' not in st.session_state:
            data = json.load(uploaded_file)
            st.session_state.json_data = data

    labeler_page()
