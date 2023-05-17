function Clock() {
  const [time, setTime] = React.useState(new Date());

  React.useEffect(() => {
    const intervalId = setInterval(() => {
      setTime(new Date());
    }, 1000);

    return () => clearInterval(intervalId);
  }, []);

  const date = time.toLocaleDateString();

  return (
    <div style={{display: "flex"}}>
      <h5>Date:&nbsp;</h5>
      <h5>{date}&nbsp;</h5>
      <h5 style={{marginLeft: "10px"}}>Time:&nbsp;</h5>
      <h5>{time.toLocaleTimeString()}</h5>
    </div>
  );
}

ReactDOM.render(<Clock/>, document.getElementById("clock"));
