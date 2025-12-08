/**
 * Header component for the Scanity application
 */
import React from 'react';
import { Link } from 'react-router-dom';
import { Shield, Zap, BarChart3, Menu, X } from 'lucide-react';
import { useState } from 'react';

interface HeaderProps {
  transparent?: boolean;
}

export const Header: React.FC<HeaderProps> = ({ transparent = false }) => {
  const [mobileMenuOpen, setMobileMenuOpen] = useState(false);

  const navigation = [
    { name: 'Home', href: '/', icon: Shield },
    { name: 'About', href: '/about', icon: BarChart3 },
  ];

  return (
    <header className={`${
      transparent
        ? 'absolute inset-x-0 top-0 z-50'
        : 'relative'
    }`}>
      <nav className="flex items-center justify-between p-6 lg:px-8" aria-label="Global">
        <div className="flex lg:flex-1">
          <Link to="/" className="-m-1.5 p-1.5">
            <span className="sr-only">Scanity</span>
            <div className="flex items-center space-x-2">
              <div className="h-8 w-8 bg-primary-500 rounded-lg flex items-center justify-center">
                <Shield className="h-5 w-5 text-white" />
              </div>
              <span className="text-xl font-bold text-white">Scanity</span>
            </div>
          </Link>
        </div>

        {/* Desktop navigation */}
        <div className="hidden lg:flex lg:gap-x-12">
          {navigation.map((item) => {
            const Icon = item.icon;
            return (
              <Link
                key={item.name}
                to={item.href}
                className="flex items-center space-x-1 text-sm font-semibold leading-6 text-text-secondary hover:text-text-primary transition-colors"
              >
                <Icon className="h-4 w-4" />
                <span>{item.name}</span>
              </Link>
            );
          })}
        </div>

        {/* CTA buttons */}
        <div className="hidden lg:flex lg:flex-1 lg:justify-end">
          <div className="flex items-center space-x-4">
            <a
              href="https://github.com"
              target="_blank"
              rel="noopener noreferrer"
              className="text-text-secondary hover:text-text-primary transition-colors"
            >
              GitHub
            </a>
            <button className="btn btn-primary">
              Get Started
            </button>
          </div>
        </div>

        {/* Mobile menu button */}
        <div className="flex lg:hidden">
          <button
            type="button"
            className="-m-2.5 inline-flex items-center justify-center rounded-md p-2.5 text-text-secondary hover:text-text-primary"
            onClick={() => setMobileMenuOpen(true)}
          >
            <span className="sr-only">Open main menu</span>
            <Menu className="h-6 w-6" aria-hidden="true" />
          </button>
        </div>
      </nav>

      {/* Mobile menu */}
      {mobileMenuOpen && (
        <div className="lg:hidden fixed inset-0 z-50">
          <div className="fixed inset-0 bg-black bg-opacity-75" onClick={() => setMobileMenuOpen(false)} />
          <div className="fixed inset-y-0 right-0 z-50 w-full overflow-y-auto bg-background-secondary px-6 py-6 sm:max-w-sm sm:ring-1 sm:ring-white sm:ring-opacity-10">
            <div className="flex items-center justify-between">
              <Link to="/" className="-m-1.5 p-1.5">
                <span className="sr-only">Scanity</span>
                <div className="flex items-center space-x-2">
                  <div className="h-8 w-8 bg-primary-500 rounded-lg flex items-center justify-center">
                    <Shield className="h-5 w-5 text-white" />
                  </div>
                  <span className="text-xl font-bold text-white">Scanity</span>
                </div>
              </Link>
              <button
                type="button"
                className="-m-2.5 rounded-md p-2.5 text-text-secondary hover:text-text-primary"
                onClick={() => setMobileMenuOpen(false)}
              >
                <span className="sr-only">Close menu</span>
                <X className="h-6 w-6" aria-hidden="true" />
              </button>
            </div>

            <div className="mt-6 flow-root">
              <div className="-my-6 divide-y divide-background-tertiary">
                <div className="space-y-2 py-6">
                  {navigation.map((item) => {
                    const Icon = item.icon;
                    return (
                      <Link
                        key={item.name}
                        to={item.href}
                        className="flex items-center space-x-2 -mx-3 block rounded-lg px-3 py-2 text-base font-semibold leading-7 text-text-secondary hover:bg-background-tertiary hover:text-text-primary transition-colors"
                        onClick={() => setMobileMenuOpen(false)}
                      >
                        <Icon className="h-5 w-5" />
                        <span>{item.name}</span>
                      </Link>
                    );
                  })}
                </div>
                <div className="py-6">
                  <div className="flex flex-col space-y-4">
                    <a
                      href="https://github.com"
                      target="_blank"
                      rel="noopener noreferrer"
                      className="block -mx-3 rounded-lg px-3 py-2.5 text-base font-semibold leading-7 text-text-secondary hover:bg-background-tertiary hover:text-text-primary transition-colors"
                    >
                      GitHub
                    </a>
                    <button className="btn btn-primary w-full">
                      Get Started
                    </button>
                  </div>
                </div>
              </div>
            </div>
          </div>
        </div>
      )}
    </header>
  );
};

export default Header;