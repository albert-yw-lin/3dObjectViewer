import tkinter as tk
from tkinter import filedialog
from dataclasses import dataclass
from typing import List, Tuple
import numpy as np

@dataclass
class Vertex:
    """Represents a vertex with ID and 3D coordinates"""
    id: int
    x: float
    y: float
    z: float

    def vertex_to_point(self) -> np.ndarray:
        return np.array([self.x, self.y, self.z])

@dataclass
class Face:
    """Represents a triangular face with three vertex IDs"""
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
        return normal / (np.linalg.norm(normal) + 1e-10)

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

class BaseRenderer:
    """Base renderer with common functionality"""
    def __init__(self, canvas: tk.Canvas):
        self.canvas = canvas
        self.scale = 100
    
    def calculate_bounding_box(self, obj: Object3D) -> Tuple[float, float, float, float]:
        """Calculate the bounding box of the object"""
        min_x = min_y = float('inf')
        max_x = max_y = float('-inf')
        
        for vertex in obj.vertices:
            point = np.array([vertex.x, vertex.y, vertex.z])
            min_x = min(min_x, point[0])
            max_x = max(max_x, point[0])
            min_y = min(min_y, point[1])
            max_y = max(max_y, point[1])
            
        return min_x, max_x, min_y, max_y
    
    def normalize_scale(self, obj: Object3D, target_ratio: float = 0.5) -> None:
        """Calculate scale factor to make object fill target ratio of window"""
        min_x, max_x, min_y, max_y = self.calculate_bounding_box(obj)
        
        canvas_width = self.canvas.winfo_width()
        canvas_height = self.canvas.winfo_height()
        
        obj_width = max_x - min_x
        obj_height = max_y - min_y
        
        if obj_width > 0 and obj_height > 0:
            scale_x = (canvas_width * target_ratio) / obj_width
            scale_y = (canvas_height * target_ratio) / obj_height
            self.scale = min(scale_x, scale_y)
    
    def project_point(self, point: np.ndarray) -> Tuple[float, float]:
        """Project 3D point to 2D screen coordinates"""
        screen_x = self.canvas.winfo_width() / 2 + point[0] * self.scale
        screen_y = self.canvas.winfo_height() / 2 - point[1] * self.scale
        return screen_x, screen_y

class Renderer2D(BaseRenderer):
    """2D orthographic renderer"""
    def render(self, obj: Object3D) -> None:
        """Render the 3D object to the canvas using 2D graphics"""
        self.normalize_scale(obj)
        self.canvas.delete("all")
        
        # Draw edges
        for face in obj.faces:
            for i in range(3):
                v1 = obj.vertices[face.vertex_ids[i] - 1]
                v2 = obj.vertices[face.vertex_ids[(i + 1) % 3] - 1]
                
                x1, y1 = self.project_point(v1.vertex_to_point())
                x2, y2 = self.project_point(v2.vertex_to_point())
                
                self.canvas.create_line(x1, y1, x2, y2, fill='blue', width=1)
        
        # Draw vertices
        for v in obj.vertices:
            x, y = self.project_point(v.vertex_to_point())
            self.canvas.create_oval(x-3, y-3, x+3, y+3, fill='blue')

class Application:
    """Main application class"""
    def __init__(self):
        self.root = tk.Tk()
        self.root.title("2d viewer")
        
        # Create canvas
        self.canvas = tk.Canvas(self.root, width=800, height=600, bg='white')
        self.canvas.pack(expand=True, fill='both')
        
        # Create menu
        menubar = tk.Menu(self.root)
        filemenu = tk.Menu(menubar, tearoff=0)
        filemenu.add_command(label="Open", command=self.load_file)
        menubar.add_cascade(label="File", menu=filemenu)
        self.root.config(menu=menubar)
        
        self.renderer = Renderer2D(self.canvas)
        self.object = None
    
    def load_file(self):
        """Load 3D object from a file"""
        filename = filedialog.askopenfilename(
            filetypes=[("Text Files", "*.txt"), ("All Files", "*.*")])
        if filename:
            self.object = Object3D()
            self.object.load_from_file(filename)
            self.renderer.render(self.object)
    
    def run(self):
        """Start the application"""
        self.root.mainloop()

if __name__ == "__main__":
    app = Application()
    app.run()