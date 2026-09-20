import customtkinter as ctk
from PIL import Image, ImageTk
import socket
import threading
import os
from concurrent.futures import ThreadPoolExecutor

ctk.set_appearance_mode("dark")
root = ctk.CTk()
root.title("Network Scanner")
root.geometry("950x600")

IMAGE_PATH = os.path.join(os.path.dirname(__file__), "bg.jpg")
original_bg = Image.open(IMAGE_PATH)
bg_label = ctk.CTkLabel(root, text="")
bg_label.place(x=0, y=0, relwidth=1, relheight=1)
bg_photo = None

def resize_bg(event):
    global bg_photo
    if event.widget == root:
        resized = original_bg.resize((event.width, event.height), Image.Resampling.LANCZOS)
        bg_photo = ImageTk.PhotoImage(resized)
        bg_label.configure(image=bg_photo)

root.bind("<Configure>", resize_bg)

card = ctk.CTkFrame(root, width=540, height=470, corner_radius=25, fg_color="white")
card.place(relx=0.5, rely=0.5, anchor="center")

ctk.CTkLabel(card, text="Network Scanner", font=("Segoe UI", 20, "bold"), text_color="#0f172a").pack(pady=(20, 2))
status_label = ctk.CTkLabel(card, text="Ready to scan 65k ports", font=("Segoe UI", 11), text_color="#64748b")
status_label.pack()

ip_var = ctk.StringVar(value="127.0.0.1")
ctk.CTkEntry(card, textvariable=ip_var, width=300, height=38, corner_radius=12, fg_color="#f1f5f9", text_color="black", justify="center").pack(pady=10)

output = ctk.CTkTextbox(card, width=470, height=260, corner_radius=15, fg_color="#0f172a", text_color="#22c55e", font=("Consolas", 11))
output.pack(pady=5, padx=15)
output.insert("0.0", " Ready...\n")

progress = ctk.CTkProgressBar(card, width=470, height=8, corner_radius=4)
progress.pack(pady=8)
progress.set(0)

def scan():
    target = ip_var.get().strip()
    output.delete("0.0", "end")
    progress.set(0)
    scan_btn.configure(state="disabled", text="Scanning 65k ports...")
    services = {135:"epmap", 445:"microsoft-ds", 80:"http", 443:"https", 22:"ssh", 5040:"Unknown", 7680:"Unknown"}
    
    def scan_port(port):
        try:
            s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            s.settimeout(0.2)
            if s.connect_ex((target, port)) == 0:
                serv = services.get(port, "Unknown")
                root.after(0, lambda: output.insert("end", f" [+] Port {port:<6} OPEN | Service: {serv}\n"))
            s.close()
        except:
            pass
        root.after(0, lambda: progress.set(port / 65535))
        root.after(0, lambda: status_label.configure(text=f"Scanning... {port}/65535"))
        
    def run_fast():
        with ThreadPoolExecutor(max_workers=800) as executor:
            executor.map(scan_port, range(1, 65536))
        root.after(0, lambda: status_label.configure(text="Scan Completed - 65k ports scanned"))
        root.after(0, lambda: output.insert("end", "\n [✓] Full 65k Scan Completed.\n"))
        root.after(0, lambda: scan_btn.configure(state="normal", text="Start Full Scan"))
        root.after(0, lambda: progress.set(1))
        
    threading.Thread(target=run_fast, daemon=True).start()

scan_btn = ctk.CTkButton(card, text="Start Full Scan (1-65535)", command=scan, width=250, height=42, corner_radius=21, fg_color="#0f172a", hover_color="#1e293b", font=("Segoe UI", 13, "bold"))
scan_btn.pack(pady=10)

root.mainloop()
