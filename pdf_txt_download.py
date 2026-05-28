import os
import requests
import pandas as pd

# =========================================
# CREATE FOLDERS
# =========================================

folders = [
    "data/pdfs/life",
    "data/pdfs/health",
    "data/pdfs/motor",
    "data/pdfs/travel",
    "data/pdfs/retirement",
    "data/markdown",
    "data/txt",
    "data/csv"
]

for folder in folders:
    os.makedirs(folder, exist_ok=True)

print("Folders created successfully!\n")

# =========================================
# HEADERS (IMPORTANT FOR DOWNLOADS)
# =========================================

headers = {
    "User-Agent": "Mozilla/5.0"
}

# =========================================
# PDF DATASET
# =========================================

pdfs = [

    # =====================================
    # LIFE INSURANCE
    # =====================================

    {
        "name": "LIC_Tech_Term_Plan.pdf",
        "url": "https://licindia.in/documents/d/guest/tech-term-plan",
        "folder": "data/pdfs/life"
    },

    {
        "name": "LIC_New_Endowment_Plan.pdf",
        "url": "https://licindia.in/documents/d/guest/new-endowment-plan",
        "folder": "data/pdfs/life"
    },

    {
        "name": "LIC_Whole_Life_Plan.pdf",
        "url": "https://licindia.in/documents/d/guest/jeevan-umang",
        "folder": "data/pdfs/life"
    },

    {
        "name": "HDFC_Click2Wealth_ULIP.pdf",
        "url": "https://www.hdfclife.com/content/dam/hdfclifeinsurancecompany/products-page/brochure-pdf/click-2-wealth-brochure.pdf",
        "folder": "data/pdfs/life"
    },

    {
        "name": "LIC_Childrens_Money_Back_Plan.pdf",
        "url": "https://licindia.in/documents/d/guest/childrens-money-back-plan",
        "folder": "data/pdfs/life"
    },

    # =====================================
    # RETIREMENT
    # =====================================

    {
        "name": "LIC_Jeevan_Shanti_Retirement.pdf",
        "url": "https://licindia.in/documents/d/guest/jeevan-shanti",
        "folder": "data/pdfs/retirement"
    },

    # =====================================
    # HEALTH INSURANCE
    # =====================================

    {
        "name": "Star_Health_Family_Optima.pdf",
        "url": "https://www.starhealth.in/sites/default/files/family-health-optima-insurance-plan-brochure.pdf",
        "folder": "data/pdfs/health"
    },

    # =====================================
    # HOME INSURANCE
    # =====================================

    {
        "name": "HDFC_ERGO_Home_Insurance.pdf",
        "url": "https://www.hdfcergo.com/docs/default-source/downloads/home-insurance/home-suraksha-policy-wording.pdf",
        "folder": "data/pdfs/health"
    },

    # =====================================
    # MOTOR INSURANCE
    # =====================================

    {
        "name": "HDFC_ERGO_Motor_Insurance.pdf",
        "url": "https://www.hdfcergo.com/docs/default-source/downloads/motor-insurance/private-car-package-policy-wordings.pdf",
        "folder": "data/pdfs/motor"
    },

    # =====================================
    # TRAVEL INSURANCE
    # =====================================

    {
        "name": "Bajaj_Allianz_Travel_Insurance.pdf",
        "url": "https://www.bajajallianz.com/download-documents/travel-insurance/travel-prime-brochure.pdf",
        "folder": "data/pdfs/travel"
    }
]

# =========================================
# DOWNLOAD PDFs
# =========================================

print("Starting PDF downloads...\n")

for pdf in pdfs:

    try:

        print(f"Downloading: {pdf['name']}")

        response = requests.get(
            pdf["url"],
            headers=headers,
            timeout=30
        )

        print("Status Code:", response.status_code)

        if response.status_code == 200:

            file_path = os.path.join(
                pdf["folder"],
                pdf["name"]
            )

            with open(file_path, "wb") as f:
                f.write(response.content)

            print(f"Saved: {file_path}\n")

        else:
            print(f"Failed to download: {pdf['name']}\n")

    except Exception as e:

        print(f"Error downloading {pdf['name']}")
        print(e)
        print()

# =========================================
# MARKDOWN FILES
# =========================================

print("Creating markdown files...\n")

term_vs_ulip = """
# Term Insurance vs ULIP

## Term Insurance
- Pure protection plan
- Lower premiums
- No investment component

## ULIP
- Investment + Insurance
- Market linked returns
- Higher charges

## Comparison Table

| Feature | Term Insurance | ULIP |
|----------|----------------|------|
| Investment | No | Yes |
| Premium | Low | Higher |
| Risk | Low | Market Risk |
| Returns | None | Market Linked |
"""

with open(
    "data/markdown/term_vs_ulip_comparison.md",
    "w",
    encoding="utf-8"
) as f:
    f.write(term_vs_ulip)

health_guide = """
# Health Insurance Guide

## Waiting Period
Time before claims become active.

## Co-pay
Amount paid by customer.

## Cashless Claims
Hospital directly settles bills with insurer.

## Network Hospital
Hospitals connected with insurance company.
"""

with open(
    "data/markdown/health_insurance_guide.md",
    "w",
    encoding="utf-8"
) as f:
    f.write(health_guide)

# =========================================
# TXT FILES
# =========================================

print("Creating txt files...\n")

motor_txt = """
Motor Insurance Guide

1. Third-party insurance is mandatory.
2. Comprehensive insurance provides wider coverage.
3. NCB means No Claim Bonus.
4. Add-ons improve policy protection.
"""

with open(
    "data/txt/motor_insurance_guide.txt",
    "w",
    encoding="utf-8"
) as f:
    f.write(motor_txt)

retirement_txt = """
Retirement Planning Guide

1. Start investing early
2. Use annuity plans
3. Diversify investments
4. Estimate inflation correctly
5. Build emergency savings
"""

with open(
    "data/txt/retirement_planning_guide.txt",
    "w",
    encoding="utf-8"
) as f:
    f.write(retirement_txt)

# =========================================
# CSV FILES
# =========================================

print("Creating CSV datasets...\n")

insurance_data = pd.DataFrame({

    "Policy_Name": [
        "LIC Tech Term",
        "Star Health Family",
        "HDFC Motor Secure",
        "Bajaj Travel Protect"
    ],

    "Category": [
        "Life",
        "Health",
        "Motor",
        "Travel"
    ],

    "Premium": [
        12000,
        18000,
        8000,
        5000
    ],

    "Coverage": [
        "1 Crore",
        "10 Lakhs",
        "Car Damage",
        "International Travel"
    ]
})

insurance_data.to_csv(
    "data/csv/insurance_policies_database.csv",
    index=False
)

premium_data = pd.DataFrame({

    "Age": [25, 35, 45, 55],

    "Term_Insurance": [
        8000,
        12000,
        20000,
        35000
    ],

    "Health_Insurance": [
        10000,
        15000,
        25000,
        40000
    ]
})

premium_data.to_csv(
    "data/csv/premium_comparison.csv",
    index=False
)

# =========================================
# FINISHED
# =========================================

print("\n===================================")
print("Dataset generation completed!")
print("===================================")

print("\nGenerated:")
print("✔ PDF folders")
print("✔ Markdown files")
print("✔ TXT files")
print("✔ CSV datasets")

print("\nNOTE:")
print("Some PDF downloads may fail because")
print("insurance websites block bots.")
print("You can manually add PDFs if needed.")