import os
import sys
import cv2
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
        "camera": "🎥 تشغيل الكاميرا",
        "result": "النتيجة: ",
        "close_camera": "❌ إيقاف الكاميرا",
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
        "camera": "🎥 Open Camera",
        "result": "Result: ",
        "close_camera": "❌ Close Camera",
        "language": "العربية"
    }
}


class App(TkinterDnD.Tk):
    def __init__(self):
        super().__init__()
        self.geometry("900x750")
        self.title("YOLO Image Classifier")
        self.language = "en"
        self.cap = None  # كائن الكاميرا

        self.container = ctk.CTkFrame(self)
        self.container.pack(expand=True, fill="both")

        self.lang_btn = ctk.CTkButton(
            self,
            text=LANGUAGES[self.language]["language"],
            command=self.switch_language,
            width=80
        )
        self.lang_btn.place(x=10, y=10)

        self.image_label = None
        self.result_label = None

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

        # ✅ Scrollable Frame
        frame = ctk.CTkScrollableFrame(self.container, width=850, height=700)
        frame.pack(expand=True, fill="both", padx=20, pady=20)

        ctk.CTkLabel(frame, text=lang["drag_label"], font=ctk.CTkFont(size=16)).pack(pady=10)

        self.image_label = ctk.CTkLabel(frame, text="")
        self.image_label.pack()

        self.result_label = ctk.CTkLabel(frame, text="", font=ctk.CTkFont(size=16))
        self.result_label.pack(pady=10)

        # أزرار التحكم
        ctk.CTkButton(frame, text=lang["select_image"], command=self.manual_select).pack(pady=5)
        ctk.CTkButton(frame, text=lang["camera"], command=self.open_camera).pack(pady=5)
        ctk.CTkButton(frame, text=lang["close_camera"], command=self.close_camera).pack(pady=5)

        # تفعيل السحب والإفلات
        self.drop_target_register(DND_FILES)
        self.dnd_bind("<<Drop>>", self.handle_drop)

    # ------------------------- 📷 الكاميرا -------------------------

    def open_camera(self):
        if self.cap is None:
            self.cap = cv2.VideoCapture(0)
        self.update_camera()

    def close_camera(self):
        if self.cap:
            self.cap.release()
            self.cap = None
            self.image_label.configure(image="", text="")

    def update_camera(self):
        if self.cap:
            ret, frame = self.cap.read()
            if ret:
                results = model(frame)
                annotated_frame = results[0].plot()
                img = cv2.cvtColor(annotated_frame, cv2.COLOR_BGR2RGB)
                img = Image.fromarray(img).resize((500, 500))
                img_tk = ImageTk.PhotoImage(img)
                self.image_label.configure(image=img_tk, text="")
                self.image_label.image = img_tk

                detections = []
                for r in results:
                    for box in r.boxes:
                        cls_id = int(box.cls[0])
                        label = model.names[cls_id]
                        conf = float(box.conf[0])
                        detections.append(f"{label} ({conf:.2f})")
                if detections:
                    self.result_label.configure(text=LANGUAGES[self.language]["result"] + ", ".join(detections))
                else:
                    self.result_label.configure(text="❌ لا يوجد كشف" if self.language == "ar" else "❌ No detection")

            self.after(1000, self.update_camera)

    # ------------------------- 📂 الصور -------------------------

    def classify_image(self, image_path):
        results = model(image_path)
        detections = []
        for r in results:
            for box in r.boxes:
                cls_id = int(box.cls[0])
                label = model.names[cls_id]
                conf = float(box.conf[0])
                detections.append(f"{label} ({conf:.2f})")
        if not detections:
            return "❌ لم يتم التعرف على أي شيء" if self.language == "ar" else "❌ No detection"
        return ", ".join(detections), results

    def handle_drop(self, event):
        path = event.data.strip("{}")
        if os.path.isfile(path):
            detections, results = self.classify_image(path)
            if results:
                annotated_frame = results[0].plot()
                img = Image.fromarray(annotated_frame)
                img = img.resize((500, 500))
                img_tk = ImageTk.PhotoImage(img)
                self.image_label.configure(image=img_tk, text="")
                self.image_label.image = img_tk
            self.result_label.configure(text=LANGUAGES[self.language]["result"] + detections)

    def manual_select(self):
        path = filedialog.askopenfilename(filetypes=[("Images", "*.png;*.jpg;*.jpeg")])
        if path:
            self.handle_drop(type("Event", (object,), {"data": path}))


if __name__ == "__main__":
    app = App()
    app.mainloop()
