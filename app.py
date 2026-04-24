# Examen - Python avancé
# Emma Loquet, M1 ECAP


### Importation des bibliothèques ===========================================================================================

import pandas as pd
import plotly.graph_objects as go
import plotly.express as px
import plotly.io as pio

#On définit un style par défault
pio.templates.default = "plotly_white"


### Préparation des données ======================================================================================================

# Chargement de `supermarket_sales.csv` dans un DataFrame `df`.
df = pd.read_csv("datasets/supermarket_sales.csv")
df.head()

# On conserve uniquement les colonnes utiles
df = df[['Invoice ID', 'Gender', 'City', 'Product line', 'Quantity', 'Unit price', 'Tax 5%', 'Total', 'Date', 'Rating']]
df.head()

df.info()
# Il n'y a aucune valeur manquante dans note base de données

#On change le type de la colonne 'Date' pour que ce soit bien une date
df['Date'] = pd.to_datetime(df['Date'])

df.info()  #Les changements ont bien été effectués


### Création des fonctions =======================================================================================================

def montant_total_achats(data) :
    MT = data['Total'].sum()
    return MT

def evaluation_moyenne(data) :
    moyenne = data['Rating'].mean()
    return moyenne

def nombre_total_achats(data) :
    total = data['Invoice ID'].count()
    return total


### Création des graphiques =======================================================================================================

def plot_evolution_montant_total(data) :

    #Montant total des achats par semaine et par ville
    evolution = (
        data
        .groupby([pd.Grouper(key="Date", freq="W"), "City"])["Total"]
        .sum()
        .reset_index()
    )

    fig = px.line(
        evolution,
        x='Date',
        y='Total',
        color="City",
        color_discrete_sequence=["#2E86AB", "#F18F01", "#6C757D"],
        title="Évolution du montant total des achats par semaine et par ville",
        labels={
            "Date" : "Semaine",
            "Total" : "Montant total des achats",
            "City" : "Ville"
        }
    )

    fig.update_layout(
    template="plotly_white",  # style plus propre
    title_x=0.5           # centre le titre
    )

    return fig


def barplot_nb_total_achats(data):

    df = (
        data
        .groupby(['City', 'Gender'])['Invoice ID']
        .count()
        .reset_index(name='Nb_Achats')
    )

    fig = px.bar(
        df,
        x='Nb_Achats',
        y='City',
        color='Gender',
        color_discrete_sequence=["#2E86AB", "#1B4F72"],
        barmode='group',
        title="Nombre total d'achats par ville et par sexe",
        labels={
            "Nb_Achats": "Nombre d'achats",
            "City": "Ville",
            "Gender": "Sexe"
        }
    )

    fig.update_layout(
        template="plotly_white",
        margin=dict(l=20, r=20, t=40, b=60),
        title_x=0.5,
        bargap=0.45
    )

    
    return fig


def pie_product_line(data):

    df = (
        data
        .groupby("Product line")
        .size()
        .reset_index(name="Part_Achat")
    )

    fig = px.pie(
        df,
        names="Product line",
        values="Part_Achat",
        title="Répartition des catégories de produits",
        color_discrete_sequence=[
            "#1B4F72",  # bleu foncé
            "#2E86AB",  # bleu principal
            "#5DADE2",  # bleu moyen
            "#85C1E9",  # bleu clair
            "#AED6F1",  # très clair
            "#D6EAF8"]
    )

    fig.update_layout(template="plotly_white", 
                      title_x=0.5,
                      margin=dict(l=10, r=10, t=40, b=10))
    

    return fig


### Tableau de bord =================================================================================================================

import dash
from dash import dcc, html, dash_table, Input, Output
import dash_bootstrap_components as dbc

app = dash.Dash(external_stylesheets=[dbc.themes.BOOTSTRAP])
server = app.server

liste_villes = [
    {"label": v, "value": v}
    for v in df["City"].dropna().unique()
]

liste_sexe = [
    {"label": g, "value": g}
    for g in df["Gender"].dropna().unique()
]


app.layout = dbc.Container([

    # HEADER
    dbc.Row([
        dbc.Col(html.H3("Analyse des ventes - Supermarché", style={"fontSize": "22px","fontWeight": "bold"}), md=4),
        dbc.Col(
            dcc.Dropdown(
                id="city-dropdown",
                options=liste_villes,
                placeholder="Ville",
                style={"color": "black"}
            ),
            md=4
        ),

        dbc.Col(
            dcc.Dropdown(
                id="gender-dropdown",
                options=liste_sexe,
                placeholder="Sexe",
                style={"color": "black"}
            ),
            md=4
        )
    ], style={"backgroundColor": "#2E86AB", "padding": "10px", "color": "white"}),

    html.Br(),

    # KPI
    dbc.Row([

        dbc.Col(html.Div(id="kpi_total", style={"fontSize": "20px", "fontWeight": "bold", "textAlign": "center"}), md=4),
        dbc.Col(html.Div(id="kpi_nb", style={"fontSize": "20px", "fontWeight": "bold", "textAlign": "center"}), md=4),
        dbc.Col(html.Div(id="kpi_rating", style={"fontSize": "20px", "fontWeight": "bold", "textAlign": "center"}), md=4),

    ], style={"marginBottom": "20px"}),

    html.Hr(),

    # GRAPHIQUES
    dbc.Row([

        dbc.Col(dcc.Graph(id="fig_line", style={"height": "350px"}), md=7),
        dbc.Col(dcc.Graph(id="fig_bar", style={"height": "350px"}), md=5),

    ], style={"marginBottom": "20px"}),

    dbc.Row([
        dbc.Col(dcc.Graph(id="fig_pie", style={"height": "300px"}), md=6),
        dbc.Col([
        html.H5("Tableau des derniers achats", style={"marginBottom": "10px","fontWeight": "normal", "fontSize": "20px"}),
        dash_table.DataTable(
            id="table_ventes",
            page_size=8,
            style_table={"overflowX": "auto"},
            style_cell={"fontSize": "12px", "textAlign": "left"}
        )
    ], md=6)
    ], style={"marginBottom": "20px"})

], fluid=True)


@app.callback(
    Output("kpi_total", "children"),
    Output("kpi_nb", "children"),
    Output("kpi_rating", "children"),
    Output("fig_line", "figure"),
    Output("fig_bar", "figure"),
    Output("fig_pie", "figure"),
    Output("table_ventes", "data"),      
    Output("table_ventes", "columns"),
    Input("city-dropdown", "value"),
    Input("gender-dropdown", "value")
)

def update_dashboard(city, gender):

    df_filter = df.copy()

    if city:
        df_filter = df_filter[df_filter["City"] == city]

    if gender:
        df_filter = df_filter[df_filter["Gender"] == gender]

    # KPI
    total = montant_total_achats(df_filter)
    nb = nombre_total_achats(df_filter)
    rating = evaluation_moyenne(df_filter)

    kpi_total = f"Montant total : {round(total, 2)} €"
    kpi_nb = f"Nombre d'achats : {nb}"
    kpi_rating = f"Note moyenne : {round(rating, 2)}"

    fig_line = plot_evolution_montant_total(df_filter)
    fig_bar = barplot_nb_total_achats(df_filter)
    fig_pie = pie_product_line(df_filter)

    df_table = df_filter.sort_values("Date", ascending=False).head(100)
    data_table = df_table.to_dict("records")
    columns = [{"name": c, "id": c} for c in df_table.columns]

    return kpi_total, kpi_nb, kpi_rating, fig_line, fig_bar, fig_pie, data_table, columns


if __name__ == '__main__' :
    app.run(debug=True, port=8031, jupyter_mode="external")










