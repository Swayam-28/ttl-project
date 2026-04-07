import os
from flask import Flask

app = Flask(__name__)

# ----- Home page -----
@app.route("/")
def home():
    return """
    <html>
    <head>
        <title>My CI/CD Demo App</title>
        <style>
            body { font-family: Arial, sans-serif; max-width: 700px; margin: 60px auto; padding: 0 20px; background: #f5f5f5; }
            h1   { color: #2c3e50; }
            p    { color: #555; line-height: 1.7; }
            a    { display: inline-block; margin: 8px 8px 0 0; padding: 10px 20px;
                   background: #2c3e50; color: white; text-decoration: none; border-radius: 6px; }
            a:hover { background: #3d5166; }
            .badge { display: inline-block; background: #27ae60; color: white;
                     padding: 4px 12px; border-radius: 20px; font-size: 13px; margin-bottom: 16px; }
        </style>
    </head>
    <body>
        <span class="badge">&#10003; Deployed via CI/CD Pipeline</span>
        <h1>Hello from my automated pipeline!</h1>
        <p>This app was automatically built, tested, and deployed using
           <strong>GitHub Actions</strong> and <strong>Docker</strong> —
           no manual steps needed.</p>
        <p>Every time I push code to GitHub, this page updates automatically.</p>
        <a href="/about">About</a>
        <a href="/status">Pipeline Status</a>
    </body>
    </html>
    """

# ----- About page -----
@app.route("/about")
def about():
    return """
    <html>
    <head>
        <title>About - CI/CD Demo</title>
        <style>
            body { font-family: Arial, sans-serif; max-width: 700px; margin: 60px auto; padding: 0 20px; background: #f5f5f5; }
            h1   { color: #2c3e50; }
            li   { color: #555; line-height: 2; }
            a    { color: #2c3e50; }
        </style>
    </head>
    <body>
        <h1>About this project</h1>
        <p>This app demonstrates a fully automated CI/CD pipeline using:</p>
        <ul>
            <li><strong>GitHub</strong> — version control &amp; code storage</li>
            <li><strong>GitHub Actions</strong> — automated build &amp; test runner</li>
            <li><strong>Docker</strong> — packages the app into a container</li>
            <li><strong>Render.com</strong> — hosts the live application</li>
        </ul>
        <p><a href="/">← Back home</a></p>
    </body>
    </html>
    """

# ----- Status page -----
@app.route("/status")
def status():
    return """
    <html>
    <head>
        <title>Status - CI/CD Demo</title>
        <style>
            body { font-family: Arial, sans-serif; max-width: 700px; margin: 60px auto; padding: 0 20px; background: #f5f5f5; }
            h1   { color: #2c3e50; }
            .ok  { background: #eafaf1; border-left: 4px solid #27ae60; padding: 12px 16px; margin: 10px 0; border-radius: 4px; }
            a    { color: #2c3e50; }
        </style>
    </head>
    <body>
        <h1>Pipeline Status</h1>
        <div class="ok">&#10003; App is running</div>
        <div class="ok">&#10003; Docker container healthy</div>
        <div class="ok">&#10003; Last deployment successful</div>
        <p><a href="/">← Back home</a></p>
    </body>
    </html>
    """

# ----- Run -----
if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port)