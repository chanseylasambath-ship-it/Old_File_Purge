# Press Shift+F10 to execute it or replace it with your code.
# Press Double Shift to search everywhere for classes, files, tool windows, actions, and settings.
# This app is deleted files permanently instead of move files.

import tkinter as tk
from tkinter import ttk, filedialog, messagebox
from pathlib import Path
from datetime import datetime, timedelta
import os


class FilePurgeApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Old File Purge")
        self.root.geometry("800x550")
        self.root.resizable(True, True)

        self.folder_var = tk.StringVar()
        self.days_var = tk.StringVar(value="90")

        self.create_ui()

    def create_ui(self):
        # Main frame
        main = ttk.Frame(self.root, padding=15)
        main.pack(fill="both", expand=True)

        # Folder selection
        ttk.Label(main, text="Process Folder:").grid(
            row=0, column=0, sticky="w", pady=5
        )

        ttk.Entry(
            main,
            textvariable=self.folder_var,
            width=70
        ).grid(row=0, column=1, sticky="ew", padx=5)

        ttk.Button(
            main,
            text="Browse...",
            command=self.browse_folder
        ).grid(row=0, column=2, padx=5)

        # Days
        ttk.Label(main, text="Delete files older than:").grid(
            row=1, column=0, sticky="w", pady=10
        )

        ttk.Entry(
            main,
            textvariable=self.days_var,
            width=10
        ).grid(row=1, column=1, sticky="w", padx=5)

        ttk.Label(main, text="days").grid(
            row=1, column=1, sticky="w", padx=85
        )

        # Buttons
        button_frame = ttk.Frame(main)
        button_frame.grid(
            row=2,
            column=0,
            columnspan=3,
            sticky="w",
            pady=10
        )

        ttk.Button(
            button_frame,
            text="Scan Files",
            command=self.scan_files
        ).pack(side="left", padx=5)

        ttk.Button(
            button_frame,
            text="Dry Run",
            command=self.dry_run
        ).pack(side="left", padx=5)

        ttk.Button(
            button_frame,
            text="Purge Old Files",
            command=self.purge_files
        ).pack(side="left", padx=5)

        ttk.Button(
            button_frame,
            text="Clear",
            command=self.clear_results
        ).pack(side="left", padx=5)

        # Results
        ttk.Label(main, text="Results:").grid(
            row=3, column=0, sticky="w", pady=(10, 5)
        )

        result_frame = ttk.Frame(main)
        result_frame.grid(
            row=4,
            column=0,
            columnspan=3,
            sticky="nsew"
        )

        self.result_text = tk.Text(
            result_frame,
            wrap="none",
            height=22
        )

        scrollbar_y = ttk.Scrollbar(
            result_frame,
            orient="vertical",
            command=self.result_text.yview
        )

        scrollbar_x = ttk.Scrollbar(
            result_frame,
            orient="horizontal",
            command=self.result_text.xview
        )

        self.result_text.configure(
            yscrollcommand=scrollbar_y.set,
            xscrollcommand=scrollbar_x.set
        )

        self.result_text.grid(
            row=0,
            column=0,
            sticky="nsew"
        )

        scrollbar_y.grid(
            row=0,
            column=1,
            sticky="ns"
        )

        scrollbar_x.grid(
            row=1,
            column=0,
            sticky="ew"
        )

        result_frame.rowconfigure(0, weight=1)
        result_frame.columnconfigure(0, weight=1)

        # Status
        self.status_var = tk.StringVar(value="Ready")

        ttk.Label(
            main,
            textvariable=self.status_var
        ).grid(
            row=5,
            column=0,
            columnspan=3,
            sticky="w",
            pady=10
        )

        # Resize behavior
        main.columnconfigure(1, weight=1)
        main.rowconfigure(4, weight=1)

    def browse_folder(self):
        folder = filedialog.askdirectory(
            title="Select Process Folder"
        )

        if folder:
            self.folder_var.set(folder)

    def get_settings(self):
        folder = self.folder_var.get().strip()

        if not folder:
            messagebox.showwarning(
                "Missing Folder",
                "Please select a process folder."
            )
            return None

        path = Path(folder)

        if not path.exists():
            messagebox.showerror(
                "Invalid Folder",
                "The selected folder does not exist."
            )
            return None

        if not path.is_dir():
            messagebox.showerror(
                "Invalid Folder",
                "The selected path is not a folder."
            )
            return None

        try:
            days = int(self.days_var.get())

            if days < 1:
                raise ValueError

        except ValueError:
            messagebox.showerror(
                "Invalid Days",
                "Please enter a positive number of days."
            )
            return None

        return path, days

    def find_old_files(self):
        settings = self.get_settings()

        if not settings:
            return []

        folder, days = settings

        cutoff_date = datetime.now() - timedelta(days=days)

        old_files = []

        try:
            # Only files directly inside the process folder.
            # Change to folder.rglob("*") if you want subfolders included.
            #for file_path in folder.iterdir():
            for file_path in folder.rglob("*"):

                if not file_path.is_file():
                    continue

                try:
                    modified_time = datetime.fromtimestamp(
                        file_path.stat().st_mtime
                    )

                    if modified_time < cutoff_date:
                        old_files.append(
                            (file_path, modified_time)
                        )

                except (PermissionError, OSError) as e:
                    self.result_text.insert(
                        tk.END,
                        f"Could not inspect: {file_path}\n"
                        f"Reason: {e}\n\n"
                    )

        except PermissionError:
            messagebox.showerror(
                "Permission Error",
                "You do not have permission to access this folder."
            )

        return old_files

    def scan_files(self):
        self.clear_results()

        old_files = self.find_old_files()

        if not old_files:
            self.result_text.insert(
                tk.END,
                "No files older than the specified age were found.\n"
            )

            self.status_var.set("No old files found.")
            return

        self.result_text.insert(
            tk.END,
            f"Found {len(old_files)} old file(s):\n\n"
        )

        for file_path, modified_time in old_files:
            self.result_text.insert(
                tk.END,
                f"{file_path}\n"
                f"Last Modified: {modified_time:%Y-%m-%d %H:%M:%S}\n\n"
            )

        self.status_var.set(
            f"{len(old_files)} old file(s) found."
        )

    def dry_run(self):
        self.clear_results()

        old_files = self.find_old_files()

        if not old_files:
            self.result_text.insert(
                tk.END,
                "DRY RUN\n"
                "No files would be deleted.\n"
            )

            self.status_var.set("Dry run complete. Nothing to delete.")
            return

        self.result_text.insert(
            tk.END,
            "========== DRY RUN ==========\n\n"
        )

        total_size = 0

        for file_path, modified_time in old_files:

            try:
                size = file_path.stat().st_size
                total_size += size
            except OSError:
                size = 0

            self.result_text.insert(
                tk.END,
                f"WOULD DELETE: {file_path}\n"
                f"Modified: {modified_time:%Y-%m-%d %H:%M:%S}\n"
                f"Size: {self.format_size(size)}\n\n"
            )

        self.result_text.insert(
            tk.END,
            "=============================\n"
            f"Files: {len(old_files)}\n"
            f"Total Size: {self.format_size(total_size)}\n"
        )

        self.status_var.set(
            f"Dry run complete. {len(old_files)} file(s) would be deleted."
        )

    def purge_files(self):
        settings = self.get_settings()

        if not settings:
            return

        folder, days = settings

        old_files = self.find_old_files()

        if not old_files:
            messagebox.showinfo(
                "Nothing to Delete",
                "No files older than the specified age were found."
            )
            return

        total_size = 0

        for file_path, _ in old_files:
            try:
                total_size += file_path.stat().st_size
            except OSError:
                pass

        # Confirmation
        confirm = messagebox.askyesno(
            "Confirm Purge",
            f"You are about to permanently delete:\n\n"
            f"Files: {len(old_files)}\n"
            f"Total Size: {self.format_size(total_size)}\n"
            f"Older than: {days} days\n\n"
            f"Folder:\n{folder}\n\n"
            f"This action cannot be undone.\n\n"
            f"Continue?"
        )

        if not confirm:
            self.status_var.set("Purge cancelled.")
            return

        deleted = 0
        failed = 0

        self.clear_results()

        self.result_text.insert(
            tk.END,
            "========== PURGE STARTED ==========\n\n"
        )

        for file_path, modified_time in old_files:

            try:
                file_path.unlink()

                deleted += 1

                self.result_text.insert(
                    tk.END,
                    f"DELETED: {file_path}\n"
                )

            except (PermissionError, OSError) as e:

                failed += 1

                self.result_text.insert(
                    tk.END,
                    f"FAILED: {file_path}\n"
                    f"Reason: {e}\n"
                )

        self.result_text.insert(
            tk.END,
            "\n========== PURGE COMPLETE ==========\n"
            f"Deleted: {deleted}\n"
            f"Failed: {failed}\n"
        )

        self.status_var.set(
            f"Purge complete. Deleted {deleted} file(s), "
            f"{failed} failed."
        )

        messagebox.showinfo(
            "Purge Complete",
            f"Purge completed.\n\n"
            f"Deleted: {deleted}\n"
            f"Failed: {failed}"
        )

    def clear_results(self):
        self.result_text.delete(
            "1.0",
            tk.END
        )
        self.status_var.set("Ready")

    @staticmethod
    def format_size(size):
        units = ["B", "KB", "MB", "GB", "TB"]

        for unit in units:
            if size < 1024:
                return f"{size:.2f} {unit}"

            size /= 1024

        return f"{size:.2f} PB"


if __name__ == "__main__":
    root = tk.Tk()

    app = FilePurgeApp(root)

    root.mainloop()

