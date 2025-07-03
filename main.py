from datetime import datetime, timedelta

import pandas as pd
import streamlit as st

from utils import (
    ANSWER,
    DATE_ADDED,
    ID,
    NEXT_APPEARANCE,
    QUESTION,
    get_next_question,
    load_all_flashcards,
    save_flashcards,
    initialize_question_queue,
)

# -------------- app config ---------------
st.set_page_config(page_title="Flashcards de Símbolos", page_icon="🚀", layout="centered")
st.subheader("Estude os Símbolos!")

# ---------------- SESSION STATE ----------------
if "flashcards_df" not in st.session_state:
    st.session_state.flashcards_df = load_all_flashcards()

# Inicializar a fila de questões randomizadas
if "question_queue" not in st.session_state:
    initialize_question_queue()

# Estado para controlar o expander da resposta
if "show_answer" not in st.session_state:
    st.session_state.show_answer = False

# Estado para rastrear o ID da questão atual
if "current_question_id" not in st.session_state:
    st.session_state.current_question_id = None


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


def reset_answer_state():
    """Reset o estado do mostrar resposta para False"""
    st.session_state.show_answer = False


# ---------------- Main page ----------------

tab1, tab2, tab3, tab4 = st.tabs(["Revisão", "Adicionar", "Buscar", "Ver Todos"])

with tab1:
    try:
        current_row = get_next_question()
        
        if current_row is not None:
            # Se mudou a questão, resetar o estado da resposta
            if st.session_state.current_question_id != current_row[ID]:
                st.session_state.current_question_id = current_row[ID]
                reset_answer_state()
            
            st.image(current_row[QUESTION])
            st.markdown(f"<h4>&mdash; Símbolo nº {current_row[ID]}</h4>", unsafe_allow_html=True)

            # Botão para mostrar/esconder resposta
            if st.button("Mostrar/Esconder Resposta", key="toggle_answer"):
                st.session_state.show_answer = not st.session_state.show_answer

            # Mostrar resposta se o estado estiver ativo
            if st.session_state.show_answer:
                st.markdown(f'<div class="answer"><p>{current_row[ANSWER]}</p></div>', unsafe_allow_html=True)

            next_appearance = None
            col1, col2, col3 = st.columns(3, gap="large")
            with col1:
                easy_submit_button: bool = st.button(label="Fácil", use_container_width=True)
                if easy_submit_button:
                    prev_time_diff = current_row[NEXT_APPEARANCE] - current_row[DATE_ADDED]
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
                update_next_appearance(current_row[ID], next_appearance)
                # Remover a questão atual da fila e resetar o estado da resposta
                if len(st.session_state.question_queue) > 0:
                    st.session_state.question_queue.pop(0)
                reset_answer_state()
                st.info(
                    f"""A próxima aparição deste card será em {next_appearance.date().strftime("%d-%m-%Y")}!""",
                    icon="🎉",
                )
                st.rerun()
        else:
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
