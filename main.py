from pdfminer.pdfinterp import PDFResourceManager, PDFPageInterpreter
from pdfminer.converter import TextConverter
from pdfminer.converter import PDFPageAggregator
from pdfminer.layout import LAParams
from pdfminer.pdfpage import PDFPage
from io import StringIO
from pathlib import Path
from io import StringIO
import re
from pdfminer.converter import TextConverter
from pdfminer.layout import LAParams
from pdfminer.pdfdocument import PDFDocument
from pdfminer.pdfinterp import PDFResourceManager, PDFPageInterpreter
from pdfminer.pdfpage import PDFPage
from pdfminer.pdfparser import PDFParser

# NOTES
# - keep in mind, this script works if every line in the file has the '€' symbol in the 'Últ. Precio'
#   column. In some cases (either they forgot, or their script failed) the '€' symbol does not appear,.
#   and causes the parser to break.
#   If this happens, just run the first method, comment it out, then modify the file and add the '€'
#   where it's missing, and run the second method.

# TODO
# - right now I'm only retrieving last values (Últ.valor) because it was the easiest.
#   I can retrieve all the other values just by taking into account that decimal values are
#   represented with two digits after the comma.

# Maybe I can build a huge-ass regular expression to parse this by lines...


class SingularBankParser():
    """
    Class for parsing data from SingularBank values basket.
    """
    

    def __init__(self):
        """
        Class instance.
        """
        self.PDF_HEADER = ''
        # self.PDF_LINE = re.compile('[A-Z][A-Z](([0-9]|[A-Z]){10}) (-?[0-9],([0-9]{2}){6})')
        self.VALUE_CODE = re.compile('[A-Z][A-Z](([0-9]|[A-Z]){10})') # value code
        self.VALUE_DATA = re.compile('(-)?[0-9]+,([0-9]){2}') # data from the value code


    def process_list_of_values(self, values_list: list):
        """
        Processes list of items containing values and monetary values.
        Values are fixed-length 12 chars long strings representing the value name.
        They have two capital letters at the begginning and the rest are 10 digits.
        """
        for item in values_list:
            item = item.strip()
            print(f'item->{item}')
            # get the value code:
            value_code = ''
            value_price = ''

            # value_code_match = re.search('[A-Z][A-Z](([0-9]|[A-Z]){10})', item)
            value_code_match = re.search(self.VALUE_CODE, item)
            data_value_match = re.search(self.VALUE_DATA, item)
            # value_price = item.split(value_code)[0]
            if value_code_match is not None:
                value_code = value_code_match.group(0)
                value_price = item.split(value_code)[1].strip()
                print(f'value_code={value_code}')
                print(f'value_price={value_price} EUR')

            elif data_value_match is not None:
               # this means we get the data
               print(f'Under construction') 


    def parse_pdf(self, documents_path: Path, output_path: Path):
        """
        Main method for parsing the PDF. Uses the PDFMiner API
        to parse the data straight from the PDF.

        Parameters
        ----------
        documents_path:Path
            Path to the document.
        output_path:Path
            Path for the output txt file.
        """
        output_string = StringIO()

        with open(documents_path, 'rb') as in_file:
            parser = PDFParser(in_file)
            doc = PDFDocument(parser)
            rsrcmgr = PDFResourceManager()
            device = TextConverter(rsrcmgr, output_string, laparams=LAParams())
            interpreter = PDFPageInterpreter(rsrcmgr, device)

            for page in PDFPage.create_pages(doc):
                interpreter.process_page(page)

        read_text = output_string.getvalue()

    # write input to txt file
        with open(output_path, 'w', encoding='utf-8') as outfile:
            outfile.write(read_text)

    def process_data(self, output_path: Path):
        """
        Processes data from the text parsed from a PDF file.
        """
        with open(output_path, 'r', encoding='utf-8') as infile:
            # read text and split the codes and prices
            for line in infile:
                if '€' in line:
                    self.process_list_of_values(line.split('€'))


def main():
    """
    Runs the main program. Reads from a file.
    """
    documents_path = Path(
        f'/Users/miggarr/Documents/cesta-mercado-europeo.pdf')
    output_path = Path(f'/Users/miggarr/Documents/cesta-mercado-europeo.txt')
    singular_bank_parser = SingularBankParser()
    # singular_bank_parser.parse_pdf(documents_path)
    singular_bank_parser.process_data(output_path)


if __name__ == '__main__':
    main()
