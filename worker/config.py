import os


DEFAULT_PROFILE_IMAGE_URL = "https://www.chcf.org/wp-content/themes/chcf_theme/images/default-profile-pic.jpg"
DATABASE_URL = os.getenv("PGRST_DB_URI")
DATABASE_REST_URL = os.getenv("DATABASE_REST_URL")
ELASTICSEARCH_URL = os.getenv("ELASTICSEARCH_URL")
