import streamlit as st
import requests
import pandas as pd
import altair as alt

# --------------------------
# CONFIGURACIÓN API FOOTBALL
# --------------------------
API_KEY = "aeea410c8e1fe91b2ca5d97d1685943b"
BASE_URL = "https://v3.football.api-sports.io"
HEADERS = {"x-apisports-key": API_KEY}

# Diccionario de ligas poco saturadas
LEAGUES = {
    "🇳🇴 Noruega - OBOS-ligaen": 3,
    "🇯🇵 Japón - J-League 2": 98,
    "🇨🇱 Chile - Primera B": 265,
    "🇿🇦 Sudáfrica - PSL": 197,
    "🇻🇳 Vietnam - V.League 2": 384,
    "🇰🇪 Kenia - Premier League": 370
}

# Configuración de página
st.set_page_config(page_title="📊 Sistema de Apuestas PRO", layout="wide")
st.title("📊 Sistema de Apuestas PRO")
st.write("Bienvenido a tu sistema de apuestas deportivas inteligente 🔥")

# Sidebar para filtros
st.sidebar.header("⚙️ Filtros")
liga = st.sidebar.selectbox("Selecciona una liga", list(LEAGUES.keys()))
mostrar_graficos = st.sidebar.checkbox("📈 Mostrar gráficos", value=True)
mostrar_odds = st.sidebar.checkbox("💸 Mostrar cuotas y recomendaciones", value=True)

# Función para obtener partidos
def get_matches(league_id):
    url = f"{BASE_URL}/fixtures?league={league_id}&season=2025&next=10"
    response = requests.get(url, headers=HEADERS)
    if response.status_code == 200:
        data = response.json()
        return pd.json_normalize(data['response'])
    else:
        st.error("❌ Error al conectar con API-FOOTBALL")
        return pd.DataFrame()

# Función para obtener cuotas
def get_odds(fixture_id):
    url = f"{BASE_URL}/odds?fixture={fixture_id}"
    response = requests.get(url, headers=HEADERS)
    if response.status_code == 200:
        data = response.json()
        if data['response']:
            bookmakers = data['response'][0]['bookmakers']
            if bookmakers:
                odds = bookmakers[0]['bets'][0]['values']
                return {v['value']: v['odd'] for v in odds}
    return {}

# Botón para cargar datos
if st.button("🔄 Obtener próximos partidos"):
    league_id = LEAGUES[liga]
    matches = get_matches(league_id)

    if not matches.empty:
        matches['date'] = pd.to_datetime(matches['fixture.date'])
        matches['home'] = matches['teams.home.name']
        matches['away'] = matches['teams.away.name']
        matches['status'] = matches['fixture.status.long']
        matches['fixture_id'] = matches['fixture.id']

        st.subheader("📋 Próximos Partidos")
        st.dataframe(matches[['date', 'home', 'away', 'status']], use_container_width=True)

        if mostrar_odds:
            st.subheader("💸 Cuotas y Recomendaciones")
            odds_data = []
            for _, row in matches.iterrows():
                odds = get_odds(row['fixture_id'])
                if odds:
                    # Calcular probabilidad implícita
                    probabilities = {k: round((1/float(v))*100, 2) for k, v in odds.items()}
                    odds_data.append({
                        "Partido": f"{row['home']} vs {row['away']}",
                        "Fecha": row['date'],
                        **odds,
                        "Prob. Implícitas": probabilities
                    })
            if odds_data:
                odds_df = pd.DataFrame(odds_data)
                st.dataframe(odds_df, use_container_width=True)
            else:
                st.warning("⚠️ No se encontraron cuotas para los próximos partidos.")

        if mostrar_graficos:
            st.subheader("📊 Tendencias")
            # Gráfico: número de partidos por día
            chart1 = alt.Chart(matches).mark_bar(color="#1f77b4").encode(
                x='date:T',
                y='count()',
                tooltip=['date:T', 'count()']
            ).properties(width=600, height=400, title="Número de partidos por fecha")
            st.altair_chart(chart1, use_container_width=True)

            # Gráfico: equipos locales más activos
            top_teams = matches['home'].value_counts().reset_index()
            top_teams.columns = ['Equipo', 'Partidos como local']
            chart2 = alt.Chart(top_teams).mark_bar(color="#ff7f0e").encode(
                x='Equipo',
                y='Partidos como local',
                tooltip=['Equipo', 'Partidos como local']
            ).properties(width=600, height=400, title="Equipos locales más activos")
            st.altair_chart(chart2, use_container_width=True)
    else:
        st.warning("⚠️ No se encontraron próximos partidos en esta liga.")
