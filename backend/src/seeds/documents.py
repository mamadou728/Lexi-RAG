import asyncio
import os
import sys
from pathlib import Path
from datetime import datetime, timezone
import httpx
from motor.motor_asyncio import AsyncIOMotorClient
from beanie import init_beanie
import certifi

# Add the src directory to Python path so imports work
# This allows running the script from the seeds directory
src_path = Path(__file__).parent.parent
if str(src_path) not in sys.path:
    sys.path.insert(0, str(src_path))

# --- IMPORTS ---
from core.config import MONGO_URI
from core.security import get_password_hash  # Use the same hash function as the API
from models.auth import User, SystemRole, AccountStatus
from models.matters import Matter, PracticeArea
from models.documents import DocumentFile, SensitivityLevel
from models.message import Conversation 
from core.encryption import AES256Service

# ---------------- CONFIG ----------------
BACKEND_URL = "http://localhost:8000"  # Adjust if your server is elsewhere
API_BASE = BACKEND_URL  
COMMON_PASSWORD = "password123"

# Hash password lazily
def get_common_hash():
    if not hasattr(get_common_hash, '_cached_hash'):
        get_common_hash._cached_hash = get_password_hash(COMMON_PASSWORD)
    return get_common_hash._cached_hash

# ---------------- 1. USER DATA ----------------
USERS_DATA = [
    {"key": "partner_bob", "email": "bob.vance@lawfirm.com", "full_name": "Bob Vance", "system_role": SystemRole.PARTNER, "account_status": AccountStatus.ACTIVE},
    {"key": "associate_jane", "email": "jane.doe@lawfirm.com", "full_name": "Jane Doe", "system_role": SystemRole.ASSOCIATE, "account_status": AccountStatus.ACTIVE},
    {"key": "staff_pam", "email": "pam.beesly@lawfirm.com", "full_name": "Pam Beesly", "system_role": SystemRole.STAFF, "account_status": AccountStatus.ACTIVE},
    {"key": "client_techcorp", "email": "admin@techcorp.com", "full_name": "TechCorp Admin", "system_role": SystemRole.CLIENT, "account_status": AccountStatus.ACTIVE},
    {"key": "client_omni", "email": "leases@omni-realestate.com", "full_name": "Omni Real Estate Rep", "system_role": SystemRole.CLIENT, "account_status": AccountStatus.ACTIVE}
]

# ---------------- 2. MATTER DATA ----------------
MATTER_MAP = {
    "matter_merger_01": {
        "title": "TechCorp v. AI_Startup Merger",
        "practice_area": PracticeArea.CORPORATE,
        "description": "Acquisition of AI_Startup LLC by TechCorp Inc.",
        "client_key": "client_techcorp",
        "team_keys": ["partner_bob", "associate_jane"]
    },
    "matter_ip_02": {
        "title": "TechCorp v. CopyCat Inc.",
        "practice_area": PracticeArea.LITIGATION,
        "description": "IP Infringement case regarding 'Fast-Retriever' software.",
        "client_key": "client_techcorp",
        "team_keys": ["partner_bob", "associate_jane"]
    },
    "matter_estate_03": {
        "title": "Millennium Tower Lease",
        "practice_area": PracticeArea.REAL_ESTATE,
        "description": "Commercial lease agreement for new HQ floors 30-35.",
        "client_key": "client_omni",
        "team_keys": ["partner_bob", "staff_pam"]
    }
}

# ---------------- 3. DOCUMENT DATA ----------------
# ---------------- 3. DOCUMENT DATA ----------------
RAW_DOCS = [
    # --- MATTER 01: TechCorp v. AI_Startup Merger ---
    {
        "_id": "doc_01",
        "filename": "Merger_Agreement_Final_Execution_Copy.pdf",
        "matter_id": "matter_merger_01",
        "sensitivity": "privileged",
        "content_text": """AGREEMENT AND PLAN OF MERGER

Identified as execution version 4.2.

This AGREEMENT AND PLAN OF MERGER (this "Agreement") is made and entered into as of January 15, 2026, by and among TechCorp Inc., a Delaware corporation ("Parent"), and AI_Startup LLC ("Company").

ARTICLE I: THE MERGER
1.1 The Merger. Upon the terms and subject to the conditions set forth in this Agreement, and in accordance with the Delaware General Corporation Law (DGCL), at the Effective Time, the Company shall be merged with and into Parent.
1.2 Closing. The closing of the Merger shall take place at the offices of the Parent's legal counsel no later than two business days after the satisfaction or waiver of the conditions set forth in Article VI.

ARTICLE II: EFFECT ON CAPITAL STOCK
2.1 Conversion of Securities. At the Effective Time, by virtue of the Merger and without any action on the part of the holders:
(a) Each share of Company Common Stock issued and outstanding immediately prior to the Effective Time shall be converted into the right to receive $15.50 in cash, without interest.
(b) Each unvested Company Stock Option shall be accelerated and cashed out at the spread value between the Strike Price and the Merger Consideration."""
    },
    {
        "_id": "doc_02",
        "filename": "AI_Startup_Financials_FY2025.xlsx",
        "matter_id": "matter_merger_01",
        "sensitivity": "internal",
        "content_text": """CONFIDENTIAL FINANCIAL REPORTING - FY 2025

SHEET 1: BALANCE SHEET (As of Dec 31, 2025)
-- Assets --
Cash and Cash Equivalents: $12,400,000
Accounts Receivable: $3,200,000
Intellectual Property (Valuation): $29,400,000
Total Assets: $45,000,000

-- Liabilities --
Short-term Debt: $2,000,000
Deferred Revenue: $5,000,000
Long-term Venture Debt: $5,000,000
Total Liabilities: $12,000,000

SHEET 2: P&L STATEMENT (Q4 2025)
Revenue: $8,500,000 (Up 15% YoY)
Cost of Goods Sold (Server Compute): $3,100,000
R&D Expenses: $2,500,000
SG&A: $1,700,000
Net Income: $1,200,000

NOTES TO FINANCIALS:
1. "Server Compute" costs spiked in November due to training the new 'Gen-X' model.
2. Revenue projections for Q1 2026 assume successful integration with TechCorp's cloud infrastructure, which is expected to reduce COGS by 40%."""
    },
    {
        "_id": "doc_03",
        "filename": "HR_Key_Employee_Retention_Plan.docx",
        "matter_id": "matter_merger_01",
        "sensitivity": "internal",
        "content_text": """PROJECT TITAN - HUMAN RESOURCES STRATEGY & RETENTION
Strictly Private and Confidential

SUBJECT: Retention of Key AI Talent Post-Acquisition

The success of the merger depends heavily on retaining the core engineering team of AI_Startup LLC. The following "Key Employees" have been identified. We propose a retention package consisting of a Cash Bonus (20% of base) and Restricted Stock Units (RSUs) vesting over 3 years.

TIER 1 CRITICAL HIRES:
1. Dr. Sarah Connor (Chief AI Architect) - Essential for legacy code knowledge.
   - Offer: $50k signing bonus + 10,000 TechCorp RSUs.
2. Miles Dyson (Neural Net Lead) - Flight risk. Has received offers from competitors.
   - Offer: $60k signing bonus + 15,000 TechCorp RSUs.

TIER 2 ENGINEERING:
3. John Doe (Senior Dev)
4. Jane Smith (Data Scientist)

CONDITIONS:
Retention bonuses will be paid out 50% upon Closing and 50% upon the one-year anniversary of the Closing Date, provided the employee has not voluntarily terminated employment."""
    },
    {
        "_id": "doc_04",
        "filename": "Board_Resolution_Approving_Acquisition.pdf",
        "matter_id": "matter_merger_01",
        "sensitivity": "privileged",
        "content_text": """MINUTES OF A SPECIAL MEETING OF THE BOARD OF DIRECTORS OF TECHCORP INC.
Held via Video Conference
January 10, 2026 at 2:00 PM EST

PRESENT: Bob Vance (Chairman), Alice Scott (CEO), and all other Directors.

The meeting was called to order to discuss Project Titan (the acquisition of AI_Startup LLC).

PRESENTATION:
The CFO presented the valuation report, noting that the purchase price of $150,000,000 represents a 4x multiple on AI_Startup's projected 2026 revenue. Legal counsel reviewed the draft Merger Agreement and highlighted the indemnification clauses.

RESOLUTION 2026-04:
WHEREAS, the Board deems it advisable and in the best interests of the Corporation to acquire AI_Startup LLC;
NOW, THEREFORE, BE IT RESOLVED, that the acquisition is hereby approved; and
RESOLVED FURTHER, that the CEO and CFO are authorized to execute the Merger Agreement and any ancillary documents required to finalize the transaction.

VOTE:
The resolution was put to a vote and passed UNANIMOUSLY."""
    },

    # --- MATTER 02: TechCorp v. CopyCat Inc. (IP Litigation) ---
    {
        "_id": "doc_05",
        "filename": "Complaint_SDNY_filed_stamped.pdf",
        "matter_id": "matter_ip_02",
        "sensitivity": "public",
        "content_text": """UNITED STATES DISTRICT COURT
SOUTHERN DISTRICT OF NEW YORK
Case No. 1:26-cv-00451

TECHCORP INC., Plaintiff,
v.
COPYCAT INC., Defendant.

COMPLAINT FOR PATENT INFRINGEMENT AND TRADE SECRET MISAPPROPRIATION

Plaintiff TechCorp Inc., by and through its undersigned attorneys, alleges as follows:

NATURE OF THE ACTION
1. This is a civil action arising under the patent laws of the United States, 35 U.S.C. § 1 et seq., and the Defend Trade Secrets Act.
2. Defendant CopyCat Inc. has unlawfully accessed, copied, and utilized Plaintiff's proprietary "Fast-Retriever" source code to build a competing product known as "QuickFetch."

COUNT I: INFRINGEMENT OF U.S. PATENT NO. 9,888,777
3. Plaintiff is the owner of U.S. Patent No. 9,888,777 (the "'777 Patent") titled "Method and System for Asynchronous Data Retrieval."
4. Defendant's "QuickFetch" software utilizes the exact method claimed in Claim 1 of the '777 Patent, specifically the "multi-threaded caching mechanism."

PRAYER FOR RELIEF
Plaintiff requests a permanent injunction enjoining Defendant from selling "QuickFetch" and damages in an amount to be determined at trial."""
    },
    {
        "_id": "doc_06",
        "filename": "Forensic_Code_Analysis_Privileged.txt",
        "matter_id": "matter_ip_02",
        "sensitivity": "privileged",
        "content_text": """ATTORNEY WORK PRODUCT / PRIVILEGED AND CONFIDENTIAL

To: Bob Vance (Partner, Outside Counsel)
From: CyberForensics Experts Ltd.
Date: January 20, 2026
Re: Analysis of CopyCat 'QuickFetch' vs TechCorp 'Fast-Retriever'

EXECUTIVE SUMMARY:
We have completed a static and dynamic analysis of the decompiled binaries of CopyCat's "QuickFetch" v1.0. We have identified significant evidence of direct code lifting.

TECHNICAL FINDINGS:
1. SHARED HASHING ALGORITHMS:
The function `calc_hash_v2` in the Defendant's code is bit-for-bit identical to TechCorp's proprietary hashing module. Even the non-functional comments were stripped, but the logic flow remains identical.

2. LEFTOVER ARTIFACTS:
In the hex dump of the `database.dll` file distributed by CopyCat, we found the string "C:/Users/TechCorp_Build_Server/Jenkins/workspace/", which is a filepath internal to TechCorp's build environment.

CONCLUSION:
It is highly probable (>99%) that the Defendant had access to the original source code repository."""
    },
    {
        "_id": "doc_07",
        "filename": "Settlement_Offer_Letter_Draft_v2.docx",
        "matter_id": "matter_ip_02",
        "sensitivity": "privileged",
        "content_text": """WITHOUT PREJUDICE AND SUBJECT TO RULE 408

January 28, 2026

VIA EMAIL
Counsel for CopyCat Inc.

Re: TechCorp Inc. v. CopyCat Inc. (Case No. 1:26-cv-00451) - Settlement Proposal

Dear Counsel,

We write on behalf of our client, TechCorp Inc., to propose a resolution to the above-referenced matter. While we are confident in our position and prepared to proceed to trial, our client prefers to avoid the cost and distraction of prolonged litigation.

TechCorp is prepared to dismiss the lawsuit with prejudice subject to the following non-negotiable terms:
1. Injunction: CopyCat must immediately cease all distribution and support of "QuickFetch."
2. Monetary Damages: Payment of $5,000,000 USD within 30 days of execution.
3. Audit Rights: TechCorp shall have the right to audit CopyCat's code repositories for the next 24 months to ensure compliance.
4. Public Apology: CopyCat will issue a press release acknowledging the infringement.

This offer remains open until February 5, 2026 at 5:00 PM EST.

Sincerely,
Bob Vance"""
    },
    {
        "_id": "doc_08",
        "filename": "Subpoena_custodian_of_records.pdf",
        "matter_id": "matter_ip_02",
        "sensitivity": "public",
        "content_text": """UNITED STATES DISTRICT COURT
SOUTHERN DISTRICT OF NEW YORK

SUBPOENA TO PRODUCE DOCUMENTS, INFORMATION, OR OBJECTS
OR TO PERMIT INSPECTION OF PREMISES IN A CIVIL ACTION

To: ServerHostingProvider LLC (Custodian of Records)
123 Data Center Way, Ashburn, VA

YOU ARE COMMANDED to produce at the time, date, and place set forth below the following documents, electronically stored information, or objects, and to permit inspection, copying, testing, or sampling of the material:

DEFINITIONS:
"Account" refers to any hosting, cloud storage, or VPS services provided to the entity known as "CopyCat Inc."

REQUESTS:
1. All access logs, IP address histories, and login timestamps for the server IP 192.168.1.55 covering the period of December 1, 2025, through January 1, 2026.
2. All billing records, invoices, and payment methods associated with Account ID #998877 associated with CopyCat Inc.
3. Any correspondence between ServerHostingProvider LLC and email addresses ending in "@copycat.com" regarding data migration or backup restoration.

Place: Law Offices of Vance & Partners, NY.
Date/Time: February 10, 2026, 10:00 AM."""
    },

    # --- MATTER 03: Millennium Tower Lease (Real Estate) ---
    {
        "_id": "doc_09",
        "filename": "Millennium_Tower_Lease_Draft_v5.docx",
        "matter_id": "matter_estate_03",
        "sensitivity": "internal",
        "content_text": """COMMERCIAL LEASE AGREEMENT

This LEASE AGREEMENT (the "Lease") is made this 1st day of February, 2026, by and between Omni Real Estate Holdings ("Landlord") and TechCorp Inc. ("Tenant").

1. PREMISES
Landlord leases to Tenant, and Tenant leases from Landlord, the entire rentable area of Floors 30 through 35 of the building located at 100 Main St (Millennium Tower), comprising approximately 120,000 rentable square feet.

2. TERM
The term of this Lease shall be ten (10) years, commencing on March 1, 2026 (the "Commencement Date") and expiring on February 28, 2036.

3. RENT
3.1 Base Rent. Tenant shall pay Base Rent at the annual rate of $65.00 per square foot, payable in equal monthly installments of $650,000.
3.2 Escalation. Base Rent shall increase by 2.5% annually on the anniversary of the Commencement Date.

4. TENANT IMPROVEMENTS (TI)
Landlord agrees to provide a TI allowance of $100 per square foot for the construction of executive offices and a dedicated server room with reinforced cooling capacity.

5. USE
The Premises shall be used for general executive and administrative offices and for no other purpose without Landlord's prior written consent."""
    },
    {
        "_id": "doc_10",
        "filename": "Zoning_Certificate_Occupancy.pdf",
        "matter_id": "matter_estate_03",
        "sensitivity": "public",
        "content_text": """CITY DEPARTMENT OF BUILDINGS
CERTIFICATE OF OCCUPANCY

Certificate No: CO-2026-00125
Date of Issue: January 2, 2026

Property Address: 100 Main St, Millennium Tower
Borough: Manhattan
Block: 1050 | Lot: 12

THIS CERTIFIES that the new building situated on the above-referenced premises has been completed in accordance with the filed plans and specifications and the requirements of the Building Code of the City of New York.

ZONING AND USAGE:
- Zoning District: C5-3 (Commercial, High Density)
- Occupancy Group: Business (Group B)
- Construction Class: 1-A (Fireproof)

LIMITATIONS:
- Floors 1-50: Approved for General Office Use.
- Maximum Occupancy per floor: 150 persons.
- Fire Protection: Fully sprinklered (NFPA 13 compliant).
- Standpipe System: Wet standpipe installed in stairwells A and B.

This certificate allows for immediate occupancy of Floors 30-35 by the tenant."""
    }
]

async def seed_db():
    """PHASE 1: Wipes DB and seeds Users & Matters directly."""
    print("PHASE 1: Seeding Users & Matters (Direct DB Access)...")
    
    # Connect & Init
    client = AsyncIOMotorClient(MONGO_URI)
    # Ensure database name matches your config
    await init_beanie(database=client.lexi_rag_db, document_models=[User, Matter, DocumentFile])

    # Wipe existing data
    await User.delete_all()
    await Matter.delete_all()
    await DocumentFile.delete_all()

    # Create Users
    user_map = {}
    common_hash = get_common_hash()
    
    for u in USERS_DATA:
        user = User(**u, password_hash=common_hash)
        await user.insert()
        user_map[u["key"]] = user
    
    print(f"✓ Created {len(USERS_DATA)} Users.")

    # Create Matters
    matter_id_map = {}
    for k, m in MATTER_MAP.items():
        client_user = user_map.get(m["client_key"])
        team_users = [user_map[t] for t in m["team_keys"] if t in user_map]
        
        matter = Matter(**m, client=client_user, assigned_team=team_users)
        await matter.insert()
        matter_id_map[k] = str(matter.id)

    print(f"✓ Created {len(MATTER_MAP)} Matters.")
    return matter_id_map

async def upload_docs(matter_map):
    """PHASE 2: Uploads text via API to trigger Vectorization."""
    print("\nPHASE 2: Uploading Docs via API (Triggers Vectorization)...")

    async with httpx.AsyncClient(timeout=30.0) as client:
        # 1. Login
        try:
            resp = await client.post(f"{API_BASE}/auth/login", data={
                "username": "bob.vance@lawfirm.com", 
                "password": COMMON_PASSWORD
            })
            
            if resp.status_code != 200:
                print(f"❌ ERROR: Login Failed ({resp.status_code})")
                return
                
            token = resp.json().get("access_token")
            if not token:
                print("❌ ERROR: No token received")
                return
            
            print("✓ Login Successful")
        except Exception as e:
            print(f"❌ ERROR: Could not connect to API. Is the server running? ({e})")
            return

        # 2. Upload Loop
        success_count = 0
        for doc in RAW_DOCS:
            mid = matter_map.get(doc["matter_id"])
            if not mid: continue

            print(f"   Uploading {doc['filename']}...", end=" ", flush=True)
            
            try:
                resp = await client.post(
                    f"{API_BASE}/documents/upload",
                    headers={"Authorization": f"Bearer {token}"},
                    json={
                        "matter_id": mid,
                        "filename": doc["filename"],
                        "content": doc["content_text"],
                        "sensitivity": doc["sensitivity"]
                    }
                )
                
                if resp.status_code == 200:
                    data = resp.json()
                    if data.get('is_vectorized'):
                        print(f"✅ Verified")
                        success_count += 1
                    else:
                        # This catches the 'Warning' state from your Router
                        print(f"⚠️  Saved, but Vector check failed")
                else:
                    print(f"❌ API Error {resp.status_code}")
                    print(f"      {resp.text}")
            except Exception as e:
                print(f"❌ Network Error: {e}")

        print(f"\nSummary: {success_count}/{len(RAW_DOCS)} documents fully vectorized.")

async def main():
    matter_ids = await seed_db()
    await upload_docs(matter_ids)

if __name__ == "__main__":
    if sys.platform == 'win32':
        asyncio.set_event_loop_policy(asyncio.WindowsSelectorEventLoopPolicy())
    asyncio.run(main())