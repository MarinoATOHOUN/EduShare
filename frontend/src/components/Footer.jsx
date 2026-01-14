/**
 * Footer Component for PDF Course Sharing Platform
 * Developed by Marino ATOHOUN for BlackBenAI
 */

import React from 'react';
import { Link } from 'react-router-dom';
import { BookOpen } from 'lucide-react';

const Footer = () => {
    return (
        <footer className="border-t bg-card mt-auto">
            <div className="container mx-auto px-4 py-8">
                <div className="grid grid-cols-1 md:grid-cols-3 gap-8">
                    {/* Brand */}
                    <div className="space-y-4">
                        <Link to="/" className="flex items-center space-x-2">
                            <BookOpen className="h-6 w-6 text-primary" />
                            <span className="text-lg font-bold text-foreground">EduShare</span>
                        </Link>
                        <p className="text-sm text-muted-foreground">
                            Une plateforme moderne de partage de documents éducatifs créée par <strong>BlackBenAI</strong>.
                        </p>
                    </div>

                    {/* Quick Links */}
                    <div className="space-y-4">
                        <h3 className="text-sm font-semibold uppercase tracking-wider">Liens rapides</h3>
                        <ul className="space-y-2">
                            <li>
                                <Link to="/documents" className="text-sm text-muted-foreground hover:text-foreground transition-colors">
                                    Parcourir les cours
                                </Link>
                            </li>
                            <li>
                                <Link to="/upload" className="text-sm text-muted-foreground hover:text-foreground transition-colors">
                                    Partager un cours
                                </Link>
                            </li>
                        </ul>
                    </div>

                    {/* Legal */}
                    <div className="space-y-4">
                        <h3 className="text-sm font-semibold uppercase tracking-wider">Légal</h3>
                        <ul className="space-y-2">
                            <li>
                                <Link to="/terms" className="text-sm text-muted-foreground hover:text-foreground transition-colors">
                                    Conditions générales
                                </Link>
                            </li>
                            <li>
                                <Link to="/privacy" className="text-sm text-muted-foreground hover:text-foreground transition-colors">
                                    Confidentialité
                                </Link>
                            </li>
                        </ul>
                    </div>
                </div>

                <div className="mt-8 pt-8 border-t text-center">
                    <p className="text-sm text-muted-foreground">
                        &copy; {new Date().getFullYear()} EduShare. Créé avec passion par <strong>BlackBenAI</strong>.
                    </p>
                </div>
            </div>
        </footer>
    );
};

export default Footer;
