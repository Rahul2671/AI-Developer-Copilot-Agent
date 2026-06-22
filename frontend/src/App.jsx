import Upload from "./components/Upload";
import Chat from "./components/Chat";
import "./App.css";

function App() {

  return (
    <div className="container">

      <h1>
        AI Developer Copilot Agent
      </h1>

      <p>
        Upload your repository and chat with your codebase
      </p>


      <div className="card">

        <Upload />

      </div>


      <div className="card">

        <Chat />

      </div>


    </div>
  )
}

export default App;