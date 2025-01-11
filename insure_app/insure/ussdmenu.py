menus = {
    "main_menu": {
        "text": "Welcome to Insure\n\n"
                "Please select an option:\n"
                "1. Buy Insurance\n"
                "2. View Policies\n"
                "3. Claims Submissions\n"
                "4. Payment Options\n"
                "5. Get Quotes\n"
                "6. Account Management\n"
                "7. Customer Support\n"
                "8. Exit",
        "options": {
            "1": "buy_insurance",
            "2": "view_policies",
            "3": "claims_submissions",
            "4": "payment_options",
            "5": "get_quotes",
            "6": "account_management",
            "7": "customer_support",
            "8": "exit_now",
        },
    },
    # Placeholder for submenus, to be filled later based on the specification
    "buy_insurance": {
        "text": "CON Select Insurance Type:\n1. Health\n2. Auto\n3. Home\n4. Go Back",
        "options": {
            "1": "health_insurance",
            "2": "auto_insurance",
            "3": "home_insurance",
            "4": "main_menu",
        },
    },
    "health_insurance": {
        "text": "CON Select Health Insurance:\n1. Individual\n2. Family\n3. Go Back",
        "options": {
            "1": "individual_health",
            "2": "family_health",
            "3": "buy_insurance",
        },
    },
    "auto_insurance": {
        "text": "CON Select Auto Insurance:\n1. Individual\n2. Family\n3. Go Back",
        "options": {
            "1": "individual_auto",
            "2": "family_auto",
            "3": "buy_insurance",
        },
    },
    "home_insurance": {
        "text": "CON Select Home Insurance:\n1. Individual\n2. Family\n3. Go Back",
        "options": {
            "1": "individual_home",
            "2": "family_home",
            "3": "buy_insurance",
        },
    },
    "view_policies": {
        "text": "CON View Policies:\n1. Individual\n2. Family\n3. Go Back",
        "options": {
            "1": "individual_policies",
            "2": "family_policies",
            "3": "main_menu",
        },
    },
    "claims_submissions": {
        "text": "CON Claims Submissions:\n1. Individual\n2. Family\n3. Go Back",
        "options": {
            "1": "individual_claims",
            "2": "family_claims",
            "3": "main_menu",
        },
    },
    "payment_options": {
        "text": "CON Payment Options:\n1. Initiatiate Mpesa\n2. Family\n3. Go Back",
        "options": {
            "1": "initiate stk push",
            "2": "main_menu",
        },
    },
    "get_quotes": {
        "text": "CON Get Quotes:\n1. Individual\n2. Family\n3. Go Back",
        "options": {
            "1": "individual_quote",
            "2": "family_quote",
            "3": "main_menu",
        },
    },
    "account_management": {
        "text": "CON Account Management:\n1. Individual\n2. Family\n3. Go Back",
        "options": {
            "1": "individual_account",
            "2": "family_account",
            "3": "main_menu",
        },
    },
    "customer_support": {
        "text": "CON Customer Support:\n1. Individual\n2. Family\n3. Go Back",
        "options": {
            "1": "individual_support",
            "2": "family_support",
            "3": "main_menu",
        },
    },
    "exit_now": {
        "text": "END Thank you for using Insure. Have a great day!",
    },

}