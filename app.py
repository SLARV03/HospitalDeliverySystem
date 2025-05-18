import tkinter as tk
from tkinter import messagebox, ttk
import heapq
from collections import defaultdict
import math

class HospitalDeliveryApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Hospital Medicine Delivery System")
        
        # Room coordinates with optimized layout
        self.room_positions = {
            # Ground Floor
            "Main Entrance": (400, 550),
            "Emergency Exit": (100, 550),
            "Information Desk": (400, 500),
            "Emergency": (300, 550),
            "Pharmacy": (500, 500),
            "Cafeteria": (600, 550),
            "Ground Floor Hallway": (400, 400),
            
            # First Floor
            "Floor 1 Elevator": (400, 300),
            "Floor 1 Emergency Exit": (700, 300),
            "Floor 1 Hallway": (500, 300),
            "Ward A": (600, 250),
            "Room 101": (700, 200),
            "Room 102": (700, 250),
            "Room 103": (700, 300),
            "Ward B": (600, 350),
            "Room 201": (700, 325),
            "Room 202": (700, 375),
            
            # Second Floor
            "Floor 2 Elevator": (400, 200),
            "Floor 2 Emergency Exit": (100, 200),
            "Floor 2 Hallway": (300, 200),
            "ICU": (200, 200),
            "ICU Room 1": (100, 150),
            "ICU Room 2": (100, 250),
            "Operating Theaters": (300, 150),
            "Theater 1": (200, 100),
            "Theater 2": (300, 100),
            
            # Special Areas
            "Pediatrics Ward": (600, 150),
            "Pediatrics Room 1": (650, 100),
            "Pediatrics Room 2": (650, 200),
            "Oncology Ward": (600, 400),
            "Oncology Room 1": (650, 350),
            "Oncology Room 2": (650, 450),
            
            # Staff Areas
            "Doctors Lounge": (200, 300),
            "Nurses Station": (200, 400),
            "Administration": (100, 400)
        }
        
        # Hospital layout graph
        self.hospital = self.create_hospital_layout()
        
        # Medicine inventory
        self.medicines = {
            "Paracetamol": 100, "Ibuprofen": 80, "Amoxicillin": 60,
            "Omeprazole": 75, "Loratadine": 50, "Morphine": 30,
            "Insulin": 40, "Chemotherapy Drugs": 20, "Pediatric Antibiotics": 45
        }
        
        # Delivery system state
        self.deliveries = []
        self.current_path = []
        self.current_delivery_index = 0
        self.delivery_in_progress = False
        self.emergency_activated = False
        
        # Initialize GUI
        self.setup_gui()
        self.center_view()

    def create_hospital_layout(self):
        """Create the hospital graph structure with proper connections"""
        return {
            # Ground Floor
            "Main Entrance": {"Information Desk": 1, "Emergency": 2, "Emergency Exit": 3},
            "Emergency Exit": {"Main Entrance": 3, "Emergency": 2},
            "Information Desk": {"Main Entrance": 1, "Pharmacy": 1, "Ground Floor Hallway": 2},
            "Emergency": {"Main Entrance": 2, "Pharmacy": 3, "Emergency Exit": 2},
            "Pharmacy": {"Information Desk": 1, "Emergency": 3, "Ground Floor Hallway": 1, "Cafeteria": 2},
            "Cafeteria": {"Pharmacy": 2, "Ground Floor Hallway": 3},
            "Ground Floor Hallway": {"Information Desk": 2, "Pharmacy": 1, "Cafeteria": 3, 
                                   "Floor 1 Elevator": 2, "Floor 2 Elevator": 2, 
                                   "Pediatrics Ward": 4, "Oncology Ward": 4},
            
            # First Floor
            "Floor 1 Elevator": {"Ground Floor Hallway": 2, "Floor 1 Hallway": 1},
            "Floor 1 Emergency Exit": {"Floor 1 Hallway": 2},
            "Floor 1 Hallway": {"Floor 1 Elevator": 1, "Ward A": 2, "Ward B": 2, 
                               "Doctors Lounge": 3, "Floor 1 Emergency Exit": 2},
            "Ward A": {"Floor 1 Hallway": 2, "Room 101": 1, "Room 102": 1, "Room 103": 1},
            "Ward B": {"Floor 1 Hallway": 2, "Room 201": 1, "Room 202": 1},
            "Room 101": {"Ward A": 1},
            "Room 102": {"Ward A": 1},
            "Room 103": {"Ward A": 1},
            "Room 201": {"Ward B": 1},
            "Room 202": {"Ward B": 1},
            
            # Second Floor
            "Floor 2 Elevator": {"Ground Floor Hallway": 2, "Floor 2 Hallway": 1},
            "Floor 2 Emergency Exit": {"Floor 2 Hallway": 2},
            "Floor 2 Hallway": {"Floor 2 Elevator": 1, "ICU": 2, "Operating Theaters": 1, 
                               "Nurses Station": 1, "Floor 2 Emergency Exit": 2},
            "ICU": {"Floor 2 Hallway": 2, "ICU Room 1": 1, "ICU Room 2": 1},
            "Operating Theaters": {"Floor 2 Hallway": 1, "Theater 1": 1, "Theater 2": 1},
            "ICU Room 1": {"ICU": 1},
            "ICU Room 2": {"ICU": 1},
            "Theater 1": {"Operating Theaters": 1},
            "Theater 2": {"Operating Theaters": 1},
            
            # Special Areas
            "Pediatrics Ward": {"Ground Floor Hallway": 4, "Pediatrics Room 1": 1, "Pediatrics Room 2": 1},
            "Oncology Ward": {"Ground Floor Hallway": 4, "Oncology Room 1": 1, "Oncology Room 2": 1},
            "Pediatrics Room 1": {"Pediatrics Ward": 1},
            "Pediatrics Room 2": {"Pediatrics Ward": 1},
            "Oncology Room 1": {"Oncology Ward": 1},
            "Oncology Room 2": {"Oncology Ward": 1},
            
            # Staff Areas
            "Doctors Lounge": {"Floor 1 Hallway": 3},
            "Nurses Station": {"Floor 2 Hallway": 1, "Administration": 2},
            "Administration": {"Nurses Station": 2}
        }

    def setup_gui(self):
        """Initialize the graphical user interface"""
        self.root.geometry("1200x800")
        
        # Control Frame
        control_frame = ttk.Frame(self.root, width=300)
        control_frame.pack(side=tk.LEFT, fill=tk.Y, padx=10, pady=10)
        
        # Medicine Stock Display
        stock_frame = ttk.Frame(control_frame)
        stock_frame.pack(fill=tk.X, pady=5)
        
        self.stock_canvas = tk.Canvas(stock_frame, height=150)
        scrollbar = ttk.Scrollbar(stock_frame, orient="vertical", command=self.stock_canvas.yview)
        self.scrollable_frame = ttk.Frame(self.stock_canvas)
        
        self.scrollable_frame.bind("<Configure>", 
            lambda e: self.stock_canvas.configure(scrollregion=self.stock_canvas.bbox("all")))
        
        self.stock_canvas.create_window((0, 0), window=self.scrollable_frame, anchor="nw")
        self.stock_canvas.configure(yscrollcommand=scrollbar.set)
        
        self.stock_canvas.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        self.update_stock_display()
        
        # Delivery Controls
        ttk.Label(control_frame, text="Delivery Room:").pack(pady=5)
        self.room_var = tk.StringVar()
        self.room_combobox = ttk.Combobox(control_frame, textvariable=self.room_var, 
                                        values=list(self.hospital.keys()))
        self.room_combobox.pack(fill=tk.X, pady=5)
        self.room_combobox.current(0)
        
        ttk.Label(control_frame, text="Medicine:").pack(pady=5)
        self.med_var = tk.StringVar()
        self.med_combobox = ttk.Combobox(control_frame, textvariable=self.med_var, 
                                       values=list(self.medicines.keys()))
        self.med_combobox.pack(fill=tk.X, pady=5)
        self.med_combobox.current(0)
        
        ttk.Label(control_frame, text="Quantity:").pack(pady=5)
        self.qty_var = tk.IntVar(value=1)
        self.qty_spinbox = ttk.Spinbox(control_frame, from_=1, to=20, textvariable=self.qty_var)
        self.qty_spinbox.pack(fill=tk.X, pady=5)
        
        ttk.Button(control_frame, text="Add Delivery", command=self.add_delivery).pack(fill=tk.X, pady=5)
        ttk.Button(control_frame, text="Remove Delivery", command=self.remove_delivery).pack(fill=tk.X, pady=5)
        
        # Emergency Button
        self.emergency_btn = tk.Button(control_frame, text="EMERGENCY STOP", 
                                     command=self.activate_emergency,
                                     bg="red", fg="white", font=('Arial', 12, 'bold'))
        self.emergency_btn.pack(fill=tk.X, pady=10)
        
        # Delivery List
        self.delivery_listbox = tk.Listbox(control_frame, height=10)
        self.delivery_listbox.pack(fill=tk.BOTH, expand=True, pady=5)
        
        # Delivery Controls
        ttk.Button(control_frame, text="Start Delivery", command=self.start_delivery).pack(fill=tk.X, pady=5)
        self.next_btn = ttk.Button(control_frame, text="Next Step", 
                                  command=self.next_step, state=tk.DISABLED)
        self.next_btn.pack(fill=tk.X, pady=5)
        
        # Display Frame with Scrollable Canvas
        display_frame = ttk.Frame(self.root)
        display_frame.pack(side=tk.RIGHT, expand=True, fill=tk.BOTH)
        
        self.canvas = tk.Canvas(display_frame, bg='white', scrollregion=(0, 0, 1600, 1600))
        h_scroll = ttk.Scrollbar(display_frame, orient="horizontal", command=self.canvas.xview)
        v_scroll = ttk.Scrollbar(display_frame, orient="vertical", command=self.canvas.yview)
        self.canvas.configure(xscrollcommand=h_scroll.set, yscrollcommand=v_scroll.set)
        
        self.canvas.grid(row=0, column=0, sticky="nsew")
        v_scroll.grid(row=0, column=1, sticky="ns")
        h_scroll.grid(row=1, column=0, sticky="ew")
        
        display_frame.grid_rowconfigure(0, weight=1)
        display_frame.grid_columnconfigure(0, weight=1)
        
        self.canvas.bind("<MouseWheel>", lambda e: self.canvas.yview_scroll(-1*(e.delta//120), "units"))
        self.draw_hospital_map()

    def update_stock_display(self):
        """Update the medicine stock display"""
        for widget in self.scrollable_frame.winfo_children():
            widget.destroy()
            
        for med, qty in self.medicines.items():
            frame = ttk.Frame(self.scrollable_frame)
            frame.pack(fill=tk.X, pady=2)
            color = 'red' if qty < 10 else 'orange' if qty < 25 else 'black'
            ttk.Label(frame, text=f"{med}:", width=20).pack(side=tk.LEFT)
            ttk.Label(frame, text=str(qty), foreground=color, width=10).pack(side=tk.LEFT)

    def draw_hospital_map(self):
        """Draw the hospital map with current state"""
        self.canvas.delete("all")
        
        # Draw connections
        for room, connections in self.hospital.items():
            x1, y1 = self.room_positions[room]
            for neighbor, dist in connections.items():
                x2, y2 = self.room_positions[neighbor]
                color = "red" if "Emergency" in room+neighbor else "blue" if "Elevator" in room+neighbor else "gray"
                self.canvas.create_line(x1, y1, x2, y2, fill=color, width=2)
                dx, dy = x2-x1, y2-y1
                angle = math.atan2(dy, dx)
                self.canvas.create_text(x1+dx/2+10*math.sin(angle), y1+dy/2-10*math.cos(angle),
                                      text=str(dist), fill="blue", font=('Arial', 8))
        
        # Draw rooms
        for room, (x, y) in self.room_positions.items():
            color = self.get_room_color(room)
            self.canvas.create_oval(x-25, y-25, x+25, y+25, fill=color, outline="black")
            label = self.get_room_label(room)
            self.canvas.create_text(x, y, text=label, font=('Arial', 8), width=50)
            
            if any(d[0] == room for d in self.deliveries):
                self.canvas.create_oval(x-30, y-30, x+30, y+30, outline="yellow", width=2)
        
        # Draw current position
        if self.current_path and self.current_delivery_index < len(self.current_path):
            current_room = self.current_path[self.current_delivery_index]
            x, y = self.room_positions[current_room]
            color = "red" if self.emergency_activated else "green"
            self.canvas.create_oval(x-30, y-30, x+30, y+30, outline=color, width=3)
            self.canvas.create_text(x, y+40, text="CURRENT", fill=color, font=('Arial', 10, 'bold'))
            
            # Draw path
            path = [self.room_positions[room] for room in self.current_path]
            for i in range(len(path)-1):
                self.canvas.create_line(path[i][0], path[i][1], path[i+1][0], path[i+1][1],
                                      fill=color, width=3, arrow=tk.LAST if i == self.current_delivery_index else None)
        
        self.canvas.configure(scrollregion=self.canvas.bbox("all"))

    def get_room_color(self, room):
        """Return color code based on room type"""
        if "Emergency Exit" in room:
            return "#ff9999"
        elif "Main Entrance" in room or "Information Desk" in room:
            return "lightgreen"
        elif "Pharmacy" in room:
            return "pink"
        elif "Room" in room or "Ward" in room:
            return "lightyellow"
        elif "ICU" in room or "Theater" in room:
            return "#ffcccc"
        elif "Elevator" in room or "Hallway" in room:
            return "#f0f0f0"
        elif "Cafeteria" in room:
            return "#ffffcc"
        elif "Administration" in room or "Lounge" in room or "Station" in room:
            return "#e6f3ff"
        return "lightblue"

    def get_room_label(self, room):
        """Return shortened room label"""
        replacements = {
            "Room ": "R", "Theater ": "T", "Ward ": "W", 
            "Emergency ": "Emerg.", "Pediatrics ": "Peds.", 
            "Oncology ": "Oncol.", "Administration": "Admin",
            "Information Desk": "Info Desk"
        }
        for old, new in replacements.items():
            if old in room:
                return room.replace(old, new)
        return room

    def center_view(self):
        """Center the canvas view"""
        self.canvas.xview_moveto(0.25)
        self.canvas.yview_moveto(0.25)

    def add_delivery(self):
        """Add a delivery to the list"""
        if self.delivery_in_progress:
            messagebox.showerror("Error", "Cannot add during active delivery")
            return
            
        room = self.room_var.get()
        med = self.med_var.get()
        qty = self.qty_var.get()
        
        if not room:
            messagebox.showerror("Error", "Please select a room")
            return
        
        if qty < 1:
            messagebox.showerror("Error", "Quantity must be at least 1")
            return
            
        if qty > self.medicines[med]:
            messagebox.showerror("Error", f"Not enough {med} in stock")
            return
        
        # Update existing delivery if exists
        for i, (r, m, q) in enumerate(self.deliveries):
            if r == room and m == med:
                self.deliveries[i] = (r, m, q+qty)
                self.medicines[med] -= qty
                self.update_stock_display()
                self.update_delivery_listbox()
                return
        
        # Add new delivery
        self.deliveries.append((room, med, qty))
        self.medicines[med] -= qty
        self.update_stock_display()
        self.update_delivery_listbox()

    def update_delivery_listbox(self):
        """Update the delivery list display"""
        self.delivery_listbox.delete(0, tk.END)
        for room, med, qty in self.deliveries:
            self.delivery_listbox.insert(tk.END, f"{room}: {med} x{qty}")

    def remove_delivery(self):
        """Remove selected delivery"""
        if self.delivery_in_progress:
            messagebox.showerror("Error", "Cannot remove during active delivery")
            return
            
        selection = self.delivery_listbox.curselection()
        if not selection:
            return
            
        index = selection[0]
        room, med, qty = self.deliveries[index]
        self.medicines[med] += qty
        del self.deliveries[index]
        self.update_stock_display()
        self.update_delivery_listbox()

    def start_delivery(self):
        """Start the delivery process"""
        if not self.deliveries:
            messagebox.showerror("Error", "No deliveries in the list")
            return
            
        self.delivery_in_progress = True
        self.emergency_activated = False
        rooms_to_visit = list(set(d[0] for d in self.deliveries))
        self.current_path = self.find_optimal_path("Pharmacy", rooms_to_visit)
        self.current_delivery_index = 0
        
        self.next_btn.config(state=tk.NORMAL)
        self.start_btn.config(state=tk.DISABLED)
        self.draw_hospital_map()
        messagebox.showinfo("Delivery Started", f"Route: {' -> '.join(self.current_path)}")

    def next_step(self):
        """Advance to next delivery step"""
        if self.emergency_activated:
            return
            
        if self.current_delivery_index < len(self.current_path) - 1:
            self.current_delivery_index += 1
            current_room = self.current_path[self.current_delivery_index]
            
            # Check for deliveries to this room
            deliveries = [d for d in self.deliveries if d[0] == current_room]
            if deliveries:
                items = "\n".join([f"{med} x{qty}" for _, med, qty in deliveries])
                messagebox.showinfo(f"Deliveries to {current_room}", items)
            
            self.draw_hospital_map()
        else:
            messagebox.showinfo("Delivery Complete", "All deliveries finished!")
            self.reset_delivery()

    def reset_delivery(self):
        """Reset delivery state"""
        self.delivery_in_progress = False
        self.current_path = []
        self.current_delivery_index = 0
        self.next_btn.config(state=tk.DISABLED)
        self.start_btn.config(state=tk.NORMAL)
        self.draw_hospital_map()

    def activate_emergency(self):
        """Emergency stop procedure"""
        if not self.delivery_in_progress:
            messagebox.showinfo("Info", "No active delivery to interrupt")
            return
            
        self.emergency_activated = True
        current_room = self.current_path[self.current_delivery_index]
        
        # Determine current floor
        floor = "Ground Floor"
        if "Floor 1" in current_room:
            floor = "First Floor"
        elif "Floor 2" in current_room:
            floor = "Second Floor"
            
        exit_room = self.emergency_exits.get(floor, "Emergency Exit")
        
        # Find path to emergency exit
        distance, path = self.a_star_search(current_room, exit_room)
        if distance == float('inf'):
            messagebox.showerror("Error", "No path to emergency exit!")
            return
            
        self.current_path = path
        self.current_delivery_index = 0
        self.advance_emergency_path()

    def advance_emergency_path(self):
        """Automatically advance through emergency path"""
        if self.current_delivery_index < len(self.current_path) - 1:
            self.current_delivery_index += 1
            self.draw_hospital_map()
            self.root.after(1000, self.advance_emergency_path)
        else:
            messagebox.showinfo("Emergency Exit Reached", f"Arrived at {self.current_path[-1]}")
            self.reset_delivery()

    def a_star_search(self, start, goal):
        """A* pathfinding algorithm"""
        open_set = []
        heapq.heappush(open_set, (0, start))
        came_from = {}
        g_score = defaultdict(lambda: float('inf'))
        g_score[start] = 0
        f_score = defaultdict(lambda: float('inf'))
        f_score[start] = self.heuristic(start, goal)
        
        while open_set:
            current_f, current = heapq.heappop(open_set)
            
            if current == goal:
                path = []
                while current in came_from:
                    path.append(current)
                    current = came_from[current]
                path.append(start)
                return (g_score[goal], path[::-1])
            
            for neighbor, cost in self.hospital[current].items():
                tentative_g = g_score[current] + cost
                if tentative_g < g_score[neighbor]:
                    came_from[neighbor] = current
                    g_score[neighbor] = tentative_g
                    f_score[neighbor] = tentative_g + self.heuristic(neighbor, goal)
                    heapq.heappush(open_set, (f_score[neighbor], neighbor))
        
        return (float('inf'), [])

    def heuristic(self, a, b):
        """Euclidean distance heuristic"""
        x1, y1 = self.room_positions[a]
        x2, y2 = self.room_positions[b]
        return math.sqrt((x2 - x1)**2 + (y2 - y1)**2)

    def find_optimal_path(self, start, targets):
        """Find optimal path using nearest neighbor approach"""
        if not targets:
            return [start]
            
        # Precompute all paths
        all_nodes = [start] + targets
        paths = {node: {} for node in all_nodes}
        for node in all_nodes:
            for other in all_nodes:
                if node != other:
                    paths[node][other] = self.a_star_search(node, other)[1]
        
        # Greedy algorithm
        path = [start]
        unvisited = set(targets)
        current = start
        
        while unvisited:
            nearest = min(unvisited, key=lambda x: len(paths[current][x]))
            path += paths[current][nearest][1:]  # Skip current node
            current = nearest
            unvisited.remove(nearest)
        
        # Return to start
        path += paths[current][start][1:]
        return path

if __name__ == "__main__":
    root = tk.Tk()
    app = HospitalDeliveryApp(root)
    root.mainloop()