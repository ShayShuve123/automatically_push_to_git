import tkinter as tk
from tkinter import ttk, filedialog, messagebox, simpledialog
import subprocess
import os

class GitGUIApp(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("Git Automation GUI")
        self.geometry("900x550")
        self.resizable(True, True)

        tk.Label(self, text="Project Directory:").grid(row=0, column=0, sticky="w", padx=5, pady=5)
        self.path_entry = tk.Entry(self, width=60)
        self.path_entry.grid(row=0, column=1, padx=5, pady=5)
        self._add_entry_menu(self.path_entry)
        tk.Button(self, text="Browse…", command=self.browse_folder, bg="#e0e0e0").grid(row=0, column=2, padx=5)

        tk.Label(self, text="Repository URL:").grid(row=1, column=0, sticky="w", padx=5, pady=5)
        self.url_entry = tk.Entry(self, width=60)
        self.url_entry.grid(row=1, column=1, padx=5, pady=5)
        self._add_entry_menu(self.url_entry)

        btn_frame = tk.Frame(self, bg="#f0f0f0")
        btn_frame.grid(row=2, column=0, columnspan=3, pady=10, sticky="ew")
        for i in range(8):
            btn_frame.grid_columnconfigure(i, weight=1)

        tk.Button(btn_frame, text="Clone",        width=12, command=self.clone_repo, bg="#dda0dd").grid(row=0, column=0, padx=3)
        tk.Button(btn_frame, text="Status",       width=12, command=lambda: self._run_simple("status"), bg="#add8e6").grid(row=0, column=1, padx=3)
        tk.Button(btn_frame, text="Fetch",        width=12, command=lambda: self._run_simple("fetch"),  bg="#e0ffff").grid(row=0, column=2, padx=3)
        tk.Button(btn_frame, text="Pull",         width=12, command=lambda: self._run_simple("pull"),   bg="#fffacd").grid(row=0, column=3, padx=3)
        tk.Button(btn_frame, text="Push",         width=12, command=self._push_only,                 bg="#98fb98").grid(row=0, column=4, padx=3)

        tk.Label(btn_frame, text="Commit Msg:", bg="#f0f0f0").grid(row=0, column=5, padx=(20,3))
        self.commit_entry = tk.Entry(btn_frame, width=30)
        self.commit_entry.grid(row=0, column=6, padx=3)
        tk.Button(btn_frame, text="Commit", width=12, command=self._add_and_commit, bg="#ffb347").grid(row=0, column=7, padx=3)

        self.output = tk.Text(self, height=15, state="disabled")
        self.output.grid(row=3, column=0, columnspan=3, sticky="nsew", padx=5, pady=5)
        self.grid_rowconfigure(3, weight=1)
        scrollbar = tk.Scrollbar(self, command=self.output.yview)
        scrollbar.grid(row=3, column=3, sticky='ns')
        self.output['yscrollcommand'] = scrollbar.set

        self.output.tag_configure('success', foreground='green')
        self.output.tag_configure('error',   foreground='red')
        self.output.tag_configure('info',    foreground='blue')

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
            entry.insert(tk.INSERT, txt)
        except tk.TclError:
            pass

    def browse_folder(self):
        d = filedialog.askdirectory()
        if d:
            self.path_entry.delete(0, tk.END)
            self.path_entry.insert(0, d)

    def _clear_log(self):
        self.output.configure(state="normal")
        self.output.delete("1.0", "end")
        self.output.configure(state="disabled")

    def _append_log(self, msg, tag='info'):
        self.output.configure(state="normal")
        self.output.insert("end", msg + "\n", tag)
        self.output.see("end")
        self.output.configure(state="disabled")

    def _run_git(self, args, cwd=None):
        cwd = cwd or self.path_entry.get().strip()
        try:
            proc = subprocess.run(
                ["git"] + args,
                cwd=cwd,
                check=True,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                text=True
            )
            return True, proc.stdout.strip()
        except subprocess.CalledProcessError as e:
            return False, (e.stderr.strip() or e.stdout.strip())

    def _run_simple(self, subcmd):
        path = self.path_entry.get().strip()
        if not os.path.isdir(path):
            messagebox.showerror("Error", f"Directory not found:\n{path}")
            return
        self._clear_log()
        ok, out = self._run_git([subcmd])
        tag = 'success' if ok else 'error'
        self._append_log(f"git {subcmd}: {out}", tag)

    def _add_and_commit(self):
        path = self.path_entry.get().strip()
        if not os.path.isdir(path):
            messagebox.showerror("Error", f"Directory not found:\n{path}")
            return
        msg = self.commit_entry.get().strip()
        if not msg:
            messagebox.showwarning("Warning", "Enter commit message first.")
            return
        #add
        ok_add, out_add = self._run_git(["add", "."])
        tag_add = 'success' if ok_add else 'error'
        self._append_log(f"git add .: {out_add}", tag_add)
        if not ok_add:
            return

        self._clear_log()
        #commit
        ok, out = self._run_git(["commit", "-m", msg])
        tag = 'success' if ok else 'error'
        self._append_log(f"git commit: {out}", tag)

    def _push_only(self):
        path = self.path_entry.get().strip()
        url  = self.url_entry.get().strip()
        if not os.path.isdir(path):
            messagebox.showerror("Error", f"Directory not found:\n{path}")
            return
        self._clear_log()
        if not url:
            url = simpledialog.askstring("Repository URL", "Enter remote repository URL:")
            if not url:
                return
            self.url_entry.insert(0, url)
        ok, _ = self._run_git(["remote", "get-url", "origin"])
        if not ok:
            ok2, out2 = self._run_git(["remote", "add", "origin", url])
            tag2 = 'success' if ok2 else 'error'
            self._append_log(f"git remote add origin: {out2}", tag2)
        ok3, out3 = self._run_git(["push", "origin", "main"])
        tag3 = 'success' if ok3 else 'error'
        self._append_log(f"git push: {out3}", tag3)

    def clone_repo(self):
        url = self.url_entry.get().strip()
        if not url:
            url = simpledialog.askstring("Repository URL", "Enter repo URL to clone:")
            if not url:
                return
            self.url_entry.insert(0, url)
        parent = filedialog.askdirectory(title="Select parent folder for clone")
        if not parent:
            return
        self._clear_log()
        ok, out = self._run_git(["clone", url], cwd=parent)
        tag = 'success' if ok else 'error'
        self._append_log(f"git clone: {out}", tag)
        if ok:
            name = os.path.splitext(os.path.basename(url))[0]
            clone_path = os.path.join(parent, name)
            self.path_entry.delete(0, tk.END)
            self.path_entry.insert(0, clone_path)
            self._append_log(f"✅ Cloned into: {clone_path}", 'success')

if __name__ == "__main__":
    app = GitGUIApp()
    app.mainloop()
