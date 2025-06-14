import tkinter as tk
from tkinter import filedialog, messagebox, simpledialog
import subprocess
import os
import getpass

# Git command runner
def run_git_command(command, cwd):
    print(f"🔄 Running: {command}")
    try:
        result = subprocess.run(
            command,
            cwd=cwd,
            check=True,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True
        )
        if result.stdout.strip():
            print(f"✅ {result.stdout.strip()}")
        return True
    except subprocess.CalledProcessError as e:
        print(f"❌ Error: {e.stderr}")
        return False

# First push routine
def push_to_git(project_path, repo_url):
    if not os.path.exists(project_path):
        print(f"❌ Directory {project_path} not found")
        return False

    use_pat = input("🔑 Use Personal Access Token (PAT)? [y/N]: ").strip().lower() == "y"
    if use_pat:
        pat = getpass.getpass("🔐 Enter your PAT: ").strip()
        if repo_url.startswith("https://"):
            repo_url = repo_url.replace("https://", f"https://:{pat}@")
        else:
            print("❌ PAT can only be used with HTTPS URLs.")
            return False

    commands = [
        ["git", "init"],
        ["git", "add", "."],
        ["git", "commit", "-m", "Initial commit"],
        ["git", "remote", "add", "origin", repo_url],
        ["git", "branch", "-M", "main"],
        ["git", "push", "--force", "origin", "HEAD:main"]
    ]

    os.chdir(project_path)

    for cmd in commands:
        if not run_git_command(cmd, project_path):
            return False

    print("🎉 Code successfully pushed to remote repository!")
    return True

class GitGUIApp(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("Git Automation GUI")
        self.geometry("800x350")
        self.resizable(False, False)

        # Project directory entry
        tk.Label(self, text="Project Directory:").grid(row=0, column=0, sticky="w", padx=5, pady=5)
        self.path_entry = tk.Entry(self, width=60)
        self.path_entry.grid(row=0, column=1, padx=5, pady=5)
        self._add_entry_menu(self.path_entry)
        tk.Button(self, text="Browse…", command=self.browse_folder, bg="#e0e0e0").grid(row=0, column=2, padx=5)

        # Repository URL entry
        tk.Label(self, text="Repository URL:").grid(row=1, column=0, sticky="w", padx=5, pady=5)
        self.url_entry = tk.Entry(self, width=60)
        self.url_entry.grid(row=1, column=1, padx=5, pady=5)
        self._add_entry_menu(self.url_entry)

        # Buttons frame
        btn_frame = tk.Frame(self)
        btn_frame.grid(row=2, column=0, columnspan=3, pady=15, sticky="ew")
        for i in range(6):
            btn_frame.grid_columnconfigure(i, weight=1)

        tk.Button(btn_frame, text="Clone",       width=12, command=self.clone_repo,  bg="#dda0dd").grid(row=0, column=0, padx=3)
        tk.Button(btn_frame, text="Get Status",  width=12, command=self.get_status,  bg="#add8e6").grid(row=0, column=1, padx=3)
        tk.Button(btn_frame, text="Add",         width=12, command=self.add_only,    bg="#e0ffff").grid(row=0, column=2, padx=3)
        tk.Button(btn_frame, text="Commit",      width=12, command=self.commit_only, bg="#ffb347").grid(row=0, column=3, padx=3)
        tk.Button(btn_frame, text="Push",        width=12, command=self.push_only,   bg="#98fb98").grid(row=0, column=4, padx=3)
        tk.Button(btn_frame, text="First Push",  width=12, command=self.first_push,  bg="#ffa07a").grid(row=0, column=5, padx=3)

    def _add_entry_menu(self, entry):
        menu = tk.Menu(entry, tearoff=0)
        menu.add_command(label="Copy", command=lambda: self._copy_entry(entry))
        menu.add_command(label="Paste", command=lambda: self._paste_entry(entry))
        entry.bind("<Button-3>", lambda e: menu.tk_popup(e.x_root, e.y_root))

    def _copy_entry(self, entry):
        try:
            sel = entry.selection_get()
            self.clipboard_clear()
            self.clipboard_append(sel)
        except tk.TclError:
            pass

    def _paste_entry(self, entry):
        try:
            txt = self.clipboard_get()
            entry.delete(0, tk.END)
            entry.insert(0, txt)
        except tk.TclError:
            pass

    def browse_folder(self):
        d = filedialog.askdirectory()
        if d:
            self.path_entry.delete(0, tk.END)
            self.path_entry.insert(0, d)

    def clone_repo(self):
        url = self.url_entry.get().strip()
        if not url:
            url = simpledialog.askstring("Clone", "Enter repository URL:")
            if not url:
                return
            self.url_entry.insert(0, url)
        parent = filedialog.askdirectory(title="Select parent folder for clone")
        if not parent:
            return
        run_git_command(["git", "clone", url], cwd=parent)
        name = os.path.splitext(os.path.basename(url))[0]
        clone_path = os.path.join(parent, name)
        self.path_entry.delete(0, tk.END)
        self.path_entry.insert(0, clone_path)
        messagebox.showinfo("Clone", f"Cloned into:\n{clone_path}")

    def get_status(self):
        path = self.path_entry.get().strip()
        if not os.path.isdir(path):
            messagebox.showerror("Error", f"Directory not found:\n{path}")
            return
        run_git_command(["git", "status"], cwd=path)

    def add_only(self):
        path = self.path_entry.get().strip()
        if not os.path.isdir(path):
            messagebox.showerror("Error", f"Directory not found:\n{path}")
            return
        run_git_command(["git", "add", "."], cwd=path)
        messagebox.showinfo("Add", "git add . completed")

    def commit_only(self):
        path = self.path_entry.get().strip()
        if not os.path.isdir(path):
            messagebox.showerror("Error", f"Directory not found:\n{path}")
            return
        msg = simpledialog.askstring("Commit", "Enter commit message:")
        if not msg:
            return
        run_git_command(["git", "add", "."], cwd=path)
        ok = run_git_command(["git", "commit", "-m", msg], cwd=path)
        if ok:
            messagebox.showinfo("Commit", "git commit completed")
        else:
            messagebox.showerror("Commit failed", "Check console for details")

    def push_only(self):
        path = self.path_entry.get().strip()
        if not os.path.isdir(path):
            messagebox.showerror("Error", f"Directory not found:\n{path}")
            return
        url = self.url_entry.get().strip()
        ok = run_git_command(["git", "remote", "get-url", "origin"], cwd=path)
        if not ok and url:
            run_git_command(["git", "remote", "add", "origin", url], cwd=path)
        run_git_command(["git", "push", "origin", "main"], cwd=path)
        messagebox.showinfo("Push", "git push completed")

    def first_push(self):
        path = self.path_entry.get().strip()
        url  = self.url_entry.get().strip()
        if not path or not url:
            messagebox.showwarning("Missing data", "Ensure both path and URL are filled")
            return
        success = push_to_git(path, url)
        if success:
            messagebox.showinfo("First Push", "First push completed successfully")
        else:
            messagebox.showerror("First Push failed", "Check console for details")

if __name__ == "__main__":
    app = GitGUIApp()
    app.mainloop()


#C:\Users\97254\PycharmProjects\automate_connect_to_remote_repository_first_time

#https://github.com/ShayShuve123/automatically_push_to_git.git
