import tkinter as tk
from tkinter import filedialog, messagebox
import subprocess
import os

class GitGUIApp(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("Git Automation GUI")
        self.resizable(False, False)

        # שדה לבחירת תיקיית הפרויקט
        tk.Label(self, text="Project Directory:").grid(row=0, column=0, sticky="w", padx=5, pady=5)
        self.path_entry = tk.Entry(self, width=50)
        self.path_entry.grid(row=0, column=1, padx=5, pady=5)
        tk.Button(self, text="Browse…", command=self.browse_folder).grid(row=0, column=2, padx=5)

        # שדה להזנת URL של ה-repo
        tk.Label(self, text="Repository URL:").grid(row=1, column=0, sticky="w", padx=5, pady=5)
        self.url_entry = tk.Entry(self, width=50)
        self.url_entry.grid(row=1, column=1, padx=5, pady=5)

        # מסגרת לכפתורי Git
        btn_frame = tk.Frame(self)
        btn_frame.grid(row=2, column=0, columnspan=3, pady=10)
        tk.Button(btn_frame, text="Status",  width=12, command=lambda: self.run_simple("status")).grid(row=0, column=0, padx=3)
        tk.Button(btn_frame, text="Fetch",   width=12, command=lambda: self.run_simple("fetch")).grid(row=0, column=1, padx=3)
        tk.Button(btn_frame, text="Pull",    width=12, command=lambda: self.run_simple("pull")).grid(row=0, column=2, padx=3)
        tk.Button(btn_frame, text="Push",    width=12, command=self.push_to_git).grid(row=0, column=3, padx=3)

        # תיבת טקסט להצגת הלוג
        self.output = tk.Text(self, height=15, width=80, state="disabled")
        self.output.grid(row=3, column=0, columnspan=3, padx=5, pady=5)
        scrollbar = tk.Scrollbar(self, command=self.output.yview)
        scrollbar.grid(row=3, column=3, sticky='nsew')
        self.output['yscrollcommand'] = scrollbar.set

    def log(self, message):
        self.output.configure(state="normal")
        self.output.insert(tk.END, message + "\n")
        self.output.see(tk.END)
        self.output.configure(state="disabled")

    def browse_folder(self):
        folder = filedialog.askdirectory()
        if folder:
            self.path_entry.delete(0, tk.END)
            self.path_entry.insert(0, folder)

    def run_git_command(self, cmd_list, cwd):
        self.log(f"🔄 Running: {' '.join(cmd_list)}")
        try:
            res = subprocess.run(
                cmd_list,
                cwd=cwd,
                check=True,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                text=True
            )
            out = res.stdout.strip()
            if out:
                self.log(f"✅ {out}")
            return True
        except subprocess.CalledProcessError as e:
            err = e.stderr.strip() or e.stdout.strip()
            self.log(f"❌ Error: {err}")
            return False

    def run_simple(self, subcommand):
        project_path = self.path_entry.get().strip()
        if not os.path.isdir(project_path):
            messagebox.showerror("Error", f"Directory not found:\n{project_path}")
            return
        # לדוגמא: git status, git fetch, git pull
        self.log("")  # רווח לפני התחלת הפעולה
        return self.run_git_command(["git", subcommand], project_path)

    def push_to_git(self):
        project_path = self.path_entry.get().strip()
        repo_url     = self.url_entry.get().strip()

        # נקה את המסך
        self.output.configure(state="normal")
        self.output.delete(1.0, tk.END)
        self.output.configure(state="disabled")

        if not os.path.isdir(project_path):
            messagebox.showerror("Error", f"Directory not found:\n{project_path}")
            return

        commands = [
            ["git", "init"],
            ["git", "add", "."],
            ["git", "commit", "-m", "Initial commit"],
            ["git", "remote", "add", "origin", repo_url],
            ["git", "branch", "-M", "main"],
            ["git", "push", "-u", "origin", "main"]
        ]

        for cmd in commands:
            if not self.run_git_command(cmd, project_path):
                self.log("❌ Push process aborted due to error.❌")
                return

        self.log("🎉 Code successfully pushed to remote repository!")
        messagebox.showinfo("Success", "🎉 הקוד נדחף בהצלחה ל־remote!")

if __name__ == "__main__":
    app = GitGUIApp()
    app.mainloop()
