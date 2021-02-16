from tkinter.filedialog import askopenfilename
from tkinter import Tk
import fitz


def openPDF():
    Tk().withdraw()
    fileName = askopenfilename()
    return open(fileName, 'rb')


def getText(file):
    pdf = fitz.open(file)
    # numPages = pdf.pageCount
    page = pdf.loadPage(0)
    pageText = page.getText("text")
    return pageText
