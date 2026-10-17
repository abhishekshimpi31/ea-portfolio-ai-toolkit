import pandas as pd
from faker import Faker
import random
import uuid

# Faker initialisieren (für realistische deutsche Namen und Firmen)
fake = Faker('de_DE')

def generate_ea_apm_data():
    # 1. Verteilung der 4000 Anwendungen berechnen
    total_apps = 4000
    planned_prod_total = 1500
    
    production_count = int(planned_prod_total * 0.6)  # 60% = 900
    planned_count = int(planned_prod_total * 0.4)     # 40% = 600
    remaining_count = total_apps - planned_prod_total # Rest = 2500
    
    # Die restlichen 2500 auf andere Status verteilen
    other_statuses = ['Draft', 'Cancelled', 'Phaseout', 'Retired']
    remaining_status_list = random.choices(other_statuses, k=remaining_count)
    
    # Alle Status zusammenführen und gut durchmischen
    all_statuses = (['Production'] * production_count) + (['Planned'] * planned_count) + remaining_status_list
    random.shuffle(all_statuses)
    
    # 2. LeanIX / ServiceNow APM Dropdown-Werte definieren
    application_types = ['Application (Standalone)', 'Application', 'functional module.', 'Non Application']
    time_model = ['Tolerate', 'Invest', 'Migrate', 'Eliminate']
    business_values = ['Low', 'Marginal', 'High', 'Critical']
    technical_fits = ['Unacceptable', 'Marginal', 'Adequate', 'Excellent']
    data_classifications = ['Public', 'Internal', 'Confidential', 'Strictly Confidential']
    business_criticalities = ['Low', 'Medium', 'High', 'Mission Critical']
    app_categories = ['HR Management', 'Finance', 'CRM', 'Supply Chain', 'IT Security', 'Marketing', 'Core Banking', 'ERP']
    
    # Diese Felder definieren wir als "Pflichtfelder", die bei fehlerhaften Einträgen geleert werden
    mandatory_field_keys = ['App_Owner', 'TIME_Classification', 'Business_Value', 'Technical_Fit', 'Data_Classification', 'Business_Criticality']

    data = []
    
    for i in range(total_apps):
        status = all_statuses[i]
        
        # 10% Infrastruktur, 90% Anwendungen
        comp_type = random.choices(['Infrastructure', 'Application'], weights=[0.1, 0.9])[0]
        
        # Ca. 80% bestehen den Pflichtfeld-Check (Pass), 20% fallen durch (Fail)
        mandatory_complete = random.choices([True, False], weights=[0.8, 0.2])[0]
        
        # Datensatz aufbauen
        record = {
            'App_ID': f"APP-{fake.unique.random_int(min=10000, max=99999)}",
            'Fact_Sheet_ID': str(uuid.uuid4())[:8], # LeanIX Style ID
            'Sys_ID': str(uuid.uuid4()), # ServiceNow Style ID
            'App_Name': fake.company() + (" Infra" if comp_type == 'Infrastructure' else " App"),
            'Application_Type': random.choice(application_types),
            'Component_Type': comp_type,
            'Status': status,
            'TIME_Classification': random.choice(time_model),
            'Business_Value': random.choice(business_values),
            'Technical_Fit': random.choice(technical_fits),
            'Data_Classification': random.choice(data_classifications),
            'Business_Criticality': random.choice(business_criticalities),
            
            'App_Manager': fake.name(),
            'App_Owner': fake.name(),
            'Support_Group': f"L2 Support {fake.city()}",
            'Cost_Center': f"CC-{random.randint(1000, 9999)}",
            
            'Implementation_Type': random.choice(['Custom Development', 'COTS', 'SaaS', 'PaaS']),
            'Provisioning_Type': random.choice(['Cloud', 'On-Premise', 'Hybrid']),
            'App_Platform_Host': random.choice(['AWS', 'Azure', 'Google Cloud', 'Internal Datacenter', 'IBM Cloud']),
            
            'Short_Description': fake.sentence(nb_words=6),
            'Long_Description': fake.paragraph(nb_sentences=4),
            'App_Category': random.choice(app_categories),
            'Portfolio_Assignment': random.choice(['Core IT', 'Innovation', 'Legacy', 'Operations']),
            'Number_of_Users': random.randint(1, 50000),
            
            # Hilfsspalten für deinen Automatisierungs-Test
            'Mandatory_Check_Passed': mandatory_complete,
            'Business_Capability': random.choice(app_categories) if random.choices([True, False], weights=[0.7, 0.3])[0] else None,
            'Technical_Assets_Valid': random.choices([True, False], weights=[0.85, 0.15])[0]
        }
        
        # Logik für den Pass/Fail-Check: Leere 3-4 Pflichtfelder, wenn mandatory_complete = False
        if not mandatory_complete:
            fields_to_blank = random.sample(mandatory_field_keys, random.randint(3, 4))
            for field in fields_to_blank:
                record[field] = None # Wird in CSV/Excel als leere Zelle ausgegeben
                
        data.append(record)
        
    return pd.DataFrame(data)

# 3. Daten generieren
print("Generiere 4000 EA/APM Datensätze... Bitte warten.")
df_apps = generate_ea_apm_data()

# 4. Als CSV exportieren
csv_filename = 'EA_APM_Applications.csv'
df_apps.to_csv(csv_filename, index=False)

# 5. Optional: Als Excel exportieren (gut für Portfolio Manager)
xlsx_filename = 'EA_APM_Applications.xlsx'
df_apps.to_excel(xlsx_filename, sheet_name='Application Portfolio', index=False)

print(f"\nErfolgreich! Die Daten wurden als '{csv_filename}' und '{xlsx_filename}' gespeichert.")

# Kontroll-Ausgabe
print("\n--- Zusammenfassung ---")
print(f"Status Verteilung:\n{df_apps['Status'].value_counts()}")
print(f"\nFehlerhafte Datensätze (für Fail-Routing): {len(df_apps[df_apps['Mandatory_Check_Passed'] == False])}")