# 3dObjectViewer

This repository contains a 3D Object Viewer application developed in Python. It provides a visual representation of 3D objects from user-specified files in a wireframe and shaded format. The viewer supports interactive mouse-based rotation, allowing users to view the object from different angles.

## Table of Contents
1. [Overview](#overview)
2. [Requirements](#requirements)
3. [Environment](#environment)
4. [Usage](#usage)
5. [File Format](#file-format)
6. [Code Structure](#code-structure)

## Overview
This application reads 3D object data from a text file and displays the object in either a wireframe or shaded mode. The viewer enables users to interact with the object by clicking and dragging to rotate it about the X and Y axes, simulating a 3D perspective view.

## Requirements
- Libraries specified in `environment.yaml`

## Environment
   Create a virtual environment with the required dependencies.
   ```bash
   conda env create -f environment.yaml
   conda activate 3dObjectViewer
   ```

## Usage
To run the application in wireframe or shaded mode, use the following commands:

### For Wireframe Mode
```bash
python viewer_2d.py
```

### For Shaded Mode
```bash
python viewer_3d.py
```

After launching, specify the 3D object file by clicking File -> Open in the application’s menu. Select the .txt file containing the 3D object data to load the object for viewing.

## File Format
The 3D object file should be a comma-separated text file with the following structure:
- **First Line**: Two integers, the number of vertices and faces.
- **Vertices**: Each line contains a vertex ID and its coordinates `(x, y, z)`.
- **Faces**: Each line contains three vertex IDs defining a triangular face.

Example:
```
4, 4
0, 1.0, 0.0, 0.0
1, -1.0, 0.0, 0.0
2, 0.0, 1.0, 0.0
3, 0.0, -1.0, 0.0
0, 1, 2
0, 2, 3
1, 2, 3
0, 1, 3
```

## Code Structure
- **`viewer_2d.py`**: Implements the wireframe view of the 3D object.
- **`viewer_3d.py`**: Extends the 2D viewer with shading based on the angle of the surface with respect to the observer.
- **`environment.yaml`**: Defines the required Python packages for this project.