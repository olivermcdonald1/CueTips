import Link from 'next/link';

const Home = () => {
  return (
    <div style={{ textAlign: 'center', marginTop: '50px' }}>
      <h1>Welcome to the Pool Game</h1>
      <p>Click below to start the game!</p>
      <Link href="/game">
        {/* <a style={{ fontSize: '20px', padding: '10px', background: 'green', color: 'white', borderRadius: '5px' }}>Start Game</a> */}
      </Link>
    </div>
  );
};

export default Home;
