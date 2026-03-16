/**
 * Footer Component for PDF Course Sharing Platform
 * Developed by Marino ATOHOUN for BlackBenAI
 */

import React, { useState } from 'react';
import { Link } from 'react-router-dom';
import { BookOpen, Mail, Send, Loader2 } from 'lucide-react';
import { Input } from './ui/input';
import { Button } from './ui/button';
import { newsletterAPI } from '../lib/api';
import { useToast } from '@/hooks/use-toast';

const Footer = () => {
    const [email, setEmail] = useState('');
    const [loading, setLoading] = useState(false);
    const { toast } = useToast();

    const handleSubscribe = async (e) => {
        e.preventDefault();
        if (!email) return;

        setLoading(true);
        try {
            await newsletterAPI.subscribe(email);
            toast({
                title: 'Inscription réussie !',
                description: 'Merci de nous avoir rejoint.',
            });
            setEmail('');
        } catch (error) {
            const message = error.response?.data?.email?.[0] || 'Une erreur est survenue. Veuillez réessayer.';
            toast({
                variant: 'destructive',
                title: 'Erreur',
                description: message,
            });
        } finally {
            setLoading(false);
        }
    };

    return (
        <footer className="border-t bg-card mt-auto">
            <div className="container mx-auto px-4 py-12">
                <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-12">
                    {/* Brand */}
                    <div className="space-y-4">
                        <Link to="/" className="flex items-center space-x-2">
                            <BookOpen className="h-6 w-6 text-primary" />
                            <span className="text-lg font-bold text-foreground">EduShare</span>
                        </Link>
                        <p className="text-sm text-muted-foreground leading-relaxed">
                            Une plateforme moderne de partage de documents éducatifs créée par <strong>BlackBenAI</strong>. Partagez, apprenez et grandissez ensemble.
                        </p>
                    </div>

                    {/* Quick Links */}
                    <div className="space-y-4">
                        <h3 className="text-sm font-semibold uppercase tracking-wider text-foreground">Liens rapides</h3>
                        <ul className="space-y-2">
                            <li>
                                <Link to="/documents" className="text-sm text-muted-foreground hover:text-primary transition-colors">
                                    Parcourir les cours
                                </Link>
                            </li>
                            <li>
                                <Link to="/upload" className="text-sm text-muted-foreground hover:text-primary transition-colors">
                                    Partager un cours
                                </Link>
                            </li>
                        </ul>
                    </div>

                    {/* Legal */}
                    <div className="space-y-4">
                        <h3 className="text-sm font-semibold uppercase tracking-wider text-foreground">Légal</h3>
                        <ul className="space-y-2">
                            <li>
                                <Link to="/terms" className="text-sm text-muted-foreground hover:text-primary transition-colors">
                                    Conditions générales
                                </Link>
                            </li>
                            <li>
                                <Link to="/privacy" className="text-sm text-muted-foreground hover:text-primary transition-colors">
                                    Confidentialité
                                </Link>
                            </li>
                        </ul>
                    </div>

                    {/* Newsletter */}
                    <div className="space-y-4">
                        <h3 className="text-sm font-semibold uppercase tracking-wider text-foreground">Newsletter</h3>
                        <p className="text-sm text-muted-foreground">
                            Abonnez-vous pour recevoir les derniers documents et mises à jour.
                        </p>
                        <form className="flex flex-col space-y-2" onSubmit={handleSubscribe}>
                            <div className="relative">
                                <Mail className="absolute left-3 top-1/2 -translate-y-1/2 h-4 w-4 text-muted-foreground" />
                                <Input
                                    type="email"
                                    placeholder="votre@email.com"
                                    className="pl-10 bg-background border-muted"
                                    value={email}
                                    onChange={(e) => setEmail(e.target.value)}
                                    required
                                    disabled={loading}
                                />
                            </div>
                            <Button type="submit" className="w-full group" disabled={loading}>
                                {loading ? (
                                    <Loader2 className="h-4 w-4 animate-spin" />
                                ) : (
                                    <>
                                        S'abonner
                                        <Send className="ml-2 h-4 w-4 group-hover:translate-x-1 transition-transform" />
                                    </>
                                )}
                            </Button>
                        </form>
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
