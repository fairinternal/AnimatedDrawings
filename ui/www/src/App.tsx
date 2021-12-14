import React from "react";
import {
  BrowserRouter as Router,
  Switch,
  Route,
  Redirect,
} from "react-router-dom";
import "./assets/scss/root.scss";
import MainPage from "./containers/MainPage";
import SharingPage from "./containers/SharingPage";
import HomePage from "./containers/HomePage";
import TermsPage from "./containers/TermsPage";
import AboutPage from "./containers/AboutPage";
import CookieBanner from "./components/Banners/CookieBanner";

function App() {
  return (
    <Router>
      <Switch>
        <Route exact path="/">
          <HomePage />
        </Route>
        <Route path="/canvas">
          <MainPage />
        </Route>
        <Route path="/share/:videoId/:type">
          <SharingPage />
        </Route>
        <Route path="/terms">
          <TermsPage />
        </Route>
        <Route path="/about">
          <AboutPage />
        </Route>
        <Redirect from="*" to="/" />
      </Switch>
      <CookieBanner />
    </Router>
  );
}

export default App;
