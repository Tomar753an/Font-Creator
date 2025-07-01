import customtkinter as ctk
import tkinter as tk
from tkinter import colorchooser, messagebox

class DrawingEditor(ctk.CTkToplevel):
    def __init__(self, master, font_name, characters, font_format):
        super().__init__(master)
        self.master = master
        self.font_name = font_name
        self.characters = list(characters) # Karakterleri listeye çevir
        self.font_format = font_format
        self.current_char_index = 0
        self.char_data = {} # Çizilen karakter verilerini saklayacak sözlük

        self.title(f"Font Oluşturucu - {self.font_name}")
        self.geometry("1000x700")
        self.resizable(True, True)

        # Ana çerçeveler
        self.grid_columnconfigure(0, weight=3) # Çizim alanı
        self.grid_columnconfigure(1, weight=1) # Kontrol paneli
        self.grid_rowconfigure(0, weight=1)

        # Sol Taraf: Çizim Alanı
        self.drawing_frame = ctk.CTkFrame(self)
        self.drawing_frame.grid(row=0, column=0, padx=10, pady=10, sticky="nsew")
        self.drawing_frame.grid_rowconfigure(0, weight=1)
        self.drawing_frame.grid_columnconfigure(0, weight=1)

        self.current_char_label = ctk.CTkLabel(self.drawing_frame, text=f"Şu an çiziliyor: {self.characters[self.current_char_index]}", font=ctk.CTkFont(size=24, weight="bold"))
        self.current_char_label.pack(pady=10)

        self.canvas_frame = ctk.CTkFrame(self.drawing_frame, width=500, height=500, fg_color="gray")
        self.canvas_frame.pack(pady=10, expand=True)
        self.canvas = tk.Canvas(self.canvas_frame, bg="white", highlightbackground="black", highlightthickness=1)
        self.canvas.pack(expand=True, fill="both")

        self.canvas.bind("<Button-1>", self.on_canvas_click)
        self.canvas.bind("<B1-Motion>", self.on_canvas_drag)

        # Sağ Taraf: Kontrol Paneli
        self.control_frame = ctk.CTkFrame(self)
        self.control_frame.grid(row=0, column=1, padx=10, pady=10, sticky="nsew")
        self.control_frame.grid_columnconfigure(0, weight=1)

        # Boyutlandırma
        self.size_label = ctk.CTkLabel(self.control_frame, text="Izgara Boyutu:")
        self.size_label.pack(pady=(20, 5))
        self.size_slider = ctk.CTkSlider(self.control_frame, from_=10, to=100, number_of_steps=90, command=self.set_grid_size)
        self.size_slider.set(16) # Varsayılan boyut
        self.size_slider.pack(pady=5)
        self.size_value_label = ctk.CTkLabel(self.control_frame, text="16x16")
        self.size_value_label.pack(pady=5)

        self.grid_size = int(self.size_slider.get())
        self.cell_size = 0 # Dinamik olarak hesaplanacak
        self.grid_cells = {} # Hücrelerin durumunu saklayacak

        # Renk Seçimi
        self.color_label = ctk.CTkLabel(self.control_frame, text="Renk Seçimi:")
        self.color_label.pack(pady=(20, 5))
        self.current_color = "#000000" # Varsayılan siyah
        self.color_button = ctk.CTkButton(self.control_frame, text="Renk Seç", command=self.choose_color)
        self.color_button.pack(pady=5)
        self.color_code_entry = ctk.CTkEntry(self.control_frame, placeholder_text="#000000")
        self.color_code_entry.insert(0, self.current_color)
        self.color_code_entry.pack(pady=5)
        self.color_code_entry.bind("<Return>", self.set_color_from_code)

        # Araçlar
        self.tool_label = ctk.CTkLabel(self.control_frame, text="Araçlar:")
        self.tool_label.pack(pady=(20, 5))
        self.pen_button = ctk.CTkButton(self.control_frame, text="Kalem", command=self.set_pen_tool)
        self.eraser_button = ctk.CTkButton(self.control_frame, text="Silgi", command=self.set_eraser_tool)
        self.pen_button.pack(side="left", padx=5, pady=5, expand=True)
        self.eraser_button.pack(side="right", padx=5, pady=5, expand=True)
        self.active_tool = "pen" # Varsayılan kalem
        self.pen_button.configure(fg_color=self.master.cget("fg_color")[1]) # Aktif aracı vurgula

        # Devam Butonu
        self.next_char_button = ctk.CTkButton(self.control_frame, text="Sonraki Harf", command=self.next_character)
        self.next_char_button.pack(pady=(40, 20), fill="x")

        self.draw_grid()
        self.protocol("WM_DELETE_WINDOW", self.on_closing) # Pencere kapatma olayını yakala

    def on_closing(self):
        if messagebox.askokcancel("Çıkış", "Uygulamadan çıkmak istediğinize emin misiniz? Kaydedilmeyen değişiklikler kaybolabilir."):
            self.master.destroy() # Ana pencereyi de kapat
            self.destroy()

    def draw_grid(self):
        self.canvas.delete("all")
        canvas_width = self.canvas.winfo_width()
        canvas_height = self.canvas.winfo_height()

        if canvas_width == 0 or canvas_height == 0: # Pencere henüz oluşturulmadıysa
            self.after(100, self.draw_grid) # Biraz bekleyip tekrar dene
            return

        self.cell_size = min(canvas_width, canvas_height) / self.grid_size

        # Izgara çizgileri
        for i in range(self.grid_size + 1):
            x = i * self.cell_size
            y = i * self.cell_size
            self.canvas.create_line(x, 0, x, self.grid_size * self.cell_size, fill="gray", tags="grid_line")
            self.canvas.create_line(0, y, self.grid_size * self.cell_size, y, fill="gray", tags="grid_line")

        # Kaydedilmiş hücreleri çiz
        current_char = self.characters[self.current_char_index]
        if current_char in self.char_data:
            for (r, c), color in self.char_data[current_char].items():
                x1, y1 = c * self.cell_size, r * self.cell_size
                x2, y2 = x1 + self.cell_size, y1 + self.cell_size
                self.canvas.create_rectangle(x1, y1, x2, y2, fill=color, outline="", tags="pixel")

    def set_grid_size(self, value):
        self.grid_size = int(value)
        self.size_value_label.configure(text=f"{self.grid_size}x{self.grid_size}")
        self.draw_grid()

    def choose_color(self):
        color_code = colorchooser.askcolor(title="Renk Seç")[1]
        if color_code:
            self.current_color = color_code
            self.color_code_entry.delete(0, tk.END)
            self.color_code_entry.insert(0, self.current_color)

    def set_color_from_code(self, event=None):
        color_code = self.color_code_entry.get()
        # Basit bir renk kodu doğrulaması
        if len(color_code) == 7 and color_code.startswith("#"):
            try:
                int(color_code[1:], 16) # Hex değeri geçerli mi kontrol et
                self.current_color = color_code
            except ValueError:
                messagebox.showerror("Hata", "Geçersiz renk kodu. Lütfen #RRGGBB formatında girin.")
        else:
            messagebox.showerror("Hata", "Geçersiz renk kodu. Lütfen #RRGGBB formatında girin.")

    def set_pen_tool(self):
        self.active_tool = "pen"
        self.pen_button.configure(fg_color=self.master.cget("fg_color")[1])
        self.eraser_button.configure(fg_color=self.master.cget("fg_color")[0])

    def set_eraser_tool(self):
        self.active_tool = "eraser"
        self.eraser_button.configure(fg_color=self.master.cget("fg_color")[1])
        self.pen_button.configure(fg_color=self.master.cget("fg_color")[0])

    def on_canvas_click(self, event):
        self._draw_on_canvas(event)

    def on_canvas_drag(self, event):
        self._draw_on_canvas(event)

    def _draw_on_canvas(self, event):
        if self.cell_size == 0: return # Henüz hücre boyutu hesaplanmadıysa

        col = int(event.x / self.cell_size)
        row = int(event.y / self.cell_size)

        if 0 <= col < self.grid_size and 0 <= row < self.grid_size:
            x1, y1 = col * self.cell_size, row * self.cell_size
            x2, y2 = x1 + self.cell_size, y1 + self.cell_size

            current_char = self.characters[self.current_char_index]
            if current_char not in self.char_data:
                self.char_data[current_char] = {}

            if self.active_tool == "pen":
                self.canvas.create_rectangle(x1, y1, x2, y2, fill=self.current_color, outline="", tags="pixel")
                self.char_data[current_char][(row, col)] = self.current_color
            elif self.active_tool == "eraser":
                self.canvas.create_rectangle(x1, y1, x2, y2, fill="white", outline="", tags="pixel")
                if (row, col) in self.char_data[current_char]:
                    del self.char_data[current_char][(row, col)]

    def next_character(self):
        # Mevcut karakterin verilerini kaydet (zaten _draw_on_canvas içinde yapılıyor)

        self.current_char_index += 1
        if self.current_char_index < len(self.characters):
            self.current_char_label.configure(text=f"Şu an çiziliyor: {self.characters[self.current_char_index]}")
            self.canvas.delete("pixel") # Sadece pikselleri sil, ızgarayı değil
            self.draw_grid() # Yeni karakter için ızgarayı ve varsa kaydedilmiş pikselleri çiz
        else:
            messagebox.showinfo("Tamamlandı", "Tüm karakterler çizildi! Şimdi fontu oluşturabilirsiniz.")
            # Burada font oluşturma butonunu veya sürecini başlatabiliriz.
            self.create_font()

    def create_font(self):
        try:
            from fontTools.ttLib import TTFont, newTable
            from fontTools.ttLib.tables._g_l_y_f import Glyph
            from fontTools.pens.basePen import BasePen
            from fontTools.pens.t2CharStringPen import T2CharStringPen
            from fontTools.ttLib.tables.CFF_ import CFFTable, CFFFontSet, CFFFont
            from fontTools.ttLib.tables.CFF_ import TopDict, PrivateDict
            from fontTools.ttLib.tables.CFF_ import CharStrings
            from fontTools.ttLib.tables.CFF_ import GlobalSubrs, LocalSubrs
            from fontTools.ttLib.tables.CFF_ import FDArray, FDSelect
            from fontTools.ttLib.tables.CFF_ import CFFGlyphSet
            from fontTools.ttLib.tables.CFF_ import CFFTable
            from fontTools.ttLib.tables.CFF_ import TopDict, PrivateDict
            from fontTools.ttLib.tables.CFF_ import CharStrings
            from fontTools.ttLib.tables.CFF_ import GlobalSubrs, LocalSubrs
            from fontTools.ttLib.tables.CFF_ import FDArray, FDSelect
            from fontTools.ttLib.tables.CFF_ import CFFGlyphSet

            font = TTFont()
            font['head'] = newTable('head')
            font['hhea'] = newTable('hhea')
            font['maxp'] = newTable('maxp')
            font['OS/2'] = newTable('OS/2')
            font['name'] = newTable('name')
            font['cmap'] = newTable('cmap')
            font['post'] = newTable('post')
            font['glyf'] = newTable('glyf')
            font['loca'] = newTable('loca')
            font['hmtx'] = newTable('hmtx')

            # Basic head table values
            font['head'].macStyle = 0
            font['head'].xMin = 0
            font['head'].yMin = 0
            font['head'].xMax = self.grid_size
            font['head'].yMax = self.grid_size
            font['head'].unitsPerEm = self.grid_size # Units per Em based on grid size
            font['head'].created = font['head'].modified = 0 # Placeholder

            # Basic hhea table values
            font['hhea'].ascender = self.grid_size
            font['hhea'].descender = 0
            font['hhea'].lineGap = 0
            font['hhea'].advanceWidthMax = self.grid_size
            font['hhea'].minLeftSideBearing = 0
            font['hhea'].minRightSideBearing = 0
            font['hhea'].xMaxExtent = self.grid_size
            font['hhea'].caretSlopeRise = 1
            font['hhea'].caretSlopeRun = 0
            font['hhea'].numberOfHMetrics = 0 # Will be updated later

            # Basic maxp table values
            font['maxp'].tableVersion = 0x00010000
            font['maxp'].numGlyphs = 0 # Will be updated later

            # Basic OS/2 table values
            font['OS/2'].usWinAscent = self.grid_size
            font['OS/2'].usWinDescent = 0
            font['OS/2'].sTypoAscender = self.grid_size
            font['OS/2'].sTypoDescender = 0
            font['OS/2'].sTypoLineGap = 0
            font['OS/2'].ulUnicodeRange1 = 0 # Placeholder
            font['OS/2'].ulUnicodeRange2 = 0 # Placeholder
            font['OS/2'].ulUnicodeRange3 = 0 # Placeholder
            font['OS/2'].ulUnicodeRange4 = 0 # Placeholder
            font['OS/2'].achVendID = 'PYTH'
            font['OS/2'].fsSelection = 0 # Placeholder
            font['OS/2'].usWeightClass = 400 # Normal
            font['OS/2'].usWidthClass = 5 # Medium
            font['OS/2'].yAvgCharWidth = self.grid_size # Placeholder

            # Name table
            name_table = font['name']
            name_table.addMultilingualName(self.font_name, nameID=1, platformID=3, platEncID=1, langID=0x409) # Font Family Name
            name_table.addMultilingualName("Regular", nameID=2, platformID=3, platEncID=1, langID=0x409) # Font Subfamily Name
            name_table.addMultilingualName(f"{self.font_name} Regular", nameID=4, platformID=3, platEncID=1, langID=0x409) # Full Font Name
            name_table.addMultilingualName("Version 1.0", nameID=5, platformID=3, platEncID=1, langID=0x409) # Version String
            name_table.addMultilingualName("Generated by Font Oluşturucu", nameID=7, platformID=3, platEncID=1, langID=0x409) # Trademark

            # CMAP table
            cmap = newTable('cmap')
            cmap.tableVersion = 0
            cmap.numCMaps = 1
            cmap.cmaps = []
            cmap.cmaps.append(newTable('cmap', 0))
            cmap.cmaps[0].platformID = 3
            cmap.cmaps[0].platEncID = 1
            cmap.cmaps[0].format = 4
            cmap.cmaps[0].language = 0
            cmap.cmaps[0].cmap = {}

            # Glyf and loca tables
            glyphs = {}
            hmtx = {}
            glyph_order = ['.notdef']

            # Create a .notdef glyph
            notdef_glyph = Glyph()
            notdef_glyph.width = self.grid_size
            notdef_glyph.lsb = 0
            notdef_glyph.endPts = []
            notdef_glyph.components = []
            notdef_glyph.numberOfContours = 0
            glyphs['.notdef'] = notdef_glyph
            hmtx['.notdef'] = (self.grid_size, 0)

            for char_code in self.characters:
                char_name = f"uni{ord(char_code):04X}"
                glyph_order.append(char_name)
                cmap.cmaps[0].cmap[ord(char_code)] = char_name

                glyph = Glyph()
                glyph.width = self.grid_size # Advance width
                glyph.lsb = 0 # Left side bearing

                # Use a pen to draw the glyph
                pen = T2CharStringPen(None, glyphSet=None) # For CFF, but we'll adapt for TTF

                if char_code in self.char_data:
                    min_x, min_y, max_x, max_y = self.grid_size, self.grid_size, 0, 0
                    for (r, c), color in self.char_data[char_code].items():
                        # Draw a rectangle for each pixel
                        x1, y1 = c, self.grid_size - (r + 1) # Flip Y-axis for font coordinates
                        x2, y2 = c + 1, self.grid_size - r
                        pen.moveTo((x1, y1))
                        pen.lineTo((x2, y1))
                        pen.lineTo((x2, y2))
                        pen.lineTo((x1, y2))
                        pen.closePath()

                        min_x = min(min_x, x1)
                        min_y = min(min_y, y1)
                        max_x = max(max_x, x2)
                        max_y = max(max_y, y2)

                    glyph.xMin = min_x
                    glyph.yMin = min_y
                    glyph.xMax = max_x
                    glyph.yMax = max_y
                else:
                    # If no data, create an empty glyph
                    glyph.xMin = 0
                    glyph.yMin = 0
                    glyph.xMax = 0
                    glyph.yMax = 0

                # Convert pen operations to glyph contours
                # This is a simplified approach. For complex shapes, you'd need to parse pen operations.
                # For pixel fonts, we can directly create contours.
                # This part needs careful implementation based on fontTools examples for pixel data.
                # For now, let's assume a simple square for each pixel.
                # A more robust solution would involve creating a custom pen or directly manipulating glyph.coordinates and glyph.endPts.

                # Placeholder for actual glyph data from pen
                # For simplicity, let's just create a dummy contour for now if no pixels are drawn
                if not self.char_data.get(char_code):
                    glyph.numberOfContours = 0
                    glyph.coordinates = []
                    glyph.endPts = []
                else:
                    # This part is tricky. fontTools expects contours. Each pixel is a rectangle (4 points, 1 contour).
                    # We need to combine these into a single glyph.
                    # A proper implementation would involve a custom pen that collects points and contours.
                    # For a simple pixel font, we can iterate through pixels and add their rectangle points.
                    # This is a very basic example and might not produce optimal font outlines.
                    all_coords = []
                    all_end_pts = []
                    current_point_index = 0
                    for (r, c), color in self.char_data[char_code].items():
                        x1, y1 = c, self.grid_size - (r + 1)
                        x2, y2 = c + 1, self.grid_size - r
                        all_coords.extend([(x1, y1), (x2, y1), (x2, y2), (x1, y2)])
                        current_point_index += 4
                        all_end_pts.append(current_point_index - 1)
                    glyph.coordinates = all_coords
                    glyph.endPts = all_end_pts
                    glyph.numberOfContours = len(self.char_data[char_code]) # One contour per pixel

                glyphs[char_name] = glyph
                hmtx[char_name] = (self.grid_size, 0) # Advance width, left side bearing

            font['glyf'].glyphs = glyphs
            font['glyf'].glyphOrder = glyph_order
            font['loca'].build(font['glyf'])
            font['hmtx'].metrics = hmtx

            font['maxp'].numGlyphs = len(glyph_order)
            font['hhea'].numberOfHMetrics = len(hmtx)

            font['cmap'] = cmap

            # Post table (for glyph names)
            post = newTable('post')
            post.formatType = 2.0
            post.glyphOrder = glyph_order
            post.extraNames = []
            font['post'] = post

            # Save the font
            file_path = f"{self.font_name}.{self.font_format.lower()}"
            font.save(file_path)
            messagebox.showinfo("Başarılı", f"Font başarıyla oluşturuldu: {file_path}")

        except Exception as e:
            messagebox.showerror("Hata", f"Font oluşturulurken bir hata oluştu: {e}")
            import traceback
            traceback.print_exc() # Hata detaylarını konsola yazdır

        self.master.destroy() # Ana pencereyi kapat
        self.destroy() # Çizim penceresini kapat


