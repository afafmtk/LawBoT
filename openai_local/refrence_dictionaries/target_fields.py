moroccan_regions = [
    "Tanger-Tetouan-Al Hoceima",
    "Oriental",
    "Fes-Meknes",
    "Rabat-Sale-Kenitra",
    "Beni Mellal-Khenifra",
    "Casablanca-Settat",
    "Marrakech-Safi",
    "Draa-Tafilalet",
    "Souss-Massa",
    "Guelmim-Oued Noun",
    "Laayoune-Sakia El Hamra",
    "Dakhla-Oued Ed-Dahab"
]

class FieldPrompts:
    Désignation_Organisme_Expropriant_prompt = (
        "Provide the official name of the organization responsible for the expropriation. "
        "Answer only with the name, nothing else."
    )

    Objet_prompt = (
        "State the object or purpose of the expropriation. "
        "Answer only with the purpose, no explanations."
    )

    Jugement_Ref_prompt = (
        "Enter the official judgment reference if 'حكم' or 'مقرر حكم' is present. "
        "If not found, reply with 'N/A'. Answer only with the reference or 'N/A'."
    )

    Date_Jugement_prompt = (
        "Provide the date of the judgment in the format DD/MM/YYYY if 'حكم' or 'مقرر حكم' is present. "
        "If not found, reply with 'N/A'. Answer only with the date or 'N/A'."
    )

    Num_Décision_prompt = (
        "Provide the official decision number if 'قرار' is present in the text. "
        "If not found, reply with 'N/A'. Answer only with the number or 'N/A'."
    )

    Num_Bulletin_Officiel_prompt = (
        "Enter the number of the official bulletin if 'الجريدة الرسمية' is mentioned. "
        "If not found, reply with 'N/A'. Answer only with the number or 'N/A'."
    )

    Date_Bulletin_Officiel_prompt = (
        "Provide the date when the expropriation was published in the official bulletin in DD/MM/YYYY format if 'الجريدة الرسمية' is mentioned. "
        "If not found, reply with 'N/A'. Answer only with the date or 'N/A'."
    )

    Référence_Loi_prompt = (
        "State the law reference associated with the expropriation. "
        "Answer only with the reference number."
    )

    Référence_Décret_Expropriation_prompt = (
        "Enter the decree reference number in the format 'x.x.xxx' if 'مرسوم' is present. "
        "Answer only with the reference number."
    )

    Région_frappée_par_le_projet_prompt = (
        f"State the Moroccan region affected by the project. "
        f"Answer must match one from this list: {moroccan_regions}. Answer only with the region name."
    )

    Commune_frappée_par_le_projet_prompt = (
        "State the specific commune affected by the project. "
        "Answer only with the commune name."
    )

    Intitulé_Projet_prompt = (
        "Provide the official title of the expropriation project. "
        "Answer only with the project title."
    )

    Tranche_Projet_d_expropriation_prompt = (
        "State the tranche or phase of the expropriation project. "
        "Answer only with the phase details."
    )

    Montant_Total_Projet_prompt = (
        "State the total cost of the project in Moroccan DH. write it from left to right "
        "Answer only with the amount."
    )

    Montant_Global_consigné_prompt = (
        "State the total amount of money deposited for the expropriation in Moroccan DH. "
        "Answer only with the amount."
    )

    Type_Versement_prompt = (
        "Specify the type of payment used in the expropriation process. "
        "Answer only with the payment type."
    )

    Nom_Prénom_prompt = (
        "List all names found accurately in bullet points format. "
        "Answer with the names in bullet points, no additional text."
    )

    Adresse_courrier_prompt = (
        "Provide the full mailing address of the expropriating organization. "
        "Answer only with the address."
    )

    Num_Téléphone_prompt = (
        "Provide the phone number of the expropriating organization, including the international code if applicable. "
        "Answer only with the phone number."
    )

    Localité_prompt = (
        "State the locality where the project is situated. "
        "Answer only with the locality name."
    )

    Identifiant_Fiscal_prompt = (
        "Provide the fiscal identifier (IF) of each company involved, if available. "
        "Answer only with the identifier numbers."
    )


expropriation_data = [
    {
        "field": "Désignation Organisme Expropriant",
        "lookuptext": "text",
        "field_prompt": FieldPrompts.Désignation_Organisme_Expropriant_prompt,
        "dynamic": True,
        "default_value": "N/A",
        "description": "Official name or title of the organization responsible for the expropriation.",
        "regex": r"^[A-Za-z\s]+$"
    },
    {
        "field": "Objet",
        "lookuptext": "text",
        "field_prompt": FieldPrompts.Objet_prompt,
        "dynamic": True,
        "default_value": "N/A",
        "description": "Purpose or reason behind the expropriation project.",
        "regex": r"^[A-Za-z\s]+$"
    },
    {
        "field": "Jugement Ref",
        "lookuptext": "table",
        "field_prompt": FieldPrompts.Jugement_Ref_prompt,
        "dynamic": True,
        "default_value": "N/A",
        "description": "Official reference number or ID associated with the judgment.",
        "regex": r"^\d+\/\d+$"
    },
    {
        "field": "Date Jugement",
        "lookuptext": "table",
        "field_prompt": FieldPrompts.Date_Jugement_prompt,
        "dynamic": True,
        "default_value": "N/A",
        "description": "The official date on which the judgment was issued.",
        "regex": r"^\d{2}\/\d{2}\/\d{4}$"
    },
    {
        "field": "N° Décision",
        "lookuptext": "table",
        "field_prompt": FieldPrompts.Num_Décision_prompt,
        "dynamic": True,
        "default_value": "N/A",
        "description": "The official decision number related to the expropriation process.",
        "regex": r"^\d+$"
    },
    {
        "field": "N° Bulletin Officiel",
        "lookuptext": "text",
        "field_prompt": FieldPrompts.Num_Bulletin_Officiel_prompt,
        "dynamic": True,
        "default_value": "N/A",
        "description": "The number assigned to the official bulletin where the expropriation information is published.",
        "regex": r"^\d+$"
    },
    {
        "field": "Date Bulletin Officiel",
        "lookuptext": "text",
        "field_prompt": FieldPrompts.Date_Bulletin_Officiel_prompt,
        "dynamic": True,
        "default_value": "N/A",
        "description": "The date of publication of the official bulletin.",
        "regex": r"^\d{2}\/\d{2}\/\d{4}$"
    },
    {
        "field": "Référence Loi",
        "lookuptext": "text",
        "field_prompt": FieldPrompts.Référence_Loi_prompt,
        "dynamic": False,
        "default_value": "7-81",
        "description": "The legal reference governing the expropriation.",
        "regex": r"^\d{1,3}-\d{2}$"
    },
    {
        "field": "Référence Décret Expropriation",
        "lookuptext": "text",
        "field_prompt": FieldPrompts.Référence_Décret_Expropriation_prompt,
        "dynamic": True,
        "default_value": "N/A",
        "description": "The reference of the decree authorizing the expropriation process.",
        "regex": r"^\d+$"
    },
    {
        "field": "Région frappée par le projet",
        "lookuptext": "text",
        "field_prompt": FieldPrompts.Région_frappée_par_le_projet_prompt,
        "dynamic": True,
        "default_value": "N/A",
        "description": "The Moroccan region impacted by the expropriation project.",
        "regex": r"^[A-Za-z\s\-]+$"
    },
    {
        "field": "Commune frappée par le projet",
        "lookuptext": "text",
        "field_prompt": FieldPrompts.Commune_frappée_par_le_projet_prompt,
        "dynamic": True,
        "default_value": "N/A",
        "description": "The specific community impacted by the project.",
        "regex": r"^[A-Za-z\s\-]+$"
    },
    {
        "field": "Intitulé Projet",
        "lookuptext": "text",
        "field_prompt": FieldPrompts.Intitulé_Projet_prompt,
        "dynamic": True,
        "default_value": "N/A",
        "description": "The official name or title of the expropriation project.",
        "regex": r"^[A-Za-z0-9\s\-]+$"
    },
    {
        "field": "Tranche Projet d'expropriation",
        "lookuptext": "table",
        "field_prompt": FieldPrompts.Tranche_Projet_d_expropriation_prompt,
        "dynamic": True,
        "default_value": "N/A",
        "description": "The tranche or phase of the expropriation project.",
        "regex": r"^\d+$"
    },
    {
        "field": "Montant Total Projet",
        "lookuptext": "text",
        "field_prompt": FieldPrompts.Montant_Total_Projet_prompt,
        "dynamic": True,
        "default_value": "N/A",
        "description": "The total financial cost of the expropriation project.",
        "regex": r"^\d+(\.\d{2})?$"
    },
    {
        "field": "Montant Global consigné",
        "lookuptext": "text",
        "field_prompt": FieldPrompts.Montant_Global_consigné_prompt,
        "dynamic": True,
        "default_value": "N/A",
        "description": "The total amount of money deposited for the expropriation.",
        "regex": r"^\d+(\.\d{2})?$"
    },
    {
        "field": "Type Versement",
        "lookuptext": "table",
        "field_prompt": FieldPrompts.Type_Versement_prompt,
        "dynamic": False,
        "default_value": "Chéque",
        "description": "The payment method used for the expropriation (e.g., Cheque).",
        "regex": r"^[A-Za-z\s]+$"
    },
    {
        "field": "Nom / Prénom and CIN ",
        "lookuptext": "table",
        "field_prompt": FieldPrompts.Nom_Prénom_prompt,
        "dynamic": True,
        "default_value": "N/A",
        "description": "The names of individuals involved, along with their CIN (national ID) if available.",
        "regex": r"^[A-Za-z\s]+(\s\d+)?$"
    },
    {
        "field": "Adresse courrier ",
        "lookuptext": "text",
        "field_prompt": FieldPrompts.Adresse_courrier_prompt,
        "dynamic": True,
        "default_value": "N/A",
        "description": "The official mailing address of the expropriating organization.",
        "regex": r"^[A-Za-z0-9\s,]+$"
    },
    {
        "field": "N° Téléphone",
        "lookuptext": "text",
        "field_prompt": FieldPrompts.Num_Téléphone_prompt,
        "dynamic": True,
        "default_value": "N/A",
        "description": "The contact phone number of the expropriating organization.",
        "regex": r"^\+?\d{10,15}$"
    },
    {
        "field": "Localité",
        "lookuptext": "text",
        "field_prompt": FieldPrompts.Localité_prompt,
        "dynamic": True,
        "default_value": "N/A",
        "description": "The locality or area where the project is located.",
        "regex": ''
    },
    {
        "field": "identifiant fiscal",
        "lookuptext": "table",
        "field_prompt": FieldPrompts.Identifiant_Fiscal_prompt,
        "dynamic": True,
        "default_value": "N/A",
        "description": "The fiscal identifier associated with companies involved in the project.",
        "regex": r"^\d{5,12}$"
    }
]
