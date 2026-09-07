import streamlit as st
import pandas as pd
import plotly.graph_objects as go
import plotly.express as px
from datetime import datetime, timedelta, date
import database as db
import utils

st.set_page_config(page_title="BTP-Engineering", page_icon="•",
                   layout="wide", initial_sidebar_state="expanded")

# ==================== DESIGN TOKENS ====================
INK    = "#1a1a1a"
INK_2  = "#5c5c5c"
MUTED  = "#9a9a9a"
HAIR   = "#ececec"
BG     = "#ffffff"

ACCENT = "#2a78d6"      # bleu (accent, Budget)
SERIE  = "#e8863a"      # orange (Dépenses)
VIOLET = "#7a5cd0"      # 3e teinte KPI
GOOD   = "#1f9d4d"      # écart positif / terminé
BAD    = "#cf4b4b"      # écart négatif

STATUT_COULEURS = {"Planifiée": "#4a90d9", "En cours": "#f0a500", "Terminée": "#1f9d4d"}
ORDRE_STATUTS   = ["Planifiée", "En cours", "Terminée"]

FONT_FAMILY = "system-ui, -apple-system, 'Segoe UI', Roboto, sans-serif"

# ==================== CSS ====================
st.markdown(f"""
<style>
    .stApp {{ background: {BG}; }}
    .block-container, [data-testid="stMainBlockContainer"] {{
        padding: 2.4rem 2.5rem 4rem 2.5rem;
        max-width: 1180px; margin-left: 0;
    }}
    h1, h2, h3, h4 {{ color: {INK}; font-weight: 650; letter-spacing: -0.01em; }}

    [data-testid="stSidebar"] {{ background: #f5f5f3; border-right: 1px solid {HAIR}; }}
    [data-testid="stSidebar"] .block-container {{ padding-top: 2rem; }}
    [data-testid="stSidebar"] [role="radiogroup"] label {{ padding: 3px 0; }}

    .stTabs [data-baseweb="tab-list"] {{ gap: 6px; border-bottom: 1px solid {HAIR}; }}
    .stTabs [data-baseweb="tab"] {{
        font-size: 0.88rem; padding: 6px 10px; color: {MUTED};
    }}
    .stTabs [aria-selected="true"] {{ color: {INK}; }}

    [data-testid="stExpander"] {{
        border: none; border-bottom: 1px solid {HAIR};
        border-radius: 0; background: transparent; box-shadow: none;
    }}
    [data-testid="stExpander"] summary {{ font-weight: 550; padding: 6px 0; }}
    [data-testid="stExpander"] summary:hover {{ color: {ACCENT}; }}

    [data-testid="stMetric"] {{ background: transparent; border: none; padding: 0; }}
    [data-testid="stMetricLabel"] p {{
        color: {MUTED}; font-size: 0.72rem; font-weight: 500;
        text-transform: uppercase; letter-spacing: 0.05em;
    }}
    [data-testid="stMetricValue"] {{ font-size: 1.35rem; font-weight: 600; color: {INK}; }}

    .stButton button {{
        border-radius: 6px; font-weight: 550; font-size: 0.87rem;
        border: 1px solid {HAIR}; box-shadow: none;
    }}
    .stButton button[kind="primary"] {{ border: none; }}

    [data-testid="stDataFrame"] {{ border: 1px solid {HAIR}; border-radius: 8px; }}
    [data-testid="stDataFrame"] * {{ font-size: 0.85rem; }}

    hr {{ margin: 1rem 0; border-color: {HAIR}; }}
</style>
""", unsafe_allow_html=True)


# ==================== HELPERS ====================
def parse_date(s):
    """'YYYY-MM-DD' (ou isoformat) -> date, sinon None."""
    if not s:
        return None
    try:
        return date.fromisoformat(str(s)[:10])
    except ValueError:
        return None


def fcfa(x):
    return f"{float(x or 0):,.0f}".replace(",", " ") + " FCFA"


def couleur_ecart(montant):
    return GOOD if montant >= 0 else BAD


def ecart_html(montant, size="1.35rem"):
    montant = float(montant or 0)
    signe = "+" if montant > 0 else ("−" if montant < 0 else "")
    val = f"{abs(montant):,.0f}".replace(",", " ")
    return (f"<span style='color:{couleur_ecart(montant)};font-weight:600;font-size:{size}'>"
            f"{signe}{val} FCFA</span>")


def titre_page(titre, sous_titre=""):
    st.markdown(
        f"<div style='margin-bottom:28px'>"
        f"<div style='font-size:1.7rem;font-weight:650;color:{INK};letter-spacing:-0.02em'>{titre}</div>"
        + (f"<div style='color:{MUTED};font-size:0.92rem;margin-top:4px'>{sous_titre}</div>"
           if sous_titre else "")
        + "</div>",
        unsafe_allow_html=True,
    )


def section(titre):
    st.markdown(
        f"<div style='display:flex;align-items:center;gap:8px;margin:38px 0 16px;"
        f"padding-bottom:8px;border-bottom:1px solid {HAIR}'>"
        f"<span style='width:14px;height:2px;background:{ACCENT};display:inline-block'></span>"
        f"<span style='font-size:0.74rem;font-weight:600;color:{MUTED};text-transform:uppercase;"
        f"letter-spacing:0.08em'>{titre}</span></div>",
        unsafe_allow_html=True,
    )


def kpi_row(items):
    """items : liste de (label, valeur_html[, couleur_accent])."""
    cards = ""
    for item in items:
        label, valeur = item[0], item[1]
        bar = item[2] if len(item) > 2 and item[2] else HAIR
        cards += (
            f"<div style='flex:1 1 150px;background:{BG};border:1px solid {HAIR};"
            f"border-top:3px solid {bar};border-radius:12px;padding:14px 16px'>"
            f"<div style='font-size:0.78rem;color:{MUTED};font-weight:500'>{label}</div>"
            f"<div style='font-size:1.5rem;font-weight:700;color:{INK};margin-top:4px'>{valeur}</div>"
            f"</div>"
        )
    st.markdown(
        f"<div style='display:flex;gap:12px;flex-wrap:wrap'>{cards}</div>",
        unsafe_allow_html=True,
    )


def afficher_ecart(label, montant):
    st.markdown(
        f"<div style='font-size:0.72rem;color:{MUTED};font-weight:500;"
        f"text-transform:uppercase;letter-spacing:0.05em'>{label}</div>"
        f"<div style='margin-top:3px'>{ecart_html(montant, size='1.5rem')}</div>",
        unsafe_allow_html=True,
    )


def toast_ok(msg):
    """Confirmation d'enregistrement, visible après le rerun."""
    st.toast(msg, icon="✅")


def sous_label(txt):
    st.markdown(
        f"<div style='color:{MUTED};font-size:0.72rem;font-weight:600;text-transform:uppercase;"
        f"letter-spacing:0.05em;margin:14px 0 2px'>{txt}</div>",
        unsafe_allow_html=True,
    )


def style_fig(fig, height=None, grid_x=False):
    fig.update_layout(
        font=dict(family=FONT_FAMILY, color=INK_2, size=12),
        paper_bgcolor="rgba(0,0,0,0)",
        plot_bgcolor="rgba(0,0,0,0)",
        margin=dict(l=4, r=16, t=6, b=4),
        legend=dict(orientation="h", yanchor="bottom", y=1.05, x=0, title_text="",
                    font=dict(color=MUTED, size=11)),
        hoverlabel=dict(bgcolor=BG, bordercolor=HAIR,
                        font=dict(family=FONT_FAMILY, color=INK)),
        bargap=0.42,
    )
    fig.update_xaxes(showgrid=grid_x, gridcolor="#f4f4f3", zeroline=False,
                     linecolor="rgba(0,0,0,0)", tickcolor="rgba(0,0,0,0)",
                     tickfont=dict(color=MUTED, size=11), title_text="")
    fig.update_yaxes(showgrid=False, zeroline=False, linecolor="rgba(0,0,0,0)",
                     tickcolor="rgba(0,0,0,0)", tickfont=dict(color=INK_2, size=11),
                     title_text="")
    if height:
        fig.update_layout(height=height)
    return fig


PLOTLY_CONF = {"displayModeBar": False}


# ==================== SIDEBAR ====================
st.sidebar.markdown(
    f"<div style='font-size:1.05rem;font-weight:650;color:{INK}'>BTP-Engineering</div>"
    f"<div style='color:{MUTED};font-size:0.78rem;margin-bottom:20px'>Suivi de chantiers</div>",
    unsafe_allow_html=True,
)
page = st.sidebar.radio(
    "Navigation",
    ["Tableau de bord", "Chantiers", "Nouveau chantier"],
    label_visibility="collapsed",
)


# ==================== PAGE : TABLEAU DE BORD ====================
if page == "Tableau de bord":
    titre_page("Tableau de bord", "Vue consolidée de tous les chantiers")

    chantiers = utils.get_all_chantiers_details()

    if not chantiers:
        st.info("Aucun chantier. Rendez-vous sur « Nouveau chantier » pour commencer.")
    else:
        total_uos = sum(c['nb_uos'] for c in chantiers)
        total_budget = sum(c['budget_total'] for c in chantiers)
        total_depenses = sum(c['depenses_total'] for c in chantiers)

        kpi_row([
            ("Chantiers", str(len(chantiers)), ACCENT),
            ("Unités d'œuvre", str(total_uos), VIOLET),
            ("Budget total", fcfa(total_budget), ACCENT),
            ("Dépenses", fcfa(total_depenses), SERIE),
            ("Écart global",
             ecart_html(total_budget - total_depenses),
             couleur_ecart(total_budget - total_depenses)),
        ])

        section("Chantier")
        chantier_names = [c['nom'] for c in chantiers]
        selected_chantier_name = st.selectbox("Chantier", chantier_names,
                                              label_visibility="collapsed")
        chantier = next(c for c in chantiers if c['nom'] == selected_chantier_name)

        st.write("")
        kpi_row([
            ("Avancement", f"{chantier['avancement_global']*100:.0f} %", ACCENT),
            ("UO terminées", f"{chantier['nb_uos_terminees']} / {chantier['nb_uos']}", GOOD),
            ("Écart budget", ecart_html(chantier['ecart_total']),
             couleur_ecart(chantier['ecart_total'])),
            ("Durée", f"{chantier['duree_jours']} j", VIOLET),
        ])

        # ---- Graphiques ----
        section("Répartition")
        col1, col2 = st.columns([1, 1.5], gap="large")

        with col1:
            st.caption("Unités d'œuvre par statut")
            counts = {s: 0 for s in ORDRE_STATUTS}
            for uo in chantier['uos']:
                counts[uo['statut']] = counts.get(uo['statut'], 0) + 1
            labels = [s for s in ORDRE_STATUTS if counts[s]]
            values = [counts[s] for s in labels]
            if values:
                fig = go.Figure(go.Pie(
                    labels=labels, values=values, sort=False, direction="clockwise",
                    marker=dict(colors=[STATUT_COULEURS[s] for s in labels],
                                line=dict(color=BG, width=2)),
                    textinfo="value", textfont=dict(color=BG, size=13),
                    hovertemplate="%{label} : %{value} UO (%{percent})<extra></extra>",
                ))
                style_fig(fig, height=210)
                fig.update_layout(showlegend=True)
                st.plotly_chart(fig, width='stretch', config=PLOTLY_CONF)
            else:
                st.caption("— Aucune unité d'œuvre.")

        with col2:
            st.caption("Budget et dépenses par unité d'œuvre")
            bdf = pd.DataFrame({
                'UO': [uo['nom'] for uo in chantier['uos']],
                'Budget': [float(uo['budget'] or 0) for uo in chantier['uos']],
                'Dépenses': [float(uo['depenses'] or 0) for uo in chantier['uos']],
            })
            bdf = bdf[(bdf['Budget'] > 0) | (bdf['Dépenses'] > 0)]
            if bdf.empty:
                st.caption("— Renseignez les budgets et dépenses des unités d'œuvre.")
            else:
                fig = go.Figure()
                fig.add_bar(y=bdf['UO'], x=bdf['Budget'], name='Budget',
                            orientation='h', marker_color=ACCENT)
                fig.add_bar(y=bdf['UO'], x=bdf['Dépenses'], name='Dépenses',
                            orientation='h', marker_color=SERIE)
                fig.update_traces(marker_line_width=0, marker_cornerradius=2,
                                  hovertemplate="%{y}<br>%{fullData.name} : %{x:,.0f} FCFA<extra></extra>")
                fig.update_layout(barmode='group', bargroupgap=0.15)
                style_fig(fig, height=max(210, 34 * len(bdf) + 60), grid_x=True)
                fig.update_yaxes(autorange='reversed')
                st.plotly_chart(fig, width='stretch', config=PLOTLY_CONF)

        # ---- Gantt ----
        section("Planning — diagramme de Gantt")
        gantt_rows = []
        for uo in chantier['uos']:
            d = parse_date(uo['date_debut'])
            duree = int(uo.get('duree_jours') or 0)
            f = parse_date(uo['date_fin'])
            if d and duree > 0:
                f = d + timedelta(days=duree)
            if d and f and f > d:
                gantt_rows.append({
                    'UO': uo['nom'],
                    'Début': pd.Timestamp(d),
                    'Fin': pd.Timestamp(f),
                    'Jours': (f - d).days,
                    'Statut': uo['statut'],
                    'Avancement': f"{uo['avancement']*100:.0f}%",
                })

        if gantt_rows:
            gdf = pd.DataFrame(gantt_rows)
            fig = px.timeline(
                gdf, x_start='Début', x_end='Fin', y='UO', color='Statut',
                category_orders={'Statut': ORDRE_STATUTS},
                color_discrete_map=STATUT_COULEURS,
                hover_data={'Jours': True, 'Avancement': True,
                            'Début': '|%d/%m/%Y', 'Fin': '|%d/%m/%Y', 'Statut': False},
            )
            fig.update_traces(marker_line_width=0)
            fig.update_yaxes(autorange='reversed')
            cd, cf = parse_date(chantier['date_debut']), parse_date(chantier['date_fin'])
            if cd and cf and cf > cd:
                fig.add_vline(x=pd.Timestamp(cd), line_width=1, line_dash='dot', line_color=HAIR)
                fig.add_vline(x=pd.Timestamp(cf), line_width=1, line_dash='dot', line_color=HAIR)
            style_fig(fig, height=max(280, 22 * len(gdf) + 90), grid_x=True)
            st.plotly_chart(fig, width='stretch', config=PLOTLY_CONF)
        else:
            st.caption("— Renseignez la date de début et le nombre de jours des unités "
                       "d'œuvre (onglet « Chantiers ») pour afficher le planning.")

        # ---- Tableau détaillé ----
        section("Détail des unités d'œuvre")
        uo_data = []
        for uo in chantier['uos']:
            d = parse_date(uo['date_debut'])
            uo_data.append({
                'Unité d\'œuvre': uo['nom'],
                'Statut': uo['statut'],
                'Début': d.strftime('%d/%m/%Y') if d else '—',
                'Jours': int(uo.get('duree_jours') or 0),
                'Avancement': uo['avancement'],
                'Budget': float(uo['budget'] or 0),
                'Dépenses': float(uo['depenses'] or 0),
                'Écart': uo['ecart_budget'],
                'Tâches': len(uo['taches']),
            })
        df = pd.DataFrame(uo_data)
        nb = lambda v: f"{v:,.0f}".replace(",", " ")
        styled = (
            df.style
            .format({'Budget': nb, 'Dépenses': nb,
                     'Écart': lambda v: f"{'+' if v > 0 else ('−' if v < 0 else '')}"
                                        f"{abs(v):,.0f}".replace(",", " "),
                     'Avancement': '{:.0%}'})
            .map(lambda v: f'color: {couleur_ecart(v)}', subset=['Écart'])
            .map(lambda v: f'color: {STATUT_COULEURS.get(v, MUTED)}', subset=['Statut'])
        )
        st.dataframe(styled, width='stretch', hide_index=True)


# ==================== PAGE : CHANTIERS ====================
elif page == "Chantiers":
    titre_page("Chantiers", "Gérer les chantiers, unités d'œuvre et tâches")

    chantiers = db.get_all_chantiers()

    if not chantiers:
        st.info("Aucun chantier. Créez-en un avec « Nouveau chantier ».")
    else:
        for chantier in chantiers:
            lieu = f"  ·  {chantier['lieu']}" if chantier['lieu'] else ""
            with st.expander(f"{chantier['nom']}{lieu}", expanded=False):
                c1, c2, c3 = st.columns(3)
                for col, lab, val in [
                    (c1, "Chef", chantier['chef_chantier']),
                    (c2, "Début", chantier['date_debut']),
                    (c3, "Fin", chantier['date_fin']),
                ]:
                    col.markdown(
                        f"<div style='color:{MUTED};font-size:0.72rem;text-transform:uppercase;"
                        f"letter-spacing:0.05em'>{lab}</div>"
                        f"<div style='color:{INK}'>{val or '—'}</div>",
                        unsafe_allow_html=True,
                    )

                st.write("")
                tab1, tab2, tab3, tab4 = st.tabs(
                    ["Vue globale", "Unités d'œuvre", "Éditer", "Supprimer"])

                with tab1:
                    details = utils.get_chantier_details(chantier['id'])
                    m1, m2, m3 = st.columns(3)
                    m1.metric("Avancement", f"{details['avancement_global']*100:.0f} %")
                    m2.metric("Budget", fcfa(details['budget_total']))
                    with m3:
                        afficher_ecart("Écart", details['ecart_total'])

                with tab2:
                    uos = db.get_uos_by_chantier(chantier['id'])

                    if not uos:
                        st.caption("Aucune unité d'œuvre pour ce chantier.")
                        if st.button("Charger la structure BTP par défaut",
                                     key=f"seed_{chantier['id']}"):
                            db.seed_chantier_template(chantier['id'])
                            toast_ok("Structure par défaut créée")
                            st.rerun()
                    else:
                        for uo in uos:
                            uid = uo['id']
                            with st.expander(uo['nom'], expanded=False):
                                budget_uo_cur = float(uo['budget'] or 0)
                                depenses_uo_cur = float(uo['depenses'] or 0)
                                avancement = utils.calculate_uo_avancement(uid)
                                taux = (depenses_uo_cur / budget_uo_cur * 100) if budget_uo_cur else 0

                                m1, m2, m3 = st.columns(3)
                                m1.metric("Avancement", f"{avancement*100:.0f} %")
                                with m2:
                                    afficher_ecart("Écart budget",
                                                   budget_uo_cur - depenses_uo_cur)
                                m3.metric("Taux de dépense", f"{taux:.0f} %")

                                # Bornes : la date de début de l'UO doit rester
                                # dans la période du chantier
                                ch_debut = parse_date(chantier['date_debut']) or date.today()
                                ch_fin = parse_date(chantier['date_fin'])
                                if not ch_fin or ch_fin < ch_debut:
                                    ch_fin = ch_debut + timedelta(days=365)
                                uo_debut_def = parse_date(uo['date_debut']) or ch_debut
                                uo_debut_def = min(max(uo_debut_def, ch_debut), ch_fin)

                                sous_label("Planning")
                                p1, p2, p3 = st.columns(3)
                                with p1:
                                    new_uo_debut = st.date_input(
                                        "Date de début", value=uo_debut_def,
                                        min_value=ch_debut, max_value=ch_fin,
                                        key=f"uo_debut_edit_{uid}")
                                with p2:
                                    max_duree = max((ch_fin - new_uo_debut).days, 0)
                                    new_duree = st.number_input(
                                        "Nombre de jours", min_value=0, max_value=max_duree,
                                        value=min(int(uo.get('duree_jours') or 0), max_duree),
                                        step=1, key=f"uo_duree_edit_{uid}")
                                with p3:
                                    new_uo_fin = new_uo_debut + timedelta(days=int(new_duree))
                                    st.metric("Date de fin", new_uo_fin.strftime("%d/%m/%Y"))

                                sous_label("Budget")
                                c1, c2, c3 = st.columns([2, 2, 1])
                                with c1:
                                    new_budget = st.number_input(
                                        "Budget (FCFA)", min_value=0.0, step=1000.0,
                                        value=budget_uo_cur, key=f"uo_budget_edit_{uid}")
                                with c2:
                                    new_depenses = st.number_input(
                                        "Dépenses (FCFA)", min_value=0.0, step=1000.0,
                                        value=depenses_uo_cur, key=f"uo_depenses_edit_{uid}")
                                with c3:
                                    st.write("")
                                    st.write("")
                                    if st.button("Enregistrer", key=f"uo_save_{uid}"):
                                        db.update_uo(uid, uo['nom'], new_uo_debut.isoformat(),
                                                     new_uo_fin.isoformat(), new_budget,
                                                     new_depenses, int(new_duree))
                                        toast_ok("Unité d'œuvre enregistrée")
                                        st.rerun()

                                sous_label("Tâches — quantités")
                                taches = db.get_taches_by_uo(uid)
                                if taches:
                                    df_taches = pd.DataFrame([{
                                        'id': t['id'],
                                        'Nom': t['nom'],
                                        'Unité': t['unite'],
                                        'Quantité prévue': t['qte_prevue'],
                                        'Quantité réalisée': t['qte_realisee'],
                                    } for t in taches])

                                    edited = st.data_editor(
                                        df_taches,
                                        key=f"taches_editor_{uid}",
                                        width='stretch',
                                        hide_index=True,
                                        disabled=['Nom', 'Unité'],
                                        column_config={
                                            'id': None,
                                            'Quantité prévue': st.column_config.NumberColumn(
                                                min_value=0.0, step=1.0),
                                            'Quantité réalisée': st.column_config.NumberColumn(
                                                min_value=0.0, step=1.0),
                                        },
                                    )

                                    if st.button("Enregistrer les quantités",
                                                 key=f"taches_save_{uid}"):
                                        orig = {t['id']: t for t in taches}
                                        changed = 0
                                        for _, row in edited.iterrows():
                                            t = orig[row['id']]
                                            qp = float(row['Quantité prévue'] or 0)
                                            qr = float(row['Quantité réalisée'] or 0)
                                            if qp != t['qte_prevue'] or qr != t['qte_realisee']:
                                                db.update_tache(t['id'], t['nom'], t['unite'],
                                                                qp, qr)
                                                changed += 1
                                        toast_ok(f"{changed} tâche(s) enregistrée(s)")
                                        st.rerun()
                                else:
                                    st.caption("Aucune tâche")

                    st.write("")
                    sous_label("Ajouter une unité d'œuvre")

                    cid = chantier['id']
                    ch_deb = parse_date(chantier['date_debut']) or date.today()
                    ch_fn = parse_date(chantier['date_fin'])
                    if not ch_fn or ch_fn < ch_deb:
                        ch_fn = ch_deb + timedelta(days=365)

                    col1, col2 = st.columns(2)
                    with col1:
                        nom_uo = st.text_input("Nom de l'UO", key=f"uo_nom_{cid}")
                        date_debut_uo = st.date_input(
                            "Date de début", value=ch_deb,
                            min_value=ch_deb, max_value=ch_fn, key=f"uo_debut_{cid}")
                        duree_uo = st.number_input(
                            "Nombre de jours", min_value=0,
                            max_value=max((ch_fn - ch_deb).days, 0),
                            value=0, step=1, key=f"uo_duree_{cid}")
                    with col2:
                        budget_uo = st.number_input("Budget (FCFA)", min_value=0.0, step=1000.0,
                                                    value=0.0, key=f"uo_budget_{cid}")
                        depenses_uo = st.number_input("Dépenses (FCFA)", min_value=0.0, step=1000.0,
                                                      value=0.0, key=f"uo_depenses_{cid}")

                    if st.button("Créer l'unité d'œuvre", key=f"add_uo_{chantier['id']}"):
                        if nom_uo:
                            date_fin_uo = date_debut_uo + timedelta(days=int(duree_uo))
                            db.add_uo(
                                chantier['id'], nom_uo,
                                date_debut_uo.isoformat(), date_fin_uo.isoformat(),
                                budget_uo, depenses_uo, int(duree_uo),
                            )
                            toast_ok("Unité d'œuvre créée")
                            st.rerun()
                        else:
                            st.error("Le nom est requis.")

                with tab3:
                    cid = chantier['id']
                    nom = st.text_input("Nom", value=chantier['nom'], key=f"edit_nom_{cid}")
                    lieu = st.text_input("Lieu", value=chantier['lieu'] or "",
                                         key=f"edit_lieu_{cid}")
                    chef = st.text_input("Chef de chantier",
                                         value=chantier['chef_chantier'] or "",
                                         key=f"edit_chef_{cid}")
                    date_debut = st.date_input(
                        "Date début", key=f"edit_debut_{cid}",
                        value=datetime.fromisoformat(chantier['date_debut'])
                        if chantier['date_debut'] else datetime.now())
                    date_fin = st.date_input(
                        "Date fin", key=f"edit_fin_{cid}",
                        value=datetime.fromisoformat(chantier['date_fin'])
                        if chantier['date_fin'] else datetime.now())

                    if st.button("Sauvegarder", key=f"save_{chantier['id']}", type="primary"):
                        db.update_chantier(chantier['id'], nom, lieu, chef,
                                           str(date_debut), str(date_fin))
                        toast_ok("Chantier enregistré")
                        st.rerun()

                with tab4:
                    st.caption("Cette action supprime le chantier ainsi que toutes ses "
                               "unités d'œuvre et tâches.")
                    if st.button("Supprimer définitivement", key=f"delete_{chantier['id']}"):
                        db.delete_chantier(chantier['id'])
                        toast_ok("Chantier supprimé")
                        st.rerun()


# ==================== PAGE : NOUVEAU CHANTIER ====================
elif page == "Nouveau chantier":
    titre_page("Nouveau chantier",
               "La structure BTP par défaut (unités d'œuvre + tâches) est créée automatiquement")

    col1, col2 = st.columns(2)
    with col1:
        nom = st.text_input("Nom du chantier *")
        lieu = st.text_input("Lieu")
    with col2:
        chef = st.text_input("Chef de chantier")

    col1, col2 = st.columns(2)
    with col1:
        date_debut = st.date_input("Date de début")
    with col2:
        date_fin = st.date_input("Date de fin")

    st.write("")
    if st.button("Créer le chantier", type="primary"):
        if not nom:
            st.error("Le nom du chantier est requis.")
        elif date_fin < date_debut:
            st.error("La date de fin doit être postérieure à la date de début.")
        else:
            db.add_chantier(nom, lieu, chef, str(date_debut), str(date_fin))
            toast_ok(f"Chantier « {nom} » créé")
            st.success(f"Chantier « {nom} » créé.")
            st.info("Ouvrez l'onglet « Chantiers » pour renseigner les quantités, "
                    "les budgets et le planning des unités d'œuvre.")


# ==================== FOOTER ====================
st.write("")
st.caption("BTP-Engineering · suivi de chantiers")
