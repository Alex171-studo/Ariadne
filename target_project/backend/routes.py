from flask import Flask
app = Flask(__name__)

@app.get("/")
def home():
    return {
        "status":"ok",
        "version":"1.2.0"
    }

@app.get("/health")
def health():
    return {
        "database":"connected",
        "cache":"running"
    }