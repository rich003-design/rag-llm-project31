import React, { useState, useEffect } from 'react';
import UrlInput from './components/UrlInput';
import ChatInterface from './components/ChatInterface';

function App() {
  const [showChat, setShowChat] = useState(false);

  const handleUrlSubmitted = () => {
    setShowChat(true); // Transition from URL input to the chat interface.
  };

  useEffect(() => {
    // Cleanup effect: when the component is unmounted (e.g., on page refresh or navigation),
    // send a POST request to delete the index on the backend.
    return () => {
      // Using relative URL to let the proxy (if configured) forward to http://localhost:5000
      fetch('/delete-index', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' }
      })
        .then(response => {
          if (!response.ok) {
            console.error('Error deleting index:', response.statusText);
          } else {
            console.log('Successfully deleted index');
          }
        })
        .catch(error => {
          console.error('Error during delete-index fetch:', error);
        });
    };
  }, []);

  return (
    <div className="App">
      {!showChat ? (
        <UrlInput onSubmit={handleUrlSubmitted} />
      ) : (
        <ChatInterface />
      )}
    </div>
  );
}

export default App;
