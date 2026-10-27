from database import (
    create_database,
    add_complaint,
    get_complaint,
    get_all_complaints
)

create_database()

new_id = add_complaint(
    "Test Resident",
    "Water Supply",
    "Building A",
    "Water supply is not working."
)

print("New complaint ID:", new_id)
print("Complaint details:", get_complaint(new_id))
print("All complaints:", get_all_complaints())