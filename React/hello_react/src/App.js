import logo from './logo.svg';
import './App.css';

function Header(props) {
    return <header >
        <h1><a href="/" > {props.title} </a></h1>
    </header>
}

function Nav(props) {
    const list = []
    for(let i=0; i<props.topics.length; i++) {
        let topic = props.topics[i];
        list.push(<li key={topic.id}><a href={"./read/"+topic.id}>{topic.title}</a></li>)
    }
    return <nav>
        <ol>
            {/* 자동 */}
            {list}
        </ol>
    </nav>
}

function Article(props) {
    return <article>
        <h2>{props.title}</h2>
        {props.body}
    </article>
}

function App() {
    const topics = [
        {id:1, title:"html", body:"html is ..."},
        {id:2, title:"css", body:"css is ..."},
        {id:3, title:"javascript", body:"javascript is ..."},
    ]
    return (
        <div className="App" >
            <Header title="WEB"> </Header>
            <Nav topics={topics}> </Nav>
            <Article title="Welcome" body="Hello"> </Article>
        </div>
    );
}

export default App;