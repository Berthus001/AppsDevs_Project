import os
import re
import customtkinter as ctk
from tkinter import END, messagebox, filedialog
from reportlab.lib.pagesizes import letter
from reportlab.pdfgen import canvas
import win32print
import win32ui
from PIL import Image, ImageTk, ImageWin


# Initialize theme
ctk.set_appearance_mode("light")
ctk.set_default_color_theme("blue")

# Path for resume
documents_path = os.path.join(os.path.expanduser("~"), "Documents")
generated_filepath = ""
image_filepath = None  # Initialize image_filepath to avoid uninitialized variable usage

# Login Page Code First
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

def toggle_password_visibility():
    if show_password_checkbox.get():
        password_entry.configure(show="")
    else:
        password_entry.configure(show="*")

def show_resume_builder():
    login_root.destroy()
    main_app()

def upload_photo():  # Declare as global to use in other functions
    file_path = filedialog.askopenfilename(filetypes=[("Image Files", "*.jpg *.jpeg *.png")])
    if file_path:
        global image_filepath
        image_filepath = file_path  # Store the file path for later use
        img = Image.open(file_path)
        img = img.resize((192, 192))  # Resize to 2x2 inches (192x192 px)
        img_tk = ImageTk.PhotoImage(img)
        image_label.configure(image=img_tk, text="") 
        image_label.image = img_tk  # Keep reference

# Helper functions
def center_window(window, width, height):
    screen_width = window.winfo_screenwidth()
    screen_height = window.winfo_screenheight()
    x = int((screen_width / 2) - (width / 2))
    y = int((screen_height / 2) - (height / 2))
    window.geometry(f"{width}x{height}+{x}+{y}")

def get_next_filename(extension, username):
    base = re.sub(r'\W+', '', username.replace(" ", "")) or "resume"
    n = 0
    while True:
        filename = f"{base}{n if n > 0 else ''}.{extension.lower()}"
        full_path = os.path.join(documents_path, filename)
        if not os.path.exists(full_path):
            return full_path
        n += 1

def clean_text(input_text):
    return ' '.join(input_text.split()) 

def save_resume():
    name = name_entry.get()
    email = email_entry.get()
    phone = phone_entry.get()
    address = Address_entry.get()
    education = education_entry.get("1.0", "end").strip()
    skills = skills_entry.get("1.0", "end").strip()
    summary = summary_text.get("1.0", "end").strip()
    working_experience = working_experience_entry.get("1.0", "end").strip()
    filetype = file_type.get()

    lines = [
        f"{name}",
        f"📧 {email}",
        f"📞 {phone}",
        f"🏡 {address}",
        "",
        "Skills:",
        skills,
        "",
        "Education:",
        education,
        "",
        "Working Experience:",
        working_experience,
        "",
        "Summary:",
        summary
    ]
    
    content = "\n".join(lines)
    generated_filepath = get_next_filename(filetype, name)

    try:
        if filetype == "TXT":
            with open(generated_filepath, "w") as f:
                f.write(content)
            status_label.configure(text=f"Saved to: {generated_filepath}", text_color="green")

        elif filetype == "PDF":
            pdf = canvas.Canvas(generated_filepath, pagesize=letter)
            pdf.setFont("Times-Roman", 12)
            width, height = letter

            # Title section (Name)
            pdf.setFont("Times-Roman", 50)
            pdf.drawString(72, height - 100, f"{name}")

            # Draw the image (resume photo)
            if image_filepath:
                if os.path.exists(image_filepath):
                    pdf.drawImage(image_filepath, width - 215, height - 150, width=144, height=144)
                else:
                    messagebox.showerror("Error", "Image file does not exist")
                    return

            # Draw a line separator
            pdf.line(72, height - 160, width - 72, height - 160)

            y_position = height - 220 

            # Personal Info Section
            pdf.setFont("Times-Roman", 16)
            pdf.drawString(72, y_position + 35, "Personal Info:")
            y_position -= 30  # Space below the title

            pdf.setFont("Times-Roman", 14)
            pdf.drawString(72, y_position + 39, f"📧 {email}")
            y_position -= 25
            pdf.drawString(72, y_position + 39, f"📞 {phone}")
            y_position -= 25
            pdf.drawString(72, y_position + 39, f"🏡 {address}")
            y_position -= 20
            pdf.line(72, y_position+ 39, width - 72, y_position + 39)
            y_position -= 40  

            # Skills Section
            pdf.setFont("Times-Roman", 16)
            pdf.drawString(72, y_position + 55, "Skills:")
            y_position -= 20

            pdf.setFont("Times-Roman", 14)
            pdf.drawString(72, y_position + 55, skills)
            y_position -= 20
            pdf.line(72, y_position, width - 72, y_position)
            y_position -= 60

            # Education Section
            pdf.setFont("Times-Roman", 16)
            pdf.drawString(72, y_position + 35, "Education:")
            y_position -= 30

            pdf.setFont("Times-Roman", 14)
            text_obj = pdf.beginText(72, y_position + 45)

            lines = education.splitlines()
            for line in lines:
                text_obj.textLine(line)
                y_position -= 14  # Adjust spacing per line

            pdf.drawText(text_obj)

            # Add line separator
            y_position -= 10
            pdf.line(72, y_position, width - 72, y_position)
            y_position -= 60

            # Working Experience Section
            pdf.setFont("Times-Roman", 16)
            pdf.drawString(72, y_position + 35, "Working Experience:")
            y_position -= 30

            pdf.setFont("Times-Roman", 14)
            text_obj = pdf.beginText(72, y_position + 45)

            for line in working_experience.splitlines():
                text_obj.textLine(line)
                y_position -= 14  # Adjust vertical spacing between lines

            pdf.drawText(text_obj)
            pdf.line(72, y_position, width - 72, y_position)
            y_position -= 60

            # Summary Section
            pdf.setFont("Times-Roman", 16)
            pdf.drawString(72, y_position + 35, "Professional Summary:")
            y_position -= 30

            pdf.setFont("Times-Roman", 14)
            text_obj = pdf.beginText(72, y_position + 45)

            for line in summary.splitlines():
                text_obj.textLine(line)
                y_position -= 14

            pdf.drawText(text_obj)           
            pdf.save()
            status_label.configure(text=f"Saved to: {generated_filepath}", text_color="green")

    except Exception as e:
        status_label.configure(text=f"Error: {str(e)}", text_color="red")

def print_resume():
    try:
        name = name_entry.get()
        email = email_entry.get()
        phone = phone_entry.get()
        address = Address_entry.get()
        skills = skills_entry.get("1.0", END).strip()
        education = education_entry.get("1.0", END).strip()
        working_experience = working_experience_entry.get("1.0", END).strip()
        summary = summary_text.get("1.0", END).strip()

        printer_name = win32print.GetDefaultPrinter()
        if not printer_name:
            raise Exception("No default printer found.")

        hprinter = win32print.OpenPrinter(printer_name)
        pdc = win32ui.CreateDC()
        pdc.CreatePrinterDC(printer_name)
        pdc.StartDoc("Resume Print")
        pdc.StartPage()

        # Fonts
        name_font = win32ui.CreateFont({
            "name": "Courier New",
            "height": 200,   # Larger for name
            "weight": 900,
        })
        title_font = win32ui.CreateFont({
            "name": "Courier New",
            "height": 160,   # Section titles
            "weight": 700,
        })
        content_font = win32ui.CreateFont({
            "name": "Courier New",
            "height": 120,   # Regular content
            "weight": 400,
        })

        x = 100
        y = 50
        line_width = 2800

        def draw_line():
            nonlocal y
            y += 20
            pdc.MoveTo((x, y))
            pdc.LineTo((line_width, y))
            y += 20

        # Name
        y += 50
        pdc.SelectObject(name_font)
        pdc.TextOut(x, y, name)
        y += 150  # Larger space after name
        draw_line()

        # Personal Info
        y += 2
        pdc.SelectObject(title_font)
        pdc.TextOut(x, y, "Personal Info:")
        y += 150
        pdc.SelectObject(content_font)
        pdc.TextOut(x, y, f"📧 {email}")
        y += 100
        pdc.TextOut(x, y, f"📞 {phone}")
        y += 100
        pdc.TextOut(x, y, f"🏡 {address}")
        y += 200
        draw_line()

        # Skills
        y += 2
        pdc.SelectObject(title_font)
        pdc.TextOut(x, y, "Skills:")
        y += 150
        pdc.SelectObject(content_font)
        for line in skills.splitlines():
            pdc.TextOut(x, y, line)
            y += 130
        y += 150
        draw_line()

        # Education
        y += 2
        pdc.SelectObject(title_font)
        pdc.TextOut(x, y, "Education:")
        y += 150
        pdc.SelectObject(content_font)
        for line in education.splitlines():
            pdc.TextOut(x, y, line)
            y += 130
        y += 150
        draw_line()

        # Working Experience
        y += 2
        pdc.SelectObject(title_font)
        pdc.TextOut(x, y, "Working Experience:")
        y += 150
        pdc.SelectObject(content_font)
        for line in working_experience.splitlines():
            pdc.TextOut(x, y, line)
            y += 130
        y += 150
        draw_line()

        # Professional Summary
        y += 2
        pdc.SelectObject(title_font)
        pdc.TextOut(x, y, "Professional Summary:")
        y += 150
        pdc.SelectObject(content_font)
        for line in summary.splitlines():
            pdc.TextOut(x, y, line)
            y += 100

        pdc.EndPage()
        pdc.EndDoc()
        pdc.DeleteDC()

    except Exception as e:
        messagebox.showerror("Printer Error", f"Unable to print the resume:\n{str(e)}")


# Main Resume Builder App Code

def main_app():
    global name_entry, email_entry, phone_entry, working_experience_entry, summary_text, file_type, status_label, image_label, skills_entry,education_entry,Address_entry, generated_filepath, image_filepath

    root = ctk.CTk()
    root.title("Resume Builder")
    root.geometry("1100x900")
    center_window(root, 1100, 900)

    root.resizable(True, True)

    # Title
    ctk.CTkLabel(root, text="📝 Resume Builder", font=("Segoe UI", 26, "bold")).grid(row=0, column=0, columnspan=2, pady=20)

    # Main Form Frame (left column)
    form_frame = ctk.CTkFrame(root ,width=800, height=750)
    form_frame.grid_propagate(False)  # Prevent the frame from resizing to fit its contents
    form_frame.grid(row=1, column=0, pady=10, padx=20, sticky="nsew")
    
    # Configure grid columns (left side for form fields, right side for buttons and image)
    form_frame.grid_columnconfigure(0, weight=2)  # Left column for form fields (Full Name, etc.)
    form_frame.grid_columnconfigure(1, weight=1)  # Right column for the working experience and summary
   

    # Helper function to create labeled entries
    def create_labeled_entry(label_text, row, column, columnspan=1):
        label = ctk.CTkLabel(form_frame, text=label_text, font=("Segoe UI", 12))
        label.grid(row=row, column=column, pady=(10, 0), padx=20, sticky="w")
        entry = ctk.CTkEntry(form_frame, width=600,)
        entry.grid(row=row+1, column=column, pady=5, padx=20, sticky="w", columnspan=columnspan)
        return entry

    # Add form fields (left side)
    name_entry = create_labeled_entry("Full Name", 0, 0)
    phone_entry = create_labeled_entry("Phone", 2, 0)
    email_entry = create_labeled_entry("Email", 4, 0)
    Address_entry = create_labeled_entry("Address", 6, 0)

    ctk.CTkLabel(form_frame, text="Skills", font=("Segoe UI", 12)).grid(row=8, column=0, pady=(10, 0), padx=20, sticky="w")
    skills_entry = ctk.CTkTextbox(form_frame, width=500, height=180, border_color="gray", border_width=2)
    skills_entry.grid(row=9, column=0, rowspan=5, pady=5, padx=20, sticky="w")

    # RIGHT SIDE entries
    ctk.CTkLabel(form_frame, text="Working Experience", font=("Segoe UI", 12)).grid(row=0, column=1, pady=(10, 0), padx=20, sticky="w")
    working_experience_entry = ctk.CTkTextbox(form_frame, width=500, height=180, border_color="gray", border_width=2)
    working_experience_entry.grid(row=1, column=1, rowspan=5, pady=5, padx=20, sticky="w")

    ctk.CTkLabel(form_frame, text="Education", font=("Segoe UI", 12)).grid(row=6, column=1, pady=(10, 0), padx=20, sticky="w")
    education_entry = ctk.CTkTextbox(form_frame, width=500, height=180, border_color="gray", border_width=2)
    education_entry.grid(row=7, column=1, rowspan=5, pady=5, padx=20, sticky="w")

    ctk.CTkLabel(form_frame, text="Summary", font=("Segoe UI", 12)).grid(row=12, column=1, pady=(10, 0), padx=20, sticky="w")
    summary_text = ctk.CTkTextbox(form_frame, width=500, height=180, border_color="gray", border_width=2)
    summary_text.grid(row=13, column=1, rowspan=5, columnspan=1, pady=5, padx=20, sticky="w")

    # Second Frame for Upload Photo, File Type Dropdown, and Buttons
    button_frame = ctk.CTkFrame(root)
    button_frame.grid(row=1, column=1, padx=20, pady=10, sticky="nsew")

    # Image Upload Section inside the second frame
    image_frame = ctk.CTkFrame(button_frame, width=300, height=200)
    image_frame.grid(row=0, column=0, padx=20, pady=10, sticky="w")
    image_label = ctk.CTkLabel(image_frame, text="No photo uploaded", font=("Segoe UI", 12))
    image_label.grid(row=0, column=0, pady=5)

    upload_btn = ctk.CTkButton(image_frame, text="Upload Profile Photo", command=upload_photo)
    upload_btn.grid(row=1, column=0, pady=5)

    # File type dropdown and buttons below the image section in the second frame
    ctk.CTkLabel(button_frame, text="Export As", font=("Segoe UI", 12)).grid(row=2, column=0, pady=(15, 5), padx=20, sticky="w")
    file_type = ctk.StringVar(value="PDF")
    file_dropdown = ctk.CTkOptionMenu(button_frame, values=["PDF", "TXT"], variable=file_type, width=140)
    file_dropdown.grid(row=3, column=0, pady=8, padx=20, sticky="w")

    # Action buttons (Generate and Print) in the second frame
    ctk.CTkButton(button_frame, text="Generate Resume", command=save_resume, fg_color="#27AE60").grid(row=4, column=0, pady=10, padx=20, sticky="w")
    ctk.CTkButton(button_frame, text="Print Resume", command=print_resume, fg_color="#2980B9").grid(row=5, column=0, pady=10, padx=20, sticky="w")

    # Button to add pointer circle

    # Status Label (for saved file confirmation)
    status_label = ctk.CTkLabel(root, text="", font=("Segoe UI", 10))
    status_label.grid(row=12, column=0, columnspan=2, pady=10)

    root.mainloop()
    
# Login Page UI
login_root = ctk.CTk()
login_root.title("Login - Resume Builder")
center_window(login_root, 400, 300)

frame = ctk.CTkFrame(login_root)
frame.pack(pady=20, padx=30, fill="both", expand=True)

ctk.CTkLabel(frame, text="Login or Create Account", font=("Segoe UI", 16, "bold")).pack(pady=15)
username_entry = ctk.CTkEntry(frame, placeholder_text="Username")
username_entry.pack(pady=5)
password_entry = ctk.CTkEntry(frame, placeholder_text="Password", show="*")
password_entry.pack(pady=5)

show_password_checkbox = ctk.CTkCheckBox(frame, text="Show Password", command=toggle_password_visibility)
show_password_checkbox.pack(pady=(5, 15)) 

ctk.CTkButton(frame, text="Login", command=login).pack(pady=5)
ctk.CTkButton(frame, text="Create Account", command=create_account).pack(pady=5)

login_root.mainloop()
