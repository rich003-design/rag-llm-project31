from app import create_app
from dotenv import load_dotenv

load_dotenv()

app = create_app()

@app.route('/')
def index():
    return "Welcome to the RAG LLM Application!"

# Test route outside the blueprint
@app.route('/test')
def test():
    return "Test route works!"

if __name__ == '__main__':
    app.run(debug=True)

