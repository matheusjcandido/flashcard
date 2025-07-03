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
    initialize_hard_questions_only,
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

# Lista para rastrear IDs dos símbolos marcados como difíceis nesta sessão
if "hard_symbols_this_session" not in st.session_state:
    st.session_state.hard_symbols_this_session = []

# Tipo de sessão (completa ou apenas difíceis)
if "session_type" not in st.session_state:
    st.session_state.session_type = "complete"  # "complete" ou "hard_only"

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


def update_session_stats(difficulty: str, symbol_id: int):
    """Atualiza as estatísticas da sessão"""
    try:
        st.session_state.session_stats["answered"] += 1
        st.session_state.session_stats[difficulty] += 1
        
        # Se marcado como difícil, adicionar à lista de símbolos difíceis desta sessão
        if difficulty == "hard" and symbol_id not in st.session_state.hard_symbols_this_session:
            st.session_state.hard_symbols_this_session.append(symbol_id)
    except Exception as e:
        st.error(f"Erro ao atualizar estatísticas: {str(e)}")
        # Reinicializar estatísticas se houver erro
        st.session_state.session_stats = {
            "total_questions": st.session_state.total_due_questions,
            "answered": 1,
            "easy": 1 if difficulty == "easy" else 0,
            "medium": 1 if difficulty == "medium" else 0,
            "hard": 1 if difficulty == "hard" else 0
        }


def reset_session():
    """Reinicia toda a sessão de estudo"""
    # Limpar os estados da sessão
    for key in ['question_queue', 'show_answer', 'current_question_id', 'session_stats', 'total_due_questions', 'hard_symbols_this_session', 'session_type']:
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
    
    # Reinicializar outros estados
    st.session_state.hard_symbols_this_session = []
    st.session_state.session_type = "complete"
    st.session_state.show_answer = False
    st.session_state.current_question_id = None
    
    # Reinicializar contagem total com TODOS os flashcards
    st.session_state.total_due_questions = len(st.session_state.flashcards_df)
    st.session_state.session_stats["total_questions"] = st.session_state.total_due_questions
    
    # Inicializar nova fila de questões randomizada
    initialize_question_queue()


def start_hard_only_session():
    """Inicia uma sessão apenas com os símbolos marcados como difíceis"""
    if len(st.session_state.hard_symbols_this_session) == 0:
        st.warning("Nenhum símbolo foi marcado como difícil nesta sessão!")
        return
    
    # Limpar estados atuais (exceto hard_symbols_this_session)
    for key in ['question_queue', 'show_answer', 'current_question_id', 'session_stats', 'total_due_questions']:
        if key in st.session_state:
            del st.session_state[key]
    
    # Configurar para sessão apenas difíceis
    st.session_state.session_type = "hard_only"
    st.session_state.show_answer = False
    st.session_state.current_question_id = None
    
    # Reinicializar estatísticas
    st.session_state.session_stats = {
        "total_questions": len(st.session_state.hard_symbols_this_session),
        "answered": 0,
        "easy": 0,
        "medium": 0,
        "hard": 0
    }
    
    st.session_state.total_due_questions = len(st.session_state.hard_symbols_this_session)
    
    # Inicializar fila apenas com símbolos difíceis
    initialize_hard_questions_only()


# ---------------- Main page ----------------

st.markdown("## 🔥 Revisão de Símbolos de Segurança")

# Mostrar tipo de sessão
if st.session_state.session_type == "hard_only":
    st.markdown("### 🎯 **Sessão: Apenas Símbolos Difíceis**")
    st.info(f"Revisando {len(st.session_state.hard_symbols_this_session)} símbolos marcados como difíceis na sessão anterior.")
else:
    st.markdown("### 📚 **Sessão: Todos os Símbolos**")

st.markdown("---")

# Mostrar barra de progresso e estatísticas
if st.session_state.total_due_questions > 0:
    # Calcular progresso com validação
    answered = st.session_state.session_stats["answered"]
    total = st.session_state.session_stats["total_questions"]
    
    if total > 0:
        progress = answered / total
        # Garantir que o progresso esteja entre 0 e 1
        progress = max(0.0, min(1.0, progress))
    else:
        progress = 0.0
    
    # Barra de progresso
    st.progress(progress, text=f"Progresso: {answered}/{total} símbolos")
    
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
            update_session_stats(difficulty_selected, current_row[ID])
            
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
        try:
            st.balloons()
            st.success("🎉 Parabéns! Você completou todos os flashcards!", icon="🏆")
            
            # Estatísticas detalhadas finais
            st.markdown("## 📊 Relatório da Sessão")
            
            # Validar valores das estatísticas
            total_answered = max(1, st.session_state.session_stats.get("answered", 1))  # Evitar divisão por zero
            easy_count = st.session_state.session_stats.get("easy", 0)
            medium_count = st.session_state.session_stats.get("medium", 0)
            hard_count = st.session_state.session_stats.get("hard", 0)
            
            # Garantir que os valores sejam consistentes
            if easy_count + medium_count + hard_count != total_answered:
                # Se houver inconsistência, ajustar
                total_answered = easy_count + medium_count + hard_count
                if total_answered == 0:
                    total_answered = 1
            
            # Métricas principais
            col1, col2, col3, col4 = st.columns(4)
            with col1:
                st.metric("Total Respondidos", total_answered)
            with col2:
                easy_pct = (easy_count / total_answered * 100) if total_answered > 0 else 0
                easy_pct = max(0, min(100, easy_pct))  # Garantir que esteja entre 0 e 100
                st.metric("😊 Fácil", f"{easy_count} ({easy_pct:.1f}%)")
            with col3:
                medium_pct = (medium_count / total_answered * 100) if total_answered > 0 else 0
                medium_pct = max(0, min(100, medium_pct))  # Garantir que esteja entre 0 e 100
                st.metric("😐 Médio", f"{medium_count} ({medium_pct:.1f}%)")
            with col4:
                hard_pct = (hard_count / total_answered * 100) if total_answered > 0 else 0
                hard_pct = max(0, min(100, hard_pct))  # Garantir que esteja entre 0 e 100
                st.metric("😰 Difícil", f"{hard_count} ({hard_pct:.1f}%)")
            
            # Gráfico de barras das estatísticas
            chart_data = pd.DataFrame({
                'Dificuldade': ['Fácil', 'Médio', 'Difícil'],
                'Quantidade': [easy_count, medium_count, hard_count],
                'Percentual': [easy_pct, medium_pct, hard_pct]
            })
            
            st.markdown("### 📈 Distribuição das Respostas")
            if chart_data['Quantidade'].sum() > 0:  # Só mostrar gráfico se houver dados
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
            
            # Informação sobre símbolos difíceis
            if len(st.session_state.hard_symbols_this_session) > 0:
                st.markdown("### 🎯 Símbolos que Precisam de Mais Atenção")
                st.warning(f"Você marcou **{len(st.session_state.hard_symbols_this_session)} símbolos** como difíceis nesta sessão.")
                st.info("💡 **Dica:** Pratique apenas esses símbolos para melhorar mais rapidamente!")
            
            # Botões para próximas ações
            st.markdown("---")
            st.markdown("### 🚀 Próximos Passos")
            
            col1, col2 = st.columns(2)
            
            with col1:
                # Botão para estudar apenas os difíceis (só aparece se houver símbolos difíceis)
                if len(st.session_state.hard_symbols_this_session) > 0:
                    if st.button("🎯 Estudar Apenas os Difíceis", use_container_width=True, key="hard_only_btn", type="secondary"):
                        start_hard_only_session()
                        st.rerun()
                else:
                    st.info("🎉 Nenhum símbolo foi marcado como difícil!")
            
            with col2:
                # Botão para nova sessão completa
                if st.button("🔄 Iniciar Nova Sessão Completa", use_container_width=True, key="new_session_btn", type="primary"):
                    reset_session()
                    st.rerun()
                    
        except Exception as e:
            st.error("Erro ao gerar relatório final. Reiniciando sessão...")
            reset_session()
            st.rerun()
            
except FileNotFoundError:
    st.error("Erro: Verifique se as imagens estão na pasta 'images' e se o arquivo 'database.csv' está no diretório correto.")
except Exception as e:
    st.error(f"Erro ao carregar flashcard: {str(e)}")
    st.info("Tentando reiniciar a sessão...")
    try:
        reset_session()
        st.rerun()
    except:
        st.error("Erro crítico. Recarregue a página.")
