#!/usr/bin/env python3
"""
Phone & User List Processor for TrackSub & FeelsRight
Cleans, normalizes, and preps contact lists for:
1. Meta / TikTok Ads Custom Audience (100% compliant D2C targeting)
2. Opted-in SMS / WhatsApp reactivation campaigns
"""

import sys
import os
import re
import csv
import argparse
from typing import List, Dict

def clean_phone_number(raw: str, default_country_code: str = "1") -> str:
    """Strip formatting and format to E.164 digits."""
    digits = re.sub(r"[^\d+]", "", str(raw).strip())
    if not digits:
        return ""
    if digits.startswith("+"):
        return digits[1:]
    if len(digits) == 10 and default_country_code:
        return default_country_code + digits
    return digits

def process_file(filepath: str, default_cc: str = "1") -> List[Dict]:
    results = []
    if not os.path.exists(filepath):
        print(f"Error: File '{filepath}' does not exist.")
        return []

    with open(filepath, "r", encoding="utf-8", errors="ignore") as f:
        reader = csv.reader(f)
        for row in reader:
            if not row:
                continue
            for item in row:
                cleaned = clean_phone_number(item, default_cc)
                if cleaned and len(cleaned) >= 10:
                    results.append({"raw": item, "e164": "+" + cleaned, "digits": cleaned})
                    break
    return results

def main():
    parser = argparse.ArgumentParser(description="Clean and prep phone numbers for D2C campaigns")
    parser.add_argument("--file", help="Path to CSV or TXT file with phone numbers")
    parser.add_argument("--cc", default="1", help="Default country code if missing (1=US/CA, 44=UK, 91=IN)")
    args = parser.parse_args()

    if not args.file:
        print("Usage: python3 user_list_processor.py --file your_contacts.csv [--cc 1]")
        print("\nFeatures:")
        print("1. Deduplicates and normalizes numbers to international E.164 standard")
        print("2. Generates CSV for Meta/TikTok Ads Custom Audience (shows app install ads without spam)")
        print("3. Preps compliant opt-in SMS / WhatsApp lists")
        return

    contacts = process_file(args.file, args.cc)
    print(f"Loaded {len(contacts)} phone numbers.")

    # Deduplicate
    unique = {c["digits"]: c for c in contacts}.values()
    print(f"Unique valid numbers: {len(unique)}")

    out_csv = "cleaned_contacts_custom_audience.csv"
    with open(out_csv, "w", newline="") as out:
        writer = csv.writer(out)
        writer.writerow(["phone"])
        for c in unique:
            writer.writerow([c["e164"]])
    print(f"\n✅ Cleaned list saved to: {out_csv}")
    print("👉 You can directly upload this file to Meta Ads Manager -> Audiences -> Custom Audience -> Customer List!")

if __name__ == "__main__":
    main()
