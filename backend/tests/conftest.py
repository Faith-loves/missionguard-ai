import os

# Tests never require the developer's NASA key or a real Firebase project.
os.environ["NASA_API_KEY"] = "test-nasa-key"
os.environ["FIREBASE_PROJECT_ID"] = "test-project"
