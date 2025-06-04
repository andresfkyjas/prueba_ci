#######################
# Import libraries
import streamlit as st
import pandas as pd
import altair as alt
import plotly.express as px
import plotly.graph_objects as go

#######################
# Page configuration
st.set_page_config(
    page_title="Financial Indicators Dashboard",
    page_icon="📈",
    layout="wide",
    initial_sidebar_state="expanded")

alt.themes.enable("dark")

#######################
# CSS styling
st.markdown("""
<style>

[data-testid="block-container"] {
    padding-left: 2rem;
    padding-right: 2rem;
    padding-top: 1rem;
    padding-bottom: 0rem;
    margin-bottom: -7rem;
}

[data-testid="stVerticalBlock"] {
    padding-left: 0rem;
    padding-right: 0rem;
}

[data-testid="stMetric"] {
    background-color: #393939;
    text-align: center;
    padding: 15px 0;
}

[data-testid="stMetricLabel"] {
  display: flex;
  justify-content: center;
  align-items: center;
}

[data-testid="stMetricDeltaIcon-Up"] {
    position: relative;
    left: 38%;
    -webkit-transform: translateX(-50%);
    -ms-transform: translateX(-50%);
    transform: translateX(-50%);
}

[data-testid="stMetricDeltaIcon-Down"] {
    position: relative;
    left: 38%;
    -webkit-transform: translateX(-50%);
    -ms-transform: translateX(-50%);
    transform: translateX(-50%);
}

</style>
""", unsafe_allow_html=True)

#######################
# Load and prepare data
@st.cache_data
def load_data():
    try:
        df = pd.read_csv('src/edu_pad/static/csv/yahoo_finance_hist.csv')
        return df
    except FileNotFoundError:
        st.error("No se encontró el archivo de datos. Ejecuta main_extractor.py primero.")
        return pd.DataFrame()

# Función para verificar y validar columnas de ubicación
def validate_location_columns(df):
    """Verifica que el DataFrame tenga todas las columnas de ubicación necesarias"""
    required_columns = ['indicator_name', 'country', 'lat', 'lon', 'region', 'currency_pair']
    missing_columns = [col for col in required_columns if col not in df.columns]
    
    if missing_columns:
        st.error(f"Faltan columnas en el archivo: {missing_columns}")
        st.info("Ejecuta main_extractor.py para regenerar el archivo con todas las columnas.")
        return False
    return True

#######################
# Load data
df_raw = load_data()
if df_raw.empty:
    st.stop()

# Validar que el archivo tenga las columnas de ubicación
if not validate_location_columns(df_raw):
    st.stop()

# Use data directly (location info already included from DataWeb)
df_with_location = df_raw.copy()

# Convert numeric columns
numeric_cols = ['abrir', 'max', 'min', 'cerrar', 'cierre_ajustado', 'volumen']
for col in numeric_cols:
    if col in df_with_location.columns:
        df_with_location[col] = pd.to_numeric(df_with_location[col], errors='coerce')

# Convert date-related columns to appropriate types
if 'year' in df_with_location.columns:
    df_with_location['year'] = pd.to_numeric(df_with_location['year'], errors='coerce').astype('Int64')
if 'month' in df_with_location.columns:
    df_with_location['month'] = pd.to_numeric(df_with_location['month'], errors='coerce').astype('Int64')
if 'day' in df_with_location.columns:
    df_with_location['day'] = pd.to_numeric(df_with_location['day'], errors='coerce').astype('Int64')

# Ensure lat and lon are numeric
if 'lat' in df_with_location.columns:
    df_with_location['lat'] = pd.to_numeric(df_with_location['lat'], errors='coerce')
if 'lon' in df_with_location.columns:
    df_with_location['lon'] = pd.to_numeric(df_with_location['lon'], errors='coerce')

#######################
# Sidebar
with st.sidebar:
    st.title('📈 Financial Indicators Dashboard')
    
    # Selector de indicador (reemplaza color theme)
    indicator_list = list(df_with_location['indicador'].unique())
    
    # Crear diccionario de nombres amigables directamente del CSV
    indicator_names = {}
    for indicador in indicator_list:
        nombre_amigable = df_with_location[df_with_location['indicador'] == indicador]['indicator_name'].iloc[0]
        indicator_names[indicador] = nombre_amigable
    
    selected_indicator_display = st.selectbox(
        'Selecciona un indicador', 
        [indicator_names[ind] for ind in indicator_list]
    )
    
    # Get the actual indicator code
    selected_indicator = next(ind for ind, name in indicator_names.items() 
                            if name == selected_indicator_display)
    
    year_list = sorted([year for year in df_with_location.year.unique() if pd.notna(year)], reverse=True)
    selected_year = st.selectbox('Selecciona un año', year_list)
    
    # Filter data
    df_selected = df_with_location[
        (df_with_location.indicador == selected_indicator) & 
        (df_with_location.year == selected_year)
    ]

#######################
# Plotting functions

def make_heatmap(input_df, input_y, input_x, input_color):
    heatmap = alt.Chart(input_df).mark_rect().encode(
        y=alt.Y(f'{input_y}:O', axis=alt.Axis(title="Año", titleFontSize=18, titlePadding=15, titleFontWeight=900, labelAngle=0)),
        x=alt.X(f'{input_x}:O', axis=alt.Axis(title="Indicador", titleFontSize=18, titlePadding=15, titleFontWeight=900)),
        color=alt.Color(f'max({input_color}):Q',
                         legend=None,
                         scale=alt.Scale(scheme='viridis')),
        stroke=alt.value('black'),
        strokeWidth=alt.value(0.25),
    ).properties(width=900
    ).configure_axis(
        labelFontSize=12,
        titleFontSize=12
    )
    return heatmap

def make_world_map(input_df):
    """Crea un mapa mundial con los indicadores usando Plotly"""
    try:
        # Prepare data for world map
        map_data = input_df.groupby(['indicador', 'indicator_name', 'country', 'lat', 'lon'])['cerrar'].mean().reset_index()
        
        fig = go.Figure()
        
        # Add points for each indicator
        for _, row in map_data.iterrows():
            fig.add_trace(go.Scattergeo(
                lon=[row['lon']],
                lat=[row['lat']],
                text=f"{row['indicator_name']}<br>País: {row['country']}<br>Valor: {row['cerrar']:.2f}",
                mode='markers+text',
                marker=dict(
                    size=15,
                    color=row['cerrar'],
                    colorscale='Viridis',
                    showscale=True,
                    colorbar=dict(title="Valor de Cierre"),
                    line=dict(width=1, color='white')
                ),
                name=row['indicator_name'],
                textposition="top center"
            ))
        
        fig.update_layout(
            title={
                'text': 'Ubicación Global de Indicadores Financieros',
                'x': 0.5,
                'xanchor': 'center'
            },
            geo=dict(
                projection_type='natural earth',
                showland=True,
                landcolor='rgb(243, 243, 243)',
                coastlinecolor='rgb(204, 204, 204)',
                showocean=True,
                oceancolor='rgb(230, 245, 255)',
                showcountries=True,
                countrycolor='rgb(204, 204, 204)'
            ),
            template='plotly_dark',
            height=400,
            showlegend=True
        )
        
        return fig
        
    except Exception as e:
        st.error(f"Error creando mapa: {e}")
        # Return simple Altair chart as fallback
        return alt.Chart(input_df).mark_circle(size=100).encode(
            x='lon:Q',
            y='lat:Q',
            color='cerrar:Q',
            tooltip=['indicator_name:N', 'cerrar:Q']
        ).properties(width=700, height=400, title="Ubicaciones de Indicadores")

def make_donut(input_response, input_text, input_color):
    if input_color == 'blue':
        chart_color = ['#29b5e8', '#155F7A']
    elif input_color == 'green':
        chart_color = ['#27AE60', '#12783D']
    elif input_color == 'orange':
        chart_color = ['#F39C12', '#875A12']
    elif input_color == 'red':
        chart_color = ['#E74C3C', '#781F16']
    
    source = pd.DataFrame({
        "Topic": ['', input_text],
        "% value": [100-input_response, input_response]
    })
    
    plot = alt.Chart(source).mark_arc(innerRadius=45, cornerRadius=25).encode(
        theta="% value",
        color=alt.Color("Topic:N",
                        scale=alt.Scale(
                            domain=[input_text, ''],
                            range=chart_color),
                        legend=None),
    ).properties(width=130, height=130)
    
    text = plot.mark_text(align='center', color="#29b5e8", font="Lato", fontSize=32, fontWeight=700, fontStyle="italic").encode(text=alt.value(f'{input_response} %'))
    return plot + text

def format_number(num):
    if abs(num) > 1000000:
        return f'{num / 1000000:.1f} M'
    elif abs(num) > 1000:
        return f'{num / 1000:.1f} K'
    return f'{num:.2f}'

def calculate_indicator_difference(input_df, input_year):
    """Calcula diferencias año a año para indicadores"""
    try:
        # Ensure year is numeric
        input_df = input_df.copy()
        input_df['year'] = pd.to_numeric(input_df['year'], errors='coerce')
        
        # Filter data for selected year and previous year
        selected_year_data = input_df[input_df['year'] == input_year].copy()
        previous_year_data = input_df[input_df['year'] == (input_year - 1)].copy()
        
        if previous_year_data.empty:
            selected_year_data['price_difference'] = 0
            return selected_year_data.sort_values(by="cerrar", ascending=False)
        
        # Calculate average closing price per indicator for each year
        current_avg = selected_year_data.groupby('indicador')['cerrar'].mean().reset_index()
        current_avg.columns = ['indicador', 'cerrar_current']
        
        previous_avg = previous_year_data.groupby('indicador')['cerrar'].mean().reset_index()
        previous_avg.columns = ['indicador', 'cerrar_previous']
        
        # Merge and calculate differences
        merged = current_avg.merge(previous_avg, on='indicador', how='left')
        merged['price_difference'] = merged['cerrar_current'] - merged['cerrar_previous'].fillna(0)
        
        # Add back other columns from current year data
        result = selected_year_data.groupby('indicador').first().reset_index()
        result = result.merge(merged[['indicador', 'price_difference']], on='indicador', how='left')
        result['price_difference'] = result['price_difference'].fillna(0)
        
        return result.sort_values(by="price_difference", ascending=False)
        
    except Exception as e:
        st.error(f"Error calculating indicator differences: {e}")
        # Return empty dataframe with required columns if error occurs
        return pd.DataFrame(columns=['indicador', 'indicator_name', 'cerrar', 'price_difference'])

#######################
# Dashboard Main Panel
col = st.columns((1.5, 4.5, 2), gap='medium')

with col[0]:
    st.markdown('#### Variaciones Alza/Baja')
    
    # Calculate differences for all indicators in selected year
    try:
        all_indicators_data = df_with_location[df_with_location.year == selected_year]
        df_differences = calculate_indicator_difference(df_with_location, selected_year)
        
        min_year = df_with_location['year'].min() if not df_with_location.empty else selected_year
        
        if selected_year > min_year and not df_differences.empty and len(df_differences) > 0:
            # Highest gain
            highest_gain = df_differences.iloc[0]
            st.metric(
                label=f"📈 {highest_gain['indicator_name']}", 
                value=format_number(highest_gain['cerrar']), 
                delta=format_number(highest_gain['price_difference'])
            )
            
            # Highest loss (lowest gain)
            if len(df_differences) > 1:
                lowest_gain = df_differences.iloc[-1]
                st.metric(
                    label=f"📉 {lowest_gain['indicator_name']}", 
                    value=format_number(lowest_gain['cerrar']), 
                    delta=format_number(lowest_gain['price_difference'])
                )
            else:
                st.metric(label="📉 Mayor Baja", value="-", delta="")
        else:
            st.metric(label="📈 Mayor Alza", value="-", delta="")
            st.metric(label="📉 Mayor Baja", value="-", delta="")
            
    except Exception as e:
        st.error(f"Error calculando variaciones: {e}")
        st.metric(label="📈 Mayor Alza", value="-", delta="")
        st.metric(label="📉 Mayor Baja", value="-", delta="")
    
    st.markdown('#### Tendencias del Mercado')
    
    try:
        if not df_differences.empty and selected_year > min_year:
            positive_indicators = len(df_differences[df_differences.price_difference > 0])
            negative_indicators = len(df_differences[df_differences.price_difference < 0])
            total_indicators = len(df_differences)
            
            positive_pct = round((positive_indicators / total_indicators) * 100) if total_indicators > 0 else 0
            negative_pct = round((negative_indicators / total_indicators) * 100) if total_indicators > 0 else 0
            
            donut_chart_positive = make_donut(positive_pct, 'Tendencia Alcista', 'green')
            donut_chart_negative = make_donut(negative_pct, 'Tendencia Bajista', 'red')
        else:
            donut_chart_positive = make_donut(0, 'Tendencia Alcista', 'green')
            donut_chart_negative = make_donut(0, 'Tendencia Bajista', 'red')
    except Exception as e:
        st.error(f"Error calculando tendencias: {e}")
        donut_chart_positive = make_donut(0, 'Tendencia Alcista', 'green')
        donut_chart_negative = make_donut(0, 'Tendencia Bajista', 'red')
    
    migrations_col = st.columns((0.2, 1, 0.2))
    with migrations_col[1]:
        st.write('Alcista')
        st.altair_chart(donut_chart_positive)
        st.write('Bajista')
        st.altair_chart(donut_chart_negative)

with col[1]:
    st.markdown('#### Mapa de Indicadores')
    
    # World map showing indicator locations using Plotly
    try:
        all_indicators_data = df_with_location[df_with_location.year == selected_year]
        if not all_indicators_data.empty:
            world_map = make_world_map(all_indicators_data)
            if isinstance(world_map, go.Figure):
                st.plotly_chart(world_map, use_container_width=True)
            else:
                st.altair_chart(world_map, use_container_width=True)
        else:
            st.info("No hay datos disponibles para el año seleccionado")
    except Exception as e:
        st.error(f"Error mostrando mapa: {e}")
    
    st.markdown('#### Histórico por Año vs Indicador')
    
    # Heatmap: year vs indicator
    try:
        heatmap_data = df_with_location.groupby(['year', 'indicator_name'])['cerrar'].mean().reset_index()
        if not heatmap_data.empty:
            heatmap = make_heatmap(heatmap_data, 'year', 'indicator_name', 'cerrar')
            st.altair_chart(heatmap, use_container_width=True)
        else:
            st.info("No hay suficientes datos para mostrar el heatmap")
    except Exception as e:
        st.error(f"Error creando heatmap: {e}")

with col[2]:
    st.markdown('#### Top Indicadores')
    
    # Show top indicators for selected year
    top_indicators = all_indicators_data.nlargest(len(all_indicators_data), 'cerrar')[['indicator_name', 'cerrar']].reset_index(drop=True)
    
    if not top_indicators.empty:
        st.dataframe(
            top_indicators,
            column_order=("indicator_name", "cerrar"),
            hide_index=True,
            width=None,
            column_config={
                "indicator_name": st.column_config.TextColumn("Indicador"),
                "cerrar": st.column_config.ProgressColumn(
                    "Valor de Cierre",
                    format="%.2f",
                    min_value=0,
                    max_value=max(top_indicators.cerrar) if len(top_indicators) > 0 else 1,
                )}
        )
    
    with st.expander('Información', expanded=True):
        st.write(f'''
            - **Indicador Seleccionado**: {selected_indicator_display}
            - **Año**: {selected_year}
            - **País/Región**: {df_with_location[df_with_location['indicador'] == selected_indicator]['country'].iloc[0] if not df_with_location.empty else 'N/A'}
            - **Tipo**: {df_with_location[df_with_location['indicador'] == selected_indicator]['currency_pair'].iloc[0] if not df_with_location.empty else 'N/A'}
            - **Variaciones Alza/Baja**: Indicadores con mayor ganancia/pérdida anual
            - **Tendencias del Mercado**: Porcentaje de indicadores con tendencia alcista/bajista
            - **Datos**: Yahoo Finance a través de web scraping
            ''')

# Mostrar datos del indicador seleccionado
if not df_selected.empty:
    st.markdown(f"### Datos detallados - {selected_indicator_display} ({selected_year})")
    
    # Time series chart for selected indicator using Plotly
    try:
        df_timeseries = df_selected.sort_values('month').copy()
        
        # Create Plotly line chart
        fig_timeseries = px.line(
            df_timeseries, 
            x='month', 
            y='cerrar',
            title=f'Evolución mensual de {selected_indicator_display}',
            labels={'cerrar': 'Precio de Cierre', 'month': 'Mes'},
            markers=True
        )
        
        fig_timeseries.update_layout(
            template='plotly_dark',
            height=400,
            title={
                'x': 0.5,
                'xanchor': 'center'
            }
        )
        
        fig_timeseries.update_traces(
            line=dict(width=3),
            marker=dict(size=8)
        )
        
        st.plotly_chart(fig_timeseries, use_container_width=True)
        
    except Exception as e:
        st.error(f"Error creando gráfico de series temporales: {e}")
        # Fallback to Altair if Plotly fails
        try:
            df_timeseries = df_selected.sort_values('month').copy()
            
            timeseries_chart = alt.Chart(df_timeseries).mark_line(
                color='#1f77b4',
                strokeWidth=3
            ).encode(
                x=alt.X('month:O', title='Mes'),
                y=alt.Y('cerrar:Q', title='Precio de Cierre'),
                tooltip=['month:O', 'cerrar:Q']
            ).properties(
                width=800,
                height=300,
                title=f'Evolución mensual de {selected_indicator_display}'
            )
            
            points = alt.Chart(df_timeseries).mark_circle(
                color='#ff7f0e',
                size=60
            ).encode(
                x='month:O',
                y='cerrar:Q',
                tooltip=['month:O', 'cerrar:Q']
            )
            
            combined_chart = timeseries_chart + points
            st.altair_chart(combined_chart, use_container_width=True)
        except Exception as e2:
            st.error(f"Error en fallback de Altair: {e2}")
    
    # Summary statistics
    try:
        col1, col2, col3, col4 = st.columns(4)
        with col1:
            st.metric("Promedio", f"{df_selected['cerrar'].mean():.2f}")
        with col2:
            st.metric("Máximo", f"{df_selected['cerrar'].max():.2f}")
        with col3:
            st.metric("Mínimo", f"{df_selected['cerrar'].min():.2f}")
        with col4:
            volatilidad = df_selected['cerrar'].std()
            st.metric("Volatilidad", f"{volatilidad:.2f}" if pd.notna(volatilidad) else "N/A")
    except Exception as e:
        st.error(f"Error calculando estadísticas: {e}")
else:
    st.info(f"No hay datos disponibles para {selected_indicator_display} en {selected_year}")