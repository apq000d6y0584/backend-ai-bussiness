import './globals.css';
import NavbarTabs from './components/NavbarTabs';

export const metadata = {
  title: 'BI AI Dashboard',
  description: 'Stock sentiment & recommendations dashboard'
};

export default function RootLayout({ children }) {
  return (
    <html lang="en" className="dark">
      <body>
        <NavbarTabs />
        <div className="min-h-screen">{children}</div>
      </body>
    </html>
  );
}



