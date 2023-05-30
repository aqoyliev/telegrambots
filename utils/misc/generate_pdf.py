# import asyncio
from fpdf import FPDF


def get_pdf(full_name, email, phone):
    pdf = FPDF(format='A4')
    pdf.add_page()
    pdf.set_font('Arial','B', 15)
    pdf.cell(50, 20, f"Ism familiya:  {full_name}")
    pdf.ln()
    pdf.cell(50, 20, f"Elektron pochta:  {email}")
    pdf.ln()
    pdf.cell(50, 20, f"Telefon raqam:  {phone}")
    pdf.output('output.pdf')

if __name__ == '__main__':
    # asyncio.run(get_pdf("Akbar Qo'yliyev", '+998970078373'))
    get_pdf("Akbar", 'akbar@gmail.com','+998970000000')