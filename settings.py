import os
from dotenv import load_dotenv

load_dotenv()

# the second argument for both lines below are just convetion
REDIS_URL = os.getenv("REDIS_URL", "redis://localhost:6379")
# default is the default queue name in rq, we are not using it
QUEUES = ["emails", "default"]