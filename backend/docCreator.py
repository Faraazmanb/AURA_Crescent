from fpdf import FPDF

def add_section(pdf, section_title, section_content=""):
    pdf.set_font("Arial", 'B', 16)
    pdf.cell(200, 10, section_title, ln=True, align="L")
    pdf.ln(5)
    
    if section_content:
        pdf.set_font("Arial", '', 12)
        pdf.multi_cell(0, 10, section_content)
        pdf.ln(5)

def create_study_schedule(pdf, schedule_content):
    add_section(pdf, "Create Study Schedule", schedule_content)
    return schedule_content

def create_learning_plan(analysis_text, output):
    # number = input("Please enter the number prefix for the filename: ")
    # filename = input("Please enter the base filename: ")

    pdf = FPDF()
    pdf.add_page()
    
    pdf.set_font("Arial", 'B', 20)
    pdf.cell(200, 10, 'Personalized Learning Plan', ln=True, align="C")
    pdf.ln(10)

    schedule_content = create_study_schedule(pdf, analysis_text)
    
    add_section(pdf, "End of Plan", "Thank you for using Aura's Learning Plan Generator!")

    final_filename = f"{output}.pdf"
    safe_filename = final_filename.encode('latin-1', 'replace').decode('latin-1')

    pdf.output(safe_filename, 'F')  # Ensure you're saving as a file
    print(f"Document has been saved as '{safe_filename}'")
    return schedule_content
