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

# Estados para estatísticas e progresso
if "session_stats" not in st.session_state:
    st.session_state.session_stats = {
        "total_questions": 0,
        "answered": 0,
        "easy": 0,
        "medium": 0,
        "hard": 0
    }

# Inicializar contagem total de questões disponíveis
if "total_due_questions" not in st.session_state:
    # Usar TODOS os flashcards em cada sessão (84 símbolos)
    st.session_state.total_due_questions = len(st.session_state.flashcards_df)
    st.session_state.session_stats["total_questions"] = st.session_state.total_due_questions


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


def update_session_stats(difficulty: str):
    """Atualiza as estatísticas da sessão"""
    st.session_state.session_stats["answered"] += 1
    st.session_state.session_stats[difficulty] += 1


def reset_session():
    """Reinicia toda a sessão de estudo"""
    # Limpar os estados da sessão
    for key in ['question_queue', 'show_answer', 'current_question_id', 'session_stats', 'total_due_questions']:
        if key in st.session_state:
            del st.session_state[key]
    
    # Reinicializar estatísticas
    st.session_state.session_stats = {
        "total_questions": 0,
        "answered": 0,
        "easy": 0,
        "medium": 0,
        "hard": 0
    }
    
    # Reinicializar contagem total com TODOS os flashcards
    st.session_state.total_due_questions = len(st.session_state.flashcards_df)
    st.session_state.session_stats["total_questions"] = st.session_state.total_due_questions
    
    # Reinicializar outros estados
    st.session_state.show_answer = False
    st.session_state.current_question_id = None
    
    # Inicializar nova fila de questões randomizada
    initialize_question_queue()


# ---------------- Main page ----------------

st.markdown("## 🔥 Revisão de Símbolos de Segurança")
st.markdown("---")
# Mostrar barra de progresso e estatísticas
if st.session_state.total_due_questions > 0:
    progress = st.session_state.session_stats["answered"] / st.session_state.session_stats["total_questions"]
    
    # Barra de progresso
    st.progress(progress, text=f"Progresso: {st.session_state.session_stats['answered']}/{st.session_state.session_stats['total_questions']} símbolos")
    
    # Estatísticas em tempo real
    col1, col2, col3, col4 = st.columns(4)
    with col1:
        st.metric("📊 Respondidos", st.session_state.session_stats["answered"])
    with col2:
        st.metric("😊 Fácil", st.session_state.session_stats["easy"], delta=None, delta_color="normal")
    with col3:
        st.metric("😐 Médio", st.session_state.session_stats["medium"], delta=None, delta_color="normal")
    with col4:
        st.metric("😰 Difícil", st.session_state.session_stats["hard"], delta=None, delta_color="normal")
    
    st.markdown("---")

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
        difficulty_selected = None
        
        col1, col2, col3 = st.columns(3, gap="large")
        with col1:
            easy_submit_button: bool = st.button(label="😊 Fácil", use_container_width=True)
            if easy_submit_button:
                prev_time_diff = current_row[NEXT_APPEARANCE] - current_row[DATE_ADDED]
                next_appearance_days = min(prev_time_diff.days + 2, 60)
                next_appearance = datetime.now() + timedelta(days=next_appearance_days)
                difficulty_selected = "easy"
        with col2:
            medium_submit_button: bool = st.button(
                label="😐 Médio", use_container_width=True
            )
            if medium_submit_button:
                next_appearance = datetime.now() + timedelta(days=2)
                difficulty_selected = "medium"
        with col3:
            hard_submit_button: bool = st.button(label="😰 Difícil", use_container_width=True)
            if hard_submit_button:
                next_appearance = datetime.now() + timedelta(days=1)
                difficulty_selected = "hard"

        if next_appearance is not None and difficulty_selected is not None:
            update_next_appearance(current_row[ID], next_appearance)
            update_session_stats(difficulty_selected)
            
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
        # Sessão completa - mostrar estatísticas finais
        st.balloons()
        st.success("🎉 Parabéns! Você completou todos os flashcards!", icon="🏆")
        
        # Estatísticas detalhadas finais
        st.markdown("## 📊 Relatório da Sessão")
        
        total_answered = st.session_state.session_stats["answered"]
        easy_count = st.session_state.session_stats["easy"]
        medium_count = st.session_state.session_stats["medium"]
        hard_count = st.session_state.session_stats["hard"]
        
        # Métricas principais
        col1, col2, col3, col4 = st.columns(4)
        with col1:
            st.metric("Total Respondidos", total_answered)
        with col2:
            easy_pct = (easy_count / total_answered * 100) if total_answered > 0 else 0
            st.metric("😊 Fácil", f"{easy_count} ({easy_pct:.1f}%)")
        with col3:
            medium_pct = (medium_count / total_answered * 100) if total_answered > 0 else 0
            st.metric("😐 Médio", f"{medium_count} ({medium_pct:.1f}%)")
        with col4:
            hard_pct = (hard_count / total_answered * 100) if total_answered > 0 else 0
            st.metric("😰 Difícil", f"{hard_count} ({hard_pct:.1f}%)")
        
        # Gráfico de barras das estatísticas
        import pandas as pd
        chart_data = pd.DataFrame({
            'Dificuldade': ['Fácil', 'Médio', 'Difícil'],
            'Quantidade': [easy_count, medium_count, hard_count],
            'Percentual': [easy_pct, medium_pct, hard_pct]
        })
        
        st.markdown("### 📈 Distribuição das Respostas")
        st.bar_chart(chart_data.set_index('Dificuldade')['Quantidade'])
        
        # Análise do desempenho
        st.markdown("### 🎯 Análise do Desempenho")
        
        if easy_pct >= 70:
            st.success("🌟 Excelente! Você domina bem os símbolos de segurança!")
        elif easy_pct >= 50:
            st.info("👍 Bom trabalho! Continue praticando para melhorar ainda mais.")
        elif hard_pct >= 50:
            st.warning("📚 Foque mais no estudo - muitos símbolos precisam de mais atenção.")
        else:
            st.info("💪 Continue praticando! A repetição é a chave do aprendizado.")
        
        # Botão para nova sessão
        st.markdown("---")
        if st.button("🔄 Iniciar Nova Sessão de Estudo", use_container_width=True, key="new_session_btn"):
            reset_session()
            st.rerun()
            
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
