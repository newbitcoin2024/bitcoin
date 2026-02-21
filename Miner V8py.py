import tkinter as tk
from tkinter import ttk, messagebox
import json, ssl, socket, webbrowser, os, subprocess, platform, time, sys

# === COULEURS ===
BG = "#f5f5f5"
FG = "#202020"
ACCENT = "#3A86FF"

# === STYLE ===
def setup_style():
    style = ttk.Style()
    style.theme_use("clam")
    style.configure("TFrame", background=BG)
    style.configure("TLabel", background=BG, foreground=FG, font=("Segoe UI", 11))
    style.configure("TButton", font=("Segoe UI", 10, "bold"), padding=7,
                    background=ACCENT, foreground="white", borderwidth=0)
    style.map("TButton", background=[("active", "#265DCA")])
    style.configure("Link.TButton", font=("Segoe UI", 10, "bold"), padding=6,
                    background=BG, foreground=ACCENT, borderwidth=0)
    style.map("Link.TButton", foreground=[("active", "#1e40af")])
    style.configure("Title.TLabel", font=("Segoe UI Semibold", 15), foreground="#000000", background=BG)

# === OUTILS ===
def open_url(url): webbrowser.open(url)

# === CONFIGURATION ===
config_file = "config.json"
default_config = {
    "bitcoin_cli": "/Users/francisc/newbitcoin/build/src/bitcoin-cli",
    "datadir": "/Users/francisc/Library/Application Support/Bitcoin",
    "rpcuser": "papa",
    "rpcpassword": "marc",
    "rpcport": "8332",
    "newbitcoin_address": ""
}

def load_config():
    if os.path.exists(config_file):
        try:
            with open(config_file, 'r') as f:
                return json.load(f)
        except json.JSONDecodeError:
            pass
    save_config(default_config)
    return default_config

def save_config(config):
    with open(config_file, 'w') as f:
        json.dump(config, f, indent=4)

config = load_config()

# === UTILITAIRE : exécuter sans ouvrir de terminal ===
def silent_run(cmd, capture_output=True):
    """Exécute une commande sans ouvrir de console Windows."""
    startupinfo = None
    creationflags = 0
    if os.name == "nt":  # Windows uniquement
        startupinfo = subprocess.STARTUPINFO()
        startupinfo.dwFlags |= subprocess.STARTF_USESHOWWINDOW
        creationflags = subprocess.CREATE_NO_WINDOW
    return subprocess.run(
        cmd,
        stdout=subprocess.PIPE if capture_output else None,
        stderr=subprocess.PIPE if capture_output else None,
        startupinfo=startupinfo,
        creationflags=creationflags,
        text=True,
        check=False
    )

# === CONNEXION ELECTRUMX ===
def check_connection():
    try:
        context = ssl.create_default_context()
        context.check_hostname = False
        context.verify_mode = ssl.CERT_NONE
        with context.wrap_socket(socket.create_connection(("newbitcoin.ddns.net", 50002), timeout=3),
                                 server_hostname="newbitcoin.ddns.net"):
            status_label.config(text="✅ Connecté à newbitcoin.ddns.net", foreground="#007744")
            return True
    except Exception:
        status_label.config(text="❌ Connexion échouée", foreground="#cc0000")
        return False

def get_fee():
    if not check_connection(): return
    fee_label.config(text="⏳ Lecture des frais...")
    try:
        context = ssl.create_default_context()
        context.check_hostname = False
        context.verify_mode = ssl.CERT_NONE
        with context.wrap_socket(socket.create_connection(("newbitcoin.ddns.net", 50002), timeout=3),
                                 server_hostname="newbitcoin.ddns.net") as sock:
            req = {"jsonrpc": "2.0", "method": "blockchain.estimatefee", "params": [2], "id": 1}
            sock.sendall(json.dumps(req).encode() + b"\n")
            resp = json.loads(sock.recv(1024).decode())
            fee = resp.get("result", None)
            if fee:
                fee_label.config(text=f"💸 Frais estimés : {fee:.6f} BTC", foreground="#007744")
            else:
                fee_label.config(text="Erreur de lecture", foreground="#cc0000")
    except Exception:
        fee_label.config(text="Erreur de connexion", foreground="#cc0000")

def get_block_height():
    if not check_connection(): return
    block_label.config(text="⏳ Lecture du dernier bloc...")
    try:
        context = ssl.create_default_context()
        context.check_hostname = False
        context.verify_mode = ssl.CERT_NONE
        with context.wrap_socket(socket.create_connection(("newbitcoin.ddns.net", 50002), timeout=3),
                                 server_hostname="newbitcoin.ddns.net") as sock:
            req = {"jsonrpc": "2.0", "method": "blockchain.headers.subscribe", "params": [], "id": 2}
            sock.sendall(json.dumps(req).encode() + b"\n")
            resp = json.loads(sock.recv(1024).decode())
            height = resp.get("result", {}).get("height", None)
            if height:
                block_label.config(text=f"📦 Dernier bloc : {height}", foreground="#007744")
            else:
                block_label.config(text="Erreur de lecture", foreground="#cc0000")
    except Exception:
        block_label.config(text="Erreur réseau", foreground="#cc0000")

# === PARAMÈTRES ===
def validate_address(address):
    return address.startswith("bc1") and len(address) >= 20

def open_settings_window():
    def save_settings():
        config["bitcoin_cli"] = bitcoin_cli_entry.get()
        config["datadir"] = datadir_entry.get()
        config["rpcuser"] = rpcuser_entry.get()
        config["rpcpassword"] = rpcpassword_entry.get()
        config["rpcport"] = rpcport_entry.get()
        addr = newbitcoin_address_entry.get()
        if not validate_address(addr):
            messagebox.showerror("Erreur", "Adresse invalide.")
            return
        config["newbitcoin_address"] = addr
        save_config(config)
        messagebox.showinfo("OK", "Paramètres enregistrés.")
        settings_window.destroy()

    settings_window = tk.Toplevel(root)
    settings_window.title("Configurer les paramètres")
    settings_window.geometry("600x300")
    fields = [
        ("Chemin bitcoin-cli", "bitcoin_cli"),
        ("Chemin datadir", "datadir"),
        ("Nom utilisateur RPC", "rpcuser"),
        ("Mot de passe RPC", "rpcpassword"),
        ("Port RPC", "rpcport"),
        ("Adresse NewBitcoin", "newbitcoin_address"),
    ]
    entries = {}
    for i, (label, key) in enumerate(fields):
        tk.Label(settings_window, text=label).grid(row=i, column=0, sticky="w")
        e = tk.Entry(settings_window, width=50)
        e.insert(0, config.get(key, ""))
        e.grid(row=i, column=1)
        entries[key] = e
    bitcoin_cli_entry, datadir_entry, rpcuser_entry, rpcpassword_entry, rpcport_entry, newbitcoin_address_entry = (
        entries["bitcoin_cli"], entries["datadir"], entries["rpcuser"],
        entries["rpcpassword"], entries["rpcport"], entries["newbitcoin_address"]
    )
    tk.Button(settings_window, text="Enregistrer", command=save_settings).grid(row=len(fields), column=0, columnspan=2, pady=10)

# === MINAGE ===
def verifier_serveur():
    result = silent_run([
        config["bitcoin_cli"],
        "-rpcuser=" + config["rpcuser"],
        "-rpcpassword=" + config["rpcpassword"],
        "-rpcport=" + config["rpcport"],
        "getblockchaininfo"
    ])
    return result.returncode == 0

def get_wallet_info():
    result = silent_run([
        config["bitcoin_cli"],
        "-rpcuser=" + config["rpcuser"],
        "-rpcpassword=" + config["rpcpassword"],
        "-rpcport=" + config["rpcport"],
        "getwalletinfo"
    ])
    if result.returncode == 0:
        try:
            return json.loads(result.stdout)
        except json.JSONDecodeError:
            pass
    log_text.insert(tk.END, "⚠️ Erreur wallet\n")
    return None

def miner_et_afficher_infos(adresse):
    silent_run([
        config["bitcoin_cli"],
        "-rpcport=" + config["rpcport"],
        "-rpcuser=" + config["rpcuser"],
        "-rpcpassword=" + config["rpcpassword"],
        "generatetoaddress", "1", adresse
    ], capture_output=False)
    result = silent_run([
        config["bitcoin_cli"],
        "-rpcport=" + config["rpcport"],
        "-rpcuser=" + config["rpcuser"],
        "-rpcpassword=" + config["rpcpassword"],
        "getblockchaininfo"
    ])
    try:
        return json.loads(result.stdout)['blocks']
    except Exception:
        log_text.insert(tk.END, "Erreur minage\n")
        return None

def demarrer_minage():
    adr = config["newbitcoin_address"]
    if not validate_address(adr):
        log_text.insert(tk.END, "Adresse invalide.\n")
        return

    temps_ecoule = 0
    last_height = 0
    is_mining = True

    while is_mining:
        if not verifier_serveur():
            log_text.insert(tk.END, "⚠️ NewBitcoin Core non lancé.\n")
            break

        wallet_info = get_wallet_info()
        if wallet_info:
            wallet_name = wallet_info.get('walletname', 'inconnu')
            balance = wallet_info.get('balance', 0.0)
            immature_balance = wallet_info.get('immature_balance', 0.0)
            current_height = miner_et_afficher_infos(adr)
            total_nbtc = balance + immature_balance

            log_text.insert(tk.END, f"Portefeuille chargé : {wallet_name} : OK\n")
            log_text.insert(tk.END, f"Hauteur actuelle locale: {current_height}\n")
            log_text.insert(tk.END, f"Solde mature : {balance}\n")
            log_text.insert(tk.END, f"Solde immature : {immature_balance}\n")
            log_text.insert(tk.END, f"Solde total : {total_nbtc}\n")

            if current_height and current_height > last_height:
                log_text.insert(tk.END, f"Bloc trouvé ! Nouvelle hauteur : {current_height}\n")
                last_height = current_height
                temps_ecoule = 0

            log_text.insert(tk.END, f"Temps depuis le dernier bloc miné : {temps_ecoule} secondes\n\n")
            temps_ecoule += 1

        log_text.see("end")
        log_text.update()
        time.sleep(1)

# === INTERFACE ===
root = tk.Tk()
root.title("💠 NewBitcoin Miner Pro")
root.geometry("950x640")
root.configure(bg=BG)
setup_style()

# HEADER
header = ttk.Frame(root)
header.pack(fill="x", pady=10)
ttk.Label(header, text="🪙 NewBitcoin Miner", style="Title.TLabel").pack(side="left", padx=20)
ttk.Button(header, text="⚙️ Paramètres", command=open_settings_window).pack(side="right", padx=20)

# MAIN
main = ttk.Frame(root)
main.pack(fill="both", expand=True, padx=25, pady=5)
main.columnconfigure(0, weight=1)
main.columnconfigure(1, weight=1)

# GAUCHE
left = ttk.Frame(main)
left.grid(row=0, column=0, sticky="nsew", padx=(0, 10))
ttk.Label(left, text="🌐 Connexion réseau", font=("Segoe UI", 12, "bold")).pack(anchor="w")
status_label = ttk.Label(left, text="⏳ Vérification...")
status_label.pack(anchor="w", pady=(0,5))
ttk.Button(left, text="Tester la connexion", command=check_connection).pack(anchor="w")
ttk.Label(left, text="⛓️ Blockchain", font=("Segoe UI", 12, "bold")).pack(anchor="w", pady=(10,2))
ttk.Button(left, text="📦 Dernier bloc", command=get_block_height).pack(anchor="w")
block_label = ttk.Label(left, text="Bloc inconnu", foreground=FG)
block_label.pack(anchor="w")
ttk.Button(left, text="💸 Estimer les frais", command=get_fee).pack(anchor="w")
fee_label = ttk.Label(left, text="Frais non disponibles", foreground=FG)
fee_label.pack(anchor="w", pady=(2,10))
ttk.Label(left, text="🔗 Liens utiles", font=("Segoe UI", 12, "bold")).pack(anchor="w", pady=(10,4))
for text, url in [
    ("🌐 Explorer", "https://henicoin.com"),
    ("💾 Télécharger NewBitcoin", "https://newbitcoin.fr/newbitcoin/fr/telecharger.html"),
    ("📦 Blocks", "https://github.com/newbitcoin2024/blocks/archive/refs/heads/main.zip"),
    ("💬 Telegram", "https://t.me/+tz_fG8Z7U9dhMjI0"),
    ("📘 Facebook", "https://www.facebook.com/profile.php?id=61570437304719"),
]:
    ttk.Button(left, text=text, style="Link.TButton", command=lambda u=url: open_url(u)).pack(anchor="w", pady=2)

# DROITE
right = ttk.Frame(main)
right.grid(row=0, column=1, sticky="nsew")
ttk.Label(right, text="⚒️ Minage local", font=("Segoe UI", 12, "bold")).pack(anchor="w")
ttk.Label(right, text="Adresse de récompense :", foreground=FG).pack(anchor="w")
ttk.Label(right, text=config["newbitcoin_address"] or "Non configurée",
          foreground=ACCENT, background=BG, font=("Segoe UI", 10, "bold")).pack(anchor="w")
ttk.Button(right, text="▶️ Démarrer le minage", command=demarrer_minage).pack(pady=5)
ttk.Label(right, text="📜 Journal d'activité", font=("Segoe UI", 12, "bold")).pack(anchor="w", pady=(15,3))
log_text = tk.Text(right, height=16, bg="#f0f0f0", fg="#333", relief="flat", wrap="word")
log_text.pack(fill="both", expand=True)

# FOOTER
footer = ttk.Frame(root)
footer.pack(fill="x", pady=5)
ttk.Label(footer, text="© Henicoin / NewBitcoin – 2025", foreground="#666", background=BG, font=("Segoe UI", 9)).pack()

check_connection()
root.mainloop()
