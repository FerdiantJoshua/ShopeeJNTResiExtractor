import PyPDF2


with open('input/download.pdf', 'rb') as f_in:    
    # pdf reader object
    pdfReader = PyPDF2.PdfFileReader(f_in)
    # number of pages in pdf
    print(pdfReader.documentInfo)
    print(pdfReader.numPages)
    # a page object
    pageObj = pdfReader.getPage(0)
    # extracting text from page.
    # this will print the text you can also save that into String
    print(pageObj.extractText())

