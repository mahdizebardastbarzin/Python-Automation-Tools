"""
File Organizer GUI
-----------------
رابط گرافیکی برای سازماندهی فایل‌ها
"""

import tkinter as tk
from tkinter import ttk, filedialog, messagebox
import os
from pathlib import Path
from automation_tools.file_organizer import FileOrganizer

class FileOrganizerGUI:
    def __init__(self, root):
        self.root = root
        self.root.title("سازماندهی فایل‌ها")
        self.root.geometry("600x400")
        self.root.resizable(False, False)
        
        # تنظیم فونت
        self.font = ('Tahoma', 10)
        
        # متغیرها
        self.folder_path = tk.StringVar()
        
        self.create_widgets()
    
    def create_widgets(self):
        # فریم اصلی
        main_frame = ttk.Frame(self.root, padding="20")
        main_frame.pack(fill=tk.BOTH, expand=True)
        
        # عنوان برنامه
        title_label = ttk.Label(
            main_frame,
            text="برنامه سازماندهی فایل‌ها",
            font=('Tahoma', 14, 'bold')
        )
        title_label.pack(pady=(0, 20))
        
        # فریم انتخاب پوشه
        folder_frame = ttk.Frame(main_frame)
        folder_frame.pack(fill=tk.X, pady=10)
        
        ttk.Label(
            folder_frame,
            text="مسیر پوشه:",
            font=self.font
        ).pack(side=tk.RIGHT, padx=5)
        
        self.folder_entry = ttk.Entry(
            folder_frame,
            textvariable=self.folder_path,
            width=50,
            font=self.font,
            state='readonly'
        )
        self.folder_entry.pack(side=tk.RIGHT, fill=tk.X, expand=True, padx=5)
        
        browse_btn = ttk.Button(
            folder_frame,
            text="مرور...",
            command=self.browse_folder,
            style='Accent.TButton'
        )
        browse_btn.pack(side=tk.LEFT, padx=5)
        
        # دکمه‌های عملیات
        btn_frame = ttk.Frame(main_frame)
        btn_frame.pack(pady=20)
        
        self.organize_btn = ttk.Button(
            btn_frame,
            text="سازماندهی فایل‌ها",
            command=self.organize_files,
            style='Accent.TButton',
            state=tk.DISABLED
        )
        self.organize_btn.pack(side=tk.RIGHT, padx=10)
        
        preview_btn = ttk.Button(
            btn_frame,
            text="پیش‌نمایش تغییرات",
            command=self.preview_changes
        )
        preview_btn.pack(side=tk.RIGHT, padx=10)
        
        # ناحیه لاگ
        log_frame = ttk.LabelFrame(main_frame, text="گزارش عملیات", padding=10)
        log_frame.pack(fill=tk.BOTH, expand=True)
        
        self.log_text = tk.Text(
            log_frame,
            height=10,
            wrap=tk.WORD,
            font=('Courier New', 9)
        )
        self.log_text.pack(fill=tk.BOTH, expand=True)
        
        # اسکرول بار
        scrollbar = ttk.Scrollbar(self.log_text)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        self.log_text.config(yscrollcommand=scrollbar.set)
        scrollbar.config(command=self.log_text.yview)
        
        # استایل‌ها
        self.root.style = ttk.Style()
        self.root.style.configure('Accent.TButton', font=('Tahoma', 10, 'bold'))
    
    def browse_folder(self):
        """باز کردن دیالوگ انتخاب پوشه"""
        folder_selected = filedialog.askdirectory()
        if folder_selected:
            self.folder_path.set(folder_selected)
            self.organize_btn.config(state=tk.NORMAL)
            self.log("پوشه انتخاب شد: " + folder_selected)
    
    def log(self, message):
        """نمایش پیام در ناحیه لاگ"""
        self.log_text.insert(tk.END, message + "\n")
        self.log_text.see(tk.END)
        self.root.update_idletasks()
    
    def organize_files(self):
        """سازماندهی فایل‌ها"""
        folder = self.folder_path.get()
        if not folder:
            messagebox.showwarning("هشدار", "لطفاً یک پوشه انتخاب کنید.")
            return
        
        try:
            organizer = FileOrganizer(folder)
            result = organizer.organize()
            
            # نمایش نتیجه
            self.log("\n--- نتیجه نهایی ---")
            for category, files in result.items():
                if files:
                    self.log(f"\n{category.upper()} ({len(files)} فایل):")
                    for file in files:
                        self.log(f"  - {file}")
            
            messagebox.showinfo("موفقیت", "فایل‌ها با موفقیت سازماندهی شدند.")
            
        except Exception as e:
            self.log(f"خطا: {str(e)}")
            messagebox.showerror("خطا", f"خطایی رخ داد:\n{str(e)}")
    
    def preview_changes(self):
        """پیش‌نمایش تغییرات بدون اعمال واقعی"""
        folder = self.folder_path.get()
        if not folder:
            messagebox.showwarning("هشدار", "لطفاً یک پوشه انتخاب کنید.")
            return
        
        try:
            organizer = FileOrganizer(folder)
            result = organizer.organize(dry_run=True)
            
            # نمایش پیش‌نمایش
            self.log("\n--- پیش‌نمایش تغییرات (تغییری اعمال نشد) ---")
            for category, files in result.items():
                if files:
                    self.log(f"\n{category.upper()} ({len(files)} فایل):")
                    for file in files:
                        self.log(f"  - {file} -> {category}/{file}")
            
            messagebox.showinfo(
                "پیش‌نمایش", 
                "پیش‌نمایش تغییرات در پنجره گزارش نمایش داده شد.\n"
                "برای اعمال تغییرات روی دکمه 'سازماندهی فایل‌ها' کلیک کنید."
            )
            
        except Exception as e:
            self.log(f"خطا: {str(e)}")
            messagebox.showerror("خطا", f"خطایی رخ داد:\n{str(e)}")

def main():
    root = tk.Tk()
    app = FileOrganizerGUI(root)
    root.mainloop()

if __name__ == "__main__":
    main()
