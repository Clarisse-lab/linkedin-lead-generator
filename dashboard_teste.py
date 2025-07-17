import streamlit as st
import requests
import pandas as pd
import time
import json
from datetime import datetime

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
    .success-msg {
        background-color: #d4edda;
        border: 1px solid #c3e6cb;
        color: #155724;
        padding: 1rem;
        border-radius: 5px;
        margin: 1rem 0;
    }
    .repeat-search-btn {
        background-color: #28a745;
        color: white;
        border: none;
        padding: 0.3rem 0.8rem;
        border-radius: 3px;
        font-size: 0.8rem;
        cursor: pointer;
    }
</style>
""", unsafe_allow_html=True)

# Header principal
st.markdown('<h1 class="main-header">🎯 LinkedIn Lead Generator</h1>', unsafe_allow_html=True)

# Sidebar - Configurações
st.sidebar.header("🔍 Parâmetros de Busca")

# URL do webhook (oculto)
webhook_url = "https://n8n.srv845413.hstgr.cloud/webhook/linkedin-leads-claude"

# Campo livre para cargos
executive_input = st.sidebar.text_input(
    "🎯 Cargos/Termos de Busca",    
    help="Digite os cargos que deseja buscar (ex: CEO CMO diretor)"
)

# Filtro por Setor
sector_filter = st.sidebar.selectbox(
    "🏭 Setor/Indústria",
    [
        "Todos os setores",
        "Tecnologia/SaaS",
        "E-commerce/Varejo", 
        "Serviços Financeiros",
        "Saúde/Farmacêutico",
        "Educação/EdTech",
        "Imobiliário/PropTech",
        "Manufatura/Indústria",
        "Consultoria/Serviços",
        "Marketing/Agências",
        "Logística/Transporte"
    ],
    index=0
)

# Localização expandida
location_options = [
    "Brasil",
    "São Paulo", "Rio de Janeiro", "Belo Horizonte", "Porto Alegre", "Salvador",
    "Brasília", "Fortaleza", "Recife", "Curitiba", "Manaus",
    "Belém", "Goiânia", "Guarulhos", "Campinas", "São Luís",
    "Maceió", "Campo Grande", "Teresina", "João Pessoa", "Vitória"
]

location = st.sidebar.selectbox(
    "📍 Localização",
    location_options,
    index=0
)

# Número de resultados
num_results = st.sidebar.slider("Número de Resultados", 5, 20, 10)

# Página inicial
start_page = st.sidebar.number_input("Página Inicial", 0, 50, 0)

# Área principal dividida em tabs
tab1, tab2, tab3, tab4 = st.tabs(["🚀 Buscar Leads", "📊 Resultados", "📈 Analytics", "📋 Histórico"])

# Inicializar session state
if 'leads_data' not in st.session_state:
    st.session_state.leads_data = []
if 'search_history' not in st.session_state:
    st.session_state.search_history = []

# Função para repetir busca
def repeat_search(search_data):
    """Função para repetir uma busca anterior"""
    # Definir os valores nos campos
    st.session_state.executive_input = search_data.get('executive_terms', '')
    st.session_state.sector_filter = search_data.get('sector', 'Todos os setores')
    st.session_state.location = search_data.get('location', 'Brasil')
    # Redirecionar para a tab de busca
    st.info("🔄 Parâmetros da busca anterior carregados! Vá para a aba 'Buscar Leads' e clique em 'Iniciar Busca'.")

# TAB 1: Buscar Leads
with tab1:
    st.header("🔍 Nova Busca de Leads")
    
    col1, col2 = st.columns([2, 1])
    
    with col1:
        st.subheader("Configuração da Busca")
        
        # Converter input em lista de termos
        executive_terms = [term.strip() for term in executive_input.split() if term.strip()]
        
        # Preview da query (oculto - só para processamento interno)
        query_terms = " OR ".join(executive_terms)
        sector_query = f" {sector_filter.split('/')[0].lower()}" if sector_filter != "Todos os setores" else ""
        query_preview = f"site:linkedin.com/in ({query_terms}){sector_query} {location}"
        
        # Informações da busca
        st.info(f"""
        **Configuração Atual:**
        - 🎯 Cargos: {', '.join(executive_terms)}
        - 🏭 Setor: {sector_filter}
        - 📍 Local: {location}
        - 📊 Resultados: {num_results}
        - 📄 Página: {start_page}
        """)
    
    with col2:
        st.subheader("Ações")
        
        # Botão de busca
        if st.button("🚀 Iniciar Busca", type="primary", use_container_width=True):
            if not executive_terms:
                st.error("❌ Digite pelo menos um cargo para buscar!")
            else:
                # Payload para o N8N
                payload = {
                    "query": query_preview,
                    "num_results": num_results,
                    "start_page": start_page,
                    "location": location,
                    "executive_terms": executive_terms,
                    "sector": sector_filter
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
                        
                        # Calcular estatísticas de potencial
                        alto_potencial = len([l for l in leads if 'ALTO' in l.get('analise', '')])
                        medio_potencial = len([l for l in leads if 'MÉDIO' in l.get('analise', '')])
                        baixo_potencial = len(leads) - alto_potencial - medio_potencial
                        
                        # Taxa de conversão (alto potencial / total)
                        conversion_rate = (alto_potencial / len(leads) * 100) if leads else 0
                        
                        # Salvar no session state
                        st.session_state.leads_data = leads
                        
                        # Adicionar ao histórico com estatísticas detalhadas
                        st.session_state.search_history.append({
                            'timestamp': datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                            'query': query_preview,
                            'results_count': len(leads),
                            'location': location,
                            'sector': sector_filter,
                            'executive_terms': ', '.join(executive_terms),
                            'alto_potencial': alto_potencial,
                            'medio_potencial': medio_potencial,
                            'baixo_potencial': baixo_potencial,
                            'conversion_rate': round(conversion_rate, 1),
                            'search_params': {
                                'executive_terms': ', '.join(executive_terms),
                                'sector': sector_filter,
                                'location': location,
                                'num_results': num_results,
                                'start_page': start_page
                            }
                        })
                        
                        status_text.markdown(f'<div class="success-msg">✅ Busca concluída! Encontrados {len(leads)} leads.</div>', unsafe_allow_html=True)
                        progress_bar.empty()
                        
                    else:
                        st.error(f"❌ Erro na requisição: {response.status_code}")
                        
                except requests.exceptions.RequestException as e:
                    st.error(f"❌ Erro de conexão: {str(e)}")

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
                col1, col2 = st.columns([3, 1])
                
                with col1:
                    st.write(f"**🔗 Link:** {lead.get('link', 'N/A')}")
                    st.write(f"**📝 Resumo:** {lead.get('resumo', 'N/A')}")
                    st.write(f"**🤖 Análise IA:** {lead.get('analise', 'N/A')}")
                
                with col2:
                    # Determinar cor do potencial
                    potencial_color = "🔥" if "ALTO" in lead.get('analise', '') else "⚡" if "MÉDIO" in lead.get('analise', '') else "📊"
                    st.markdown(f"### {potencial_color} Potencial")
        
        # Botões de ação
        col1, col2 = st.columns(2)
        
        with col1:
            if st.button("📥 Exportar para CSV"):
                df = pd.DataFrame(filtered_data)
                csv = df.to_csv(index=False)
                st.download_button(
                    label="⬇️ Download CSV",
                    data=csv,
                    file_name=f"leads_linkedin_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv",
                    mime="text/csv"
                )
        
        with col2:
            # Botão para abrir planilha do Google Sheets
            planilha_url = "https://docs.google.com/spreadsheets/d/181jPxTxogNrgZKFh8BmEtwEhxsPbOTRUfxYrdox5N2k/edit?usp=sharing"
            st.markdown(f'<a href="{planilha_url}" target="_blank"><button style="background-color: #4CAF50; color: white; padding: 10px 20px; border: none; border-radius: 5px; cursor: pointer; font-size: 14px;">📊 Abrir Planilha</button></a>', unsafe_allow_html=True)
    else:
        st.info("🔍 Nenhum resultado encontrado. Execute uma busca primeiro!")

# TAB 3: Analytics
with tab3:
    st.header("📈 Analytics e Insights")
    
    if st.session_state.leads_data:
        # Estatísticas simples
        potencial_counts = {
            'Alto': len([l for l in st.session_state.leads_data if 'ALTO' in l.get('analise', '')]),
            'Médio': len([l for l in st.session_state.leads_data if 'MÉDIO' in l.get('analise', '')]),
            'Baixo': len(st.session_state.leads_data) - len([l for l in st.session_state.leads_data if 'ALTO' in l.get('analise', '') or 'MÉDIO' in l.get('analise', '')])
        }
        
        # Mostrar estatísticas
        st.subheader("📊 Distribuição por Potencial")
        col1, col2, col3 = st.columns(3)
        
        with col1:
            st.metric("🔥 Alto Potencial", potencial_counts['Alto'])
        with col2:
            st.metric("⚡ Médio Potencial", potencial_counts['Médio'])
        with col3:
            st.metric("📊 Baixo Potencial", potencial_counts['Baixo'])
        
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
        avg_conversion = sum([s.get('conversion_rate', 0) for s in st.session_state.search_history]) / total_searches if total_searches > 0 else 0
        
        # Métricas do histórico
        col1, col2, col3, col4 = st.columns(4)
        with col1:
            st.metric("Total de Buscas", total_searches)
        with col2:
            st.metric("Total de Leads", total_leads_found)
        with col3:
            st.metric("Média por Busca", f"{avg_leads:.1f}")
        with col4:
            st.metric("Taxa Conversão Média", f"{avg_conversion:.1f}%")
        
        # Histórico detalhado
        st.subheader("📊 Histórico Detalhado")
        
        for i, search in enumerate(reversed(st.session_state.search_history)):
            with st.expander(f"🔍 Busca {len(st.session_state.search_history) - i} - {search['timestamp']}", expanded=False):
                col1, col2 = st.columns([2, 1])
                
                with col1:
                    st.write(f"**🎯 Cargos:** {search['executive_terms']}")
                    st.write(f"**🏭 Setor:** {search['sector']}")
                    st.write(f"**📍 Local:** {search['location']}")
                    st.write(f"**📊 Total de Leads:** {search['results_count']}")
                    
                    # Distribuição por potencial
                    col_a, col_b, col_c = st.columns(3)
                    with col_a:
                        st.metric("🔥 Alto", search.get('alto_potencial', 0))
                    with col_b:
                        st.metric("⚡ Médio", search.get('medio_potencial', 0))
                    with col_c:
                        st.metric("📊 Baixo", search.get('baixo_potencial', 0))
                    
                    st.write(f"**📈 Taxa de Conversão:** {search.get('conversion_rate', 0)}%")
                
                with col2:
                    st.write("**Ações:**")
                    
                    # Botão para repetir busca
                    if st.button(f"🔄 Repetir Busca", key=f"repeat_{i}"):
                        # Extrair parâmetros da busca
                        search_params = search.get('search_params', {})
                        
                        # Simular repetição da busca
                        st.info("🔄 Repetindo busca com os mesmos parâmetros...")
                        st.write("**Parâmetros da busca:**")
                        for key, value in search_params.items():
                            st.write(f"- {key}: {value}")
                        
                        # Você pode implementar aqui a lógica real para repetir a busca
                        # Por exemplo, definindo os valores no session_state e redirecionando
                        st.warning("💡 **Dica:** Copie os parâmetros acima e cole na aba 'Buscar Leads'")
                    
                    # Botão para ver detalhes
                    if st.button(f"👁️ Ver Query", key=f"query_{i}"):
                        st.code(search.get('query', 'Query não disponível'))
        
        # Análise de tendências
        st.subheader("📈 Análise de Tendências")
        
        if len(st.session_state.search_history) > 1:
            # Preparar dados para análise
            df_history = pd.DataFrame(st.session_state.search_history)
            
            # Média de leads por localização
            if 'location' in df_history.columns:
                location_stats = df_history.groupby('location').agg({
                    'results_count': 'mean',
                    'conversion_rate': 'mean'
                }).round(1)
                
                st.write("**📍 Performance por Localização:**")
                for location, stats in location_stats.iterrows():
                    st.write(f"- {location}: {stats['results_count']} leads/busca ({stats['conversion_rate']}% conversão)")
            
            # Média de leads por setor
            if 'sector' in df_history.columns:
                sector_stats = df_history.groupby('sector').agg({
                    'results_count': 'mean',
                    'conversion_rate': 'mean'
                }).round(1)
                
                st.write("**🏭 Performance por Setor:**")
                for sector, stats in sector_stats.iterrows():
                    st.write(f"- {sector}: {stats['results_count']} leads/busca ({stats['conversion_rate']}% conversão)")
        
        # Botão para limpar histórico
        st.subheader("🗑️ Gerenciar Histórico")
        col1, col2 = st.columns(2)
        
        with col1:
            if st.button("🗑️ Limpar Histórico"):
                st.session_state.search_history = []
                st.success("✅ Histórico limpo!")
                st.rerun()
        
        with col2:
            # Botão para exportar histórico
            if st.button("📥 Exportar Histórico"):
                df_export = pd.DataFrame(st.session_state.search_history)
                csv_export = df_export.to_csv(index=False)
                st.download_button(
                    label="⬇️ Download Histórico CSV",
                    data=csv_export,
                    file_name=f"historico_buscas_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv",
                    mime="text/csv"
                )
    
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