import customtkinter as ctk
import qrcode
from PIL import Image, ImageTk
from pyzbar import pyzbar
import cv2
import os
import sys
from tkinter import filedialog, messagebox
from datetime import datetime

ctk.set_appearance_mode("dark")
ctk.set_default_color_theme("blue")

ACCENT = "#3B82F6"
ACCENT_HOVER = "#2563EB"
BG_DARK = "#0F172A"
BG_CARD = "#1E293B"
BG_INPUT = "#334155"
TEXT_PRIMARY = "#F1F5F9"
TEXT_SECONDARY = "#94A3B8"
SUCCESS = "#22C55E"
DANGER = "#EF4444"


class QRKodApp(ctk.CTk):
    def __init__(self):
        super().__init__()

        self.title("QR Kod Üretici & Okuyucu")
        self.geometry("900x650")
        self.minsize(800, 600)
        self.configure(fg_color=BG_DARK)

        self.qr_image_label = None
        self.cap = None
        self.scanning = False

        self._build_ui()

    def _build_ui(self):
        self.grid_columnconfigure(0, weight=1)
        self.grid_columnconfigure(1, weight=1)
        self.grid_rowconfigure(1, weight=1)

        header = ctk.CTkFrame(self, fg_color="transparent", height=60)
        header.grid(row=0, column=0, columnspan=2, sticky="ew", padx=20, pady=(15, 5))
        header.grid_columnconfigure(0, weight=1)

        ctk.CTkLabel(
            header,
            text="QR Kod",
            font=ctk.CTkFont(size=26, weight="bold"),
            text_color=ACCENT,
        ).grid(row=0, column=0, sticky="w")
        ctk.CTkLabel(
            header,
            text="Üretici & Okuyucu",
            font=ctk.CTkFont(size=26, weight="bold"),
            text_color=TEXT_PRIMARY,
        ).grid(row=0, column=1, sticky="w", padx=(5, 0))

        self.tabview = ctk.CTkTabview(
            self,
            fg_color=BG_CARD,
            segmented_button_fg_color=BG_INPUT,
            segmented_button_selected_color=ACCENT,
            segmented_button_selected_hover_color=ACCENT_HOVER,
            text_color=TEXT_PRIMARY,
        )
        self.tabview.grid(row=1, column=0, columnspan=2, sticky="nsew", padx=20, pady=(5, 15))

        self.tab_uret = self.tabview.add("  QR Üret  ")
        self.tab_oku = self.tabview.add("  QR Oku  ")

        self._build_uretici_tab()
        self._build_oku_tab()

    def _build_uretici_tab(self):
        self.tab_uret.grid_columnconfigure(0, weight=1)
        self.tab_uret.grid_columnconfigure(1, weight=1)
        self.tab_uret.grid_rowconfigure(0, weight=1)

        left_frame = ctk.CTkFrame(self.tab_uret, fg_color="transparent")
        left_frame.grid(row=0, column=0, sticky="nsew", padx=20, pady=20)
        left_frame.grid_rowconfigure(2, weight=1)

        ctk.CTkLabel(
            left_frame,
            text="Metin veya URL girin",
            font=ctk.CTkFont(size=14, weight="bold"),
            text_color=TEXT_PRIMARY,
        ).grid(row=0, column=0, sticky="w", pady=(0, 8))

        self.input_textbox = ctk.CTkTextbox(
            left_frame,
            height=120,
            fg_color=BG_INPUT,
            text_color=TEXT_PRIMARY,
            font=ctk.CTkFont(size=13),
            corner_radius=10,
            border_width=1,
            border_color="#475569",
        )
        self.input_textbox.grid(row=1, column=0, sticky="ew", pady=(0, 12))
        self.input_textbox.insert("1.0", "https://example.com")

        options_frame = ctk.CTkFrame(left_frame, fg_color="transparent")
        options_frame.grid(row=2, column=0, sticky="ew", pady=(0, 12))
        options_frame.grid_columnconfigure((0, 1), weight=1)

        ctk.CTkLabel(options_frame, text="Boyut:", text_color=TEXT_SECONDARY, font=ctk.CTkFont(size=12)).grid(row=0, column=0, sticky="w")
        self.size_var = ctk.StringVar(value="Orta")
        ctk.CTkSegmentedButton(
            options_frame,
            values=["Küçük", "Orta", "Büyük"],
            variable=self.size_var,
            fg_color=BG_INPUT,
            selected_color=ACCENT,
            selected_hover_color=ACCENT_HOVER,
            text_color=TEXT_PRIMARY,
            font=ctk.CTkFont(size=11),
        ).grid(row=1, column=0, columnspan=2, sticky="ew", pady=(4, 0))

        ctk.CTkLabel(options_frame, text="Kenar Boşluğu:", text_color=TEXT_SECONDARY, font=ctk.CTkFont(size=12)).grid(row=2, column=0, sticky="w", pady=(10, 0))
        self.border_var = ctk.StringVar(value="4")
        ctk.CTkSegmentedButton(
            options_frame,
            values=["1", "2", "4", "8"],
            variable=self.border_var,
            fg_color=BG_INPUT,
            selected_color=ACCENT,
            selected_hover_color=ACCENT_HOVER,
            text_color=TEXT_PRIMARY,
            font=ctk.CTkFont(size=11),
        ).grid(row=3, column=0, columnspan=2, sticky="ew", pady=(4, 0))

        btn_frame = ctk.CTkFrame(left_frame, fg_color="transparent")
        btn_frame.grid(row=3, column=0, sticky="ew")
        btn_frame.grid_columnconfigure((0, 1), weight=1)

        ctk.CTkButton(
            btn_frame,
            text="QR Kod Üret",
            command=self.qr_uret,
            fg_color=ACCENT,
            hover_color=ACCENT_HOVER,
            height=40,
            corner_radius=10,
            font=ctk.CTkFont(size=13, weight="bold"),
        ).grid(row=0, column=0, sticky="ew", padx=(0, 6))

        ctk.CTkButton(
            btn_frame,
            text="Kaydet",
            command=self.qr_kaydet,
            fg_color="#475569",
            hover_color="#64748B",
            height=40,
            corner_radius=10,
            font=ctk.CTkFont(size=13, weight="bold"),
        ).grid(row=0, column=1, sticky="ew", padx=(6, 0))

        right_frame = ctk.CTkFrame(self.tab_uret, fg_color=BG_CARD, corner_radius=12)
        right_frame.grid(row=0, column=1, sticky="nsew", padx=(0, 20), pady=20)

        self.qr_preview_label = ctk.CTkLabel(
            right_frame,
            text="QR kod burada\ngörünecek",
            font=ctk.CTkFont(size=14),
            text_color=TEXT_SECONDARY,
        )
        self.qr_preview_label.pack(expand=True, fill="both", padx=15, pady=15)

        self.qr_image_data = None

    def _build_oku_tab(self):
        self.tab_oku.grid_columnconfigure(0, weight=1)
        self.tab_oku.grid_rowconfigure(1, weight=1)

        top_frame = ctk.CTkFrame(self.tab_oku, fg_color="transparent")
        top_frame.grid(row=0, column=0, sticky="ew", padx=20, pady=(20, 10))
        top_frame.grid_columnconfigure((0, 1, 2), weight=1)

        ctk.CTkButton(
            top_frame,
            text="Kameradan Oku",
            command=self.kameradan_oku_baslat,
            fg_color=ACCENT,
            hover_color=ACCENT_HOVER,
            height=40,
            corner_radius=10,
            font=ctk.CTkFont(size=13, weight="bold"),
        ).grid(row=0, column=0, sticky="ew", padx=(0, 6))

        ctk.CTkButton(
            top_frame,
            text="Durdur",
            command=self.kamerayi_durdur,
            fg_color=DANGER,
            hover_color="#DC2626",
            height=40,
            corner_radius=10,
            font=ctk.CTkFont(size=13, weight="bold"),
        ).grid(row=0, column=1, sticky="ew", padx=6)

        ctk.CTkButton(
            top_frame,
            text="Dosyadan Oku",
            command=self.dosyadan_oku,
            fg_color="#475569",
            hover_color="#64748B",
            height=40,
            corner_radius=10,
            font=ctk.CTkFont(size=13, weight="bold"),
        ).grid(row=0, column=2, sticky="ew", padx=(6, 0))

        content_frame = ctk.CTkFrame(self.tab_oku, fg_color="transparent")
        content_frame.grid(row=1, column=0, sticky="nsew", padx=20, pady=(0, 20))
        content_frame.grid_columnconfigure(0, weight=1)
        content_frame.grid_rowconfigure(0, weight=1)

        self.camera_label = ctk.CTkLabel(
            content_frame,
            text="Kamera burada görünecek\nveya bir QR kod dosyası seçin",
            font=ctk.CTkFont(size=14),
            text_color=TEXT_SECONDARY,
            fg_color=BG_CARD,
            corner_radius=12,
        )
        self.camera_label.grid(row=0, column=0, sticky="nsew")

        result_frame = ctk.CTkFrame(content_frame, fg_color=BG_CARD, corner_radius=10, height=60)
        result_frame.grid(row=1, column=0, sticky="ew", pady=(10, 0))
        result_frame.grid_columnconfigure(0, weight=1)

        ctk.CTkLabel(
            result_frame,
            text="Okunan Sonuç:",
            font=ctk.CTkFont(size=12, weight="bold"),
            text_color=TEXT_SECONDARY,
        ).grid(row=0, column=0, sticky="w", padx=15, pady=(8, 0))

        self.result_label = ctk.CTkLabel(
            result_frame,
            text="Henüz okunmadı",
            font=ctk.CTkFont(size=13),
            text_color=SUCCESS,
            wraplength=600,
        )
        self.result_label.grid(row=1, column=0, sticky="w", padx=15, pady=(0, 10))

        self.camera_image_label = None

    def _boyut_map(self):
        return {"Küçük": qrcode.constants.ERROR_CORRECT_L, "Orta": qrcode.constants.ERROR_CORRECT_M, "Büyük": qrcode.constants.ERROR_CORRECT_H}

    def qr_uret(self):
        text = self.input_textbox.get("1.0", "end-1c").strip()
        if not text:
            messagebox.showwarning("Uyarı", "Lütfen bir metin veya URL girin.")
            return

        border = int(self.border_var.get())
        error_level = self._boyut_map()[self.size_var.get()]

        qr = qrcode.QRCode(version=None, error_correction=error_level, box_size=10, border=border)
        qr.add_data(text)
        qr.make(fit=True)

        img = qr.make_image(fill_color="#1E293B", back_color="transparent").convert("RGBA")
        self.qr_image_data = img

        display_size = (280, 280)
        img_resized = img.resize(display_size, Image.Resampling.LANCZOS)
        photo = ImageTk.PhotoImage(img_resized)

        self.qr_preview_label.configure(image=photo, text="")
        self.qr_preview_label.image = photo

    def qr_kaydet(self):
        if not self.qr_image_data:
            messagebox.showwarning("Uyarı", "Önce bir QR kod üretin.")
            return

        file_path = filedialog.asksaveasfilename(
            defaultextension=".png",
            filetypes=[("PNG", "*.png"), ("JPEG", "*.jpg"), ("SVG", "*.svg"), ("Tüm Dosyalar", "*.*")],
            initialfile=f"qr_{datetime.now().strftime('%Y%m%d_%H%M%S')}.png",
        )
        if file_path:
            self.qr_image_data.save(file_path)
            messagebox.showinfo("Kaydedildi", f"QR kod kaydedildi:\n{file_path}")

    def kameradan_oku_baslat(self):
        if self.scanning:
            return
        self.cap = cv2.VideoCapture(0)
        if not self.cap.isOpened():
            messagebox.showerror("Hata", "Kamera açılamadı.")
            return
        self.scanning = True
        self.kare_goster()

    def kare_goster(self):
        if not self.scanning or not self.cap:
            return

        ret, frame = self.cap.read()
        if not ret:
            self.kamerayi_durdur()
            return

        decoded = pyzbar.decode(frame)
        for obj in decoded:
            data = obj.data.decode("utf-8")
            self.result_label.configure(text=data, text_color=SUCCESS)
            self._sonucu_kopyala(data)

        frame_rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        h, w = frame_rgb.shape[:2]
        max_w, max_h = 550, 400
        scale = min(max_w / w, max_h / h)
        new_w, new_h = int(w * scale), int(h * scale)
        frame_resized = cv2.resize(frame_rgb, (new_w, new_h))

        img = Image.fromarray(frame_resized)
        photo = ImageTk.PhotoImage(img)

        self.camera_label.configure(image=photo, text="")
        self.camera_label.image = photo

        self.after(30, self.kare_goster)

    def kamerayi_durdur(self):
        self.scanning = False
        if self.cap:
            self.cap.release()
            self.cap = None
        self.camera_label.configure(image="", text="Kamera durduruldu", text_color=TEXT_SECONDARY)

    def dosyadan_oku(self):
        file_path = filedialog.askopenfilename(filetypes=[("Resim", "*.png *.jpg *.jpeg *.bmp *.gif"), ("Tüm Dosyalar", "*.*")])
        if not file_path:
            return

        img = cv2.imread(file_path)
        if img is None:
            messagebox.showerror("Hata", "Dosya okunamadı.")
            return

        decoded = pyzbar.decode(img)
        if not decoded:
            messagebox.showinfo("Bilgi", "QR kod bulunamadı.")
            return

        results = [obj.data.decode("utf-8") for obj in decoded]
        display = "\n".join(results)
        self.result_label.configure(text=display, text_color=SUCCESS)

        img_rgb = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)
        pil_img = Image.fromarray(img_rgb)
        display_size = (400, 300)
        pil_img = pil_img.resize(display_size, Image.Resampling.LANCZOS)
        photo = ImageTk.PhotoImage(pil_img)
        self.camera_label.configure(image=photo, text="")
        self.camera_label.image = photo

    def _sonucu_kopyala(self, text):
        self.clipboard_clear()
        self.clipboard_append(text)


if __name__ == "__main__":
    app = QRKodApp()
    app.mainloop()
