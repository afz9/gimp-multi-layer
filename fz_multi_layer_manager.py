#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
Multi-Layer Manager Plugin for GIMP
Version: 0.9
Author: Farzin (AFZ Design)
"""

from gimpfu import *
import gtk
import gobject
import math

def multi_layer_manager(image, drawable):
    """
    Multi-Layer Manager - Select and perform actions on multiple layers
    """
    
    # Global variable to store copied layer properties
    copied_layer_props = None
    
    # Create dialog window
    dialog = gtk.Dialog(
        "Multi-Layer Manager",
        None,
        gtk.DIALOG_MODAL | gtk.DIALOG_DESTROY_WITH_PARENT,
        (gtk.STOCK_CANCEL, gtk.RESPONSE_CANCEL,
         gtk.STOCK_OK, gtk.RESPONSE_OK)
    )
    
    dialog.set_default_size(400, 700)  # Increased height for new button
    
    # Create main container
    vbox = gtk.VBox(spacing=10)
    dialog.vbox.pack_start(vbox, True, True, 10)
    
    # Instructions label
    instruction_label = gtk.Label("Select layers below, then choose an action:")
    instruction_label.set_alignment(0, 0.5)
    vbox.pack_start(instruction_label, False, False, 0)
    
    # Create scrolled window for layer list
    scrolled_window = gtk.ScrolledWindow()
    scrolled_window.set_policy(gtk.POLICY_AUTOMATIC, gtk.POLICY_AUTOMATIC)
    scrolled_window.set_size_request(350, 250)
    vbox.pack_start(scrolled_window, True, True, 0)
    
    # Create layer list with checkboxes
    layer_store = gtk.ListStore(bool, str, gobject.TYPE_PYOBJECT, int)  # Added int for indent level
    layer_view = gtk.TreeView(layer_store)
    
    # Checkbox column
    checkbox_renderer = gtk.CellRendererToggle()
    checkbox_renderer.set_property('activatable', True)
    
    def on_checkbox_toggled(renderer, path):
        layer_store[path][0] = not layer_store[path][0]
    
    checkbox_renderer.connect('toggled', on_checkbox_toggled)
    checkbox_column = gtk.TreeViewColumn("Select", checkbox_renderer, active=0)
    layer_view.append_column(checkbox_column)
    
    # Layer name column with custom rendering
    text_renderer = gtk.CellRendererText()
    
    def cell_data_func(column, cell, model, iter):
        indent_level = model.get_value(iter, 3)  # Get indent level
        layer_name = model.get_value(iter, 1)
        
        if indent_level == 0:  # Top level - white text on grey background
            cell.set_property('text', layer_name)
            cell.set_property('foreground', '#FFFFFF')  # White text
            cell.set_property('background', '#454545')  # Grey background
            cell.set_property('weight', 400)  # Normal weight
        else:  # Nested - normal text with more indentation
            indented_name = "    " * indent_level + layer_name.lstrip()
            cell.set_property('text', indented_name)
            cell.set_property('foreground', '#424242')  # Dark gray
            cell.set_property('background', None)  # Default background
            cell.set_property('weight', 400)  # Normal weight
    
    name_column = gtk.TreeViewColumn("Layer Name", text_renderer)
    name_column.set_cell_data_func(text_renderer, cell_data_func)
    layer_view.append_column(name_column)
    
    # Function to recursively add layers and their children
    def add_layers_recursive(layer_list, parent_name="", indent_level=0):
        for layer in layer_list:
            # Add the layer to the store with indent level
            layer_store.append([False, layer.name, layer, indent_level])
            
            # If this is a layer group, add its children
            if hasattr(layer, 'layers') and layer.layers:
                add_layers_recursive(layer.layers, layer.name, indent_level + 1)
    
    # Populate layer list with nested structure
    add_layers_recursive(image.layers)
    
    scrolled_window.add(layer_view)
    
    # Action buttons frame
    action_frame = gtk.Frame("Actions")
    vbox.pack_start(action_frame, False, False, 0)
    
    action_vbox = gtk.VBox(spacing=5)
    action_frame.add(action_vbox)
    
    # Action buttons
    duplicate_btn = gtk.Button("Duplicate Selected Layers")
    delete_btn = gtk.Button("Delete Selected Layers")
    move_up_btn = gtk.Button("Move Selected Layers Up")
    move_down_btn = gtk.Button("Move Selected Layers Down")
    move_btn = gtk.Button("Move Selected Layers...")  # New move button
    toggle_visibility_btn = gtk.Button("Toggle Visibility")
    group_btn = gtk.Button("Create Layer Group")
    merge_btn = gtk.Button("Merge Selected Layers")
    opacity_btn = gtk.Button("Set Opacity...")
    blend_mode_btn = gtk.Button("Set Blend Mode...")
    scale_btn = gtk.Button("Scale Selected Layers...")
    rotate_btn = gtk.Button("Rotate Selected Layers...")
    copy_btn = gtk.Button("Copy Layer Effects")
    paste_btn = gtk.Button("Paste Layer Effects")
    
    action_vbox.pack_start(duplicate_btn, False, False, 2)
    action_vbox.pack_start(delete_btn, False, False, 2)
    action_vbox.pack_start(move_up_btn, False, False, 2)
    action_vbox.pack_start(move_down_btn, False, False, 2)
    action_vbox.pack_start(move_btn, False, False, 2)  # Add new move button
    action_vbox.pack_start(toggle_visibility_btn, False, False, 2)
    action_vbox.pack_start(group_btn, False, False, 2)
    action_vbox.pack_start(merge_btn, False, False, 2)
    action_vbox.pack_start(opacity_btn, False, False, 2)
    action_vbox.pack_start(blend_mode_btn, False, False, 2)
    action_vbox.pack_start(scale_btn, False, False, 2)
    action_vbox.pack_start(rotate_btn, False, False, 2)
    action_vbox.pack_start(copy_btn, False, False, 2)
    action_vbox.pack_start(paste_btn, False, False, 2)
    
    # Selection helpers
    helper_frame = gtk.Frame("Selection Helpers")
    vbox.pack_start(helper_frame, False, False, 0)
    
    helper_hbox = gtk.HBox(spacing=5)
    helper_frame.add(helper_hbox)
    
    select_all_btn = gtk.Button("Select All")
    select_none_btn = gtk.Button("Select None")
    select_visible_btn = gtk.Button("Select Visible")
    
    helper_hbox.pack_start(select_all_btn, True, True, 2)
    helper_hbox.pack_start(select_none_btn, True, True, 2)
    helper_hbox.pack_start(select_visible_btn, True, True, 2)
    
    def get_selected_layers():
        selected = []
        for row in layer_store:
            if row[0]:  # If checkbox is checked
                selected.append(row[2])  # Get the layer object
        return selected
    
    def update_display():
        gimp.displays_flush()
        pdb.gimp_image_undo_group_end(image)
    
    # Button event handlers
    def on_duplicate(widget):
        pdb.gimp_image_undo_group_start(image)
        selected = get_selected_layers()
        if selected:
            for layer in selected:
                new_layer = pdb.gimp_layer_copy(layer, False)
                pdb.gimp_image_insert_layer(image, new_layer, None, 0)
            update_display()
            dialog.response(gtk.RESPONSE_OK)
    
    def on_delete(widget):
        pdb.gimp_image_undo_group_start(image)
        selected = get_selected_layers()
        if selected:
            for layer in selected:
                pdb.gimp_image_remove_layer(image, layer)
            update_display()
            dialog.response(gtk.RESPONSE_OK)
    
    def on_move_up(widget):
        pdb.gimp_image_undo_group_start(image)
        selected = get_selected_layers()
        if selected:
            # Move layers up one position
            for layer in selected:
                pos = pdb.gimp_image_get_item_position(image, layer)
                if pos > 0:
                    pdb.gimp_image_reorder_item(image, layer, None, pos - 1)
            update_display()
    
    def on_move_down(widget):
        pdb.gimp_image_undo_group_start(image)
        selected = get_selected_layers()
        if selected:
            # Move layers down one position (reverse order to avoid conflicts)
            for layer in reversed(selected):
                pos = pdb.gimp_image_get_item_position(image, layer)
                if pos < len(image.layers) - 1:
                    pdb.gimp_image_reorder_item(image, layer, None, pos + 1)
            update_display()
    
    def on_move_layers(widget):
        # Create move dialog
        move_dialog = gtk.Dialog("Move Layers", dialog, gtk.DIALOG_MODAL)
        move_dialog.add_button(gtk.STOCK_CANCEL, gtk.RESPONSE_CANCEL)
        move_dialog.add_button(gtk.STOCK_OK, gtk.RESPONSE_OK)
        
        table = gtk.Table(3, 2, False)
        table.set_row_spacings(5)
        table.set_col_spacings(10)
        move_dialog.vbox.pack_start(table, True, True, 10)
        
        # X offset input
        x_label = gtk.Label("X Offset (pixels):")
        x_label.set_alignment(0, 0.5)
        x_entry = gtk.Entry()
        x_entry.set_text("0")
        
        table.attach(x_label, 0, 1, 0, 1)
        table.attach(x_entry, 1, 2, 0, 1)
        
        # Y offset input
        y_label = gtk.Label("Y Offset (pixels):")
        y_label.set_alignment(0, 0.5)
        y_entry = gtk.Entry()
        y_entry.set_text("0")
        
        table.attach(y_label, 0, 1, 1, 2)
        table.attach(y_entry, 1, 2, 1, 2)
        
        # Quick move buttons
        button_frame = gtk.Frame("Quick Move")
        move_dialog.vbox.pack_start(button_frame, False, False, 5)
        
        button_table = gtk.Table(3, 3, True)
        button_frame.add(button_table)
        
        # Create directional buttons
        btn_up_left = gtk.Button("↖")
        btn_up = gtk.Button("↑")
        btn_up_right = gtk.Button("↗")
        btn_left = gtk.Button("←")
        btn_center = gtk.Button("○")
        btn_right = gtk.Button("→")
        btn_down_left = gtk.Button("↙")
        btn_down = gtk.Button("↓")
        btn_down_right = gtk.Button("↘")
        
        # Quick move distance entry
        distance_hbox = gtk.HBox(spacing=5)
        distance_label = gtk.Label("Distance:")
        distance_entry = gtk.Entry()
        distance_entry.set_text("10")
        distance_entry.set_size_request(50, -1)
        distance_hbox.pack_start(distance_label, False, False, 0)
        distance_hbox.pack_start(distance_entry, False, False, 0)
        move_dialog.vbox.pack_start(distance_hbox, False, False, 5)
        
        def quick_move(widget, dx, dy):
            try:
                distance = int(distance_entry.get_text())
                x_entry.set_text(str(int(x_entry.get_text()) + dx * distance))
                y_entry.set_text(str(int(y_entry.get_text()) + dy * distance))
            except ValueError:
                pass
        
        def reset_position(widget):
            x_entry.set_text("0")
            y_entry.set_text("0")
        
        # Connect quick move buttons
        btn_up_left.connect("clicked", quick_move, -1, -1)
        btn_up.connect("clicked", quick_move, 0, -1)
        btn_up_right.connect("clicked", quick_move, 1, -1)
        btn_left.connect("clicked", quick_move, -1, 0)
        btn_center.connect("clicked", reset_position)
        btn_right.connect("clicked", quick_move, 1, 0)
        btn_down_left.connect("clicked", quick_move, -1, 1)
        btn_down.connect("clicked", quick_move, 0, 1)
        btn_down_right.connect("clicked", quick_move, 1, 1)
        
        # Arrange buttons in grid
        button_table.attach(btn_up_left, 0, 1, 0, 1)
        button_table.attach(btn_up, 1, 2, 0, 1)
        button_table.attach(btn_up_right, 2, 3, 0, 1)
        button_table.attach(btn_left, 0, 1, 1, 2)
        button_table.attach(btn_center, 1, 2, 1, 2)
        button_table.attach(btn_right, 2, 3, 1, 2)
        button_table.attach(btn_down_left, 0, 1, 2, 3)
        button_table.attach(btn_down, 1, 2, 2, 3)
        button_table.attach(btn_down_right, 2, 3, 2, 3)
        
        move_dialog.show_all()
        response = move_dialog.run()
        
        if response == gtk.RESPONSE_OK:
            try:
                x_offset = int(x_entry.get_text())
                y_offset = int(y_entry.get_text())
                
                if x_offset != 0 or y_offset != 0:
                    pdb.gimp_image_undo_group_start(image)
                    selected = get_selected_layers()
                    
                    for layer in selected:
                        current_x, current_y = layer.offsets
                        new_x = current_x + x_offset
                        new_y = current_y + y_offset
                        pdb.gimp_layer_set_offsets(layer, new_x, new_y)
                    
                    update_display()
                
            except ValueError:
                pass  # Invalid input, ignore
        
        move_dialog.destroy()
    
    def on_toggle_visibility(widget):
        pdb.gimp_image_undo_group_start(image)
        selected = get_selected_layers()
        if selected:
            for layer in selected:
                layer.visible = not layer.visible
            update_display()
    
    def on_create_group(widget):
        pdb.gimp_image_undo_group_start(image)
        selected = get_selected_layers()
        if selected:
            # Create a new layer group
            group = pdb.gimp_layer_group_new(image)
            pdb.gimp_image_insert_layer(image, group, None, 0)
            group.name = "Layer Group"
            
            # Move selected layers into the group
            for layer in selected:
                pdb.gimp_image_reorder_item(image, layer, group, 0)
            update_display()
            dialog.response(gtk.RESPONSE_OK)
    
    def on_merge_layers(widget):
        pdb.gimp_image_undo_group_start(image)
        selected = get_selected_layers()
        if len(selected) > 1:
            # Merge down from top to bottom
            selected.sort(key=lambda l: pdb.gimp_image_get_item_position(image, l))
            base_layer = selected[0]
            for layer in selected[1:]:
                try:
                    base_layer = pdb.gimp_image_merge_down(image, layer, 0)
                except:
                    pass  # Skip if merge fails
            update_display()
            dialog.response(gtk.RESPONSE_OK)
    
    def on_set_opacity(widget):
        # Create simple opacity dialog
        opacity_dialog = gtk.Dialog("Set Opacity", dialog, gtk.DIALOG_MODAL)
        opacity_dialog.add_button(gtk.STOCK_CANCEL, gtk.RESPONSE_CANCEL)
        opacity_dialog.add_button(gtk.STOCK_OK, gtk.RESPONSE_OK)
        
        hbox = gtk.HBox(spacing=10)
        opacity_dialog.vbox.pack_start(hbox, True, True, 10)
        
        label = gtk.Label("Opacity (0-100):")
        hbox.pack_start(label, False, False, 5)
        
        entry = gtk.Entry()
        entry.set_text("100")
        hbox.pack_start(entry, True, True, 5)
        
        opacity_dialog.show_all()
        response = opacity_dialog.run()
        
        if response == gtk.RESPONSE_OK:
            try:
                opacity = float(entry.get_text())
                if 0 <= opacity <= 100:
                    pdb.gimp_image_undo_group_start(image)
                    selected = get_selected_layers()
                    for layer in selected:
                        layer.opacity = opacity
                    update_display()
            except:
                pass
        
        opacity_dialog.destroy()
    
    def on_set_blend_mode(widget):
        # Create blend mode dialog
        modes = [
            ("Normal", 0), ("Multiply", 3), ("Screen", 4), ("Overlay", 5),
            ("Soft Light", 19), ("Hard Light", 18), ("Color Dodge", 16),
            ("Color Burn", 17), ("Darken Only", 7), ("Lighten Only", 8),
            ("Addition", 33), ("Subtract", 34), ("Difference", 6),
            ("Color", 13), ("Hue", 11), ("Saturation", 12), ("Luminance", 14)
        ]
        
        blend_dialog = gtk.Dialog("Set Blend Mode", dialog, gtk.DIALOG_MODAL)
        blend_dialog.add_button(gtk.STOCK_CANCEL, gtk.RESPONSE_CANCEL)
        blend_dialog.add_button(gtk.STOCK_OK, gtk.RESPONSE_OK)
        
        combo = gtk.combo_box_new_text()
        for mode_name, mode_value in modes:
            combo.append_text(mode_name)
        combo.set_active(0)
        
        blend_dialog.vbox.pack_start(combo, True, True, 10)
        blend_dialog.show_all()
        response = blend_dialog.run()
        
        if response == gtk.RESPONSE_OK:
            selected_idx = combo.get_active()
            if selected_idx >= 0:
                mode_value = modes[selected_idx][1]
                pdb.gimp_image_undo_group_start(image)
                selected = get_selected_layers()
                for layer in selected:
                    pdb.gimp_layer_set_mode(layer, mode_value)
                update_display()
        
        blend_dialog.destroy()
    
    def on_scale_layers(widget):
        # Create scale dialog
        scale_dialog = gtk.Dialog("Scale Layers", dialog, gtk.DIALOG_MODAL)
        scale_dialog.add_button(gtk.STOCK_CANCEL, gtk.RESPONSE_CANCEL)
        scale_dialog.add_button(gtk.STOCK_OK, gtk.RESPONSE_OK)
        
        table = gtk.Table(4, 2, False)
        table.set_row_spacings(5)
        table.set_col_spacings(10)
        scale_dialog.vbox.pack_start(table, True, True, 10)
        
        # Width input
        width_label = gtk.Label("Width (px or %):")
        width_label.set_alignment(0, 0.5)
        width_entry = gtk.Entry()
        width_entry.set_text("100%")
        
        table.attach(width_label, 0, 1, 0, 1)
        table.attach(width_entry, 1, 2, 0, 1)
        
        # Height input
        height_label = gtk.Label("Height (px or %):")
        height_label.set_alignment(0, 0.5)
        height_entry = gtk.Entry()
        height_entry.set_text("100%")
        
        table.attach(height_label, 0, 1, 1, 2)
        table.attach(height_entry, 1, 2, 1, 2)
        
        # Chain link checkbox for proportional scaling
        chain_check = gtk.CheckButton("Keep proportions")
        chain_check.set_active(True)
        table.attach(chain_check, 0, 2, 2, 3)
        
        # Helper function to parse dimension value
        def parse_dimension(text):
            text = text.strip()
            if text.endswith('%'):
                return float(text[:-1]), True  # value, is_percentage
            else:
                return float(text), False
        
        # Helper function to format dimension value
        def format_dimension(value, is_percentage):
            if is_percentage:
                return "%.1f%%" % value
            else:
                return "%d" % int(value)
        
        # Variables to prevent recursive updates
        updating_width = [False]  # Use list to avoid scope issues
        updating_height = [False]
        
        # Update height when width changes
        def on_width_changed(entry):
            if updating_height[0] or not chain_check.get_active():
                return
            
            try:
                updating_width[0] = True
                width_text = width_entry.get_text().strip()
                if not width_text:
                    return
                
                width_val, width_is_percent = parse_dimension(width_text)
                
                # If both are percentages, just copy the value
                if width_is_percent:
                    height_entry.set_text(format_dimension(width_val, True))
                else:
                    # Convert to percentage based on original dimensions if possible
                    # For now, just copy the pixel value - could be enhanced to be smarter
                    height_entry.set_text(format_dimension(width_val, False))
                    
            except ValueError:
                pass  # Invalid input, ignore
            finally:
                updating_width[0] = False
        
        # Update width when height changes
        def on_height_changed(entry):
            if updating_width[0] or not chain_check.get_active():
                return
            
            try:
                updating_height[0] = True
                height_text = height_entry.get_text().strip()
                if not height_text:
                    return
                
                height_val, height_is_percent = parse_dimension(height_text)
                
                # If both are percentages, just copy the value
                if height_is_percent:
                    width_entry.set_text(format_dimension(height_val, True))
                else:
                    # Convert to percentage based on original dimensions if possible
                    # For now, just copy the pixel value - could be enhanced to be smarter
                    width_entry.set_text(format_dimension(height_val, False))
                    
            except ValueError:
                pass  # Invalid input, ignore
            finally:
                updating_height[0] = False
        
        # Connect the change events
        width_entry.connect('focus-out-event', lambda w, e: on_width_changed(w))
        width_entry.connect('activate', on_width_changed)  # Enter key
        height_entry.connect('focus-out-event', lambda w, e: on_height_changed(w))
        height_entry.connect('activate', on_height_changed)  # Enter key
        
        # Interpolation method
        interp_label = gtk.Label("Interpolation:")
        interp_label.set_alignment(0, 0.5)
        interp_combo = gtk.combo_box_new_text()
        interp_combo.append_text("None (Fastest)")
        interp_combo.append_text("Linear")
        interp_combo.append_text("Cubic")
        interp_combo.set_active(2)  # Default to Cubic
        
        table.attach(interp_label, 0, 1, 3, 4)
        table.attach(interp_combo, 1, 2, 3, 4)
        
        scale_dialog.show_all()
        response = scale_dialog.run()
        
        if response == gtk.RESPONSE_OK:
            try:
                width_text = width_entry.get_text().strip()
                height_text = height_entry.get_text().strip()
                keep_proportions = chain_check.get_active()
                interp_type = interp_combo.get_active()
                
                pdb.gimp_image_undo_group_start(image)
                selected = get_selected_layers()
                
                for layer in selected:
                    current_width = layer.width
                    current_height = layer.height
                    
                    # Parse width
                    if width_text.endswith('%'):
                        new_width = int(current_width * float(width_text[:-1]) / 100)
                    else:
                        new_width = int(width_text)
                    
                    # Parse height
                    if height_text.endswith('%'):
                        new_height = int(current_height * float(height_text[:-1]) / 100)
                    else:
                        new_height = int(height_text)
                    
                    # Apply proportional scaling if requested
                    if keep_proportions:
                        # Use width ratio for both dimensions
                        ratio = float(new_width) / current_width
                        new_height = int(current_height * ratio)
                    
                    # Scale the layer
                    if new_width > 0 and new_height > 0:
                        pdb.gimp_layer_scale(layer, new_width, new_height, False)
                
                update_display()
                
            except Exception as e:
                print("Scale error:", str(e))
        
        scale_dialog.destroy()
    
    def on_rotate_layers(widget):
        # Create rotate dialog
        rotate_dialog = gtk.Dialog("Rotate Layers", dialog, gtk.DIALOG_MODAL)
        rotate_dialog.add_button(gtk.STOCK_CANCEL, gtk.RESPONSE_CANCEL)
        rotate_dialog.add_button(gtk.STOCK_OK, gtk.RESPONSE_OK)
        
        table = gtk.Table(3, 2, False)
        table.set_row_spacings(5)
        table.set_col_spacings(10)
        rotate_dialog.vbox.pack_start(table, True, True, 10)
        
        # Angle input
        angle_label = gtk.Label("Angle (degrees):")
        angle_label.set_alignment(0, 0.5)
        angle_entry = gtk.Entry()
        angle_entry.set_text("0")
        
        table.attach(angle_label, 0, 1, 0, 1)
        table.attach(angle_entry, 1, 2, 0, 1)
        
        # Quick angle buttons
        button_hbox = gtk.HBox(spacing=5)
        btn_90 = gtk.Button("90°")
        btn_180 = gtk.Button("180°")
        btn_270 = gtk.Button("270°")
        btn_neg90 = gtk.Button("-90°")
        
        def set_angle(widget, angle):
            angle_entry.set_text(str(angle))
        
        btn_90.connect("clicked", set_angle, 90)
        btn_180.connect("clicked", set_angle, 180)
        btn_270.connect("clicked", set_angle, 270)
        btn_neg90.connect("clicked", set_angle, -90)
        
        button_hbox.pack_start(btn_90, True, True, 0)
        button_hbox.pack_start(btn_180, True, True, 0)
        button_hbox.pack_start(btn_270, True, True, 0)
        button_hbox.pack_start(btn_neg90, True, True, 0)
        
        table.attach(button_hbox, 0, 2, 1, 2)
        
        # Interpolation method
        interp_label = gtk.Label("Interpolation:")
        interp_label.set_alignment(0, 0.5)
        interp_combo = gtk.combo_box_new_text()
        interp_combo.append_text("None (Fastest)")
        interp_combo.append_text("Linear")
        interp_combo.append_text("Cubic")
        interp_combo.set_active(2)  # Default to Cubic
        
        table.attach(interp_label, 0, 1, 2, 3)
        table.attach(interp_combo, 1, 2, 2, 3)
        
        rotate_dialog.show_all()
        response = rotate_dialog.run()
        
        if response == gtk.RESPONSE_OK:
            try:
                angle = float(angle_entry.get_text())
                interp_type = interp_combo.get_active()
                
                # Convert degrees to radians
                angle_rad = math.radians(angle)
                
                pdb.gimp_image_undo_group_start(image)
                selected = get_selected_layers()
                
                for layer in selected:
                    # Get layer center
                    center_x = layer.offsets[0] + layer.width / 2.0
                    center_y = layer.offsets[1] + layer.height / 2.0
                    
                    # Rotate around layer center
                    pdb.gimp_item_transform_rotate(layer, angle_rad, False, center_x, center_y)
                
                update_display()
                
            except Exception as e:
                print("Rotate error:", str(e))
        
        rotate_dialog.destroy()
    
    def on_copy_effects(widget):
        selected = get_selected_layers()
        if len(selected) == 1:
            layer = selected[0]
            global copied_layer_props
            copied_layer_props = {
                'opacity': layer.opacity,
                'mode': layer.mode,
                'visible': layer.visible
            }
    
    def on_paste_effects(widget):
        if copied_layer_props:
            pdb.gimp_image_undo_group_start(image)
            selected = get_selected_layers()
            for layer in selected:
                layer.opacity = copied_layer_props['opacity']
                pdb.gimp_layer_set_mode(layer, copied_layer_props['mode'])
                layer.visible = copied_layer_props['visible']
            update_display()
    
    # Selection helper functions
    def on_select_all(widget):
        for row in layer_store:
            row[0] = True
    
    def on_select_none(widget):
        for row in layer_store:
            row[0] = False
    
    def on_select_visible(widget):
        for row in layer_store:
            layer = row[2]
            row[0] = layer.visible
    
    # Connect button signals
    duplicate_btn.connect("clicked", on_duplicate)
    delete_btn.connect("clicked", on_delete)
    move_up_btn.connect("clicked", on_move_up)
    move_down_btn.connect("clicked", on_move_down)
    move_btn.connect("clicked", on_move_layers)  # Connect new move button
    toggle_visibility_btn.connect("clicked", on_toggle_visibility)
    group_btn.connect("clicked", on_create_group)
    merge_btn.connect("clicked", on_merge_layers)
    opacity_btn.connect("clicked", on_set_opacity)
    blend_mode_btn.connect("clicked", on_set_blend_mode)
    scale_btn.connect("clicked", on_scale_layers)
    rotate_btn.connect("clicked", on_rotate_layers)
    copy_btn.connect("clicked", on_copy_effects)
    paste_btn.connect("clicked", on_paste_effects)
    
    select_all_btn.connect("clicked", on_select_all)
    select_none_btn.connect("clicked", on_select_none)
    select_visible_btn.connect("clicked", on_select_visible)
    
    # Show dialog
    dialog.show_all()
    response = dialog.run()
    dialog.destroy()

# Register the plugin
register(
    "multi_layer_manager",
    "Multi-Layer Manager - Select and manage multiple layers at once",
    "Select multiple layers and perform batch operations like duplicate, delete, move, scale, rotate, etc.",
    "Your Name",
    "Your Name",
    "2024",
    "Multi-Layer Manager...",
    "*",
    [
        (PF_IMAGE, "image", "Input image", None),
        (PF_DRAWABLE, "drawable", "Input drawable", None),
    ],
    [],
    multi_layer_manager,
    menu="<Image>/Layer/")

main()