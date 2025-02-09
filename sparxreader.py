import sys
from PyQt5.QtCore import Qt, QUrl
from PyQt5.QtWidgets import QApplication, QMainWindow, QVBoxLayout, QPushButton, QLabel, QHBoxLayout, QWidget, QStackedWidget, QLineEdit, QTableWidget, QTableWidgetItem, QSizePolicy
from PyQt5.QtGui import QClipboard
from PyQt5.QtWebEngineWidgets import QWebEngineView
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import pyperclip
class MainUI(QMainWindow):
    def __init__(self):
        super().__init__()
        self.driver = None
        self.selected_url = None
        self.selected_book_title = None
        self.setWindowTitle("Book Viewer")
        self.setGeometry(0, 0, 1920, 1080)
        self.showMaximized()
        main_layout = QHBoxLayout()
        self.left_menu = QVBoxLayout()
        self.left_menu.setAlignment(Qt.AlignCenter)
        self.sparx_button = QPushButton("SparxReader")
        self.library_button = QPushButton("Library")
        self.spoof_button = QPushButton("SpoofText")
        self.isbn_button = QPushButton("Locate ISBN")
        self.database_button = QPushButton("Database")
        self.exit_button = QPushButton("Exit")
        self.selected_label = QLabel("Selected Book: <none>")
        button_style = "background-color:rgb(83, 146, 255); color: white; font-size: 20px; padding: 20px; border-radius: 12px; border: none; text-align: center;"
        self.sparx_button.setStyleSheet(button_style)
        self.library_button.setStyleSheet(button_style)
        self.spoof_button.setStyleSheet(button_style)
        self.isbn_button.setStyleSheet("background-color: #6BA4FF; color: white; font-size: 20px; padding: 20px; border-radius: 12px; text-align: center;")
        self.database_button.setStyleSheet("background-color: #6BA4FF; color: white; font-size: 20px; padding: 20px; border-radius: 12px; text-align: center;")
        self.exit_button.setStyleSheet("background-color: #FF5C5C; color: white; font-size: 20px; padding: 20px; border-radius: 12px; border: none; text-align: center;")
        self.selected_label.setStyleSheet("color: #333; font-size: 18px; margin-top: 20px; text-align: center;")
        self.sparx_button.clicked.connect(self.show_sparx)
        self.library_button.clicked.connect(self.show_library)
        self.spoof_button.clicked.connect(self.start_spoof_text)
        self.isbn_button.clicked.connect(self.locate_isbn)
        self.database_button.clicked.connect(self.show_database_ui)
        self.exit_button.clicked.connect(self.close_application)
        self.left_menu.addWidget(self.sparx_button)
        self.left_menu.addWidget(self.library_button)
        self.left_menu.addWidget(self.spoof_button)
        self.left_menu.addWidget(self.isbn_button)
        self.left_menu.addWidget(self.database_button)
        self.left_menu.addWidget(self.exit_button)
        self.left_menu.addWidget(self.selected_label)
        self.left_menu_widget = QWidget()
        self.left_menu_widget.setLayout(self.left_menu)
        self.left_menu_widget.setStyleSheet("background-color:rgb(163, 187, 255); padding: 30px; border-radius: 15px;")
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
        self.database_ui_open = False
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
                self.selected_book_title = url_str.split('/')[-2]
                if len(self.selected_book_title) > 30:
                    self.selected_book_title = self.selected_book_title[:30] + "..."
                self.selected_label.setText(f"Selected Book: {self.selected_book_title}")
                self.stacked_widget.setCurrentWidget(self.sparx_view)
        self.library_embed.urlChanged.connect(handle_url_change)
        self.stacked_widget.addWidget(self.library_embed)
        self.stacked_widget.setCurrentWidget(self.library_embed)
    def locate_isbn(self):
        if not self.selected_book_title:
            self.selected_label.setText("No book selected! Please select a book first.")
            return
        for i in range(self.stacked_widget.count()):
            self.stacked_widget.widget(i).hide()
        isbn_url = f"https://isbnsearch.org/search?s={self.selected_book_title}"
        isbn_embed = QWebEngineView()
        isbn_embed.setUrl(QUrl(isbn_url))
        self.stacked_widget.addWidget(isbn_embed)
        self.stacked_widget.setCurrentWidget(isbn_embed)
        isbn_embed.show()
        def handle_isbn(url):
            url_str = url.toString()
            if "isbnsearch.org" in url_str and self.selected_isbn is None:
                self.selected_isbn = self.extract_isbn_from_page()
                self.selected_label.setText(f"ISBN: {self.selected_isbn}")
        isbn_embed.urlChanged.connect(handle_isbn)
    def extract_isbn_from_page(self):
        try:
            isbn_element = self.driver.find_element(By.XPATH, "//span[contains(text(),'ISBN-13')]/following-sibling::span")
            return isbn_element.text.strip()
        except Exception as e:
            return None
    def toggle_database_ui(self):
        if self.database_ui_open:
            self.database_ui.close()
            self.database_ui_open = False
        else:
            self.show_database_ui()
    def show_database_ui(self):
        self.database_ui = QWidget()
        layout = QVBoxLayout()
        self.database_ui.setStyleSheet("background-color:rgb(109, 171, 234);")  # Dark background
        self.table = QTableWidget()
        self.table.setRowCount(26)
        self.table.setColumnCount(2)
        self.table.setHorizontalHeaderLabels(['Book Title', 'ISBN'])
        self.table.verticalHeader().setVisible(False)
        self.table.setColumnWidth(0, 920)
        self.table.setColumnWidth(1, 920)
        self.table.setStyleSheet("""
        QTableWidget {
            background-color:rgb(117, 169, 218);  /* Darker background for the table */
            color: white;
            font-weight: bold;
        }
        QTableWidget::item {
            border: 1px solid #7F8C8D;
            padding: 5px;
        }
        QHeaderView::section {
            background-color: #16A085;
            color: white;
            font-weight: bold;
        }
    """)
        self.table.setSelectionBehavior(QTableWidget.SelectRows)
        self.table.setSelectionMode(QTableWidget.NoSelection)
        for row in range(26):
            for col in range(2):
                item = QTableWidgetItem()
                item.setFlags(item.flags() & ~Qt.ItemIsEditable)
                self.table.setItem(row, col, item)
        books_data = [
            ("Ride Your Wave", "9781648271205"),
            ("Sword Art Online - Aincrad 1", "9788076790353"),
            ("Spy Classroom | Vol. 1", "9781975322403"),
            ("Reincarnated as a Sword | Vol. 1", "9781642751413"),
            ("A Certain Magical Index | Vol. 1", "9780316339124"),
            ("No Game, No life | Vol. 1", "9781626920798"),
            ("Suzume", "9781975373061"),
            ("Re:Zero - Starting Life in Another World | Vol. 1", "9780316315319"),
            ("Goblin Slayer | Vol. 1", "9780316501590"),
            ("Trapped in a Dating Sim: The World of Otome Games is Tough for Mobs | Vol. 1", "9781648274268"),
            ("That Time I Got Reincarnated as a Slime | Vol. 1", "9780316414203"),
            ("your name.", "9780316471862"),
            ("Disciple of the Lich: Or How I Was Cursed by the Gods and Dropped Into the Abyss | Vol. 1", "9781648275524"),
            ("The detective Is Already Dead | Vol. 1", "9781975325756"),
            ("Mushoku Tensei: Jobless Reincarnation | Vol. 1", "9781626922358"),
            ("Konosuba: An Explosion on This Wonderful World! | Vol. 1", "9781975359607"),
            ("Arifureta: From Commonplace to Worlds Strongest | Vol. 1", "9781626927681"),
            ("I Want to Eat Your Pancreas | Complete Collection", "9781642750324"),
            ("Jujutsu Kaisen 01", "9786230022180"),
            ("Classroom of the Elite | Vol. 1", "9781642751376"),
            ("I Had That Same Dream Again | Complete Collection", "9781645054917"),
            ("Re:Zero - Starting Life in Another World -, Vol. 1 (light novel)", "9780316315302")
        ]
        for row, (book_name, isbn) in enumerate(books_data):
            self.table.setItem(row, 0, QTableWidgetItem(book_name))
            self.table.setItem(row, 1, QTableWidgetItem(isbn))
        layout.addWidget(self.table)
        exit_button = QPushButton("Close Database")
        exit_button.setStyleSheet("background-color: #FF5C5C; color: white; font-size: 20px; padding: 20px; border-radius: 12px; text-align: center;")
        exit_button.clicked.connect(self.close_database_ui)
        refresh_button = QPushButton("Refresh Database")
        refresh_button.setStyleSheet("background-color: #4CAF50; color: white; font-size: 20px; padding: 20px; border-radius: 12px; text-align: center;")
        refresh_button.clicked.connect(self.refresh_database_ui)
        layout.addWidget(refresh_button)
        layout.addWidget(exit_button)
        self.text_label = QLabel("Database loaded successfully!")
        self.text_label.setStyleSheet("font-size: 18px; color: white; padding: 10px;")
        layout.addWidget(self.text_label)
        self.database_ui.setLayout(layout)
        self.database_ui.setWindowTitle("Database")
        self.database_ui.setGeometry(0, 0, 1500, 900)
        self.database_ui.showFullScreen()
        self.database_ui_open = True
    def close_database_ui(self):
        """Closes the database UI window."""
        if self.database_ui:
            self.database_ui.close()
        self.database_ui_open = False
    def refresh_database_ui(self):
        """Refreshes the database UI without clearing data."""
        if self.database_ui:
            self.database_ui.close()
        self.show_database_ui()
    def initialize_driver(self):
        options = Options()
        options.add_argument("--start-maximized")
        options.add_argument("--disable-blink-features=AutomationControlled")
        options.add_argument("--disable-popup-blocking")
        preview_url = self.selected_url.replace("/books/", "/preview/books/")  # Preview URL
        options.add_argument(f"--app={preview_url}")
        options.add_argument("--disable-infobars")
        options.add_argument("--disable-notifications")
        options.add_argument("--disable-extensions")
        driver = webdriver.Chrome(options=options)
        driver.maximize_window()
        return driver
    def return_to_menu(self):
        if self.driver:
            self.driver.minimize_window()
        self.return_window.close()
        self.show()
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
        screen_geometry = QApplication.desktop().availableGeometry()
        self.return_window.move(screen_geometry.left(), screen_geometry.bottom() - self.return_window.height())
        self.return_window.setWindowFlags(self.return_window.windowFlags() | Qt.WindowStaysOnTopHint)
        self.return_window.show()
    def start_spoof_text(self):
        if not self.selected_url:
            self.selected_label.setText("No book selected!")
            return
        if not self.driver:
            self.driver = self.initialize_driver()
        self.driver.execute_script("window.open('');")
        self.driver.switch_to.window(self.driver.window_handles[-1])
        self.driver.close()  # Close the blank tab
        self.driver.switch_to.window(self.driver.window_handles[0])
        preview_url = self.selected_url.replace("/books/", "/preview/books/")
        self.driver.get(preview_url)
        WebDriverWait(self.driver, 10).until(EC.url_contains("https://pdfroom.com/preview/books/"))
        WebDriverWait(self.driver, 10).until(EC.presence_of_element_located((By.TAG_NAME, "body")))
        try:
            self.driver.execute_script("document.getElementById('signupPopup').remove();")
        except:
            pass
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
    def close_application(self):
        QApplication.quit()
app = QApplication(sys.argv)
window = MainUI()
window.show()
sys.exit(app.exec_())
