import streamlit as st
import snowflake.connector
import pandas as pd
import config

# ==========================================
# 1. SEITEN-KONFIGURATION & SESSION STATE
# ==========================================
st.set_page_config(page_title="EA Issue Management", layout="wide")

# Initialisiere den Session State für die Navigation (ID und Monat merken)
if 'selected_app_id' not in st.session_state:
    st.session_state.selected_app_id = None
if 'selected_month' not in st.session_state:
    st.session_state.selected_month = None

def reset_selection():
    st.session_state.selected_app_id = None
    st.session_state.selected_month = None

# --- NEU: E-Mail Historie lesen ---
def get_email_history(app_id, month_year):
    if not conn: return 0, None
    query = f"""
    SELECT COUNT(*) as SEND_COUNT, MAX(SENT_AT) as LAST_SENT 
    FROM EA_PORTFOLIO_DB.APM_SCHEMA.EMAIL_NOTIFICATION_LOG 
    WHERE APP_ID = '{app_id}' AND MONTH_YEAR = '{month_year}'
    """
    df_history = pd.read_sql(query, conn)
    count = df_history['SEND_COUNT'].iloc[0]
    last_sent = df_history['LAST_SENT'].iloc[0]
    return count, last_sent

# --- NEU: E-Mail Versand in Snowflake speichern ---
def log_email_sent(app_id, month_year, recipients):
    if not conn: return
    cursor = conn.cursor()
    # Wir machen eine kommagetrennte Liste aus den Empfängern
    recipients_str = ", ".join(recipients)
    query = f"""
    INSERT INTO EA_PORTFOLIO_DB.APM_SCHEMA.EMAIL_NOTIFICATION_LOG (APP_ID, MONTH_YEAR, RECIPIENTS)
    VALUES ('{app_id}', '{month_year}', '{recipients_str}')
    """
    cursor.execute(query)
    cursor.close()

# --- NEU: E-Mail Versand in Snowflake speichern ---
def log_email_sent(app_id, month_year, recipients):
    if not conn: return
    cursor = conn.cursor()
    # Wir machen eine kommagetrennte Liste aus den Empfängern
    recipients_str = ", ".join(recipients)
    query = f"""
    INSERT INTO EA_PORTFOLIO_DB.APM_SCHEMA.EMAIL_NOTIFICATION_LOG (APP_ID, MONTH_YEAR, RECIPIENTS)
    VALUES ('{app_id}', '{month_year}', '{recipients_str}')
    """
    cursor.execute(query)
    cursor.close()

# ==========================================
# 2. DATENBANKVERBINDUNG
# ==========================================
@st.cache_resource
def init_connection():
    try:
        return snowflake.connector.connect(
            user=config.SNOWFLAKE_USER,
            password=config.SNOWFLAKE_PASSWORD,
            account=config.SNOWFLAKE_ACCOUNT,
            warehouse=config.SNOWFLAKE_WAREHOUSE,
            database=config.SNOWFLAKE_DATABASE,
            schema=config.SNOWFLAKE_SCHEMA
        )
    except Exception as e:
        st.error(f"Fehler bei der Datenbankverbindung: {e}")
        return None

conn = init_connection()

# ==========================================
# 3. DATEN ABFRAGEN
# ==========================================
@st.cache_data(ttl=600)
def load_issue_apps():
    if not conn:
        return pd.DataFrame()
    
    # Lade alle Felder, um dynamisch auf leere Werte prüfen zu können
    query = """
    SELECT *
    FROM EA_PORTFOLIO_DB.APM_SCHEMA.APPLICATION_STATUS_ANALSYS 
    WHERE MANDATORY_CHECK_PASSED = FALSE
    ORDER BY APP_ID DESC;
    """
    return pd.read_sql(query, conn)

# ==========================================
# 4. HAUPT-APP LOGIK
# ==========================================
if conn:
    df = load_issue_apps()
    
    if df.empty:
        st.success("🎉 Großartig! Es gibt aktuell keine fehlgeschlagenen Anwendungen.")
    else:
        # ------------------------------------------
        # ANSICHT 1: DETAILSEITE DER ANWENDUNG
        # ------------------------------------------
        if st.session_state.selected_app_id and st.session_state.selected_month:
            st.button("🔙 Zurück zur App-Liste", on_click=reset_selection)
            
            # Filtere exakt nach der ID UND dem Monat
            condition = (df['APP_ID'] == st.session_state.selected_app_id) & (df['MONTH_YEAR'] == st.session_state.selected_month)
            app_data = df[condition].iloc[0]
            
            st.title(f"{app_data.get('APP_ID', 'Unbekannt')} - {app_data.get('APP_NAME', 'Unbenannt')}")
            st.error("⚠️ Mandatory Check: Failed")
            
            # --- Dynamische Prüfung auf leere Felder ---
            empty_fields = []
            for column_name in df.columns:
                val = app_data[column_name]
                if pd.isna(val) or val is None or str(val).strip() == "" or str(val).strip() == "None":
                    empty_fields.append(column_name)
            
            if empty_fields:
                st.warning(f"🚨 **Achtung, folgende {len(empty_fields)} Felder sind leer:** " + ", ".join(empty_fields))
            else:
                st.success("✅ Alle Datenfelder sind vollständig ausgefüllt.")
            
            st.divider()
            
            # Basis-Informationen anzeigen
            col1, col2 = st.columns(2)
            with col1:
                st.write(f"**Monat/Jahr:** {app_data.get('MONTH_YEAR', '-')}")
                st.write(f"**Plattform:** {app_data.get('APP_PLATFORM_HOST', '-')}")
                st.write(f"**Status:** {app_data.get('STATUS', '-')}")
            with col2:
                st.write(f"**Anwendungstyp:** {app_data.get('APPLICATION_TYPE', '-')}")
                st.write(f"**Transition Category:** {app_data.get('STATUS_TRANSITION_CATEGORY', '-')}")
                
            st.write("### Beschreibung")
            st.info(app_data.get('LONG_DESCRIPTION', 'Keine Beschreibung vorhanden.'))
            
            st.button("🤖 KI-Analyse für diese App starten", type="primary", disabled=True)
            
            st.divider()
            
            # --- E-MAIL BENACHRICHTIGUNG ---
            st.write("### 📧 Verantwortliche kontaktieren")
            
            app_id = app_data.get('APP_ID')
            app_month = app_data.get('MONTH_YEAR')
            
            # NEU: Historie aus Snowflake abfragen und anzeigen
            send_count, last_sent = get_email_history(app_id, app_month)
            if send_count > 0:
                # Formatiere das Datum schön (z.B. 2026-10-11 14:30)
                formatted_date = last_sent.strftime("%Y-%m-%d %H:%M") if pd.notna(last_sent) else "Unbekannt"
                st.info(f"ℹ️ **Historie:** Für diese Anwendung wurden bereits **{send_count}** Erinnerungen gesendet. (Zuletzt am: {formatted_date})")
            else:
                st.info("ℹ️ **Historie:** Bisher wurden noch keine Erinnerungen für diese Anwendung gesendet.")
            
            
            owner = app_data.get('APP_OWNER')
            manager = app_data.get('APP_MANAGER')
            
            available_contacts = {}
            if pd.notna(owner) and str(owner).strip() not in ["", "None"]:
                available_contacts["Owner"] = str(owner).strip()
            if pd.notna(manager) and str(manager).strip() not in ["", "None"]:
                available_contacts["Manager"] = str(manager).strip()
                
            if not available_contacts:
                st.warning("⚠️ Für diese Anwendung ist leider weder ein Owner noch ein Manager in der Datenbank hinterlegt.")
            else:
                selected_roles = st.multiselect(
                    "Empfänger auswählen:", 
                    options=list(available_contacts.keys()),
                    default=list(available_contacts.keys())
                )
                
                recipients = [available_contacts[role] for role in selected_roles]
                
                app_name = app_data.get('APP_NAME', 'Unbenannt')
                default_subject = f"Aktion erforderlich: Fehlende Daten für Anwendung {app_name}"
                default_body = (
                    f"Hallo,\n\n"
                    f"bei der Überprüfung der Anwendung '{app_name}' (ID: {app_id}) "
                    f"wurde festgestellt, dass einige Pflichtfelder (Mandatory Checks) fehlen.\n\n"
                    f"Bitte aktualisieren Sie die Daten zeitnah im EA-System.\n\n"
                    f"Viele Grüße\nDein EA Portfolio Management"
                )
                
                email_subject = st.text_input("Betreff", value=default_subject)
                email_body = st.text_area("Nachricht", value=default_body, height=150)
                
                if st.button("✉️ E-Mail senden", type="primary", disabled=len(recipients) == 0):
                    # 1. API Aufruf für den echten Mail-Versand kommt hierhin
                    
                    # 2. NEU: In Snowflake protokollieren
                    log_email_sent(app_id, app_month, recipients)
                    
                    st.success(f"Die E-Mail wurde erfolgreich gesendet und in der Historie gespeichert!")
                    
                    # Lädt die Seite neu, damit der Zähler sofort hochgeht
                    st.rerun()

        # ------------------------------------------
        # ANSICHT 2: LISTENANSICHT & FILTER
        # ------------------------------------------
        else:
            st.title("🏢 EA Portfolio - Issue Management")
            st.subheader("Anwendungen mit fehlgeschlagenem Mandatory Check")
            
            # -- FILTER BEREICH (SEITENLEISTE) --
            st.sidebar.header("🔍 Filter")
            
            available_months = ["Alle"] + sorted(df['MONTH_YEAR'].dropna().unique().tolist())
            selected_month = st.sidebar.selectbox("Monat / Jahr", available_months)
            
            available_statuses = ["Alle"] + sorted(df['STATUS'].dropna().unique().tolist())
            selected_status = st.sidebar.selectbox("App Status", available_statuses)
            
            if 'STATUS_TRANSITION_CATEGORY' in df.columns:
                available_transitions = ["Alle"] + sorted(df['STATUS_TRANSITION_CATEGORY'].dropna().unique().tolist())
                selected_transition = st.sidebar.selectbox("Transition Category", available_transitions)
            else:
                selected_transition = "Alle"
            
            search_id = st.sidebar.text_input("App ID (z.B. APP-10773)")
            search_name = st.sidebar.text_input("App Name")

            # -- DATEN FILTERN --
            filtered_df = df.copy()
            if selected_month != "Alle":
                filtered_df = filtered_df[filtered_df['MONTH_YEAR'] == selected_month]
            if selected_status != "Alle":
                filtered_df = filtered_df[filtered_df['STATUS'] == selected_status]
            if selected_transition != "Alle" and 'STATUS_TRANSITION_CATEGORY' in filtered_df.columns:
                filtered_df = filtered_df[filtered_df['STATUS_TRANSITION_CATEGORY'] == selected_transition]
            if search_id:
                filtered_df = filtered_df[filtered_df['APP_ID'].astype(str).str.contains(search_id, case=False, na=False)]
            if search_name:
                filtered_df = filtered_df[filtered_df['APP_NAME'].astype(str).str.contains(search_name, case=False, na=False)]

            st.write(f"Es werden **{len(filtered_df)}** Anwendungen angezeigt.")
            st.divider()

            # -- PAGINATION (Seitenaufteilung) --
            if not filtered_df.empty:
                items_per_page = 50
                total_pages = max(1, (len(filtered_df) - 1) // items_per_page + 1)
                
                col_empty, col_page = st.columns([3, 1])
                with col_page:
                    current_page = st.number_input("Seite", min_value=1, max_value=total_pages, value=1, step=1)
                
                start_idx = (current_page - 1) * items_per_page
                end_idx = start_idx + items_per_page
                display_df = filtered_df.iloc[start_idx:end_idx]

                # -- LISTENANSICHT RENDERN --
                for index, row in display_df.iterrows():
                    with st.container():
                        col_info, col_btn = st.columns([4, 1])
                        
                        app_id = row.get('APP_ID', 'Unbekannt')
                        app_month = row.get('MONTH_YEAR', 'Unbekannt')
                        
                        with col_info:
                            st.write(f"### {row.get('APP_NAME', 'Unbenannt')}")
                            st.write(f"**ID:** {app_id} | **Status:** {row.get('STATUS', '-')} | **Monat:** {app_month}")
                        
                        with col_btn:
                            st.write("")
                            if st.button("Details öffnen", key=f"btn_{app_id}_{app_month}_{index}"):
                                st.session_state.selected_app_id = app_id
                                st.session_state.selected_month = app_month
                                st.rerun()
                    st.divider()