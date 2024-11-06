import tkinter as tk
from tkinter import filedialog
import numpy as np
from dataclasses import dataclass
from typing import List, Tuple
import math
from viewer_2d import BaseRenderer, Object3D, Vertex, Face

class Renderer3D(BaseRenderer):
    """3D renderer with rotation and shading capabilities.

    Extends BaseRenderer to provide 3D visualization with interactive rotation
    and face shading based on orientation.

    Args:
        canvas (tk.Canvas): tkinter canvas widget for drawing
    """
    def __init__(self, canvas: tk.Canvas):
        super().__init__(canvas)
        self.rotation_x = 0
        self.rotation_y = 0
        self.last_x = 0
        self.last_y = 0
        
    def transform_point(self, point: np.ndarray) -> np.ndarray:
        """Apply rotation transformation to a 3D point.

        Args:
            point (np.ndarray): original 3D point coordinates

        Returns:
            np.ndarray: transformed 3D point coordinates
        """
        
        rx_matrix = np.array([
            [1.0, 0.0, 0.0],
            [0.0, np.cos(self.rotation_x), -np.sin(self.rotation_x)],
            [0.0, np.sin(self.rotation_x), np.cos(self.rotation_x)]
        ])
        
        ry_matrix = np.array([
            [np.cos(self.rotation_y), 0.0, np.sin(self.rotation_y)],
            [0.0, 1.0, 0.0],
            [-np.sin(self.rotation_y), 0.0, np.cos(self.rotation_y)]
        ])
        
        point = rx_matrix @ point
        point = ry_matrix @ point
        
        return point
    
    def project_point(self, point: np.ndarray) -> Tuple[float, float]:
        """Project 3D point to 2D screen coordinates with depth information.

        Args:
            point (np.ndarray): 3D point coordinates

        Returns:
            Tuple[float, float, float]: x, y screen coordinates and z depth value
        """
        screen_x = self.canvas.winfo_width() / 2 + point[0] * self.scale
        screen_y = self.canvas.winfo_height() / 2 - point[1] * self.scale
        
        return screen_x, screen_y, point[2]  # Return z for depth sorting
    
    def calculate_color(self, normal: np.ndarray) -> str:
        """Calculate face color based on angle with Z-axis.

        Args:
            normal (np.ndarray): face normal vector

        Returns:
            str: hex color code based on face orientation
        """
        # Calculate angle between normal and z-axis, which in this case is the abs z value of normal
        angle = np.arccos(abs(normal[2]))
        angle_deg = math.degrees(angle)
        
        # Interpolate between colors #00005F (on edge) and #0000FF (flat)
        intensity = 1 - (angle_deg / 90)  # 1 when flat, 0 when edge
        color_value = int(95 + intensity * 160)  # Interpolate between 95 (5F) and 255 (FF)
        
        return f'#{0:02x}{0:02x}{color_value:02x}'
    
    def render(self, obj: Object3D) -> None:
        """Render the 3D object with shaded faces and depth sorting.

        Implements the painter's algorithm for visibility and applies shading
        based on face orientation.

        Args:
            obj (Object3D): the 3D object to render
        """
        self.normalize_scale(obj, is_3d=True)
        self.canvas.delete("all")
        
        # Calculate and sort faces by depth
        face_data = []
        for face in obj.faces:
            # Get vertices of the face
            vertices = [obj.vertices[vid - 1] for vid in face.vertex_ids]
            
            # Calculate normal before rotation
            normal = face.calculate_normal(obj.vertices)

            # Transform vertices and normal
            transformed_vertices = [self.transform_point(v.vertex_to_point()) for v in vertices]
            transformed_normal = self.transform_point(normal)
            transformed_normal = transformed_normal / (np.linalg.norm(transformed_normal) + 1e-10) # add a small value to prevent zero devision error

            # Project vertices
            projected_vertices = [self.project_point(v) for v in transformed_vertices]
            
            # Calculate center point for depth sorting
            center_z = sum(v[2] for v in transformed_vertices) / 3
            
            color = self.calculate_color(transformed_normal)
            
            face_data.append((
                center_z,  # Use rotated center Z for depth sorting
                projected_vertices,
                color
            ))
            
        # Sort faces by depth (painter's algorithm) - furthest first
        face_data.sort(key=lambda x: x[0])  #sort in ascending order
        
        # Draw faces from back to front
        for _, vertices, color in face_data:
            points = [(v[0], v[1]) for v in vertices]
            # Only draw if we have valid points
            self.canvas.create_polygon(points, fill=color, outline='blue')
        
        # Draw vertices
        for v in obj.vertices:
            point = self.transform_point(v.vertex_to_point())
            x, y, _ = self.project_point(point)
            # Only draw if we have valid coordinates
            if not math.isnan(x) and not math.isnan(y):
                self.canvas.create_oval(x-3, y-3, x+3, y+3, fill='blue')

    def start_drag(self, event):
        """Record the starting position of a drag operation.

        Args:
            event: tkinter mouse event
        """
        self.last_x = event.x
        self.last_y = event.y
    
    def drag(self, event, obj: Object3D):
        """Handle mouse drag for rotation.

        Updates rotation angles based on mouse movement and rerenders the object.

        Args:
            event: tkinter mouse event
            obj (Object3D): the 3D object to rotate and render
        """
        dx = event.x - self.last_x
        dy = event.y - self.last_y
        
        self.rotation_y += dx * 0.01
        self.rotation_x += dy * 0.01
        
        self.last_x = event.x
        self.last_y = event.y
        
        self.render(obj)

class Application:
    """Main application class"""
    def __init__(self):
        self.root = tk.Tk()
        self.root.title("3D Shaded Viewer")
        
        self.canvas = tk.Canvas(self.root, width=800, height=600, bg='white')
        self.canvas.pack(expand=True, fill='both')
        
        menubar = tk.Menu(self.root)
        filemenu = tk.Menu(menubar, tearoff=0)
        filemenu.add_command(label="Open", command=self.load_file)
        menubar.add_cascade(label="File", menu=filemenu)
        self.root.config(menu=menubar)
        
        self.renderer = Renderer3D(self.canvas)
        self.object = None
        
        self.canvas.bind("<Button-1>", self.renderer.start_drag)
        self.canvas.bind("<Button-1>", self.renderer.start_drag)
        self.canvas.bind("<B1-Motion>", self.handle_drag)
    
    def load_file(self):
        """Load 3D object from a file"""
        filename = filedialog.askopenfilename(
            filetypes=[("Text Files", "*.txt"), ("All Files", "*.*")])
        if filename:
            self.object = Object3D()
            self.object.load_from_file(filename)
            self.renderer.render(self.object)
    
    def handle_drag(self, event):
        """Handle mouse drag events for object rotation.

        Args:
            event: tkinter mouse event
        """
        if self.object:
            self.renderer.drag(event, self.object)
    
    def run(self):
        """Start the application"""
        self.root.mainloop()

if __name__ == "__main__":
    app = Application()
    app.run()