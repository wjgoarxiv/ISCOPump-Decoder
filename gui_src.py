from PyQt6.QtWidgets import QApplication, QMainWindow, QVBoxLayout, QHBoxLayout, QLabel, QPushButton, QTextEdit, QWidget, QComboBox, QFileDialog, QMessageBox, QFrame
from PyQt6.QtGui import QFont, QIcon, QDesktopServices
from PyQt6.QtCore import Qt, QUrl
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas
from matplotlib.figure import Figure
import sys
import pandas as pd
import matplotlib.pyplot as plt
from matplotlib import rcParams
import pandas as pd

def rcparams():
    rcParams['figure.figsize'] = 4, 5 
    rcParams['font.family'] = 'sans-serif'

    # Check whether Arial or SF Pro Display are installed in the computer
    try:
        rcParams['font.sans-serif'] = ['SF Pro Display']
    except:
        try:
            rcParams['font.sans-serif'] = ['Arial']
        except:
            print("ERROR Note that Arial and SF Pro are not installed in the computer. The program will use the default font.")
            pass

    # Label should be far away from the axes
    rcParams['axes.labelpad'] = 8
    rcParams['xtick.major.pad'] = 7
    rcParams['ytick.major.pad'] = 7

    # Add minor ticks
    rcParams['xtick.minor.visible'] = True
    rcParams['ytick.minor.visible'] = True

    # Tick width
    rcParams['xtick.major.width'] = 1
    rcParams['ytick.major.width'] = 1
    rcParams['xtick.minor.width'] = 0.5
    rcParams['ytick.minor.width'] = 0.5

    # Tick length
    rcParams['xtick.major.size'] = 5
    rcParams['ytick.major.size'] = 5
    rcParams['xtick.minor.size'] = 3
    rcParams['ytick.minor.size'] = 3

    # Tick color
    rcParams['xtick.color'] = 'black'
    rcParams['ytick.color'] = 'black'

    rcParams['font.size'] = 10
    rcParams['axes.titlepad'] = 10
    rcParams['axes.titleweight'] = 'normal'
    rcParams['axes.titlesize'] = 14

    # Axes settings
    rcParams['axes.labelweight'] = 'normal'
    rcParams['xtick.labelsize'] = 10
    rcParams['ytick.labelsize'] = 10
    rcParams['axes.labelsize'] = 12
    rcParams['xtick.direction'] = 'in'
    rcParams['ytick.direction'] = 'in'
    
class ISCODecoder(QMainWindow):
    def __init__(self):
        super().__init__()

        self.df = None  # For the ISCOPump log
        self.df3 = None  # For the DWStemp log

        # Set the window title
        self.setWindowTitle("ISCO Decoder")

        # Initialize UI components 
        self.initUI()

    def initUI(self):
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        
        # Main layout for the central widget
        main_layout = QVBoxLayout(central_widget)

        # Title, version, author
        title_font = QFont("Arial", 20, QFont.Weight.Bold)
        main_layout.addWidget(QLabel("ISCODecoder", font=title_font, alignment=Qt.AlignmentFlag.AlignCenter))
        main_layout.addWidget(QLabel("버젼 1.0.1", font=QFont("Arial", 12, QFont.Weight.Bold), alignment=Qt.AlignmentFlag.AlignCenter))
        main_layout.addWidget(QLabel("저자: @wjgoarxiv", font=QFont("Arial", 12, QFont.Weight.Bold), alignment=Qt.AlignmentFlag.AlignCenter))

        # Horizontal layout for buttons
        button_layout = QHBoxLayout()
        self.github_button = QPushButton("ISCOPump-Decoder에 관하여")
        self.github_button.clicked.connect(lambda: QDesktopServices.openUrl(QUrl("https://github.com/wjgoarxiv/ISCOPump-Decoder")))
        button_layout.addWidget(self.github_button)

        self.wjgoarxiv_github_button = QPushButton("저자 GitHub")
        self.wjgoarxiv_github_button.clicked.connect(lambda: QDesktopServices.openUrl(QUrl("https://github.com/wjgoarxiv")))
        button_layout.addWidget(self.wjgoarxiv_github_button)

        self.wjgoarxiv_hp_button = QPushButton("저자 홈페이지")
        self.wjgoarxiv_hp_button.clicked.connect(lambda: QDesktopServices.openUrl(QUrl("https://woojingo.site")))
        button_layout.addWidget(self.wjgoarxiv_hp_button)

        self.donate_button = QPushButton("저자에게 기부를!")
        self.donate_button.clicked.connect(lambda: QDesktopServices.openUrl(QUrl("https://www.buymeacoffee.com/woojingo")))
        button_layout.addWidget(self.donate_button)

        # Add a line to separate the dropdowns and the canvas
        line = QFrame()
        line.setFrameShape(QFrame.Shape.HLine)
        line.setFrameShadow(QFrame.Shadow.Sunken)
        main_layout.addWidget(line)
        
        # Add the button layout to the main layout
        main_layout.addLayout(button_layout)

        # Add a line to separate the dropdowns and the canvas
        line = QFrame()
        line.setFrameShape(QFrame.Shape.HLine)
        line.setFrameShadow(QFrame.Shadow.Sunken)
        main_layout.addWidget(line)

        # Create buttons to load the CSV files and add to the main layouts
        load_button_layout = QHBoxLayout()
        load_isco_button = QPushButton('ISCO CSV 데이터 불러오기', self)
        load_isco_button.clicked.connect(self.load_csv)
        load_button_layout.addWidget(load_isco_button)

        load_dw_button = QPushButton('DW CSV 데이터 불러오기', self)
        load_dw_button.clicked.connect(self.load_csv3)
        load_button_layout.addWidget(load_dw_button)

        main_layout.addLayout(load_button_layout)

        # Create the Data preview sections
        preview_layout = QHBoxLayout()

        # Preview for ISCO
        self.preview_isco_layout = QVBoxLayout()
        self.preview_isco = QTextEdit()
        self.preview_isco_layout.addWidget(QLabel("ISCO 데이터 미리보기:"))
        self.preview_isco_layout.addWidget(self.preview_isco)

        # Preview for DW
        self.preview_dw_layout = QVBoxLayout()
        self.preview_dw = QTextEdit()
        self.preview_dw_layout.addWidget(QLabel("DW 데이터 미리보기:"))
        self.preview_dw_layout.addWidget(self.preview_dw)

        # Add previews to the horizontal layout
        preview_layout.addLayout(self.preview_isco_layout)
        preview_layout.addLayout(self.preview_dw_layout)
        
        # Add the previews to the main layout
        main_layout.addLayout(preview_layout)

        # Dropdowns for selecting variables to plot
        self.dropdown_x_var = QComboBox()
        self.dropdown_y_var = QComboBox()
        plot_button = QPushButton('플롯!', self)
        plot_button.clicked.connect(self.plot_data)

        # Horizontal layout for dropdowns and plot button
        dropdown_layout = QHBoxLayout()
        dropdown_layout.addWidget(QLabel("X 변수 선택하기:"))
        dropdown_layout.addWidget(self.dropdown_x_var)
        dropdown_layout.addWidget(QLabel("Y 변수 선택하기:"))
        dropdown_layout.addWidget(self.dropdown_y_var)
        dropdown_layout.addWidget(plot_button)

        main_layout.addLayout(dropdown_layout)

        # Add a line to separate the dropdowns and the canvas
        line = QFrame()
        line.setFrameShape(QFrame.Shape.HLine)
        line.setFrameShadow(QFrame.Shadow.Sunken)
        main_layout.addWidget(line)

        # Add buttons to call save_csv and save_csv3 functions
        save_button_layout = QHBoxLayout()
        save_isco_button = QPushButton('변환된 ISCO CSV 파일 저장하기', self)
        save_isco_button.clicked.connect(self.save_csv)
        save_button_layout.addWidget(save_isco_button)

        save_dw_button = QPushButton('변환된 DW CSV 파일 저장하기', self)
        save_dw_button.clicked.connect(self.save_csv3)
        save_button_layout.addWidget(save_dw_button)

        main_layout.addLayout(save_button_layout)

        # Placeholder for matplotlib canvas
        self.canvas = FigureCanvas(Figure(figsize=(5, 5)))
        main_layout.addWidget(self.canvas)

        # Dividing section with line  
        hlayout = QHBoxLayout()
        line = QFrame()
        line.setFrameShape(QFrame.Shape.VLine)
        line.setFrameShadow(QFrame.Shadow.Sunken)

        # Figure saving button
        save_figure_button = QPushButton('그래프 그림으로 저장하기', self)
        save_figure_button.clicked.connect(self.save_figure)
        hlayout.addWidget(save_figure_button)

        # Add the dividing section to the main layout
        main_layout.addLayout(hlayout)

        # Exit
        exit_button = QPushButton('종료하기', self)
        exit_button.clicked.connect(self.close)
        main_layout.addWidget(exit_button)

    def load_csv(self):
        # Open a file dialog to select the CSV file
        file_path, _ = QFileDialog.getOpenFileName(self, "Load the ISCOPump CSV", "", "CSV Files (*.csv);;All Files (*)")

        # The below one is the column title
        column_titles = [
            'Time_Sample_Interval',
            'PumpA_Pressure',
            'PumpB_Pressure',
            'PumpC_Pressure',
            'AnalogInputs_A',
            'AnalogInputs_B',
            'AnalogInputs_C',
            'AnalogInputs_D',
            'AnalogInputs_E',
            'Digital_In',
            'PumpA_FlowRate',
            'PumpA_Volume',
            'PumpA_Status',
            'PumpA_ControlStatus',
            'PumpA_ProblemStatus',
            'PumpB_FlowRate',
            'PumpB_Volume',
            'PumpB_Status',
            'PumpB_ControlStatus',
            'PumpB_ProblemStatus',
            'PumpC_FlowRate',
            'PumpC_Volume',
            'PumpC_Status',
            'PumpC_ControlStatus',
            'PumpC_ProblemStatus',
            'System_FlowRate',
            'System_Pressure',
            'System_Volume',
        ] 

        try:
            # Load the CSV file 
            self.df = pd.read_csv(file_path, encoding='UTF-8', index_col=False, names=column_titles)

            # Check if the dataframe is None
            if self.df is None:
                raise ValueError("ERROR: The loaded file is not a valid CSV file.")
            
            # Time unit conversion 
            self.df['Time_Sample_Interval_min'] = self.df['Time_Sample_Interval'] / 60000

            # Pump pressure unit conversion
            # Units = psi * 5
            self.df['PumpA_Pressure_bar'] = self.df['PumpA_Pressure'] * 0.0689476 / 5
            self.df['PumpB_Pressure_bar'] = self.df['PumpB_Pressure'] * 0.0689476 / 5
            self.df['PumpC_Pressure_bar'] = self.df['PumpC_Pressure'] * 0.0689476 / 5

            # Pump volume unit conversion
            # Units = Liters * 10E9 

            # PumpA_Volume_L = df['PumpA_Volume'] * 10E-9
            # PumpA_Volume_mL = df['PumpA_volume'] * 10E-6
            self.df['PumpA_Volume_mL'] = self.df['PumpA_Volume'] * 10E-7
            self.df['PumpB_Volume_mL'] = self.df['PumpB_Volume'] * 10E-7
            self.df['PumpC_Volume_mL'] = self.df['PumpC_Volume'] * 10E-7

            # Flow rate unit conversion 
            # Units = L / min * 10E10 

            # PumpA_FlowRate_L_min = df['PumpA_FlowRate'] * 10E-10
            # PumpA_FlowRate_mL_min = df['PumpA_FlowRate'] * 10E-7
            self.df['PumpA_FlowRate_mL_min'] = self.df['PumpA_FlowRate'] * 0.0000001
            self.df['PumpB_FlowRate_mL_min'] = self.df['PumpB_FlowRate'] * 0.0000001
            self.df['PumpC_FlowRate_mL_min'] = self.df['PumpC_FlowRate'] * 0.0000001

            # Start `Time_Sample_Interval_min` from 0
            self.df['Time_Sample_Interval_min'] = self.df['Time_Sample_Interval_min'] - self.df['Time_Sample_Interval_min'][0]

            # Show a sucesss message box
            QMessageBox.information(self, "Success", "ISCOPump CSV file loaded successfully!")
            
            # Print the treated dataframe to the terminal
            print(self.df.head(5))

        except Exception as e: 
            # Show the error message box
            QMessageBox.critical(self, "Error", f"Error loading ISCOPump CSV file: {str(e)}")

        # Check if the dataframe is None
        if self.df is None:
            self.preview_isco.setText("ERROR: The loaded file is not a valid CSV file.")
        else:
            self.preview_isco.setText(str(self.df.head(10)))

        # After loading the CSV file, update the dropdowns
        self.update_dropdowns(self.df)

    def load_csv3(self): 
        # Open a file dialog to select the CSV file
        file_path, _ = QFileDialog.getOpenFileName(self, "Load the DWStemp CSV", "", "CSV Files (*.csv);;All Files (*)")

        # Data loading
        try: 
            self.df3 = pd.read_csv(file_path, encoding="cp949", header=1)

            # 'min' column generation
            self.df3['min'] = self.df3.iloc[1:, 0].astype(float) / 60 

            # Saving the 5th column 
            fifth_column = self.df3.columns[4]

            QMessageBox.information(self, "Success", "DWStemp CSV file loaded successfully!")

            print(self.df3.head(5))  

        except Exception as e: 
            # Show the error message box
            QMessageBox.critical(self, "Error", f"Error loading DWStemp CSV file: {str(e)}")

        if self.df3 is None:
            self.preview_dw.setText("ERROR: The loaded file is not a valid CSV file.")
        else:
            self.preview_dw.setText(str(self.df3.head(10)))

        # After loading the CSV file, update the dropdowns
        self.update_dropdowns(self.df3)

    def save_csv(self):
        # Prompt user to select file name and location to save CSV file
        file_name, _ = QFileDialog.getSaveFileName(self, "Save ISCO CSV", "", "CSV Files (*.csv)")

        # If user cancels the dialog, do nothing
        if not file_name:
            return

        if self.df is None:
            QMessageBox.critical(self, "Error", "No ISCOPump CSV file is loaded.")
            return
        else: 
            # Write treated ISCO data to selected CSV file
            self.df.to_csv(file_name, index=False)

    def save_csv3(self):
        # Prompt user to select file name and location to save CSV file
        file_name, _ = QFileDialog.getSaveFileName(self, "Save DW CSV", "", "CSV Files (*.csv)")

        # If user cancels the dialog, do nothing
        if not file_name:
            return

        if self.df3 is None:
            QMessageBox.critical(self, "Error", "No DWStemp CSV file is loaded.")
            return
        else:
            # Write treated DW data to selected CSV file
            self.df3.to_csv(file_name, index=False)

    def plot_data(self):

        # Load rcparams
        rcparams()

        # Get selected variables from the dropdowns
        x_var = self.dropdown_x_var.currentText()
        y_var = self.dropdown_y_var.currentText()

        # Check if df and df3 are not None and x_var and y_var are in their columns
        if self.df is not None and self.df3 is not None and x_var in self.df.columns and y_var in self.df3.columns:
            min_length = min(len(self.df[x_var]), len(self.df3[y_var]))

            # Check if df and df3 have the same length
            if len(self.df3[x_var]) != len(self.df[y_var]):
                self.df3 = self.df3[:min_length]
                self.df = self.df[:min_length]

            # Clear the canvas
            self.canvas.figure.clear()

            # Create an axis
            ax = self.canvas.figure.subplots()

            # Plot data (case studies)
            if self.df is not None and x_var in self.df.columns and y_var in self.df.columns:
                ax.plot(self.df[x_var], self.df[y_var], color='black')
            elif self.df3 is not None and x_var in self.df3.columns and y_var in self.df3.columns:
                ax.plot(self.df3[x_var], self.df3[y_var], color='black')
            elif self.df is not None and x_var in self.df.columns and y_var in self.df3.columns:
                ax.plot(self.df[x_var], self.df3[y_var], color='black')
            elif self.df3 is not None and x_var in self.df3.columns and y_var in self.df.columns:
                ax.plot(self.df3[x_var], self.df[y_var], color='black')
            else:
                print("ERROR: The selected variable does not exist in the dataframe.")

            # Label the axis
            ax.set_ylabel(y_var)
            ax.set_xlabel(x_var)

            # Tight layout
            plt.tight_layout()

            # Redraw the canvas
            self.canvas.draw()

        elif self.df is not None and x_var in self.df.columns and y_var in self.df.columns:
            # Clear the canvas
            self.canvas.figure.clear()

            # Create an axis
            ax = self.canvas.figure.subplots()

            # Plot data (case studies)
            ax.plot(self.df[x_var], self.df[y_var], color='black')

            # Label the axis
            ax.set_ylabel(y_var)
            ax.set_xlabel(x_var)

            # Tight layout
            plt.tight_layout()

            # Redraw the canvas
            self.canvas.draw()

        elif self.df3 is not None and x_var in self.df3.columns and y_var in self.df3.columns:
            # Clear the canvas
            self.canvas.figure.clear()

            # Create an axis
            ax = self.canvas.figure.subplots()

            # Plot data (case studies)
            ax.plot(self.df3[x_var], self.df3[y_var], color='black')

            # Label the axis
            ax.set_ylabel(y_var)
            ax.set_xlabel(x_var)

            # Tight layout
            plt.tight_layout()

            # Redraw the canvas
            self.canvas.draw()

        elif self.df is not None and x_var in self.df.columns and y_var in self.df3.columns:
            # Clear the canvas
            self.canvas.figure.clear()

            # Create an axis
            ax = self.canvas.figure.subplots()

            # Plot data (case studies)
            ax.plot(self.df[x_var], self.df3[y_var], color='black')

            # Label the axis
            ax.set_ylabel(y_var)
            ax.set_xlabel(x_var)

            # Tight layout
            plt.tight_layout()

            # Redraw the canvas
            self.canvas.draw()

        elif self.df3 is not None and x_var in self.df3.columns and y_var in self.df.columns:
            # Clear the canvas
            self.canvas.figure.clear()

            # Create an axis
            ax = self.canvas.figure.subplots()

            # Plot data (case studies)
            ax.plot(self.df3[x_var], self.df[y_var], color='black')

            # Label the axis
            ax.set_ylabel(y_var)
            ax.set_xlabel(x_var)

            # Tight layout
            plt.tight_layout()

            # Redraw the canvas
            self.canvas.draw()

        elif self.df is not None and x_var in self.df.columns and y_var in self.df.columns:
            # Clear the canvas
            self.canvas.figure.clear()

            # Create an axis
            ax = self.canvas.figure.subplots()

            # Plot data (case studies)
            ax.plot(self.df[x_var], self.df[y_var], color='black')

            # Label the axis
            ax.set_ylabel(y_var)
            ax.set_xlabel(x_var)

            # Tight layout
            plt.tight_layout()

            # Redraw the canvas
            self.canvas.draw()

        elif self.df3 is not None and x_var in self.df3.columns and y_var in self.df3.columns:
            # Clear the canvas
            self.canvas.figure.clear()

            # Create an axis
            ax = self.canvas.figure.subplots()

            # Plot data (case studies)
            ax.plot(self.df3[x_var], self.df3[y_var], color='black')

            # Label the axis
            ax.set_ylabel(y_var)
            ax.set_xlabel(x_var)

            # Tight layout
            plt.tight_layout()

            # Redraw the canvas
            self.canvas.draw()

        elif self.df is not None and x_var in self.df.columns and y_var in self.df3.columns:
            # Clear the canvas
            self.canvas.figure.clear()

            # Create an axis
            ax = self.canvas.figure.subplots()

            # Plot data (case studies)
            ax.plot(self.df[x_var], self.df3[y_var], color='black')

            # Label the axis
            ax.set_ylabel(y_var)
            ax.set_xlabel(x_var)

            # Tight layout
            plt.tight_layout()

            # Redraw the canvas
            self.canvas.draw()

        elif self.df3 is not None and x_var in self.df3.columns and y_var in self.df.columns:
            # Clear the canvas
            self.canvas.figure.clear()

            # Create an axis
            ax = self.canvas.figure.subplots()

            # Plot data (case studies)
            ax.plot(self.df3[x_var], self.df[y_var], color='black')

            # Label the axis
            ax.set_ylabel(y_var)
            ax.set_xlabel(x_var)

            # Tight layout
            plt.tight_layout()

            # Redraw the canvas
            self.canvas.draw()

        else: 
            QMessageBox.critical(self, "Error", "The selected variable does not exist in the dataframe.")

    def save_figure(self):

        # PNG, JPG, and other formats are supported
        file_name, _ = QFileDialog.getSaveFileName(self, "Save Figure", "", "PNG Files (*.png);;JPG Files (*.jpg);;All Files (*)")

        # If user cancels the dialog, do nothing
        if not file_name:
            return

        # Save the figure
        self.canvas.figure.savefig(file_name, dpi=400, bbox_inches='tight', transparent=True)

    def update_dropdowns(self, df):
        # Clear the dropdowns
        self.dropdown_x_var.clear()
        self.dropdown_y_var.clear()

        for column_name in df.columns:
            self.dropdown_x_var.addItem(column_name)
            self.dropdown_y_var.addItem(column_name)

    def load_stylesheet(self, file_path):
        with open(file_path, "r") as f:
            self.setStyleSheet(f.read())
    
my_style_sheet = """
/* General Styles */
QWidget {
    background-color: #ffffff; /* Light background color */
    color: #094067; /* Dark text color */
    font-family: Helvetica, Arial;
}

/* Custom font for Headlines/Labels with a rounded background */
QLabel {
    font-size: 15px;
    color: #ffffff; /* Assuming white text for contrast */
    background-color: #3da9fc; /* Button background color for visibility */
    font-weight: bold;
    padding: 2px; /* Padding to ensure text doesn't touch the border edge */
    border: None; /* No border */
    border-radius: 6px; 
    margin: 1px; /* Optional margin around the label */
    /* Additional QLabel styles if needed */
}
/* Styles for QPushButton */
QPushButton {
    background-color: #3da9fc; /* Button background color */
    color: #ffffff; /* Light button text color */
    border: None; /* No border */
    border-radius: 4px;
    padding: 5px 10px;
    font-size: 14px;
    font-weight: bold;
}

QPushButton:hover {
    background-color: #90b4ce; /* Lighter secondary color for hover state */
}

QPushButton:pressed {
    background-color: #ef4565; /* Tertiary color for pressed state */
}

QTextEdit {
    background-color: #ffffff; /* Light background color for text edit */
    border: 1px solid #90b4ce; /* Light secondary color for border */
    border-radius: 4px;
    padding: 4px;
    color: #fffffe; /* Changed to black text color for better visibility */
}

/* Styles for QComboBox */
QComboBox {
    background-color: #fffffe; /* Light background color for better visibility */
    color: #5f6c7b; /* Dark text color for better visibility */
    border: 1px solid #90b4ce; /* Light secondary color for border */
    border-radius: 4px;
    padding: 4px;
    min-width: 6em;
}

QComboBox::drop-down {
    subcontrol-origin: padding;
    subcontrol-position: top right;
    width: 15px;
    border-left-width: 1px;
    border-left-color: #90b4ce; /* Light secondary color for border */
    border-left-style: solid;
    border-top-right-radius: 4px;
    border-bottom-right-radius: 4px;
}

QComboBox::down-arrow {
    image: url(path/to/arrow.png); /* Replace with the actual path to the arrow image */
}

/* Style for QComboBox when it's expanded (showing the dropdown items) */
QComboBox QAbstractItemView {
    border: 1px solid #90b4ce; /* Light secondary color for border */
    selection-background-color: #3da9fc; /* Button background color for the selected item */
    selection-color: #ffffff; /* Light button text color for the selected item */
    background-color: #fffffe; /* Light background color for the dropdown */
    color: #5f6c7b; /* Dark text color for the dropdown items */
}

/* Styles for QFrame used as a line */
QFrame {
    background-color: #094067; /* Dark stroke color for lines */
}

/* Styles for the QMainWindow */
QMainWindow {
    background-color: #ffffff; /* Light background color */
}

/* Additional styling for other widgets like QMenuBar, QStatusBar, QToolBar if they are used */
QMenuBar {
	background-color: #ffffff; /* Light background color */
	color: #094067; /* Dark text color */
	border-bottom: 1px solid #90b4ce; /* Light secondary color for border */
}

QMenuBar::item {
	spacing: 3px; /* spacing between menu bar items */
	padding: 1px 4px;
	background: transparent;
}

QMenuBar::item:selected {
	background: #90b4ce; /* Light secondary color for selected menu bar item */
}

QMenuBar::item:pressed {
	background: #ef4565; /* Tertiary color for pressed menu bar item */
}

/* Styles for QFileDialog */
QFileDialog {
    background-color: #ffffff; /* Light background color */
	color: #094067; /* Dark text color */
    border: 1px solid #90b4ce; /* Light secondary color for border */
    border-radius: 4px;
    padding: 4px;
}

QFileDialog QListView, QFileDialog QTreeView {
	background-color: #ffffff; /* Light background color */
	border: 1px solid #90b4ce; /* Light secondary color for border */
	border-radius: 4px;
	padding: 4px;
}

QFileDialog QListView::item, QFileDialog QTreeView::item {
	background-color: #ffffff; /* Light background color */
	color: #094067; /* Dark text color */
}	

QFileDialog QListView::item:selected, QFileDialog QTreeView::item:selected {
	background-color: #90b4ce; /* Light secondary color for border */
	color: #ffffff; /* Light text color */
}

QStatusBar {
	background-color: #ffffff; /* Light background color */
	color: #094067; /* Dark text color */
	border-top: 1px solid #90b4ce; /* Light secondary color for border */
}

QToolBar {
	background-color: #ffffff; /* Light background color */
	border-bottom: 1px solid #90b4ce; /* Light secondary color for border */
}

QToolBar::separator {
	background-color: #90b4ce; /* Light secondary color for border */
	width: 1px;
	height: 1px;
}

QToolButton {
	background-color: #ffffff; /* Light background color */
	border: 1px solid #90b4ce; /* Light secondary color for border */
	border-radius: 4px;
	padding: 4px;
}

QToolButton:hover {
	background-color: #90b4ce; /* Light secondary color for border */
}

QToolButton:checked {
	background-color: #ef4565; /* Tertiary color for pressed state */
}

QToolButton:pressed {
	background-color: #ef4565; /* Tertiary color for pressed state */
}

QToolButton:disabled {
	background-color: #ffffff; /* Light background color */
	border: 1px solid #90b4ce; /* Light secondary color for border */
	border-radius: 4px;
	padding: 4px;
}

QToolButton:checked:disabled {
	background-color: #ef4565; /* Tertiary color for pressed state */
}

QToolButton:pressed:disabled {
	background-color: #ef4565; /* Tertiary color for pressed state */
}

/* Styles for QTabWidget */

QTabWidget::pane {
	border: 1px solid #90b4ce; /* Light secondary color for border */
	padding: 4px;
}

QTabWidget::tab-bar {
	left: 5px; /* move to the right by 5px */
}
"""

if __name__ == "__main__":
    app = QApplication(sys.argv)
    app.setWindowIcon(QIcon("icon.ico"))
    app.setStyleSheet(my_style_sheet)
    window = ISCODecoder()
    window.show()
    sys.exit(app.exec())
