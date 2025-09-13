import os
import sys
import numpy as np
from PIL import Image, ImageTk
from ultralytics import YOLO
from tkinter import filedialog
from tkinterdnd2 import TkinterDnD, DND_FILES
import customtkinter as ctk

def resource_path(relative_path):
    try:
        base_path = sys._MEIPASS
    except AttributeError:
        base_path = os.path.abspath(".")
    return os.path.join(base_path, relative_path)

# تحميل موديل YOLO
# يمكنك تغيير "yolov8n.pt" إلى "yolov8s.pt" أو أي وزن آخر
model = YOLO("yolov8n.pt")

LANGUAGES = {
    "ar": {
        "title": "مصنف الصور (YOLO)",
        "login": "تسجيل الدخول",
        "signup": "إنشاء حساب",
        "switch_to_signup": "ليس لديك حساب؟ أنشئ حساب",
        "switch_to_login": "لديك حساب؟ تسجيل الدخول",
        "username": "اسم المستخدم",
        "password": "كلمة المرور",
        "login_btn": "دخول",
        "signup_btn": "إنشاء",
        "drag_label": "اسحب صورة هنا 🖼️",
        "select_image": "📂 اختر صورة يدويًا",
        "result": "النتيجة: ",
        "language": "English"
    },
    "en": {
        "title": "Image Classifier (YOLO)",
        "login": "Login",
        "signup": "Sign Up",
        "switch_to_signup": "No account? Create one",
        "switch_to_login": "Already have an account? Login",
        "username": "Username",
        "password": "Password",
        "login_btn": "Login",
        "signup_btn": "Create",
        "drag_label": "Drag an image here 🖼️",
        "select_image": "📂 Select image manually",
        "result": "Result: ",
        "language": "العربية"
    }
}

class App(TkinterDnD.Tk):
    def __init__(self):
        super().__init__()
        self.geometry("800x700")
        self.title("YOLO Image Classifier")
        self.language = "en"

        self.container = ctk.CTkFrame(self)
        self.container.pack(expand=True, fill="both")

        self.lang_btn = ctk.CTkButton(
            self,
            text=LANGUAGES[self.language]["language"],
            command=self.switch_language,
            width=80
        )
        self.lang_btn.place(x=10, y=10)

        self.show_login_screen()

    def switch_language(self):
        self.language = "ar" if self.language == "en" else "en"
        self.lang_btn.configure(text=LANGUAGES[self.language]["language"])
        self.show_login_screen()

    def clear_container(self):
        for widget in self.container.winfo_children():
            widget.destroy()

    def show_login_screen(self):
        self.clear_container()
        lang = LANGUAGES[self.language]

        ctk.CTkLabel(self.container, text=lang["login"], font=ctk.CTkFont(size=20)).pack(pady=20)
        ctk.CTkLabel(self.container, text=lang["username"]).pack()
        username_entry = ctk.CTkEntry(self.container)
        username_entry.pack(pady=5)
        ctk.CTkLabel(self.container, text=lang["password"]).pack()
        password_entry = ctk.CTkEntry(self.container, show="*")
        password_entry.pack(pady=5)

        ctk.CTkButton(self.container, text=lang["login_btn"], command=self.show_main_screen).pack(pady=10)
        ctk.CTkButton(
            self.container,
            text=lang["switch_to_signup"],
            fg_color="transparent",
            text_color="gray",
            command=self.show_signup_screen
        ).pack(pady=5)

    def show_signup_screen(self):
        self.clear_container()
        lang = LANGUAGES[self.language]

        ctk.CTkLabel(self.container, text=lang["signup"], font=ctk.CTkFont(size=20)).pack(pady=20)
        ctk.CTkLabel(self.container, text=lang["username"]).pack()
        ctk.CTkEntry(self.container).pack(pady=5)
        ctk.CTkLabel(self.container, text=lang["password"]).pack()
        ctk.CTkEntry(self.container, show="*").pack(pady=5)

        ctk.CTkButton(self.container, text=lang["signup_btn"], command=self.show_main_screen).pack(pady=10)
        ctk.CTkButton(
            self.container,
            text=lang["switch_to_login"],
            fg_color="transparent",
            text_color="gray",
            command=self.show_login_screen
        ).pack(pady=5)

    def show_main_screen(self):
        self.clear_container()
        lang = LANGUAGES[self.language]

        frame = ctk.CTkFrame(self.container)
        frame.pack(expand=True, fill="both", padx=20, pady=20)

        label = ctk.CTkLabel(frame, text=lang["drag_label"], font=ctk.CTkFont(size=16))
        label.pack(pady=10)

        image_label = ctk.CTkLabel(frame, text="")
        image_label.pack()

        result_label = ctk.CTkLabel(frame, text="", font=ctk.CTkFont(size=16))
        result_label.pack(pady=10)

        def classify_image(image_path):
            try:
                results = model(image_path)
                detections = []
                for r in results:
                    for box in r.boxes:
                        cls_id = int(box.cls[0])
                        label = model.names[cls_id]
                        conf = float(box.conf[0])
                        detections.append(f"{label} ({conf:.2f})")
                if not detections:
                    return "❌ لم يتم التعرف على أي شيء"
                return ", ".join(detections), results
            except Exception as e:
                return f"Error: {str(e)}", None

        def handle_drop(event):
            path = event.data.strip("{}")
            if os.path.isfile(path):
                try:
                    detections, results = classify_image(path)
                    if results:
                        annotated_frame = results[0].plot()
                        img = Image.fromarray(annotated_frame)
                        img = img.resize((500, 500))
                        img_tk = ImageTk.PhotoImage(img)
                        image_label.configure(image=img_tk, text="")
                        image_label.image = img_tk

                    result_label.configure(text=lang["result"] + detections)
                except Exception as e:
                    print(f"[ERROR] Failed to load image: {e}")
                    result_label.configure(text="❌ تعذر تحميل الصورة")

        self.drop_target_register(DND_FILES)
        self.dnd_bind("<<Drop>>", handle_drop)

        def manual_select():
            path = filedialog.askopenfilename(filetypes=[("Images", "*.png;*.jpg;*.jpeg")])
            if path:
                handle_drop(type("Event", (object,), {"data": path}))

        ctk.CTkButton(frame, text=lang["select_image"], command=manual_select).pack(pady=5)


if __name__ == "__main__":
    app = App()
    app.mainloop()
