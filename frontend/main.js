const { app, BrowserWindow, ipcMain } = require('electron')
const path = require('path')
const { spawn } = require('child_process')

let pythonProcess = null
let mainWindow = null

function createPythonProcess() {
  // We use 'uv run' to execute the python script in the correct environment
  // Adjust the path to where your backend folder is relative to main.js
  const backendPath = path.join(__dirname, '..', 'backend')

  // Windows: cmd /c uv run ... might be safer if uv isn't in PATH for the app
  // But let's try direct execution first.
  pythonProcess = spawn('uv', ['run', 'python', '-m', 'app.main'], {
    cwd: backendPath,
    shell: true // creating a shell to ensure PATH is loaded
  })

  pythonProcess.stdout.on('data', (data) => {
    console.log(`Python stdout: ${data}`)
    if (mainWindow) {
      mainWindow.webContents.send('python-data', data.toString())
    }
  })

  pythonProcess.stderr.on('data', (data) => {
    console.error(`Python stderr: ${data}`)
  })

  pythonProcess.on('close', (code) => {
    console.log(`Python process exited with code ${code}`)
    pythonProcess = null
  })
}

function createWindow() {
  mainWindow = new BrowserWindow({
    width: 800,
    height: 600,
    webPreferences: {
      preload: path.join(__dirname, 'preload.js'),
      contextIsolation: true,
      nodeIntegration: false
    }
  })

  mainWindow.loadFile('index.html')

  // Open DevTools for debugging
  // mainWindow.webContents.openDevTools()
}

app.whenReady().then(() => {
  createPythonProcess()
  createWindow()

  ipcMain.on('to-python', (event, arg) => {
    if (pythonProcess) {
      pythonProcess.stdin.write(JSON.stringify(arg) + '\n')
    }
  })

  app.on('activate', () => {
    if (BrowserWindow.getAllWindows().length === 0) {
      createWindow()
    }
  })
})

app.on('window-all-closed', () => {
  if (pythonProcess) {
    pythonProcess.kill()
  }
  if (process.platform !== 'darwin') {
    app.quit()
  }
})
