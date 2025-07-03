import os
from datetime import datetime, timedelta
from typing import Callable

import pandas as pd
import streamlit as st

FLASHCARDS_CSV = "flashcards.csv"

ID = "id"
QUESTION = "question"
ANSWER = "answer"
DATE_ADDED = "date_added"
NEXT_APPEARANCE = "next_appearance"
TAGS = "tags"

N_CARDS_PER_ROW = 2
DEFAULT_TAGS = [
    "cs",
    "dbms",
    "ds/algo",
    "english",
    "linux",
    "ml/dl",
    "os",
    "personal",
    "python",
    "other",
    "vocab",
]


def get_empty_df():
    return pd.DataFrame(columns=[ID, QUESTION, ANSWER, DATE_ADDED, NEXT_APPEARANCE, TAGS])


def save_flashcards(flashcards_df: pd.DataFrame):
    # Mantem a lógica de salvar para o agendamento
    if not flashcards_df.empty:
        flashcards_df.to_csv("flashcards_symbols.csv", index=False)


def load_all_flashcards():
    if os.path.exists("simbolos.csv"):
        df = pd.read_csv("simbolos.csv", header=None, names=[ANSWER])
        df[ID] = df.index + 1
        df[QUESTION] = df[ID].apply(lambda i: f"images/{i}.png")
        df[DATE_ADDED] = pd.to_datetime(datetime.now())
        df[NEXT_APPEARANCE] = pd.to_datetime(datetime.now() - timedelta(days=1))
        df[TAGS] = "simbolos"
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
    if len(df) > 0:
        return df[df[NEXT_APPEARANCE] <= datetime.now()]
    else:
        return get_empty_df()


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


def get_question():
    due_questions = get_due_flashcards(st.session_state.flashcards_df)
    for i, row in due_questions.iterrows():
        yield i, row


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
        st.__cached__
    else:
        st.write("Nenhum flashcard disponível.")
