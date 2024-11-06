import tkinter as tk
from tkinter import filedialog
from dataclasses import dataclass
from typing import List, Tuple

@dataclass
class Vertex:
    """Represents a vertex with ID and 3D coordinates"""
    id: int
    x: float
    y: float
    z: float

@dataclass
class Face:
    """Represents a triangular face with three vertex IDs"""
    vertex_ids: Tuple[int, int, int]

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
    """Handles orthographic projection and 2D rendering"""
    def __init__(self, canvas: tk.Canvas):
        self.canvas = canvas
        self.scale = 100  # Scale factor for rendering
        
    def project_point(self, vertex: Vertex) -> Tuple[float, float]:
        """Project 3D point to 2D screen coordinates using orthographic projection
        X-axis points right, Y-axis points up, Z-axis points out of screen
        Origin is at center of window"""
        screen_x = self.canvas.winfo_width() / 2 + vertex.x * self.scale
        screen_y = self.canvas.winfo_height() / 2 - vertex.y * self.scale  # Negative because screen Y is inverted
        return screen_x, screen_y
    
    def render(self, obj: Object3D) -> None:
        """Render the 3D object to the canvas using 2D graphics"""
        self.canvas.delete("all")
        
        # Draw edges
        for face in obj.faces:
            for i in range(3):
                # Get vertices for this edge
                v1 = obj.vertices[face.vertex_ids[i] - 1]
                v2 = obj.vertices[face.vertex_ids[(i + 1) % 3] - 1]
                
                # Project vertices to 2D
                x1, y1 = self.project_point(v1)
                x2, y2 = self.project_point(v2)
                
                # Draw edge
                self.canvas.create_line(x1, y1, x2, y2, fill='blue', width=1)
        
        # Draw vertices as small filled circles
        for vertex in obj.vertices:
            x, y = self.project_point(vertex)
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
        
        self.renderer = Renderer(self.canvas)
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