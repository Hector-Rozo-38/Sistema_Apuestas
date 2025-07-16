import streamlit as st
import requests
import pandas as pd
import altair as alt

# --------------------------
# CONFIGURACIÓN TheSportsDB
# --------------------------
API_KEY = "a14ea39afead556d671817d80016b881" 
BASE_URL = f"https://www.thesportsdb.com/api/v1/json/{API_KEY}"

# Diccionario de ligas con sus IDs en TheSportsDB
LEAGUES = {
    # LIGAS TOP
    "🇪🇸 España - La Liga": "4335",
    "🏴 Inglaterra - Premier League": "4328",
    "🇮🇹 Italia - Serie A": "4332",
    "🇫🇷 Francia - Ligue 1": "4334",
    "🇩🇪 Alemania - Bundesliga": "4331",
    "🇺🇸 EE.UU. - MLS": "4346",
    "🇦🇷 Argentina - Primera División": "4402",
    "🇲🇽 México - Liga MX": "4350",

    # LIGAS MENOS CONOCIDAS
    "🇨🇴 Colombia - Categoría Primera A": "4348",
    "🇨🇴 Colombia - Categoría Primera B": "4367",
    "🇧🇷 Brasil - Serie A": "4336",
    "🇧🇷 Brasil - Serie B": "4444",
    "🇸🇦 Arabia Saudita - Pro League": "4480",
    "🇸🇦 Arabia Saudita - King’s Cup": "4482",
    "🇯🇵 Japón - J-League": "4393",
    "🇯🇵 Japón - J-League 2": "4394",
    "🇨🇱 Chile - Primera División": "4396",
    "🇿🇦 Sudáfrica - Premier League": "4397",
    "🇻🇳 Vietnam - V.League 1": "4421"
}

# Configuración de página
st.set_page_config(page_title="📊 Sistema de Apuestas PRO", layout="wide")
st.title("📊 Sistema de Apuestas PRO")
st.write("Bienvenido a tu sistema de apuestas deportivas inteligente 🔥")

# Sidebar para filtros
st.sidebar.header("⚙️ Filtros")
liga = st.sidebar.selectbox("Selecciona una liga", list(LEAGUES.keys()))
mostrar_graficos = st.sidebar.checkbox("📈 Mostrar gráficos", value=True)
mostrar_odds = st.sidebar.checkbox("💸 Mostrar cuotas y recomendaciones (beta)", value=False)

# Función para obtener próximos partidos
def get_upcoming_matches(league_id):
    url = f"{BASE_URL}/eventsnextleague.php?id={league_id}"
    response = requests.get(url)
    if response.status_code == 200:
        data = response.json()
        if data['events']:
            df = pd.json_normalize(data['events'])
            # Filtrar solo partidos que NO están finalizados
            df = df[df['strStatus'].isin(['Not Started', 'Live', 'Postponed'])]
            return df
    return pd.DataFrame()

# Botón para cargar datos
if st.button("🔄 Obtener próximos partidos"):
    league_id = LEAGUES[liga]
    matches = get_upcoming_matches(league_id)

    if not matches.empty:
        matches['dateEvent'] = pd.to_datetime(matches['dateEvent'])
        matches['strHomeTeam'] = matches['strHomeTeam'].fillna("Desconocido")
        matches['strAwayTeam'] = matches['strAwayTeam'].fillna("Desconocido")
        matches['strTime'] = matches['strTime'].fillna("Sin hora")
        matches['strStatus'] = matches['strStatus'].fillna("Sin estado")

        st.subheader("📋 Próximos Partidos")
        st.dataframe(matches[['dateEvent', 'strHomeTeam', 'strAwayTeam', 'strTime', 'strStatus']], use_container_width=True)

        if mostrar_odds:
            st.subheader("💸 Cuotas y Recomendaciones (beta)")
            st.info("⚠️ Las cuotas aún no están disponibles en esta API. Se integrarán en futuras versiones.")

        if mostrar_graficos:
            st.subheader("📊 Tendencias")
            chart = alt.Chart(matches).mark_bar(color="#1f77b4").encode(
                x='dateEvent:T',
                y='count()',
                tooltip=['dateEvent:T', 'count()']
            ).properties(width=600, height=400, title="Número de partidos por fecha")
            st.altair_chart(chart, use_container_width=True)
    else:
        st.warning("⚠️ No hay próximos partidos registrados para esta liga.")

