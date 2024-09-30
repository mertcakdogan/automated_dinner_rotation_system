import random
import tkinter as tk
from tkinter import ttk, messagebox, simpledialog
from datetime import datetime, timedelta
import sqlite3
import json

class YemekSirasiUygulamasi:
    def __init__(self, master):
        self.master = master
        self.master.title("Akşam Yemeği Sırası Belirleme / Dinner Duty Rotation")
        self.master.geometry("650x550")
        self.master.configure(bg="#f0f0f0")

        self.style = ttk.Style()
        self.style.theme_use('clam')
        self.style.configure('TButton', font=('Helvetica', 12), padding=10)
        self.style.configure('TLabel', font=('Helvetica', 12), background="#f0f0f0")
        self.style.configure('Header.TLabel', font=('Helvetica', 18, 'bold'))

        self.current_language = 'tr'  # Varsayılan dil Türkçe
        self.texts = self.get_texts()

        self.conn = sqlite3.connect('dinner_rotation.db')
        self.create_table()
        
        self.load_data()
        self.create_widgets()

    def create_table(self):
        cursor = self.conn.cursor()
        cursor.execute('''
        CREATE TABLE IF NOT EXISTS friends
        (id INTEGER PRIMARY KEY, name TEXT UNIQUE)
        ''')
        cursor.execute('''
        CREATE TABLE IF NOT EXISTS rotation
        (id INTEGER PRIMARY KEY, start_date TEXT, rotation_order TEXT)
        ''')
        self.conn.commit()

    def load_data(self):
        cursor = self.conn.cursor()
        cursor.execute("SELECT name FROM friends")
        self.arkadaslar = [row[0] for row in cursor.fetchall()]
        
        cursor.execute("SELECT start_date, rotation_order FROM rotation ORDER BY id DESC LIMIT 1")
        result = cursor.fetchone()
        if result:
            self.baslangic_tarihi = datetime.strptime(result[0], "%Y-%m-%d").date()
            rotation_order = json.loads(result[1])
            self.sira = {datetime.strptime(date, "%Y-%m-%d").date(): friend 
                         for date, friend in rotation_order.items()}
        else:
            self.baslangic_tarihi = datetime.now().date()
            self.sira = {}

    def save_data(self):
        cursor = self.conn.cursor()
        cursor.execute("DELETE FROM friends")
        cursor.executemany("INSERT INTO friends (name) VALUES (?)", 
                           [(friend,) for friend in self.arkadaslar])
        
        if self.sira:
            rotation_order = json.dumps({date.strftime("%Y-%m-%d"): friend 
                                         for date, friend in self.sira.items()})
            cursor.execute("INSERT INTO rotation (start_date, rotation_order) VALUES (?, ?)",
                           (self.baslangic_tarihi.strftime("%Y-%m-%d"), rotation_order))
        
        self.conn.commit()

    def get_texts(self):
        return {
            'tr': {
                'title': "Akşam Yemeği Sırası Belirleme",
                'add_friend': "Arkadaş Ekle",
                'draw': "Kura Çek",
                'who_today': "Bugün Kim?",
                'change_language': "Change to English",
                'friend_name': "Yeni arkadaşın adını girin:",
                'success': "Başarılı",
                'friend_added': "{} arkadaş listesine eklendi.",
                'warning': "Uyarı",
                'friend_exists': "Bu arkadaş zaten listede var.",
                'min_friends': "Kura çekmek için en az 2 arkadaş gerekli.",
                'dinner_order': "Yemek Sırası:",
                'info': "Bilgi",
                'no_draw': "Henüz kura çekilmemiş. Lütfen önce kura çekin.",
                'past_turn': "Sıra {}'daydı. Yeni kura çekmelisiniz.",
                'today_turn': "Bugün sıra {}'da.",
                'future_turn': "{} gün sonra sıra {}'da olacak.",
                'todays_responsible': "Bugünün Sorumlusu"
            },
            'en': {
                'title': "Dinner Duty Rotation",
                'add_friend': "Add Friend",
                'draw': "Draw",
                'who_today': "Who's Today?",
                'change_language': "Türkçe'ye Geç",
                'friend_name': "Enter the name of the new friend:",
                'success': "Success",
                'friend_added': "{} has been added to the friend list.",
                'warning': "Warning",
                'friend_exists': "This friend is already in the list.",
                'min_friends': "At least 2 friends are required to draw.",
                'dinner_order': "Dinner Order:",
                'info': "Information",
                'no_draw': "No draw has been made yet. Please draw first.",
                'past_turn': "It was {}'s turn. You should draw again.",
                'today_turn': "Today is {}'s turn.",
                'future_turn': "In {} days, it will be {}'s turn.",
                'todays_responsible': "Today's Responsible"
            }
        }

    def create_widgets(self):
        main_frame = ttk.Frame(self.master, padding="20 20 20 20", style='TFrame')
        main_frame.pack(fill=tk.BOTH, expand=True)

        self.header_label = ttk.Label(main_frame, text=self.texts[self.current_language]['title'], style='Header.TLabel')
        self.header_label.pack(pady=(0, 20))

        button_frame = ttk.Frame(main_frame)
        button_frame.pack(fill=tk.X, pady=10)

        self.add_friend_button = ttk.Button(button_frame, text=self.texts[self.current_language]['add_friend'], command=self.arkadas_ekle)
        self.add_friend_button.pack(side=tk.LEFT, padx=(0, 10))

        self.draw_button = ttk.Button(button_frame, text=self.texts[self.current_language]['draw'], command=self.kura_cek)
        self.draw_button.pack(side=tk.LEFT, padx=(0, 10))

        self.who_today_button = ttk.Button(button_frame, text=self.texts[self.current_language]['who_today'], command=self.bugun_kim)
        self.who_today_button.pack(side=tk.LEFT)

        self.change_language_button = ttk.Button(main_frame, text=self.texts[self.current_language]['change_language'], command=self.change_language)
        self.change_language_button.pack(pady=10)

        self.arkadas_listesi = tk.Listbox(main_frame, font=('Helvetica', 12), height=5)
        self.arkadas_listesi.pack(fill=tk.X, pady=10)

        self.sonuc_text = tk.Text(main_frame, wrap=tk.WORD, font=('Helvetica', 12), height=10)
        self.sonuc_text.pack(fill=tk.BOTH, expand=True)

    def change_language(self):
        self.current_language = 'en' if self.current_language == 'tr' else 'tr'
        self.update_texts()

    def update_texts(self):
        self.master.title(self.texts[self.current_language]['title'])
        self.header_label.config(text=self.texts[self.current_language]['title'])
        self.add_friend_button.config(text=self.texts[self.current_language]['add_friend'])
        self.draw_button.config(text=self.texts[self.current_language]['draw'])
        self.who_today_button.config(text=self.texts[self.current_language]['who_today'])
        self.change_language_button.config(text=self.texts[self.current_language]['change_language'])

    def arkadas_ekle(self):
        yeni_arkadas = simpledialog.askstring(self.texts[self.current_language]['add_friend'], 
                                              self.texts[self.current_language]['friend_name'])
        if yeni_arkadas and yeni_arkadas not in self.arkadaslar:
            self.arkadaslar.append(yeni_arkadas)
            self.arkadas_listesi.insert(tk.END, yeni_arkadas)
            self.save_data()
            messagebox.showinfo(self.texts[self.current_language]['success'], 
                                self.texts[self.current_language]['friend_added'].format(yeni_arkadas))
        elif yeni_arkadas in self.arkadaslar:
            messagebox.showwarning(self.texts[self.current_language]['warning'], 
                                   self.texts[self.current_language]['friend_exists'])

    def kura_cek(self):
        if len(self.arkadaslar) < 2:
            messagebox.showwarning(self.texts[self.current_language]['warning'], 
                                   self.texts[self.current_language]['min_friends'])
            return

        random.shuffle(self.arkadaslar)
        self.baslangic_tarihi = datetime.now().date()
        self.sira = {self.baslangic_tarihi + timedelta(days=i): arkadas for i, arkadas in enumerate(self.arkadaslar)}
        
        self.save_data()
        
        self.sonuc_text.delete('1.0', tk.END)
        self.sonuc_text.insert(tk.END, self.texts[self.current_language]['dinner_order'] + "\n\n")
        for tarih, arkadas in self.sira.items():
            self.sonuc_text.insert(tk.END, f"{tarih.strftime('%d.%m.%Y')}: {arkadas}\n")


    def kura_cek(self):
        if len(self.arkadaslar) < 2:
            messagebox.showwarning(self.texts[self.current_language]['warning'], 
                                   self.texts[self.current_language]['min_friends'])
            return

        random.shuffle(self.arkadaslar)
        self.baslangic_tarihi = datetime.now().date()
        self.sira = {self.baslangic_tarihi + timedelta(days=i): arkadas for i, arkadas in enumerate(self.arkadaslar)}
        
        self.sonuc_text.delete('1.0', tk.END)
        self.sonuc_text.insert(tk.END, self.texts[self.current_language]['dinner_order'] + "\n\n")
        for tarih, arkadas in self.sira.items():
            self.sonuc_text.insert(tk.END, f"{tarih.strftime('%d.%m.%Y')}: {arkadas}\n")

    def bugun_kim(self):
        bugun = datetime.now().date()
        if not self.sira:
            messagebox.showinfo(self.texts[self.current_language]['info'], 
                                self.texts[self.current_language]['no_draw'])
            return

        en_yakin_tarih = min(self.sira.keys(), key=lambda x: abs(x - bugun))
        kisi = self.sira[en_yakin_tarih]
        
        if en_yakin_tarih < bugun:
            messagebox.showinfo(self.texts[self.current_language]['info'], 
                                self.texts[self.current_language]['past_turn'].format(kisi))
        elif en_yakin_tarih == bugun:
            messagebox.showinfo(self.texts[self.current_language]['todays_responsible'], 
                                self.texts[self.current_language]['today_turn'].format(kisi))
        else:
            gun_farki = (en_yakin_tarih - bugun).days
            messagebox.showinfo(self.texts[self.current_language]['info'], 
                                self.texts[self.current_language]['future_turn'].format(gun_farki, kisi))

if __name__ == "__main__":
    root = tk.Tk()
    app = YemekSirasiUygulamasi(root)
    root.mainloop()
    