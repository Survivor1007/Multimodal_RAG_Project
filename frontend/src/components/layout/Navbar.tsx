import { Link, useLocation } from "react-router-dom";
import { useThemeStore } from "../../store/themeStore";
import {
  Sparkles,
  Bot,
  FileText,
  BarChart3,
  Sun,
  Moon,
  Layers,
} from "lucide-react";
import { Github } from "../../layouts/GithubIcon";

export default function Navbar() {
  const { theme, toggleTheme } = useThemeStore();
  const location = useLocation();

  const navLinks = [
    { name: "Overview", path: "/", icon: Layers },
    { name: "RAG Assistant", path: "/chat", icon: Bot },
    { name: "Documents & Search", path: "/documents", icon: FileText },
    { name: "Analytics & Fine-Tuning", path: "/analytics", icon: BarChart3 },
  ];

  return (
    <header className="sticky top-0 z-50 w-full border-b border-slate-200/80 dark:border-slate-800/80 bg-white/80 dark:bg-slate-950/80 backdrop-blur-md transition-colors">
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
        <div className="flex items-center justify-between h-16">
          {/* Logo & Brand */}
          <Link to="/" className="flex items-center gap-2 group">
            <div className="p-2 rounded-xl bg-gradient-to-tr from-brand-600 to-indigo-500 text-white shadow-md shadow-brand-500/20 group-hover:scale-105 transition-transform">
              <Sparkles className="w-5 h-5" />
            </div>
            <div>
              <span className="text-lg font-bold bg-gradient-to-r from-slate-900 via-brand-600 to-indigo-600 dark:from-white dark:via-brand-400 dark:to-indigo-400 bg-clip-text text-transparent">
                Multimodal RAG
              </span>
              <span className="hidden sm:inline-block ml-2 text-xs font-semibold px-2 py-0.5 rounded-full bg-brand-500/10 text-brand-600 dark:text-brand-400 border border-brand-500/20">
                v2.0 Hybrid
              </span>
            </div>
          </Link>

          {/* Nav Links */}
          <nav className="hidden md:flex items-center gap-1 bg-slate-100/80 dark:bg-slate-900/80 p-1 rounded-xl border border-slate-200/60 dark:border-slate-800/60">
            {navLinks.map((link) => {
              const Icon = link.icon;
              const isActive = location.pathname === link.path;
              return (
                <Link
                  key={link.path}
                  to={link.path}
                  className={`flex items-center gap-2 px-3 py-1.5 rounded-lg text-sm font-medium transition-all ${
                    isActive
                      ? "bg-white dark:bg-slate-800 text-brand-600 dark:text-brand-400 shadow-sm"
                      : "text-slate-600 dark:text-slate-400 hover:text-slate-900 dark:hover:text-white"
                  }`}
                >
                  <Icon className="w-4 h-4" />
                  {link.name}
                </Link>
              );
            })}
          </nav>

          {/* Right Action Icons */}
          <div className="flex items-center gap-3">
            {/* Theme Toggle Button */}
            <button
              onClick={toggleTheme}
              className="p-2 rounded-xl border border-slate-200 dark:border-slate-800 bg-white dark:bg-slate-900 text-slate-700 dark:text-slate-300 hover:bg-slate-100 dark:hover:bg-slate-800 transition-colors"
              title={`Switch to ${theme === "dark" ? "light" : "dark"} mode`}
            >
              {theme === "dark" ? (
                <Sun className="w-5 h-5 text-amber-400" />
              ) : (
                <Moon className="w-5 h-5 text-indigo-600" />
              )}
            </button>

            {/* GitHub Repo Button */}
            <a
              href="https://github.com"
              target="_blank"
              rel="noreferrer"
              className="hidden sm:flex items-center gap-2 px-3 py-2 rounded-xl text-sm font-medium border border-slate-200 dark:border-slate-800 bg-white dark:bg-slate-900 text-slate-700 dark:text-slate-300 hover:bg-slate-100 dark:hover:bg-slate-800 transition-colors"
            >
              <Github className="w-4 h-4" />
              <span>GitHub</span>
            </a>
          </div>
        </div>

        {/* Mobile Navigation Links */}
        <div className="flex md:hidden items-center justify-around py-2 border-t border-slate-200/60 dark:border-slate-800/60">
          {navLinks.map((link) => {
            const Icon = link.icon;
            const isActive = location.pathname === link.path;
            return (
              <Link
                key={link.path}
                to={link.path}
                className={`flex flex-col items-center gap-1 text-xs font-medium ${
                  isActive
                    ? "text-brand-600 dark:text-brand-400 font-bold"
                    : "text-slate-500 dark:text-slate-400"
                }`}
              >
                <Icon className="w-4 h-4" />
                {link.name.split(" ")[0]}
              </Link>
            );
          })}
        </div>
      </div>
    </header>
  );
}
