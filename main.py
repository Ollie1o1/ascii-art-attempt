#!/usr/bin/env python3
import math
import time
import threading
import tkinter as tk
from tkinter import font
import sys

class SpinningCube:
    def __init__(self, size=30):
        self.size = size
        self.angle_x = 0
        self.angle_y = 0
        self.angle_z = 0
        self.running = True
        
        # Define cube vertices (8 corners of a cube)
        self.vertices = [
            [-1, -1, -1], [1, -1, -1], [1, 1, -1], [-1, 1, -1],  # Back face
            [-1, -1, 1], [1, -1, 1], [1, 1, 1], [-1, 1, 1]       # Front face
        ]
        
        # Define cube edges (which vertices connect)
        self.edges = [
            [0, 1], [1, 2], [2, 3], [3, 0],  # Back face
            [4, 5], [5, 6], [6, 7], [7, 4],  # Front face
            [0, 4], [1, 5], [2, 6], [3, 7]   # Connecting edges
        ]
        
    def update_size(self, new_size):
        """Update cube size dynamically"""
        self.size = new_size
        
    def rotate_point(self, point, angle_x, angle_y, angle_z):
        """Rotate a 3D point around x, y, and z axes"""
        x, y, z = point
        
        # Rotate around X axis
        cos_x, sin_x = math.cos(angle_x), math.sin(angle_x)
        y, z = y * cos_x - z * sin_x, y * sin_x + z * cos_x
        
        # Rotate around Y axis
        cos_y, sin_y = math.cos(angle_y), math.sin(angle_y)
        x, z = x * cos_y + z * sin_y, -x * sin_y + z * cos_y
        
        # Rotate around Z axis
        cos_z, sin_z = math.cos(angle_z), math.sin(angle_z)
        x, y = x * cos_z - y * sin_z, x * sin_z + y * cos_z
        
        return [x, y, z]
    
    def project_3d_to_2d(self, point):
        """Project 3D point to 2D screen coordinates"""
        x, y, z = point
        # Simple perspective projection
        distance = 5
        factor = distance / (distance + z)
        screen_x = int(x * factor * self.size)
        screen_y = int(y * factor * self.size)
        return screen_x, screen_y
    
    def draw_line(self, canvas, x1, y1, x2, y2, char='*'):
        """Draw a line on the canvas using Bresenham's algorithm"""
        dx = abs(x2 - x1)
        dy = abs(y2 - y1)
        x, y = x1, y1
        sx = 1 if x1 < x2 else -1
        sy = 1 if y1 < y2 else -1
        
        if dx > dy:
            err = dx / 2.0
            while x != x2:
                if 0 <= y < len(canvas) and 0 <= x < len(canvas[0]):
                    canvas[y][x] = char
                err -= dy
                if err < 0:
                    y += sy
                    err += dx
                x += sx
        else:
            err = dy / 2.0
            while y != y2:
                if 0 <= y < len(canvas) and 0 <= x < len(canvas[0]):
                    canvas[y][x] = char
                err -= dx
                if err < 0:
                    x += sx
                    err += dy
                y += sy
        
        # Draw end point
        if 0 <= y2 < len(canvas) and 0 <= x2 < len(canvas[0]):
            canvas[y2][x2] = char
    
    def render_frame(self, canvas_width, canvas_height):
        """Render one frame of the spinning cube with dynamic centering"""
        # Create canvas based on provided dimensions
        canvas = [[' ' for _ in range(canvas_width)] for _ in range(canvas_height)]
        
        # Calculate center offset for centering the cube
        center_x = canvas_width // 2
        center_y = canvas_height // 2
        
        # Rotate and project vertices
        projected_vertices = []
        for vertex in self.vertices:
            rotated = self.rotate_point(vertex, self.angle_x, self.angle_y, self.angle_z)
            projected = self.project_3d_to_2d(rotated)
            # Center the projected coordinates
            centered_x = projected[0] + center_x
            centered_y = projected[1] + center_y
            projected_vertices.append((centered_x, centered_y))
        
        # Draw edges
        for edge in self.edges:
            start, end = edge
            x1, y1 = projected_vertices[start]
            x2, y2 = projected_vertices[end]
            
            # Choose character based on edge orientation for visual effect
            if start < 4 and end < 4:  # Back face
                char = '·'
            elif start >= 4 and end >= 4:  # Front face
                char = '█'
            else:  # Connecting edges
                char = '▓'
            
            self.draw_line(canvas, x1, y1, x2, y2, char)
        
        # Draw vertices as points
        for i, (x, y) in enumerate(projected_vertices):
            if 0 <= y < len(canvas) and 0 <= x < len(canvas[0]):
                canvas[y][x] = '●' if i >= 4 else '○'
        
        return canvas
    
    def stop(self):
        """Stop the animation"""
        self.running = False

class ModernTerminalWindow:
    def __init__(self):
        self.root = tk.Tk()
        self.root.title("3D ASCII Spinning Cube • Modern Terminal")
        
        # Modern color scheme
        self.colors = {
            'bg': '#1a1a1a',          # Dark charcoal background
            'header_bg': '#2d2d2d',    # Slightly lighter for headers
            'cube_bg': '#161616',      # Darker for cube area
            'footer_bg': '#2d2d2d',    # Match header
            'text': '#e0e0e0',        # Light gray text
            'accent': '#4a9eff',      # Blue accent
            'cube_text': '#b8b8b8',   # Gray cube text
            'border': '#404040'        # Border color
        }
        
        self.root.configure(bg=self.colors['bg'])
        self.root.geometry("1200x800")
        self.root.resizable(True, True)
        
        # Fonts
        self.header_font = font.Font(family="Segoe UI", size=12, weight="bold")
        self.info_font = font.Font(family="Segoe UI", size=10)
        self.cube_font = font.Font(family="Courier New", size=9, weight="normal")
        
        # Create main container
        self.main_frame = tk.Frame(self.root, bg=self.colors['bg'])
        self.main_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        # Create header section
        self.create_header()
        
        # Create cube display area
        self.create_cube_area()
        
        # Create footer section
        self.create_footer()
        
        # Create the spinning cube
        self.cube = SpinningCube(size=20)
        
        # Animation variables
        self.animation_thread = None
        self.current_width = 0
        self.current_height = 0
        self.frame_count = 0
        self.start_time = time.time()
        
        # Bind window resize events
        self.root.bind('<Configure>', self.on_window_resize)
        
        # Handle window closing
        self.root.protocol("WM_DELETE_WINDOW", self.on_closing)
        
        # Start animation
        self.start_animation()
    
    def create_header(self):
        """Create the header section"""
        self.header_frame = tk.Frame(self.main_frame, bg=self.colors['header_bg'], relief=tk.RAISED, bd=1)
        self.header_frame.pack(fill=tk.X, pady=(0, 5))
        
        # Title
        self.title_label = tk.Label(
            self.header_frame, 
            text="🎲 3D ASCII SPINNING CUBE",
            font=self.header_font,
            bg=self.colors['header_bg'],
            fg=self.colors['accent'],
            pady=10
        )
        self.title_label.pack()
        
        # Info row
        self.info_frame = tk.Frame(self.header_frame, bg=self.colors['header_bg'])
        self.info_frame.pack(fill=tk.X, padx=20, pady=(0, 10))
        
        # Left info
        self.left_info = tk.Label(
            self.info_frame,
            text="Initializing...",
            font=self.info_font,
            bg=self.colors['header_bg'],
            fg=self.colors['text'],
            anchor=tk.W
        )
        self.left_info.pack(side=tk.LEFT, fill=tk.X, expand=True)
        
        # Right info
        self.right_info = tk.Label(
            self.info_frame,
            text="Ready",
            font=self.info_font,
            bg=self.colors['header_bg'],
            fg=self.colors['text'],
            anchor=tk.E
        )
        self.right_info.pack(side=tk.RIGHT, fill=tk.X, expand=True)
    
    def create_cube_area(self):
        """Create the cube display area"""
        self.cube_frame = tk.Frame(self.main_frame, bg=self.colors['cube_bg'], relief=tk.SUNKEN, bd=2)
        self.cube_frame.pack(fill=tk.BOTH, expand=True, pady=5)
        
        # Cube display text widget
        self.cube_display = tk.Text(
            self.cube_frame,
            bg=self.colors['cube_bg'],
            fg=self.colors['cube_text'],
            font=self.cube_font,
            insertbackground=self.colors['cube_text'],
            selectbackground=self.colors['border'],
            selectforeground=self.colors['text'],
            wrap=tk.NONE,
            state=tk.DISABLED,
            relief=tk.FLAT,
            bd=0
        )
        
        # Scrollbars for cube area
        self.v_scrollbar = tk.Scrollbar(self.cube_frame, orient=tk.VERTICAL, command=self.cube_display.yview)
        self.h_scrollbar = tk.Scrollbar(self.cube_frame, orient=tk.HORIZONTAL, command=self.cube_display.xview)
        
        self.cube_display.configure(yscrollcommand=self.v_scrollbar.set, xscrollcommand=self.h_scrollbar.set)
        
        # Pack scrollbars and display
        self.v_scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        self.h_scrollbar.pack(side=tk.BOTTOM, fill=tk.X)
        self.cube_display.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
    
    def create_footer(self):
        """Create the footer section"""
        self.footer_frame = tk.Frame(self.main_frame, bg=self.colors['footer_bg'], relief=tk.RAISED, bd=1)
        self.footer_frame.pack(fill=tk.X, pady=(5, 0))
        
        # Rotation info
        self.rotation_label = tk.Label(
            self.footer_frame,
            text="Rotation: X=0.00, Y=0.00, Z=0.00",
            font=self.info_font,
            bg=self.colors['footer_bg'],
            fg=self.colors['text'],
            pady=8
        )
        self.rotation_label.pack()
        
        # Status row
        self.status_frame = tk.Frame(self.footer_frame, bg=self.colors['footer_bg'])
        self.status_frame.pack(fill=tk.X, padx=20, pady=(0, 8))
        
        # Status left
        self.status_left = tk.Label(
            self.status_frame,
            text="Status: Running • Animation: Active",
            font=self.info_font,
            bg=self.colors['footer_bg'],
            fg=self.colors['accent'],
            anchor=tk.W
        )
        self.status_left.pack(side=tk.LEFT, fill=tk.X, expand=True)
        
        # Status right
        self.status_right = tk.Label(
            self.status_frame,
            text="Resize window to adjust cube size",
            font=self.info_font,
            bg=self.colors['footer_bg'],
            fg=self.colors['text'],
            anchor=tk.E
        )
        self.status_right.pack(side=tk.RIGHT, fill=tk.X, expand=True)
    
    def on_window_resize(self, event):
        """Handle window resize events"""
        if event.widget == self.root:
            self.update_dimensions()
    
    def update_dimensions(self):
        """Update canvas dimensions based on window size"""
        self.cube_display.update_idletasks()
        
        # Calculate character dimensions
        char_width = self.cube_font.measure('M')
        char_height = self.cube_font.metrics('linespace')
        
        # Get cube display area dimensions
        widget_width = self.cube_display.winfo_width()
        widget_height = self.cube_display.winfo_height()
        
        if widget_width > 0 and widget_height > 0:
            self.current_width = max(40, widget_width // char_width)
            self.current_height = max(20, widget_height // char_height)
            
            # Calculate optimal cube size
            available_space = min(self.current_width, self.current_height)
            optimal_size = max(10, min(35, available_space // 3))
            
            self.cube.update_size(optimal_size)
    
    def update_cube_display(self, canvas):
        """Update the cube display area"""
        self.cube_display.config(state=tk.NORMAL)
        self.cube_display.delete(1.0, tk.END)
        
        # Convert canvas to string
        cube_text = '\n'.join(''.join(row) for row in canvas)
        self.cube_display.insert(tk.END, cube_text)
        
        self.cube_display.config(state=tk.DISABLED)
    
    def update_header_info(self):
        """Update header information"""
        elapsed = time.time() - self.start_time
        
        left_text = f"Window: {self.current_width}×{self.current_height} • Cube Size: {self.cube.size} • Frame: {self.frame_count}"
        right_text = f"Runtime: {elapsed:.1f}s • FPS: 24"
        
        self.left_info.config(text=left_text)
        self.right_info.config(text=right_text)
    
    def update_footer_info(self):
        """Update footer information"""
        rotation_text = f"Rotation: X={self.cube.angle_x:.2f}, Y={self.cube.angle_y:.2f}, Z={self.cube.angle_z:.2f}"
        self.rotation_label.config(text=rotation_text)
    
    def animate_cube(self):
        """Animation loop for the spinning cube"""
        fps = 24
        frame_delay = 1.0 / fps
        
        # Initial setup
        self.root.after(100, self.update_dimensions)
        
        while self.cube.running:
            try:
                if self.current_width <= 0 or self.current_height <= 0:
                    time.sleep(0.1)
                    continue
                
                # Render cube frame
                canvas = self.cube.render_frame(self.current_width, self.current_height)
                
                # Update displays
                self.root.after(0, lambda: self.update_cube_display(canvas))
                self.root.after(0, self.update_header_info)
                self.root.after(0, self.update_footer_info)
                
                # Update rotation angles
                self.cube.angle_x += 0.05
                self.cube.angle_y += 0.07
                self.cube.angle_z += 0.03
                
                # Normalize angles
                self.cube.angle_x %= 2 * math.pi
                self.cube.angle_y %= 2 * math.pi
                self.cube.angle_z %= 2 * math.pi
                
                self.frame_count += 1
                time.sleep(frame_delay)
                
            except Exception as e:
                print(f"Animation error: {e}")
                break
    
    def start_animation(self):
        """Start the animation in a separate thread"""
        self.animation_thread = threading.Thread(target=self.animate_cube, daemon=True)
        self.animation_thread.start()
    
    def on_closing(self):
        """Handle window closing"""
        self.cube.stop()
        self.root.quit()
        self.root.destroy()
    
    def run(self):
        """Start the terminal window"""
        self.root.mainloop()

def main():
    """Main function to create and run the terminal window"""
    try:
        print("🎲 Starting Modern 3D ASCII Spinning Cube Interface...")
        print("Opening minimalistic terminal window...")
        print("Features: Responsive sizing, dedicated sections, modern UI")
        print("Close the window to exit.")
        
        terminal = ModernTerminalWindow()
        terminal.run()
        
    except KeyboardInterrupt:
        print("\n🎲 Animation stopped by user.")
        sys.exit(0)
    except Exception as e:
        print(f"Error: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()
