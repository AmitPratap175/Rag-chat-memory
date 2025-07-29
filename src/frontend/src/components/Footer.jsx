import React from "react";

function Footer() {
  const date = new Date().getFullYear();

  return (
    <div className="flex flex-col text-center justify-center pb-0 pt-2 bottom-0 lg:text-lg text-xs" >
      <div className=" font-semibold" >Brahmware presents you Brahmnaut</div>

      <div>&copy; {date} All rights reseved.</div>

    </div>
  );
}

export default Footer;
