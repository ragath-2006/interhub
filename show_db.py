import sys
import json
from datetime import datetime
from bson import ObjectId
from db_mongo import db

class MongoEncoder(json.JSONEncoder):
    def default(self, o):
        if isinstance(o, ObjectId):
            return str(o)
        if isinstance(o, datetime):
            return o.strftime("%Y-%m-%d %H:%M:%S")
        return super().default(o)

def print_banner():
    print("=" * 65)
    print("        INTERNHUB - MONGODB DATABASE EXPLORER        ")
    print("=" * 65)
    print("Database Name: internhub_db")
    print("Connection   : mongodb://localhost:27017")
    print("-" * 65)

def show_summary():
    print_banner()
    collections = sorted(db.list_collection_names())
    print(f"{'Collection Name':<25} | {'Total Documents':<15}")
    print("-" * 65)
    total_docs = 0
    for col in collections:
        cnt = db[col].count_documents({})
        total_docs += cnt
        print(f" {col:<24} | {cnt:<15}")
    print("-" * 65)
    print(f" Total Records Across Collections: {total_docs}")
    print("=" * 65)
    print("\nHow to view details:")
    print("  python show_db.py students       -> View all student resumes")
    print("  python show_db.py companies      -> View registered companies")
    print("  python show_db.py internships    -> View all internship postings")
    print("  python show_db.py applications   -> View candidate applications")
    print("  python show_db.py reviews        -> View verified reviews")
    print("  python show_db.py users          -> View user accounts & roles")
    print("  python show_db.py --all          -> View full dump of all collections\n")

def show_collection(col_name):
    if col_name not in db.list_collection_names():
        print(f"Error: Collection '{col_name}' does not exist.")
        print(f"Available collections: {', '.join(sorted(db.list_collection_names()))}")
        return

    print_banner()
    count = db[col_name].count_documents({})
    print(f"COLLECTION: [{col_name.upper()}] - {count} Document(s)")
    print("-" * 65)
    
    docs = list(db[col_name].find())
    for idx, doc in enumerate(docs, 1):
        print(f"\n--- [Document #{idx} | ID: {doc.get('_id')} ] ---")
        doc_clean = {k: v for k, v in doc.items() if k != '_id'}
        print(json.dumps(doc_clean, indent=2, cls=MongoEncoder, ensure_ascii=False))
    print("=" * 65)

def main():
    if len(sys.argv) < 2:
        show_summary()
    elif sys.argv[1] == '--all':
        print_banner()
        for col in sorted(db.list_collection_names()):
            show_collection(col)
    else:
        show_collection(sys.argv[1].lower().strip())

if __name__ == '__main__':
    main()
