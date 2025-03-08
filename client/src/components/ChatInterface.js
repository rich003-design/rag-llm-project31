import React, { useState, useEffect, useRef } from 'react';
import ChatMessage from './ChatMessage';

function ChatInterface() {
  const [messages, setMessages] = useState([]);
  const [inputText, setInputText] = useState('');
  const messagesEndRef = useRef(null);

  // Scroll to the bottom of the chat messages
  const scrollToBottom = () => {
    if (messagesEndRef.current) {
      messagesEndRef.current.scrollIntoView({ behavior: "smooth" });
    }
  };

  useEffect(() => {
    scrollToBottom();
  }, [messages]);

  const handleSendMessage = async (event) => {
    event.preventDefault();
    if (!inputText.trim()) return; // Prevent sending empty messages

    // Create user's message and add to history
    const userMessage = { text: inputText, isBot: false };
    const updatedHistory = [...messages, userMessage];

    // Add a new empty bot message for streaming response
    const botMessage = { text: '', isBot: true };
    setMessages([...updatedHistory, botMessage]);
    setInputText('');

    // Prepare request body
    const body = {
      chatHistory: updatedHistory,
      question: inputText,
    };

    // Send the query to the server
    const response = await fetch('http://localhost:5000/handle-query', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify(body),
    });

    if (!response.body) return;

    // Stream the response using a TextDecoderStream
    const decoder = new TextDecoderStream();
    const reader = response.body.pipeThrough(decoder).getReader();
    let accumulatedAnswer = "";

    while (true) {
      const { value, done } = await reader.read();
      if (done) break;
      accumulatedAnswer += value;

      // Capture the current accumulated answer in a local variable
      const newAnswer = accumulatedAnswer;
      setMessages((currentHistory) => {
        const updatedHistory = [...currentHistory];
        const lastChatIndex = updatedHistory.length - 1;
        updatedHistory[lastChatIndex] = {
          ...updatedHistory[lastChatIndex],
          text: newAnswer
        };
        return updatedHistory;
      });
    }
  };

  return (
    <div className="chat-container">
      <header className="chat-header">URL Question & Answer</header>
      {messages.length === 0 && (
        <div className="chat-message bot-message">
          <p className="initial-message">
            Hi there! I'm a bot trained to answer questions about the URL you entered. Try asking me a question below!
          </p>
        </div>
      )}
      <div className="chat-messages">
        {messages.map((message, index) => (
          <ChatMessage key={index} message={message} />
        ))}
        <div ref={messagesEndRef} />
      </div>
      <form className="chat-input" onSubmit={handleSendMessage}>
        <input
          type="text"
          placeholder="Type a question and press enter ..."
          value={inputText}
          onChange={(e) => setInputText(e.target.value)}
        />
      </form>
    </div>
  );
}

export default ChatInterface;
