import React, { useEffect, useState } from 'react';

function App() {
  const [events, setEvents] = useState([]);

  const fetchEvents = async () => {
    try {
      
      const response = await fetch('http://localhost:5000/api/actions', {
        headers: { 'ngrok-skip-browser-warning': 'true' }
      });
      const data = await response.json();
      setEvents(data);
    } catch (err) {
      console.error("Fetch error:", err);
    }
  };

  useEffect(() => {
    fetchEvents();
    const interval = setInterval(fetchEvents, 15000); 
    return () => clearInterval(interval);
  }, []);

  return (
    <div style={{ padding: '40px', fontFamily: 'Arial' }}>
      <h1>GitHub Activity Monitor</h1>
      <div style={{ background: '#f4f4f4', padding: '20px', borderRadius: '8px' }}>
        {events.length === 0 ? <p>Waiting for events...</p> : (
          events.map((ev, index) => (
            <div key={index} style={{ borderBottom: '1px solid #ddd', padding: '10px 0' }}>
              <strong>{ev.author}</strong> {ev.action === 'PUSH' ? 'pushed to' : 'merged branch'} 
              <strong> {ev.to_branch}</strong> on {ev.timestamp}
            </div>
          ))
        )}
      </div>
    </div>
  );
}

export default App;