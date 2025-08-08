import Link from "next/link";

const Header = () => {
  return (
    <header className="bg-gray-800 text-white p-4">
      <nav className="container mx-auto flex justify-between">
        <Link href="/" className="text-xl font-bold">
          AI Tutor
        </Link>
        <ul className="flex space-x-4">
          <li><Link href="/upload">Upload Book</Link></li>
          <li><Link href="/study-plan">Study Plan</Link></li>
          <li><Link href="/chat">Tutor Chat</Link></li>
          <li><Link href="/code-lab">Code Lab</Link></li>
        </ul>
      </nav>
    </header>
  );
};

export default Header;

