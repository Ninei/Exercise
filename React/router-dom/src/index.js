import React from 'react';
import ReactDOM from 'react-dom/client';
import './index.css';
// import App from './App';
import reportWebVitals from './reportWebVitals';

import {BrowserRouter, Route, Routes, NavLink} from 'react-router-dom';

function Home() {
  return(
    <div>
        <h2>Home</h2>
        Home ...
    </div>
  )
}

var contents = [
  {id:1, title:"HTML", description:"HTML is ..."},
  {id:2, title:"JS", description:"JS is ..."},
  {id:3, title:"React", description:"React is ..."}
]

function Topics() {
  var lis = [];
  for(var i=0; i<contents.length; i++) {
    lis.push(<li><NavLink to={"topics"+contents[i].id>contents[i].description}></NavLink></li>)
  }
  return(
    <div>
        <h2>Topics</h2>
        <ul>
          <li><NavLink to="/topics/1">HTML</NavLink></li>
          <li><NavLink to="/topics/2">JS</NavLink></li>
          <li><NavLink to="/topics/3">React</NavLink></li>
        </ul>
      <Routes>
        <Route path="/topics/1">HTML is ...</Route>
        <Route path="/topics/2">JS is ...</Route>
        <Route path="/topics/3" element={<div>React is ...</div>}></Route>
      </Routes>
    </div>
  )
}


function Contact() {
  return(
    <div>
        <h2>Contact</h2>
        Contact ...
    </div>
  )
}

function NotFound() {
  return(
    <div>
        <h2>NotFound</h2>
        NotFound ...
    </div>
  )
}

function App(params) {
  return (
    <div>
      <h1>React Router DOM example</h1>
      <ul>
        <li><NavLink to="/">Home</NavLink></li>
        <li><NavLink to="/topics">Topics</NavLink></li>
        <li><NavLink to="/contact">Contact</NavLink></li>
      </ul>
      <Routes>
        <Route path="/topics/*" element={<Topics></Topics>}></Route>
        <Route path="/contact/*" element={<Contact></Contact>}></Route>
        <Route path="/" element={<Home></Home>}></Route>
        <Route path="/*" element={<NotFound />} />
      </Routes>
    </div>
  )
}

const root = ReactDOM.createRoot(document.getElementById('root'));
root.render(
  <React.StrictMode>
    <BrowserRouter><App /></BrowserRouter>
  </React.StrictMode>
);

// If you want to start measuring performance in your app, pass a function
// to log results (for example: reportWebVitals(console.log))
// or send to an analytics endpoint. Learn more: https://bit.ly/CRA-vitals
reportWebVitals();
