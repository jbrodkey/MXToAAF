# MXToAAF GUI Improvements

This document describes three key improvements made to the MXToAAF GUI to enhance user experience during batch processing and improve error handling.

## 1. Progress Display ("Processing X of Y")

### Objective
Display real-time processing progress (e.g., "Processing 3/18") next to the "Output Log" header so users can see how many files have been processed without scrolling through the log. Progress updates should appear in the log as processing occurs, not after completion.

### Implementation

#### A. Add Progress Tracking Variable
In the GUI initialization, add a `StringVar` to track progress state:

```python
progress_var = tk.StringVar(value="")
```

This variable updates dynamically as batch processing progresses.

#### B. Smart Stdout Redirection with Carriage Return Handling
The batch processor outputs progress to stdout using `\r` (carriage return) to overwrite the progress line. The GUI captures this in real-time with a custom `StdoutRedirector` that intelligently handles `\r`:

```python
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
```

This redirector:
- Captures all stdout output in real-time (not buffered)
- Intelligently handles `\r` by replacing the last logged line instead of appending
- Allows progress bar animations to update in place within the log
- Forwards all output to the `log()` function for parsing and display

#### C. Parse Progress from Log Output
The `log()` function intercepts progress lines from batch processing and extracts the "X/Y" count:

```python
def log(msg):
    # ... existing log display code ...
    
    # Parse progress "X/Y" from batch processing output
    if "/" in s and "%" in s:
        # Extract X/Y from progress bar line like "1/18 (5.6%)"
        parts = s.split()
        for part in parts:
            if "/" in part and part[0].isdigit():
                progress_var.set(f"Processing {part}")
                break
```

When the batch processor outputs lines like `[████░░░░] 3/18 (16.7%)`, this code:
1. Detects the "/" character and "%" together
2. Splits the line into words
3. Finds the first word containing "/" that starts with a digit
4. Updates `progress_var` with `"Processing 3/18"`

#### D. Display Progress Label in Log Header
Add a progress label to the log area header, positioned next to "Output Log":

```python
log_header = ttk.Frame(frm)
log_header.grid(row=8, column=0, columnspan=3, sticky='ew', pady=(0, 2))
ttk.Label(log_header, text="Output Log").pack(side='left')
progress_lbl = ttk.Label(log_header, textvariable=progress_var, foreground="#555555")
progress_lbl.pack(side='left', padx=(12, 0))
ttk.Button(log_header, text="Clear", command=clear_log, width=8).pack(side='right')
```

The progress label:
- Binds to `progress_var` for automatic updates
- Uses a gray foreground (`#555555`) for subtle appearance
- Updates in real-time as processing proceeds

#### E. Clear Progress on Clear Button
When the user clicks "Clear", reset the progress display:

```python
def clear_log():
    log_text.configure(state='normal')
    log_text.delete('1.0', 'end')
    log_text.configure(state='disabled')
    out_var.set('')
    progress_var.set('')  # Reset progress display
    # ... hide button, etc ...
```

### Result
During batch processing, the log header displays:
```
Output Log Processing 1/18     [Clear]
Output Log Processing 5/18     [Clear]
Output Log Processing 18/18    [Clear]
```

---

## 2. Source Not Found Error Handling

### Objective
If the user changes the input path before clicking "Run", or the source is deleted/moved, display a user-friendly error dialog instead of a cryptic ffmpeg error.

### Implementation

#### A. Pre-Run Source Verification
Before starting processing, verify that the selected source still exists:

```python
def run_clicked():
    inp = input_var.get().strip()
    # ... other validation ...
    
    # Verify source still exists
    if not os.path.exists(inp):
        messagebox.showerror("Source not found", "The selected source is not available")
        return
```

This catches the most common case: user selects a path, then deletes/moves it before hitting Run. The error message is simplified to avoid showing potentially long file paths.

#### B. Catch ffmpeg Conversion Errors
When converting audio files or processing, ffmpeg errors often indicate a missing source. Catch these and show a friendly dialog:

```python
except Exception as e:
    error_str = str(e)
    # Check for common ffmpeg/source not found errors
    if "returned non-zero exit status" in error_str or "No such file" in error_str or not os.path.exists(inp):
        messagebox.showerror("Source not found", 
            f"The source file or directory is no longer available or cannot be accessed:\n{inp}")
    elif error_str.strip():
        log(f"Error: {e}")
        messagebox.showerror("Error", f"AAF creation failed: {e}")
```

This detection handles:
- **ffmpeg exit status errors** (e.g., `returned non-zero exit status 254`): Usually indicates the source ffmpeg tried to access no longer exists
- **"No such file" errors**: Direct file-not-found message from ffmpeg or Python
- **Source path validation failure**: Re-check if input path still exists during processing

#### C. User-Friendly Error Message
Instead of showing:
```
Error: Command '['/opt/homebrew/bin/ffmpeg', '-y', '-v', 'error', '-i', '/path/to/missing/file/', ...] returned non-zero exit status 254
```

The user now sees:
```
Source not found

The source file or directory is no longer available or cannot be accessed:
/path/to/missing/file/

[OK]
```

### Result
Users get immediate, clear feedback that their source is missing rather than a technical ffmpeg error.

---

## 3. Forced Output into AAFs Directory

### Objective
Ensure all AAF output goes into an `AAFs` root directory, regardless of whether the output path is manually set or left as default. For directory processing, preserve the source directory structure as subdirectories within `AAFs`.

### Implementation

#### A. Normalize Output Path to Include AAFs with Directory Structure
Modify the output path logic to always use `/AAFs` and preserve parent directory structure:

```python
# Always ensure output path uses AAFs folder structure
if not outp:
    # Default behavior: AAFs folder at parent level with directory structure preserved
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
```

This logic:
1. **If output is blank (default)**: Create `AAFs` folder one level up from the directory input, or next to a file input
2. **If output is manually set and doesn't end with "AAFs"**: Append `/AAFs` to the path
3. **If output already ends with "AAFs"**: Use it as-is (no duplication)

#### B. Single File Processing
Single files always go into the `AAFs` directory:
- Input: `/path/to/song.mp3` → Output: `/path/to/AAFs/song.aaf` (default)
- Input: `/path/to/song.mp3`, Manual output: `/custom/location` → Output: `/custom/location/AAFs/song.aaf`

#### C. Directory Processing with Source Structure Preservation
The GUI calculates the output path to include parent directory names, and batch.py mirrors any subdirectories found within the selected source:

**GUI Output Path Calculation:**
```python
# For directory input: wavTest_MX/AC_DC/Back In Black/
dir_name = "Back In Black"  # Selected directory name
parent_name = "AC_DC"  # Parent directory name
grandparent = "wavTest_MX"  # Grandparent directory
# Result: wavTest_MX/AAFs/AC_DC/Back In Black/
outp = os.path.join(grandparent, "AAFs", parent_name, dir_name)
```

**Batch Processing Subdirectory Mirroring:**
```python
# In batch.py _process_single_file()
rel = p.relative_to(src_root)  # Get relative path from selected directory
dest_dir = out_dir / rel.parent  # Create matching subdirectory structure
dest = dest_dir / (p.stem + ".aaf")
```

This two-level approach ensures:
1. The selected directory name and its parent are preserved in the output path
2. Any subdirectories within the selected directory are mirrored by batch.py

**Example:**
- Source: `wavTest_MX/AC_DC/Back In Black/` (selected)
- Contains: `01 Hells Bells.wav`, `02 Shoot to Thrill.wav`
- Output: `wavTest_MX/AAFs/AC_DC/Back In Black/01 Hells Bells.aaf`, `02 Shoot to Thrill.aaf`

If the selected directory has subdirectories (e.g., `Back In Black/Disc 1/`), batch.py mirrors them:
- Output: `wavTest_MX/AAFs/AC_DC/Back In Black/Disc 1/01 Hells Bells.aaf`

#### D. Output Field Behavior
Whether the output field is populated or left blank:
- **Blank (default)**: Field stays blank after processing, but actual output goes to auto-generated `AAFs` folder (shown in log)
- **Manually set**: Field retains user's value (without `/AAFs` appended visually), but actual processing goes to `/AAFs` subdirectory

This ensures:
1. Users always know where their files are (in `AAFs`)
2. Source directory structure is preserved within `AAFs`
3. Manual and default behaviors are consistent
4. The "Open AAF Location" button knows to open the actual `AAFs` folder (tracked separately from the output field)

### Result
**Example Workflows:**

**Workflow 1: Batch process with default output (nested directory)**
- Input: Select `wavTest_MX/AC_DC/Back In Black/`
- Output: Leave blank
- Result: AAFs created in `wavTest_MX/AAFs/AC_DC/Back In Black/` with subdirectories mirrored from source

**Workflow 2: Batch process with manual output**
- Input: Select `wavTest_MX/AC_DC/Back In Black/`
- Output: Set to `/Exports/`
- Result: AAFs created in `/Exports/AAFs/` (directory structure not preserved for manual output)

**Workflow 3: Single file with default output**
- Input: Select `/Music/song.mp3`
- Output: Leave blank
- Result: AAF created in `/Music/AAFs/song.aaf`

**Workflow 4: Single file with manual output**
- Input: Select `/Music/song.mp3`
- Output: Set to `/Exports/`
- Result: AAF created in `/Exports/AAFs/song.aaf`

---

## Integration Summary

These three improvements work together to create a robust, user-friendly batch processing experience:

1. **Progress display** keeps users informed during long operations
2. **Source validation** prevents confusing errors when files are moved/deleted
3. **Forced AAFs output** ensures predictable, organized output regardless of input path handling

The changes are implemented in:
- `mxto_aaf_gui.py`: Progress tracking, source validation, output normalization
- `mxto_aaf/batch.py`: Already supports mirrored directory structure (no changes needed)

All improvements maintain backward compatibility with the CLI and batch processing modules.
