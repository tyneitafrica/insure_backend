# from .ussdmenu import menus
# BASE_URL = "http://127.0.0.1:8000/api/ussd/"

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
    # Placeholder for submenus, to be filled later
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
        "text": "CON Payment Options:\n1. Individual\n2. Family\n3. Go Back",
        "options": {
            "1": "individual_payment",
            "2": "family_payment",
            "3": "main_menu",
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




def process_ussd(text):
    # Split the text input to determine user progression
    steps = text.split("*")
    current_level = len(steps)
    if text == '':
        return menus["main_menu"]["text"]

    elif current_level == 1:  # Main menu
        user_input = steps[0]
        if user_input in menus["main_menu"]["options"]:
            next_menu_key = menus["main_menu"]["options"][user_input]
            return menus[next_menu_key]["text"]
        else:
            return "CON Invalid option. Please try again.\n" + menus["main_menu"]["text"]

    elif current_level == 2:  # Submenu level (e.g., Buy Insurance)
        main_choice = steps[0]
        submenu_choice = steps[1]

        main_menu_key = menus["main_menu"]["options"].get(main_choice)
        submenu = menus.get(main_menu_key)

        if submenu and submenu_choice in submenu["options"]:
            next_menu_key = submenu["options"][submenu_choice]
            return menus[next_menu_key]["text"]
        else:
            return "CON Invalid option. Please try again.\n" + menus["main_menu"]["text"]
 

if __name__ == "__main__":
    print("Starting USSD simulation...")
    text = ""  # Initial empty input to start at the main menu

    while True:
        # Process the current USSD text
        response = process_ussd(text)

        # Print the response to the terminal
        print("\n" + response)

        # Check if it's an END response
        if response.startswith("END"):
            print("\nSession terminated.\n")
            break

        # Get the next input from the user
        next_input = input("Enter your choice (or type 'exit' to quit): ")
        if next_input.lower() == "exit":
            print("\nExiting simulation. Goodbye!\n")
            break

        # Append the user input to the current text
        if text:
            text += f"*{next_input}"  # Add to the progression
        else:
            text = next_input  # Start a new session