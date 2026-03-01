"""
MLBevo Door Module Test Report Viewer
A desktop application for viewing and analyzing test logs
"""
import sys
import re
from typing import Optional, List
from PyQt6.QtWidgets import (
    QApplication, QMainWindow, QWidget, QVBoxLayout, QHBoxLayout,
    QLabel, QPushButton, QTableWidget, QTableWidgetItem, QLineEdit,
    QHeaderView, QFileDialog, QFrame, QGridLayout
)
from PyQt6.QtCore import Qt, QMimeData, pyqtSignal
from PyQt6.QtGui import QDragEnterEvent, QDropEvent, QFont, QColor, QPalette

from log_parser import parse_log_file, ParsedLog, TestRow, get_result_variant


# Color palette matching the React app
COLORS = {
    'background': '#EFF2F7',
    'foreground': '#1E293B',
    'card': '#FFFFFF',
    'primary': '#1E3A5F',
    'primary_foreground': '#F1F5F9',
    'muted': '#E2E8F0',
    'muted_foreground': '#64748B',
    'border': '#CBD5E1',
    'pass': '#16A34A',
    'pass_bg': '#DCFCE7',
    'fail': '#DC2626',
    'fail_bg': '#FEE2E2',
    'warn': '#F59E0B',
    'warn_bg': '#FEF3C7',
    'header_start': '#1E3A5F',
    'header_end': '#2E4A6F',
}


class DropArea(QFrame):
    """Drag and drop area for file upload"""
    file_loaded = pyqtSignal(str, str)  # content, filename
    
    def __init__(self):
        super().__init__()
        self.setAcceptDrops(True)
        self.init_ui()
    
    def init_ui(self):
        self.setFrameStyle(QFrame.Shape.StyledPanel)
        self.setStyleSheet(f"""
            QFrame {{
                border: 2px dashed {COLORS['border']};
                border-radius: 12px;
                background-color: {COLORS['card']};
                padding: 40px;
            }}
            QFrame:hover {{
                border-color: {COLORS['primary']};
            }}
        """)
        
        layout = QVBoxLayout()
        layout.setAlignment(Qt.AlignmentFlag.AlignCenter)
        
        # Icon placeholder
        icon_label = QLabel("📁")
        icon_label.setStyleSheet(f"""
            QLabel {{
                font-size: 48px;
                background-color: {COLORS['muted']};
                border-radius: 30px;
                padding: 20px;
            }}
        """)
        icon_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        icon_label.setFixedSize(100, 100)
        
        # Text
        text_label = QLabel("Drop a test log file here or click to browse")
        text_label.setStyleSheet(f"""
            QLabel {{
                font-size: 14px;
                font-weight: 600;
                color: {COLORS['foreground']};
                margin-top: 10px;
            }}
        """)
        
        subtext_label = QLabel("Supports .txt, .csv, .log files")
        subtext_label.setStyleSheet(f"""
            QLabel {{
                font-size: 12px;
                color: {COLORS['muted_foreground']};
                margin-top: 5px;
            }}
        """)
        
        layout.addWidget(icon_label, alignment=Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(text_label, alignment=Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(subtext_label, alignment=Qt.AlignmentFlag.AlignCenter)
        
        self.setLayout(layout)
    
    def mousePressEvent(self, event):
        """Handle click to open file dialog"""
        file_name, _ = QFileDialog.getOpenFileName(
            self,
            "Open Test Log File",
            "",
            "Log Files (*.txt *.csv *.log);;All Files (*)"
        )
        if file_name:
            self.load_file(file_name)
    
    def dragEnterEvent(self, event: QDragEnterEvent):
        """Accept drag events with files"""
        if event.mimeData().hasUrls():
            event.acceptProposedAction()
    
    def dropEvent(self, event: QDropEvent):
        """Handle file drop"""
        files = [u.toLocalFile() for u in event.mimeData().urls()]
        if files:
            self.load_file(files[0])
    
    def load_file(self, file_path: str):
        """Load and emit file content"""
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read()
            file_name = file_path.split('/')[-1].split('\\')[-1]
            self.file_loaded.emit(content, file_name)
        except Exception as e:
            print(f"Error loading file: {e}")


class MetadataCard(QFrame):
    """Card displaying a single metadata item"""
    
    def __init__(self, icon: str, label: str, value: str, is_badge: bool = False):
        super().__init__()
        self.is_badge = is_badge
        self.value_text = value
        self.init_ui(icon, label, value)
    
    def init_ui(self, icon: str, label: str, value: str):
        self.setFrameStyle(QFrame.Shape.StyledPanel)
        self.setStyleSheet(f"""
            QFrame {{
                border: 1px solid {COLORS['border']};
                border-radius: 12px;
                background-color: {COLORS['card']};
                padding: 20px;
            }}
        """)
        
        layout = QVBoxLayout()
        
        # Header with icon and label
        header_layout = QHBoxLayout()
        
        icon_label = QLabel(icon)
        icon_label.setStyleSheet(f"""
            QLabel {{
                font-size: 18px;
                background-color: rgba(30, 58, 95, 0.1);
                border-radius: 8px;
                padding: 8px;
            }}
        """)
        icon_label.setFixedSize(36, 36)
        icon_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        
        label_widget = QLabel(label)
        label_widget.setStyleSheet(f"""
            QLabel {{
                font-size: 12px;
                font-weight: 500;
                color: {COLORS['muted_foreground']};
            }}
        """)
        
        header_layout.addWidget(icon_label)
        header_layout.addWidget(label_widget)
        header_layout.addStretch()
        
        # Value
        if self.is_badge:
            value_widget = self.create_badge(value)
        else:
            value_widget = QLabel(value)
            value_widget.setStyleSheet(f"""
                QLabel {{
                    font-size: 16px;
                    font-weight: 600;
                    font-family: 'Courier New', monospace;
                    color: {COLORS['foreground']};
                    margin-top: 5px;
                }}
            """)
        
        layout.addLayout(header_layout)
        layout.addWidget(value_widget)
        
        self.setLayout(layout)
    
    def create_badge(self, value: str) -> QLabel:
        """Create a colored badge for result value"""
        variant = get_result_variant(value)
        
        if variant == 'pass':
            bg_color = COLORS['pass_bg']
            text_color = COLORS['pass']
        elif variant == 'fail':
            bg_color = COLORS['fail_bg']
            text_color = COLORS['fail']
        else:
            bg_color = COLORS['warn_bg']
            text_color = COLORS['warn']
        
        badge = QLabel(value)
        badge.setStyleSheet(f"""
            QLabel {{
                background-color: {bg_color};
                color: {text_color};
                border: 1px solid {text_color}40;
                border-radius: 12px;
                padding: 4px 10px;
                font-size: 12px;
                font-weight: 600;
                font-family: 'Courier New', monospace;
            }}
        """)
        badge.setAlignment(Qt.AlignmentFlag.AlignLeft)
        return badge


class ResultsTableWidget(QWidget):
    """Table widget with search and sorting functionality"""
    
    def __init__(self):
        super().__init__()
        self.rows: List[TestRow] = []
        self.filtered_rows: List[TestRow] = []
        self.sort_column = -1
        self.sort_ascending = True
        self.init_ui()
    
    def init_ui(self):
        layout = QVBoxLayout()
        layout.setContentsMargins(0, 0, 0, 0)
        
        # Search bar and info
        top_layout = QHBoxLayout()
        
        self.search_input = QLineEdit()
        self.search_input.setPlaceholderText("Search rows...")
        self.search_input.setStyleSheet(f"""
            QLineEdit {{
                padding: 8px 12px 8px 35px;
                border: 1px solid {COLORS['border']};
                border-radius: 8px;
                background-color: {COLORS['card']};
                font-size: 13px;
                color: {COLORS['foreground']};
            }}
            QLineEdit:focus {{
                border: 2px solid {COLORS['primary']};
            }}
        """)
        self.search_input.setFixedWidth(320)
        self.search_input.textChanged.connect(self.on_search)
        
        info_label = QLabel("ℹ️ Only rows containing ExternalId, LowerLimit and UpperLimit are displayed.")
        info_label.setStyleSheet(f"""
            QLabel {{
                font-size: 11px;
                color: {COLORS['muted_foreground']};
            }}
        """)
        
        top_layout.addWidget(self.search_input)
        top_layout.addStretch()
        top_layout.addWidget(info_label)
        
        # Table
        self.table = QTableWidget()
        self.table.setColumnCount(8)
        self.table.setHorizontalHeaderLabels([
            'External ID', 'Text', 'Lower Limit', 'Value',
            'Upper Limit', 'Unit', 'Result', 'Status Text'
        ])
        
        # Table styling
        self.table.setStyleSheet(f"""
            QTableWidget {{
                border: 1px solid {COLORS['border']};
                border-radius: 12px;
                background-color: {COLORS['card']};
                gridline-color: {COLORS['border']};
                font-size: 13px;
            }}
            QTableWidget::item {{
                padding: 8px;
                border-bottom: 1px solid {COLORS['border']};
            }}
            QTableWidget::item:selected {{
                background-color: rgba(30, 58, 95, 0.1);
            }}
            QHeaderView::section {{
                background-color: {COLORS['muted']};
                color: {COLORS['muted_foreground']};
                padding: 10px;
                border: none;
                border-bottom: 1px solid {COLORS['border']};
                font-size: 11px;
                font-weight: 600;
                text-transform: uppercase;
            }}
            QHeaderView::section:hover {{
                background-color: {COLORS['border']};
                cursor: pointer;
            }}
        """)
        
        # Table settings
        self.table.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeMode.Interactive)
        self.table.horizontalHeader().setStretchLastSection(True)
        self.table.verticalHeader().setVisible(False)
        self.table.setAlternatingRowColors(True)
        self.table.setSelectionBehavior(QTableWidget.SelectionBehavior.SelectRows)
        self.table.setSortingEnabled(False)  # We'll handle sorting ourselves
        self.table.horizontalHeader().sectionClicked.connect(self.on_header_clicked)
        
        # Row count label
        self.count_label = QLabel()
        self.count_label.setStyleSheet(f"""
            QLabel {{
                padding: 10px;
                border-top: 1px solid {COLORS['border']};
                font-size: 13px;
                color: {COLORS['muted_foreground']};
            }}
        """)
        
        layout.addLayout(top_layout)
        layout.addWidget(self.table)
        layout.addWidget(self.count_label)
        
        self.setLayout(layout)
    
    def set_rows(self, rows: List[TestRow]):
        """Set table data"""
        self.rows = rows
        self.filtered_rows = rows.copy()
        self.update_table()
    
    def on_search(self, text: str):
        """Filter rows based on search text"""
        if not text:
            self.filtered_rows = self.rows.copy()
        else:
            text_lower = text.lower()
            self.filtered_rows = [
                row for row in self.rows
                if any(text_lower in str(getattr(row, field)).lower()
                      for field in ['external_id', 'text', 'lower_limit', 'value',
                                   'upper_limit', 'unit', 'result', 'status_text'])
            ]
        self.update_table()
    
    def on_header_clicked(self, logical_index: int):
        """Handle column header click for sorting"""
        if self.sort_column == logical_index:
            self.sort_ascending = not self.sort_ascending
        else:
            self.sort_column = logical_index
            self.sort_ascending = True
        
        self.sort_rows()
        self.update_table()
    
    def sort_rows(self):
        """Sort filtered rows by current sort column"""
        if self.sort_column < 0:
            return
        
        field_names = ['external_id', 'text', 'lower_limit', 'value',
                      'upper_limit', 'unit', 'result', 'status_text']
        field = field_names[self.sort_column]
        
        self.filtered_rows.sort(
            key=lambda row: str(getattr(row, field)),
            reverse=not self.sort_ascending
        )
    
    def update_table(self):
        """Update table display"""
        self.table.setRowCount(len(self.filtered_rows))
        
        for i, row in enumerate(self.filtered_rows):
            # Set alternating row colors
            if i % 2 == 0:
                for j in range(8):
                    self.table.setItem(i, j, QTableWidgetItem())
                    self.table.item(i, j).setBackground(QColor(COLORS['muted']))
            
            # External ID
            item = QTableWidgetItem(row.external_id)
            item.setFont(QFont('Courier New', 10, QFont.Weight.Bold))
            self.table.setItem(i, 0, item)
            
            # Text
            self.table.setItem(i, 1, QTableWidgetItem(row.text))
            
            # Lower Limit
            item = QTableWidgetItem(self.format_hex_value(row.lower_limit))
            item.setFont(QFont('Courier New', 9))
            self.table.setItem(i, 2, item)
            
            # Value
            item = QTableWidgetItem(self.format_value(row.value))
            item.setFont(QFont('Courier New', 9))
            self.table.setItem(i, 3, item)
            
            # Upper Limit
            item = QTableWidgetItem(self.format_hex_value(row.upper_limit))
            item.setFont(QFont('Courier New', 9))
            self.table.setItem(i, 4, item)
            
            # Unit
            self.table.setItem(i, 5, QTableWidgetItem(row.unit))
            
            # Result (with color badge)
            result_item = QTableWidgetItem(row.result)
            result_item.setFont(QFont('Courier New', 10, QFont.Weight.Bold))
            variant = get_result_variant(row.result)
            if variant == 'pass':
                result_item.setForeground(QColor(COLORS['pass']))
            elif variant == 'fail':
                result_item.setForeground(QColor(COLORS['fail']))
            else:
                result_item.setForeground(QColor(COLORS['warn']))
            self.table.setItem(i, 6, result_item)
            
            # Status Text
            item = QTableWidgetItem(row.status_text)
            item.setForeground(QColor(COLORS['muted_foreground']))
            self.table.setItem(i, 7, item)
        
        # Update count
        count = len(self.filtered_rows)
        self.count_label.setText(f"{count} result{'s' if count != 1 else ''}")
    
    def format_value(self, value: str) -> str:
        """Format value - displays full values, wraps hex in 8-byte lines"""
        trimmed = value.strip()
        
        # Check for scientific notation (e.g., "9.8999999999999993E+37")
        if 'E+' in trimmed.upper() or 'E-' in trimmed.upper():
            try:
                # Parse as float and format with limited precision
                num = float(trimmed)
                # Format with 1 decimal place in scientific notation
                return f"{num:.1e}"
            except ValueError:
                # If parsing fails, fall through to hex formatting
                pass
        
        # Otherwise use hex formatting
        return self.format_hex_value(trimmed)
    
    def format_hex_value(self, value: str) -> str:
        """Format hex values - wraps every 8 bytes (16 hex chars) with newline"""
        trimmed = value.strip()
        
        # Case 1: bytes separated by spaces (e.g., "07 00 FF 00")
        bytes_match = re.findall(r'[0-9A-Fa-f]{2}', trimmed)
        is_byte_array = bool(bytes_match) and len(''.join(bytes_match)) == len(trimmed.replace(' ', ''))
        
        if is_byte_array:
            # Wrap every 8 bytes with newline
            chunks = []
            for i in range(0, len(bytes_match), 8):
                chunks.append(' '.join(bytes_match[i:i+8]))
            return '\n'.join(chunks)
        
        # Case 2: continuous hex without spaces (wrap every 16 hex characters = 8 bytes)
        if re.match(r'^[0-9A-Fa-f]+$', trimmed):
            # Wrap every 16 hex chars (8 bytes)
            chunks = [trimmed[i:i+16] for i in range(0, len(trimmed), 16)]
            return '\n'.join(chunks)
        
        # Return full value as-is if not recognized as hex
        return value


class MainWindow(QMainWindow):
    """Main application window"""
    
    def __init__(self):
        super().__init__()
        self.parsed_log: Optional[ParsedLog] = None
        self.file_name: str = ''
        self.init_ui()
    
    def init_ui(self):
        self.setWindowTitle("MLBevo Door Module Test Report")
        self.setMinimumSize(1400, 800)
        
        # Set application palette
        palette = QPalette()
        palette.setColor(QPalette.ColorRole.Window, QColor(COLORS['background']))
        self.setPalette(palette)
        
        # Central widget
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        
        main_layout = QVBoxLayout()
        main_layout.setContentsMargins(0, 0, 0, 0)
        main_layout.setSpacing(0)
        
        # Header
        header = self.create_header()
        main_layout.addWidget(header)
        
        # Content area
        self.content_widget = QWidget()
        self.content_layout = QVBoxLayout()
        self.content_layout.setContentsMargins(40, 30, 40, 30)
        self.content_layout.setSpacing(20)
        self.content_widget.setLayout(self.content_layout)
        
        # Initial drop area
        self.drop_area = DropArea()
        self.drop_area.file_loaded.connect(self.on_file_loaded)
        self.content_layout.addWidget(self.drop_area)
        
        main_layout.addWidget(self.content_widget)
        
        # Footer
        footer = self.create_footer()
        main_layout.addWidget(footer)
        
        central_widget.setLayout(main_layout)
    
    def create_header(self) -> QWidget:
        """Create application header with gradient background"""
        header = QFrame()
        header.setFixedHeight(90)
        header.setStyleSheet(f"""
            QFrame {{
                background: qlineargradient(
                    x1:0, y1:0, x2:1, y2:1,
                    stop:0 {COLORS['header_start']},
                    stop:1 {COLORS['header_end']}
                );
            }}
        """)
        
        layout = QHBoxLayout()
        layout.setContentsMargins(40, 20, 40, 20)
        
        # Icon
        icon_label = QLabel("💻")
        icon_label.setStyleSheet(f"""
            QLabel {{
                font-size: 32px;
                background-color: rgba(255, 255, 255, 0.1);
                border-radius: 8px;
                padding: 10px;
            }}
        """)
        icon_label.setFixedSize(52, 52)
        icon_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        
        # Title and subtitle
        text_layout = QVBoxLayout()
        text_layout.setSpacing(2)
        
        title = QLabel("MLBevo Door Module Test Report")
        title.setStyleSheet(f"""
            QLabel {{
                font-size: 18px;
                font-weight: 700;
                color: {COLORS['primary_foreground']};
            }}
        """)
        
        subtitle = QLabel("AQP1 Testman Log Viewer")
        subtitle.setStyleSheet(f"""
            QLabel {{
                font-size: 13px;
                color: rgba(241, 245, 249, 0.7);
            }}
        """)
        
        text_layout.addWidget(title)
        text_layout.addWidget(subtitle)
        
        layout.addWidget(icon_label)
        layout.addLayout(text_layout)
        layout.addStretch()
        
        header.setLayout(layout)
        return header
    
    def create_footer(self) -> QWidget:
        """Create application footer"""
        footer = QFrame()
        footer.setFixedHeight(30)
        
        layout = QHBoxLayout()
        layout.setContentsMargins(40, 5, 40, 5)
        
        label = QLabel("Designed for AQP1 by D. Piskorowski")
        label.setStyleSheet(f"""
            QLabel {{
                font-size: 9px;
                color: {COLORS['muted_foreground']};
            }}
        """)
        label.setAlignment(Qt.AlignmentFlag.AlignRight)
        
        layout.addStretch()
        layout.addWidget(label)
        
        footer.setLayout(layout)
        return footer
    
    def on_file_loaded(self, content: str, file_name: str):
        """Handle file load"""
        self.file_name = file_name
        self.parsed_log = parse_log_file(content)
        self.show_results()
    
    def show_results(self):
        """Display parsed results"""
        # Clear content
        while self.content_layout.count():
            item = self.content_layout.takeAt(0)
            if item.widget():
                item.widget().deleteLater()
        
        # File name and reset button
        top_layout = QHBoxLayout()
        
        file_label = QLabel(f"📄 {self.file_name}")
        file_label.setStyleSheet(f"""
            QLabel {{
                font-size: 13px;
                font-family: 'Courier New', monospace;
                color: {COLORS['muted_foreground']};
            }}
        """)
        
        reset_button = QPushButton("Load another file")
        reset_button.setStyleSheet(f"""
            QPushButton {{
                padding: 6px 12px;
                border: 1px solid {COLORS['border']};
                border-radius: 8px;
                background-color: {COLORS['card']};
                color: {COLORS['foreground']};
                font-size: 13px;
                font-weight: 500;
            }}
            QPushButton:hover {{
                background-color: {COLORS['muted']};
            }}
        """)
        reset_button.clicked.connect(self.reset_view)
        
        top_layout.addWidget(file_label)
        top_layout.addStretch()
        top_layout.addWidget(reset_button)
        
        self.content_layout.addLayout(top_layout)
        
        # Metadata cards
        cards_layout = QGridLayout()
        cards_layout.setSpacing(15)
        
        card1 = MetadataCard(
            "#️⃣",
            "Serial Number",
            self.parsed_log.metadata.serial_number
        )
        card2 = MetadataCard(
            "✔️",
            "Test Result",
            self.parsed_log.metadata.test_result,
            is_badge=True
        )
        card3 = MetadataCard(
            "📊",
            "Filtered Rows",
            str(len(self.parsed_log.rows))
        )
        
        cards_layout.addWidget(card1, 0, 0)
        cards_layout.addWidget(card2, 0, 1)
        cards_layout.addWidget(card3, 0, 2)
        
        self.content_layout.addLayout(cards_layout)
        
        # Results table
        self.results_table = ResultsTableWidget()
        self.results_table.set_rows(self.parsed_log.rows)
        self.content_layout.addWidget(self.results_table)
    
    def reset_view(self):
        """Reset to initial state"""
        self.parsed_log = None
        self.file_name = ''
        
        # Clear content
        while self.content_layout.count():
            item = self.content_layout.takeAt(0)
            if item.widget():
                item.widget().deleteLater()
            elif item.layout():
                self.clear_layout(item.layout())
        
        # Show drop area again
        self.drop_area = DropArea()
        self.drop_area.file_loaded.connect(self.on_file_loaded)
        self.content_layout.addWidget(self.drop_area)
    
    def clear_layout(self, layout):
        """Recursively clear a layout"""
        while layout.count():
            item = layout.takeAt(0)
            if item.widget():
                item.widget().deleteLater()
            elif item.layout():
                self.clear_layout(item.layout())


def main():
    """Main application entry point"""
    app = QApplication(sys.argv)
    
    # Set application-wide font
    font = QFont("Inter", 10)
    app.setFont(font)
    
    # Create and show main window
    window = MainWindow()
    window.show()
    
    sys.exit(app.exec())


if __name__ == '__main__':
    main()
