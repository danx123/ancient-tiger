"""
Cheat console overlay UI
"""

from PySide6.QtWidgets import QWidget, QVBoxLayout, QLineEdit, QLabel, QScrollArea, QFrame
from PySide6.QtCore import Qt, Signal, QTimer
from PySide6.QtGui import QPainter, QColor, QFont, QKeyEvent

class CheatConsole(QWidget):
    """Cheat console overlay"""
    
    cheat_executed = Signal(str, str)  # success_message, action_flag
    console_closed = Signal()
    
    def __init__(self, cheat_system, parent=None):
        super().__init__(parent)
        self.cheat_system = cheat_system
        
        self.setWindowFlags(Qt.FramelessWindowHint | Qt.Tool)
        self.setAttribute(Qt.WA_TranslucentBackground)
        
        self.command_history = []
        self.history_index = -1
        
        self.setup_ui()
        
    def setup_ui(self):
        """Setup console UI"""
        main_layout = QVBoxLayout()
        main_layout.setContentsMargins(0, 0, 0, 0)
        
        # Console container
        console_frame = QFrame()
        console_frame.setStyleSheet("""
            QFrame {
                background: rgba(0, 0, 0, 220);
                border: 2px solid #FFD700;
                border-radius: 10px;
            }
        """)
        console_frame.setFixedSize(800, 500)
        
        console_layout = QVBoxLayout(console_frame)
        console_layout.setContentsMargins(15, 15, 15, 15)
        console_layout.setSpacing(10)
        
        # Header
        header = QLabel("🎮 CHEAT CONSOLE")
        header.setFont(QFont("Consolas", 16, QFont.Bold))
        header.setStyleSheet("color: #FFD700; background: transparent; border: none;")
        header.setAlignment(Qt.AlignCenter)
        console_layout.addWidget(header)
        
        # Help text
        help_text = QLabel("Type 'HELP' to see all cheats | '~' or ESC to close")
        help_text.setFont(QFont("Consolas", 10))
        help_text.setStyleSheet("color: #888888; background: transparent; border: none;")
        help_text.setAlignment(Qt.AlignCenter)
        console_layout.addWidget(help_text)
        
        # Output area (scroll)
        self.scroll_area = QScrollArea()  # Simpan ke self
        self.scroll_area.setWidgetResizable(True)
        self.scroll_area.setStyleSheet("""
            QScrollArea {
                background: rgba(20, 20, 20, 200);
                border: 1px solid #555555;
                border-radius: 5px;
            }
            QScrollBar:vertical {
                background: rgba(40, 40, 40, 200);
                width: 10px;
            }
            QScrollBar::handle:vertical {
                background: #FFD700;
                border-radius: 5px;
            }
        """)
        
        self.output_widget = QWidget()
        self.output_layout = QVBoxLayout(self.output_widget)
        self.output_layout.setAlignment(Qt.AlignTop)
        self.output_layout.setSpacing(5)
        
        self.scroll_area.setWidget(self.output_widget) # Gunakan self.scroll_area
        console_layout.addWidget(self.scroll_area)
        
        # Input line
        self.input_line = QLineEdit()
        self.input_line.setFont(QFont("Consolas", 12))
        self.input_line.setStyleSheet("""
            QLineEdit {
                background: rgba(40, 40, 40, 200);
                border: 2px solid #FFD700;
                border-radius: 5px;
                color: #FFFFFF;
                padding: 8px;
            }
            QLineEdit:focus {
                border: 2px solid #FFA500;
            }
        """)
        self.input_line.setPlaceholderText("Enter cheat code...")
        self.input_line.returnPressed.connect(self.execute_command)
        console_layout.addWidget(self.input_line)
        
        main_layout.addWidget(console_frame, alignment=Qt.AlignCenter)
        self.setLayout(main_layout)
        
        # Welcome message
        self.add_output("=== Ancient Tiger Cheat Console ===", "#FFD700")
        self.add_output("Type 'HELP' for list of available cheats", "#888888")
        self.add_output("", "#FFFFFF")
        
    def show_console(self):
        """Show console centered on parent"""
        if self.parent():
            self.setGeometry(self.parent().rect())
        self.show()
        self.input_line.setFocus()
        self.input_line.clear()
        
    def close_console(self):
        """Close console"""
        self.console_closed.emit()
        self.close()
        
    def execute_command(self):
        """Execute entered command"""
        command = self.input_line.text().strip()
        if not command:
            return
        
        # Add to history
        self.command_history.append(command)
        self.history_index = len(self.command_history)
        
        # Display command
        self.add_output(f"> {command}", "#00FF00")
        
        # Special commands
        if command.upper() == "HELP":
            self.show_help()
        elif command.upper() == "CLEAR":
            self.clear_output()
        elif command.upper() == "EXIT" or command.upper() == "QUIT":
            self.close_console()
        else:
            # Execute cheat
            success, message = self.cheat_system.execute_cheat(command)
            
            if success:
                self.add_output(f"✓ {message}", "#00FF00")
                self.cheat_executed.emit(message, message)  # Emit for game to handle
            else:
                self.add_output(f"✗ {message}", "#FF0000")
        
        self.input_line.clear()
        
    def show_help(self):
        """Show all available cheats"""
        self.add_output("=== AVAILABLE CHEATS ===", "#FFD700")
        
        categories = self.cheat_system.get_all_cheats_by_category()
        
        for category, cheats in sorted(categories.items()):
            self.add_output(f"\n[{category}]", "#FFA500")
            for cheat in cheats:
                code = cheat['code']
                desc = cheat['description']
                param = " <param>" if cheat.get('needs_param') else ""
                self.add_output(f"  {code}{param} - {desc}", "#CCCCCC")
        
        self.add_output("\nOther commands: CLEAR, EXIT", "#888888")
        
    def clear_output(self):
        """Clear output area"""
        while self.output_layout.count():
            child = self.output_layout.takeAt(0)
            if child.widget():
                child.widget().deleteLater()
        
        self.add_output("Console cleared", "#888888")
        
    def add_output(self, text, color="#FFFFFF"):
        """Add text to output"""
        label = QLabel(text)
        label.setFont(QFont("Consolas", 10))
        label.setStyleSheet(f"color: {color}; background: transparent; border: none;")
        label.setWordWrap(True)
        self.output_layout.addWidget(label)
        
        # Auto scroll to bottom
        QTimer.singleShot(10, self.scroll_to_bottom)
        
    def scroll_to_bottom(self):
        """Scroll output to bottom"""
        # Jangan pakai parent(), tapi pakai referensi langsung
        if hasattr(self, 'scroll_area') and self.scroll_area:
            scrollbar = self.scroll_area.verticalScrollBar()
            scrollbar.setValue(scrollbar.maximum())
        
    def keyPressEvent(self, event):
        """Handle key press"""
        # History navigation
        if event.key() == Qt.Key_Up:
            if self.history_index > 0:
                self.history_index -= 1
                self.input_line.setText(self.command_history[self.history_index])
        elif event.key() == Qt.Key_Down:
            if self.history_index < len(self.command_history) - 1:
                self.history_index += 1
                self.input_line.setText(self.command_history[self.history_index])
            else:
                self.history_index = len(self.command_history)
                self.input_line.clear()
        
        # Close console
        elif event.key() == Qt.Key_Escape or event.key() == Qt.Key_QuoteLeft:  # ~ key
            self.close_console()
        
        else:
            super().keyPressEvent(event)
    
    def paintEvent(self, event):
        """Draw semi-transparent background"""
        painter = QPainter(self)
        painter.fillRect(self.rect(), QColor(0, 0, 0, 150))