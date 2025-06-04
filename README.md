---

# Multi-Layer Manager Plugin for GIMP

A versatile GIMP plugin to batch manage layers with ease, supporting nested groups and a wide array of operations.

---

## Installation

1. Save the script file (e.g., `multi_layer_manager.py`) into GIMP's plug-ins directory:
   - **Linux:** `~/.config/GIMP/2.10/plug-ins/`
   - **Windows:** `C:\Users\<YourUser>\AppData\Roaming\GIMP\2.10\plug-ins\`
   - **macOS:** `~/Library/Application Support/GIMP/2.10/plug-ins/`

2. **(Linux/macOS only)** Make the script executable:
   ```bash
   chmod +x multi_layer_manager.py
   ```

3. Restart GIMP or refresh the scripts via:
   - **GIMP menu:** Filters > Script-Fu > Refresh scripts

---

## Usage

1. Open your image in GIMP.
2. Navigate to **Layer > Multi-Layer Manager...** in the menu bar.
3. The plugin dialog will appear with the following features:
   - **Layer List:** Select multiple layers using checkboxes. Nested groups are displayed with indentation.
   - **Actions:** Choose batch operations such as:
     - Duplicate, delete, move up/down
     - Move layers with offset controls
     - Toggle visibility
     - Create groups, merge layers
     - Set opacity and blend mode
     - Scale and rotate layers
     - Copy and paste layer effects
   - **Selection Helpers:** Select all, none, or only visible layers quickly.
4. Click **OK** to execute the selected operations.

---

## Additional Notes

- The plugin has been tested on **GIMP Version 2.10.22**.
- Supports nested layer groups for hierarchical management.
- Some actions will open additional dialogs for fine-tuned control.
- Always save your work before performing batch operations to prevent accidental data loss.

---

## A Little Favor :)

If you find this plugin useful and want to support my work, consider buying me a coffee!  
Support link: [https://paypal.me/AFZDesign](https://paypal.me/AFZDesign)

Thank you for your support!

---

## License

This project is licensed under the MIT License. See the [LICENSE](LICENSE) file for details.

---

**Enjoy managing your layers efficiently!**

---
