import tkinter as tk

root = tk.Tk()
root.geometry("400x300")

# Create a horizontal PanedWindow
paned_window = tk.PanedWindow(root, orient='horizontal')
paned_window.pack(fill=tk.BOTH, expand=True)

# Left pane: A simple frame with a label
left_frame = tk.Frame(paned_window, background="lightblue")
left_label = tk.Label(left_frame, text="Left Pane", bg="lightblue")
left_label.pack(padx=20, pady=20)
paned_window.add(left_frame, width=150, minsize=50)

# Right pane: Another frame with a different color and label
right_frame = tk.Frame(paned_window, background="lightgreen")
right_label = tk.Label(right_frame, text="Right Pane", bg="lightgreen")
right_label.pack(padx=20, pady=20)
paned_window.add(right_frame, width=150, minsize=50)

root.mainloop()