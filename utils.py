import os
import random
from datetime import datetime, timedelta
from typing import Callable

import pandas as pd
import streamlit as st

DATABASE_CSV = "database.csv"
FLASHCARDS_SYMBOLS_CSV = "flashcards_symbols.csv"

ID = "id"
QUESTION = "question"
ANSWER = "answer"
DATE_ADDED = "date_added"
NEXT_APPEARANCE = "next_appearance"
TAGS = "tags"

N_CARDS_PER_ROW = 2


def get_empty_df():
    return pd.DataFrame(columns=[ID, QUESTION, ANSWER, DATE_ADDED, NEXT_APPEARANCE, TAGS])


def save_flashcards(flashcards_df: pd.DataFrame):
    # Salva o progresso dos flashcards com as datas de próxima aparição
    if not flashcards_df.empty:
        flashcards_df.to_csv(FLASHCARDS_SYMBOLS_CSV, index=False)


def load_all_flashcards():
    # Carrega a base de dados das imagens e denominações
    if os.path.exists(DATABASE_CSV):
        df = pd.read_csv(DATABASE_CSV)
        df[ID] = df.index + 1
        df[DATE_ADDED] = pd.to_datetime(datetime.now())
        df[NEXT_APPEARANCE] = pd.to_datetime(datetime.now() - timedelta(days=1))
        df[TAGS] = "simbolos"
        
        # Se existe um arquivo de progresso, carrega as datas de próxima aparição
        if os.path.exists(FLASHCARDS_SYMBOLS_CSV):
            progress_df = pd.read_csv(FLASHCARDS_SYMBOLS_CSV)
            progress_df[DATE_ADDED] = pd.to_datetime(progress_df[DATE_ADDED])
            progress_df[NEXT_APPEARANCE] = pd.to_datetime(progress_df[NEXT_APPEARANCE])
            
            # Atualiza as datas de próxima aparição baseado no progresso salvo
            for _, progress_row in progress_df.iterrows():
                mask = df[ID] == progress_row[ID]
                if mask.any():
                    df.loc[mask, NEXT_APPEARANCE] = progress_row[NEXT_APPEARANCE]
                    df.loc[mask, DATE_ADDED] = progress_row[DATE_ADDED]
        
        return df
    else:
        return get_empty_df()


def concat_df(df1: pd.DataFrame, df2: pd.DataFrame) -> pd.DataFrame:
    # Se um dos DataFrames estiver vazio, retorna o outro
    if df1.empty:
        return df2
    elif df2.empty:
        return df1
    else:
        return pd.concat([df1, df2], ignore_index=True)


def get_due_flashcards(df: pd.DataFrame) -> pd.DataFrame:
    # Retorna TODOS os flashcards para praticar todos os 84 símbolos a cada sessão
    if len(df) > 0:
        return df.copy()  # Retorna todos os flashcards, não apenas os "due"
    else:
        return get_empty_df()


def initialize_question_queue():
    """Inicializa uma fila de questões em ordem aleatória com TODOS os flashcards"""
    all_questions = st.session_state.flashcards_df
    if not all_questions.empty:
        # Criar uma lista de IDs em ordem aleatória com TODOS os flashcards
        question_ids = all_questions[ID].tolist()
        random.shuffle(question_ids)
        st.session_state.question_queue = question_ids
        print(f"Inicializada fila com {len(question_ids)} questões")  # Debug
    else:
        st.session_state.question_queue = []


def get_next_question():
    """Retorna a próxima questão da fila randomizada"""
    # Se a fila estiver vazia, não há mais questões
    if not hasattr(st.session_state, 'question_queue') or len(st.session_state.question_queue) == 0:
        return None
    
    # Pegar o próximo ID da fila
    next_id = st.session_state.question_queue[0]
    
    # Buscar a linha correspondente no DataFrame
    df = st.session_state.flashcards_df
    matching_rows = df[df[ID] == next_id]
    
    if not matching_rows.empty:
        return matching_rows.iloc[0]
    else:
        # Se por algum motivo o ID não for encontrado, remover da fila e tentar o próximo
        st.session_state.question_queue.pop(0)
        return get_next_question() if len(st.session_state.question_queue) > 0 else None


def prepare_flashcard_df(
    question: str,
    answer: str,
    id: int,
    date_added: datetime,
    next_appearance: datetime,
    tags: list,
) -> pd.DataFrame:
    return pd.DataFrame(
        [
            {
                ID: id,
                QUESTION: question,
                ANSWER: answer,
                DATE_ADDED: date_added,
                NEXT_APPEARANCE: next_appearance,
                TAGS: tags,
            }
        ]
    )


def initialize_hard_questions_only():
    """Inicializa uma fila apenas com os símbolos marcados como difíceis"""
    if hasattr(st.session_state, 'hard_symbols_this_session') and len(st.session_state.hard_symbols_this_session) > 0:
        # Criar fila apenas com IDs dos símbolos difíceis em ordem aleatória
        hard_question_ids = st.session_state.hard_symbols_this_session.copy()
        random.shuffle(hard_question_ids)
        st.session_state.question_queue = hard_question_ids
        print(f"Inicializada fila com {len(hard_question_ids)} símbolos difíceis")  # Debug
    else:
        st.session_state.question_queue = []


def search(text_search: str, df: pd.DataFrame) -> Callable:
    def search_df():
        if df.empty:
            st.warning("O DataFrame está vazio. Não há dados para pesquisar.")
            return

        search_items = df[ANSWER].str.contains(text_search, case=False, na=False)
        matching_rows = df[search_items]
        if matching_rows.empty:
            st.info(f"Nenhum resultado encontrado para '{text_search}'.")
            return

        for n_row, row in matching_rows.reset_index().iterrows():
            i = n_row % N_CARDS_PER_ROW
            if i == 0:
                st.write("---")
                cols = st.columns(N_CARDS_PER_ROW, gap="large")
            with cols[n_row % N_CARDS_PER_ROW]:
                st.caption(f"Símbolo {int(row[ID])}")
                st.image(row[QUESTION])
                with st.expander("Resposta"):
                    st.markdown(f"*{row[ANSWER].strip()}*")

    return search_df


@st.cache_data(ttl=3600)
def convert_df(df):
    return df.to_csv().encode("utf-8")


def view_flashcards(df):
    if not df.empty:
        st.dataframe(
            df,
            use_container_width=True,
            column_order=[QUESTION, ANSWER, ID, DATE_ADDED, NEXT_APPEARANCE, TAGS],
        )
        st.download_button(
            label="Baixar Flashcards",
            data=convert_df(df),
            file_name="flashcards.csv",
            mime="text/csv",
        )
    else:
        st.write("Nenhum flashcard disponível.")
