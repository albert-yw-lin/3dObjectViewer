import tkinter as tk
from tkinter import filedialog
import numpy as np
from dataclasses import dataclass
from typing import List, Tuple
import math

@dataclass
class Vertex:
    id: int
    x: float
    y: float
    z: float

@dataclass
class Face:
    vertex_ids: Tuple[int, int, int]
    
    def calculate_normal(self, vertices: List[Vertex]) -> np.ndarray:
        """Calculate the normal vector of the face"""
        v1 = vertices[self.vertex_ids[0] - 1]
        v2 = vertices[self.vertex_ids[1] - 1]
        v3 = vertices[self.vertex_ids[2] - 1]
        
        # Create vectors from vertices
        vec1 = np.array([v2.x - v1.x, v2.y - v1.y, v2.z - v1.z])
        vec2 = np.array([v3.x - v1.x, v3.y - v1.y, v3.z - v1.z])
        
        # Calculate cross product
        normal = np.cross(vec1, vec2)
        
        # Normalize
        return normal / (np.linalg.norm(normal)+1e-10)

class Object3D:
    """Represents a 3D object with vertices and faces"""
    def __init__(self):
        self.vertices: List[Vertex] = []
        self.faces: List[Face] = []
        
    def load_from_file(self, filename: str) -> None:
        """Load 3D object data from a formatted text file"""
        with open(filename, 'r') as f:
            # Read number of vertices and faces
            num_vertices, num_faces = map(int, f.readline().strip().split(','))
            
            # Read vertices
            for _ in range(num_vertices):
                vid, x, y, z = map(float, f.readline().strip().split(','))
                self.vertices.append(Vertex(int(vid), x, y, z))
                
            # Read faces
            for _ in range(num_faces):
                v1, v2, v3 = map(int, f.readline().strip().split(','))
                self.faces.append(Face((v1, v2, v3)))

class Renderer:
    """Handles 3D to 2D projection and rendering with shading"""
    def __init__(self, canvas: tk.Canvas):
        self.canvas = canvas
        self.rotation_x = 0
        self.rotation_y = 0
        self.scale = 100
        self.last_x = 0
        self.last_y = 0
        
    def rotate_point(self, point: np.ndarray) -> np.ndarray:
        """Apply rotation transformations to a point"""
        # Ensure point is a numpy array
        point = np.array(point, dtype=float)
        
        # Create rotation matrices with better numerical stability
        rx_matrix = np.array([
            [1.0, 0.0, 0.0],
            [0.0, np.cos(self.rotation_x), -np.sin(self.rotation_x)],
            [0.0, np.sin(self.rotation_x), np.cos(self.rotation_x)]
        ], dtype=float)
        
        ry_matrix = np.array([
            [np.cos(self.rotation_y), 0.0, np.sin(self.rotation_y)],
            [0.0, 1.0, 0.0],
            [-np.sin(self.rotation_y), 0.0, np.cos(self.rotation_y)]
        ], dtype=float)
        
        # Apply rotations with better precision
        point = rx_matrix @ point
        point = ry_matrix @ point
        
        return point
    
    def rotate_normal(self, normal: np.ndarray) -> np.ndarray:
        """Rotate a normal vector using the same transformation as points"""
        rotated = self.rotate_point(normal)
        # Ensure normal stays normalized after rotation
        return rotated / (np.linalg.norm(rotated)+1e-10)
    
    def project_point(self, x: float, y: float, z: float) -> Tuple[float, float]:
        """Project 3D point to 2D screen coordinates"""
        point = np.array([x, y, z])
        point = self.rotate_point(point)
        
        screen_x = self.canvas.winfo_width() / 2 + point[0] * self.scale
        screen_y = self.canvas.winfo_height() / 2 - point[1] * self.scale
        
        return screen_x, screen_y, point[2]  # Return z for depth sorting
    
    def calculate_color(self, normal: np.ndarray) -> str:
        """Calculate face color based on angle with Z-axis"""
        # Calculate angle between normal and z-axis, which in this case is the abs z value of normal
        angle = np.arccos(abs(normal[2]))
        
        # Convert angle to degrees
        angle_deg = math.degrees(angle)
        
        # Interpolate between colors #00005F (on edge) and #0000FF (flat)
        intensity = 1 - (angle_deg / 90)  # 1 when flat, 0 when edge
        color_value = int(95 + intensity * 160)  # Interpolate between 95 (5F) and 255 (FF)
        
        return f'#{0:02x}{0:02x}{color_value:02x}'
    
    def render(self, obj: Object3D) -> None:
        """Render the 3D object with shaded faces"""
        self.canvas.delete("all")
        
        # Calculate and sort faces by depth
        face_data = []
        for face in obj.faces:
            # Get vertices of the face
            vertices = [obj.vertices[vid - 1] for vid in face.vertex_ids]
            
            # Calculate normal before rotation
            normal = face.calculate_normal(obj.vertices)

            # Rotate the normal
            rotated_normal = self.rotate_normal(normal)
            
            # Project vertices
            projected_vertices = [self.project_point(v.x, v.y, v.z) for v in vertices]
            
            # Calculate center point for depth sorting
            center_z = sum(v[2] for v in projected_vertices) / 3
            
            color = self.calculate_color(rotated_normal)
            
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
        for vertex in obj.vertices:
            x, y, _ = self.project_point(vertex.x, vertex.y, vertex.z)
            # Only draw if we have valid coordinates
            if not math.isnan(x) and not math.isnan(y):
                self.canvas.create_oval(x-3, y-3, x+3, y+3, fill='blue')

    def start_drag(self, event):
        """Record the starting position of a drag operation"""
        self.last_x = event.x
        self.last_y = event.y
    
    def drag(self, event, obj: Object3D):
        """Handle mouse drag for rotation"""
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
        
        self.renderer = Renderer(self.canvas)
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
        """Handle mouse drag events"""
        if self.object:
            self.renderer.drag(event, self.object)
    
    def run(self):
        """Start the application"""
        self.root.mainloop()

if __name__ == "__main__":
    app = Application()
    app.run()