#this file indicates how someone should preprocess a pdf file manually
#the example is on this file: C:\Users\LENOVO\Documents\GitHub\Chatbot QCĐT\Data\Hoc_phi\Hoc_phi_2025_DHCQ_KSCS_VLVH_SDH.pdf

import fitz
import re

# defining preprocessing functions

def basic_clean(text):
    """cleaning the text"""
    print("Cleaning the text")
    #delete page number
    text = re.sub(r'^\d+\s*$', '', text, flags=re.MULTILINE)
    #delete blank line
    text = re.sub(r'\n{3,}', '\n\n', text)
    #delete blank space at the beginning or end of a line
    lines = [line.strip() for line in text.split('\n')]
    text = ('\n').join(lines)
    #normalize vietnamese syntax 
    text = text.replace('\u2013', '-')   # en dash → gạch ngang
    text = text.replace('\u2019', "'")   # curly quote

    return text.strip()

def dataframe_to_markdown(df):
    """Convert pandas DataFrame to markdown tables"""
    print("Converting dataframes to markdown tables")
    #create header row
    headers = [str(col).strip() for col in df.columns]
    md_table = "| " + " | ".join(headers) + " |\n"

    #Create sepaarator row
    md_table += "|" + "|".join(["---" for _ in headers]) + "|\n"

    #Add data rows
    for _, row in df.iterrows():
        values = [str(v).strip() for v in row.values if str(v).strip() != 'nan']
        if values: # Only add if row has content
            md_table += "| " + " | ".join(values) + " |\n"

    return md_table.strip()

def extract_text_and_tables_by_page(path):
    """Extract text and tables separately by page"""
    print("Extracting text and tables")
    doc = fitz.open(path)
    pages_data = []

    for page_num, page in enumerate(doc):
        page_info = {
            "page": page_num + 1,
            "text": page.get_text(),
            "tables": []
        }

        #extract tables for this page
        tabs = page.find_tables()
        for tab in tabs:
            df = tab.to_pandas()
            #Store tables in the DataFrames
            page_info["tables"].append(df)

        pages_data.append(page_info)
    return pages_data           
    

def merge_text_and_tables(pages_data, source_file, category, year):
    """Merge cleaned text and tables into one document"""
    header = f"""
    Nguồn: {source_file}
    Danh mục: {category}
    Năm: {year}
    Ngày xử lý: 6/4/2026

---NỘI DUNG---

"""
    print("Merging text and tables")
    body = ""
    for page_data in pages_data:
        page_num = page_data["page"]
        text = basic_clean(page_data["text"])

        body += f"\n[TRANG {page_num}]\n{text}\n"

        #add cleaned tables for this page
        if page_data["tables"]:
            body += "\n--- BẢNG ---\n"
            for df in page_data["tables"]:
                md_table = dataframe_to_markdown(df)
                body += f"\n{md_table}"

        body += "\n"

    return header + body

def save_clean_txt(text, output_path):
    """save cleaned text"""
    print("Saving cleaned text")
    with open(output_path, "w", encoding="utf-8") as f:
        f.write(text)

# Preprocessing data
pages_data = extract_text_and_tables_by_page('Data\Hoc_phi\Hoc_phi_2024_DHCQ_KSCS_VLVH_SDH_2.pdf')
merged = merge_text_and_tables(
    pages_data,
    source_file='Hoc_phi_2024_DHCQ_KSCS_VLVH_SDH_2.pdf',
    category='Hoc_phi.pdf',
    year='2024'
)
save_clean_txt(merged, "Data/Hoc_phi/Hoc_phi_2024_DHCQ_KSCS_VLVH_SDH_2.txt")