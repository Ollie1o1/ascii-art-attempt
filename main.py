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

class TerminalWindow:
    def __init__(self):
        self.root = tk.Tk()
        self.root.title("3D ASCII Spinning Cube Terminal")
        self.root.configure(bg='black')
        self.root.geometry("1000x700")
        
        # Set window icon and make it resizable
        self.root.resizable(True, True)
        
        # Create text widget that looks like a terminal
        self.terminal_font = font.Font(family="Courier", size=9, weight="normal")
        
        # Create frame for the text widget and scrollbar
        self.frame = tk.Frame(self.root, bg='black')
        self.frame.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)
        
        # Create text widget
        self.text_widget = tk.Text(
            self.frame,
            bg='black',
            fg='#00ff00',  # Green text like classic terminals
            font=self.terminal_font,
            insertbackground='#00ff00',
            selectbackground='#333333',
            selectforeground='#00ff00',
            wrap=tk.NONE,
            state=tk.DISABLED
        )
        
        # Create scrollbar
        self.scrollbar = tk.Scrollbar(self.frame, orient=tk.VERTICAL, command=self.text_widget.yview)
        self.text_widget.configure(yscrollcommand=self.scrollbar.set)
        
        # Pack scrollbar and text widget
        self.scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        self.text_widget.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        
        # Create the spinning cube
        self.cube = SpinningCube(size=20)
        
        # Animation thread
        self.animation_thread = None
        
        # Window dimensions tracking
        self.current_width = 0
        self.current_height = 0
        
        # Bind window resize events
        self.root.bind('<Configure>', self.on_window_resize)
        
        # Handle window closing
        self.root.protocol("WM_DELETE_WINDOW", self.on_closing)
        
        # Start animation
        self.start_animation()
    
    def on_window_resize(self, event):
        """Handle window resize events"""
        # Only respond to the root window resize, not child widgets
        if event.widget == self.root:
            self.update_dimensions()
    
    def update_dimensions(self):
        """Update canvas dimensions based on window size"""
        # Get text widget dimensions
        self.text_widget.update_idletasks()
        
        # Calculate character dimensions based on font
        char_width = self.terminal_font.measure('M')
        char_height = self.terminal_font.metrics('linespace')
        
        # Get widget pixel dimensions
        widget_width = self.text_widget.winfo_width()
        widget_height = self.text_widget.winfo_height()
        
        # Calculate how many characters can fit
        if widget_width > 0 and widget_height > 0:
            self.current_width = max(40, widget_width // char_width - 2)
            self.current_height = max(20, widget_height // char_height - 8)  # Reserve space for headers
            
            # Calculate optimal cube size based on available space
            # Use 25% of the smaller dimension for cube size
            available_space = min(self.current_width, self.current_height)
            optimal_size = max(8, min(30, available_space // 4))
            
            # Update cube size
            self.cube.update_size(optimal_size)
    
    def update_display(self, content):
        """Update the terminal display with new content"""
        self.text_widget.config(state=tk.NORMAL)
        self.text_widget.delete(1.0, tk.END)
        self.text_widget.insert(tk.END, content)
        self.text_widget.config(state=tk.DISABLED)
        
        # Auto-scroll to bottom
        self.text_widget.see(tk.END)
    
    def animate_cube(self):
        """Animation loop for the spinning cube"""
        fps = 24
        frame_delay = 1.0 / fps
        frame_count = 0
        start_time = time.time()
        
        # Initial dimension setup
        self.root.after(100, self.update_dimensions)
        
        while self.cube.running:
            try:
                # Ensure we have valid dimensions
                if self.current_width <= 0 or self.current_height <= 0:
                    time.sleep(0.1)
                    continue
                
                # Calculate canvas dimensions for the cube area
                header_lines = 6
                footer_lines = 5
                available_height = max(10, self.current_height - header_lines - footer_lines)
                canvas_width = self.current_width
                canvas_height = available_height
                
                # Render frame
                canvas = self.cube.render_frame(canvas_width, canvas_height)
                
                # Create display content
                current_time = time.time()
                elapsed = current_time - start_time
                
                # Create header
                header_line = "=" * min(80, self.current_width)
                title_line = "🎲 3D ASCII SPINNING CUBE TERMINAL 🎲".center(len(header_line))
                
                content = []
                content.append(header_line)
                content.append(title_line)
                content.append(header_line)
                content.append(f"Window: {self.current_width}x{self.current_height} | Cube Size: {self.cube.size} | FPS: {fps} | Frame: {frame_count}")
                content.append(f"Runtime: {elapsed:.1f}s | Resize window to adjust cube size")
                content.append(header_line)
                
                # Add canvas
                for row in canvas:
                    content.append(''.join(row))
                
                # Add footer
                content.append(header_line)
                content.append(f"Rotation: X={self.cube.angle_x:.2f}, Y={self.cube.angle_y:.2f}, Z={self.cube.angle_z:.2f}")
                content.append("Status: Running | Animation: Active | Responsive: Enabled")
                content.append("Resize this window to see the cube adapt to different sizes!")
                content.append(header_line)
                
                # Update display
                display_text = '\n'.join(content)
                self.root.after(0, lambda: self.update_display(display_text))
                
                # Update rotation angles
                self.cube.angle_x += 0.05
                self.cube.angle_y += 0.07
                self.cube.angle_z += 0.03
                
                # Keep angles in reasonable range
                if self.cube.angle_x > 2 * math.pi:
                    self.cube.angle_x -= 2 * math.pi
                if self.cube.angle_y > 2 * math.pi:
                    self.cube.angle_y -= 2 * math.pi
                if self.cube.angle_z > 2 * math.pi:
                    self.cube.angle_z -= 2 * math.pi
                
                frame_count += 1
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
        # Show startup message
        startup_msg = """
====================================================================
              🎲 3D ASCII SPINNING CUBE TERMINAL 🎲
====================================================================
Initializing responsive terminal interface...
Loading adaptive 3D cube renderer...
Setting up dynamic sizing system...
Configuring auto-centering algorithms...

🔄 Responsive Features:
• Cube automatically resizes with window
• Always centered in the display area
• Optimal size calculated dynamically
• Real-time dimension tracking

Try resizing this window to see the cube adapt!
Animation will begin shortly...
====================================================================
        """
        self.update_display(startup_msg)
        
        # Start the tkinter main loop
        self.root.mainloop()

def main():
    """Main function to create and run the terminal window"""
    try:
        print("🎲 Starting Responsive 3D ASCII Spinning Cube Terminal...")
        print("A separate resizable window will open shortly.")
        print("Try resizing the window to see the cube adapt!")
        print("Close the window to exit the animation.")
        
        # Create and run the terminal window
        terminal = TerminalWindow()
        terminal.run()
        
    except KeyboardInterrupt:
        print("\n🎲 Animation stopped by user.")
        sys.exit(0)
    except Exception as e:
        print(f"Error: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()