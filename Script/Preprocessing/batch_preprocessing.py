import fitz
import pandas as pd
import re
import os
from pathlib import Path
from docx import Document

# Import functions from Demo_manual_preprocessing
import sys
sys.path.insert(0, r'C:\Users\LENOVO\Documents\GitHub\Chatbot QCĐT\Script\Preprocessing')

from Demo_manual_preprocessing import basic_clean, dataframe_to_markdown, extract_text_and_tables_by_page, merge_text_and_tables, save_clean_txt
from Demo_manual_preprocessing_word import extract_text_and_tables as extract_text_and_tables_word, merge_text_and_tables as merge_text_and_tables_word

# Define all files to preprocess
files_to_process = [
    # PDF files
    {
        "path": r".\Data\Hoc_bong\Hoc_bong_2022_KKHT.pdf",
        "type": "pdf",
        "source_name": "Hoc_bong_2022_KKHT.pdf",
        "category": "Hoc_bong",
        "year": "2022",
        "output": r"Data\Hoc_bong\Hoc_bong_2022_KKHT.txt"
    },
    {
        "path": r".\Data\Hoc_bong\Hoc_bong_2021_TDN.pdf",
        "type": "pdf",
        "source_name": "Hoc_bong_2021_TDN.pdf",
        "category": "Hoc_bong",
        "year": "2021",
        "output": r"Data\Hoc_bong\Hoc_bong_2021_TDN.txt"
    },
    {
        "path": r".\Data\QCDT\QCDT_2025_.pdf",
        "type": "pdf",
        "source_name": "QCDT_2025_.pdf",
        "category": "QCDT",
        "year": "2025",
        "output": r"Data\QCDT\QCDT_2025_.txt"
    },
    {
        "path": r".\Data\QCDT\QCDT_2021.pdf",
        "type": "pdf",
        "source_name": "QCDT_2021.pdf",
        "category": "QCDT",
        "year": "2021",
        "output": r"Data\QCDT\QCDT_2021.txt"
    },
    {
        "path": r".\Data\Other\Other_2021_Hoc_online.pdf",
        "type": "pdf",
        "source_name": "Other_2021_Hoc_online.pdf",
        "category": "Other",
        "year": "2021",
        "output": r"Data\Other\Other_2021_Hoc_online.txt"
    },
    {
        "path": r".\Data\Other\Other_2021_Thi_online.pdf",
        "type": "pdf",
        "source_name": "Other_2021_Thi_online.pdf",
        "category": "Other",
        "year": "2021",
        "output": r"Data\Other\Other_2021_Thi_online.txt"
    },
    {
        "path": r".\Data\Other\Otjher_2021_Quan_ly_Ho_tro_SV_nuoc_ngoai.pdf",
        "type": "pdf",
        "source_name": "Otjher_2021_Quan_ly_Ho_tro_SV_nuoc_ngoai.pdf",
        "category": "Other",
        "year": "2021",
        "output": r"Data\Other\Otjher_2021_Quan_ly_Ho_tro_SV_nuoc_ngoai.txt"
    },
    {
        "path": r".\Data\Ki_su_chuyen_sau\KSCS_2024_QDDT.pdf",
        "type": "pdf",
        "source_name": "KSCS_2024_QDDT.pdf",
        "category": "Ki_su_chuyen_sau",
        "year": "2024",
        "output": r"Data\Ki_su_chuyen_sau\KSCS_2024_QDDT.txt"
    },
    {
        "path": r".\Data\Ki_su_chuyen_sau\KSCS_2025_cong_nhan_hoc_phan.pdf",
        "type": "pdf",
        "source_name": "KSCS_2025_cong_nhan_hoc_phan.pdf",
        "category": "Ki_su_chuyen_sau",
        "year": "2025",
        "output": r"Data\Ki_su_chuyen_sau\KSCS_2025_cong_nhan_hoc_phan.txt"
    },
    {
        "path": r".\Data\Huong_dan\Huong_dan_2023_Thu_tuc_hanh_chinh_VB_CC_KQHT.pdf",
        "type": "pdf",
        "source_name": "Huong_dan_2023_Thu_tuc_hanh_chinh_VB_CC_KQHT.pdf",
        "category": "Huong_dan",
        "year": "2023",
        "output": r"Data\Huong_dan\Huong_dan_2023_Thu_tuc_hanh_chinh_VB_CC_KQHT.txt"
    },
    {
        "path": r".\Data\Huong_dan\Huong_dan_2023_Thuc_tap.pdf",
        "type": "pdf",
        "source_name": "Huong_dan_2023_Thuc_tap.pdf",
        "category": "Huong_dan",
        "year": "2023",
        "output": r"Data\Huong_dan\Huong_dan_2023_Thuc_tap.txt"
    },
    {
        "path": r".\Data\Huong_dan\Huong_dan_2023_Quy_doi_tin_chi.pdf",
        "type": "pdf",
        "source_name": "Huong_dan_2023_Quy_doi_tin_chi.pdf",
        "category": "Huong_dan",
        "year": "2023",
        "output": r"Data\Huong_dan\Huong_dan_2023_Quy_doi_tin_chi.txt"
    },
    {
        "path": r".\Data\Huong_dan\Huong_dan_2021_Quy_doi_tin_chi.pdf",
        "type": "pdf",
        "source_name": "Huong_dan_2021_Quy_doi_tin_chi.pdf",
        "category": "Huong_dan",
        "year": "2021",
        "output": r"Data\Huong_dan\Huong_dan_2021_Quy_doi_tin_chi.txt"
    },
    {
        "path": r".\Data\Hoc_phi\Hoc_phi_2024_DHCQ_KSCS_VLVH_SDH_1.pdf",
        "type": "pdf",
        "source_name": "Hoc_phi_2024_DHCQ_KSCS_VLVH_SDH_1.pdf",
        "category": "Hoc_phi",
        "year": "2024",
        "output": r"Data\Hoc_phi\Hoc_phi_2024_DHCQ_KSCS_VLVH_SDH_1.txt"
    },
    {
        "path": r".\Data\Hoc_phi\Hoc_phi_2023_GTTC.pdf",
        "type": "pdf",
        "source_name": "Hoc_phi_2023_GTTC.pdf",
        "category": "Hoc_phi",
        "year": "2023",
        "output": r"Data\Hoc_phi\Hoc_phi_2023_GTTC.txt"
    },
    {
        "path": r".\Data\Hoc_phi\Hoc_phi_2023_DTCQ.pdf",
        "type": "pdf",
        "source_name": "Hoc_phi_2023_DTCQ.pdf",
        "category": "Hoc_phi",
        "year": "2023",
        "output": r"Data\Hoc_phi\Hoc_phi_2023_DTCQ.txt"
    },
    {
        "path": r".\Data\Ngoai_ngu\Ngoai_ngu_2023_HSGD.pdf",
        "type": "pdf",
        "source_name": "Ngoai_ngu_2023_HSGD.pdf",
        "category": "Ngoai_ngu",
        "year": "2023",
        "output": r"Data\Ngoai_ngu\Ngoai_ngu_2023_HSGD.txt"
    },
    {
        "path": r".\Data\Ngoai_ngu\Ngoai_ngu_2021_GD_Lien_Hoan.pdf",
        "type": "pdf",
        "source_name": "Ngoai_ngu_2021_GD_Lien_Hoan.pdf",
        "category": "Ngoai_ngu",
        "year": "2021",
        "output": r"Data\Ngoai_ngu\Ngoai_ngu_2021_GD_Lien_Hoan.txt"
    },
    # Word files
    {
        "path": r".\Data\Do_an\DATN_2021_Dang_ky.docx",
        "type": "docx",
        "source_name": "DATN_2021_Dang_ky.docx",
        "category": "Do_an",
        "year": "2021",
        "output": r"Data\Do_an\DATN_2021_Dang_ky.txt"
    },
    {
        "path": r".\Data\Huong_dan\Huong_dan_2021_nhan_bang.docx",
        "type": "docx",
        "source_name": "Huong_dan_2021_nhan_bang.docx",
        "category": "Huong_dan",
        "year": "2021",
        "output": r"Data\Huong_dan\Huong_dan_2021_nhan_bang.txt"
    },
    {
        "path": r".\Data\Huong_dan\Huong_dan_2021_Gui_cau_hoi.docx",
        "type": "docx",
        "source_name": "Huong_dan_2021_Gui_cau_hoi.docx",
        "category": "Huong_dan",
        "year": "2021",
        "output": r"Data\Huong_dan\Huong_dan_2021_Gui_cau_hoi.txt"
    },
    {
        "path": r".\Data\Huong_dan\Huong_dan_2020_chuyen_truong.docx",
        "type": "docx",
        "source_name": "Huong_dan_2020_chuyen_truong.docx",
        "category": "Huong_dan",
        "year": "2020",
        "output": r"Data\Huong_dan\Huong_dan_2020_chuyen_truong.txt"
    },
]

def process_batch():
    """Process all files in batch"""
    total = len(files_to_process)
    success = 0
    failed = 0
    
    for idx, file_info in enumerate(files_to_process, 1):
        print(f"\n[{idx}/{total}] Processing: {file_info['source_name']}")
        print(f"  Type: {file_info['type']}")
        print(f"  Path: {file_info['path']}")
        
        try:
            if file_info['type'] == 'pdf':
                # Process PDF
                pages_data = extract_text_and_tables_by_page(file_info['path'])
                merged = merge_text_and_tables(
                    pages_data,
                    source_file=file_info['source_name'],
                    category=file_info['category'],
                    year=file_info['year']
                )
            else:  # docx
                # Process Word
                content_data = extract_text_and_tables_word(file_info['path'])
                merged = merge_text_and_tables_word(
                    content_data,
                    source_file=file_info['source_name'],
                    category=file_info['category'],
                    year=file_info['year']
                )
            
            save_clean_txt(merged, file_info['output'])
            print(f"  ✓ SUCCESS: Saved to {file_info['output']}")
            success += 1
            
        except Exception as e:
            print(f"  ✗ FAILED: {str(e)}")
            failed += 1
    
    print(f"\n{'='*60}")
    print(f"Batch Processing Complete!")
    print(f"Total: {total} | Success: {success} | Failed: {failed}")
    print(f"{'='*60}")

if __name__ == "__main__":
    process_batch()
