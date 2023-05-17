function Messages(props) {
    const [messages, setMessages] = React.useState([]);
  
    React.useEffect(() => {
      const intervalId = setInterval(() => {
        fetch('/api/messages')
          .then(response => response.json())
          .then(data => setMessages(data));
      }, props.interval);
  
      return () => clearInterval(intervalId);
    }, [props.interval]);
  
    return (
      <div>
        <div>{messages.map((item) =>
          <p>{item}</p>
        )}</div>
      </div>
    );
  }
  
  ReactDOM.render(<Messages interval={1000} />, document.getElementById("messages"));
  