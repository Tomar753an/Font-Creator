import customtkinter as ctk
import tkinter as tk
from tkinter import messagebox
from drawing_editor import DrawingEditor

class App(ctk.CTk):
    def __init__(self):
        super().__init__()

        self.title("Font Oluşturucu")
        self.geometry("400x300")
        self.resizable(False, False)

        self.grid_columnconfigure(0, weight=1)
        self.grid_rowconfigure((0, 1, 2, 3, 4), weight=1)

        # Font Adı
        self.font_name_label = ctk.CTkLabel(self, text="Font Adı:")
        self.font_name_label.grid(row=0, column=0, padx=20, pady=5, sticky="w")
        self.font_name_entry = ctk.CTkEntry(self, placeholder_text="Örn: MyCustomFont")
        self.font_name_entry.grid(row=1, column=0, padx=20, pady=5, sticky="ew")

        # Karakterler
        self.characters_label = ctk.CTkLabel(self, text="Fonta Eklenecek Karakterler (örn: ABCabc123):")
        self.characters_label.grid(row=2, column=0, padx=20, pady=5, sticky="w")
        self.characters_entry = ctk.CTkEntry(self, placeholder_text="Örn: ABCÇDEFGĞHIİJKLMNOÖPRSŞTUÜVWXYZabcçdefgğhıijklmnoöprsştuüvwxyz0123456789")
        self.characters_entry.grid(row=3, column=0, padx=20, pady=5, sticky="ew")

        # Format Seçimi
        self.format_label = ctk.CTkLabel(self, text="Font Formatı:")
        self.format_label.grid(row=4, column=0, padx=20, pady=5, sticky="w")
        self.format_optionmenu = ctk.CTkOptionMenu(self, values=["TTF", "OTF"])
        self.format_optionmenu.grid(row=5, column=0, padx=20, pady=5, sticky="ew")
        self.format_optionmenu.set("TTF") # Varsayılan değer

        # Başla Butonu
        self.start_button = ctk.CTkButton(self, text="Oluşturmaya Başla", command=self.start_creation, state="disabled")
        self.start_button.grid(row=6, column=0, padx=20, pady=20, sticky="ew")

        # Giriş alanlarındaki değişiklikleri izle
        self.font_name_entry.bind("<KeyRelease>", self._check_fields)
        self.characters_entry.bind("<KeyRelease>", self._check_fields)

    def _check_fields(self, event=None):
        if self.font_name_entry.get() and self.characters_entry.get():
            self.start_button.configure(state="normal")
        else:
            self.start_button.configure(state="disabled")

    def start_creation(self):
        font_name = self.font_name_entry.get()
        characters = self.characters_entry.get()
        font_format = self.format_optionmenu.get()

        if not font_name or not characters:
            messagebox.showerror("Hata", "Lütfen tüm alanları doldurun.")
            return

        # İlk pencereyi kapat ve ikinci pencereyi aç
        self.withdraw() # Ana pencereyi gizle
        self.drawing_editor = DrawingEditor(self, font_name, characters, font_format)
        self.drawing_editor.protocol("WM_DELETE_WINDOW", self.on_drawing_editor_close) # Çizim editörü kapatıldığında ana pencereyi tekrar göster

    def on_drawing_editor_close(self):
        self.drawing_editor.destroy()
        self.deiconify() # Ana pencereyi tekrar göster

if __name__ == "__main__":
    app = App()
    app.mainloop()
