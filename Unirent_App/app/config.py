class Config:
    # Image configuration
    ALLOWED_IMAGE_EXTENSIONS = ['jpg', 'jpeg', 'png', 'gif']
    MAX_IMAGE_SIZE = 8 * 1024 * 1024  # 8MB
    FALLBACK_IMAGE_URL = "/static/images/fallback.jpg"