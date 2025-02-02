import sys
from PyQt5.QtCore import Qt, QUrl
from PyQt5.QtWidgets import QApplication, QMainWindow, QVBoxLayout, QPushButton, QLabel, QHBoxLayout, QWidget, QStackedWidget, QLineEdit
from PyQt5.QtWebEngineWidgets import QWebEngineView
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

class MainUI(QMainWindow):
    def __init__(self):
        super().__init__()
        self.driver = None  # Initialize driver as None
        self.selected_url = None
        self.selected_book_title = None  # Track the selected book title
        self.setWindowTitle("Book Viewer")
        self.setGeometry(0, 0, 1920, 1080)  # Set the window size to full screen
        self.showMaximized()  # Ensure it maximizes

        # Main layout
        main_layout = QHBoxLayout()
        
        # Left menu
        self.left_menu = QVBoxLayout()
        self.left_menu.setAlignment(Qt.AlignCenter)

        self.sparx_button = QPushButton("SparxReader")
        self.library_button = QPushButton("Library")
        self.spoof_button = QPushButton("SpoofText")
        self.isbn_button = QPushButton("Locate ISBN")  # New button for locating ISBN
        self.exit_button = QPushButton("Exit")
        self.selected_label = QLabel("Selected Book: <none>")

        button_style = "background-color:rgb(83, 146, 255); color: white; font-size: 20px; padding: 20px; border-radius: 12px; border: none; text-align: center;"
        self.sparx_button.setStyleSheet(button_style)
        self.library_button.setStyleSheet(button_style)
        self.spoof_button.setStyleSheet(button_style)
        self.isbn_button.setStyleSheet("background-color: #6BA4FF; color: white; font-size: 20px; padding: 20px; border-radius: 12px; text-align: center;")
        self.exit_button.setStyleSheet("background-color: #FF5C5C; color: white; font-size: 20px; padding: 20px; border-radius: 12px; border: none; text-align: center;")
        
        self.selected_label.setStyleSheet("color: #333; font-size: 18px; margin-top: 20px; text-align: center;")

        self.sparx_button.clicked.connect(self.show_sparx)
        self.library_button.clicked.connect(self.show_library)
        self.spoof_button.clicked.connect(self.start_spoof_text)
        self.isbn_button.clicked.connect(self.locate_isbn)  # Connect the "Locate ISBN" button
        self.exit_button.clicked.connect(self.close_application)

        self.left_menu.addWidget(self.sparx_button)
        self.left_menu.addWidget(self.library_button)
        self.left_menu.addWidget(self.spoof_button)
        self.left_menu.addWidget(self.isbn_button)  # Add the new button
        self.left_menu.addWidget(self.exit_button)
        self.left_menu.addWidget(self.selected_label)
        
        self.left_menu_widget = QWidget()
        self.left_menu_widget.setLayout(self.left_menu)
        self.left_menu_widget.setStyleSheet("background-color:rgb(163, 187, 255); padding: 30px; border-radius: 15px;")

        # Stacked views
        self.stacked_widget = QStackedWidget()
        self.sparx_view = QWebEngineView()
        self.sparx_view.setUrl(QUrl("https://app.sparxreader.com"))
        
        self.library_view = QWidget()
        self.setup_library_view()
        
        self.stacked_widget.addWidget(self.sparx_view)
        self.stacked_widget.addWidget(self.library_view)
        
        main_layout.addWidget(self.left_menu_widget, 1)
        main_layout.addWidget(self.stacked_widget, 4)
        
        container = QWidget()
        container.setLayout(main_layout)
        container.setStyleSheet("background-color:rgb(164, 206, 255);")
        self.setCentralWidget(container)

    def setup_library_view(self):
        layout = QVBoxLayout()

        self.search_label = QLabel("Search for a book:")
        self.search_label.setStyleSheet("font-size: 24px; color: #444; text-align: center;")

        self.search_input = QLineEdit()
        self.search_input.setPlaceholderText("Enter book title...")
        self.search_input.setStyleSheet("font-size: 18px; padding: 15px; background-color: #FFF; border: 2px solidrgb(145, 167, 205); border-radius: 10px; margin-bottom: 30px;")

        self.confirm_button = QPushButton("Confirm")
        self.confirm_button.setStyleSheet("background-color: #6BA4FF; color: white; font-size: 20px; padding: 18px; border-radius: 10px; text-align: center;")
        self.confirm_button.clicked.connect(self.search_books)

        layout.addWidget(self.search_label, alignment=Qt.AlignCenter)
        layout.addWidget(self.search_input, alignment=Qt.AlignCenter)
        layout.addWidget(self.confirm_button, alignment=Qt.AlignCenter)
        
        background = QWidget()
        background.setStyleSheet("background-color:rgb(176, 216, 255); padding: 40px; border-radius: 15px;")
        background.setLayout(layout)

        self.library_view.setLayout(QVBoxLayout())
        self.library_view.layout().addWidget(background)

    def show_sparx(self):
        self.stacked_widget.setCurrentWidget(self.sparx_view)

    def show_library(self):
        self.stacked_widget.setCurrentWidget(self.library_view)

    def search_books(self):
        query = self.search_input.text()
        if not query:
            return

        search_url = f"https://pdfroom.com/search?query={query}&sort=#search"
        self.library_embed = QWebEngineView()
        self.library_embed.setUrl(QUrl(search_url))

        def handle_url_change(url):
            url_str = url.toString()
            if url_str.startswith("https://pdfroom.com/books/"):
                self.selected_url = url_str
                self.selected_book_title = url_str.split('/')[-2]  # Extract book title from the URL
                # Check if the title is longer than 30 characters
                if len(self.selected_book_title) > 30:
                    self.selected_book_title = self.selected_book_title[:30] + "..."  # Truncate and add "..."
                self.selected_label.setText(f"Selected Book: {self.selected_book_title}")  # Set truncated title
                self.stacked_widget.setCurrentWidget(self.sparx_view)

        self.library_embed.urlChanged.connect(handle_url_change)
        self.stacked_widget.addWidget(self.library_embed)
        self.stacked_widget.setCurrentWidget(self.library_embed)

    def locate_isbn(self):
        if not self.selected_book_title:
            self.selected_label.setText("No book selected! Please select a book first.")
            return

        # Hide all existing embeds before displaying the new one
        for i in range(self.stacked_widget.count()):
            self.stacked_widget.widget(i).hide()

        # Create the new embed for ISBN search
        isbn_url = f"https://isbnsearch.org/search?s={self.selected_book_title}"
        isbn_embed = QWebEngineView()
        isbn_embed.setUrl(QUrl(isbn_url))

        self.stacked_widget.addWidget(isbn_embed)
        self.stacked_widget.setCurrentWidget(isbn_embed)
        isbn_embed.show()  # Show the new embed

    def start_spoof_text(self):
        if not self.selected_url:
            self.selected_label.setText("No book selected!")
            return

        # Initialize the Chrome driver when the user presses "SpoofText"
        if not self.driver:
            self.driver = self.initialize_driver()

        # Open the URL in a new tab, close the blank tab if any
        self.driver.execute_script("window.open('');")  # Open a new blank tab
        self.driver.switch_to.window(self.driver.window_handles[-1])  # Switch to the new blank tab
        self.driver.close()  # Close the blank tab
        self.driver.switch_to.window(self.driver.window_handles[0])  # Switch back to the original tab

        # Open the preview URL in the existing tab
        preview_url = self.selected_url.replace("/books/", "/preview/books/")
        self.driver.get(preview_url)

        # Wait until the URL contains the specified base and page is fully loaded
        WebDriverWait(self.driver, 10).until(EC.url_contains("https://pdfroom.com/preview/books/"))
        WebDriverWait(self.driver, 10).until(EC.presence_of_element_located((By.TAG_NAME, "body")))

        try:
            self.driver.execute_script("document.getElementById('signupPopup').remove();")
        except:
            pass

        # Force fullscreen by setting this script
        self.driver.execute_script("document.body.requestFullscreen();")
        self.driver.execute_script("""        
            document.addEventListener('keydown', function(event) {
                if(event.key === 'F11') {
                    event.preventDefault();
                }
            });
        """)

        self.hide()
        self.show_return_ui()

    def initialize_driver(self):
        options = Options()
        options.add_argument("--start-maximized")
        options.add_argument("--disable-blink-features=AutomationControlled")
        options.add_argument("--disable-popup-blocking")
        
        # Use app mode (no address bar, no window controls)
        preview_url = self.selected_url.replace("/books/", "/preview/books/")  # Preview URL
        options.add_argument(f"--app={preview_url}")
        
        # Additional options to reduce automation detection
        options.add_argument("--disable-infobars")  # Disable the 'Chrome is being controlled' infobar
        options.add_argument("--disable-notifications")  # Disable notifications popups
        options.add_argument("--disable-extensions")  # Disable extensions

        driver = webdriver.Chrome(options=options)
        driver.maximize_window()
        return driver

    def show_return_ui(self):
        return_ui = QWidget()
        layout = QVBoxLayout()
        return_button = QPushButton("Return to Menu")
        return_button.setStyleSheet("background-color: #5F9BFF; color: white; font-size: 20px; padding: 20px; border-radius: 12px;")
        return_button.clicked.connect(self.return_to_menu)
        layout.addWidget(return_button, alignment=Qt.AlignCenter)
        return_ui.setLayout(layout)
        self.return_window = QMainWindow()
        self.return_window.setCentralWidget(return_ui)

        # Move the return UI to the bottom-left corner
        screen_geometry = QApplication.desktop().availableGeometry()
        self.return_window.move(screen_geometry.left(), screen_geometry.bottom() - self.return_window.height())

        # Make the return window stay on top of all applications
        self.return_window.setWindowFlags(self.return_window.windowFlags() | Qt.WindowStaysOnTopHint)

        self.return_window.show()

    def return_to_menu(self):
        if self.driver:
            self.driver.minimize_window()  # Hide the Chrome window instead of closing it
        self.return_window.close()
        self.show()

    def close_application(self):
        if self.driver:
            self.driver.quit()
        QApplication.quit()


if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = MainUI()
    window.show()
    sys.exit(app.exec_())
