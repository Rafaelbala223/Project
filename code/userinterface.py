import tkinter as tk
import pygubu
from tkinter import messagebox
from typing import Dict, List
from networking import Networking
from supabase_manager import supabase, print_database_content, insert_user

# Code for UI
networking = Networking()
# Make build_ui_instance a global variable to hold the pygubu.Builder instance
build_ui_instance: pygubu.Builder = pygubu.Builder()

def createSockets() -> None:
    if networking.setupSockets():
        print("Sockets setup successful.")
    else:
        print("Failed to set up sockets.")
    


def on_continue_clicked(root: tk.Tk, users, input_ids) -> None:
    # Initialize lists to store user data
    user_data = []
    
    
    #networking.transmit_equipment_code(23)
    
    for input_id, field_name in input_ids.items():
        if "_equipment_id_" in input_id:
            entry = build_ui_instance.get_object(input_id)
            equipment_id = entry.get().strip()
            if(len(equipment_id) != 0):
                networking.transmit_equipment_code(equipment_id)
                print(equipment_id)

    # Iterate over input IDs to retrieve user information
    for input_id, field_name in input_ids.items():
        if "_user_id_" in input_id:  # Check if the input ID corresponds to user ID
            entry = build_ui_instance.get_object(input_id)
            username_field = input_id.replace("user_id", "username")  # Get corresponding username field ID
            username_entry = build_ui_instance.get_object(username_field)
            user_id = entry.get().strip()
            username = username_entry.get().strip()
            if user_id and username:  # Only append if both user ID and username are not empty
                user_data.append((user_id, username))

    # Insert user data into Supabase table
    for user_id, username in user_data:
        # Convert user_id to int (assuming user_id should be an integer)
        try:
            user_id = int(user_id)
        except ValueError:
            messagebox.showerror("Error", "User ID must be a valid number.")
            return

        # Check if user_id already exists in the users table
        query = supabase.table("users").select("user_id").eq("username", username)
        response = query.execute()

        # If user_id already exists, show error message and skip insertion
        if response.data:
            #messagebox.showerror("Error", f"User ID {user_id} already exists.")
            continue
        else:
            # If user_id doesn't exist, add the user to the Supabase table
            insert_user(username, user_id)
            messagebox.showinfo("Info", f"User ID {user_id} not found, adding to the database.")

    # Notify user of successful insertion
    messagebox.showinfo("Success", "User information inserted successfully.")
    

    
def clear_entry_fields(builder: pygubu.Builder):
    # Print a message indicating F12 is being clicked
    print("F12 pressed. Clearing entry fields.")

    # Function to recursively traverse all widgets and clear entry widget contents
    def clear_widgets(widget):
        if isinstance(widget, tk.Entry):
            # Clear the content of the entry widget
            widget.delete(0, tk.END)
        elif hasattr(widget, 'winfo_children'):
            # Recursively traverse all children widgets
            for child_widget in widget.winfo_children():
                clear_widgets(child_widget)

    # Start clearing widgets from the root
    root_widget = builder.get_object("master")
    clear_widgets(root_widget)


def build_ui(root: tk.Tk, users: dict) -> None:
    global build_ui_instance  # Make sure to use the global instance

    try:

        build_ui_instance.add_from_file("ui/player_interface.ui")
    except:
        build_ui_instance.add_from_file("../ui/player_interface.ui")


    # Bind the F12 key to the clear_entry_fields function
    root.bind("<F12>", lambda event: clear_entry_fields(build_ui_instance))
    
    main_frame: tk.Frame = build_ui_instance.get_object("master", root)
    main_frame.place(relx=0.5, rely=0.5, anchor=tk.CENTER)

    red_frame: tk.Frame = build_ui_instance.get_object("red_team", main_frame)
    blue_frame: tk.Frame = build_ui_instance.get_object("blue_team", main_frame)

    input_ids: Dict[int, str] = {}
    fields: List[str] = {
        "red_equipment_id_",
        "red_user_id_",
        "red_username_",
        "blue_equipment_id_",
        "blue_user_id_",
        "blue_username_"
    }

    for i in range(1, 16):
        for field in fields:
            entry_id = f"{field}{i}"  # Use the ID from XML directly
            entry = build_ui_instance.get_object(entry_id,
                                                 red_frame if "red" in field else blue_frame)
            input_ids[entry_id] = entry_id  # Use the same ID for input_ids
            entry.bind("<Return>", lambda event, entry=entry: autofill_username(entry))



    submit_button = build_ui_instance.get_object("submit")
    submit_button.configure(command=lambda: on_continue_clicked(root, users, input_ids))


def builder(root:tk.Tk, users :dict) -> None:
    builder: pygubu.Builder = pygubu.Builder()
    try:
        builder.add_from_file("ui/player_interface.ui")
    except:
        builder.add_from_file("../ui/player_interface.ui")
    # Place the main frame in the center of the root window
    # make unresizable
    main_frame: tk.Frame = builder.get_object("master", root)
    main_frame.place(relx=0.5, rely=0.5, anchor=tk.CENTER)

    # Create frames for the teams
    teams_frame: tk.Frame = builder.get_object("teams", main_frame)
    red_frame: tk.Frame = builder.get_object("red_team", teams_frame)
    blue_frame: tk.Frame = builder.get_object("blue_team", teams_frame)

    # Create a dictionary of  IDs and corresponding entry field IDs
    input_ids: Dict[int, str] = {}
    fields: List[str] = {
        "red_equipment_id_",
        "red_user_id_",
        "red_username_",
        "blue_equipment_id_",
        "blue_user_id_",
        "blue_username_"
    }

    # Add each entry field ID to the dictionary of entry field IDs
    for i in range(1, 16):
        for field in fields:
            entry_id = f"{field}{i}"
            entry = builder.get_object(entry_id, red_frame if "red" in field else blue_frame)
            input_ids[entry.winfo_id()] = entry_id
            entry.bind("<Return>", lambda event, entry_id=entry_id: autofill_username(builder.get_object(entry_id)))

    # Testing submit button
    builder.get_object("submit").configure(command=lambda: on_continue_clicked(root, users, input_ids))

def autofill_username(entry):
    user_id = entry.get().strip()
    if user_id:
        try:
            # Get the parent frame
            parent_frame = entry.master
            while parent_frame.winfo_name() not in {"red_team", "blue_team"}:
                parent_frame = parent_frame.master

            # Get the corresponding username entry widget
            username_entry = parent_frame.nametowidget(entry.winfo_name().replace("user_id", "username"))
            if username_entry:
                # Query Supabase to find username based on user ID
                query = supabase.table("users").select("username").eq("user_id", user_id)
                response = query.execute()
                
                # Print the response
                print("Supabase Response:", response)

                # Check if response contains data and retrieve username
                if response and response.data:
                    username = response.data[0]["username"]
                    print("Retrieved username:", username)  # Debugging statement
                    username_entry.delete(0, tk.END)  # Clear existing content
                    username_entry.insert(0, username)
                else:
                    print("No username data found in response.")  # Debugging statement
            else:
                print("Username entry widget not found.")
        except Exception as e:
            print(f"An error occurred: {e}")