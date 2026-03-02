import customtkinter as ctk
from tkinter import messagebox
from random import choice
import pandas as pd
import os
from datetime import datetime
from ai import check_interaction
import schedule
import threading
import time
import platform
import subprocess


#========== IMPORTS ==========#

CTK_BOX_RADIUS = 20
CTK_BTN_RADIUS = 20

#========== POP-UP + SOUND ==========#
def play_sound():
    system = platform.system()
    try:
        if system == "Darwin":
            subprocess.Popen(["afplay", "/System/Library/Sounds/Glass.aiff"])
        elif system == "Windows":
            import winsound
            winsound.Beep(1000, 300)
        else:
            subprocess.Popen(["paplay", "/usr/share/sounds/freedesktop/stereo/message.oga"])
    except Exception as e:
        print("Sound error:", e)

#========== APP SETUP ==========#
ctk.set_default_color_theme("green")

app = ctk.CTk()
app._apply_appearance_mode = True
app.title("MyMedAI")
app.geometry("1050x720")

#========== FILE SETUP ==========#
HISTORY_FILE = "interaction_history.csv"
SCHEDULE_FILE = "scheduled_meds.csv"
DRUG_DB_FILE = "nationalDrugs.csv"

if not os.path.exists(HISTORY_FILE):
    pd.DataFrame(columns=["timestamp", "drugs", "model", "response"]).to_csv(HISTORY_FILE, index=False)
if not os.path.exists(SCHEDULE_FILE):
    pd.DataFrame(columns=["medication", "dosage", "time", "created_at"]).to_csv(SCHEDULE_FILE, index=False)

history_df = pd.read_csv(HISTORY_FILE)
schedule_df = pd.read_csv(SCHEDULE_FILE)
df = pd.read_csv(DRUG_DB_FILE) if os.path.exists(DRUG_DB_FILE) else pd.DataFrame()

valid_medications = set()
if not df.empty:
    for col in ["drug_name", "generic_name", "brand_names"]:
        df[col] = df[col].astype(str)
        for entry in df[col]:
            for name in entry.split(","):
                name_clean = name.strip().lower()
                if name_clean and name_clean != "nan":
                    valid_medications.add(name_clean)



#========== GUI  ==========#
sidebar = ctk.CTkFrame(app, width=220, fg_color="#C62828", corner_radius=CTK_BOX_RADIUS)
sidebar.pack(side="left", fill="y")
logo = ctk.CTkLabel(sidebar, text="MyMedAI", font=("Helvetica", 22, "bold"), text_color="white")
logo.pack(pady=30)

main = ctk.CTkFrame(app, fg_color="black", corner_radius=CTK_BOX_RADIUS)
main.pack(side="left", fill="both", expand=True, padx=20, pady=20)

pages = {}
model_type = ctk.StringVar(value="cloud")

#========== FUNCTIONS ==========#
def show_page(name): 
    for frame in pages.values():
        frame.pack_forget()
    pages[name].pack(fill="both", expand=True)

def check_interaction_func():
    meds = interaction_input.get()
    drug_list = [d.strip().lower() for d in meds.split(",") if d.strip()]
    if len(drug_list) < 2:
        messagebox.showwarning("Too Few", "Enter at least two medications.")
        return
    for med in drug_list:
        if med not in valid_medications:
            messagebox.showerror("Invalid Medication", f"'{med}' not found.")
            return
    prompt = f"Give a short, clear answer: Is it safe to take {', '.join(drug_list)} together?"
    try:
        result = check_interaction([prompt], model_type=model_type.get())
        response = result.content if hasattr(result, "content") else str(result)
        messagebox.showinfo("AI Response", response)
        new_entry = {
            "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            "drugs": ", ".join(drug_list),
            "model": model_type.get(),
            "response": response
        }
        global history_df
        history_df = pd.concat([history_df, pd.DataFrame([new_entry])], ignore_index=True)
        history_df.to_csv(HISTORY_FILE, index=False)
    except Exception as e:
        messagebox.showerror("Error", str(e))

def ask_ai_func():
    query = chat_input.get()
    if not query:
        messagebox.showwarning("No Input", "Enter a medical question.")
        return
    prompt = f"You are a medical assistant. Give a helpful, concise answer to this question without assuming it's a drug interaction: {query}"
    try:
        result = check_interaction([prompt], model_type=model_type.get())
        response = result.content if hasattr(result, "content") else str(result)
        chat_output.configure(state="normal")
        chat_output.insert("end", f"You: {query}\nBot: {response}\n\n")
        chat_output.configure(state="disabled")
        chat_input.delete(0, "end")
    except Exception as e:
        messagebox.showerror("Error", str(e))

def save_reminder():
    med = sched_name.get()
    dose = sched_dose.get()
    t = sched_time.get()
    if not med or not dose or not t:
        messagebox.showwarning("Input Error", "Enter medication, dosage, and time.")
        return
    new_row = {
        "medication": med,
        "dosage": dose,
        "time": t,
        "created_at": datetime.now().isoformat()
    }
    global schedule_df
    schedule_df = pd.concat([schedule_df, pd.DataFrame([new_row])], ignore_index=True)
    schedule_df.to_csv(SCHEDULE_FILE, index=False)
    messagebox.showinfo("Saved", f"Reminder set for {med} ({dose}) at {t}.")
    refresh_schedule_list()

def run_schedule():
    schedule.clear()
    for _, row in schedule_df.iterrows():
        schedule.every().day.at(row["time"]).do(remind, row["medication"])
    threading.Thread(target=schedule_loop, daemon=True).start()
    messagebox.showinfo("Started", "Reminders running in the background.")

def schedule_loop():
    while True:
        schedule.run_pending()
        time.sleep(1)

def remind(med):
    play_sound()
    messagebox.showinfo("Reminder", f"Time to take: {med}")

def compare_scheduled():
    if schedule_df.empty:
        messagebox.showinfo("No Data", "No medications scheduled to compare.")
        return
    meds = schedule_df["medication"].tolist()
    prompt = f"Based on the following scheduled medications: {', '.join(meds)}, are there any known interaction risks or timing issues?"
    try:
        result = check_interaction([prompt], model_type=model_type.get())
        response = result.content if hasattr(result, "content") else str(result)
        messagebox.showinfo("AI Comparison Result", response)
    except Exception as e:
        messagebox.showerror("Error", str(e))

def refresh_schedule_list():
    for widget in schedule_list_frame.winfo_children():
        widget.destroy()
    for index, row in schedule_df.iterrows():
        entry_text = f"{row['medication']} | {row['dosage']} at {row['time']}"
        label = ctk.CTkLabel(schedule_list_frame, text=entry_text)
        label.pack(anchor="w", padx=10)
        del_btn = ctk.CTkButton(schedule_list_frame, text="❌ Delete", width=60, fg_color="#A62828",
                                command=lambda i=index: delete_schedule_entry(i))
        del_btn.pack(pady=2)

def delete_schedule_entry(index):
    global schedule_df
    schedule_df.drop(index, inplace=True)
    schedule_df.reset_index(drop=True, inplace=True)
    schedule_df.to_csv(SCHEDULE_FILE, index=False)
    refresh_schedule_list()

def show_lookup_result():
    term = med_lookup_input.get().strip().lower()
    if not term:
        messagebox.showwarning("Empty", "Enter a medication name.")
        return
    matches = df[df.apply(lambda row: term in row.astype(str).str.lower().str.cat(sep=", "), axis=1)]
    if matches.empty:
        med_lookup_output.configure(state="normal")
        med_lookup_output.delete("1.0", "end")
        med_lookup_output.insert("end", f"No data found for '{term}'.")
        med_lookup_output.configure(state="disabled")
    else:
        result = ""
        for _, row in matches.iterrows():
            result += f"\nDrug Name: {row.get('drug_name', '')}\nGeneric Name: {row.get('generic_name', '')}\nBrand Names: {row.get('brand_names', '')}\nSide Effects: {row.get('side_effects', '')}\n---\n"
        med_lookup_output.configure(state="normal")
        med_lookup_output.delete("1.0", "end")
        med_lookup_output.insert("end", result.strip())
        med_lookup_output.configure(state="disabled")

#========== SIDE PAGES ==========#
pages = {}
interaction_input = chat_input = None
sched_name = sched_dose = sched_time = None
schedule_list_frame = med_lookup_input = med_lookup_output = chat_output = None

#========== DASHBOARD ==========#
dashboard = ctk.CTkFrame(main, fg_color="black", corner_radius=CTK_BOX_RADIUS)
pages["Home"] = dashboard

# Welcome Header
ctk.CTkLabel(
    dashboard,
    text="Welcome to MyMedAI!",
    font=("Helvetica", 28, "bold"),
    text_color="white"
).pack(padx=20, pady=(20, 10), anchor="w")

stats_frame = ctk.CTkFrame(dashboard, fg_color="#1a1a1a", corner_radius=CTK_BOX_RADIUS)
stats_frame.pack(padx=20, pady=10, fill="x")

ctk.CTkLabel(stats_frame, text=f"📅 Scheduled Medications: {len(schedule_df)}", font=("Helvetica", 14), text_color="white").pack(anchor="w", padx=10, pady=2)
ctk.CTkLabel(stats_frame, text=f"📊 Total Interactions: {len(history_df)}", font=("Helvetica", 14), text_color="white").pack(anchor="w", padx=10, pady=2)

button_frame = ctk.CTkFrame(dashboard, fg_color="#2c2c2c", corner_radius=CTK_BOX_RADIUS)
button_frame.pack(padx=20, pady=30, fill="x")  


button_width = 200  
ctk.CTkButton(
    button_frame,
    text="➕ New Check",
    fg_color="#C62828",
    hover_color="#FDDDE0",
    corner_radius=CTK_BTN_RADIUS,
    width=button_width,
    command=lambda: show_page("Interactions")
).pack(pady=5)

ctk.CTkButton(
    button_frame,
    text="💬 Ask AI",
    fg_color="#C62828",
    hover_color="#FDDDE0",
    corner_radius=CTK_BTN_RADIUS,
    width=button_width,
    command=lambda: show_page("Chatbot")
).pack(pady=5)

ctk.CTkButton(
    button_frame,
    text="📊 Compare Scheduled",
    fg_color="#C62828",
    hover_color="#FDDDE0",
    corner_radius=CTK_BTN_RADIUS,
    width=button_width,
    command=compare_scheduled
).pack(pady=5)


#========== ROTATING TIPS / QUOTES ==========#

tips = [
    "💡 Tip: Stay hydrated with your meds!",
    "🕒 Tip: Set reminder times you'll remember.",
    "✅ Tip: Double-check interactions before taking anything new.",
    "🧠 Quote: \"An ounce of prevention is worth a pound of cure.\"",
    "💬 Quote: \"Health is not valued until sickness comes.\" – Thomas Fuller",
]
ctk.CTkLabel(dashboard, text=choice(tips), text_color="gray", font=("Helvetica", 12)).pack(pady=10)

#========== INTERACTION PAGE ==========#
interactions = ctk.CTkFrame(main, fg_color="black", corner_radius=CTK_BOX_RADIUS)
pages["Interactions"] = interactions

# Page Title
ctk.CTkLabel(interactions, text="Drug Interaction Checker", font=("Helvetica", 20, "bold"), text_color="white").pack(anchor="w", padx=20, pady=10)

# Medication Input Field
interaction_input = ctk.CTkEntry(interactions, placeholder_text="Enter medications (comma-separated)", width=600, corner_radius=CTK_BOX_RADIUS)
interaction_input.pack(pady=(10, 20))

# Radio Buttons Box
radio_box = ctk.CTkFrame(interactions, fg_color="#1a1a1a", corner_radius=CTK_BOX_RADIUS)
radio_box.pack(pady=10)

ctk.CTkLabel(radio_box, text="Choose Model", font=("Helvetica", 14, "bold"), text_color="white").pack(anchor="w", padx=10, pady=5)

ctk.CTkRadioButton(radio_box, text="Cloud AI", variable=model_type, value="cloud").pack(anchor="w", padx=10, pady=3)
ctk.CTkRadioButton(radio_box, text="Local AI", variable=model_type, value="local").pack(anchor="w", padx=10, pady=3)

# Action Button Box
action_box = ctk.CTkFrame(interactions, fg_color="#2c2c2c", corner_radius=CTK_BOX_RADIUS)
action_box.pack(pady=20)

ctk.CTkButton(action_box, text="Check Interaction", fg_color="#C62828", corner_radius=CTK_BTN_RADIUS, command=check_interaction_func).pack(padx=20, pady=10)


#========== SCHEDULER PAGE ==========#
scheduler = ctk.CTkFrame(main, fg_color="black", corner_radius=CTK_BOX_RADIUS)
pages["Scheduler"] = scheduler
ctk.CTkLabel(scheduler, text="Medication Scheduler", font=("Helvetica", 20, "bold"), text_color="white").pack(anchor="w", padx=20, pady=10)
sched_name = ctk.CTkEntry(scheduler, placeholder_text="Medication", corner_radius=CTK_BOX_RADIUS)
sched_name.pack(pady=5)
sched_dose = ctk.CTkEntry(scheduler, placeholder_text="Dosage (e.g., 500mg)", corner_radius=CTK_BOX_RADIUS)
sched_dose.pack(pady=5)
sched_time = ctk.CTkEntry(scheduler, placeholder_text="HH:MM", corner_radius=CTK_BOX_RADIUS)
sched_time.pack(pady=5)
ctk.CTkButton(scheduler, text="Add Reminder", fg_color="#C62828", corner_radius=CTK_BTN_RADIUS, command=save_reminder).pack(pady=10)
ctk.CTkButton(scheduler, text="Start Reminders", fg_color="#C62828", corner_radius=CTK_BTN_RADIUS, command=run_schedule).pack(pady=5)

schedule_list_frame = ctk.CTkFrame(scheduler, fg_color="#1a1a1a", corner_radius=CTK_BOX_RADIUS)
schedule_list_frame.pack(fill="both", expand=True, padx=10, pady=10)
ctk.CTkButton(scheduler, text="🔄 Refresh List", fg_color="#C62828", corner_radius=CTK_BTN_RADIUS, command=refresh_schedule_list).pack(pady=5)

#========== CHATBOT PAGE ==========#
chat = ctk.CTkFrame(main, fg_color="black", corner_radius=CTK_BOX_RADIUS)
pages["Chatbot"] = chat
ctk.CTkLabel(chat, text="Health Assistant Chatbot", font=("Helvetica", 20, "bold"), text_color="white").pack(anchor="w", padx=20, pady=10)
chat_input = ctk.CTkEntry(chat, placeholder_text="Ask anything medical...", width=600, corner_radius=CTK_BOX_RADIUS)
chat_input.pack(pady=5)
ctk.CTkButton(chat, text="Ask", fg_color="#C62828", corner_radius=CTK_BTN_RADIUS, command=ask_ai_func).pack(pady=5)
chat_output = ctk.CTkTextbox(chat, height=200, width=800)
chat_output.pack(pady=10)
chat_output.configure(state="disabled")

#========== LOOKUP PAGE ==========#
lookup = ctk.CTkFrame(main, fg_color="black", corner_radius=CTK_BOX_RADIUS)
pages["Lookup"] = lookup
ctk.CTkLabel(lookup, text="Medication Lookup", font=("Helvetica", 20, "bold"), text_color="white").pack(anchor="w", padx=20, pady=10)
med_lookup_input = ctk.CTkEntry(lookup, placeholder_text="Enter medication name to search", width=400, corner_radius=CTK_BOX_RADIUS)
med_lookup_input.pack(pady=5)
ctk.CTkButton(lookup, text="Search", fg_color="#C62828", corner_radius=CTK_BTN_RADIUS, command=show_lookup_result).pack(pady=5)
med_lookup_output = ctk.CTkTextbox(lookup, height=300, width=800)
med_lookup_output.pack(pady=10)
med_lookup_output.configure(state="disabled")

#========== VIEW/EDIT SCHEDULE PAGE  & FUNCTIONS ==========#

view_edit = ctk.CTkFrame(main, fg_color="black", corner_radius=CTK_BOX_RADIUS)
pages["View/Edit Schedule"] = view_edit
ctk.CTkLabel(view_edit, text="Your Scheduled Medications", font=("Helvetica", 20, "bold"), text_color="white").pack(anchor="w", padx=20, pady=10)
ve_frame = ctk.CTkFrame(view_edit, fg_color="#1a1a1a", corner_radius=CTK_BOX_RADIUS)
ve_frame.pack(fill="both", expand=True, padx=20, pady=10)

def delete_and_refresh(index):
    delete_schedule_entry(index)
    refresh_view_edit()

def refresh_view_edit():
    for widget in ve_frame.winfo_children():
        widget.destroy()
    for index, row in schedule_df.iterrows():
        item_frame = ctk.CTkFrame(ve_frame, fg_color="transparent")
        item_frame.pack(fill="x", pady=5, padx=10)

        ctk.CTkLabel(item_frame, text=f"{row['medication']}", width=120).pack(side="left")
        dose_entry = ctk.CTkEntry(item_frame, width=120)
        dose_entry.insert(0, row['dosage'])
        dose_entry.pack(side="left", padx=5)

        time_entry = ctk.CTkEntry(item_frame, width=100)
        time_entry.insert(0, row['time'])
        time_entry.pack(side="left", padx=5)

        save_btn = ctk.CTkButton(item_frame, text="✅ Save", width=60, fg_color="#28A745", corner_radius=CTK_BTN_RADIUS,
                                command=lambda i=index, d=dose_entry, t=time_entry: update_schedule_entry(i, d.get(), t.get()))
        save_btn.pack(side="left", padx=5)

        del_btn = ctk.CTkButton(item_frame, text="❌ Delete", width=60, fg_color="#A62828", corner_radius=CTK_BTN_RADIUS,
                                command=lambda i=index: delete_and_refresh(i))
        del_btn.pack(side="left", padx=5)

def update_schedule_entry(index, new_dose, new_time):
    global schedule_df
    schedule_df.at[index, 'dosage'] = new_dose
    schedule_df.at[index, 'time'] = new_time
    schedule_df.to_csv(SCHEDULE_FILE, index=False)
    refresh_view_edit()

refresh_view_edit()

#========== SIDEPAGE BUTTONS ==========#
def make_nav_btn(name):
    btn = ctk.CTkButton(sidebar, text=name, width=180, corner_radius=CTK_BTN_RADIUS, fg_color="white", text_color="#C62828", hover_color="#FDDDE0", command=lambda: show_page(name))
    btn.configure(font=("Helvetica", 14, "bold"))
    return btn

for section in ["Home", "Interactions", "Scheduler", "Chatbot", "Lookup", "View/Edit Schedule"]:
    make_nav_btn(section).pack(pady=5)



#========== CUD LOGO ==========#
from PIL import Image, ImageTk
cud_image = ctk.CTkImage(light_image=Image.open("cudLogo.png"), size=(150, 150))
logo_label = ctk.CTkLabel(sidebar, image=cud_image, text="")
logo_label.pack(expand=True, pady=10)

#========== RUN APP ==========#
refresh_schedule_list()
show_page("Home")
app.mainloop()

