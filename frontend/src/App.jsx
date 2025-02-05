import { useState, useEffect, useRef } from 'react';
import { Send, Upload, Archive } from 'lucide-react';

const API_URL = 'http://127.0.0.1:3000';

const MessageLoadingIndicator = () => (
  <div className="flex justify-start w-full">
    <div className="bg-gray-800 rounded-lg p-4 max-w-[80%] shadow-lg">
      <div className="flex items-center space-x-4">
        <div className="w-8 h-8 bg-blue-500 rounded-full animate-pulse" />
        <div className="space-y-2">
          <div className="h-2 w-48 bg-gray-600 rounded animate-pulse" />
          <div className="h-2 w-32 bg-gray-600 rounded animate-pulse" />
        </div>
      </div>
    </div>
  </div>
);

const App = () => {
  const [messages, setMessages] = useState([]);
  const [input, setInput] = useState('');
  const [isLoading, setIsLoading] = useState(false);
  const [isUploading, setIsUploading] = useState(false);
  const [isFollowUp, setIsFollowUp] = useState(false)
  const messagesEndRef = useRef(null);
  const fileInputRef = useRef(null);

  // Scroll to bottom when response arrives
  const scrollToBottom = () => {
    messagesEndRef.current?.scrollIntoView({ behavior: "smooth" });
  };

  useEffect(() => {
    // Get greeting message from Ollama LLM
    const fetchGreeting = async () => {
      setIsLoading(true);
      try {
        const response = await fetch(`${API_URL}/start`, {
          method: 'GET',
          headers: {
            'Content-Type': 'application/json',
          },
        });
        const data = await response.json();
        setMessages([{ type: 'assistant', content: data.response }]);
      } catch (error) {
        console.error('Error fetching greeting:', error);
      } finally {
        // Response recieved
        setIsLoading(false);
      }
    };

    fetchGreeting();
  }, []);

  useEffect(() => {
    scrollToBottom();
  }, [messages, isLoading]);

  const handleSubmit = async (e) => {
    e.preventDefault();
    if (!input.trim()) return;

    const userMessage = input.trim();
    setInput('');
    setMessages(prev => [...prev, { type: 'user', content: userMessage }]);
    setIsLoading(true);

    // Send message to backend
    try {
      const response = await fetch(`${API_URL}/query`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({ "prompt": userMessage }),
      });

      if (!response.ok) {
        throw new Error(`HTTP error! status: ${response.status}`);
      }

      // Get response
      const data = await response.json();
      
      if (!data || !data.response) {
        throw new Error('Invalid response format from server');
      }

      setMessages(prev => [...prev, { type: 'assistant', content: data.response }]);
    } catch (error) {
      console.error('Error sending message:', error);
      setMessages(prev => [...prev, {
        type: 'error',
        content: `Error: ${error.message || 'Failed to send message. Please try again.'}`
      }]);
    } finally {
      setIsLoading(false);
    }
  };

  // Function to handle file uploads
  const handleFileUpload = async (event) => {
    const file = event.target.files?.[0];
    if (!file) return;

    setIsUploading(true);
    const formData = new FormData();
    formData.append('file', file);

    try {
      // Send route for file upload, to be implemented
      const response = await fetch(`${API_URL}/send`, {
        method: 'POST',
        body: formData,
      });

      if (!response.ok) throw new Error('Upload failed');

      setMessages(prev => [...prev, {
        type: 'system',
        content: `Successfully uploaded ${file.name}`
      }]);
    } catch (error) {
      console.error('Error uploading file:', error);
      setMessages(prev => [...prev, {
        type: 'error',
        content: `Failed to upload ${file.name}`
      }]);
    } finally {
      setIsUploading(false);
      if (fileInputRef.current) {
        fileInputRef.current.value = '';
      }
    }
  };

  return (
    <div className="flex h-screen bg-gray-900">
      {/* Sidebar */}
      <div className="w-45 bg-gray-800 p-4 flex flex-col">
        <div className="flex items-center space-x-2 mb-8">
          <Archive className="w-8 h-8 text-blue-500" />
          <span className="text-xl font-bold text-white">ArchiveAI</span>
        </div>

        <div className="flex-1">
          <div className="relative">
            <input
              type="file"
              ref={fileInputRef}
              onChange={handleFileUpload}
              accept=".pdf"
              className="hidden"
              id="file-upload"
            />
            {/*File upload feature to be implemented*/}
            <label
              htmlFor="file-upload"
              className={`flex items-center justify-center space-x-2 bg-gray-700 hover:bg-gray-600 text-white rounded-lg p-3 cursor-pointer transition-colors ${isUploading ? 'opacity-50 cursor-not-allowed' : ''
                }`}
            >
              <Upload className="w-5 h-5" />
              <span>{isUploading ? 'Uploading...' : 'Upload PDF'}</span>
            </label>
          </div>
        </div>
      </div>

      {/* Main Chat Area */}
      <div className="flex-1 flex flex-col">
        <div className="flex-1 overflow-y-auto p-4 space-y-4">
          {messages.map((message, index) => (
            <div
              key={index}
              className={`flex ${message.type === 'user' ? 'justify-end' : 'justify-start'}`}
            >
              <div
                className={`max-w-[80%] rounded-lg p-4 ${message.type === 'user'
                    ? 'bg-blue-600 text-white'
                    : message.type === 'error'
                      ? 'bg-red-600 text-white'
                      : message.type === 'system'
                        ? 'bg-green-600 text-white'
                        : 'bg-gray-800 text-gray-100'
                  }`}
              >
                {message.content}
              </div>
            </div>
          ))}
          {isLoading && <MessageLoadingIndicator />}
          <div ref={messagesEndRef} />
        </div>

        <form onSubmit={handleSubmit} className="p-4 border-t border-gray-800">
          <div className="flex space-x-4">
            <input
              type="text"
              value={input}
              onChange={(e) => {
                setInput(e.target.value)
                setIsFollowUp(e.target.value.startsWith("/followup"))
              }}
              placeholder="Type your message..."
              className={`flex-1 bg-gray-800 text-gray-100 rounded-lg px-4 py-2 focus:outline-none focus:ring-2 focus:ring-blue-500 ${isFollowUp ? "font-mono text-primary" : ""
                }`}
              disabled={isLoading}
            />
            <button
              type="submit"
              onClick={() => setIsFollowUp(false)}
              disabled={isLoading || !input.trim()}
              className="bg-blue-600 text-white rounded-lg px-4 py-2 hover:bg-blue-700 focus:outline-none focus:ring-2 focus:ring-blue-500 disabled:opacity-50 disabled:cursor-not-allowed"
            >
              <Send className="w-5 h-5" />
            </button>
          </div>
        </form>
      </div>
    </div>
  );
};

export default App;