from robocorp.tasks import task
from robocorp import browser

from RPA.HTTP import HTTP
from RPA.Tables import Tables

from RPA.PDF import PDF
from RPA.Archive import Archive
import shutil

@task
def order_robots_from_RobotSpareBin():
    """
    Orders robots from RobotSpareBin Industries Inc.
    Saves the order HTML receipt as a PDF file.
    Saves the screenshot of the ordered robot.
    Embeds the screenshot of the robot to the PDF receipt.
    Creates ZIP archive of the receipts and the images.
    """
    # browser.configure(
    #     slowmo = 500,
    # )
    open_robot_order_website()
    click_alert_button()
    download_csv_file()
    get_orders()
    archive_receipts()
    clean_up()

def open_robot_order_website():
    """Open the order website"""
    browser.goto("https://robotsparebinindustries.com/#/robot-order")

def click_alert_button():
    page= browser.page()
    page.click("button:text('Ok')")

def make_order(order):
    page = browser.page()

    page.select_option("#head", str(order["Head"]))

    body_path = f"//input[@type='radio' and @name='body' and @value='{order['Body']}']"
    page.click(body_path)

    page.fill(".form-control",order["Legs"])
    page.fill("#address",order["Address"])

    while True:
        page.click("button:text('Order')")
        order_another = page.query_selector("#order-another")
        if order_another:
            pdf_path = store_receipt_as_pdf(int(order["Order number"]))
            screenshot_path = screenshot_robot(int(order["Order number"]))
            embed_screenshot_to_receipt(screenshot_path, pdf_path)
            order_other()
            click_alert_button()
            break
 

     
def download_csv_file():
    """Downloades csv files from the url"""
    http = HTTP()
    http.download(url="https://robotsparebinindustries.com/orders.csv",overwrite=True)

def get_orders():
    """Read and get orders from csv file"""
    tables=Tables()
    orders= tables.read_table_from_csv("orders.csv")
    for order in orders:
        make_order(order)


def order_other():
    page = browser.page()
    page.click("button:text('Order another robot')")


def screenshot_robot(order_number):
    """Takes screenshot of the ordered bot image"""
    page = browser.page()
    screenshot_path = "output/screenshots/{0}.png".format(order_number)
    page.locator("#robot-preview-image").screenshot(path=screenshot_path)
    return screenshot_path

def store_receipt_as_pdf(order_number):
    """This stores the robot order receipt as pdf"""
    page = browser.page()
    order_receipt_html = page.locator("#receipt").inner_html()
    pdf = PDF()
    pdf_path = "output/receipts/{0}.pdf".format(order_number)
    pdf.html_to_pdf(order_receipt_html, pdf_path)
    return pdf_path

def embed_screenshot_to_receipt(screenshot_path, pdf_path):
    """Embeds the screenshot to the bot receipt"""
    pdf = PDF()
    pdf.add_watermark_image_to_pdf(image_path=screenshot_path,
                                   source_path=pdf_path,
                                   output_path=pdf_path)

def archive_receipts():
    """Archives all the receipt pdfs into a single zip archive"""
    lib = Archive()
    lib.archive_folder_with_zip("./output/receipts", "./output/receipts.zip")


def clean_up():
    """Cleans up the folders where receipts and screenshots are saved."""
    shutil.rmtree("./output/receipts")
    shutil.rmtree("./output/screenshots")

