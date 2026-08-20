import csv
import shutil
import tkinter as tk
from tkinter import ttk, filedialog, messagebox
from pathlib import Path
from datetime import datetime, timedelta

APP_NAME = "Process File Purge"

class ProcessFilePurgeApp:

    def __init__(self, root):
        self.root = root

        self.root.title(APP_NAME)
        self.root.geometry("1000x700")
        self.root.minsize(850, 600)

        self.process_folder = tk.StringVar()
        self.quarantine_folder = tk.StringVar()

        self.retention_days = tk.StringVar(value="90")
        self.quarantine_retention_days = tk.StringVar(value="30")

        self.recursive = tk.BooleanVar(value=True)

        self.create_ui()

    # =========================================================
    # UI
    # =========================================================

    def create_ui(self):

        main = ttk.Frame(self.root, padding=15)
        main.pack(fill=tk.BOTH, expand=True)

        main.columnconfigure(1, weight=1)
        main.rowconfigure(7, weight=1)

        # -----------------------------------------------------
        # Process Folder
        # -----------------------------------------------------

        ttk.Label(
            main,
            text="Process Folder:",
            font=("Segoe UI", 10, "bold")
        ).grid(
            row=0,
            column=0,
            sticky="w",
            pady=8
        )

        ttk.Entry(
            main,
            textvariable=self.process_folder
        ).grid(
            row=0,
            column=1,
            sticky="ew",
            padx=10
        )

        ttk.Button(
            main,
            text="Browse...",
            command=self.select_process_folder
        ).grid(
            row=0,
            column=2
        )

        # -----------------------------------------------------
        # Quarantine Folder
        # -----------------------------------------------------

        ttk.Label(
            main,
            text="Quarantine Folder:",
            font=("Segoe UI", 10, "bold")
        ).grid(
            row=1,
            column=0,
            sticky="w",
            pady=8
        )

        ttk.Entry(
            main,
            textvariable=self.quarantine_folder
        ).grid(
            row=1,
            column=1,
            sticky="ew",
            padx=10
        )

        ttk.Button(
            main,
            text="Browse...",
            command=self.select_quarantine_folder
        ).grid(
            row=1,
            column=2
        )

        # -----------------------------------------------------
        # Retention
        # -----------------------------------------------------

        ttk.Label(
            main,
            text="Process retention:"
        ).grid(
            row=2,
            column=0,
            sticky="w",
            pady=8
        )

        retention_frame = ttk.Frame(main)
        retention_frame.grid(
            row=2,
            column=1,
            sticky="w",
            padx=10
        )

        ttk.Entry(
            retention_frame,
            textvariable=self.retention_days,
            width=10
        ).pack(side=tk.LEFT)

        ttk.Label(
            retention_frame,
            text=" days"
        ).pack(side=tk.LEFT, padx=5)

        # -----------------------------------------------------
        # Quarantine retention
        # -----------------------------------------------------

        ttk.Label(
            main,
            text="Quarantine retention:"
        ).grid(
            row=3,
            column=0,
            sticky="w",
            pady=8
        )

        quarantine_retention_frame = ttk.Frame(main)

        quarantine_retention_frame.grid(
            row=3,
            column=1,
            sticky="w",
            padx=10
        )

        ttk.Entry(
            quarantine_retention_frame,
            textvariable=self.quarantine_retention_days,
            width=10
        ).pack(side=tk.LEFT)

        ttk.Label(
            quarantine_retention_frame,
            text=" days before permanent deletion"
        ).pack(side=tk.LEFT, padx=5)

        # -----------------------------------------------------
        # Recursive
        # -----------------------------------------------------

        ttk.Checkbutton(
            main,
            text="Include files in subfolders",
            variable=self.recursive
        ).grid(
            row=4,
            column=1,
            sticky="w",
            padx=10,
            pady=5
        )

        # -----------------------------------------------------
        # Buttons
        # -----------------------------------------------------

        button_frame = ttk.Frame(main)

        button_frame.grid(
            row=5,
            column=0,
            columnspan=3,
            sticky="w",
            pady=15
        )

        ttk.Button(
            button_frame,
            text="Scan",
            command=self.scan
        ).pack(side=tk.LEFT, padx=5)

        ttk.Button(
            button_frame,
            text="Dry Run",
            command=self.dry_run
        ).pack(side=tk.LEFT, padx=5)

        ttk.Button(
            button_frame,
            text="Quarantine Old Files",
            command=self.quarantine_old_files
        ).pack(side=tk.LEFT, padx=5)

        ttk.Button(
            button_frame,
            text="Purge Quarantine",
            command=self.purge_quarantine
        ).pack(side=tk.LEFT, padx=5)

        ttk.Button(
            button_frame,
            text="Clear",
            command=self.clear_log
        ).pack(side=tk.LEFT, padx=5)

        # -----------------------------------------------------
        # Warning
        # -----------------------------------------------------

        warning = ttk.Label(
            main,
            text=(
                "Safety: Files are moved to Quarantine first. "
                "They are not permanently deleted during normal processing."
            ),
            foreground="darkgreen"
        )

        warning.grid(
            row=6,
            column=0,
            columnspan=3,
            sticky="w",
            pady=5
        )

        # -----------------------------------------------------
        # Log
        # -----------------------------------------------------

        log_frame = ttk.Frame(main)

        log_frame.grid(
            row=7,
            column=0,
            columnspan=3,
            sticky="nsew"
        )

        log_frame.columnconfigure(0, weight=1)
        log_frame.rowconfigure(0, weight=1)

        self.log = tk.Text(
            log_frame,
            wrap=tk.NONE,
            font=("Consolas", 9)
        )

        self.log.grid(
            row=0,
            column=0,
            sticky="nsew"
        )

        vertical_scroll = ttk.Scrollbar(
            log_frame,
            orient=tk.VERTICAL,
            command=self.log.yview
        )

        vertical_scroll.grid(
            row=0,
            column=1,
            sticky="ns"
        )

        horizontal_scroll = ttk.Scrollbar(
            log_frame,
            orient=tk.HORIZONTAL,
            command=self.log.xview
        )

        horizontal_scroll.grid(
            row=1,
            column=0,
            sticky="ew"
        )

        self.log.configure(
            yscrollcommand=vertical_scroll.set,
            xscrollcommand=horizontal_scroll.set
        )

        # -----------------------------------------------------
        # Status
        # -----------------------------------------------------

        self.status = tk.StringVar(
            value="Ready"
        )

        ttk.Label(
            main,
            textvariable=self.status,
            relief=tk.SUNKEN,
            anchor=tk.W
        ).grid(
            row=8,
            column=0,
            columnspan=3,
            sticky="ew",
            pady=(10, 0)
        )

    # =========================================================
    # Folder Selection
    # =========================================================

    def select_process_folder(self):

        folder = filedialog.askdirectory(
            title="Select Process Folder"
        )

        if folder:
            self.process_folder.set(folder)

            # Automatically create a sensible default quarantine
            # folder next to Process.
            process_path = Path(folder)

            default_quarantine = (
                process_path.parent / "Process_Quarantine"
            )

            self.quarantine_folder.set(
                str(default_quarantine)
            )

    def select_quarantine_folder(self):

        folder = filedialog.askdirectory(
            title="Select Quarantine Folder"
        )

        if folder:
            self.quarantine_folder.set(folder)

    # =========================================================
    # Validation
    # =========================================================

    def validate_settings(self):

        process = self.process_folder.get().strip()
        quarantine = self.quarantine_folder.get().strip()

        if not process:

            messagebox.showwarning(
                "Process Folder",
                "Please select the Process folder."
            )

            return None

        if not quarantine:

            messagebox.showwarning(
                "Quarantine Folder",
                "Please select a Quarantine folder."
            )

            return None

        process_path = Path(process)
        quarantine_path = Path(quarantine)

        if not process_path.exists():

            messagebox.showerror(
                "Invalid Process Folder",
                "The Process folder does not exist."
            )

            return None

        if not process_path.is_dir():

            messagebox.showerror(
                "Invalid Process Folder",
                "The Process path is not a folder."
            )

            return None

        try:

            days = int(self.retention_days.get())

            if days <= 0:
                raise ValueError

        except ValueError:

            messagebox.showerror(
                "Invalid Retention",
                "Process retention must be a positive number."
            )

            return None

        try:

            quarantine_days = int(
                self.quarantine_retention_days.get()
            )

            if quarantine_days <= 0:
                raise ValueError

        except ValueError:

            messagebox.showerror(
                "Invalid Quarantine Retention",
                "Quarantine retention must be a positive number."
            )

            return None

        # Make sure quarantine isn't inside Process.
        try:

            process_resolved = process_path.resolve()
            quarantine_resolved = quarantine_path.resolve()

            if (
                quarantine_resolved == process_resolved
                or process_resolved in quarantine_resolved.parents
            ):

                messagebox.showerror(
                    "Invalid Quarantine Folder",
                    "The Quarantine folder cannot be inside "
                    "the Process folder."
                )

                return None

        except OSError as error:

            messagebox.showerror(
                "Path Error",
                str(error)
            )

            return None

        return (
            process_path,
            quarantine_path,
            days,
            quarantine_days
        )

    # =========================================================
    # Find Old Process Files
    # =========================================================

    def find_old_files(self):

        settings = self.validate_settings()

        if not settings:
            return []

        process_folder, _, days, _ = settings

        cutoff = (
            datetime.now()
            - timedelta(days=days)
        )

        old_files = []

        try:

            if self.recursive.get():
                files = process_folder.rglob("*")
            else:
                files = process_folder.iterdir()

            for path in files:

                if not path.is_file():
                    continue

                try:

                    modified = datetime.fromtimestamp(
                        path.stat().st_mtime
                    )

                    if modified < cutoff:

                        old_files.append({
                            "path": path,
                            "modified": modified,
                            "size": path.stat().st_size
                        })

                except (PermissionError, OSError) as error:

                    self.write_log(
                        f"ERROR inspecting: {path}"
                    )

                    self.write_log(
                        f"       {error}"
                    )

        except (PermissionError, OSError) as error:

            messagebox.showerror(
                "Access Error",
                f"Unable to scan Process folder.\n\n{error}"
            )

        return old_files

    # =========================================================
    # Scan
    # =========================================================

    def scan(self):

        self.clear_log()

        self.write_log(
            "========== PROCESS FOLDER SCAN =========="
        )

        self.write_log("")

        files = self.find_old_files()

        if not files:

            self.write_log(
                "No files older than the retention period found."
            )

            self.status.set(
                "No old files found."
            )

            return

        total_size = sum(
            item["size"]
            for item in files
        )

        for item in files:

            self.write_log(
                f"OLD FILE: {item['path']}"
            )

            self.write_log(
                f"Modified: "
                f"{item['modified']:%Y-%m-%d %H:%M:%S}"
            )

            self.write_log(
                f"Size: {self.format_size(item['size'])}"
            )

            self.write_log("")

        self.write_log(
            "------------------------------------------"
        )

        self.write_log(
            f"Files found: {len(files)}"
        )

        self.write_log(
            f"Total size: {self.format_size(total_size)}"
        )

        self.status.set(
            f"{len(files)} old file(s) found."
        )

    # =========================================================
    # Dry Run
    # =========================================================

    def dry_run(self):

        self.clear_log()

        self.write_log(
            "========== DRY RUN =========="
        )

        self.write_log(
            "No files will be moved or deleted."
        )

        self.write_log("")

        files = self.find_old_files()

        if not files:

            self.write_log(
                "No files would be quarantined."
            )

            self.status.set(
                "Dry run complete. Nothing to quarantine."
            )

            return

        total_size = sum(
            item["size"]
            for item in files
        )

        for item in files:

            self.write_log(
                f"WOULD QUARANTINE: {item['path']}"
            )

            self.write_log(
                f"Modified: "
                f"{item['modified']:%Y-%m-%d %H:%M:%S}"
            )

            self.write_log("")

        self.write_log(
            "========== SUMMARY =========="
        )

        self.write_log(
            f"Files: {len(files)}"
        )

        self.write_log(
            f"Total size: {self.format_size(total_size)}"
        )

        self.status.set(
            f"Dry run: {len(files)} file(s) "
            f"would be quarantined."
        )

    # =========================================================
    # Quarantine Old Files
    # =========================================================

    def quarantine_old_files(self):

        settings = self.validate_settings()

        if not settings:
            return

        (
            process_folder,
            quarantine_folder,
            days,
            _
        ) = settings

        files = self.find_old_files()

        if not files:

            messagebox.showinfo(
                "Quarantine",
                f"No files older than {days} days were found."
            )

            return

        total_size = sum(
            item["size"]
            for item in files
        )

        confirmation = messagebox.askyesno(
            "Confirm Quarantine",
            f"The following files will be moved:\n\n"
            f"Files: {len(files)}\n"
            f"Size: {self.format_size(total_size)}\n"
            f"Older than: {days} days\n\n"
            f"FROM:\n{process_folder}\n\n"
            f"TO:\n{quarantine_folder}\n\n"
            f"Files will NOT be permanently deleted.\n\n"
            f"Continue?"
        )

        if not confirmation:

            self.status.set(
                "Quarantine operation cancelled."
            )

            return

        # Create quarantine folder.
        try:

            quarantine_folder.mkdir(
                parents=True,
                exist_ok=True
            )

        except OSError as error:

            messagebox.showerror(
                "Quarantine Error",
                f"Unable to create quarantine folder.\n\n{error}"
            )

            return

        self.clear_log()

        self.write_log(
            "========== QUARANTINE STARTED =========="
        )

        self.write_log(
            f"Source: {process_folder}"
        )

        self.write_log(
            f"Destination: {quarantine_folder}"
        )

        self.write_log("")

        moved = 0
        failed = 0

        audit_records = []

        for item in files:

            source = item["path"]

            try:

                relative_path = source.relative_to(
                    process_folder
                )

                destination = (
                    quarantine_folder
                    / relative_path
                )

                destination.parent.mkdir(
                    parents=True,
                    exist_ok=True
                )

                destination = self.get_unique_path(
                    destination
                )

                shutil.move(
                    str(source),
                    str(destination)
                )

                moved += 1

                self.write_log(
                    f"MOVED: {source}"
                )

                self.write_log(
                    f"   TO: {destination}"
                )

                audit_records.append({
                    "timestamp": datetime.now().isoformat(
                        timespec="seconds"
                    ),
                    "action": "QUARANTINED",
                    "source": str(source),
                    "destination": str(destination),
                    "modified": item["modified"].isoformat(
                        timespec="seconds"
                    ),
                    "size": item["size"],
                    "status": "SUCCESS"
                })

            except (PermissionError, OSError, ValueError) as error:

                failed += 1

                self.write_log(
                    f"FAILED: {source}"
                )

                self.write_log(
                    f"        {error}"
                )

                audit_records.append({
                    "timestamp": datetime.now().isoformat(
                        timespec="seconds"
                    ),
                    "action": "QUARANTINE",
                    "source": str(source),
                    "destination": "",
                    "modified": item["modified"].isoformat(
                        timespec="seconds"
                    ),
                    "size": item["size"],
                    "status": f"FAILED: {error}"
                })

        self.write_audit_log(
            quarantine_folder,
            audit_records
        )

        self.write_log("")

        self.write_log(
            "========== QUARANTINE COMPLETE =========="
        )

        self.write_log(
            f"Moved: {moved}"
        )

        self.write_log(
            f"Failed: {failed}"
        )

        self.status.set(
            f"Quarantine complete: "
            f"{moved} moved, {failed} failed."
        )

        messagebox.showinfo(
            "Quarantine Complete",
            f"Operation completed.\n\n"
            f"Moved to Quarantine: {moved}\n"
            f"Failed: {failed}"
        )

    # =========================================================
    # Permanently Purge Quarantine
    # =========================================================

    def purge_quarantine(self):

        settings = self.validate_settings()

        if not settings:
            return

        (
            _,
            quarantine_folder,
            _,
            quarantine_days
        ) = settings

        if not quarantine_folder.exists():

            messagebox.showinfo(
                "Quarantine",
                "The Quarantine folder does not exist."
            )

            return

        cutoff = (
            datetime.now()
            - timedelta(days=quarantine_days)
        )

        files = []

        try:

            for path in quarantine_folder.rglob("*"):

                if not path.is_file():
                    continue

                try:

                    modified = datetime.fromtimestamp(
                        path.stat().st_mtime
                    )

                    if modified < cutoff:

                        files.append({
                            "path": path,
                            "modified": modified,
                            "size": path.stat().st_size
                        })

                except (PermissionError, OSError) as error:

                    self.write_log(
                        f"ERROR inspecting quarantine file: "
                        f"{path} - {error}"
                    )

        except (PermissionError, OSError) as error:

            messagebox.showerror(
                "Quarantine Error",
                str(error)
            )

            return

        if not files:

            messagebox.showinfo(
                "Quarantine Purge",
                f"No quarantined files are older than "
                f"{quarantine_days} days."
            )

            return

        total_size = sum(
            item["size"]
            for item in files
        )

        confirmation = messagebox.askyesno(
            "PERMANENT DELETE",
            f"WARNING: This permanently deletes files.\n\n"
            f"Files: {len(files)}\n"
            f"Size: {self.format_size(total_size)}\n"
            f"Older than: {quarantine_days} days\n\n"
            f"Quarantine:\n{quarantine_folder}\n\n"
            f"THIS ACTION CANNOT BE UNDONE.\n\n"
            f"Continue?"
        )

        if not confirmation:

            self.status.set(
                "Permanent purge cancelled."
            )

            return

        self.clear_log()

        self.write_log(
            "========== QUARANTINE PURGE =========="
        )

        deleted = 0
        failed = 0

        audit_records = []

        for item in files:

            path = item["path"]

            try:

                path.unlink()

                deleted += 1

                self.write_log(
                    f"PERMANENTLY DELETED: {path}"
                )

                audit_records.append({
                    "timestamp": datetime.now().isoformat(
                        timespec="seconds"
                    ),
                    "action": "PERMANENT_DELETE",
                    "source": str(path),
                    "destination": "",
                    "modified": item["modified"].isoformat(
                        timespec="seconds"
                    ),
                    "size": item["size"],
                    "status": "SUCCESS"
                })

            except (PermissionError, OSError) as error:

                failed += 1

                self.write_log(
                    f"FAILED: {path}"
                )

                self.write_log(
                    f"        {error}"
                )

                audit_records.append({
                    "timestamp": datetime.now().isoformat(
                        timespec="seconds"
                    ),
                    "action": "PERMANENT_DELETE",
                    "source": str(path),
                    "destination": "",
                    "modified": item["modified"].isoformat(
                        timespec="seconds"
                    ),
                    "size": item["size"],
                    "status": f"FAILED: {error}"
                })

        self.write_audit_log(
            quarantine_folder,
            audit_records
        )

        self.write_log("")

        self.write_log(
            "========== PURGE COMPLETE =========="
        )

        self.write_log(
            f"Deleted: {deleted}"
        )

        self.write_log(
            f"Failed: {failed}"
        )

        self.status.set(
            f"Permanent purge complete: "
            f"{deleted} deleted, {failed} failed."
        )

        messagebox.showinfo(
            "Purge Complete",
            f"Permanent purge completed.\n\n"
            f"Deleted: {deleted}\n"
            f"Failed: {failed}"
        )

    # =========================================================
    # Avoid Duplicate Names
    # =========================================================

    @staticmethod
    def get_unique_path(path):

        if not path.exists():
            return path

        timestamp = datetime.now().strftime(
            "%Y%m%d_%H%M%S"
        )

        stem = path.stem
        suffix = path.suffix

        counter = 1

        while True:

            candidate = (
                path.parent
                / f"{stem}_{timestamp}_{counter}{suffix}"
            )

            if not candidate.exists():
                return candidate

            counter += 1

    # =========================================================
    # Audit CSV
    # =========================================================

    def write_audit_log(
        self,
        quarantine_folder,
        records
    ):

        if not records:
            return

        try:

            quarantine_folder.mkdir(
                parents=True,
                exist_ok=True
            )

            log_file = (
                quarantine_folder
                / "purge_audit.csv"
            )

            file_exists = log_file.exists()

            with open(
                log_file,
                "a",
                newline="",
                encoding="utf-8"
            ) as file:

                writer = csv.DictWriter(
                    file,
                    fieldnames=[
                        "timestamp",
                        "action",
                        "source",
                        "destination",
                        "modified",
                        "size",
                        "status"
                    ]
                )

                if not file_exists:
                    writer.writeheader()

                writer.writerows(records)

        except OSError as error:

            self.write_log(
                f"WARNING: Unable to write audit log: {error}"
            )

    # =========================================================
    # Logging
    # =========================================================

    def write_log(self, message):

        timestamp = datetime.now().strftime(
            "%Y-%m-%d %H:%M:%S"
        )

        self.log.insert(
            tk.END,
            f"[{timestamp}] {message}\n"
        )

        self.log.see(tk.END)

        self.root.update_idletasks()

    # =========================================================
    # Clear
    # =========================================================

    def clear_log(self):

        self.log.delete(
            "1.0",
            tk.END
        )

        self.status.set(
            "Ready"
        )

    # =========================================================
    # File Size
    # =========================================================

    @staticmethod
    def format_size(size):

        units = [
            "B",
            "KB",
            "MB",
            "GB",
            "TB"
        ]

        for unit in units:

            if size < 1024:

                return f"{size:.2f} {unit}"

            size /= 1024

        return f"{size:.2f} PB"


# =============================================================
# Application Entry Point
# =============================================================

if __name__ == "__main__":

    root = tk.Tk()

    app = ProcessFilePurgeApp(root)

    root.mainloop()
