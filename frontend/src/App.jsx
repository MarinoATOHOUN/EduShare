/**
 * Main App Component for PDF Course Sharing Platform
 * Developed by Marino ATOHOUN
 */

import React, { useState, useEffect } from 'react';
import { BrowserRouter as Router, Routes, Route } from 'react-router-dom';
import { AuthProvider } from './hooks/useAuth';
import { ThemeProvider } from './hooks/useTheme';
import { Toaster } from '@/components/ui/toaster';
import Navbar from './components/Navbar';
import Footer from './components/Footer';
import HomePage from './components/HomePage';
import LoginPage from './components/LoginPage';
import RegisterPage from './components/RegisterPage';
import DocumentsPage from './components/DocumentsPage';
import UploadPage from './components/UploadPage';
import ProfilePage from './components/ProfilePage';
import DocumentDetailPage from './components/DocumentDetailPage';
import TermsPage from './components/TermsPage';
import PrivacyPage from './components/PrivacyPage';
import ProtectedRoute from './components/ProtectedRoute';
import AdDisplay from './components/AdDisplay';
import DeveloperApiPage from './components/DeveloperApiPage';
import PricingPage from './components/PricingPage';
import './App.css';

function App() {
  const [timerAdKey, setTimerAdKey] = useState(0);

  useEffect(() => {
    // Trigger a timer ad every 2 minutes
    const interval = setInterval(() => {
      setTimerAdKey(prev => prev + 1);
    }, 120000); // 2 minutes

    return () => clearInterval(interval);
  }, []);

  return (
    <ThemeProvider defaultTheme="light" storageKey="vite-ui-theme">
      <AuthProvider>
        <Router>
          <div className="min-h-screen bg-background">
            <AdDisplay triggerAction="on_load" />
            <AdDisplay key={`timer-ad-${timerAdKey}`} triggerAction="on_timer" />
            <Navbar />
            <main className="container mx-auto px-4 py-8">
              <Routes>
                <Route path="/" element={<HomePage />} />
                <Route path="/login" element={<LoginPage />} />
                <Route path="/register" element={<RegisterPage />} />
                <Route path="/documents" element={<DocumentsPage />} />
                <Route path="/documents/:id" element={<DocumentDetailPage />} />
                <Route path="/terms" element={<TermsPage />} />
                <Route path="/privacy" element={<PrivacyPage />} />
                <Route path="/developers" element={<DeveloperApiPage />} />
                <Route path="/pricing" element={<PricingPage />} />
                <Route
                  path="/upload"
                  element={
                    <ProtectedRoute>
                      <UploadPage />
                    </ProtectedRoute>
                  }
                />
                <Route
                  path="/profile"
                  element={
                    <ProtectedRoute>
                      <ProfilePage />
                    </ProtectedRoute>
                  }
                />
              </Routes>
            </main>
            <Footer />
            <Toaster />
          </div>
        </Router>
      </AuthProvider>
    </ThemeProvider>
  );
}

export default App;
