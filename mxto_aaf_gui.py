#!/usr/bin/env python3
"""
MXToAAF GUI - Graphical User Interface for Music to AAF Conversion

A graphical interface for converting music files (mp3, m4a, aif, wav) to AAFs for Avid import.
Provides file/folder browsing, embed option, CSV export, and real-time processing feedback.

Author: Jason Brodkey
Version: 0.9.0
Date: 2025-11-30
"""

import tkinter as tk
from tkinter import ttk, filedialog, messagebox
from tkinter.scrolledtext import ScrolledText
import os
import sys
import threading
import subprocess
import webbrowser
import importlib.metadata as importlib_metadata


def resource_path(relative_path: str) -> str:
    """Return absolute path to resource, works for dev and PyInstaller."""
    try:
        base_path = sys._MEIPASS  # type: ignore[attr-defined]
    except Exception:
        base_path = os.path.abspath(".")
    return os.path.join(base_path, relative_path)


def get_app_version() -> str:
    # Prefer the packaged version string; fall back to metadata if installed as a wheel
    try:
        return __version__
    except Exception:
        pass
    try:
        return importlib_metadata.version("mxtoaaf")
    except Exception:
        return "unknown"

from mxto_aaf.__version__ import __version__
from mxto_aaf.batch import process_directory
from mxto_aaf.metadata import extract_music_metadata
from mxto_aaf.aaf import create_music_aaf
from mxto_aaf.utils import convert_to_wav


def launch_gui():
    root = tk.Tk()
    root.title("MXToAAF - Music to AAF Converter")
    root.geometry("680x520")
    # Use native theme only; do not paint custom colors so Aqua/Vista control appearance
    # This mirrors WAVsToALE behavior exactly.
    try:
        style = ttk.Style()
        if sys.platform == 'darwin' and 'aqua' in style.theme_names():
            style.theme_use('aqua')
    except Exception:
        pass

    # Variables
    input_var = tk.StringVar()
    out_var = tk.StringVar()
    fps_var = tk.StringVar(value="24")
    embed_var = tk.BooleanVar(value=True)
    csv_var = tk.BooleanVar(value=False)
    meta_csv_var = tk.BooleanVar(value=False)
    last_outputs = {'paths': [], 'last_output_path': None}
    progress_var = tk.StringVar(value="")
    status_var = tk.StringVar(value="")
    cancel_event = threading.Event()

    def log(msg):
        log_text.configure(state='normal')
        log_text.insert('end', str(msg) + "\n")
        log_text.see('end')
        log_text.configure(state='disabled')
        # Track output folder for Open button and parse progress
        try:
            s = str(msg)
            if "Output:" in s:
                path = s.split("Output:", 1)[1].strip()
                if path and os.path.isdir(path):
                    last_outputs['paths'].append(path)
                    try:
                        if not open_btn.winfo_ismapped():
                            open_btn.pack(side='left', padx=(8, 0))
                        open_btn.configure(state='normal')
                    except Exception:
                        pass
            # Parse progress "X/Y" from batch processing output
            if "/" in s and "%" in s:
                # Extract X/Y from progress bar line like "1/18 (5.6%)"
                parts = s.split()
                for part in parts:
                    if "/" in part and part[0].isdigit():
                        progress_var.set(f"Processing {part}")
                        break
        except Exception:
            pass

    def browse_input_file():
        path = filedialog.askopenfilename(
            title="Select music file",
            filetypes=[("Audio Files", "*.mp3 *.m4a *.wav *.aif *.aiff"), ("All Files", "*.*")]
        )
        if path:
            input_var.set(path)

    def browse_input_dir():
        path = filedialog.askdirectory(title="Select music directory")
        if path:
            input_var.set(path)

    def browse_out():
        path = filedialog.askdirectory(title="Select output folder")
        if path:
            out_var.set(path)

    def run_clicked():
        inp = input_var.get().strip()
        outp = out_var.get().strip()
        embed = embed_var.get()
        export_csv = csv_var.get()
        export_meta_csv = meta_csv_var.get()
        
        # Parse FPS
        try:
            fps = float(fps_var.get().strip() or "24")
            if fps <= 0:
                raise ValueError
        except Exception:
            messagebox.showwarning("Invalid FPS", "FPS must be a positive number (e.g. 24 or 23.976). Using 24.")
            fps = 24.0

        if not inp:
            messagebox.showerror("Missing input", "Please select a music file or directory.")
            return
        
        # Verify source still exists
        if not os.path.exists(inp):
            messagebox.showerror("Source not found", "The selected source is not available")
            return
        
        # Track if output was manually specified or left blank for default
        output_was_blank = not outp
        
        # Always ensure output path uses AAFs folder structure
        if not outp:
            # Default behavior: AAFs folder at parent level with directory name preserved
            if os.path.isfile(inp):
                # For files: AAFs next to the file
                outp = os.path.join(os.path.dirname(inp), "AAFs")
            else:
                # For directories: AAFs as sibling, with selected dir name included in output path
                # This preserves the directory structure under AAFs
                # e.g., select "AC_DC/Back In Black" → output to "AAFs/AC_DC/Back In Black"
                dir_path = inp.rstrip('/\\')
                dir_name = os.path.basename(dir_path)
                parent = os.path.dirname(dir_path)
                parent_name = os.path.basename(parent) if parent else ""
                
                # Include parent directory name if it exists (preserve one level of structure)
                if parent_name:
                    outp = os.path.join(os.path.dirname(parent), "AAFs", parent_name, dir_name)
                else:
                    outp = os.path.join(parent, "AAFs", dir_name)
        else:
            # If manually set, force it to end with AAFs folder
            if not outp.rstrip('/\\').endswith("AAFs"):
                outp = os.path.join(outp, "AAFs")
            else:
                # If user already specified AAFs, use as-is
                outp = outp.rstrip('/\\')

        cancel_event.clear()
        run_btn.configure(state='disabled')
        cancel_btn.configure(state='normal')

        def worker():
            log("Starting conversion…")
            log(f"Frame rate: {fps} fps")
            log(f"Embed audio: {'Yes' if embed else 'No'}")
            log(f"Input: {inp}")
            # Only show output in log, don't populate the field if it was left blank
            log(f"Output: {outp}")
            # Store actual output path for Open button
            last_outputs['last_output_path'] = outp
            # Animate dots to show activity before first progress line
            import time
            log_text.configure(state='normal')
            log_text.insert('end', 'Processing')
            log_text.see('end')
            log_text.configure(state='disabled')
            for i in range(1, 11):
                log_text.configure(state='normal')
                log_text.insert('end', '.')
                log_text.see('end')
                log_text.configure(state='disabled')
                time.sleep(0.175)  # 175ms per dot = 1.75s total
            log("")  # newline after dots
            last_outputs['paths'].clear()
            try:
                if os.path.isdir(inp):
                    summary = process_directory(
                        inp,
                        outp,
                        recursive=True,
                        embed=embed,
                        skip_existing=True,
                        export_csv=os.path.join(outp, "results.csv") if export_csv else None,
                        export_metadata_csv=os.path.join(outp, "metadata.csv") if export_meta_csv else None,
                        fps=fps,
                    )
                    log(f"✓ Success: {summary['success_count']}")
                    log(f"✗ Failed: {summary['failed_count']}")
                    log(f"⊘ Skipped: {summary['skipped_count']}")
                    log(f"Duration: {summary['total_duration']:.1f}s")
                    log(f"Output: {outp}")
                else:
                    # Single-file processing
                    os.makedirs(outp, exist_ok=True)
                    base = os.path.splitext(os.path.basename(inp))[0]
                    dest = os.path.join(outp, base + ".aaf")
                    import time as _time
                    t0 = _time.time()
                    md = extract_music_metadata(str(inp))
                    created = None
                    try:
                        if embed and not inp.lower().endswith('.wav'):
                            tmp = os.path.join(outp, base + ".tmp.wav")
                            convert_to_wav(str(inp), tmp)
                            created = create_music_aaf(tmp, md, dest, embed=True, tag_map=None, fps=fps)
                            try:
                                os.remove(tmp)
                            except Exception:
                                pass
                        else:
                            created = create_music_aaf(str(inp), md, dest, embed=embed, tag_map=None, fps=fps)
                        dur = _time.time() - t0
                        log(f"✓ Created: {created}")
                        log(f"Duration: {dur:.1f}s")
                        # Optional CSV outputs for single-file
                        if export_csv:
                            try:
                                csv_path = os.path.join(outp, "results.csv")
                                import csv as _csv
                                write_header = not os.path.exists(csv_path)
                                with open(csv_path, "a", newline="", encoding="utf-8") as f:
                                    w = _csv.writer(f)
                                    if write_header:
                                        w.writerow(["input", "output", "status", "error", "duration_s"])
                                    w.writerow([inp, created, "success", "", f"{dur:.3f}"])
                            except Exception as _e:
                                log(f"Warning: unable to write CSV report: {_e}")
                        if export_meta_csv:
                            try:
                                mpath = os.path.join(outp, "metadata.csv")
                                import csv as _csv
                                write_header = not os.path.exists(mpath)
                                with open(mpath, "a", newline="", encoding="utf-8") as f:
                                    w = _csv.writer(f)
                                    if write_header:
                                        w.writerow([
                                            "input","output","status","error","duration_s",
                                            "Track Name","Track","Total Tracks","Genre","Artist","Album Artist","Talent","Composer","Source","Album","Catalog #","Description","Duration"
                                        ])
                                    w.writerow([
                                        inp, created, "success", "", f"{dur:.3f}",
                                        md.track_name, md.track, md.total_tracks, md.genre, md.artist, md.album_artist,
                                        md.talent, md.composer, md.source, md.album, md.catalog_number, md.description, md.duration
                                    ])
                            except Exception as _e:
                                log(f"Warning: unable to write metadata CSV: {_e}")
                        # Expose output folder button
                        try:
                            open_btn.pack(side='left', padx=(8, 0))
                            open_btn.configure(state='normal')
                        except Exception:
                            pass
                    except Exception as e:
                        # Re-raise single-file errors to outer handler
                        raise e

                try:
                    open_btn.pack(side='left', padx=(8, 0))
                    open_btn.configure(state='normal')
                except Exception:
                    pass
                messagebox.showinfo("Done", "AAF creation completed.")
            except Exception as e:
                error_str = str(e)
                # Check for common ffmpeg/source not found errors
                if "returned non-zero exit status" in error_str or "No such file" in error_str or not os.path.exists(inp):
                    messagebox.showerror("Source not found", f"The source file or directory is no longer available or cannot be accessed:\n{inp}")
                elif error_str.strip():
                    log(f"Error: {e}")
                    messagebox.showerror("Error", f"AAF creation failed: {e}")
                try:
                    progress_var.set("")
                except Exception:
                    pass
            finally:
                run_btn.configure(state='normal')
                cancel_btn.configure(state='disabled')

        threading.Thread(target=worker, daemon=True).start()

    def cancel_clicked():
        cancel_event.set()
        log("Cancellation requested…")

    def clear_log():
        log_text.configure(state='normal')
        log_text.delete('1.0', 'end')
        log_text.configure(state='disabled')
        # Only clear output field (keep input field)
        out_var.set('')
        progress_var.set('')
        try:
            open_btn.pack_forget()
            open_btn.configure(state='disabled')
        except Exception:
            pass

    def open_output_location():
        # Use the last output path from processing, not the field value
        outp = last_outputs.get('last_output_path') or out_var.get().strip()
        if outp and os.path.isdir(outp):
            try:
                if sys.platform == 'darwin':
                    subprocess.run(['open', outp], check=False)
                elif sys.platform == 'win32':
                    os.startfile(outp)
                else:
                    subprocess.run(['xdg-open', outp], check=False)
            except Exception:
                messagebox.showwarning("Open Location", "Could not open the AAF location.")

    def load_text_file(path_candidates):
        """Return text content from the first existing path in candidates list."""
        for candidate in path_candidates:
            try:
                real = resource_path(candidate)
                if os.path.exists(real):
                    with open(real, "r", encoding="utf-8", errors="ignore") as f:
                        return f.read()
            except Exception:
                continue
        return "Content not available."

    def show_about():
        about = tk.Toplevel(root)
        about.title("About MXToAAF")
        about.geometry("520x420")
        about.transient(root)
        about.grab_set()

        app_version = get_app_version()

        ttk.Label(about, text=f"MXToAAF v{app_version}", font=(None, 12, "bold")).pack(pady=(10, 2))
        ttk.Label(about, text="Music to AAF Converter", font=(None, 10)).pack()
        ttk.Label(about, text="© Jason Brodkey", font=(None, 10)).pack(pady=(0, 10))

        ttk.Button(about, text="Close", command=about.destroy).pack(pady=(8, 12))

    def show_license():
        lic_win = tk.Toplevel(root)
        lic_win.title("License Information")
        lic_win.geometry("720x560")
        lic_win.transient(root)
        lic_win.grab_set()

        license_text = load_text_file(["LICENSES.txt", "LICENSE.txt", "LICENSE"])

        ttk.Label(lic_win, text="License Information", font=(None, 12, "bold")).pack(pady=(10, 4))
        box = ScrolledText(lic_win, height=28, wrap='word')
        box.pack(fill='both', expand=True, padx=12, pady=(2, 12))
        box.insert('1.0', license_text)
        box.configure(state='disabled')
        ttk.Button(lic_win, text="Close", command=lic_win.destroy).pack(pady=(0, 10))

    def show_help():
        help_win = tk.Toplevel(root)
        help_win.title("MXToAAF Help")
        help_win.geometry("780x600")
        help_win.transient(root)
        help_win.grab_set()

        readme_file = "docs/README_windows.md" if sys.platform.startswith("win") else "docs/README_mac.md"
        help_text = load_text_file([readme_file, "README.md"])

        ttk.Label(help_win, text="MXToAAF Help", font=(None, 12, "bold")).pack(pady=(10, 4))
        box = ScrolledText(help_win, height=34, wrap='word')
        box.pack(fill='both', expand=True, padx=12, pady=(2, 12))
        box.insert('1.0', help_text)
        box.configure(state='disabled')
        ttk.Button(help_win, text="Close", command=help_win.destroy).pack(pady=(0, 10))

    # Layout
    frm = ttk.Frame(root, padding=12)
    frm.pack(fill='both', expand=True)

    # Input
    ttk.Label(frm, text="Music file or directory").grid(row=0, column=0, sticky='w')
    input_entry = ttk.Entry(frm, textvariable=input_var, width=60)
    input_entry.grid(row=1, column=0, columnspan=2, sticky='we', pady=(1, 0))
    # Place the buttons in a frame in the same row as the entry
    input_btns = ttk.Frame(frm)
    input_btns.grid(row=1, column=2, sticky='w', pady=0)
    ttk.Button(input_btns, text="File…", command=browse_input_file).grid(row=0, column=0, padx=(0, 4), pady=0)
    ttk.Button(input_btns, text="Folder…", command=browse_input_dir).grid(row=0, column=1, pady=0)

    # Output
    ttk.Label(frm, text="Output Folder for AAFs").grid(row=2, column=0, sticky='w', pady=(6, 0))
    out_entry = ttk.Entry(frm, textvariable=out_var, width=60)
    out_entry.grid(row=3, column=0, columnspan=2, sticky='we', pady=(1, 0))
    ttk.Button(frm, text="Browse…", command=browse_out).grid(row=3, column=2, sticky='w', pady=0)

    # FPS
    fps_row = ttk.Frame(frm)
    fps_row.grid(row=4, column=0, columnspan=3, sticky='w', pady=(6, 8))
    ttk.Label(fps_row, text="FPS:").pack(side='left')
    ttk.Entry(fps_row, textvariable=fps_var, width=8).pack(side='left', padx=(4, 0))
    ttk.Label(fps_row, text="(default 24)").pack(side='left', padx=(6, 0))

    # Advanced options toggle (collapsed by default)
    adv_frame = ttk.Frame(frm)
    adv_frame.grid(row=5, column=0, columnspan=3, sticky='w', pady=(0, 4))
    adv_expanded = tk.BooleanVar(value=False)

    def toggle_advanced():
        if adv_expanded.get():
            adv_container.grid_remove()
            adv_expanded.set(False)
            adv_btn.configure(text="Advanced ▼")
        else:
            adv_container.grid()
            adv_expanded.set(True)
            adv_btn.configure(text="Advanced ▲")

    adv_btn = ttk.Button(adv_frame, text="Advanced ▼", command=toggle_advanced, width=12)
    adv_btn.pack(side='left')

    # Advanced container with all 3 checkboxes
    adv_container = ttk.Frame(frm)
    adv_container.grid(row=6, column=0, columnspan=3, sticky='w', pady=(0, 8))
    ttk.Checkbutton(adv_container, text="Embed audio in AAF (recommended)", variable=embed_var).pack(side='left')
    ttk.Checkbutton(adv_container, text="Export results CSV", variable=csv_var).pack(side='left', padx=(12, 0))
    ttk.Checkbutton(adv_container, text="Export metadata CSV", variable=meta_csv_var).pack(side='left', padx=(12, 0))
    adv_container.grid_remove()

    # Action buttons
    buttons_row = ttk.Frame(frm)
    buttons_row.grid(row=7, column=0, columnspan=3, sticky='ew', pady=(0, 8))
    run_btn = ttk.Button(buttons_row, text="Run", command=run_clicked)
    run_btn.pack(side='left')
    cancel_btn = ttk.Button(buttons_row, text="Cancel", command=cancel_clicked, state='disabled')
    cancel_btn.pack(side='left', padx=(8, 0))
    open_btn = ttk.Button(buttons_row, text="Open AAF Location", command=open_output_location, state='disabled')
    open_btn.pack(side='left', padx=(8, 0))
    open_btn.pack_forget()  # Hide initially

    # Log area with clear button
    log_header = ttk.Frame(frm)
    log_header.grid(row=8, column=0, columnspan=3, sticky='ew', pady=(0, 2))
    ttk.Label(log_header, text="Output Log").pack(side='left')
    progress_lbl = ttk.Label(log_header, textvariable=progress_var, foreground="#555555")
    progress_lbl.pack(side='left', padx=(12, 0))
    ttk.Button(log_header, text="Clear", command=clear_log, width=8).pack(side='right')

    log_text = ScrolledText(frm, height=16, state='disabled')
    log_text.grid(row=9, column=0, columnspan=3, sticky='nsew')
    frm.rowconfigure(9, weight=1)

    # Copyright, website, and version labels below log
    copyright_font = (None, 10)
    footer = ttk.Frame(frm)
    footer.grid(row=10, column=0, columnspan=3, sticky='ew', pady=(4, 0))

    def open_website(event=None):
        webbrowser.open_new_tab('https://www.editcandy.com')

    left_lbl = ttk.Label(footer, text="© Jason Brodkey", font=copyright_font, anchor='w', justify='left')
    left_lbl.grid(row=0, column=0, sticky='w')

    center_lbl = ttk.Label(footer, text="www.editcandy.com", font=copyright_font, foreground="#4ea3ff", cursor="hand2")
    center_lbl.grid(row=0, column=1)
    center_lbl.bind("<Button-1>", open_website)

    app_version = get_app_version()
    right_lbl = ttk.Label(footer, text=f"v{app_version}", font=copyright_font, anchor='e', justify='right')
    right_lbl.grid(row=0, column=2, sticky='e')

    footer.columnconfigure(0, weight=1)
    footer.columnconfigure(1, weight=1)
    footer.columnconfigure(2, weight=1)

    frm.columnconfigure(0, weight=1)

    # Menubar with Help/About/License
    menubar = tk.Menu(root)
    help_menu = tk.Menu(menubar, tearoff=0)
    help_menu.add_command(label="MXToAAF Help", command=show_help)
    help_menu.add_command(label="License Info", command=show_license)
    help_menu.add_separator()
    help_menu.add_command(label="About MXToAAF", command=show_about)
    menubar.add_cascade(label="Help", menu=help_menu)
    root.config(menu=menubar)

    # On macOS, wire the standard About item to our dialog
    try:
        if sys.platform == 'darwin':
            root.createcommand('tkAboutDialog', show_about)
    except Exception:
        pass

    # Redirect stdout to log with smart handling of \r (carriage return) for progress bars
    class StdoutRedirector:
        def __init__(self):
            self.last_was_carriage_return = False
            
        def write(self, message):
            if not message:
                return
            
            # Handle carriage return (\r) - used by progress bars to update same line
            if '\r' in message:
                # Split by \r and process each part
                parts = message.split('\r')
                for i, part in enumerate(parts):
                    if not part.strip():
                        continue
                    
                    if i > 0 or self.last_was_carriage_return:
                        # Replace last line in log
                        log_text.configure(state='normal')
                        log_text.delete("end-2l", "end-1l")
                        log_text.configure(state='disabled')
                    
                    if part.strip():
                        log(part.rstrip('\n'))
                
                self.last_was_carriage_return = True
            else:
                # Normal output
                if message.strip():
                    log(message.rstrip('\n'))
                self.last_was_carriage_return = False
                
        def flush(self):
            pass

    sys.stdout = StdoutRedirector()

    root.mainloop()


def main():
    launch_gui()


if __name__ == "__main__":
    main()
