import tkinter as tk
from tkinter import ttk, messagebox, scrolledtext
import csv
import json
import re
import tiktoken

# --- Setup tokenizer ---
tokenizer = tiktoken.get_encoding('gpt2')

# --- Load Symptom Vocabulary ---
symptom_vocabulary = set()
try:
    with open('health_dataset.csv', 'r', encoding='utf-8') as f:
        reader = csv.reader(f)
        for row in reader:
            for phrase in row:
                cleaned = phrase.strip().lower()
                if cleaned:
                    symptom_vocabulary.add(cleaned)
except FileNotFoundError:
    symptom_vocabulary = set()
    print("ERROR: health_dataset.csv not found!")

# --- Define GUI ---
root = tk.Tk()
root.title("🩺 Symptom Analyzer & Treatment Finder")
root.geometry("800x600")
root.configure(bg="#f0f6ff")

# --- Style ---
style = ttk.Style()
style.configure("TLabel", background="#f0f6ff", font=("Segoe UI", 11))
style.configure("TButton", font=("Segoe UI", 11, "bold"), padding=6)
style.configure("Header.TLabel", font=("Segoe UI", 18, "bold"), background="#cce0ff", anchor="center")

# --- Header ---
header = ttk.Label(root, text="Medical Symptom Analyzer", style="Header.TLabel")
header.pack(fill="x", pady=10)

# --- Input Frame ---
frame_input = ttk.Frame(root, padding=15)
frame_input.pack(fill="x")

label = ttk.Label(frame_input, text="Describe your symptoms:")
label.pack(anchor="w")

input_box = scrolledtext.ScrolledText(frame_input, height=4, wrap=tk.WORD, font=("Segoe UI", 10))
input_box.pack(fill="x", pady=5)

# --- Output Frame ---
frame_output = ttk.Frame(root, padding=15)
frame_output.pack(fill="both", expand=True)

output_box = scrolledtext.ScrolledText(frame_output, height=20, wrap=tk.WORD, font=("Consolas", 10))
output_box.pack(fill="both", expand=True)

# --- Core Logic ---
def analyze_symptoms():
    output_box.delete("1.0", tk.END)
    user_query = input_box.get("1.0", tk.END).strip().lower()

    if not user_query:
        messagebox.showwarning("Input Missing", "Please enter your symptoms before analyzing.")
        return

    matched_symptoms = {s for s in symptom_vocabulary if s in user_query}

    if not matched_symptoms:
        output_box.insert(tk.END, "No known symptoms found in your description.\n")
        return

    output_box.insert(tk.END, "✅ Matched Symptoms:\n")
    for s in matched_symptoms:
        output_box.insert(tk.END, f"  • {s}\n")

    output_box.insert(tk.END, "\nToken IDs:\n")
    for s in matched_symptoms:
        tokens = tokenizer.encode(s)
        output_box.insert(tk.END, f"  '{s}': {tokens}\n")

    output_box.insert(tk.END, "\n--- Finding Potential Treatments ---\n")

    try:
        with open('UpdatedSolution.json', 'r', encoding='utf-8') as sol:
            data = json.load(sol)

        found_match = False

        def check_disease(entry):
            nonlocal found_match
            symptoms_list = entry.get('symptoms')
            if not symptoms_list:
                return False
            overlap = matched_symptoms.intersection(set(s.lower() for s in symptoms_list))
            if overlap:
                found_match = True
                disease = entry.get('disease', 'Unknown Disease')
                aid1 = entry.get('first_aid_treatment_1', 'No first aid listed.')
                aid2 = entry.get('first_aid_treatment_2', 'No second aid listed.')

                output_box.insert(tk.END, f"\n--- Possible Match ---\n")
                output_box.insert(tk.END, f"Disease: {disease}\n")
                output_box.insert(tk.END, f"Matched Symptoms: {list(overlap)}\n")
                output_box.insert(tk.END, f"First Aid 1: {aid1}\n")
                output_box.insert(tk.END, f"First Aid 2: {aid2}\n")

        if isinstance(data, list):
            for entry in data:
                check_disease(entry)
        elif isinstance(data, dict) and "data" in data:
            for entry in data["data"]:
                check_disease(entry)

        if not found_match:
            output_box.insert(tk.END, "\nNo matching disease found in the database.\n")

    except FileNotFoundError:
        output_box.insert(tk.END, "ERROR: UpdatedSolution.json not found.\n")
    except json.JSONDecodeError:
        output_box.insert(tk.END, "ERROR: Invalid JSON format in UpdatedSolution.json.\n")

# --- Button ---
analyze_btn = ttk.Button(root, text="🔍 Analyze Symptoms", command=analyze_symptoms)
analyze_btn.pack(pady=10)

root.mainloop()
