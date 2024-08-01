import logging
import math
import numpy as np
import pandas as pd
#import matplotlib.pyplot as plt
import sys
import os
import timeit

# Setup logging
log_filename = "analysis.log"
logging.basicConfig(level=logging.DEBUG,
                    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
                    handlers=[logging.FileHandler(log_filename),
                              logging.StreamHandler(sys.stdout)])

logger = logging.getLogger(__name__)

LH_PRE_N = 51
LH_POST_N = 36
ER_PRE_N = 0
ER_POST_N = 0

questions = {
    "Passwortverwaltung": {
        "Verwendung desselben Passworts": {
            "Wissen": "Es ist nicht akzeptabel, meine Social Media Passwörter für meine Arbeitskonten zu verwenden.",
            "Einstellung": "Es ist nicht sicher, dasselbe Passwort für soziale Medien und Arbeitskonten zu verwenden.",
            "Verhalten": "Ich verwende unterschiedliche Passwörter für meine Konten bei sozialen Medien und bei der Arbeit."
        },
        "Gemeinsame Nutzung von Passwörtern": {
            "Wissen": "Ich darf meine Arbeitspasswörter nicht mit Kollegen teilen.",
            "Einstellung": "Es ist eine schlechte Idee, meine Arbeitspasswörter weiterzugeben, selbst wenn ein Kollege danach fragt.",
            "Verhalten": "Ich gebe meine Arbeitspasswörter nicht an Kollegen weiter."
        },
        "Verwendung eines sicheren Passworts": {
            "Wissen": "Eine Mischung aus Buchstaben, Zahlen und Symbolen ist notwendig für Arbeitspasswörter.",
            "Einstellung": "Es ist nicht sicher, ein Arbeitspasswort zu haben, das nur aus Buchstaben besteht.",
            "Verhalten": "Ich verwende bei meinen Passwörtern für die Arbeit eine Kombination aus Buchstaben, Zahlen und Symbolen."
        }
    },
    "E-Mail-Nutzung": {
        "Das Anklicken von Links in E-Mails von bekannten Absendern": {
            "Wissen": "Ich darf nicht auf alle Links in E-Mails von Leuten, die ich kenne, klicken.",
            "Einstellung": "Es ist nicht immer sicher, auf Links in E-Mails von Leuten zu klicken, die ich kenne.",
            "Verhalten": "Ich klicke nicht immer auf Links in E-Mails, nur weil sie von jemandem kommen, den ich kenne."
        },
        "Das Anklicken von Links in E-Mails von unbekannten Absendern": {
            "Wissen": "Ich darf nicht auf einen Link in einer E-Mail von einem unbekannten Absender klicken.",
            "Einstellung": "Es kann Schlimmes passieren, wenn ich auf einen Link in einer E-Mail von einem unbekannten Absender klicke.",
            "Verhalten": "Wenn eine E-Mail von einem unbekannten Absender interessant aussieht, klicke ich nicht auf einen darin enthaltenen Link."
        },
        "Anhänge in E-Mails öffnen von unbekannten Absendern": {
            "Wissen": "Ich darf E-Mail-Anhänge von unbekannten Absendern nicht öffnen.",
            "Einstellung": "Es ist riskant, einen E-Mail-Anhang von einem unbekannten Absender zu öffnen.",
            "Verhalten": "Ich öffne keine E-Mail-Anhänge, wenn mir der Absender unbekannt ist."
        }
    },
    "Internetnutzung": {
        "Herunterladen von Dateien": {
            "Wissen": "Ich darf nicht alle Dateien auf meinen Arbeitscomputer herunterladen, auch wenn sie mir helfen, meine Arbeit zu erledigen.",
            "Einstellung": "Das Herunterladen von Dateien auf meinen Arbeitscomputer kann riskant sein.",
            "Verhalten": "Ich lade nicht alle Dateien auf meinen Arbeitscomputer herunter, die mir helfen, meine Arbeit zu erledigen."
        },
        "Zugriff auf dubiose Websites": {
            "Wissen": "Wenn ich bei der Arbeit bin, sollte ich auf bestimmte Websites nicht zugreifen.",
            "Einstellung": "Nur weil ich bei der Arbeit auf eine Website zugreifen kann, heißt das noch lange nicht, dass sie sicher ist.",
            "Verhalten": "Wenn ich bei der Arbeit auf das Internet zugreife, besuche ich nicht jede Website, die ich möchte."
        },
        "Eingabe von Informationen im Internet": {
            "Wissen": "Ich darf nicht jede Information auf jeder Website eingeben, auch wenn sie mir hilft, meine Arbeit zu erledigen.",
            "Einstellung": "Auch wenn es mir hilft, meine Arbeit zu erledigen, spielt es eine Rolle, welche Informationen ich auf einer Website eingebe.",
            "Verhalten": "Ich prüfe die Sicherheit von Websites, bevor ich Informationen eingebe."
        }
    },
    "Nutzung sozialer Medien": {
        "SM-Privatsphäre-Einstellungen": {
            "Wissen": "Ich muss die Privatsphäre-Einstellungen auf meinen Konten in den sozialen Medien regelmäßig überprüfen.",
            "Einstellung": "Es ist eine gute Idee, meine Datenschutzeinstellungen in den sozialen Medien regelmäßig zu überprüfen.",
            "Verhalten": "Ich überprüfe meine Privatsphäre-Einstellungen in den sozialen Medien regelmäßig."#????
        },
        "Berücksichtigung der Folgen": {
            "Wissen": "Ich kann für etwas gekündigt werden, das ich in den sozialen Medien poste.",
            "Einstellung": "Es macht etwas, wenn ich in den sozialen Medien Dinge poste, die ich normalerweise in der Öffentlichkeit nicht sagen würde.",
            "Verhalten": "Ich poste nichts in den sozialen Medien, bevor ich (nicht) die negativen Folgen bedacht habe."
        },
        "Beiträge über die Arbeit": {
            "Wissen": "Ich kann in den sozialen Medien über meine Arbeit nicht posten, was ich will.",
            "Einstellung": "Es ist riskant, bestimmte Informationen über meine Arbeit in den sozialen Medien zu veröffentlichen.",
            "Verhalten": "Ich poste über meine Arbeit in den sozialen Medien, nicht was ich will."
        }
    },
    "Mobile Geräte": {
        "Physische Sicherung mobiler Geräte": {
            "Wissen": "Wenn ich an einem öffentlichen Ort arbeite, muss ich meinen Laptop immer bei mir haben.",
            "Einstellung": "Wenn ich in einem Café arbeite, kann ich meinen Laptop nicht eine Minute lang unbeaufsichtigt lassen.",
            "Verhalten": "Wenn ich an einem öffentlichen Ort arbeite, lasse ich meinen Laptop nicht unbeaufsichtigt."
        },
        "Senden von sensiblen Informationen über Wi-Fi": {
            "Wissen": "Ich darf sensible Arbeitsdateien nicht über ein öffentliches Wi-Fi-Netz versenden.",
            "Einstellung": "Es ist riskant, sensible Arbeitsdateien über ein öffentliches Wi-Fi-Netzwerk zu versenden.",
            "Verhalten": "Ich sende sensible Arbeitsdateien nicht über ein öffentliches Wi-Fi-Netz."
        },
        "Schulter-Surfen": {
            "Wissen": "Wenn ich an einem sensiblen Dokument arbeite, muss ich sicherstellen, dass Fremde meinen Laptop-Bildschirm nicht sehen können.",
            "Einstellung": "Es ist riskant, mit einem Laptop auf sensible Arbeitsdateien zuzugreifen, wenn Fremde meinen Bildschirm sehen können.",
            "Verhalten": "Ich achte darauf, dass Fremde meinen Laptop-Bildschirm nicht sehen können, wenn ich an einem sensiblen Dokument arbeite."
        }
    },
    "Umgang mit Informationen": {
        "Entsorgung von empfindlichen Ausdrucken": {
            "Wissen": "Sensible Ausdrucke können nicht auf die gleiche Weise wie nicht sensible Ausdrucke entsorgt werden.",
            "Einstellung": "Die Entsorgung sensibler Ausdrucke in den Mülleimer ist nicht sicher.",
            "Verhalten": "Wenn sensible Ausdrucke entsorgt werden müssen, sorge ich dafür, dass sie geschreddert oder vernichtet werden."
        },
        "Einlegen von Wechseldatenträgern": {
            "Wissen": "Wenn ich einen USB-Stick an einem öffentlichen Ort finde, sollte ich ihn nicht an meinen Arbeitscomputer anschließen.",
            "Einstellung": "Wenn ich einen USB-Stick an einem öffentlichen Ort finde, kann etwas Schlimmes passieren, wenn ich ihn an meinen Arbeitscomputer anschließe.",
            "Verhalten": "Ich würde einen USB-Stick, den ich an einem öffentlichen Ort gefunden habe, nicht an meinen Arbeitscomputer anschließen."
        },
        "Hinterlassen von sensiblem Material": {
            "Wissen": "Ich darf Ausdrucke mit sensiblen Informationen nicht über Nacht auf meinem Schreibtisch liegen lassen.",
            "Einstellung": "Es ist riskant, Ausdrucke mit sensiblen Informationen über Nacht auf meinem Schreibtisch liegen zu lassen.",
            "Verhalten": "Ich lasse Ausdrucke mit sensiblen Informationen nicht auf meinem Schreibtisch liegen, wenn ich nicht da bin."
        }
    },
    "Berichterstattung über Vorfälle": {
        "Meldung verdächtigen Verhaltens": {
            "Wissen": "Wenn ich jemanden sehe, der sich an meinem Arbeitsplatz verdächtig verhält, sollte ich dies melden.",
            "Einstellung": "Wenn ich jemanden ignoriere, der sich an meinem Arbeitsplatz verdächtig verhält, kann etwas Schlimmes passieren.",
            "Verhalten": "Wenn ich sehen würde, dass sich jemand an meinem Arbeitsplatz verdächtig verhält, würde ich etwas dagegen unternehmen."
        },
        "Ignorieren schlechten Sicherheitsverhaltens von Kollegen": {
            "Wissen": "Ich darf das schlechte Sicherheitsverhalten meiner Kollegen nicht ignorieren.",
            "Einstellung": "Es kann etwas Schlimmes passieren, wenn ich das schlechte Sicherheitsverhalten eines Kollegen ignoriere.",
            "Verhalten": "Wenn ich bemerken würde, dass mein Kollege die Sicherheitsvorschriften ignoriert, würde ich etwas unternehmen."
        },
        "Meldung aller Vorfälle": {
            "Wissen": "Die Meldung von Sicherheitsvorfällen ist nicht freiwillig.",
            "Einstellung": "Es ist riskant, Sicherheitsvorfälle zu ignorieren, auch wenn ich sie für unbedeutend halte.",
            "Verhalten": "Wenn ich einen Sicherheitsvorfall bemerkt habe, würde ich ihn melden."
        }
    }
}

### HELPER FUNCTIONS
def calculate_cohens_d(mean_pre, mean_post, sd_pre, sd_post, n_pre, n_post):
    if n_pre + n_post - 2 == 0:
        return float('nan')
    pooled_sd = np.sqrt(((n_pre - 1) * sd_pre ** 2 + (n_post - 1) * sd_post ** 2) / (n_pre + n_post - 2))
    cohens_d = (mean_post - mean_pre) / pooled_sd
    return cohens_d

def add_suffix_to_filename(filename, suffix, remove=None):
    name = os.path.splitext(filename)[0]
    name_parts = name.split('-')
    if remove != None:
        for val in remove:
            try:
                name_parts.remove(val)
            except:
                continue
    name_parts.append(suffix)
    new_name = '-'.join(name_parts) + '.csv'
    return new_name

### LATEX FUNCTIONS ###
def write_latex_file(data, file_path):
    with open(file_path, 'w') as latex_file:
        latex_file.write(data)

def generate_latex_table(df, groupby_column, file_path):
    df_pre = df[df['Gruppe'] == 'Pre']
    df_post = df[df['Gruppe'] == 'Post']
    
    categories = df[groupby_column].unique()

    if groupby_column == "Kategorie":
        caption = "Durchschnitt und Standardabweichung pro Kategorie"
    elif groupby_column == "Subkategorie":
        caption = "Durchschnitt und Standardabweichung pro Kategorie"
    latex_code = """
\\documentclass{article}
\\usepackage{booktabs}
\\begin{document}

\\begin{table}[h]
    \\centering
"""

    latex_code += f"\\caption{{{caption}}}"

    latex_code = """
    \\label{tab:groupDescriptives}
    \\begin{tabular}{lrrrr}
        \\toprule
         Kategorie & Gruppe & N & Durchschnitt & Standardabweichung  \\\\
        \\midrule[0.4pt]
    """
    for category in categories:
        pre_cat_df = df_pre[df_pre[groupby_column] == category]
        post_cat_df = df_post[df_post[groupby_column] == category]
        
        pre_group_name = str(pre_cat_df['Gruppe'].unique()[0])
        post_group_name = str(post_cat_df['Gruppe'].unique()[0])
        
        pre_kat_mean = pre_cat_df['Mean'].mean()
        pre_kat_sd = pre_cat_df['SD'].mean()
        
        post_kat_mean = post_cat_df['Mean'].mean()
        post_kat_sd = post_cat_df['SD'].mean()
        
        latex_code += f"{category} & {pre_group_name} & {LH_PRE_N} & {pre_kat_mean:.3f} & {pre_kat_sd:.3f} \\\\\n"
        latex_code += f" & {post_group_name} & {LH_POST_N} & {post_kat_mean:.3f} & {post_kat_sd:.3f} \\\\\n"

    latex_code += """
        \\bottomrule
    \\end{tabular}
\\end{table}

\\end{document}
    """

    write_latex_file(latex_code, file_path)
    
def generate_tikz_diagram(title, data):
    """
    data = {
        "item1":(y, sd),
        "item2":(y, sd),
        "item3":(y, sd)
    }
    """
    num_items = len(data)
    xtick_values = ",".join(map(str, range(1, num_items + 1)))
    xticklabels = ",".join(data.keys())

    coordinates_pre = []
    coordinates_post = []

    for i, (key, (value, deviation)) in enumerate(data.items(), 1):
        coordinates_pre.append(f"({i},{value}) +- (0.0, {deviation})")
        coordinates_post.append(f"({i},{value}) +- (0.0, {deviation})")

    coordinates_pre_str = "\n\t\t".join(coordinates_pre)
    coordinates_post_str = "\n\t\t".join(coordinates_post)

    tikz_code = f"""
\\documentclass[border=5pt]{{standalone}}
\\usepackage{{pgfplots}}
\\pgfplotsset{{compat=1.17}}
\\begin{{document}}

\\begin{{tikzpicture}}[line cap=rect]
    \\begin{{axis}}[
        width=10cm,
        ybar,
        bar width=0.3,
        nodes near coords,
        enlargelimits=0.3,
        xtick={{{xtick_values}}},
        xticklabel style={{align=center}},
        xticklabels={{{xticklabels}}},
        legend style={{
            legend pos=outer north east
        }},
        legend image code/.code={{%
            \\draw[#1, draw=none] (0cm,-0.1cm) rectangle (0.25cm,0.1cm);
        }},
        xlabel={{Kategorien}},
        ylabel={{Mittelwert}}
        ]
        \\addplot+[error bars/.cd,
        y dir=both,y explicit]
        coordinates {{
            {coordinates_pre_str}
        }};
        \\addplot+[error bars/.cd,
        y dir=both,y explicit]
        coordinates {{
            {coordinates_post_str}
        }}; 
        \\legend{{Prä, Post}}
    \\end{{axis}}
    \\node[above,font=\\large\\bfseries] at (current bounding box.north) {{{title}}};
\\end{{tikzpicture}}
\\end{{document}}
"""

    return tikz_code

def generate_plots(df, title, groupby_column):
    df_pre = df[df['Gruppe'] == 'Pre']
    df_post = df[df['Gruppe'] == 'Post']
    
    categories = df[groupby_column].unique()

    means_pre = df_pre.groupby(groupby_column)["Mean"].mean()
    means_post = df_post.groupby(groupby_column)["Mean"].mean()
    sds_pre = df_pre.groupby(groupby_column)["SD"].mean()
    sds_post = df_post.groupby(groupby_column)["SD"].mean()

    x = np.arange(len(categories))  # the label locations
    width = 0.35  # the width of the bars

    fig, ax = plt.subplots(figsize=(10, 6))
    rects1 = ax.bar(x - width/2, means_pre, width, label='Pre', yerr=sds_pre, capsize=5)
    rects2 = ax.bar(x + width/2, means_post, width, label='Post', yerr=sds_post, capsize=5)

    ax.set_xlabel(groupby_column)
    ax.set_ylabel('Mean')
    ax.set_title(title)
    ax.set_xticks(x)
    ax.set_xticklabels(categories, rotation=45, ha='right')
    ax.legend()

    fig.tight_layout()
    plt.savefig(f'{title}.png')
    
### DATAFRAME FUNCTIONS
def rename_columns(df):
    # Rename specific columns to avoid errors
    alt = [
        'Ich darf sensible Arbeitsdateien über ein öffentliches* Wi-Fi-Netz versenden.\xa0 (* Wi-Fi-Netz ohne Passwortschutz) ',
        'Ich sende sensible Arbeitsdateien über ein öffentliches* Wi-Fi-Netz. (* Wi-Fi-Netz ohne Passwortschutz) ',
        'Ich darf sensible Arbeitsdateien über ein öffentliches* Wi-Fi-Netz versenden.\xa0 (* Wi-Fi-Netz ohne Passwortschutz)',
        'Ich sende sensible Arbeitsdateien über ein öffentliches* Wi-Fi-Netz. (* Wi-Fi-Netz ohne Passwortschutz)',
        'Es ist riskant, sensible Arbeitsdateien über ein öffentliches* Wi-Fi-Netzwerk zu versenden. \xa0(* Wi-Fi-Netz ohne Passwortschutz)'
    ]
    neu = [
        'Ich darf sensible Arbeitsdateien über ein öffentliches Wi-Fi-Netz versenden.',
        'Ich sende sensible Arbeitsdateien über ein öffentliches Wi-Fi-Netz.',
        'Ich darf sensible Arbeitsdateien über ein öffentliches Wi-Fi-Netz versenden.',
        'Ich sende sensible Arbeitsdateien über ein öffentliches Wi-Fi-Netz.',
        'Es ist riskant, sensible Arbeitsdateien über ein öffentliches Wi-Fi-Netzwerk zu versenden.'
    ]
    df.rename(columns=dict(zip(alt, neu)), inplace=True)
    
    # Überprüfen, ob die Spalte existiert, und gegebenenfalls umbenennen
    old_column_name = "Bitte geben Sie hier Ihren ProbandInnencode an. Dieser setzt sich zusammen aus: Dem Anfangsbuchstaben des Vornamens Ihrer Mutter (Beispiel: M für Maria)Dem Anfangsbuchstaben Ihres Geburtsortes (B..."
    new_column_name = "ProbandInnencode"

    if old_column_name in df.columns:
        df.rename(columns={old_column_name: new_column_name}, inplace=True)

def add_suffix_to_columnname(df):
    rename_map = {}
    for category, subcategories in questions.items():
        for subcategory, dimensions in subcategories.items():
            for dimension, question in dimensions.items():
                prefix = dimension[0]  # Anfangsbuchstabe der Dimension
                new_column_name = f"{prefix} - {question}"
                rename_map[question] = new_column_name

    return df.rename(columns=rename_map)
    
def drop_unnecessary_columns(df):
    # Define keywords to delete unnecessary columns
    keywords = ["Punkte", "Feedback", "Name", "Gesamtpunktzahl", "Prüfungsfeedback", "Zeitpunkt der letzten Änderung"]
    columns_to_delete = [col for col in df.columns if any(keyword in col for keyword in keywords)]
    columns_to_delete.append("E-Mail")

    # Drop unnecessary columns
    df.drop(columns=columns_to_delete, inplace=True)

def sort_columns(df):
    # Extrahieren der Fragen aus dem Dictionary in der gewünschten Reihenfolge
    ordered_questions = []
    for category, subcategories in questions.items():
        for subcategory, types in subcategories.items():
            for q_type, question in types.items():
                ordered_questions.append(question)
    
    # Filtern der Spalten im DataFrame, die in der gewünschten Reihenfolge vorhanden sind
    existing_columns = [col for col in ordered_questions if col in df.columns]

    # Alle Spalten im DataFrame
    all_columns = df.columns.tolist()
    
    # Convertiere die Likert-Fragen zu numerischen Werten
    # Konvertieren der Werte der Fragen-Spalten in numerische Werte
    for column in df.columns:
        if column in ordered_questions:
            df[column] = pd.to_numeric(df[column], errors='coerce')

    # Finden des Startindex für die Fragen im DataFrame
    start_index = min(all_columns.index(col) for col in existing_columns)

    # Neue Spaltenreihenfolge erstellen
    new_order = all_columns[:start_index] + existing_columns + [col for col in all_columns[start_index:] if col not in existing_columns]

    # DataFrame mit neuer Spaltenreihenfolge anzeigen
    df_new = df[new_order]
    return df_new
    
def invert_specified_likert_score(df):
    # Define columns to invert and their new names
    columns_to_invert = [
        "Es ist akzeptabel, meine Social Media Passwörter für meine Arbeitskonten zu verwenden.",
        "Ich darf meine Arbeitspasswörter mit Kollegen teilen.",
        "Ich darf auf alle Links in E-Mails von Leuten, die ich kenne, klicken.",
        "Ich darf E-Mail-Anhänge von unbekannten Absendern öffnen.",
        "Ich darf alle Dateien auf meinen Arbeitscomputer herunterladen, wenn sie mir helfen, meine Arbeit zu erledigen.",
        "Ich darf jede Information auf jeder Website eingeben, wenn sie mir hilft, meine Arbeit zu erledigen.",
        "Ich kann in den sozialen Medien über meine Arbeit posten, was ich will.",
        "Ich darf sensible Arbeitsdateien über ein öffentliches Wi-Fi-Netz versenden.",
        "Sensible Ausdrucke können auf die gleiche Weise wie nicht sensible Ausdrucke entsorgt werden.",
        "Ich darf Ausdrucke mit sensiblen Informationen über Nacht auf meinem Schreibtisch liegen lassen.",
        "Die Meldung von Sicherheitsvorfällen ist freiwillig.",
        "Es ist sicher, dasselbe Passwort für soziale Medien und Arbeitskonten zu verwenden.",
        "Es ist sicher, ein Arbeitspasswort zu haben, das nur aus Buchstaben besteht.",
        "Es ist immer sicher, auf Links in E-Mails von Leuten zu klicken, die ich kenne.",
        "Es kann nichts Schlimmes passieren, wenn ich auf einen Link in einer E-Mail von einem unbekannten Absender klicke.",
        "Wenn es mir hilft, meine Arbeit zu erledigen, spielt es keine Rolle, welche Informationen ich auf einer Website eingebe.",
        "Es macht nichts, wenn ich in den sozialen Medien Dinge poste, die ich normalerweise in der Öffentlichkeit nicht sagen würde.",
        "Wenn ich in einem Café arbeite, kann ich meinen Laptop ruhig eine Minute lang unbeaufsichtigt lassen.",
        "Die Entsorgung sensibler Ausdrucke in den Mülleimer ist sicher.",
        "Wenn ich einen USB-Stick an einem öffentlichen Ort finde, kann nichts Schlimmes passieren, wenn ich ihn an meinen Arbeitscomputer anschließe.",
        "Wenn ich jemanden ignoriere, der sich an meinem Arbeitsplatz verdächtig verhält, kann nichts Schlimmes passieren.",
        "Es kann nichts Schlimmes passieren, wenn ich das schlechte Sicherheitsverhalten eines Kollegen ignoriere.",
        "Ich gebe meine Arbeitspasswörter an Kollegen weiter.",
        "Wenn eine E-Mail von einem unbekannten Absender interessant aussieht, klicke ich auf einen darin enthaltenen Link.",
        "Ich lade alle Dateien auf meinen Arbeitscomputer herunter, die mir helfen, meine Arbeit zu erledigen.",
        "Wenn ich bei der Arbeit auf das Internet zugreife, besuche ich jede Website, die ich möchte.",
        "Ich poste über meine Arbeit in den sozialen Medien, was ich will.",
        "Ich sende sensible Arbeitsdateien über ein öffentliches Wi-Fi-Netz.",
        "Ich lasse Ausdrucke mit sensiblen Informationen auf meinem Schreibtisch liegen, wenn ich nicht da bin.",
        "Wenn ich bemerken würde, dass mein Kollege die Sicherheitsvorschriften ignoriert, würde ich nichts unternehmen.",
        "Wenn ich an einem öffentlichen Ort arbeite, lasse ich meinen Laptop unbeaufsichtigt.",
        "Ich überprüfe meine Privatsphäre-Einstellungen in den sozialen Medien nicht regelmäßig.",
        "Ich kann nicht für etwas gekündigt werden, das ich in den sozialen Medien poste."
    ]

    inverted_column_names = [
        "Es ist nicht akzeptabel, meine Social Media Passwörter für meine Arbeitskonten zu verwenden.",
        "Ich darf meine Arbeitspasswörter nicht mit Kollegen teilen.",
        "Ich darf nicht auf alle Links in E-Mails von Leuten, die ich kenne, klicken.",
        "Ich darf E-Mail-Anhänge von unbekannten Absendern nicht öffnen.",
        "Ich darf nicht alle Dateien auf meinen Arbeitscomputer herunterladen, auch wenn sie mir helfen, meine Arbeit zu erledigen.",
        "Ich darf nicht jede Information auf jeder Website eingeben, auch wenn sie mir hilft, meine Arbeit zu erledigen.",
        "Ich kann in den sozialen Medien über meine Arbeit nicht posten, was ich will.",
        "Ich darf sensible Arbeitsdateien nicht über ein öffentliches Wi-Fi-Netz versenden.",
        "Sensible Ausdrucke können nicht auf die gleiche Weise wie nicht sensible Ausdrucke entsorgt werden.",
        "Ich darf Ausdrucke mit sensiblen Informationen nicht über Nacht auf meinem Schreibtisch liegen lassen.",
        "Die Meldung von Sicherheitsvorfällen ist nicht freiwillig.",
        "Es ist nicht sicher, dasselbe Passwort für soziale Medien und Arbeitskonten zu verwenden.",
        "Es ist nicht sicher, ein Arbeitspasswort zu haben, das nur aus Buchstaben besteht.",
        "Es ist nicht immer sicher, auf Links in E-Mails von Leuten zu klicken, die ich kenne.",
        "Es kann Schlimmes passieren, wenn ich auf einen Link in einer E-Mail von einem unbekannten Absender klicke.",
        "Auch wenn es mir hilft, meine Arbeit zu erledigen, spielt es eine Rolle, welche Informationen ich auf einer Website eingebe.",
        "Es macht etwas, wenn ich in den sozialen Medien Dinge poste, die ich normalerweise in der Öffentlichkeit nicht sagen würde.",
        "Wenn ich in einem Café arbeite, kann ich meinen Laptop nicht eine Minute lang unbeaufsichtigt lassen.",
        "Die Entsorgung sensibler Ausdrucke in den Mülleimer ist nicht sicher.",
        "Wenn ich einen USB-Stick an einem öffentlichen Ort finde, kann etwas Schlimmes passieren, wenn ich ihn an meinen Arbeitscomputer anschließe.",
        "Wenn ich jemanden ignoriere, der sich an meinem Arbeitsplatz verdächtig verhält, kann etwas Schlimmes passieren.",
        "Es kann etwas Schlimmes passieren, wenn ich das schlechte Sicherheitsverhalten eines Kollegen ignoriere.",
        "Ich gebe meine Arbeitspasswörter nicht an Kollegen weiter.",
        "Wenn eine E-Mail von einem unbekannten Absender interessant aussieht, klicke ich nicht auf einen darin enthaltenen Link.",
        "Ich lade nicht alle Dateien auf meinen Arbeitscomputer herunter, die mir helfen, meine Arbeit zu erledigen.",
        "Wenn ich bei der Arbeit auf das Internet zugreife, besuche ich nicht jede Website, die ich möchte.",
        "Ich poste über meine Arbeit in den sozialen Medien, nicht was ich will.",
        "Ich sende sensible Arbeitsdateien nicht über ein öffentliches Wi-Fi-Netz.",
        "Ich lasse Ausdrucke mit sensiblen Informationen nicht auf meinem Schreibtisch liegen, wenn ich nicht da bin.",
        "Wenn ich bemerken würde, dass mein Kollege die Sicherheitsvorschriften ignoriert, würde ich etwas unternehmen.",
        "Wenn ich an einem öffentlichen Ort arbeite, lasse ich meinen Laptop nicht unbeaufsichtigt.",
        "Ich überprüfe meine Privatsphäre-Einstellungen in den sozialen Medien regelmäßig.",
        "Ich kann für etwas gekündigt werden, das ich in den sozialen Medien poste."
    ]

    # Invert Likert scale for marked questions
    invert_likert = lambda x: 6 - int(x)
    for old_col, new_col in zip(columns_to_invert, inverted_column_names):
        if old_col in df.columns:
            df[old_col] = df[old_col].apply(invert_likert)
            df.rename(columns={old_col: new_col}, inplace=True)

def add_participant_group_to_df(df, filename):
    s = os.path.splitext(filename)[0].split("-")
    if 'LH' in s:
        df.insert(1, "Massnahme", "1")
    elif 'ER' in s:
        df.insert(1, "Massnahme", "2")
        
    if 'pre' in s:
        df.insert(2, "Gruppe", "1")
    elif 'post' in s:
        df.insert(2, "Gruppe", "2")
    
    return df
    
def combine_dataframes(df1, df2):
    df_combined = pd.concat([df1, df2], axis=0, ignore_index=True).fillna("Null")
    return df_combined

def write_df_to_file(df, filename):
    # Save the dataframe
    
    #os.path.splitext(filepath)[0] + '.csv'
    df.to_csv(filename, index=False)
    #print(f"Sanitized file saved as {filename}")
    logger.info(f"Dataframe saved as {filename}")

def sanitize_ms_forms_excel(input_file):
    # Read and store content of an excel file
    logger.info(f"Sanitizing file {input_file}")
    df = pd.read_excel(input_file)

    # Drop unnecessary columns
    drop_unnecessary_columns(df)

    # Replace Likert-Scale text values with corresponding numbers
    likert_text_to_number = {
        'Stimme überhaupt nicht zu': '1', 
        'Stimme nicht zu': '2',
        'Neutral': '3', 
        'Stimme zu': '4',
        'Stimme voll und ganz zu': '5'
    }
    df.replace(likert_text_to_number, inplace=True)

    # Normalize column names
    df.columns = df.columns.str.strip()

    rename_columns(df)
    
    df = add_participant_group_to_df(df, input_file)

    # Check for responses made without due care
    # TODO: Add Check for same value over all columns

    invert_specified_likert_score(df)
    
    df = sort_columns(df)

    # Save the dataframe
    suffix = "sanitized"
    new_filename = add_suffix_to_filename(input_file, suffix)
    output_df = df #add_suffix_to_columnname(df)

    write_df_to_file(output_df, new_filename)
    return df

def generate_complete_summary_csv(pre_questionaire_df, post_questionaire_df, treatment):
    import copy
    results = []

    # treatment = "LH"
    # pre_questionaire_df = df_lh_pre
    # post_questionaire_df = df_lh_post

    #qresults = questions.copy()
    qresults = copy.deepcopy(questions)

    total_mean_pre = []
    total_sd_pre = []
    total_mean_post = []
    total_sd_post = []

    total_knowledge_mean_pre = []
    total_knowledge_sd_pre = []
    total_knowledge_mean_post = []
    total_knowledge_sd_post = []

    total_attitude_mean_pre = []
    total_attitude_sd_pre = []
    total_attitude_mean_post = []
    total_attitude_sd_post = []

    total_behaviour_mean_pre = []
    total_behaviour_sd_pre = []
    total_behaviour_mean_post = []
    total_behaviour_sd_post = []

    for category, subcategories in questions.items():
        #print(category)

        category_mean_pre = []
        category_sd_pre = []
        category_mean_post = []
        category_sd_post = []

        category_knowledge_mean_pre = []
        category_knowledge_sd_pre = []
        category_knowledge_mean_post = []
        category_knowledge_sd_post = []

        category_attitude_mean_pre = []
        category_attitude_sd_pre = []
        category_attitude_mean_post = []
        category_attitude_sd_post = []

        category_behaviour_mean_pre = []
        category_behaviour_sd_pre = []
        category_behaviour_mean_post = []
        category_behaviour_sd_post = []
        
        for subcategory, dimensions in subcategories.items():
            #print("-", subcategory)

            subcategory_mean_pre = []
            subcategory_sd_pre = []
            subcategory_mean_post = []
            subcategory_sd_post = []

            for dimension, question in dimensions.items():
                #print("--", dimension, question)

                mean_pre = pre_questionaire_df[question].mean()
                sd_pre = pre_questionaire_df[question].std()
                mean_post = post_questionaire_df[question].mean()
                sd_post = post_questionaire_df[question].std()
                cohens_d = calculate_cohens_d(mean_pre, mean_post, sd_pre, sd_post, len(pre_questionaire_df), len(post_questionaire_df))
                mean_diff = mean_post - mean_pre
                # save results per question (=Subkategorie-Dimension)
                qresults[category][subcategory][dimension] = {
                    "mean_pre": float(mean_pre),
                    "sd_pre": float(sd_pre),
                    "mean_post": float(mean_post),
                    "sd_post": float(sd_post),
                    "cohens_d": float(cohens_d),
                    "mean_diff": float(mean_diff)
                }
                results.append({
                    "Maßnahme": treatment,
                    "Kategorie": category,
                    "Subkategorie": subcategory,
                    "Dimension": dimension,
                    "mean_pre": float(mean_pre),
                    "sd_pre": float(sd_pre),
                    "mean_post": float(mean_post),
                    "sd_post": float(sd_post),
                    "cohens_d": float(cohens_d),
                    "mean_diff": float(mean_diff)
                })
                subcategory_mean_pre.append(mean_pre)
                subcategory_sd_pre.append(sd_pre)
                subcategory_mean_post.append(mean_post)
                subcategory_sd_post.append(sd_post)

                category_mean_pre.append(mean_pre)
                category_sd_pre.append(sd_pre)
                category_mean_post.append(mean_post)
                category_sd_post.append(sd_post)

                total_mean_pre.append(mean_pre)
                total_sd_pre.append(sd_pre)
                total_mean_post.append(mean_post)
                total_sd_post.append(sd_post)

                if dimension == "Wissen":
                    category_knowledge_mean_pre.append(mean_pre)
                    category_knowledge_sd_pre.append(sd_pre)
                    category_knowledge_mean_post.append(mean_post)
                    category_knowledge_sd_post.append(sd_post)

                    total_knowledge_mean_pre.append(mean_pre)
                    total_knowledge_sd_pre.append(sd_pre)
                    total_knowledge_mean_post.append(mean_post)
                    total_knowledge_sd_post.append(sd_post)
                elif dimension == "Einstellung":
                    category_attitude_mean_pre.append(mean_pre)
                    category_attitude_sd_pre.append(sd_pre)
                    category_attitude_mean_post.append(mean_post)
                    category_attitude_sd_post.append(sd_post)

                    total_attitude_mean_pre.append(mean_pre)
                    total_attitude_sd_pre.append(sd_pre)
                    total_attitude_mean_post.append(mean_post)
                    total_attitude_sd_post.append(sd_post)
                elif dimension == "Verhalten":
                    category_behaviour_mean_pre.append(mean_pre)
                    category_behaviour_sd_pre.append(sd_pre)
                    category_behaviour_mean_post.append(mean_post)
                    category_behaviour_sd_post.append(sd_post)

                    total_behaviour_mean_pre.append(mean_pre)
                    total_behaviour_sd_pre.append(sd_pre)
                    total_behaviour_mean_post.append(mean_post)
                    total_behaviour_sd_post.append(sd_post)
                #break
            subcategory_mean_pre_val = np.mean(subcategory_mean_pre)
            subcategory_sd_pre_val = np.mean(subcategory_sd_pre)
            subcategory_mean_post_val = np.mean(subcategory_mean_post)
            subcategory_sd_post_val = np.mean(subcategory_sd_post)

            qresults[category][subcategory]["Gesamt"] = {
                "subcategory_mean_pre": float(subcategory_mean_pre_val),
                "subcategory_sd_pre": float(subcategory_sd_pre_val),
                "subcategory_mean_post": float(subcategory_mean_post_val),
                "subcategory_sd_post": float(subcategory_sd_post_val),
                "subcategory_cohens_d": float(calculate_cohens_d(subcategory_mean_pre_val,subcategory_mean_post_val,subcategory_sd_pre_val,subcategory_sd_post_val,len(pre_questionaire_df), len(post_questionaire_df))),
                "subcategory_mean_diff": float(subcategory_mean_post_val-subcategory_mean_pre_val)
            }
            results.append({
                "Maßnahme": treatment,
                "Kategorie": category,
                "Subkategorie": subcategory,
                "Dimension": "Gesamt",
                "mean_pre": float(subcategory_mean_pre_val),
                "sd_pre": float(subcategory_sd_pre_val),
                "mean_post": float(subcategory_mean_post_val),
                "sd_post": float(subcategory_sd_post_val),
                "cohens_d": float(calculate_cohens_d(subcategory_mean_pre_val,subcategory_mean_post_val,subcategory_sd_pre_val,subcategory_sd_post_val,len(pre_questionaire_df), len(post_questionaire_df))),
                "mean_diff": float(subcategory_mean_post_val-subcategory_mean_pre_val)
            })
            #break
        # Wissen
        category_knowledge_mean_pre_val = np.mean(category_knowledge_mean_pre)
        category_knowledge_sd_pre_val = np.mean(category_knowledge_sd_pre)
        category_knowledge_mean_post_val = np.mean(category_knowledge_mean_post)
        category_knowledge_sd_post_val = np.mean(category_knowledge_sd_post)
        qresults[category]["Wissen"] = {
            "category_mean_pre": float(category_knowledge_mean_pre_val),
            "category_sd_pre": float(category_knowledge_sd_pre_val),
            "category_mean_post": float(category_knowledge_mean_post_val),
            "category_sd_post": float(category_knowledge_sd_post_val),
            "category_cohens_d": float(calculate_cohens_d(category_knowledge_mean_pre_val,category_knowledge_mean_post_val,category_knowledge_sd_pre_val,category_knowledge_sd_post_val,len(pre_questionaire_df), len(post_questionaire_df))),
            "category_mean_diff": float(category_knowledge_mean_post_val-category_knowledge_mean_pre_val)
        }
        results.append({
            "Maßnahme": treatment,
            "Kategorie": category,
            "Subkategorie": "Gesamt",
            "Dimension": "Wissen",
            "mean_pre": float(category_knowledge_mean_pre_val),
            "sd_pre": float(category_knowledge_sd_pre_val),
            "mean_post": float(category_knowledge_mean_post_val),
            "sd_post": float(category_knowledge_sd_post_val),
            "cohens_d": float(calculate_cohens_d(category_knowledge_mean_pre_val,category_knowledge_mean_post_val,category_knowledge_sd_pre_val,category_knowledge_sd_post_val,len(pre_questionaire_df), len(post_questionaire_df))),
            "mean_diff": float(category_knowledge_mean_post_val-category_knowledge_mean_pre_val)
        })
        # Einstellung
        category_attitude_mean_pre_val = np.mean(category_attitude_mean_pre)
        category_attitude_sd_pre_val = np.mean(category_attitude_sd_pre)
        category_attitude_mean_post_val = np.mean(category_attitude_mean_post)
        category_attitude_sd_post_val = np.mean(category_attitude_sd_post)
        qresults[category]["Einstellung"] = {
            "category_mean_pre": float(category_attitude_mean_pre_val),
            "category_sd_pre": float(category_attitude_sd_pre_val),
            "category_mean_post": float(category_attitude_mean_post_val),
            "category_sd_post": float(category_attitude_sd_post_val),
            "category_cohens_d": float(calculate_cohens_d(category_attitude_mean_pre_val,category_attitude_mean_post_val,category_attitude_sd_pre_val,category_attitude_sd_post_val,len(pre_questionaire_df), len(post_questionaire_df))),
            "category_mean_diff": float(category_attitude_mean_post_val-category_attitude_mean_pre_val)
        }
        results.append({
            "Maßnahme": treatment,
            "Kategorie": category,
            "Subkategorie": "Gesamt",
            "Dimension": "Einstellung",
            "mean_pre": float(category_attitude_mean_pre_val),
            "sd_pre": float(category_attitude_sd_pre_val),
            "mean_post": float(category_attitude_mean_post_val),
            "sd_post": float(category_attitude_sd_post_val),
            "cohens_d": float(calculate_cohens_d(category_attitude_mean_pre_val,category_attitude_mean_post_val,category_attitude_sd_pre_val,category_attitude_sd_post_val,len(pre_questionaire_df), len(post_questionaire_df))),
            "mean_diff": float(category_attitude_mean_post_val-category_attitude_mean_pre_val)
        })
        # Verhalten
        category_behaviour_mean_pre_val = np.mean(category_behaviour_mean_pre)
        category_behaviour_sd_pre_val = np.mean(category_behaviour_sd_pre)
        category_behaviour_mean_post_val = np.mean(category_behaviour_mean_post)
        category_behaviour_sd_post_val = np.mean(category_behaviour_sd_post)
        qresults[category]["Verhalten"] = {
            "category_mean_pre": float(category_behaviour_mean_pre_val),
            "category_sd_pre": float(category_behaviour_sd_pre_val),
            "category_mean_post": float(category_behaviour_mean_post_val),
            "category_sd_post": float(category_behaviour_sd_post_val),
            "category_cohens_d": float(calculate_cohens_d(category_behaviour_mean_pre_val,category_behaviour_mean_post_val,category_behaviour_sd_pre_val,category_behaviour_sd_post_val,len(pre_questionaire_df), len(post_questionaire_df))),
            "category_mean_diff": float(category_behaviour_mean_post_val-category_behaviour_mean_pre_val)
        }
        results.append({
            "Maßnahme": treatment,
            "Kategorie": category,
            "Subkategorie": "Gesamt",
            "Dimension": "Verhalten",
            "mean_pre": float(category_behaviour_mean_pre_val),
            "sd_pre": float(category_behaviour_sd_pre_val),
            "mean_post": float(category_behaviour_mean_post_val),
            "sd_post": float(category_behaviour_sd_post_val),
            "cohens_d": float(calculate_cohens_d(category_behaviour_mean_pre_val,category_behaviour_mean_post_val,category_behaviour_sd_pre_val,category_behaviour_sd_post_val,len(pre_questionaire_df), len(post_questionaire_df))),
            "mean_diff": float(category_behaviour_mean_post_val-category_behaviour_mean_pre_val)
        })
        # Gesamt
        category_mean_pre_val = np.mean(category_mean_pre)
        category_sd_pre_val = np.mean(category_sd_pre)
        category_mean_post_val = np.mean(category_mean_post)
        category_sd_post_val = np.mean(category_sd_post)
        qresults[category]["Gesamt"] = {
            "category_mean_pre": float(category_mean_pre_val),
            "category_sd_pre": float(category_sd_pre_val),
            "category_mean_post": float(category_mean_post_val),
            "category_sd_post": float(category_sd_post_val),
            "category_cohens_d": float(calculate_cohens_d(category_mean_pre_val,category_mean_post_val,category_sd_pre_val,category_sd_post_val,len(pre_questionaire_df), len(post_questionaire_df))),
            "category_mean_diff": float(category_mean_post_val-category_mean_pre_val)
        }
        results.append({
            "Maßnahme": treatment,
            "Kategorie": category,
            "Subkategorie": "Gesamt",
            "Dimension": "Gesamt",
            "mean_pre": float(category_mean_pre_val),
            "sd_pre": float(category_sd_pre_val),
            "mean_post": float(category_mean_post_val),
            "sd_post": float(category_sd_post_val),
            "cohens_d": float(calculate_cohens_d(category_mean_pre_val,category_mean_post_val,category_sd_pre_val,category_sd_post_val,len(pre_questionaire_df), len(post_questionaire_df))),
            "mean_diff": float(category_mean_post_val-category_mean_pre_val)
        })
        #break

    # Wissen
    total_knowledge_mean_pre_val = np.mean(total_knowledge_mean_pre)
    total_knowledge_sd_pre_val = np.mean(total_knowledge_sd_pre)
    total_knowledge_mean_post_val = np.mean(total_knowledge_mean_post)
    total_knowledge_sd_post_val = np.mean(total_knowledge_sd_post)
    qresults["Wissen"] = {
        "total_mean_pre": float(total_knowledge_mean_pre_val),
        "total_sd_pre": float(total_knowledge_sd_pre_val),
        "total_mean_post": float(total_knowledge_mean_post_val),
        "total_sd_post": float(total_knowledge_sd_post_val),
        "total_cohens_d": float(calculate_cohens_d(total_knowledge_mean_pre_val,total_knowledge_mean_post_val,total_knowledge_sd_pre_val,total_knowledge_sd_post_val,len(pre_questionaire_df), len(post_questionaire_df))),
        "total_mean_diff": float(total_knowledge_mean_post_val-total_knowledge_mean_pre_val)
    }
    results.append({
        "Maßnahme": treatment,
        "Kategorie": "Gesamt",
        "Subkategorie": "Gesamt",
        "Dimension": "Wissen",
        "mean_pre": float(total_knowledge_mean_pre_val),
        "sd_pre": float(total_knowledge_sd_pre_val),
        "mean_post": float(total_knowledge_mean_post_val),
        "sd_post": float(total_knowledge_sd_post_val),
        "cohens_d": float(calculate_cohens_d(total_knowledge_mean_pre_val,total_knowledge_mean_post_val,total_knowledge_sd_pre_val,total_knowledge_sd_post_val,len(pre_questionaire_df), len(post_questionaire_df))),
        "mean_diff": float(total_knowledge_mean_post_val-total_knowledge_mean_pre_val)
    })
    # Einstellung
    total_attitude_mean_pre_val = np.mean(total_attitude_mean_pre)
    total_attitude_sd_pre_val = np.mean(total_attitude_sd_pre)
    total_attitude_mean_post_val = np.mean(total_attitude_mean_post)
    total_attitude_sd_post_val = np.mean(total_attitude_sd_post)
    qresults["Einstellung"] = {
        "total_mean_pre": float(total_attitude_mean_pre_val),
        "total_sd_pre": float(total_attitude_sd_pre_val),
        "total_mean_post": float(total_attitude_mean_post_val),
        "total_sd_post": float(total_attitude_sd_post_val),
        "total_cohens_d": float(calculate_cohens_d(total_attitude_mean_pre_val,total_attitude_mean_post_val,total_attitude_sd_pre_val,total_attitude_sd_post_val,len(pre_questionaire_df), len(post_questionaire_df))),
        "total_mean_diff": float(total_attitude_mean_post_val-total_attitude_mean_pre_val)
    }
    results.append({
        "Maßnahme": treatment,
        "Kategorie": "Gesamt",
        "Subkategorie": "Gesamt",
        "Dimension": "Einstellung",
        "mean_pre": float(total_attitude_mean_pre_val),
        "sd_pre": float(total_attitude_sd_pre_val),
        "mean_post": float(total_attitude_mean_post_val),
        "sd_post": float(total_attitude_sd_post_val),
        "cohens_d": float(calculate_cohens_d(total_attitude_mean_pre_val,total_attitude_mean_post_val,total_attitude_sd_pre_val,total_attitude_sd_post_val,len(pre_questionaire_df), len(post_questionaire_df))),
        "mean_diff": float(total_attitude_mean_post_val-total_attitude_mean_pre_val)
    })
    # Verhalten
    total_behaviour_mean_pre_val = np.mean(total_behaviour_mean_pre)
    total_behaviour_sd_pre_val = np.mean(total_behaviour_sd_pre)
    total_behaviour_mean_post_val = np.mean(total_behaviour_mean_post)
    total_behaviour_sd_post_val = np.mean(total_behaviour_sd_post)
    qresults["Verhalten"] = {
        "total_mean_pre": float(total_behaviour_mean_pre_val),
        "total_sd_pre": float(total_behaviour_sd_pre_val),
        "total_mean_post": float(total_behaviour_mean_post_val),
        "total_sd_post": float(total_behaviour_sd_post_val),
        "total_cohens_d": float(calculate_cohens_d(total_behaviour_mean_pre_val,total_behaviour_mean_post_val,total_behaviour_sd_pre_val,total_behaviour_sd_post_val,len(pre_questionaire_df), len(post_questionaire_df))),
        "total_mean_diff": float(total_behaviour_mean_post_val-total_behaviour_mean_pre_val)
    }
    results.append({
        "Maßnahme": treatment,
        "Kategorie": "Gesamt",
        "Subkategorie": "Gesamt",
        "Dimension": "Verhalten",
        "mean_pre": float(total_behaviour_mean_pre_val),
        "sd_pre": float(total_behaviour_sd_pre_val),
        "mean_post": float(total_behaviour_mean_post_val),
        "sd_post": float(total_behaviour_sd_post_val),
        "cohens_d": float(calculate_cohens_d(total_behaviour_mean_pre_val,total_behaviour_mean_post_val,total_behaviour_sd_pre_val,total_behaviour_sd_post_val,len(pre_questionaire_df), len(post_questionaire_df))),
        "mean_diff": float(total_behaviour_mean_post_val-total_behaviour_mean_pre_val)
    })
    # Gesamt
    total_mean_pre_val = np.mean(total_mean_pre)
    total_sd_pre_val = np.mean(total_sd_pre)
    total_mean_post_val = np.mean(total_mean_post)
    total_sd_post_val = np.mean(total_sd_post)
    qresults["Gesamt"] = {
        "total_mean_pre": float(total_mean_pre_val),
        "total_sd_pre": float(total_sd_pre_val),
        "total_mean_post": float(total_mean_post_val),
        "total_sd_post": float(total_sd_post_val),
        "total_cohens_d": float(calculate_cohens_d(total_mean_pre_val,total_mean_post_val,total_sd_pre_val,total_sd_post_val,len(pre_questionaire_df), len(post_questionaire_df))),
        "total_mean_diff": float(total_mean_post_val-total_mean_pre_val)
    }
    results.append({
        "Maßnahme": treatment,
        "Kategorie": "Gesamt",
        "Subkategorie": "Gesamt",
        "Dimension": "Gesamt",
        "mean_pre": float(total_mean_pre_val),
        "sd_pre": float(total_sd_pre_val),
        "mean_post": float(total_mean_post_val),
        "sd_post": float(total_sd_post_val),
        "cohens_d": float(calculate_cohens_d(total_mean_pre_val,total_mean_post_val,total_sd_pre_val,total_sd_post_val,len(pre_questionaire_df), len(post_questionaire_df))),
        "mean_diff": float(total_mean_post_val-total_mean_pre_val)
    })

    df_results = pd.DataFrame(results)
    return df_results, qresults

def analyse(pre_questionaire_df, post_questionaire_df):
    df_pre = pre_questionaire_df
    df_post = post_questionaire_df

    results = []

    # Berechnung der Mittelwerte und Standardabweichungen für jede Frage
    for group, df in [("Pre", df_pre), ("Post", df_post)]:
        for category, subcategories in questions.items():
            for subcategory, dimensions in subcategories.items():
                for dimension, question in dimensions.items():
                    mean_value = df[question].mean()
                    std_value = df[question].std()
                    results.append({
                        "Gruppe": group,
                        "Kategorie": category,
                        "Subkategorie": subcategory,
                        "Dimension": dimension,
                        "Mean": mean_value,
                        "SD": std_value
                    })

    df_results = pd.DataFrame(results)

    # Berechnung der Gesamtmittelwerte und Standardabweichungen pro Dimension für jede Kategorie
    category_dimension_results = df_results.groupby(["Gruppe", "Kategorie", "Dimension"]).agg({"Mean": "mean", "SD": "std"}).reset_index()
    
    # Berechnung der Gesamtmittelwerte und Standardabweichungen für jede Kategorie über alle Dimensionen hinweg
    category_overall_results = df_results.groupby(["Gruppe", "Kategorie"]).agg({"Mean": "mean", "SD": "std"}).reset_index()
    category_overall_results["Dimension"] = "Gesamt"

    # Zusammenführen der Ergebnisse
    df_output = pd.concat([df_results, category_dimension_results, category_overall_results], ignore_index=True)
    
    return df_output


# def generate_summary_csv(pre_questionaire_df, post_questionaire_df, output_filename):
#     results = []

#     # Berechnung der Mittelwerte, Standardabweichungen und Cohen's d für jede Frage
#     for category, subcategories in questions.items():
#         for subcategory, dimensions in subcategories.items():
#             mean_pre = {}
#             sd_pre = {}
#             mean_post = {}
#             sd_post = {}
            
#             for dimension, question in dimensions.items():
#                 mean_pre[dimension] = pre_questionaire_df[question].mean()
#                 sd_pre[dimension] = pre_questionaire_df[question].std()
#                 mean_post[dimension] = post_questionaire_df[question].mean()
#                 sd_post[dimension] = post_questionaire_df[question].std()
            
#             for dimension, question in dimensions.items():
#                 cohens_d = calculate_cohens_d(
#                     mean_pre[dimension], mean_post[dimension],
#                     sd_pre[dimension], sd_post[dimension],
#                     len(pre_questionaire_df), len(post_questionaire_df)
#                 )
#                 results.append({
#                     "Kategorie": f"{category} - {subcategory} ({dimension})",
#                     "Mean_pre": mean_pre[dimension],
#                     "SD_pre": sd_pre[dimension],
#                     "Mean_post": mean_post[dimension],
#                     "SD_post": sd_post[dimension],
#                     "cohens_d": cohens_d
#                 })
            
#             overall_mean_pre = np.mean(list(mean_pre.values()))
#             overall_sd_pre = np.mean(list(sd_pre.values()))
#             overall_mean_post = np.mean(list(mean_post.values()))
#             overall_sd_post = np.mean(list(sd_post.values()))
#             overall_cohens_d = calculate_cohens_d(
#                 overall_mean_pre, overall_mean_post,
#                 overall_sd_pre, overall_sd_post,
#                 len(pre_questionaire_df), len(post_questionaire_df)
#             )
#             results.append({
#                 "Kategorie": f"{category} - Gesamt",
#                 "Mean_pre": overall_mean_pre,
#                 "SD_pre": overall_sd_pre,
#                 "Mean_post": overall_mean_post,
#                 "SD_post": overall_sd_post,
#                 "cohens_d": overall_cohens_d
#             })

#     df_results = pd.DataFrame(results)
#     df_results = df_results.round(2)  # Rundet alle numerischen Werte auf 2 Nachkommastellen

#     df_results.to_csv(output_filename, index=False)
#     logger.info(f"Summary CSV generated and saved as {output_filename}")
#     return df_results


# def generate_detailed_summary_csv(pre_questionaire_df, post_questionaire_df, treatment, output_filename):
#     results = []

#     for category, subcategories in questions.items():
#         for subcategory, dimensions in subcategories.items():
#             mean_pre = {}
#             sd_pre = {}
#             mean_post = {}
#             sd_post = {}
            
#             for dimension, question in dimensions.items():
#                 mean_pre[dimension] = pre_questionaire_df[question].mean()
#                 sd_pre[dimension] = pre_questionaire_df[question].std()
#                 mean_post[dimension] = post_questionaire_df[question].mean()
#                 sd_post[dimension] = post_questionaire_df[question].std()
            
#             overall_mean_pre = np.mean(list(mean_pre.values()))
#             overall_sd_pre = np.mean(list(sd_pre.values()))
#             overall_mean_post = np.mean(list(mean_post.values()))
#             overall_sd_post = np.mean(list(sd_post.values()))
#             mean_diff = abs(overall_mean_pre - overall_mean_post)
            
#             results.append({
#                 "Maßnahme": treatment,
#                 "Kategorie": category,
#                 "Subkategorie": subcategory,
#                 "Mean_pre": overall_mean_pre,
#                 "SD_pre": overall_sd_pre,
#                 "Mean_post": overall_mean_post,
#                 "SD_post": overall_sd_post,
#                 "Mean_diff": mean_diff
#             })

#     df_results = pd.DataFrame(results)
#     df_results = df_results.round(2)  # Rundet alle numerischen Werte auf 2 Nachkommastellen

#     df_results.to_csv(output_filename, index=False)
#     logger.info(f"Detailed summary CSV generated and saved as {output_filename}")
#     return df_results


def main(lh_pre_excel_filepath, lh_post_excel_filepath, er_pre_excel_filepath, er_post_excel_filepath):
    start = timeit.default_timer()
    logger.info("Starting")
    logger.info("Checking if input files exist.")
    if not os.path.exists(lh_pre_excel_filepath):
        logger.error(f"File {lh_pre_excel_filepath} does not exist.")
        return
    if not os.path.exists(lh_post_excel_filepath):
        logger.error(f"File {lh_post_excel_filepath} does not exist.")
        return
    if not os.path.exists(er_pre_excel_filepath):
        logger.error(f"File {er_pre_excel_filepath} does not exist.")
        return
    if not os.path.exists(er_post_excel_filepath):
        logger.error(f"File {er_post_excel_filepath} does not exist.")
        return
    # Schritt 1: Bereinigung der Excel-Dateien
    lh_pre_df = sanitize_ms_forms_excel(lh_pre_excel_filepath)
    lh_post_df = sanitize_ms_forms_excel(lh_post_excel_filepath)
    
    er_pre_df = sanitize_ms_forms_excel(er_pre_excel_filepath)
    er_post_df = sanitize_ms_forms_excel(er_post_excel_filepath)
    
    lh_comb_df = combine_dataframes(lh_pre_df, lh_post_df)
    er_comb_df = combine_dataframes(er_pre_df, er_post_df)
    
    lh_er_comb_df = combine_dataframes(lh_comb_df, er_comb_df)
    
    lh_comb_filename = add_suffix_to_filename(lh_pre_excel_filepath, "combined", ["pre", "post"])
    er_comb_filename = add_suffix_to_filename(er_pre_excel_filepath, "combined", ["pre", "post"])
    
    write_df_to_file(lh_comb_df, lh_comb_filename)
    write_df_to_file(er_comb_df, er_comb_filename)
    write_df_to_file(lh_er_comb_df,"lh_er_comb.csv")
    
    # Schritt 2: Analyse der bereinigten CSV-Dateien
    df_output_lh = analyse(lh_pre_df, lh_post_df)
    df_output_lh.insert(0, "Massnahme", "1")
    df_output_er = analyse(er_pre_df, er_post_df)
    df_output_er.insert(0, "Massnahme", "2")

    df_sum_results_lh = generate_complete_summary_csv(lh_pre_df, lh_post_df, "LH")
    df_sum_results_er = generate_complete_summary_csv(er_pre_df, er_post_df, "ER")
    df_lh_er_sum_results = pd.concat([df_sum_results_lh, df_sum_results_er], axis=0, ignore_index=True)
    output_filename = "LH-ER-Sum-Results.csv"
    write_df_to_file(df_lh_er_sum_results, output_filename)

    # df_det_sum_results_lh = generate_detailed_summary_csv(lh_pre_df, lh_post_df, "LH", "detailed_summary_results.csv")
    # df_det_sum_results_er = generate_detailed_summary_csv(er_pre_df, er_post_df, "ER", "detailed_summary_results.csv")
    # df_lh_er_det_sum_results = pd.concat([df_det_sum_results_lh, df_det_sum_results_er], axis=0, ignore_index=True)
    # output_filename = "LH-ER-Det-Sum-Results.csv"
    # write_df_to_file(df_lh_er_det_sum_results, output_filename)

    write_df_to_file(df_output_lh, add_suffix_to_filename(lh_pre_excel_filepath, "results"))
    write_df_to_file(df_output_er, add_suffix_to_filename(er_pre_excel_filepath, "results"))
    
    lh_er_comb_result_df = pd.concat([df_output_lh, df_output_er], axis=0, ignore_index=True).fillna("Gesamt")
    
    # Ausgabe-DataFrame erstellen
    output_filename = "LH-ER-Results-combined.csv"
    write_df_to_file(lh_er_comb_result_df, output_filename)
    
    # Schritt 3: Erzeugen von Plots und Tabellen
    # generate_plots(df_output, "Mean and SD for Categories", "Kategorie")
    # generate_plots(df_output, "Mean and SD for Subcategories", "Subkategorie")
    # Latex Tabelle generieren
    #generate_latex_table(df_output, "latex/results_subkategorie.tex")#, "Kategorie", "latex/results_kategorie.tex")
    # generate_latex_table(df_output, "Subkategorie", "latex/results_subkategorie.tex")
    # generate_latex_table(df_output, "Kategorie", "latex/results_kategorie.tex")
    stop = timeit.default_timer()
    logger.info(f"Total execution time: {stop - start:.2f} seconds.")

if __name__ == "__main__":
    if len(sys.argv) != 5:
        logger.error("Usage: python run_analysis.py <lh_lh_pre_excel_filepath.xlsx> <lh_lh_post_excel_filepath.xlsx> <er_lh_pre_excel_filepath.xlsx> <er_lh_post_excel_filepath.xlsx>")
    else:
        main(sys.argv[1], sys.argv[2], sys.argv[3], sys.argv[4])
