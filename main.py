from datetime import datetime, timedelta

import pandas as pd
import streamlit as st

from utils import (
    ANSWER,
    DATE_ADDED,
    ID,
    NEXT_APPEARANCE,
    QUESTION,
    get_question,
    load_all_flashcards,
    save_flashcards,
)

# -------------- app config ---------------
st.set_page_config(page_title="Flashcards de Símbolos", page_icon="🚀", layout="centered")
st.subheader("Estude os Símbolos!")

# ---------------- SESSION STATE ----------------
if "flashcards_df" not in st.session_state:
    st.session_state.flashcards_df = load_all_flashcards()


# external css
def local_css(file_name: str):
    with open(file_name) as f:
        st.markdown(f"<style>{f.read()}</style>", unsafe_allow_html=True)


local_css("style.css")


def update_next_appearance(id: int, next_appearance: datetime):
    if next_appearance is not None:
        st.session_state.flashcards_df.loc[
            st.session_state.flashcards_df[ID] == id, NEXT_APPEARANCE
        ] = next_appearance
        save_flashcards(st.session_state.flashcards_df)


# ---------------- Main page ----------------

tab1, tab2, tab3, tab4 = st.tabs(["Revisão", "Adicionar", "Buscar", "Ver Todos"])

with tab1:
    try:
        q_no, row = next(get_question())
        st.image(row[QUESTION])
        st.markdown(f"<h4>&mdash; Símbolo nº {row[ID]}</h4>", unsafe_allow_html=True)

        with st.expander("Mostrar Resposta"):
            st.write(row[ANSWER])

        next_appearance = None
        col1, col2, col3 = st.columns(3, gap="large")
        with col1:
            easy_submit_button: bool = st.button(label="Fácil", use_container_width=True)
            if easy_submit_button:
                prev_time_diff = row[NEXT_APPEARANCE] - row[DATE_ADDED]
                next_appearance_days = min(prev_time_diff.days + 2, 60)
                next_appearance = datetime.now() + timedelta(days=next_appearance_days)
        with col2:
            medium_submit_button: bool = st.button(
                label="Médio", use_container_width=True
            )
            if medium_submit_button:
                next_appearance = datetime.now() + timedelta(days=2)
        with col3:
            hard_submit_button: bool = st.button(label="Difícil", use_container_width=True)
            if hard_submit_button:
                next_appearance = datetime.now() + timedelta(days=1)

        if next_appearance is not None:
            update_next_appearance(row[ID], next_appearance)
            st.info(
                f"""A próxima aparição deste card será em {next_appearance.date().strftime("%d-%m-%Y")}!""",
                icon="🎉",
            )
            st.rerun()
    except StopIteration:
        st.info("Parabéns! Você completou todos os flashcards. Bom trabalho!", icon="🙌")
    except FileNotFoundError:
        st.error("Erro: Verifique se as imagens estão na pasta 'images' e se o arquivo 'database.csv' está no diretório correto.")
    except Exception as e:
        st.error(f"Erro ao carregar flashcard: {str(e)}")


with tab2:
    st.info("A funcionalidade de adicionar novos flashcards foi desativada nesta versão.")

with tab3:
    st.info("A funcionalidade de busca foi desativada nesta versão.")

with tab4:
    st.info("A funcionalidade de visualizar todos os flashcards foi desativada nesta versão.")
