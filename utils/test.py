import sys
import os
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from utils.firebase import save_user, get_user_by_id
save_user("naveen-1609", {"access_token": "abc123", "plan": "20-day"})
print(get_user_by_id("naveen-1609"))
