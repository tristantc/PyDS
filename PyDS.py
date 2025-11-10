class PyDS:
    def __init__(self, filename: str, Npoints: int, **kwargs):
        import numpy as np
        
        # Load defaults and override with user-provided kwargs
        self.defaults(**kwargs)
        kwargs = {**self.defKwargs, **kwargs}
        self.points = np.linspace(0, 1, Npoints)
        
        # Load the SVG file and process contents
        self.load(filename)
        self.find_rect() # Find the reference rectangle
        self.find_plots() # Find the plot paths
    
    def load(self, filename):
        # Load paths and attributes from SVG
        self.paths, self.attributes = self.svg(filename)
    
    def find_plots(self):
        # Identify all 'path' type elements in the SVG
        for i, attr in enumerate(self.attributes):
            if attr['id'][:4].lower() == 'path':
                self.path_i.append(i)
        
        # Convert SVG path coordinates to plot coordinates
        for path_idx, i in enumerate(self.path_i):
            # Determine which rectangle this path uses
            rect_id = None
            if path_idx in self.path_params:
                rect_id = self.path_params[path_idx].get('rect_id', None)
            
            # Get the transform for this rectangle (or use default)
            if rect_id and rect_id in self.rect_transforms:
                transform = self.rect_transforms[rect_id]
                kx = transform['kx']
                x_origin = transform['x_origin']
                h_box = transform['h_box']
                y_origin_base = transform['y_origin']
            else:
                # Use default rectangle
                kx = self.kx
                x_origin = self.x_origin
                h_box = self.h_box
                y_origin_base = self.y_origin
            
            # Get per-path parameters (y_start and height) or use defaults
            if path_idx in self.path_params:
                path_y_start = self.path_params[path_idx].get('y', self.y_start)
                path_height = self.path_params[path_idx].get('height', self.or_height)
            else:
                path_y_start = self.y_start
                path_height = self.or_height
            
            # Calculate per-path scaling factor for y-axis
            path_ky = path_height / h_box
            path_y_origin = y_origin_base
            
            # Handle multi-segment paths by concatenating all segments
            path_obj = self.paths[i]
            
            # Calculate total length of all segments
            total_length = sum(seg.length() for seg in path_obj)
            
            # Sample points proportionally across all segments
            x_coords = []
            y_coords = []
            
            for t in self.points:
                # Find which segment this t value corresponds to
                target_length = t * total_length
                cumulative_length = 0
                
                for seg in path_obj:
                    seg_length = seg.length()
                    if cumulative_length + seg_length >= target_length:
                        # This segment contains our point
                        local_t = (target_length - cumulative_length) / seg_length if seg_length > 0 else 0
                        local_t = max(0, min(1, local_t))  # Clamp to [0, 1]
                        point = seg.point(local_t)
                        
                        # Apply coordinate transformation using this path's rectangle
                        x_coords.append(kx * (point.real - x_origin))
                        y_coords.append(path_ky * (h_box - point.imag + path_y_origin))
                        break
                    cumulative_length += seg_length
            
            self.line['x'].append(x_coords)
            self.line['y'].append(y_coords)
        
    def plot(self, N, **kwargs):
        import matplotlib.pyplot as plt
        if 'label' in kwargs:
            plt.plot(self.line['x'][N], self.line['y'][N], label=kwargs['label'], marker='o')
        else:
            plt.plot(self.line['x'][N], self.line['y'][N])
    
    def plot_all(self, **kwargs):
        import matplotlib.pyplot as plt
        if 'labels' in kwargs:
            labels = kwargs['labels']
        else:
            labels = [f'Plot {i}' for i in self.path_i]
        
        for i, label in zip(self.path_i, labels):
            self.plot(i, label=label)
            plt.legend()
        
    def find_rect(self):
        # Find ALL rectangles in the SVG and store their transformations
        rect_indices = []
        rect_ids = []
        
        for i, attr in enumerate(self.attributes):
            if attr['id'][:4].lower() == 'rect':
                rect_indices.append(i)
                rect_ids.append(attr['id'])
        
        # Use first rect as default
        if rect_indices:
            self.rect_i = rect_indices[0]
        
        # Process each rectangle
        for idx, rect_id in zip(rect_indices, rect_ids):
            self.rect_map[rect_id] = idx
            
            # Get rectangle-specific parameters if defined
            if rect_id in self.rect_params:
                x_start = self.rect_params[rect_id].get('x', self.x_start)
                y_start = self.rect_params[rect_id].get('y', self.y_start)
                width = self.rect_params[rect_id].get('width', self.or_width)
                height = self.rect_params[rect_id].get('height', self.or_height)
            else:
                # Use defaults
                x_start = self.x_start
                y_start = self.y_start
                width = self.or_width
                height = self.or_height
            
            # Extract bounding box coordinates
            w_box = self.paths[idx][0].point(1).real - self.paths[idx][0].point(0).real
            h_box = self.paths[idx][1].point(1).imag - self.paths[idx][1].point(0).imag
            
            # Scaling factors
            kx = width / w_box
            ky = height / h_box
            
            # Origins
            x_origin = self.paths[idx][0].point(0).real - x_start / kx
            y_origin = self.paths[idx][1].point(0).imag + y_start / ky
            
            # Store transformation
            self.rect_transforms[rect_id] = {
                'kx': kx,
                'ky': ky,
                'x_origin': x_origin,
                'y_origin': y_origin,
                'w_box': w_box,
                'h_box': h_box
            }
        
        # Set default transforms from first rectangle for backward compatibility
        if rect_ids:
            default_transform = self.rect_transforms[rect_ids[0]]
            self.kx = default_transform['kx']
            self.ky = default_transform['ky']
            self.x_origin = default_transform['x_origin']
            self.y_origin = default_transform['y_origin']
            self.w_box = default_transform['w_box']
            self.h_box = default_transform['h_box']
            
            # For completeness
            self.x_box = self.x_origin
            self.y_box = self.h_box
    
    def defaults(self, **kwargs):
        # Load libraries
        from svgpathtools import svg2paths, wsvg
        import xml.etree.ElementTree as ET
        
        self.ET = ET
        self.svg = svg2paths
        self.wsvg = wsvg
        
        # Default plotting parameters
        self.defKwargs = {    'width': 50,    'height': 50,    'Nplots': 1,    'x': 0,    'y': 0,    'path_params': None,    'rect_params': None    }
        
        # Combine defaults with user kwargs
        kwargs = {**self.defKwargs, **kwargs}
        
        # Set base dimensions and starting points
        self.width = kwargs['width']
        self.height = kwargs['height']
        self.x_start = kwargs['x']
        self.y_start = kwargs['y']
        
        # Per-path parameters: dict with path indices as keys, can now include 'rect_id'
        # Example: path_params={0: {'y': 450, 'height': 90, 'rect_id': 'rect1'}}
        self.path_params = kwargs['path_params'] if kwargs['path_params'] is not None else {}
        
        # Per-rectangle parameters: dict with rect IDs as keys
        # Example: rect_params={'rect1': {'x': 0, 'y': 0, 'width': 50, 'height': 100}}
        self.rect_params = kwargs['rect_params'] if kwargs['rect_params'] is not None else {}
        
        # Internal state
        self.rect_i = None
        self.rect_map = {}  # Maps rect_id -> index in paths array
        self.rect_transforms = {}  # Maps rect_id -> {kx, ky, x_origin, y_origin, w_box, h_box}
        self.path_i = []
        self.line = {'x': [], 'y': []}
    
    def values(self, i: int) -> dict:
        # Return a dictionary of x/y values for a single path
        size = len(self.line['x'][i])
        x = [float(self.line['x'][i][j]) for j in range(size)]
        y = [float(self.line['y'][i][j]) for j in range(size)]
        return {'x': x, 'y': y}
    
    @property
    def width(self):
        print(f"Width of the graph is {self.or_width}")
        return self.or_width
    
    @width.setter
    def width(self, value):
        self.or_width = value
    
    @property
    def height(self):
        print(f"Height of the graph is {self.or_height}")
        return self.or_height
    
    @height.setter
    def height(self, value):
        self.or_height = value
