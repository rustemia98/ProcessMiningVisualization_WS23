from PyQt5.QtCore import Qt
from PyQt5.QtWidgets import QWidget, QSlider,QLabel,QVBoxLayout, QHBoxLayout, QFrame, QGraphicsView, QGraphicsScene
from PyQt5.QtGui import QPixmap, QPainter, QTransform
from mining_algorithms.heuristic_mining import HeuristicMining
from mining_algorithms.csv_preprocessor import read
from custom_ui.algorithm_view_interface import AlgorithmViewInterface

class HeuristicGraphView(QWidget, AlgorithmViewInterface):
    def __init__(self, parent):
        super().__init__()
        self.parent = parent

        #modifiers and global variables
        self.zoom_factor = 1.0
        self.dependency_treshhold = 0.5
        self.min_frequency = 1
        self.max_frequency = 100
        self.graphviz_graph = None

        # Create a QGraphicsView and set its properties
        self.view = QGraphicsView(self)
        self.view.setRenderHint(QPainter.Antialiasing)
        self.view.setRenderHint(QPainter.SmoothPixmapTransform)
        self.view.setViewportUpdateMode(QGraphicsView.FullViewportUpdate)
        self.view.setDragMode(QGraphicsView.ScrollHandDrag)

        # Create a QGraphicsScene and set its properties
        self.scene = QGraphicsScene(self)
        self.view.setScene(self.scene)

        # Set the zoom level of the QGraphicsView
        self.view.setTransform(QTransform().scale(self.zoom_factor, self.zoom_factor))

        # Add a slider to to control the zoom level
        self.zoom_slider = QSlider(Qt.Horizontal)
        self.zoom_slider.setMinimum(1)
        self.zoom_slider.setMaximum(200)
        self.zoom_slider.setValue(100)
        self.zoom_slider.setTickInterval(10)
        self.zoom_slider.setTickPosition(QSlider.TicksBelow)
        self.zoom_slider.valueChanged.connect(self.__zoom)

        view_layout = QVBoxLayout()
        view_layout.addWidget(self.zoom_slider)
        view_layout.addWidget(self.view)
        
        # Create the slider frame
        slider_frame = QFrame()
        slider_frame.setFrameShape(QFrame.StyledPanel)
        slider_frame.setFrameShadow(QFrame.Sunken)
        slider_frame.setMinimumWidth(200)

        # Create the sliders
        slider_layout = QHBoxLayout()

        self.freq_slider = QSlider(Qt.Vertical)
        self.freq_slider.setRange(self.min_frequency, self.max_frequency)
        self.freq_slider.setValue(self.min_frequency)
        self.freq_slider.valueChanged.connect(self.__freq_slider_changed)
        self.freq_slider_label = QLabel(f"Min Frequency: {self.min_frequency}")
        self.freq_slider_label.setAlignment(Qt.AlignCenter)

        self.thresh_slider = QSlider(Qt.Vertical)
        self.thresh_slider.setRange(0, 100)
        self.thresh_slider.setValue(50)
        self.thresh_slider.valueChanged.connect(self.__thresh_slider_changed)
        self.thresh_slider_label = QLabel(f"Dependency Threshhold: {self.dependency_treshhold}")
        self.thresh_slider_label.setAlignment(Qt.AlignCenter)

        freq_slider_layout = QVBoxLayout()
        freq_slider_layout.addWidget(self.freq_slider)
        freq_slider_layout.addWidget(self.freq_slider_label)

        thresh_slider_layout = QVBoxLayout()
        thresh_slider_layout.addWidget(self.thresh_slider)
        thresh_slider_layout.addWidget(self.thresh_slider_label)

        slider_layout.addLayout(freq_slider_layout)
        slider_layout.addLayout(thresh_slider_layout)

        # Create the main layout
        main_layout = QHBoxLayout(self)
        main_layout.addLayout(view_layout, stretch=3)
        main_layout.addWidget(slider_frame, stretch=1)

        # Add the slider layout to the slider frame layout
        slider_frame_layout = QVBoxLayout()
        slider_frame_layout.addWidget(QLabel("Heuristic Mining Modifiers", alignment=Qt.AlignCenter))
        slider_frame_layout.addLayout(slider_layout)
        slider_frame.setLayout(slider_frame_layout)

        self.setLayout(main_layout)

    #This function is called in main before the graph is shown.
    def mine(self, filepath, timeLabel, caseLabel, eventLabel):
        cases = read(filepath, timeLabel, caseLabel, eventLabel)
        self.Heuristic_Model = HeuristicMining(cases)
        self.max_frequency = self.Heuristic_Model.get_max_frequency()
        self.freq_slider.setRange(self.min_frequency,self.max_frequency)
        self.__mine_and_draw_csv()

    def __freq_slider_changed(self, value):
        # Update the label with the slider value
        self.freq_slider_label.setText(f"Min. Frequency: {value}")
        # Redraw graph when value changes
        self.min_frequency = value
        self.__mine_and_draw_csv()
    
    def __thresh_slider_changed(self, value):
        # Update the label with the slider value
        self.thresh_slider_label.setText(f"Dependency Threshhold: {value/100:.2f}")
        # Redraw graph when value changes
        self.dependency_treshhold = value/100
        self.__mine_and_draw_csv()

    def __zoom(self, value):
        # Calculate the zoom factor based on the slider value
        self.zoom_factor = value / 100.0
        self.view.setTransform(QTransform().scale(self.zoom_factor, self.zoom_factor))
    
    def __mine_and_draw_csv(self):

        '''with graphviz'''
        self.graphviz_graph = self.Heuristic_Model.create_dependency_graph_with_graphviz(self.dependency_treshhold,self.min_frequency)
        
        self.filepath = 'temp/graph_viz'
        filename = self.filepath + '.png'
        self.graphviz_graph.render(self.filepath,format = 'png')

        # Load the image and add it to the QGraphicsScene
        self.image = QPixmap(filename)
        self.scene.clear()
        self.item = self.scene.addPixmap(self.image)
        print("heuristic_graph_display_view: CSV mined")
        
    def generate_png(self):
        #the heuristic algorithm loads the png to show on the canvas.
        #No need to generate it again, if it is already there.
        return

    def generate_svg(self):
        self.graphviz_graph.render(self.filepath,format = 'svg')
        print("heuristic_graph_display_view: SVG generated")

    def clear(self):
        self.scene.clear()
        self.dependency_treshhold= 0.5
        self.min_frequency = 1
        self.zoom_factor = 1.0
