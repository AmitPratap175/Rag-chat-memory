import { BrowserRouter, Routes, Route } from "react-router-dom";
import Price from "./Pages/Price";
import Support from "./Pages/Support";
import Bots from "./Pages/Bots";
import Home from "./Pages/Home";
import Footer from "./components/Footer";

function App() {
  return (
    <BrowserRouter>
      

      <Routes>
        <Route path="/" element={<Home />} />

        <Route path="/support" element={<Support />} />

        <Route path="/bots" element={<Bots />} />

        <Route path="/pricing" element={<Price />} />
      </Routes>

        {/* <Footer /> */}
    </BrowserRouter>
  );
}

export default App;
