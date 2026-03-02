# MyMedAI – Medication Management System

## Overview

MyMedAI is a medication management system that helps users:

* Check drug interactions
* Manage scheduled medications
* Track interaction history
* Use AI-assisted responses for medication-related queries
* Run a reminder module (C++ component)

The project combines multiple paradigms and technologies, including Python, Prolog, and C++.

---

## Features

* Drug interaction checking using Prolog knowledge base
* AI-powered assistance via Python
* Medication scheduling with CSV storage
* Interaction history logging
* C++ reminder module
* Demo script for testing functionality

---

## Tech Stack

* Python (main application logic)
* Prolog (drug interaction rules – `interactions.pl`)
* C++ (reminder system – `reminder.cpp`)
* CSV files (data storage)
* Environment variables (`.env`)

---

## Project Structure

```
medicationProject/
│
├── app.py                     # Main application
├── ai.py                      # AI logic
├── demo.py                    # Demo script
├── interactions.pl            # Prolog interaction rules
├── reminder.cpp               # C++ reminder system
├── reminder                   # Compiled reminder executable
│
├── nationalDrugs.csv          # Drug database
├── scheduled_meds.csv         # Scheduled medications
├── interaction_history.csv    # Logged interactions
│
├── cudLogo.png                # Logo asset
├── .env                       # Environment configuration

```

---

## Installation

### 1. Clone the repository

```
git clone https://github.com/Ahmaddd-y/medication-reminder-system-spring-2024-.git
cd medication-reminder-system-spring-2024-
```

### 2. Install Python dependencies

If requirements are not provided, install manually as needed. Typical example:

```
pip install python-dotenv
```

Install any additional packages required by `app.py` or `ai.py`.

### 3. Install Prolog

Ensure SWI-Prolog is installed and accessible from your system path.

### 4. Compile the C++ reminder module

```
g++ reminder.cpp -o reminder
```

---

## Configuration

Edit the `.env` file to configure any required API keys or environment variables used in `ai.py`.

---

## Running the Project

### Run the main application

```
python app.py
```

### Run demo

```
python demo.py
```

### Run reminder module

```
./reminder
```

---

## How It Works

* The user inputs medication data.
* Python handles user interaction and logic.
* Prolog checks for drug interactions using defined rules.
* Results are stored in CSV files.
* The C++ module handles medication reminders.

---

## Academic Context

This project demonstrates multiple programming paradigms:

* Logic Programming (Prolog)
* Procedural / Object-Oriented (Python)
* Systems Programming (C++)

It was developed as part of a Programming Paradigms course.

---

## Notes

* Ensure all CSV files remain in the root directory.
* Do not delete `interactions.pl`, as it is required for interaction checks.
* If the reminder executable is missing, recompile `reminder.cpp`.
