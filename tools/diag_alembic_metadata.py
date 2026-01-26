from db.base import Base

print("=== TABLES IN Base.metadata ===")
for table_name in Base.metadata.tables.keys():
    print("-", table_name)

