import streamlit as st
import requests
import pandas as pd
import time
import json
from datetime import datetime
import plotly.express as px
import plotly.graph_objects as go

# Configuração da página
st.set_page_config(
    page_title="LinkedIn Lead Generator",
    page_icon="🎯",
    layout="wide",
    initial_sidebar_state="expanded"
)

# CSS customizado
st.markdown("""
<style>
    .main-header {
        font-size: 2.5rem;
        font-weight: bold;
        color: #0e76a8;
        text-align: center;
        margin-bottom: 2rem;
    }
    .metric-card {
        background: linear-gradient(90deg, #667eea 0%, #764ba2 100%);
        padding: 1rem;
        border-radius: 10px;
        color: white;
        text-align: center;
        margin: 0.5rem 0;
    }
    .success-msg {
        background-color: #d4edda;
        border: 1px solid #c3e6cb;
        color: #155724;
        padding: 1rem;
        border-radius: 5px;
        margin: 1rem 0;
    }
</style>
""", unsafe_allow_html=True)

# Header principal
st.markdown('<h1 class="main-header">🎯 LinkedIn Lead Generator</h1>', unsafe_allow_html=True)

# Sidebar - Configurações
st.sidebar.header("⚙️ Configurações")

# URL do seu webhook N8N (substitua pela sua)
webhook_url = st.sidebar.text_input(
    "🔗 URL do Webhook N8N", 
    value="https://n8n.srv845413.hstgr.cloud/webhook-test/linkedin-search",
    help="Cole aqui a URL do seu webhook do N8N"
)

st.sidebar.markdown("---")

# Configurações de busca
st.sidebar.subheader("🔍 Parâmetros de Busca")

# Termos executivos
executive_terms = st.sidebar.multiselect(
    "Cargos Executivos",
    ["CEO", "founder", "director", "owner", "presidente", "sócio", "empreendedor"],
    default=["CEO", "founder", "director"]
)

# Localização
location = st.sidebar.selectbox(
    "Localização",
    ["Brasil", "São Paulo", "Rio de Janeiro", "Belo Horizonte", "Porto Alegre", "Salvador"],
    index=0
)

# Número de resultados
num_results = st.sidebar.slider("Número de Resultados", 5, 20, 10)

# Página inicial (para variar resultados)
start_page = st.sidebar.number_input("Página Inicial", 0, 50, 0)

st.sidebar.markdown("---")

# Área principal dividida em tabs
tab1, tab2, tab3, tab4 = st.tabs(["🚀 Buscar Leads", "📊 Resultados", "📈 Analytics", "📋 Histórico"])

# Inicializar session state
if 'leads_data' not in st.session_state:
    st.session_state.leads_data = []
if 'search_history' not in st.session_state:
    st.session_state.search_history = []
if 'is_searching' not in st.session_state:
    st.session_state.is_searching = False

# TAB 1: Buscar Leads
with tab1:
    st.header("🔍 Nova Busca de Leads")
    
    col1, col2 = st.columns([2, 1])
    
    with col1:
        st.subheader("Configuração da Busca")
        
        # Preview da query
        query_terms = " OR ".join(executive_terms)
        query_preview = f"site:linkedin.com/in ({query_terms}) {location}"
        
        st.code(f"Query: {query_preview}", language="text")
        
        # Informações da busca
        st.info(f"""
        **Configuração Atual:**
        - 🎯 Cargos: {', '.join(executive_terms)}
        - 📍 Local: {location}
        - 📊 Resultados: {num_results}
        - 📄 Página: {start_page}
        """)
    
    with col2:
        st.subheader("Ações")
        
        # Botão de busca
        if st.button("🚀 Iniciar Busca", type="primary", use_container_width=True):
            if not webhook_url:
                st.error("❌ Configure a URL do webhook primeiro!")
            else:
                st.session_state.is_searching = True
                
                # Payload para o N8N
                payload = {
                    "query": query_preview,
                    "num_results": num_results,
                    "start_page": start_page,
                    "location": location,
                    "executive_terms": executive_terms
                }
                
                # Progress bar
                progress_bar = st.progress(0)
                status_text = st.empty()
                
                try:
                    status_text.text("📡 Enviando requisição para N8N...")
                    progress_bar.progress(25)
                    
                    # Chamada para o N8N
                    response = requests.post(webhook_url, json=payload, timeout=300)
                    progress_bar.progress(50)
                    
                    if response.status_code == 200:
                        status_text.text("✅ Processando resultados...")
                        progress_bar.progress(75)
                        
                        # Simular delay de processamento
                        time.sleep(2)
                        
                        # Parse da resposta
                        result_data = response.json()
                        progress_bar.progress(100)
                        
                        # Ajustar para o formato do N8N Aggregate
                        if 'leads' in result_data:
                            leads = result_data['leads']
                            # Se leads é um objeto com 'data', extrair o array
                            if isinstance(leads, dict) and 'data' in leads:
                                leads = leads['data']
                            # Se leads não é uma lista, transformar em lista
                            elif not isinstance(leads, list):
                                leads = [leads]
                        else:
                            leads = []
                        
                        # Salvar no session state
                        st.session_state.leads_data = leads
                        
                        # Adicionar ao histórico
                        st.session_state.search_history.append({
                            'timestamp': datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                            'query': query_preview,
                            'results_count': len(leads),
                            'location': location
                        })
                        
                        status_text.markdown(f'<div class="success-msg">✅ Busca concluída! Encontrados {len(leads)} leads.</div>', unsafe_allow_html=True)
                        progress_bar.empty()
                        
                    else:
                        st.error(f"❌ Erro na requisição: {response.status_code}")
                        
                except requests.exceptions.RequestException as e:
                    st.error(f"❌ Erro de conexão: {str(e)}")
                
                st.session_state.is_searching = False
        
        # Botão de exemplo (para demonstração)
        if st.button("📋 Carregar Dados de Exemplo", use_container_width=True):
            # Dados de exemplo para demonstração
            st.session_state.leads_data = [
                {
                    "titulo": "João Silva - CEO Tech Innovations",
                    "link": "https://linkedin.com/in/joao-silva-ceo",
                    "resumo": "CEO da Tech Innovations com 10+ anos de experiência em tecnologia",
                    "analise": "ALTO POTENCIAL - CEO de empresa de tecnologia, decisor principal, ótimo fit para serviços de marketing digital.",
                    "potencial": "ALTO"
                },
                {
                    "titulo": "Maria Santos - Founder StartupXYZ", 
                    "link": "https://linkedin.com/in/maria-santos-founder",
                    "resumo": "Founder e CEO da StartupXYZ, empresa de e-commerce em crescimento",
                    "analise": "MÉDIO POTENCIAL - Founder de startup, pode ter orçamento limitado mas interesse em crescimento.",
                    "potencial": "MÉDIO"
                },
                {
                    "titulo": "Carlos Costa - Director Financeiro",
                    "link": "https://linkedin.com/in/carlos-costa-cfo", 
                    "resumo": "CFO em empresa multinacional, especialista em gestão financeira",
                    "analise": "BAIXO POTENCIAL - Foco em área financeira, pouco provável interesse direto em marketing.",
                    "potencial": "BAIXO"
                }
            ]
            st.success("✅ Dados de exemplo carregados!")

# TAB 2: Resultados
with tab2:
    st.header("📊 Resultados da Busca")
    
    if st.session_state.leads_data:
        # Métricas resumo
        col1, col2, col3, col4 = st.columns(4)
        
        # Calcular estatísticas
        total_leads = len(st.session_state.leads_data)
        alto_potencial = len([l for l in st.session_state.leads_data if 'ALTO' in l.get('analise', '')])
        medio_potencial = len([l for l in st.session_state.leads_data if 'MÉDIO' in l.get('analise', '')])
        baixo_potencial = total_leads - alto_potencial - medio_potencial
        
        with col1:
            st.metric("Total de Leads", total_leads, "🎯")
        with col2:
            st.metric("Alto Potencial", alto_potencial, "🔥")
        with col3:
            st.metric("Médio Potencial", medio_potencial, "⚡")
        with col4:
            st.metric("Baixo Potencial", baixo_potencial, "📊")
        
        # Filtros
        st.subheader("🔍 Filtrar Resultados")
        col1, col2 = st.columns(2)
        
        with col1:
            potencial_filter = st.selectbox(
                "Filtrar por Potencial",
                ["Todos", "Alto Potencial", "Médio Potencial", "Baixo Potencial"]
            )
        
        with col2:
            search_filter = st.text_input("🔍 Buscar por nome/empresa")
        
        # Aplicar filtros
        filtered_data = st.session_state.leads_data.copy()
        
        if potencial_filter != "Todos":
            if potencial_filter == "Alto Potencial":
                filtered_data = [l for l in filtered_data if 'ALTO' in l.get('analise', '')]
            elif potencial_filter == "Médio Potencial":
                filtered_data = [l for l in filtered_data if 'MÉDIO' in l.get('analise', '')]
            elif potencial_filter == "Baixo Potencial":
                filtered_data = [l for l in filtered_data if 'ALTO' not in l.get('analise', '') and 'MÉDIO' not in l.get('analise', '')]
        
        if search_filter:
            filtered_data = [l for l in filtered_data if search_filter.lower() in l.get('titulo', '').lower()]
        
        # Exibir resultados
        st.subheader(f"📋 Leads Encontrados ({len(filtered_data)})")
        
        for i, lead in enumerate(filtered_data):
            with st.expander(f"👤 {lead.get('titulo', 'N/A')}", expanded=False):
                col1, col2 = st.columns([2, 1])
                
                with col1:
                    st.write(f"**🔗 Link:** {lead.get('link', 'N/A')}")
                    st.write(f"**📝 Resumo:** {lead.get('resumo', 'N/A')}")
                    st.write(f"**🤖 Análise IA:** {lead.get('analise', 'N/A')}")
                
                with col2:
                    # Determinar cor do potencial
                    potencial_color = "🔥" if "ALTO" in lead.get('analise', '') else "⚡" if "MÉDIO" in lead.get('analise', '') else "📊"
                    st.markdown(f"### {potencial_color} Potencial")
                    
                    if st.button(f"📩 Contactar", key=f"contact_{i}"):
                        st.info("Funcionalidade de contato em desenvolvimento!")
        
        # Botão de export
        if st.button("📥 Exportar para CSV"):
            df = pd.DataFrame(filtered_data)
            csv = df.to_csv(index=False)
            st.download_button(
                label="⬇️ Download CSV",
                data=csv,
                file_name=f"leads_linkedin_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv",
                mime="text/csv"
            )
    else:
        st.info("🔍 Nenhum resultado encontrado. Execute uma busca primeiro!")

# TAB 3: Analytics
with tab3:
    st.header("📈 Analytics e Insights")
    
    if st.session_state.leads_data:
        # Gráfico de distribuição por potencial
        potencial_counts = {
            'Alto': len([l for l in st.session_state.leads_data if 'ALTO' in l.get('analise', '')]),
            'Médio': len([l for l in st.session_state.leads_data if 'MÉDIO' in l.get('analise', '')]),
            'Baixo': len(st.session_state.leads_data) - len([l for l in st.session_state.leads_data if 'ALTO' in l.get('analise', '') or 'MÉDIO' in l.get('analise', '')])
        }
        
        col1, col2 = st.columns(2)
        
        with col1:
            # Gráfico de pizza
            fig_pie = px.pie(
                values=list(potencial_counts.values()),
                names=list(potencial_counts.keys()),
                title="Distribuição por Potencial",
                color_discrete_map={'Alto': '#ff6b6b', 'Médio': '#feca57', 'Baixo': '#48dbfb'}
            )
            st.plotly_chart(fig_pie, use_container_width=True)
        
        with col2:
            # Gráfico de barras
            fig_bar = px.bar(
                x=list(potencial_counts.keys()),
                y=list(potencial_counts.values()),
                title="Quantidade por Potencial",
                color=list(potencial_counts.keys()),
                color_discrete_map={'Alto': '#ff6b6b', 'Médio': '#feca57', 'Baixo': '#48dbfb'}
            )
            st.plotly_chart(fig_bar, use_container_width=True)
        
        # Insights automáticos
        st.subheader("🧠 Insights Automáticos")
        
        total = len(st.session_state.leads_data)
        alto_perc = (potencial_counts['Alto'] / total * 100) if total > 0 else 0
        
        if alto_perc > 30:
            st.success(f"🎯 Excelente! {alto_perc:.1f}% dos leads são de alto potencial!")
        elif alto_perc > 15:
            st.info(f"👍 Bom resultado! {alto_perc:.1f}% dos leads são de alto potencial.")
        else:
            st.warning(f"⚠️ Apenas {alto_perc:.1f}% dos leads são de alto potencial. Considere refinar os critérios de busca.")
        
        # Sugestões de melhoria
        st.subheader("💡 Sugestões de Melhoria")
        suggestions = [
            "🎯 Teste diferentes combinações de cargos executivos",
            "📍 Experimente segmentar por cidades específicas",
            "🔄 Varie as páginas de busca para encontrar leads diferentes",
            "📊 Analise os padrões dos leads de alto potencial",
            "⏰ Execute buscas em horários diferentes"
        ]
        
        for suggestion in suggestions:
            st.write(f"• {suggestion}")
    
    else:
        st.info("📊 Execute uma busca para ver analytics!")

# TAB 4: Histórico
with tab4:
    st.header("📋 Histórico de Buscas")
    
    if st.session_state.search_history:
        # Estatísticas do histórico
        total_searches = len(st.session_state.search_history)
        total_leads_found = sum([s['results_count'] for s in st.session_state.search_history])
        avg_leads = total_leads_found / total_searches if total_searches > 0 else 0
        
        col1, col2, col3 = st.columns(3)
        with col1:
            st.metric("Total de Buscas", total_searches)
        with col2:
            st.metric("Total de Leads", total_leads_found)
        with col3:
            st.metric("Média por Busca", f"{avg_leads:.1f}")
        
        # Tabela do histórico
        df_history = pd.DataFrame(st.session_state.search_history)
        st.dataframe(df_history, use_container_width=True)
        
        # Gráfico temporal
        if len(st.session_state.search_history) > 1:
            fig_timeline = px.line(
                df_history, 
                x='timestamp', 
                y='results_count',
                title="Evolução dos Resultados por Busca",
                markers=True
            )
            st.plotly_chart(fig_timeline, use_container_width=True)
        
        # Botão para limpar histórico
        if st.button("🗑️ Limpar Histórico"):
            st.session_state.search_history = []
            st.success("✅ Histórico limpo!")
            st.rerun()
    
    else:
        st.info("📝 Nenhuma busca realizada ainda.")

# Footer
st.markdown("---")
st.markdown(
    """
    <div style='text-align: center; color: #666; padding: 1rem;'>
        🚀 LinkedIn Lead Generator - Powered by N8N & Streamlit<br>
        Developed with ❤️ for efficient lead generation
    </div>
    """,
    unsafe_allow_html=True
)