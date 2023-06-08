import streamlit as st
import pandas as pd
import plotly.express as px

st.title("Auswertung Trainingsdaten")

# Datei Upload ermöglichen und CSV als Dataframe hinterlegen
with st.expander("Dateiupload:"):
    uploaded_file = st.file_uploader("Datei", type=["csv"])
if uploaded_file is not None:
    # Can be used wherever a "file-like" object is accepted:
    df = pd.read_csv(uploaded_file)
    # Datentransformation der hochgeladenen Datei
    df = df.dropna(subset=["Wiederholungen"])
    df["Datum"] = pd.to_datetime(df["Datum"]).dt.normalize()
    df["Volumen"] = (df["Gewicht"] * df["Wiederholungen"]).astype(int)
    df["1RM"] = (df["Gewicht"] / (1.0278 - 0.0278 * df["Wiederholungen"])).round(0)
    df["Woche"] = df['Datum'] - pd.offsets.Week(weekday=0)
    
    # Statistiken erstellen auf Datums und Übungslevel
    stats = df.groupby(["Woche", "Datum", "Übung"]).agg({"Gewicht": "max", "Wiederholungen" : "sum", "Volumen": "sum", "1RM": "max"}).reset_index()
    weekly_stats = stats.groupby("Woche").agg({"Volumen": "sum", "1RM": "mean"}).reset_index()
    weekly_stats["Volumen"] = weekly_stats["Volumen"].astype(int)
    weekly_stats["1RM"] = weekly_stats["1RM"].round(1)
    Übungen = stats["Übung"].unique().tolist()
    fig = px.bar(weekly_stats, x="Woche", y="Volumen", template="simple_white")
    stats["Gewicht_diff"] = stats.groupby("Übung")["Gewicht"].diff()
    best_exercise = stats.groupby("Übung")["Gewicht_diff"].sum().sort_values(ascending=False).head(5).reset_index()
    worst_exercise = stats.groupby("Übung")["Gewicht_diff"].sum().sort_values().head(5).reset_index()
    st.header("Volumen")
    st.plotly_chart(fig)
    col1, col2 = st.columns(2)
    with col1:
        st.header("Top Übungen")
        st.dataframe(best_exercise, hide_index=True, column_config={"Gewicht_diff": "Fortschritt kg"})
        st.header("Übung")
        select = st.radio(" ",Übungen)
    
    filtered = stats[stats["Übung"] == select]
    with col2:
        st.header("Flop Übungen")
        st.dataframe(worst_exercise, hide_index=True, column_config={"Gewicht_diff": "Fortschritt kg"})
        fig2  = px.line(filtered, x="Datum", y="Gewicht", template="simple_white", markers=True)
        st.header("Gewicht")
        st.plotly_chart(fig2)
        fig3  = px.line(filtered, x="Datum", y="1RM", template="simple_white", markers=True)
        st.header("1RM")
        st.plotly_chart(fig3)


else:
    None


