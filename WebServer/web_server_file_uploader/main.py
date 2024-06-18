from fastapi import FastAPI
from fastapi import UploadFile
import os
from fastapi import File
import shutil
from fastapi.responses import HTMLResponse


app = FastAPI()

@app.get("/", response_class=HTMLResponse)
async def main():
    content = """
<!DOCTYPE html>
<html>
    <head>
        <title>Upload a file</title>
    </head>
    <body>
        <h1>Upload a file</h1>
        <form action="/uploadfile/" method="post" enctype="multipart/form-data">
            <input type="file" name="file">
            <input type="submit">
        </form>
    </body>
</html>
    """
    return content


@app.get('/hello') #decorator function
def hello():
    return "Hello"

@app.get('/bye') #decorator function
def bye():
    return "Bye"

@app.get('/led/{led_number}/{status}')
def change_led_state(led_number:str, status: int): 
    str_status = 'ON' if status > 0 else 'OFF'
    return f"led {led_number} turned {status}"

if __name__ == '__main__':
    import uvicorn
    #comment
    uvicorn.run(app, host='0.0.0.0', port= 8080)

@app.post('/uploadfile')
def upload_file(file: UploadFile = File(...)):
    try:
        os.makedirs('./uploads', exist_ok=True)
        with open(f'./uploads/{file.filename}', "wb+") as f:
            shutil.copyfileobj(file.file, f)
        return "ok"
    except Exception as e:
        return f"Upload failed due to {e}"
    
    
