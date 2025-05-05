import os
import re

import win32ui
from tkinter import *
from tkinter import messagebox
from reportlab.pdfgen import canvas
import win32print

# Get path to Documents folder
documents_path = os.path.join(os.path.expanduser("~"), "Documents")
generated_filepath = ""


def center_window(window, width, height):
    screen_width = window.winfo_screenwidth()
    screen_height = window.winfo_screenheight()
    x = int((screen_width / 2) - (width / 2))
    y = int((screen_height / 2) - (height / 2))
    window.geometry(f"{width}x{height}+{x}+{y}")


def get_next_filename(extension, username):
    base = re.sub(r'\W+', '', username) or "resume"
    n = 1
    # Remove spaces and non-alphanumeric characters, and replace spaces with nothing
    base = re.sub(r'\W+', '', username.replace(" ", "")) or "resume"
    n = 0
    while True:
        filename = f"{base}{n}.{extension.lower()}"
        # Append number if n > 0, else use the base name
        filename = f"{base}{n if n > 0 else ''}.{extension.lower()}"
        full_path = os.path.join(documents_path, filename)
        if not os.path.exists(full_path):
            return full_path
        n += 1


def save_resume():
    global generated_filepath
    name = name_entry.get()
    email = email_entry.get()
    phone = phone_entry.get()
    summary = summary_text.get("1.0", END).strip()
    filetype = file_type.get()

    content = f"Name: {name}\nEmail: {email}\nPhone: {phone}\nSummary:\n{summary}"
    generated_filepath = get_next_filename(filetype, name)

    if filetype == "TXT":
        with open(generated_filepath, "w") as f:
            f.write(content)
    elif filetype == "PDF":
        pdf = canvas.Canvas(generated_filepath)
        lines = content.split("\n")
        y = 800
        for line in lines:
            pdf.drawString(50, y, line)
            y -= 20
        pdf.save()

    status_label.config(text=f"Saved to: {generated_filepath}", fg="green")


def print_direct():
    receipt_text = (
        "Resume Print Receipt\n"
        "----------------------------\n"
        f"Name: {name_entry.get()}\n"
        f"Email: {email_entry.get()}\n"
        f"Phone: {phone_entry.get()}\n"
        "----------------------------\n"
        f"Summary:\n{summary_text.get('1.0', END).strip()}\n"
    )

    printer_name = win32print.GetDefaultPrinter()
    hprinter = win32print.OpenPrinter(printer_name)
    printer_info = win32print.GetPrinter(hprinter, 2)
    pdc = win32ui.CreateDC()
    pdc.CreatePrinterDC(printer_name)
    pdc.StartDoc("Resume Print")
    pdc.StartPage()

    font = win32ui.CreateFont({
        "name": "Courier New",
        "height": 20,
        "weight": 400,
    })
    pdc.SelectObject(font)

    y = 100
    for line in receipt_text.split("\n"):
        pdc.TextOut(100, y, line)
        y += 30

    pdc.EndPage()
    pdc.EndDoc()
    pdc.DeleteDC()
    status_label.config(text="Resume sent to printer.", fg="green")


def main_app():
    global name_entry, email_entry, phone_entry, summary_text, file_type, status_label

    root = Tk()
    root.title("Resume Builder")
    window_width = 700
    window_height = 800
    center_window(root, window_width, window_height)
    root.config(bg="#f4f6f7")  # Light gray background

    # Header
    header = Label(
        root, text="📝 Resume Builder", font=("Segoe UI", 26, "bold"),
        bg="#f4f6f7", fg="#2c3e50"
    )
    header.pack(pady=30)

    # Main frame
    form_frame = Frame(root, bg="white", bd=2, relief="groove")
    form_frame.pack(padx=30, pady=10, fill="both", expand=True)

    def create_labeled_entry(text):
        frame = Frame(form_frame, bg="white")
        frame.pack(fill="x", pady=10, padx=20)
        label = Label(frame, text=text, width=12, anchor="w", font=("Segoe UI", 11), bg="white")
        label.pack(side=LEFT)
        entry = Entry(frame, width=40, font=("Segoe UI", 11), bd=1, relief="solid")
        entry.pack(side=LEFT, padx=10)
        return entry

    name_entry = create_labeled_entry("Full Name")
    email_entry = create_labeled_entry("Email")
    phone_entry = create_labeled_entry("Phone")

    # Summary Section
    summary_frame = Frame(form_frame, bg="white")
    summary_frame.pack(fill="x", pady=10, padx=20)

    summary_label = Label(summary_frame, text="Summary", font=("Segoe UI", 11), bg="white", width=12, anchor="w")
    summary_label.pack(side="left")

    summary_text = Text(summary_frame, width=40, height=6, font=("Segoe UI", 11), bd=1, relief="solid", wrap="word")
    summary_text.pack(side="left", padx=10)

    # Export Option
    option_frame = Frame(form_frame, bg="white")
    option_frame.pack(fill="x", pady=10, padx=20)
    Label(option_frame, text="Export As", width=12, anchor="w", font=("Segoe UI", 11), bg="white").pack(side=LEFT)
    file_type = StringVar(value="PDF")
    dropdown = OptionMenu(option_frame, file_type, "PDF", "TXT")
    dropdown.config(font=("Segoe UI", 10), width=10)
    dropdown.pack(side=LEFT, padx=10)

    # Button Frame
    button_frame = Frame(form_frame, bg="white")
    button_frame.pack(pady=20)
    Button(
        button_frame, text="Generate Resume", command=save_resume,
        width=18, bg="#27AE60", fg="white", font=("Segoe UI", 11, "bold"), relief="flat", padx=10, pady=5
    ).pack(side=LEFT, padx=10)

    Button(
        button_frame, text="Print Resume", command=print_direct,
        width=18, bg="#2980B9", fg="white", font=("Segoe UI", 11, "bold"), relief="flat", padx=10, pady=5
    ).pack(side=LEFT, padx=10)

    # Status Label
    status_label = Label(
        root, text="", font=("Segoe UI", 10), bg="#f4f6f7", fg="red"
    )
    status_label.pack(pady=10)

    root.mainloop()


def show_resume_builder():
    login_root.destroy()
    main_app()


def login():
    username = username_entry.get()
    password = password_entry.get()
    try:
        with open("users.txt", "r") as f:
            users = f.read().splitlines()
            if f"{username}:{password}" in users:
                show_resume_builder()
            else:
                messagebox.showerror("Login Failed", "Wrong username or password")
    except FileNotFoundError:
        messagebox.showerror("Error", "No users registered yet")


def create_account():
    username = username_entry.get()
    password = password_entry.get()
    if not username or not password:
        messagebox.showerror("Error", "Please fill in both fields")
        return
    if os.path.exists("users.txt"):
        with open("users.txt", "r") as f:
            existing_users = [line.split(":")[0] for line in f]
        if username in existing_users:
            messagebox.showerror("Error", "Username already exists")
            return
    with open("users.txt", "a") as f:
        f.write(f"{username}:{password}\n")
    messagebox.showinfo("Success", "Account created. You can now log in.")


login_root = Tk()
login_root.title("Login - Resume Builder")
center_window(login_root, 400, 300)
login_root.configure(bg="#E8F0FE")

frame = Frame(login_root, bg="white", bd=2, relief="groove")
frame.place(relx=0.5, rely=0.5, anchor="center", width=320, height=240)

Label(frame, text="Login or Create Account", font=("Segoe UI", 14, "bold"), bg="white", fg="#333").pack(pady=10)
Label(frame, text="Username", font=("Segoe UI", 10), bg="white").pack()
username_entry = Entry(frame, width=30, font=("Segoe UI", 10))
username_entry.pack(pady=5)

Label(frame, text="Password", font=("Segoe UI", 10), bg="white").pack()
password_entry = Entry(frame, show="*", width=30, font=("Segoe UI", 10))
password_entry.pack(pady=5)

Button(frame, text="Login", command=login, width=15, bg="#4CAF50", fg="white", font=("Segoe UI", 10, "bold")).pack(
    pady=5)
Button(frame, text="Create Account", command=create_account, width=15, bg="#2196F3", fg="white",
       font=("Segoe UI", 10, "bold")).pack()

login_root.mainloop()
